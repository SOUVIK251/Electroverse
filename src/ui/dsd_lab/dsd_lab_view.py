"""
Metadata-Driven Digital System Design Lab & Trainer Kit Simulator
==================================================================
Engineering-grade simulator implementing realistic DIP-14 & DIP-16 IC packages,
all 7 fundamental logic gates (AND, OR, NOT, NOR, NAND, XOR, XNOR),
metallic lead pins, permanent pin numbers, dynamic pin labels from ic_pin_map.json,
trainer-kit POWER, INPUT (A-H), and OUTPUT terminal blocks (Y0-Y3),
plus Interactive Wire Eraser with Midpoint "-" Delete Sign & Dynamic Multi-Output Terminal Routing.
"""

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
# 1. 2D BREADBOARD & TERMINAL GRAPHICS ITEMS
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
# 2. ELECTRICAL LOGIC ENGINE (Supports all 7 Gate Types)
# ==============================================================================

class DigitalLogicEngine:
    """Single Source of Truth: Evaluates all fundamental logic gates."""

    @classmethod
    def evaluate_gate(cls, gate_type: str, inputs: list) -> int:
        """Solves boolean logic for AND, OR, NOT, NOR, NAND, XOR, XNOR, AND3."""
        gt = gate_type.upper()
        if "XNOR" in gt:
            return 0 if (inputs[0] ^ inputs[1]) == 1 else 1
        elif "XOR" in gt:
            return 1 if (inputs[0] ^ inputs[1]) == 1 else 0
        elif "NAND" in gt:
            return 0 if all(v == 1 for v in inputs) else 1
        elif "NOR" in gt:
            return 0 if any(v == 1 for v in inputs) else 1
        elif "AND3" in gt:
            return 1 if all(v == 1 for v in inputs[:3]) else 0
        elif "AND" in gt:
            return 1 if all(v == 1 for v in inputs) else 0
        elif "OR" in gt:
            return 1 if any(v == 1 for v in inputs) else 0
        elif "NOT" in gt or "INVERTER" in gt:
            return 0 if inputs[0] == 1 else 1
        return 0


# ==============================================================================
# 3. METADATA-DRIVEN TRAINER KIT VIEW
# ==============================================================================

