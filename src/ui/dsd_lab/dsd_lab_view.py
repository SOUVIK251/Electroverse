import sys
import os
import json
import math
import time
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QSlider, QGridLayout, QFileDialog, QLineEdit, QSplitter,
    QTabWidget, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QProgressBar,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItemGroup
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QSize, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QPixmap, QTransform
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager
from src.core.event_bus import EventBus, EventChannels
from src.core.eckb_loader import ECKBLoader


# ==============================================================================
# 1. NODE-BASED NETLIST ENGINE DATA STRUCTURES (Single Source of Truth)
# ==============================================================================

class ElectricalPin:
    """Represents a physical hardware pin or socket node."""
    def __init__(self, pin_id: str, pin_type: str = "SIGNAL", parent_comp: str = "BREADBOARD"):
        self.pin_id = pin_id            # e.g., 'IC_PIN_1', 'IN_A', 'OUT_Y0', 'PWR_VCC_TERM'
        self.pin_type = pin_type        # 'INPUT', 'OUTPUT', 'POWER', 'GROUND', 'SIGNAL'
        self.parent_comp = parent_comp  # e.g., 'IC_7408', 'TRAINER_KIT', 'BREADBOARD'
        self.logic_state = 0            # 0 (LOW), 1 (HIGH), or None (UNPOWERED)
        self.connected_net_id = None    # ID of ElectricalNet it belongs to

    def __repr__(self):
        return f"<Pin {self.pin_id} ({self.pin_type}) Net={self.connected_net_id}>"


class ElectricalNet:
    """Represents an equipotential electrical net joining 1 or more connected pins."""
    def __init__(self, net_id: str, net_type: str = "SIGNAL"):
        self.net_id = net_id
        self.net_type = net_type        # 'POWER', 'GROUND', 'SIGNAL', 'CLOCK'
        self.pins = set()               # Set of ElectricalPin instances
        self.voltage = 0                # 0 (LOW), 1 (HIGH), or None (UNPOWERED)
        self.is_power_rail = False
        self.is_ground_rail = False

    def add_pin(self, pin: ElectricalPin):
        self.pins.add(pin)
        pin.connected_net_id = self.net_id

    def get_pin_ids(self) -> list:
        return [p.pin_id for p in self.pins]


class BreadboardNetlistEngine:
    """Node-based Electrical Netlist Construction and Recomputation Engine.
    
    Single source of truth for the Digital System Design Practice Area.
    No coordinate inference; electrical nets are derived strictly from physical pin connections.
    """
    def __init__(self):
        self.pins = {}      # pin_id -> ElectricalPin
        self.nets = []      # list of ElectricalNet
        self.ic_power_status = {}  # ic_key -> bool
        self.warnings = []  # List of validation warning messages

    def register_pin(self, pin_id: str, pin_type: str = "SIGNAL", parent_comp: str = "BREADBOARD") -> ElectricalPin:
        if pin_id not in self.pins:
            self.pins[pin_id] = ElectricalPin(pin_id, pin_type, parent_comp)
        return self.pins[pin_id]

    def build_nets(self, wires: list):
        """Constructs connected net components via Graph BFS traversal."""
        adj = {pin_id: set() for pin_id in self.pins}

        # 1. Connect internal breadboard strip holes & rails
        self._connect_breadboard_internal_strips(adj)

        # 2. Connect physical wires
        for wire in wires:
            sh = getattr(wire, 'start_hole', '')
            eh = getattr(wire, 'end_hole', '')
            if sh and eh and sh in adj and eh in adj:
                adj[sh].add(eh)
                adj[eh].add(sh)

        # 3. Graph BFS Connected Components -> Form ElectricalNets
        visited = set()
        self.nets = []
        net_idx = 1

        for pin_id in self.pins:
            if pin_id not in visited:
                comp_pins = set()
                queue = [pin_id]
                visited.add(pin_id)
                
                while queue:
                    curr = queue.pop(0)
                    comp_pins.add(curr)
                    for neighbor in adj.get(curr, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                net_id = f"NET_{net_idx}"
                net_idx += 1
                net = ElectricalNet(net_id)

                for p_id in comp_pins:
                    pin_obj = self.pins[p_id]
                    net.add_pin(pin_obj)
                    if p_id == "PWR_VCC_TERM" or "RAIL_VCC" in p_id:
                        net.is_power_rail = True
                        net.net_type = "POWER"
                    elif p_id == "PWR_GND_TERM" or "RAIL_GND" in p_id:
                        net.is_ground_rail = True
                        net.net_type = "GROUND"

                self.nets.append(net)

    def _connect_breadboard_internal_strips(self, adj):
        """Electrically connects five-hole breadboard strips & continuous power rails."""
        # Top VCC Rail
        vcc_top_pins = [p for p in self.pins if p.startswith("RAIL_VCC_TOP_")]
        for p in vcc_top_pins:
            adj["PWR_VCC_TERM"].add(p)
            adj[p].add("PWR_VCC_TERM")
            
        # Top GND Rail
        gnd_top_pins = [p for p in self.pins if p.startswith("RAIL_GND_TOP_")]
        for p in gnd_top_pins:
            adj["PWR_GND_TERM"].add(p)
            adj[p].add("PWR_GND_TERM")

        # Five-hole vertical strips (A..E and F..J for columns 0..29)
        for col in range(30):
            top_strip = [f"STRIP_TOP_{col}_{r}" for r in ["A", "B", "C", "D", "E"]]
            for i in range(len(top_strip)):
                for j in range(i + 1, len(top_strip)):
                    p1, p2 = top_strip[i], top_strip[j]
                    if p1 in adj and p2 in adj:
                        adj[p1].add(p2)
                        adj[p2].add(p1)

            bot_strip = [f"STRIP_BOT_{col}_{r}" for r in ["F", "G", "H", "I", "J"]]
            for i in range(len(bot_strip)):
                for j in range(i + 1, len(bot_strip)):
                    p1, p2 = bot_strip[i], bot_strip[j]
                    if p1 in adj and p2 in adj:
                        adj[p1].add(p2)
                        adj[p2].add(p1)

        # DIP IC Lead Connections to Breadboard Strip Columns
        for i in range(7):
            pin_num = i + 1
            col_idx = 10 + i
            ic_pin_id = f"IC_PIN_{pin_num}"
            strip_pin_id = f"STRIP_TOP_{col_idx}_E"
            if ic_pin_id in adj and strip_pin_id in adj:
                adj[ic_pin_id].add(strip_pin_id)
                adj[strip_pin_id].add(ic_pin_id)

        for i in range(7):
            pin_num = 14 - i
            col_idx = 10 + i
            ic_pin_id = f"IC_PIN_{pin_num}"
            strip_pin_id = f"STRIP_BOT_{col_idx}_F"
            if ic_pin_id in adj and strip_pin_id in adj:
                adj[ic_pin_id].add(strip_pin_id)
                adj[strip_pin_id].add(ic_pin_id)

    def validate_power_rails(self, ic_key: str, power_switch_on: bool, has_wires: bool) -> bool:
        """Validates if IC Pin 14 (VCC) is in +5V Net and IC Pin 7 (GND) is in GND Net."""
        if not power_switch_on:
            self.ic_power_status[ic_key] = False
            return False

        vcc_pin = self.pins.get("IC_PIN_14")
        gnd_pin = self.pins.get("IC_PIN_7")

        has_vcc = False
        has_gnd = False

        if vcc_pin and vcc_pin.connected_net_id:
            for net in self.nets:
                if net.net_id == vcc_pin.connected_net_id:
                    if any(p.pin_id == "PWR_VCC_TERM" or "RAIL_VCC" in p.pin_id for p in net.pins):
                        has_vcc = True
                        break

        if gnd_pin and gnd_pin.connected_net_id:
            for net in self.nets:
                if net.net_id == gnd_pin.connected_net_id:
                    if any(p.pin_id == "PWR_GND_TERM" or "RAIL_GND" in p.pin_id for p in net.pins):
                        has_gnd = True
                        break

        if not has_wires:
            has_vcc = True
            has_gnd = True

        is_powered = has_vcc and has_gnd
        self.ic_power_status[ic_key] = is_powered
        return is_powered

    def validate_wire(self, start_pin_id: str, end_pin_id: str) -> bool:
        """Validates electrical safety of a candidate wire connection."""
        sp = self.pins.get(start_pin_id)
        ep = self.pins.get(end_pin_id)
        if not sp or not ep:
            return True

        if (sp.pin_type == "POWER" and ep.pin_type == "OUTPUT") or (sp.pin_type == "OUTPUT" and ep.pin_type == "POWER"):
            self.warnings.append(f"Short Circuit Warning: Power connected to Output ({start_pin_id} -> {end_pin_id})!")
            return False
        if (sp.pin_type == "GROUND" and ep.pin_type == "OUTPUT") or (sp.pin_type == "OUTPUT" and ep.pin_type == "GROUND"):
            self.warnings.append(f"Short Circuit Warning: Ground connected to Output ({start_pin_id} -> {end_pin_id})!")
            return False

        return True


# ==============================================================================
# 2. 2D BREADBOARD & TERMINAL GRAPHICS ITEMS
# ==============================================================================

class WireDeleteButtonItem(QGraphicsEllipseItem):
    """Floating '-' Delete Button Item placed at Wire Midpoint."""
    def __init__(self, wire_owner, x, y, radius=9, parent=None):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, parent)
        self.wire_owner = wire_owner
        self.setBrush(QBrush(QColor("#ef4444")))
        self.setPen(QPen(QColor("#ffffff"), 1.5))
        self.setZValue(100)
        self.setAcceptHoverEvents(True)
        
        self.txt = QGraphicsTextItem("–", self)
        self.txt.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.txt.setDefaultTextColor(QColor("#ffffff"))
        self.txt.setPos(x - 6, y - 13)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor("#dc2626")))
        self.setPen(QPen(QColor("#fca5a5"), 2.0))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor("#ef4444")))
        self.setPen(QPen(QColor("#ffffff"), 1.5))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            scene = self.scene()
            if scene and hasattr(scene, "remove_wire"):
                scene.remove_wire(self.wire_owner)
                return
        super().mousePressEvent(event)


class BreadboardHoleItem(QGraphicsEllipseItem):
    """Interactive 2D Breadboard & Terminal Hole Pin Socket."""
    def __init__(self, hole_id, x, y, radius=4, color_hex="#090d16", border_hex="#475569", parent=None):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, parent)
        self.hole_id = hole_id
        self.center_x = x
        self.center_y = y
        self.default_brush = QBrush(QColor(color_hex))
        self.default_pen = QPen(QColor(border_hex), 1.5)
        self.setBrush(self.default_brush)
        self.setPen(self.default_pen)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        scene = self.scene()
        if scene and getattr(scene, "eraser_mode", False):
            self.setBrush(QBrush(QColor("#ef4444")))
            self.setPen(QPen(QColor("#fca5a5"), 2.5))
        else:
            self.setBrush(QBrush(QColor("#06b6d4")))
            self.setPen(QPen(QColor("#38bdf8"), 2.5))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(self.default_brush)
        self.setPen(self.default_pen)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        log.debug(f"[ConnectorAudit] Clicked Hole Socket ID={self.hole_id} at ({self.center_x}, {self.center_y})")
        super().mousePressEvent(event)


class WireLineItem(QGraphicsLineItem):
    """Click-to-draw Jumper Wire Item with Midpoint '-' Delete Sign Button."""
    def __init__(self, x1, y1, x2, y2, color_hex="#ef4444", start_hole="", end_hole="", parent=None):
        super().__init__(x1, y1, x2, y2, parent)
        self.color_hex = color_hex
        self.start_hole = start_hole
        self.end_hole = end_hole
        self.delete_btn_item = None
        self.setPen(QPen(QColor(color_hex), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        scene = self.scene()
        if scene and getattr(scene, "eraser_mode", False):
            self.setPen(QPen(QColor("#ef4444"), 5.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        else:
            self.setPen(QPen(QColor(self.color_hex).lighter(140), 4.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(QPen(QColor(self.color_hex), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        super().hoverLeaveEvent(event)

    def show_delete_button(self):
        scene = self.scene()
        if not scene:
            return
        
        for item in scene.items():
            if isinstance(item, WireLineItem) and item != self:
                item.hide_delete_button()
                
        if not self.delete_btn_item:
            line = self.line()
            mid_x = (line.x1() + line.x2()) / 2.0
            mid_y = (line.y1() + line.y2()) / 2.0
            self.delete_btn_item = WireDeleteButtonItem(self, mid_x, mid_y)
            scene.addItem(self.delete_btn_item)

    def hide_delete_button(self):
        if self.delete_btn_item and self.scene():
            self.scene().removeItem(self.delete_btn_item)
            self.delete_btn_item = None

    def mousePressEvent(self, event):
        scene = self.scene()
        if event.button() == Qt.MouseButton.RightButton or (scene and getattr(scene, "eraser_mode", False)):
            if scene and hasattr(scene, "remove_wire"):
                scene.remove_wire(self)
                return
        elif event.button() == Qt.MouseButton.LeftButton:
            self.show_delete_button()
        super().mousePressEvent(event)


class TinkercadCanvasScene(QGraphicsScene):
    """2D Interactive Scene for Components, Breadboard Grid, Terminals, and Wires."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#090d16")))
        self.current_wire_color = "#ef4444"
        self.eraser_mode = False
        self.drawing_wire = False
        self.temp_wire = None
        self.wire_start_item = None
        self.wire_start_pt = None
        self.wires = []

    def set_wire_color(self, color_hex):
        self.current_wire_color = color_hex
        self.eraser_mode = False

    def toggle_eraser_mode(self, enabled=True):
        self.eraser_mode = enabled

    def remove_wire(self, wire_item):
        if hasattr(wire_item, "hide_delete_button"):
            wire_item.hide_delete_button()
        if wire_item in self.wires:
            self.wires.remove(wire_item)
        self.removeItem(wire_item)
        EventBus.publish(EventChannels.WIRE_CONNECTED, action="removed")
        if self.parent() and hasattr(self.parent(), "solve_circuit_logic"):
            self.parent().solve_circuit_logic()

    def mousePressEvent(self, event):
        items_at_pos = self.items(event.scenePos())
        clicked_wire_or_btn = any(isinstance(i, (WireLineItem, WireDeleteButtonItem)) for i in items_at_pos)
        
        if not clicked_wire_or_btn:
            for w in self.wires:
                w.hide_delete_button()

        if self.eraser_mode:
            for item in items_at_pos:
                if isinstance(item, WireLineItem):
                    self.remove_wire(item)
                    return
        elif event.button() == Qt.MouseButton.LeftButton:
            for item in items_at_pos:
                if isinstance(item, BreadboardHoleItem):
                    self.drawing_wire = True
                    self.wire_start_item = item
                    self.wire_start_pt = QPointF(item.center_x, item.center_y)
                    self.temp_wire = WireLineItem(
                        self.wire_start_pt.x(), self.wire_start_pt.y(),
                        event.scenePos().x(), event.scenePos().y(),
                        self.current_wire_color,
                        start_hole=item.hole_id
                    )
                    self.addItem(self.temp_wire)
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing_wire and self.temp_wire:
            self.temp_wire.setLine(
                self.wire_start_pt.x(), self.wire_start_pt.y(),
                event.scenePos().x(), event.scenePos().y()
            )
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing_wire and self.temp_wire:
            items_at_pos = self.items(event.scenePos())
            for item in items_at_pos:
                if isinstance(item, BreadboardHoleItem) and item.center_x != self.wire_start_pt.x():
                    final_wire = WireLineItem(
                        self.wire_start_pt.x(), self.wire_start_pt.y(),
                        item.center_x, item.center_y,
                        self.current_wire_color,
                        start_hole=self.wire_start_item.hole_id if self.wire_start_item else "",
                        end_hole=item.hole_id
                    )
                    self.addItem(final_wire)
                    self.wires.append(final_wire)
                    log.info(f"[WireRouting] Placed Wire: {final_wire.start_hole} -> {final_wire.end_hole}")
                    EventBus.publish(EventChannels.WIRE_CONNECTED, color=self.current_wire_color)
                    if self.parent() and hasattr(self.parent(), "solve_circuit_logic"):
                        self.parent().solve_circuit_logic()
                    break
            self.removeItem(self.temp_wire)
            self.temp_wire = None
            self.wire_start_item = None
            self.drawing_wire = False
            return
        super().mouseReleaseEvent(event)


# ==============================================================================
# 3. ELECTRICAL LOGIC ENGINE
# ==============================================================================

class DigitalLogicEngine:
    """Evaluates digital logic gates based on IC datasheet models."""

    @classmethod
    def evaluate_gate(cls, gate_type: str, inputs: list) -> int:
        gt = str(gate_type).upper()
        in1 = inputs[0] if len(inputs) > 0 else 0
        in2 = inputs[1] if len(inputs) > 1 else 0

        if "NAND" in gt or "7400" in gt:
            return 0 if (in1 == 1 and in2 == 1) else 1
        elif "NOR" in gt or "7402" in gt:
            return 0 if (in1 == 1 or in2 == 1) else 1
        elif "XNOR" in gt or "74266" in gt:
            return 0 if (in1 ^ in2) == 1 else 1
        elif "XOR" in gt or "7486" in gt:
            return 1 if (in1 ^ in2) == 1 else 0
        elif "AND3" in gt or "7411" in gt:
            return 1 if all(v == 1 for v in inputs[:3]) else 0
        elif "AND" in gt or "7408" in gt:
            return 1 if (in1 == 1 and in2 == 1) else 0
        elif "OR" in gt or "7432" in gt:
            return 1 if (in1 == 1 or in2 == 1) else 0
        elif "NOT" in gt or "7404" in gt or "INVERTER" in gt:
            return 0 if in1 == 1 else 1
        return 0

    @classmethod
    def evaluate_experiment(cls, exp_id: str, inputs_dict: dict, clock_val: int = 0) -> dict:
        a = inputs_dict.get("IN_A", 0)
        b = inputs_dict.get("IN_B", 0)
        c = inputs_dict.get("IN_C", 0)
        d = inputs_dict.get("IN_D", 0)
        e = inputs_dict.get("IN_E", 0)

        outs = {"OUT_Y0": 0, "OUT_Y1": 0, "OUT_Y2": 0, "OUT_Y3": 0}

        if exp_id in ["nand_gate", "7400"]:
            outs["OUT_Y0"] = 0 if (a == 1 and b == 1) else 1
        elif exp_id in ["and_gate", "7408"]:
            outs["OUT_Y0"] = a & b
        elif exp_id in ["or_gate", "7432"]:
            outs["OUT_Y0"] = a | b
        elif exp_id in ["not_gate", "7404"]:
            outs["OUT_Y0"] = 1 if a == 0 else 0
        elif exp_id in ["nor_gate", "7402"]:
            outs["OUT_Y0"] = 0 if (a == 1 or b == 1) else 1
        elif exp_id in ["xor_gate", "7486"]:
            outs["OUT_Y0"] = a ^ b
        elif exp_id in ["xnor_gate", "74266", "gate_xnor"] or "xnor" in str(exp_id).lower():
            outs["OUT_Y0"] = 0 if (a ^ b) == 1 else 1
        elif exp_id == "half_adder":
            outs["OUT_Y0"] = a ^ b        # Sum S
            outs["OUT_Y1"] = a & b        # Carry C
        elif exp_id == "full_adder":
            s = a ^ b ^ c
            cout = (a & b) | (b & c) | (a & c)
            outs["OUT_Y0"] = s            # Sum S
            outs["OUT_Y1"] = cout         # Carry Out
        elif exp_id == "mux_2_1":
            outs["OUT_Y0"] = b if c == 1 else a
        elif exp_id == "decoder_2_4":
            idx = (b << 1) | a
            outs[f"OUT_Y{idx}"] = 1
        elif exp_id == "encoder_4_2":
            if e == 1:
                outs["OUT_Y2"] = 1
            else:
                outs["OUT_Y0"] = b | d
                outs["OUT_Y1"] = c | d
        elif exp_id == "d_flip_flop":
            outs["OUT_Y0"] = a if clock_val == 1 else 0  # Q
            outs["OUT_Y1"] = 0 if a == 1 else 1           # Q_bar
        else:
            outs["OUT_Y0"] = a & b

        return outs

    @classmethod
    def validate_gate_truth_table(cls, exp_id: str) -> bool:
        tables = {
            "and_gate":  [(0,0,0), (0,1,0), (1,0,0), (1,1,1)],
            "7408":      [(0,0,0), (0,1,0), (1,0,0), (1,1,1)],
            "or_gate":   [(0,0,0), (0,1,1), (1,0,1), (1,1,1)],
            "7432":      [(0,0,0), (0,1,1), (1,0,1), (1,1,1)],
            "not_gate":  [(0,0,1), (1,0,0)],
            "7404":      [(0,0,1), (1,0,0)],
            "nand_gate": [(0,0,1), (0,1,1), (1,0,1), (1,1,0)],
            "7400":      [(0,0,1), (0,1,1), (1,0,1), (1,1,0)],
            "nor_gate":  [(0,0,1), (0,1,0), (1,0,0), (1,1,0)],
            "7402":      [(0,0,1), (0,1,0), (1,0,0), (1,1,0)],
            "xor_gate":  [(0,0,0), (0,1,1), (1,0,1), (1,1,0)],
            "7486":      [(0,0,0), (0,1,1), (1,0,1), (1,1,0)],
            "xnor_gate": [(0,0,1), (0,1,0), (1,0,0), (1,1,1)],
            "gate_xnor": [(0,0,1), (0,1,0), (1,0,0), (1,1,1)],
            "74266":     [(0,0,1), (0,1,0), (1,0,0), (1,1,1)],
        }
        if exp_id not in tables:
            return True

        all_ok = True
        for row in tables[exp_id]:
            in1, in2, expected = row[0], row[1], row[-1]
            out = cls.evaluate_experiment(exp_id, {"IN_A": in1, "IN_B": in2})["OUT_Y0"]
            if out != expected:
                log.warning(f"[TruthTableAudit] Mismatch in {exp_id}: In=({in1},{in2}) Expected={expected} Actual={out}")
                all_ok = False
        return all_ok


# ==============================================================================
# 4. METADATA-DRIVEN TRAINER KIT VIEW WITH NODE-BASED CIRCUIT ENGINE
# ==============================================================================

class DSDLabView(QWidget):
    """Metadata-Driven Breadboard Trainer Kit UI with Pure Node-Based Circuit Engine Architecture."""

    OUTPUT_TERMINAL_KEYS = ["OUT_Y0", "OUT_Y1", "OUT_Y2", "OUT_Y3"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.power_on = True
        self.is_simulating = True
        self.clock_state = 0
        self.clock_hz = 2.0
        self.step_counter = 0
        
        self.inputs_state = {
            "IN_A": 0, "IN_B": 0, "IN_C": 0, "IN_D": 0,
            "IN_E": 0, "IN_F": 0, "IN_G": 0, "IN_H": 0
        }
        self.outputs_state = {"OUT_Y0": 0, "OUT_Y1": 0, "OUT_Y2": 0, "OUT_Y3": 0}
        
        self.beginner_mode = True
        self.current_experiment = "and_gate"
        self.current_ic_key = "7408"
        self.current_gate_idx = 0
        self.current_step_idx = 0

        # Initialize Node-Based Electrical Netlist Engine
        self.net_engine = BreadboardNetlistEngine()
        
        ECKBLoader.initialize()
        self.grid_data = ECKBLoader.get_dataset("breadboard_grid")
        self.comp_data = ECKBLoader.get_dataset("canvas_components")
        self.input_term_data = ECKBLoader.get_dataset("input_terminals").get("terminals", [])
        self.output_term_data = ECKBLoader.get_dataset("output_terminals").get("terminals", [])
        self.wire_styles = ECKBLoader.get_dataset("wire_styles").get("styles", {})
        
        self.init_ui()
        self.subscribe_events()
        self.update_metadata_guided_flow()
        
        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(33)
        self.sim_timer.timeout.connect(self.on_sim_tick)
        self.sim_timer.start()

    def subscribe_events(self):
        EventBus.subscribe(EventChannels.SWITCH_TOGGLED, self.on_event_switch_toggled)
        EventBus.subscribe(EventChannels.POWER_CHANGED, self.on_event_power_changed)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)
        
        top_bar = self.create_top_control_bar()
        main_layout.addWidget(top_bar)
        
        color_bar = self.create_wire_color_palette()
        main_layout.addWidget(color_bar)
        
        top_header_row = QHBoxLayout()
        top_header_row.setSpacing(6)
        
        input_panel = self.create_input_terminal_panel()
        top_header_row.addWidget(input_panel, 1)
        
        card_panel = self.create_next_connection_card_panel()
        top_header_row.addWidget(card_panel, 2)
        
        output_panel = self.create_output_terminal_panel()
        top_header_row.addWidget(output_panel, 1)
        
        main_layout.addLayout(top_header_row)
        
        work_splitter = QSplitter(Qt.Orientation.Horizontal)
        work_splitter.setHandleWidth(3)
        
        left_toolbox = self.create_left_toolbox()
        work_splitter.addWidget(left_toolbox)
        
        center_workbench = self.create_center_workbench()
        work_splitter.addWidget(center_workbench)
        
        right_inspector = self.create_right_inspector()
        work_splitter.addWidget(right_inspector)
        
        work_splitter.setSizes([220, 600, 240])
        main_layout.addWidget(work_splitter, 1)
        
        self.status_bar_frame = QFrame()
        self.status_bar_frame.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 4px; padding: 3px 6px;")
        sb_lay = QHBoxLayout(self.status_bar_frame)
        sb_lay.setContentsMargins(5, 2, 5, 2)
        
        self.lbl_status_led = QLabel("● +5V POWER ON")
        self.lbl_status_led.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
        
        self.lbl_diag_msg = QLabel("Lab Instructor: Select an experiment to pre-load breadboard circuit & connections checklist.")
        self.lbl_diag_msg.setStyleSheet("color: #94a3b8; font-size: 8.5pt;")
        
        sb_lay.addWidget(self.lbl_status_led)
        sb_lay.addWidget(self.lbl_diag_msg, 1)
        main_layout.addWidget(self.status_bar_frame)
        
        self.build_2d_breadboard_grid()

    def create_top_control_bar(self):
        card = QFrame()
        card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 4px 8px;")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(10)
        
        title_lbl = QLabel("⚡ Digital Trainer Kit")
        title_lbl.setStyleSheet("font-weight: bold; color: #06b6d4; font-size: 10.5pt;")
        layout.addWidget(title_lbl)

        exp_lbl = QLabel("Experiment:")
        exp_lbl.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 8.5pt;")
        layout.addWidget(exp_lbl)

        self.exp_combo = QComboBox()
        self.exp_combo.addItem("1. AND Gate (IC 7408)", "and_gate")
        self.exp_combo.addItem("2. OR Gate (IC 7432)", "or_gate")
        self.exp_combo.addItem("3. NOT Gate (IC 7404)", "not_gate")
        self.exp_combo.addItem("4. NAND Gate (IC 7400)", "nand_gate")
        self.exp_combo.addItem("5. NOR Gate (IC 7402)", "nor_gate")
        self.exp_combo.addItem("6. XOR Gate (IC 7486)", "xor_gate")
        self.exp_combo.addItem("7. XNOR Gate (IC 74266)", "xnor_gate")
        self.exp_combo.setStyleSheet("background-color: #1e293b; color: #ffffff; font-weight: bold; padding: 3px 6px; border-radius: 4px; font-size: 8.5pt;")
        self.exp_combo.currentIndexChanged.connect(self.on_experiment_combo_changed)
        layout.addWidget(self.exp_combo)
        
        self.chk_beginner_mode = QCheckBox("Beginner Mode")
        self.chk_beginner_mode.setChecked(True)
        self.chk_beginner_mode.setStyleSheet("color: #10b981; font-weight: bold; font-size: 9pt;")
        self.chk_beginner_mode.toggled.connect(self.on_beginner_mode_toggled)
        layout.addWidget(self.chk_beginner_mode)
        
        layout.addStretch()
        
        self.btn_sim_toggle = QPushButton(" ▶ Start Simulation")
        self.btn_sim_toggle.setStyleSheet("background-color: #06b6d4; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
        self.btn_sim_toggle.clicked.connect(self.toggle_simulation_mode)
        layout.addWidget(self.btn_sim_toggle)
        
        self.btn_power = QPushButton(" +5V Power ON")
        self.btn_power.setIcon(qta.icon("fa5s.power-off", color="#ffffff"))
        self.btn_power.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
        self.btn_power.clicked.connect(self.toggle_power)
        layout.addWidget(self.btn_power)
        
        clk_lbl = QLabel("Clock:")
        clk_lbl.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 8.5pt;")
        layout.addWidget(clk_lbl)
        
        self.slider_clk_hz = QSlider(Qt.Orientation.Horizontal)
        self.slider_clk_hz.setRange(1, 20)
        self.slider_clk_hz.setValue(2)
        self.slider_clk_hz.setFixedWidth(70)
        self.slider_clk_hz.valueChanged.connect(self.on_clk_hz_changed)
        layout.addWidget(self.slider_clk_hz)
        
        self.lbl_clk_hz = QLabel("2.0 Hz")
        self.lbl_clk_hz.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 8.5pt;")
        layout.addWidget(self.lbl_clk_hz)
        
        layout.addSpacing(6)
        self.btn_reset = QPushButton(" Clear Canvas")
        self.btn_reset.setIcon(qta.icon("fa5s.trash-alt", color="#ef4444"))
        self.btn_reset.setStyleSheet("background-color: #450a0a; color: #fca5a5; border: 1px solid #7f1d1d; padding: 3px 8px; border-radius: 4px; font-size: 8.5pt;")
        self.btn_reset.clicked.connect(self.reset_workspace)
        layout.addWidget(self.btn_reset)
        
        return card

    def create_wire_color_palette(self):
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 3px 6px;")
        lay = QHBoxLayout(card)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setSpacing(6)
        
        lbl_wire = QLabel("🎨 Wire Swatch:")
        lbl_wire.setStyleSheet("color: #f8fafc; font-weight: bold; font-size: 8.5pt;")
        lay.addWidget(lbl_wire)
        
        swatches = [
            ("Red (+5V)", "#ef4444"),
            ("Black (GND)", "#1e293b"),
            ("Cyan (Signal)", "#06b6d4"),
            ("Yellow (Clock)", "#eab308"),
            ("Green (HIGH)", "#10b981"),
            ("Blue (LOW)", "#3b82f6")
        ]
        
        for name, hex_code in swatches:
            btn = QPushButton(name)
            btn.setStyleSheet(f"background-color: {hex_code}; color: {'#000000' if hex_code in ['#f8fafc', '#eab308'] else '#ffffff'}; font-weight: bold; padding: 2px 6px; border-radius: 3px; font-size: 8pt;")
            btn.clicked.connect(lambda _, h=hex_code: self.set_active_wire_color(h))
            lay.addWidget(btn)
            
        lay.addSpacing(10)
        self.btn_eraser = QPushButton(" 🧹 Erase Wire")
        self.btn_eraser.setCheckable(True)
        self.btn_eraser.setStyleSheet("QPushButton { background-color: #450a0a; color: #fca5a5; font-weight: bold; padding: 2px 8px; border: 1px solid #ef4444; border-radius: 3px; font-size: 8pt; } QPushButton:checked { background-color: #ef4444; color: white; }")
        self.btn_eraser.clicked.connect(self.on_eraser_toggled)
        lay.addWidget(self.btn_eraser)

        self.btn_auto_wire = QPushButton(" ⚡ Auto-Wire Preset")
        self.btn_auto_wire.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 2px 8px; border-radius: 3px; font-size: 8pt;")
        self.btn_auto_wire.clicked.connect(self.auto_wire_preset)
        lay.addWidget(self.btn_auto_wire)
        
        lay.addStretch()
        return card

    def set_active_wire_color(self, hex_code):
        if hasattr(self, 'btn_eraser'):
            self.btn_eraser.setChecked(False)
        if hasattr(self, 'canvas_scene'):
            self.canvas_scene.set_wire_color(hex_code)

    def on_eraser_toggled(self, checked):
        if hasattr(self, 'canvas_scene'):
            self.canvas_scene.toggle_eraser_mode(checked)

    def create_input_terminal_panel(self):
        card = QFrame()
        card.setStyleSheet("background-color: #091322; border: 2px solid #0284c7; border-radius: 6px; padding: 4px;")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(4, 3, 4, 3)
        lay.setSpacing(2)
        
        title = QLabel("⚡ INPUT TERMINALS (A-H)")
        title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 8.5pt;")
        lay.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(2)
        
        self.input_btns = {}
        inputs_list = ["IN_A", "IN_B", "IN_C", "IN_D", "IN_E", "IN_F", "IN_G", "IN_H"]
        
        for idx, key in enumerate(inputs_list):
            name = key.replace("IN_", "")
            row = idx // 4
            col = idx % 4
            
            btn = QPushButton(f"{name}: LOW")
            btn.setCheckable(True)
            btn.setStyleSheet("background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 2px 4px; border-radius: 3px; font-size: 7.5pt;")
            btn.clicked.connect(lambda _, k=key, b=btn: self.toggle_input_terminal(k, b))
            grid.addWidget(btn, row, col)
            self.input_btns[key] = btn
            
        lay.addLayout(grid)
        return card

    def create_next_connection_card_panel(self):
        self.banner_assistant = QFrame()
        self.banner_assistant.setStyleSheet("background-color: #032b45; border: 2px solid #0284c7; border-radius: 6px; padding: 6px;")
        b_lay = QVBoxLayout(self.banner_assistant)
        b_lay.setContentsMargins(6, 4, 6, 4)
        b_lay.setSpacing(3)
        
        b_header = QHBoxLayout()
        self.lbl_assistant_title = QLabel("──────────────  NEXT CONNECTION  ──────────────")
        self.lbl_assistant_title.setStyleSheet("color: #38bdf8; font-weight: 800; font-size: 9pt;")
        b_header.addWidget(self.lbl_assistant_title)
        b_header.addStretch()
        
        self.lbl_conn_counter = QLabel("Connections: 1 / 5 Completed")
        self.lbl_conn_counter.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
        b_header.addWidget(self.lbl_conn_counter)
        
        self.progress_guided = QProgressBar()
        self.progress_guided.setRange(0, 100)
        self.progress_guided.setValue(20)
        self.progress_guided.setFixedWidth(80)
        self.progress_guided.setFixedHeight(5)
        self.progress_guided.setTextVisible(False)
        self.progress_guided.setStyleSheet("QProgressBar { background-color: #0369a1; border: none; border-radius: 2px; } QProgressBar::chunk { background-color: #38bdf8; border-radius: 2px; }")
        b_header.addWidget(self.progress_guided)
        
        b_lay.addLayout(b_header)
        
        card_grid = QGridLayout()
        card_grid.setSpacing(2)
        
        card_grid.addWidget(QLabel("FROM:"), 0, 0)
        self.lbl_card_from = QLabel("+5V Power Terminal")
        self.lbl_card_from.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_from, 0, 1)
        
        card_grid.addWidget(QLabel("TO:"), 0, 2)
        self.lbl_card_to = QLabel("Pin 14 (VCC)")
        self.lbl_card_to.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_to, 0, 3)
        
        card_grid.addWidget(QLabel("WIRE COLOR:"), 1, 0)
        self.lbl_card_color = QLabel("Red Wire")
        self.lbl_card_color.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_color, 1, 1)
        
        card_grid.addWidget(QLabel("PURPOSE:"), 1, 2)
        self.lbl_card_purpose = QLabel("IC Power Supply")
        self.lbl_card_purpose.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_purpose, 1, 3)
        
        b_lay.addLayout(card_grid)
        
        self.lbl_card_reason = QLabel("REASON: Powers internal logic gates. Without VCC power the IC cannot operate.")
        self.lbl_card_reason.setStyleSheet("color: #93c5fd; font-size: 8pt; font-style: italic;")
        b_lay.addWidget(self.lbl_card_reason)
        
        act_lay = QHBoxLayout()
        self.btn_center_prev = QPushButton(" ⬅ Previous")
        self.btn_center_prev.setStyleSheet("background-color: #1e293b; color: #94a3b8; border: 1px solid #334155; font-weight: bold; padding: 2px 6px; border-radius: 3px; font-size: 8pt;")
        self.btn_center_prev.clicked.connect(self.prev_guided_step)
        act_lay.addWidget(self.btn_center_prev)
        
        act_lay.addStretch()
        
        self.btn_center_next = QPushButton(" ✓ Verify & Next ➡")
        self.btn_center_next.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        self.btn_center_next.clicked.connect(self.advance_guided_step)
        act_lay.addWidget(self.btn_center_next)
        
        b_lay.addLayout(act_lay)
        return self.banner_assistant

    def create_output_terminal_panel(self):
        card = QFrame()
        card.setStyleSheet("background-color: #061e14; border: 2px solid #047857; border-radius: 6px; padding: 6px;")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(4)
        
        title = QLabel("💡 OUTPUT TERMINALS (Y0-Y3)")
        title.setStyleSheet("color: #34d399; font-weight: bold; font-size: 9pt;")
        lay.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(4)
        
        self.output_led_widgets = {}
        
        labels_config = [
            ("OUT_Y0", "Y0", 0, 0),
            ("OUT_Y1", "Y1", 0, 1),
            ("OUT_Y2", "Y2", 1, 0),
            ("OUT_Y3", "Y3", 1, 1),
        ]
        
        for key, name, row, col in labels_config:
            lbl = QLabel(f"{name}: OFF (0V)")
            lbl.setStyleSheet("background-color: #1e293b; color: #64748b; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")
            grid.addWidget(lbl, row, col)
            self.output_led_widgets[key] = lbl
            
        self.lbl_out_y0 = self.output_led_widgets["OUT_Y0"]
        self.lbl_out_y1 = self.output_led_widgets["OUT_Y1"]
        self.lbl_out_y2 = self.output_led_widgets["OUT_Y2"]
        self.lbl_out_y3 = self.output_led_widgets["OUT_Y3"]

        lay.addLayout(grid)
        return card

    def toggle_input_terminal(self, input_key, btn_widget):
        new_val = 1 if btn_widget.isChecked() else 0
        self.inputs_state[input_key] = new_val
        btn_name = input_key.replace("IN_", "")
        
        if new_val == 1:
            btn_widget.setText(f"{btn_name}: HIGH")
            btn_widget.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; padding: 2px 4px; border-radius: 3px; font-size: 7.5pt;")
        else:
            btn_widget.setText(f"{btn_name}: LOW")
            btn_widget.setStyleSheet("background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 2px 4px; border-radius: 3px; font-size: 7.5pt;")
            
        EventBus.publish(EventChannels.SWITCH_TOGGLED, terminal=input_key, logic=new_val)
        self.solve_circuit_logic()

    def create_left_toolbox(self):
        card = QFrame()
        card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 6, 6, 6)
        
        layout.addWidget(QLabel("🧰 IC Package Selector", styleSheet="color: #06b6d4; font-weight: bold; font-size: 9pt;"))
        
        self.ic_selector = QComboBox()
        self.ic_selector.addItem("IC 7408 (Quad 2-Input AND)", "7408")
        self.ic_selector.addItem("IC 7432 (Quad 2-Input OR)", "7432")
        self.ic_selector.addItem("IC 7404 (Hex Inverter NOT)", "7404")
        self.ic_selector.addItem("IC 7400 (Quad 2-Input NAND)", "7400")
        self.ic_selector.addItem("IC 7402 (Quad 2-Input NOR)", "7402")
        self.ic_selector.addItem("IC 7486 (Quad 2-Input XOR)", "7486")
        self.ic_selector.addItem("IC 74266 (Quad 2-Input XNOR)", "74266")
        self.ic_selector.currentIndexChanged.connect(self.on_ic_selection_changed)
        layout.addWidget(self.ic_selector)
        
        self.combo_gate_select = QComboBox()
        self.combo_gate_select.addItems([
            "Gate 1 (Pins 1,2 -> Pin 3)",
            "Gate 2 (Pins 4,5 -> Pin 6)",
            "Gate 3 (Pins 9,10 -> Pin 8)",
            "Gate 4 (Pins 12,13 -> Pin 11)"
        ])
        self.combo_gate_select.currentIndexChanged.connect(self.on_gate_index_changed)
        layout.addWidget(QLabel("Active Gate Section:", styleSheet="color: #94a3b8; font-size: 8.5pt;"))
        layout.addWidget(self.combo_gate_select)
        
        layout.addSpacing(6)
        self.lbl_gate_desc = QLabel("IC Metadata Active")
        self.lbl_gate_desc.setWordWrap(True)
        self.lbl_gate_desc.setStyleSheet("color: #94a3b8; font-size: 8pt; line-height: 1.3;")
        layout.addWidget(self.lbl_gate_desc)
        
        layout.addStretch()
        return card

    def create_center_workbench(self):
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 4px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self.canvas_scene = TinkercadCanvasScene(self)
        self.canvas_view = QGraphicsView(self.canvas_scene)
        self.canvas_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.canvas_view.setStyleSheet("border: 1px solid #334155; background-color: #090d16; border-radius: 4px;")
        layout.addWidget(self.canvas_view, 1)
        
        return card

    def create_right_inspector(self):
        card = QFrame()
        card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 6, 6, 6)
        
        insp_tabs = QTabWidget()
        insp_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e293b; background-color: #0b0f19; border-radius: 4px; }
            QTabBar::tab { background-color: #1e293b; color: #94a3b8; padding: 4px 6px; font-size: 8pt; font-weight: bold; }
            QTabBar::tab:selected { background-color: #06b6d4; color: #ffffff; }
        """)
        
        # Tab 1: Checklist
        steps_widget = QWidget()
        st_lay = QVBoxLayout(steps_widget)
        st_lay.setContentsMargins(3, 3, 3, 3)
        st_lay.addWidget(QLabel("📋 Connections Checklist:", styleSheet="color: #38bdf8; font-weight: bold; font-size: 8.5pt;"))
        self.list_steps = QListWidget()
        self.list_steps.setStyleSheet("QListWidget { background-color: #0b0f19; color: #f8fafc; border: 1px solid #1e293b; border-radius: 4px; } QListWidget::item { padding: 3px; font-size: 8pt; }")
        st_lay.addWidget(self.list_steps)
        insp_tabs.addTab(steps_widget, "Checklist")

        # Tab 2: Truth Table Verification
        tt_widget = QWidget()
        tt_lay = QVBoxLayout(tt_widget)
        tt_lay.setContentsMargins(3, 3, 3, 3)
        
        self.lbl_tt_status = QLabel("✓ Live Truth Table Verification")
        self.lbl_tt_status.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
        tt_lay.addWidget(self.lbl_tt_status)

        self.table_truth = QTableWidget(4, 3)
        self.table_truth.setHorizontalHeaderLabels(["IN A", "IN B", "OUT Y"])
        self.table_truth.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_truth.setStyleSheet("QTableWidget { background-color: #0b0f19; color: #FFF; font-size: 8pt; border: 1px solid #1e293b; }")
        tt_lay.addWidget(self.table_truth)

        insp_tabs.addTab(tt_widget, "Truth Table")
        
        # Tab 3: Datasheet
        ds_widget = QWidget()
        ds_lay = QVBoxLayout(ds_widget)
        ds_lay.setContentsMargins(3, 3, 3, 3)
        ds_lay.addWidget(QLabel("📄 Datasheet Quick View:", styleSheet="color: #06b6d4; font-weight: bold; font-size: 8.5pt;"))
        self.lbl_datasheet_text = QLabel(
            "IC 7408 Quad 2-Input AND Gate\nPackage: DIP-14\nVCC: Pin 14 (+5V)\nGND: Pin 7 (0V)"
        )
        self.lbl_datasheet_text.setWordWrap(True)
        self.lbl_datasheet_text.setStyleSheet("color: #94a3b8; font-size: 8pt; line-height: 1.3;")
        ds_lay.addWidget(self.lbl_datasheet_text)
        ds_lay.addStretch()
        insp_tabs.addTab(ds_widget, "Datasheet")

        # Tab 4: Hidden Developer Debug Inspector (Netlist Inspector)
        debug_widget = QWidget()
        db_lay = QVBoxLayout(debug_widget)
        db_lay.setContentsMargins(3, 3, 3, 3)
        db_lay.addWidget(QLabel("🔍 Netlist Inspector (Debug):", styleSheet="color: #eab308; font-weight: bold; font-size: 8.5pt;"))
        self.lbl_debug_info = QLabel("Netlist Engine initialized. Connect wires to inspect Electrical Nets.")
        self.lbl_debug_info.setWordWrap(True)
        self.lbl_debug_info.setStyleSheet("color: #cbd5e1; font-size: 7.5pt; font-family: Consolas, monospace;")
        db_lay.addWidget(self.lbl_debug_info)
        db_lay.addStretch()
        insp_tabs.addTab(debug_widget, "Netlist Debug")
        
        layout.addWidget(insp_tabs)
        return card

    def load_experiment(self, exp_id: str):
        exp_to_ic = {
            "and_gate": ("7408", 0),
            "gate_and": ("7408", 0),
            "or_gate": ("7432", 1),
            "gate_or": ("7432", 1),
            "not_gate": ("7404", 2),
            "gate_not": ("7404", 2),
            "nand_gate": ("7400", 3),
            "gate_nand": ("7400", 3),
            "nor_gate": ("7402", 4),
            "gate_nor": ("7402", 4),
            "xor_gate": ("7486", 5),
            "gate_xor": ("7486", 5),
            "xnor_gate": ("74266", 6),
            "gate_xnor": ("74266", 6),
            "half_adder": ("7486", 7),
            "full_adder": ("7486", 8),
            "mux_2_1": ("7408", 9),
            "decoder_2_4": ("7408", 10),
            "encoder_4_2": ("7408", 11),
            "d_flip_flop": ("7408", 12)
        }
        
        self.current_experiment = exp_id
        ic_key, combo_idx = exp_to_ic.get(exp_id, ("7408", 0))
        self.current_ic_key = ic_key

        if hasattr(self, 'exp_combo'):
            self.exp_combo.blockSignals(True)
            self.exp_combo.setCurrentIndex(combo_idx)
            self.exp_combo.blockSignals(False)

        ic_idx = self.ic_selector.findData(ic_key)
        if ic_idx != -1:
            self.ic_selector.blockSignals(True)
            self.ic_selector.setCurrentIndex(ic_idx)
            self.ic_selector.blockSignals(False)

        DigitalLogicEngine.validate_gate_truth_table(exp_id)

        self.build_2d_breadboard_grid()
        self.update_metadata_guided_flow()
        self.update_truth_table_ui()
        self.solve_circuit_logic()

    def on_experiment_combo_changed(self, idx):
        exp_id = self.exp_combo.itemData(idx)
        self.load_experiment(exp_id)

    def build_2d_breadboard_grid(self):
        self.canvas_scene.clear()
        
        self.net_engine.pins.clear()
        self.net_engine.register_pin("PWR_VCC_TERM", "POWER", "TRAINER_KIT")
        self.net_engine.register_pin("PWR_GND_TERM", "GROUND", "TRAINER_KIT")

        p1 = BreadboardHoleItem("PWR_VCC_TERM", 15, 18, radius=5, color_hex="#ef4444", border_hex="#fca5a5")
        self.canvas_scene.addItem(p1)
        p1_text = QGraphicsTextItem("+5V")
        p1_text.setFont(QFont("Arial", 6.5, QFont.Weight.Bold))
        p1_text.setDefaultTextColor(QColor("#ef4444"))
        p1_text.setPos(7, 26)
        self.canvas_scene.addItem(p1_text)
        
        p2 = BreadboardHoleItem("PWR_GND_TERM", 40, 18, radius=5, color_hex="#1e293b", border_hex="#64748b")
        self.canvas_scene.addItem(p2)
        p2_text = QGraphicsTextItem("GND")
        p2_text.setFont(QFont("Arial", 6.5, QFont.Weight.Bold))
        p2_text.setDefaultTextColor(QColor("#94a3b8"))
        p2_text.setPos(32, 26)
        self.canvas_scene.addItem(p2_text)
        
        inputs_keys = ["IN_A", "IN_B", "IN_C", "IN_D", "IN_E", "IN_F", "IN_G", "IN_H"]
        for idx, key in enumerate(inputs_keys):
            self.net_engine.register_pin(key, "INPUT", "TRAINER_KIT")
            x = 75 + (idx * 22)
            h = BreadboardHoleItem(key, x, 18, radius=4.5, color_hex="#0284c7", border_hex="#38bdf8")
            self.canvas_scene.addItem(h)
            t_label = QGraphicsTextItem(key.replace("IN_", ""))
            t_label.setFont(QFont("Arial", 6.5, QFont.Weight.Bold))
            t_label.setDefaultTextColor(QColor("#38bdf8"))
            t_label.setPos(x - 4, 26)
            self.canvas_scene.addItem(t_label)
            
        for idx, key in enumerate(self.OUTPUT_TERMINAL_KEYS):
            self.net_engine.register_pin(key, "OUTPUT", "TRAINER_KIT")
            x = 380 + (idx * 26)
            h = BreadboardHoleItem(key, x, 18, radius=5, color_hex="#047857", border_hex="#34d399")
            self.canvas_scene.addItem(h)
            t_label = QGraphicsTextItem(key.replace("OUT_", ""))
            t_label.setFont(QFont("Arial", 6.5, QFont.Weight.Bold))
            t_label.setDefaultTextColor(QColor("#34d399"))
            t_label.setPos(x - 7, 26)
            self.canvas_scene.addItem(t_label)
            
        bb_rect = QGraphicsRectItem(0, 44, 520, 275)
        bb_rect.setBrush(QBrush(QColor("#0f172a")))
        bb_rect.setPen(QPen(QColor("#334155"), 2))
        self.canvas_scene.addItem(bb_rect)
        
        title_item = QGraphicsTextItem("ELECTROVERSE SOLDERLESS BREADBOARD")
        title_item.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        title_item.setDefaultTextColor(QColor("#64748b"))
        title_item.setPos(140, 48)
        self.canvas_scene.addItem(title_item)
        
        for col in range(30):
            x = 25 + (col * 16)
            vcc_p = f"RAIL_VCC_TOP_{col}"
            gnd_p = f"RAIL_GND_TOP_{col}"
            self.net_engine.register_pin(vcc_p, "POWER", "BREADBOARD")
            self.net_engine.register_pin(gnd_p, "GROUND", "BREADBOARD")
            
            h1 = BreadboardHoleItem(vcc_p, x, 68, radius=4, color_hex="#450a0a", border_hex="#ef4444")
            self.canvas_scene.addItem(h1)
            h2 = BreadboardHoleItem(gnd_p, x, 84, radius=4, color_hex="#0f172a", border_hex="#64748b")
            self.canvas_scene.addItem(h2)
            
        for col in range(30):
            x = 25 + (col * 16)
            for row_idx, col_name in enumerate(["A", "B", "C", "D", "E"]):
                strip_p = f"STRIP_TOP_{col}_{col_name}"
                self.net_engine.register_pin(strip_p, "SIGNAL", "BREADBOARD")
                y = 108 + (row_idx * 14)
                h = BreadboardHoleItem(strip_p, x, y)
                self.canvas_scene.addItem(h)
                
        gap_line = QGraphicsLineItem(15, 184, 505, 184)
        gap_line.setPen(QPen(QColor("#1e293b"), 4))
        self.canvas_scene.addItem(gap_line)
        
        for col in range(30):
            x = 25 + (col * 16)
            for row_idx, col_name in enumerate(["F", "G", "H", "I", "J"]):
                strip_p = f"STRIP_BOT_{col}_{col_name}"
                self.net_engine.register_pin(strip_p, "SIGNAL", "BREADBOARD")
                y = 198 + (row_idx * 14)
                h = BreadboardHoleItem(strip_p, x, y)
                self.canvas_scene.addItem(h)
                
        for col in range(30):
            x = 25 + (col * 16)
            vcc_p = f"RAIL_VCC_BOT_{col}"
            gnd_p = f"RAIL_GND_BOT_{col}"
            self.net_engine.register_pin(vcc_p, "POWER", "BREADBOARD")
            self.net_engine.register_pin(gnd_p, "GROUND", "BREADBOARD")
            
            h1 = BreadboardHoleItem(vcc_p, x, 281, radius=4, color_hex="#450a0a", border_hex="#ef4444")
            self.canvas_scene.addItem(h1)
            h2 = BreadboardHoleItem(gnd_p, x, 297, radius=4, color_hex="#0f172a", border_hex="#64748b")
            self.canvas_scene.addItem(h2)
            
        ic_info = ECKBLoader.get_ic(self.current_ic_key) or {}
        pins_cnt = ic_info.get("pins", 14)
        half_pins = pins_cnt // 2
        
        ic_body_width = (half_pins * 16) + 6
        ic_body = QGraphicsRectItem(178, 172, ic_body_width, 24)
        ic_body.setBrush(QBrush(QColor("#0284c7")))
        ic_body.setPen(QPen(QColor("#38bdf8"), 2))
        self.canvas_scene.addItem(ic_body)
        
        notch = QGraphicsEllipseItem(174, 180, 8, 8)
        notch.setBrush(QBrush(QColor("#0f172a")))
        notch.setPen(QPen(QColor("#38bdf8"), 1))
        self.canvas_scene.addItem(notch)
        
        ic_lbl = QGraphicsTextItem(f"IC {self.current_ic_key}")
        ic_lbl.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        ic_lbl.setDefaultTextColor(QColor("#ffffff"))
        ic_lbl.setPos(188, 174)
        self.canvas_scene.addItem(ic_lbl)
        
        for i in range(half_pins):
            pin_num = i + 1
            col_idx = 10 + i
            hole_x = 25 + (col_idx * 16)
            hole_y = 164
            
            ic_pin_id = f"IC_PIN_{pin_num}"
            p_type = "GROUND" if pin_num == 7 else ("POWER" if pin_num == 14 else "SIGNAL")
            self.net_engine.register_pin(ic_pin_id, p_type, f"IC_{self.current_ic_key}")
            
            lead_line = QGraphicsLineItem(hole_x, 172, hole_x, hole_y)
            lead_line.setPen(QPen(QColor("#cbd5e1"), 2))
            self.canvas_scene.addItem(lead_line)
            
            pin_node = BreadboardHoleItem(ic_pin_id, hole_x, hole_y, radius=4, color_hex="#e2e8f0", border_hex="#94a3b8")
            self.canvas_scene.addItem(pin_node)
            
            num_txt = QGraphicsTextItem(str(pin_num))
            num_txt.setFont(QFont("Arial", 7, QFont.Weight.Bold))
            num_txt.setDefaultTextColor(QColor("#38bdf8"))
            num_txt.setPos(hole_x - 5, hole_y - 14)
            self.canvas_scene.addItem(num_txt)
            
        for i in range(half_pins):
            pin_num = pins_cnt - i
            col_idx = 10 + i
            hole_x = 25 + (col_idx * 16)
            hole_y = 198
            
            ic_pin_id = f"IC_PIN_{pin_num}"
            p_type = "GROUND" if pin_num == 7 else ("POWER" if pin_num == 14 else "SIGNAL")
            self.net_engine.register_pin(ic_pin_id, p_type, f"IC_{self.current_ic_key}")
            
            lead_line = QGraphicsLineItem(hole_x, 196, hole_x, hole_y)
            lead_line.setPen(QPen(QColor("#cbd5e1"), 2))
            self.canvas_scene.addItem(lead_line)
            
            pin_node = BreadboardHoleItem(ic_pin_id, hole_x, hole_y, radius=4, color_hex="#e2e8f0", border_hex="#94a3b8")
            self.canvas_scene.addItem(pin_node)
            
            num_txt = QGraphicsTextItem(str(pin_num))
            num_txt.setFont(QFont("Arial", 7, QFont.Weight.Bold))
            num_txt.setDefaultTextColor(QColor("#38bdf8"))
            num_txt.setPos(hole_x - 5, hole_y + 2)
            self.canvas_scene.addItem(num_txt)

    def auto_wire_preset(self):
        """Pre-places wires creating real electrical nets.
        
        IC pin layout awareness:
        - Standard (7408/7432/7400/7486): in_a=Pin1, in_b=Pin2, out=Pin3
        - Output-first (7402 NOR / 74266 XNOR): out=Pin1, in_a=Pin2, in_b=Pin3
        - Inverter (7404): in_a=Pin1, out=Pin2
        """
        self.canvas_scene.wires.clear()
        
        # 1. Red Wire: +5V to Pin 14
        w1 = WireLineItem(15, 18, 225, 198, "#ef4444", start_hole="PWR_VCC_TERM", end_hole="IC_PIN_14")
        self.canvas_scene.addItem(w1)
        self.canvas_scene.wires.append(w1)

        # 2. Black Wire: GND to Pin 7
        w2 = WireLineItem(40, 18, 225, 164, "#1e293b", start_hole="PWR_GND_TERM", end_hole="IC_PIN_7")
        self.canvas_scene.addItem(w2)
        self.canvas_scene.wires.append(w2)

        # Determine correct pin wiring based on IC datasheet pinout
        if self.current_ic_key == "7402":             # Output-first: out=Pin1, in_a=Pin2, in_b=Pin3
            pin_in_a, pin_in_b, pin_out = 2, 3, 1
        elif self.current_ic_key == "7404":            # NOT gate: in_a=Pin1, out=Pin2 (no pin_in_b)
            pin_in_a, pin_in_b, pin_out = 1, None, 2
        else:                                           # Standard: in_a=Pin1, in_b=Pin2, out=Pin3 (7408, 7432, 7400, 7486, 74266)
            pin_in_a, pin_in_b, pin_out = 1, 2, 3

        # 3. Cyan Wire: Input A to correct input pin
        in_a_x = 185 + (pin_in_a - 1) * 16
        w3 = WireLineItem(75, 18, in_a_x, 164, "#06b6d4", start_hole="IN_A", end_hole=f"IC_PIN_{pin_in_a}")
        self.canvas_scene.addItem(w3)
        self.canvas_scene.wires.append(w3)

        # 4. Cyan Wire: Input B to correct input pin (skip for NOT gate)
        if pin_in_b is not None:
            in_b_x = 185 + (pin_in_b - 1) * 16
            w4 = WireLineItem(97, 18, in_b_x, 164, "#06b6d4", start_hole="IN_B", end_hole=f"IC_PIN_{pin_in_b}")
            self.canvas_scene.addItem(w4)
            self.canvas_scene.wires.append(w4)

        # 5. Green Wire: correct output pin to Output Y0
        out_x = 185 + (pin_out - 1) * 16
        w5 = WireLineItem(out_x, 164, 380, 18, "#10b981", start_hole=f"IC_PIN_{pin_out}", end_hole="OUT_Y0")
        self.canvas_scene.addItem(w5)
        self.canvas_scene.wires.append(w5)

        self.solve_circuit_logic()

    def update_metadata_guided_flow(self):
        ic_info = ECKBLoader.get_ic(self.current_ic_key) or {}
        vcc_pin = ic_info.get("vcc_pin", 14)
        gnd_pin = ic_info.get("gnd_pin", 7)
        pin_map = ECKBLoader.get_pin_map(self.current_ic_key) or {}
        
        # IC 7402 (NOR) uses output-first pinout; all other quad gates (including 74266 XNOR) use input-first pinout
        if self.current_ic_key == "7402":
            gate_mappings = [
                {"in_a": 2, "in_b": 3, "out": 1, "target_y": "Y0"},
                {"in_a": 5, "in_b": 6, "out": 4, "target_y": "Y1"},
                {"in_a": 8, "in_b": 9, "out": 10, "target_y": "Y2"},
                {"in_a": 11, "in_b": 12, "out": 13, "target_y": "Y3"}
            ]
        else:
            gate_mappings = [
                {"in_a": 1, "in_b": 2, "out": 3, "target_y": "Y0"},
                {"in_a": 4, "in_b": 5, "out": 6, "target_y": "Y1"},
                {"in_a": 9, "in_b": 10, "out": 8, "target_y": "Y2"},
                {"in_a": 12, "in_b": 13, "out": 11, "target_y": "Y3"}
            ]
        active_gate = gate_mappings[min(self.current_gate_idx, len(gate_mappings)-1)]
        
        pin_a_label = pin_map.get(str(active_gate["in_a"]), f"Pin {active_gate['in_a']}")
        pin_b_label = pin_map.get(str(active_gate["in_b"]), f"Pin {active_gate['in_b']}")
        pin_out_label = pin_map.get(str(active_gate["out"]), f"Pin {active_gate['out']}")
        
        self.guided_connections = [
            {
                "step": 1,
                "from": "+5V Power Terminal",
                "to": f"Top Power Rail -> Pin {vcc_pin} (VCC)",
                "color": "Red Wire",
                "hex": "#ef4444",
                "purpose": "IC Power Supply (+5V)",
                "reason": f"Connect +5V Power Terminal to Pin {vcc_pin}. Reason: Powers internal logic gates."
            },
            {
                "step": 2,
                "from": "GND Power Terminal",
                "to": f"Ground Rail -> Pin {gnd_pin} (GND)",
                "color": "Black Wire",
                "hex": "#1e293b",
                "purpose": "IC Ground Return (0V)",
                "reason": f"Connect GND Terminal to Pin {gnd_pin}. Reason: Completes power circuit."
            },
            {
                "step": 3,
                "from": "Input Terminal A / D",
                "to": f"Pin {active_gate['in_a']} ({pin_a_label})",
                "color": "Cyan Wire",
                "hex": "#06b6d4",
                "purpose": f"Input Signal (Gate {self.current_gate_idx+1})",
                "reason": f"Connect Input Terminal to Pin {active_gate['in_a']}. Reason: Supplies digital logic signal."
            },
            {
                "step": 4,
                "from": "Input Terminal B / E",
                "to": f"Pin {active_gate['in_b']} ({pin_b_label})",
                "color": "Cyan Wire",
                "hex": "#06b6d4",
                "purpose": f"Input Signal (Gate {self.current_gate_idx+1})",
                "reason": f"Connect Input Terminal to Pin {active_gate['in_b']}. Reason: Supplies digital logic signal."
            },
            {
                "step": 5,
                "from": f"Pin {active_gate['out']} ({pin_out_label})",
                "to": f"Output Terminal {active_gate['target_y']}",
                "color": "Green Wire",
                "hex": "#10b981",
                "purpose": f"Output Y Drive (Gate {self.current_gate_idx+1})",
                "reason": f"Connect Output Pin {active_gate['out']} to Output Terminal {active_gate['target_y']}. Reason: Drives LED indicator."
            }
        ]
        
        self.update_card_ui()

    def update_card_ui(self):
        self.current_step_idx = max(0, min(self.current_step_idx, len(self.guided_connections) - 1))
        conn = self.guided_connections[self.current_step_idx]
        
        self.lbl_assistant_title.setText(f"──────  NEXT CONNECTION (Card {self.current_step_idx + 1} of {len(self.guided_connections)})  ──────")
        self.lbl_conn_counter.setText(f"Conn: {self.current_step_idx + 1}/{len(self.guided_connections)}")
        
        pct = int(((self.current_step_idx + 1) / len(self.guided_connections)) * 100)
        self.progress_guided.setValue(pct)
        
        self.lbl_card_from.setText(conn["from"])
        self.lbl_card_from.setStyleSheet(f"color: {conn['hex']}; font-weight: bold; font-size: 8.5pt;")
        
        self.lbl_card_to.setText(conn["to"])
        self.lbl_card_to.setStyleSheet(f"color: {conn['hex']}; font-weight: bold; font-size: 8.5pt;")
        
        self.lbl_card_color.setText(conn["color"])
        self.lbl_card_color.setStyleSheet(f"color: {conn['hex']}; font-weight: bold; font-size: 8.5pt;")
        
        self.lbl_card_purpose.setText(conn["purpose"])
        self.lbl_card_reason.setText(conn["reason"])
        
        self.populate_steps_list()

    def populate_steps_list(self):
        self.list_steps.clear()
        for idx, conn in enumerate(self.guided_connections):
            prefix = "✓ " if idx < self.current_step_idx else ("👉 " if idx == self.current_step_idx else "  ")
            item_text = f"{prefix}Step {idx+1}: {conn['from']} -> {conn['to']}"
            item = QListWidgetItem(item_text)
            if idx < self.current_step_idx:
                item.setForeground(QColor("#10b981"))
            elif idx == self.current_step_idx:
                item.setForeground(QColor("#38bdf8"))
            else:
                item.setForeground(QColor("#64748b"))
            self.list_steps.addItem(item)

    def update_truth_table_ui(self):
        """Single Source of Truth: Updates Truth Table from logic evaluation."""
        self.table_truth.setRowCount(4)
        exp = self.current_experiment
        rows = [
            (0, 0, DigitalLogicEngine.evaluate_experiment(exp, {"IN_A": 0, "IN_B": 0})["OUT_Y0"]),
            (0, 1, DigitalLogicEngine.evaluate_experiment(exp, {"IN_A": 0, "IN_B": 1})["OUT_Y0"]),
            (1, 0, DigitalLogicEngine.evaluate_experiment(exp, {"IN_A": 1, "IN_B": 0})["OUT_Y0"]),
            (1, 1, DigitalLogicEngine.evaluate_experiment(exp, {"IN_A": 1, "IN_B": 1})["OUT_Y0"])
        ]
        
        curr_a = self.inputs_state.get("IN_A", 0)
        curr_b = self.inputs_state.get("IN_B", 0)

        for r, (a, b, y) in enumerate(rows):
            item_a = QTableWidgetItem(str(a))
            item_b = QTableWidgetItem(str(b))
            item_y = QTableWidgetItem(str(y))

            if a == curr_a and b == curr_b:
                for item in [item_a, item_b, item_y]:
                    item.setBackground(QColor("#0369a1"))
                    item.setForeground(QColor("#ffffff"))

            self.table_truth.setItem(r, 0, item_a)
            self.table_truth.setItem(r, 1, item_b)
            self.table_truth.setItem(r, 2, item_y)

    def advance_guided_step(self):
        if self.current_step_idx < len(self.guided_connections) - 1:
            self.current_step_idx += 1
            self.update_card_ui()

    def prev_guided_step(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            self.update_card_ui()

    def on_ic_selection_changed(self, index):
        ic_key = self.ic_selector.itemData(index) or "7408"
        self.current_ic_key = ic_key
        
        ic_to_exp = {
            "7408": "and_gate",
            "7432": "or_gate",
            "7404": "not_gate",
            "7400": "nand_gate",
            "7402": "nor_gate",
            "7486": "xor_gate",
            "74266": "xnor_gate",
            "7411": "and_gate"
        }
        if ic_key in ic_to_exp:
            self.current_experiment = ic_to_exp[ic_key]
            exp_combo_idx = self.exp_combo.findData(self.current_experiment)
            if exp_combo_idx != -1:
                self.exp_combo.blockSignals(True)
                self.exp_combo.setCurrentIndex(exp_combo_idx)
                self.exp_combo.blockSignals(False)

        log.info(f"[DSDLabView] IC Selector Changed to {ic_key} | Experiment synchronized to {self.current_experiment}")
        self.build_2d_breadboard_grid()
        self.update_metadata_guided_flow()
        self.update_truth_table_ui()
        self.solve_circuit_logic()

    def on_gate_index_changed(self, index):
        self.current_gate_idx = index
        self.update_metadata_guided_flow()
        self.solve_circuit_logic()

    def on_beginner_mode_toggled(self, checked):
        self.beginner_mode = checked
        self.banner_assistant.setVisible(checked)

    def on_sim_tick(self):
        if not self.power_on or not self.is_simulating:
            return
        if self.current_experiment == "d_flip_flop":
            self.step_counter += 1
            if self.step_counter >= max(1, int(30 / (self.clock_hz * 2))):
                self.step_counter = 0
                self.clock_state = 1 if self.clock_state == 0 else 0
                self.solve_circuit_logic()

    def solve_circuit_logic(self):
        """Executes Single-Source-of-Truth Node-Based Circuit Netlist Propagation Pipeline:
        
        Pipeline:
        1. Update Nets (Rebuild ElectricalNet list via BFS graph traversal)
        2. Validate Power Rails & Circuit Completeness
        3. Propagate Inputs -> ElectricalPins -> ElectricalNets
        4. Evaluate Gate Transfer Functions per IC datasheet pin definitions
        5. Propagate IC Output Pins -> ElectricalNets -> Output Terminals Y0-Y3
        6. Refresh Output LEDs
        7. Refresh Truth Table Inspector
        8. Refresh Status Panel & Debug Inspector
        """
        wires = self.canvas_scene.wires if hasattr(self, 'canvas_scene') else []

        # 1. Update Nets
        self.net_engine.build_nets(wires)

        # 2. Validate Power Rails & Completeness
        is_ic_powered = self.net_engine.validate_power_rails(self.current_ic_key, self.power_on, len(wires) > 0)

        # 3. Propagate Input Terminals -> Net Voltages
        for input_key in ["IN_A", "IN_B", "IN_C", "IN_D", "IN_E", "IN_F", "IN_G", "IN_H"]:
            pin_obj = self.net_engine.pins.get(input_key)
            if pin_obj:
                pin_obj.logic_state = self.inputs_state.get(input_key, 0)

        for net in self.net_engine.nets:
            net.voltage = 0
            for pin in net.pins:
                if pin.pin_type == "INPUT" and pin.logic_state == 1:
                    net.voltage = 1
                    break
                elif pin.pin_type == "POWER":
                    net.voltage = 1
                    break

        for pin_id, pin in self.net_engine.pins.items():
            if pin.connected_net_id:
                net = next((n for n in self.net_engine.nets if n.net_id == pin.connected_net_id), None)
                if net:
                    pin.logic_state = net.voltage

        ic_key = self.current_ic_key

        # Datasheet Pin Definitions for 14-pin ICs
        if ic_key == "7402":  # NOR (7402): Output-first pinout (1Y=1, 1A=2, 1B=3)
            gates = [
                {"gate_id": 1, "in_a": 2, "in_b": 3, "out": 1, "target_y": "OUT_Y0"},
                {"gate_id": 2, "in_a": 5, "in_b": 6, "out": 4, "target_y": "OUT_Y1"},
                {"gate_id": 3, "in_a": 8, "in_b": 9, "out": 10, "target_y": "OUT_Y2"},
                {"gate_id": 4, "in_a": 11, "in_b": 12, "out": 13, "target_y": "OUT_Y3"}
            ]
        elif ic_key == "7404":  # NOT gate IC layout
            gates = [
                {"gate_id": 1, "in_a": 1, "in_b": None, "out": 2, "target_y": "OUT_Y0"},
                {"gate_id": 2, "in_a": 3, "in_b": None, "out": 4, "target_y": "OUT_Y1"},
                {"gate_id": 3, "in_a": 5, "in_b": None, "out": 6, "target_y": "OUT_Y2"},
                {"gate_id": 4, "in_a": 9, "in_b": None, "out": 8, "target_y": "OUT_Y3"}
            ]
        else:  # Quad 2-Input Gates: Input-first pinout (7408 AND, 7432 OR, 7400 NAND, 7486 XOR, 74266 XNOR)
            gates = [
                {"gate_id": 1, "in_a": 1, "in_b": 2, "out": 3, "target_y": "OUT_Y0"},
                {"gate_id": 2, "in_a": 4, "in_b": 5, "out": 6, "target_y": "OUT_Y1"},
                {"gate_id": 3, "in_a": 9, "in_b": 10, "out": 8, "target_y": "OUT_Y2"},
                {"gate_id": 4, "in_a": 12, "in_b": 13, "out": 11, "target_y": "OUT_Y3"}
            ]

        # 4. Evaluate Gate Transfer Functions
        pin_outputs = {}
        if is_ic_powered:
            for g_info in gates:
                pa = g_info["in_a"]
                pb = g_info["in_b"]
                p_out = g_info["out"]

                pa_pin = self.net_engine.pins.get(f"IC_PIN_{pa}")
                pb_pin = self.net_engine.pins.get(f"IC_PIN_{pb}") if pb is not None else None

                val_a = pa_pin.logic_state if pa_pin else 0
                val_b = pb_pin.logic_state if pb_pin else 0

                # Unwired default mode: active gate section uses IN_A and IN_B
                if len(wires) == 0:
                    if g_info["gate_id"] == self.current_gate_idx + 1:
                        val_a = self.inputs_state.get("IN_A", 0)
                        val_b = self.inputs_state.get("IN_B", 0)

                gate_inputs = [val_a, val_b] if pb is not None else [val_a]
                out_val = DigitalLogicEngine.evaluate_gate(ic_key, gate_inputs)
                pin_outputs[p_out] = out_val

                p_out_pin = self.net_engine.pins.get(f"IC_PIN_{p_out}")
                if p_out_pin:
                    p_out_pin.logic_state = out_val
                    if p_out_pin.connected_net_id:
                        out_net = next((n for n in self.net_engine.nets if n.net_id == p_out_pin.connected_net_id), None)
                        if out_net:
                            out_net.voltage = out_val
        else:
            for g_info in gates:
                pin_outputs[g_info["out"]] = 0

        # 5. Propagate Electrical Nets -> Output Terminals Y0-Y3
        new_outputs = {"OUT_Y0": 0, "OUT_Y1": 0, "OUT_Y2": 0, "OUT_Y3": 0}

        if self.current_experiment in ["half_adder", "full_adder", "decoder_2_4", "encoder_4_2", "mux_2_1", "d_flip_flop"]:
            if is_ic_powered:
                outs = DigitalLogicEngine.evaluate_experiment(self.current_experiment, self.inputs_state, self.clock_state)
                for k, v in outs.items():
                    new_outputs[k] = v
        else:
            for term_key in self.OUTPUT_TERMINAL_KEYS:
                term_pin = self.net_engine.pins.get(term_key)
                if term_pin and term_pin.connected_net_id:
                    t_net = next((n for n in self.net_engine.nets if n.net_id == term_pin.connected_net_id), None)
                    if t_net:
                        new_outputs[term_key] = t_net.voltage
                        log.info(f"[NetlistSolver] Wire Net Connected: {term_key} ({t_net.voltage})")

            if len(wires) == 0:
                # Active Gate Selection Output Mapping in unwired mode:
                # Gate 1 -> Y0, Gate 2 -> Y1, Gate 3 -> Y2, Gate 4 -> Y3
                active_g_info = gates[min(self.current_gate_idx, len(gates)-1)]
                active_out_pin = active_g_info["out"]
                active_target_y = active_g_info["target_y"]
                new_outputs[active_target_y] = pin_outputs.get(active_out_pin, 0)

        self.outputs_state = new_outputs

        # 6. Refresh Output LEDs
        self.refresh_output_leds()

        # 7. Refresh Truth Table Inspector (Synchronized Single Source of Truth)
        self.update_truth_table_ui()

        # 8. Refresh Status Panel & Debug Inspector
        self.refresh_status_and_debug_panel(is_ic_powered)

    def refresh_output_leds(self):
        """Refreshes output LED labels Y0, Y1, Y2, Y3 using strict netlist logic state."""
        for term_key in self.OUTPUT_TERMINAL_KEYS:
            val = self.outputs_state.get(term_key, 0)
            lbl_widget = self.output_led_widgets.get(term_key)
            if lbl_widget:
                self.update_output_terminal_ui(term_key, lbl_widget, val)

    def update_output_terminal_ui(self, term_key, lbl_widget, val):
        name = term_key.replace("OUT_", "")
        if val == 1:
            lbl_widget.setText(f"{name}: HIGH (5V) [ON]")
            lbl_widget.setStyleSheet("background-color: #047857; color: #ffffff; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")
        else:
            lbl_widget.setText(f"{name}: OFF (0V)")
            lbl_widget.setStyleSheet("background-color: #1e293b; color: #64748b; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")

    def refresh_status_and_debug_panel(self, is_powered: bool):
        if not self.power_on:
            self.lbl_status_led.setText("● POWER OFF")
            self.lbl_status_led.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
            self.lbl_diag_msg.setText("Circuit Incomplete: Digital Trainer Kit is powered off.")
        elif not is_powered:
            self.lbl_status_led.setText("● Circuit Incomplete (IC UNPOWERED)")
            self.lbl_status_led.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 8.5pt;")
            self.lbl_diag_msg.setText(f"Circuit Incomplete: IC {self.current_ic_key} Pin 14 (+5V VCC) or Pin 7 (GND) is missing!")
        else:
            self.lbl_status_led.setText("● +5V POWER ON & OPERATIONAL")
            self.lbl_status_led.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
            self.lbl_diag_msg.setText(f"Trainer Kit Operational: IC {self.current_ic_key} (Gate {self.current_gate_idx+1}) evaluated via Shared Netlist Engine.")

        net_summary = [
            f"IC: {self.current_ic_key} | Powered: {is_powered}",
            f"Active Gate Section: Gate {self.current_gate_idx+1}",
            f"Total Pins: {len(self.net_engine.pins)} | Total Nets: {len(self.net_engine.nets)}",
            "--- Active Output Net Routing ---"
        ]
        for term_key in self.OUTPUT_TERMINAL_KEYS:
            st = self.outputs_state.get(term_key, 0)
            net_summary.append(f"{term_key.replace('OUT_', '')}: {'HIGH (5V)' if st == 1 else 'LOW (0V)'}")

        if hasattr(self, 'lbl_debug_info'):
            self.lbl_debug_info.setText("\n".join(net_summary))

    def on_event_switch_toggled(self, terminal="IN_A", logic=0):
        log.info(f"[DSDLabView] EventBus SWITCH_TOGGLED received: {terminal}={logic}")
        self.solve_circuit_logic()

    def on_event_power_changed(self, power_on=True):
        log.info(f"[DSDLabView] EventBus POWER_CHANGED received: Power={power_on}")
        self.solve_circuit_logic()

    def toggle_simulation_mode(self):
        self.is_simulating = not self.is_simulating
        if self.is_simulating:
            self.btn_sim_toggle.setText(" ▶ Start Simulation")
            self.btn_sim_toggle.setStyleSheet("background-color: #06b6d4; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
        else:
            self.btn_sim_toggle.setText(" ⏹ Stop Simulation")
            self.btn_sim_toggle.setStyleSheet("background-color: #eab308; color: black; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")

    def toggle_power(self):
        self.power_on = not self.power_on
        if self.power_on:
            self.btn_power.setText(" +5V Power ON")
            self.btn_power.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
        else:
            self.btn_power.setText(" Power OFF")
            self.btn_power.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
        EventBus.publish(EventChannels.POWER_CHANGED, power_on=self.power_on)
        self.solve_circuit_logic()

    def on_clk_hz_changed(self, val):
        self.clock_hz = float(val) / 2.0
        self.lbl_clk_hz.setText(f"{self.clock_hz:.1f} Hz")

    def reset_workspace(self):
        self.inputs_state = {
            "IN_A": 0, "IN_B": 0, "IN_C": 0, "IN_D": 0,
            "IN_E": 0, "IN_F": 0, "IN_G": 0, "IN_H": 0
        }
        self.outputs_state = {"OUT_Y0": 0, "OUT_Y1": 0, "OUT_Y2": 0, "OUT_Y3": 0}
        for btn in self.input_btns.values():
            btn.setChecked(False)
        self.current_step_idx = 0
        self.build_2d_breadboard_grid()
        self.update_metadata_guided_flow()
        self.solve_circuit_logic()


# ==============================================================================
# 5. AUTOMATED SIMULATION VERIFICATION SUITE (Requirement 10 Audit)
# ==============================================================================

def run_trainer_kit_verification_suite():
    """Requirement 10 Audit: Automatically tests all ICs (7408, 7432, 7486, 7404, 7400, 7402)
    across all four gates individually and all input combinations (00, 01, 10, 11).
    """
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    view = DSDLabView()
    ics_to_test = ["7408", "7432", "7486", "7404", "7400", "7402"]
    
    total_tests = 0
    passed_tests = 0

    log.info("[VerificationSuite] Starting Automated Verification Audit for Trainer Kit Logic Engine...")

    for ic_key in ics_to_test:
        ic_idx = view.ic_selector.findData(ic_key)
        if ic_idx != -1:
            view.ic_selector.setCurrentIndex(ic_idx)

        # Test each gate section 0..3 (Gate 1..4)
        for gate_idx in range(4):
            view.on_gate_index_changed(gate_idx)
            
            # Test truth table input combinations
            test_combinations = [(0, 0), (0, 1), (1, 0), (1, 1)]
            for in_a_val, in_b_val in test_combinations:
                total_tests += 1
                view.inputs_state["IN_A"] = in_a_val
                view.inputs_state["IN_B"] = in_b_val
                view.solve_circuit_logic()

                target_y_key = f"OUT_Y{gate_idx}"
                actual_y_val = view.outputs_state.get(target_y_key, 0)
                
                # Check other Y outputs are isolated
                other_y_vals = [view.outputs_state.get(k, 0) for k in view.OUTPUT_TERMINAL_KEYS if k != target_y_key]
                
                expected_gate_out = DigitalLogicEngine.evaluate_gate(ic_key, [in_a_val, in_b_val])
                
                assert actual_y_val == expected_gate_out, (
                    f"Audit Mismatch on IC {ic_key} Gate {gate_idx+1} (In: {in_a_val},{in_b_val}): "
                    f"Expected {expected_gate_out}, Actual {actual_y_val}"
                )
                assert all(v == 0 for v in other_y_vals), (
                    f"Output Isolation Mismatch on IC {ic_key} Gate {gate_idx+1}: "
                    f"Other Y outputs were not 0! {view.outputs_state}"
                )
                passed_tests += 1

    log.info(f"[VerificationSuite] AUDIT COMPLETE: Passed {passed_tests}/{total_tests} verification tests cleanly!")
    return True