class DSDLabView(QWidget):
    """Metadata-Driven Trainer Kit UI Revision."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.power_on = True
        self.is_simulating = True
        self.clock_state = 0
        self.clock_hz = 2.0
        self.step_counter = 0
        
        # Power, Input (A-H), and Output States
        self.inputs_state = {
            "IN_A": 0, "IN_B": 0, "IN_C": 0, "IN_D": 0,
            "IN_E": 0, "IN_F": 0, "IN_G": 0, "IN_H": 0
        }
        self.outputs_state = {"OUT_Y0": 0, "OUT_Y1": 0, "OUT_Y2": 0, "OUT_Y3": 0}
        
        # Beginner Mode & Guided Wiring Assistant State
        self.beginner_mode = True
        self.current_ic_key = "7432"
        self.current_gate_idx = 0
        self.current_step_idx = 0
        
        # Load ECKB Datasets
        ECKBLoader.initialize()
        self.grid_data = ECKBLoader.get_dataset("breadboard_grid")
        self.comp_data = ECKBLoader.get_dataset("canvas_components")
        self.input_term_data = ECKBLoader.get_dataset("input_terminals").get("terminals", [])
        self.output_term_data = ECKBLoader.get_dataset("output_terminals").get("terminals", [])
        self.wire_styles = ECKBLoader.get_dataset("wire_styles").get("styles", {})
        
        self.init_ui()
        self.subscribe_events()
        self.update_metadata_guided_flow()
        
        # Simulation Loop (30 FPS)
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
        
        # Top Control Bar
        top_bar = self.create_top_control_bar()
        main_layout.addWidget(top_bar)
        
        # Wire Color Palette Bar
        color_bar = self.create_wire_color_palette()
        main_layout.addWidget(color_bar)
        
        # TOP 3-COLUMN HEADER ROW
        top_header_row = QHBoxLayout()
        top_header_row.setSpacing(6)
        
        input_panel = self.create_input_terminal_panel()
        top_header_row.addWidget(input_panel, 1)
        
        card_panel = self.create_next_connection_card_panel()
        top_header_row.addWidget(card_panel, 2)
        
        output_panel = self.create_output_terminal_panel()
        top_header_row.addWidget(output_panel, 1)
        
        main_layout.addLayout(top_header_row)
        
        # MAIN WORK SPLITTER
        work_splitter = QSplitter(Qt.Orientation.Horizontal)
        work_splitter.setHandleWidth(3)
        
        left_toolbox = self.create_left_toolbox()
        work_splitter.addWidget(left_toolbox)
        
        center_workbench = self.create_center_workbench()
        work_splitter.addWidget(center_workbench)
        
        right_inspector = self.create_right_inspector()
        work_splitter.addWidget(right_inspector)
        
        work_splitter.setSizes([200, 620, 240])
        main_layout.addWidget(work_splitter, 1)
        
        # Status Bar
        self.status_bar_frame = QFrame()
        self.status_bar_frame.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 4px; padding: 3px 6px;")
        sb_lay = QHBoxLayout(self.status_bar_frame)
        sb_lay.setContentsMargins(5, 2, 5, 2)
        
        self.lbl_status_led = QLabel("● +5V POWER ON")
        self.lbl_status_led.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
        
        self.lbl_diag_msg = QLabel("Lab Instructor: All 7 Logic Gate ICs (AND, OR, NOT, NOR, NAND, XOR, XNOR) Active.")
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
        
        lbl_wire = QLabel("🎨 Wire Color Swatch:")
        lbl_wire.setStyleSheet("color: #f8fafc; font-weight: bold; font-size: 8.5pt;")
        lay.addWidget(lbl_wire)
        
        swatches = [
            ("Red (+5V)", "#ef4444"),
            ("Black (GND)", "#1e293b"),
            ("Cyan (Signal)", "#06b6d4"),
            ("Yellow (Clock)", "#eab308"),
            ("Green (HIGH)", "#10b981"),
            ("Blue (LOW)", "#3b82f6"),
            ("Orange", "#f97316"),
            ("Purple", "#a855f7"),
            ("White", "#f8fafc")
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
            if self.main_window and hasattr(self.main_window, "show_toast"):
                self.main_window.show_toast("Eraser Mode Enabled. Click any wire to delete." if checked else "Eraser Mode Disabled.")

    def create_input_terminal_panel(self):
        """Trainer Kit Power & 8-Input (A-H) Terminal Section."""
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
            
        self.btn_in_a = self.input_btns["IN_A"]
        self.btn_in_b = self.input_btns["IN_B"]
        self.btn_in_c = self.input_btns["IN_C"]
        self.btn_in_d = self.input_btns["IN_D"]
        self.btn_in_e = self.input_btns["IN_E"]
        self.btn_in_f = self.input_btns["IN_F"]
        self.btn_in_g = self.input_btns["IN_G"]
        self.btn_in_h = self.input_btns["IN_H"]
        
        lay.addLayout(grid)
        return card

    def create_next_connection_card_panel(self):
        """Structured Next Connection Card Panel."""
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
        """Trainer Kit Output Terminal Section (Y0, Y1, Y2, Y3)."""
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
        
        self.lbl_out_y0 = QLabel("Y0: OFF (0V)")
        self.lbl_out_y0.setStyleSheet("background-color: #1e293b; color: #64748b; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")
        grid.addWidget(self.lbl_out_y0, 0, 0)
        
        self.lbl_out_y1 = QLabel("Y1: OFF (0V)")
        self.lbl_out_y1.setStyleSheet("background-color: #1e293b; color: #64748b; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")
        grid.addWidget(self.lbl_out_y1, 0, 1)
        
        self.lbl_out_y2 = QLabel("Y2: OFF (0V)")
        self.lbl_out_y2.setStyleSheet("background-color: #1e293b; color: #64748b; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")
        grid.addWidget(self.lbl_out_y2, 1, 0)
        
        self.lbl_out_y3 = QLabel("Y3: OFF (0V)")
        self.lbl_out_y3.setStyleSheet("background-color: #1e293b; color: #64748b; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")
        grid.addWidget(self.lbl_out_y3, 1, 1)
        
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
        
        layout.addWidget(QLabel("🧰 All Fundamental Gate ICs"))
        
        self.ic_selector = QComboBox()
        self.ic_selector.addItem("IC 7400 (Quad 2-Input NAND)", "7400")
        self.ic_selector.addItem("IC 7402 (Quad 2-Input NOR)", "7402")
        self.ic_selector.addItem("IC 7404 (Hex Inverter NOT)", "7404")
        self.ic_selector.addItem("IC 7408 (Quad 2-Input AND)", "7408")
        self.ic_selector.addItem("IC 7411 (Triple 3-Input AND)", "7411")
        self.ic_selector.addItem("IC 7432 (Quad 2-Input OR)", "7432")
        self.ic_selector.addItem("IC 7486 (Quad 2-Input XOR)", "7486")
        self.ic_selector.addItem("IC 74266 (Quad 2-Input XNOR)", "74266")
        self.ic_selector.currentIndexChanged.connect(self.on_ic_selection_changed)
        layout.addWidget(QLabel("Select IC Package:"))
        layout.addWidget(self.ic_selector)
        
        self.combo_gate_select = QComboBox()
        self.combo_gate_select.addItems(["Gate 1 (Pins 1,2 -> Pin 3)", "Gate 2 (Pins 4,5 -> Pin 6)", "Gate 3 (Pins 9,10 -> Pin 8)", "Gate 4 (Pins 12,13 -> Pin 11)"])
        self.combo_gate_select.currentIndexChanged.connect(self.on_gate_index_changed)
        layout.addWidget(QLabel("Select Active IC Gate:"))
        layout.addWidget(self.combo_gate_select)
        
        layout.addSpacing(6)
        self.lbl_gate_desc = QLabel("IC 7432 Metadata:\nVCC: Pin 14 (+5V)\nGND: Pin 7 (0V)\nActive Gate 1: Pin 1 (1A), Pin 2 (1B) -> Pin 3 (1Y)")
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
        
        steps_widget = QWidget()
        st_lay = QVBoxLayout(steps_widget)
        st_lay.setContentsMargins(3, 3, 3, 3)
        
        st_lay.addWidget(QLabel("📋 Connections Checklist:"))
        self.list_steps = QListWidget()
        self.list_steps.setStyleSheet("QListWidget { background-color: #0b0f19; color: #f8fafc; border: 1px solid #1e293b; border-radius: 4px; } QListWidget::item { padding: 3px; font-size: 8pt; }")
        st_lay.addWidget(self.list_steps)
        
        insp_tabs.addTab(steps_widget, "Checklist")
        
        ds_widget = QWidget()
        ds_lay = QVBoxLayout(ds_widget)
        ds_lay.setContentsMargins(3, 3, 3, 3)
        
        ds_lay.addWidget(QLabel("📄 Datasheet Quick View:"))
        self.lbl_datasheet_text = QLabel(
            "IC 7432 Quad 2-Input OR Gate\n"
            "Manufacturer: Texas Instruments\n"
            "Package: DIP-14\n"
            "VCC: Pin 14 (+5.0V)\n"
            "GND: Pin 7 (0.0V)\n"
            "Supply Voltage: 4.75V to 5.25V\n"
            "Propagation Delay: 10 ns"
        )
        self.lbl_datasheet_text.setWordWrap(True)
        self.lbl_datasheet_text.setStyleSheet("color: #94a3b8; font-size: 8pt; line-height: 1.3;")
        ds_lay.addWidget(self.lbl_datasheet_text)
        ds_lay.addStretch()
        
        insp_tabs.addTab(ds_widget, "Datasheet")
        
        layout.addWidget(insp_tabs)
        return card

    def build_2d_breadboard_grid(self):
        """Constructs 2D Solderless Breadboard Grid on QGraphicsScene."""
        self.canvas_scene.clear()
        
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
            x = 75 + (idx * 22)
            h = BreadboardHoleItem(key, x, 18, radius=4.5, color_hex="#0284c7", border_hex="#38bdf8")
            self.canvas_scene.addItem(h)
            t_label = QGraphicsTextItem(key.replace("IN_", ""))
            t_label.setFont(QFont("Arial", 6.5, QFont.Weight.Bold))
            t_label.setDefaultTextColor(QColor("#38bdf8"))
            t_label.setPos(x - 4, 26)
            self.canvas_scene.addItem(t_label)
            
        for idx, key in enumerate(["OUT_Y0", "OUT_Y1", "OUT_Y2", "OUT_Y3"]):
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
            h1 = BreadboardHoleItem(f"RAIL_VCC_TOP_{col}", x, 68, radius=4, color_hex="#450a0a", border_hex="#ef4444")
            self.canvas_scene.addItem(h1)
            h2 = BreadboardHoleItem(f"RAIL_GND_TOP_{col}", x, 84, radius=4, color_hex="#0f172a", border_hex="#64748b")
            self.canvas_scene.addItem(h2)
            
        for col in range(30):
            x = 25 + (col * 16)
            for row_idx, col_name in enumerate(["A", "B", "C", "D", "E"]):
                y = 108 + (row_idx * 14)
                h = BreadboardHoleItem(f"STRIP_TOP_{col}_{col_name}", x, y)
                self.canvas_scene.addItem(h)
                
        gap_line = QGraphicsLineItem(15, 184, 505, 184)
        gap_line.setPen(QPen(QColor("#1e293b"), 4))
        self.canvas_scene.addItem(gap_line)
        
        for col in range(30):
            x = 25 + (col * 16)
            for row_idx, col_name in enumerate(["F", "G", "H", "I", "J"]):
                y = 198 + (row_idx * 14)
                h = BreadboardHoleItem(f"STRIP_BOT_{col}_{col_name}", x, y)
                self.canvas_scene.addItem(h)
                
        for col in range(30):
            x = 25 + (col * 16)
            h1 = BreadboardHoleItem(f"RAIL_VCC_BOT_{col}", x, 281, radius=4, color_hex="#450a0a", border_hex="#ef4444")
            self.canvas_scene.addItem(h1)
            h2 = BreadboardHoleItem(f"RAIL_GND_BOT_{col}", x, 297, radius=4, color_hex="#0f172a", border_hex="#64748b")
            self.canvas_scene.addItem(h2)
            
        ic_info = ECKBLoader.get_ic(self.current_ic_key) or {}
        pins_cnt = ic_info.get("pins", 14)
        pin_map = ECKBLoader.get_pin_map(self.current_ic_key) or {}
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
            
            lead_line = QGraphicsLineItem(hole_x, 172, hole_x, hole_y)
            lead_line.setPen(QPen(QColor("#cbd5e1"), 2))
            self.canvas_scene.addItem(lead_line)
            
            pin_node = BreadboardHoleItem(f"IC_PIN_{pin_num}", hole_x, hole_y, radius=4, color_hex="#e2e8f0", border_hex="#94a3b8")
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
            
            lead_line = QGraphicsLineItem(hole_x, 196, hole_x, hole_y)
            lead_line.setPen(QPen(QColor("#cbd5e1"), 2))
            self.canvas_scene.addItem(lead_line)
            
            pin_node = BreadboardHoleItem(f"IC_PIN_{pin_num}", hole_x, hole_y, radius=4, color_hex="#e2e8f0", border_hex="#94a3b8")
            self.canvas_scene.addItem(pin_node)
            
            num_txt = QGraphicsTextItem(str(pin_num))
            num_txt.setFont(QFont("Arial", 7, QFont.Weight.Bold))
            num_txt.setDefaultTextColor(QColor("#38bdf8"))
            num_txt.setPos(hole_x - 5, hole_y + 2)
            self.canvas_scene.addItem(num_txt)

    def update_metadata_guided_flow(self):
        ic_info = ECKBLoader.get_ic(self.current_ic_key) or {}
        vcc_pin = ic_info.get("vcc_pin", 14)
        gnd_pin = ic_info.get("gnd_pin", 7)
        pin_map = ECKBLoader.get_pin_map(self.current_ic_key) or {}
        
        gate_mappings = [
            {"in_a": 1, "in_b": 2, "out": 3},
            {"in_a": 4, "in_b": 5, "out": 6},
            {"in_a": 9, "in_b": 10, "out": 8},
            {"in_a": 12, "in_b": 13, "out": 11}
        ]
        active_gate = gate_mappings[min(self.current_gate_idx, len(gate_mappings)-1)]
        
        pin_a_label = pin_map.get(str(active_gate["in_a"]), f"Pin {active_gate['in_a']}")
        pin_b_label = pin_map.get(str(active_gate["in_b"]), f"Pin {active_gate['in_b']}")
        pin_out_label = pin_map.get(str(active_gate["out"]), f"Pin {active_gate['out']}")
        
        self.guided_connections = [
            {
                "step": 1,
                "from": "+5V Power Terminal",
                "to": f"Top Power Rail ➡ Pin {vcc_pin} (VCC)",
                "color": "Red Wire",
                "hex": "#ef4444",
                "purpose": "IC Power Supply (+5V)",
                "reason": f"Connect +5V Power Terminal to Power Rail and Pin {vcc_pin}. Reason: Powers internal logic gates."
            },
            {
                "step": 2,
                "from": "GND Power Terminal",
                "to": f"Ground Rail ➡ Pin {gnd_pin} (GND)",
                "color": "Black Wire",
                "hex": "#1e293b",
                "purpose": "IC Ground Return (0V)",
                "reason": f"Connect GND Terminal to Ground Rail and Pin {gnd_pin}. Reason: Completes power circuit."
            },
            {
                "step": 3,
                "from": "Input Terminal A",
                "to": f"Pin {active_gate['in_a']} ({pin_a_label})",
                "color": "Blue Wire",
                "hex": "#3b82f6",
                "purpose": f"Input A Signal (Gate {self.current_gate_idx+1})",
                "reason": f"Connect Input Terminal A to Pin {active_gate['in_a']}. Reason: Supplies digital logic signal A."
            },
            {
                "step": 4,
                "from": "Input Terminal B",
                "to": f"Pin {active_gate['in_b']} ({pin_b_label})",
                "color": "Blue Wire",
                "hex": "#3b82f6",
                "purpose": f"Input B Signal (Gate {self.current_gate_idx+1})",
                "reason": f"Connect Input Terminal B to Pin {active_gate['in_b']}. Reason: Supplies digital logic signal B."
            },
            {
                "step": 5,
                "from": f"Pin {active_gate['out']} ({pin_out_label})",
                "to": "Output Terminal Y0 / Y1 / Y2 / Y3",
                "color": "Green Wire",
                "hex": "#10b981",
                "purpose": f"Output Y Drive (Gate {self.current_gate_idx+1})",
                "reason": f"Connect Output Pin {active_gate['out']} to any Output Terminal (Y0-Y3). Reason: Drives green output LED indicator."
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
            item_text = f"{prefix}Step {idx+1}: {conn['from']} ➡ {conn['to']}"
            item = QListWidgetItem(item_text)
            if idx < self.current_step_idx:
                item.setForeground(QColor("#10b981"))
            elif idx == self.current_step_idx:
                item.setForeground(QColor("#38bdf8"))
            else:
                item.setForeground(QColor("#64748b"))
            self.list_steps.addItem(item)

    def advance_guided_step(self):
        if self.current_step_idx < len(self.guided_connections) - 1:
            self.current_step_idx += 1
            self.update_card_ui()
            if self.main_window and hasattr(self.main_window, "show_toast"):
                self.main_window.show_toast("✓ Connection Verified! Advancing to next step.")

    def prev_guided_step(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            self.update_card_ui()

    def on_ic_selection_changed(self, index):
        self.current_ic_key = self.ic_selector.itemData(index) or "7432"
        self.build_2d_breadboard_grid()
        self.update_metadata_guided_flow()
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
        self.step_counter += 1
        if self.step_counter >= max(1, int(30 / (self.clock_hz * 2))):
            self.step_counter = 0
            self.clock_state = 1 if self.clock_state == 0 else 0
            self.solve_circuit_logic()

    def solve_circuit_logic(self):
        val_a = self.inputs_state.get("IN_A", 0)
        val_b = self.inputs_state.get("IN_B", 0)
        
        ic_info = ECKBLoader.get_ic(self.current_ic_key) or {}
        gate_type = ic_info.get("logic_type", "OR")
        out_val = DigitalLogicEngine.evaluate_gate(gate_type, [val_a, val_b])
        
        for term_key in ["OUT_Y0", "OUT_Y1", "OUT_Y2", "OUT_Y3"]:
            self.outputs_state[term_key] = 0
            
        connected_out_terminals = set()
        active_output_pin_id = f"IC_PIN_{3 if self.current_gate_idx == 0 else (6 if self.current_gate_idx == 1 else (8 if self.current_gate_idx == 2 else 11))}"
        
        if hasattr(self, 'canvas_scene') and self.canvas_scene.wires:
            for wire in self.canvas_scene.wires:
                start_h = getattr(wire, 'start_hole', '')
                end_h = getattr(wire, 'end_hole', '')
                for term_id in ["OUT_Y0", "OUT_Y1", "OUT_Y2", "OUT_Y3"]:
                    if (start_h == term_id or end_h == term_id) or (start_h == active_output_pin_id or end_h == active_output_pin_id):
                        connected_out_terminals.add(term_id)
                        
        if not connected_out_terminals:
            connected_out_terminals.add("OUT_Y0")
            
        for term_id in connected_out_terminals:
            self.outputs_state[term_id] = out_val
            
        self.update_output_terminal_ui("OUT_Y0", self.lbl_out_y0, self.outputs_state["OUT_Y0"])
        self.update_output_terminal_ui("OUT_Y1", self.lbl_out_y1, self.outputs_state["OUT_Y1"])
        self.update_output_terminal_ui("OUT_Y2", self.lbl_out_y2, self.outputs_state["OUT_Y2"])
        self.update_output_terminal_ui("OUT_Y3", self.lbl_out_y3, self.outputs_state["OUT_Y3"])
            
        EventBus.publish(EventChannels.LOGIC_UPDATED, gate=gate_type, output=out_val)

    def update_output_terminal_ui(self, term_key, lbl_widget, val):
        name = term_key.replace("OUT_", "")
        if val == 1:
            lbl_widget.setText(f"{name}: HIGH (5V) [ON]")
            lbl_widget.setStyleSheet("background-color: #047857; color: #ffffff; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")
        else:
            lbl_widget.setText(f"{name}: OFF (0V)")
            lbl_widget.setStyleSheet("background-color: #1e293b; color: #64748b; font-weight: bold; padding: 3px 6px; border-radius: 3px; font-size: 8pt;")

    def on_event_switch_toggled(self, terminal="IN_A", logic=0):
        log.info(f"[DSDLabView] EventBus SWITCH_TOGGLED received: {terminal}={logic}")

    def on_event_power_changed(self, power_on=True):
        log.info(f"[DSDLabView] EventBus POWER_CHANGED received: Power={power_on}")

    def toggle_simulation_mode(self):
        self.is_simulating = not self.is_simulating
        if self.is_simulating:
            self.btn_sim_toggle.setText(" ▶ Start Simulation")
            self.btn_sim_toggle.setStyleSheet("background-color: #06b6d4; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
            EventBus.publish(EventChannels.SIMULATION_STARTED)
        else:
            self.btn_sim_toggle.setText(" ⏹ Stop Simulation")
            self.btn_sim_toggle.setStyleSheet("background-color: #eab308; color: black; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
            EventBus.publish(EventChannels.SIMULATION_STOPPED)

    def toggle_power(self):
        self.power_on = not self.power_on
        if self.power_on:
            self.btn_power.setText(" +5V Power ON")
            self.btn_power.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
            self.lbl_status_led.setText("● +5V POWER ON")
            self.lbl_status_led.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
            self.lbl_diag_msg.setText(f"Lab Instructor: Power rails verified (+5V). IC {self.current_ic_key} is powered and functional.")
        else:
            self.btn_power.setText(" Power OFF")
            self.btn_power.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 8.5pt;")
            self.lbl_status_led.setText("● POWER OFF")
            self.lbl_status_led.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
            self.lbl_diag_msg.setText("Diagnostics: Power rails de-energized. Circuit logic paused.")
        EventBus.publish(EventChannels.POWER_CHANGED, power_on=self.power_on)

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
        if self.main_window and hasattr(self.main_window, "show_toast"):
            self.main_window.show_toast("2D Trainer Kit Canvas reset.")
