"""
ElectroVerse — Authentic Virtual 8085 Microprocessor Trainer Kit
Faithfully emulates the physical 8085 hardware trainer board used in engineering laboratories.

Architecture:
  ┌──────────────────────────────────────────────────────────────┐
  │  ADDRESS DISPLAY [4 digits]    DATA DISPLAY [2 digits]       │  ← 7-Segment row
  ├──────────────────────────────────────────────────────────────┤
  │  Register Panel              │  Memory Viewer (64KB RAM)     │
  │  (A,B,C,D,E,H,L,PC,SP,FLAGS) │  Address : Hex : ASCII       │
  ├──────────────────────────────────────────────────────────────┤
  │  FUNCTION KEYPAD (Blue)      │  HEX KEYPAD (0-9, A-F)       │
  │  RESET VCT INT SHIFT         │  C  D  E  F                  │
  │  EXREG INS DEL               │  8H 9L  A  B                 │
  │  GO    B.M REL EXMEM         │  4PCH 5PCL 6SPH 7SPL         │
  │  STRING MEMCNEXT FILL        │  0  1  2SER 3                 │
  ├──────────────────────────────────────────────────────────────┤
  │  Console / Output Log                                        │
  └──────────────────────────────────────────────────────────────┘

Key behavior rules (matches physical hardware):
  - MEM/MEMC NEXT → enter Address Mode; user types 4 hex digits → address latch
  - After address entry → each digit pair entered = data byte stored at that address,
    display auto-advances to next address after each byte (NEXT action)
  - STEP → single instruction, updates all registers & flags
  - RUN/GO → continuous until HLT or invalid opcode
  - RESET → CPU registers reset, memory preserved
  - EXREG Si → examine/set register by name using keypad input
  - INS DATA / DEL DATA → insert / delete bytes at current cursor
  - No preloaded programs; students enter everything manually
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QGridLayout, QTableWidget, QTableWidgetItem, QTextEdit, QSplitter,
    QHeaderView, QScrollArea, QFileDialog, QMessageBox, QLineEdit,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QFontDatabase, QPalette

from src.core.logger import log
from src.core.v8085_cpu import Virtual8085CPU, CPUError, MemoryAccessError
from src.core.i8085.trainer_controller import TrainerController, TrainerSnapshot

# ---------------------------------------------------------------------------
# Helper: Seven-Segment LCD style label
# ---------------------------------------------------------------------------
class SegDisplay(QLabel):
    """Simulates a 7-segment LED display digit group."""
    def __init__(self, digits: int = 4, parent=None):
        super().__init__(parent)
        self._digits = digits
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._apply_style()
        self.set_value("0" * digits)

    def _apply_style(self):
        self.setStyleSheet(f"""
            QLabel {{
                background: #0A0A00;
                color: #FF2200;
                font-family: 'Segment7', 'DSEG7 Classic', 'Courier New', monospace;
                font-size: {22 if self._digits == 4 else 28}pt;
                font-weight: bold;
                letter-spacing: {8 if self._digits == 4 else 10}px;
                padding: 4px 14px;
                border: 2px solid #1A1A00;
                border-radius: 4px;
                min-width: {self._digits * 26}px;
            }}
        """)

    def set_value(self, text: str):
        self.setText(text.upper().rjust(self._digits, '0')[:self._digits])


class DataSegDisplay(SegDisplay):
    """Green-coloured data display."""
    def _apply_style(self):
        self.setStyleSheet(f"""
            QLabel {{
                background: #000A00;
                color: #00FF55;
                font-family: 'Segment7', 'DSEG7 Classic', 'Courier New', monospace;
                font-size: 28pt;
                font-weight: bold;
                letter-spacing: 12px;
                padding: 4px 14px;
                border: 2px solid #001A00;
                border-radius: 4px;
                min-width: 80px;
            }}
        """)


# ---------------------------------------------------------------------------
# LED Indicator
# ---------------------------------------------------------------------------
class LEDIndicator(QLabel):
    def __init__(self, color_on="#FF2200", color_off="#2A0000", parent=None):
        super().__init__("●", parent)
        self._on  = color_on
        self._off = color_off
        self.set_state(False)

    def set_state(self, on: bool):
        c = self._on if on else self._off
        self.setStyleSheet(f"color:{c}; font-size:10pt;")


# ---------------------------------------------------------------------------
# Main Virtual 8085 Trainer Widget
# ---------------------------------------------------------------------------
class Virtual8085TrainerWidget(QWidget):
    """
    Authentic Virtual 8085 Microprocessor Trainer Kit.
    No preloaded programs. Students interact exactly as with real hardware.
    """

    # -----------------------------------------------------------------------
    # Trainer FSM states
    # -----------------------------------------------------------------------
    STATE_IDLE         = "IDLE"
    STATE_ADDR_ENTRY   = "ADDR_ENTRY"    # entering address
    STATE_DATA_ENTRY   = "DATA_ENTRY"    # entering bytes
    STATE_EXAM_MEM     = "EXAM_MEM"      # read-only memory inspection
    STATE_EXAM_REG     = "EXAM_REG"      # read-only register inspection
    STATE_REG_SELECT   = "REG_SELECT"    # choose register
    STATE_REG_DATA     = "REG_DATA"      # entering new value for selected register

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing Authentic Virtual 8085 Trainer Kit")
        self.cpu = Virtual8085CPU()

        # TrainerController: encapsulates the complete physical trainer kit FSM
        # All MEM/NEXT/PREV/GO/EXEC/EXAM logic is delegated here.
        self.tc = TrainerController(self.cpu)

        # Legacy FSM mirrors — kept for backward-compat with _refresh_all / display helpers
        self._state          = self.STATE_IDLE
        self._cur_addr       = 0x2000
        self._reg_index      = 0
        self._input_buf      = []   # mirrors tc._buf for legacy display helpers
        self._addr_nibbles   = []
        self._data_nibbles   = []
        self._reg_target     = None
        self._reg_nibbles    = []

        # Execution
        self._is_running     = False
        self._run_timer      = QTimer(self)
        self._run_timer.timeout.connect(self._exec_step)

        self._build_ui()
        self._refresh_all()
        self._log("System Ready.  Press MEM to enter memory write mode.")

    # =======================================================================
    # UI Construction
    # =======================================================================
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Main green PCB frame
        pcb = QFrame()
        pcb.setStyleSheet("""
            QFrame#pcb {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0B2010, stop:0.4 #0D2A14, stop:1 #091A0C);
                border: 3px solid #1A4020;
                border-radius: 10px;
            }
        """)
        pcb.setObjectName("pcb")
        pcb_lay = QVBoxLayout(pcb)
        pcb_lay.setContentsMargins(12, 10, 12, 10)
        pcb_lay.setSpacing(8)

        # ── 1. PCB Title strip ──────────────────────────────────────────
        title_bar = QFrame()
        title_bar.setStyleSheet("background:transparent;")
        tb = QHBoxLayout(title_bar)
        tb.setContentsMargins(0, 0, 0, 0)
        brand = QLabel("SHUCON  8085  MICROPROCESSOR  TRAINER  SYSTEM")
        brand.setStyleSheet("color:#A0D8AF; font-size:8pt; font-weight:bold; letter-spacing:2px;")
        tb.addWidget(brand)
        tb.addStretch()
        rev = QLabel("PCB REV 4.1")
        rev.setStyleSheet("color:#607060; font-size:7pt;")
        tb.addWidget(rev)
        pcb_lay.addWidget(title_bar)

        # ── 2. 7-Segment Display Row ────────────────────────────────────
        seg_frame = self._build_display_row()
        pcb_lay.addWidget(seg_frame)

        # ── 3. Main body: left panel + right panel ──────────────────────
        body_split = QSplitter(Qt.Orientation.Horizontal)
        body_split.setStyleSheet("QSplitter::handle{background:#1A4020;width:3px;}")

        # Left: Registers + Memory Viewer
        left = self._build_left_panel()
        body_split.addWidget(left)

        # Center: Keypad board (function keys + hex keys)
        center = self._build_keypad_board()
        body_split.addWidget(center)

        # Right: Console output
        right = self._build_console_panel()
        body_split.addWidget(right)

        body_split.setSizes([310, 440, 280])
        pcb_lay.addWidget(body_split, 1)

        root.addWidget(pcb)

    # -----------------------------------------------------------------------
    def _build_display_row(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("""
            QFrame {
                background: #050C05;
                border: 2px solid #1A4020;
                border-radius: 6px;
                padding: 6px 16px;
            }
        """)
        lay = QHBoxLayout(f)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(24)

        # Label ADDRESS DISPLAY
        al = QLabel("ADDRESS DISPLAY")
        al.setStyleSheet("color:#607060; font-size:7pt; font-weight:bold; letter-spacing:1px;")
        lay.addWidget(al)

        self._seg_addr = SegDisplay(4)
        self._seg_addr.set_value("2000")
        lay.addWidget(self._seg_addr)

        lay.addStretch(1)

        # Label DATA DISPLAY
        dl = QLabel("DATA DISPLAY")
        dl.setStyleSheet("color:#607060; font-size:7pt; font-weight:bold; letter-spacing:1px;")
        lay.addWidget(dl)

        self._seg_data = DataSegDisplay(2)
        self._seg_data.set_value("00")
        lay.addWidget(self._seg_data)

        lay.addStretch(1)

        # Status LEDs strip
        led_frame = QFrame()
        led_frame.setStyleSheet("background:transparent;")
        lf_lay = QVBoxLayout(led_frame)
        lf_lay.setContentsMargins(0,0,0,0)
        lf_lay.setSpacing(2)
        lf_lay.addWidget(QLabel("STATUS", styleSheet="color:#607060;font-size:6pt;"))
        led_row = QHBoxLayout()
        self._leds = {}
        for name, color_on in [("HALT","#FF4444"), ("RUN","#44FF44"),
                                 ("MEM","#FFAA22"), ("REG","#22AAFF")]:
            col = QVBoxLayout()
            led = LEDIndicator(color_on)
            lbl = QLabel(name)
            lbl.setStyleSheet("color:#607060;font-size:5.5pt;")
            col.addWidget(led, 0, Qt.AlignmentFlag.AlignHCenter)
            col.addWidget(lbl, 0, Qt.AlignmentFlag.AlignHCenter)
            led_row.addLayout(col)
            self._leds[name] = led
        lf_lay.addLayout(led_row)
        lay.addWidget(led_frame)

        return f

    # -----------------------------------------------------------------------
    def _build_left_panel(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:transparent;}")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(0,0,4,0)
        lay.setSpacing(6)

        # ── Registers ──────────────────────────────────────────────────
        reg_frame = QFrame()
        reg_frame.setStyleSheet("""
            QFrame{background:#05150A; border:1px solid #1A4020; border-radius:5px; padding:4px;}
        """)
        rg = QGridLayout(reg_frame)
        rg.setSpacing(4)

        hdr = QLabel("CPU  REGISTERS")
        hdr.setStyleSheet("color:#A0D8AF;font-size:8pt;font-weight:bold;letter-spacing:1px;")
        rg.addWidget(hdr, 0, 0, 1, 4)

        self._reg_labels = {}
        reg_defs = [
            ("A (ACC)", "A",  "#F97316"),
            ("B",       "B",  "#06B6D4"),
            ("C",       "C",  "#06B6D4"),
            ("D",       "D",  "#3B82F6"),
            ("E",       "E",  "#3B82F6"),
            ("H",       "H",  "#10B981"),
            ("L",       "L",  "#10B981"),
            ("SP",      "SP", "#A855F7"),
            ("PC",      "PC", "#F43F5E"),
        ]
        for i, (lname, key, clr) in enumerate(reg_defs):
            row, col = divmod(i, 3)
            lbl_n = QLabel(lname)
            lbl_n.setStyleSheet("color:#607060;font-size:8pt;")
            lbl_v = QLabel("00H")
            lbl_v.setStyleSheet(f"color:{clr};font-size:8pt;font-weight:bold;font-family:Consolas,monospace;")
            rg.addWidget(lbl_n, row+1, col*2)
            rg.addWidget(lbl_v, row+1, col*2+1)
            self._reg_labels[key] = lbl_v

        # Flags row
        flag_row = QHBoxLayout()
        flag_row.addWidget(QLabel("FLAGS:", styleSheet="color:#607060;font-size:8pt;"))
        self._flag_labels = {}
        for fn, fc in [("S","#F97316"),("Z","#FACC15"),("AC","#06B6D4"),("P","#10B981"),("CY","#F43F5E")]:
            lbl = QLabel(f"{fn}=0")
            lbl.setStyleSheet(f"color:{fc};font-size:8pt;font-weight:bold;")
            flag_row.addWidget(lbl)
            self._flag_labels[fn] = lbl
        rg.addLayout(flag_row, len(reg_defs)//3+2, 0, 1, 6)

        lay.addWidget(reg_frame)

        # ── Memory Viewer ──────────────────────────────────────────────
        mv_hdr = QLabel("  MEMORY  (64 KB)")
        mv_hdr.setStyleSheet("color:#A0D8AF;font-size:8pt;font-weight:bold;background:transparent;")
        lay.addWidget(mv_hdr)

        self._mem_table = QTableWidget()
        self._mem_table.setColumnCount(4)
        self._mem_table.setHorizontalHeaderLabels(["ADDR", "HEX", "   ", "ASCII"])
        self._mem_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._mem_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._mem_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._mem_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._mem_table.setStyleSheet("""
            QTableWidget{
                background:#030D05; color:#A0D8AF;
                font-family:Consolas,monospace; font-size:8pt;
                border:1px solid #1A4020; gridline-color:#0D2510;
            }
            QHeaderView::section{
                background:#0D2510; color:#607060;
                font-size:7pt; border:none; padding:2px;
            }
            QTableWidget::item:selected{background:#1A4020;}
        """)
        self._mem_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._mem_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._mem_table.verticalHeader().setVisible(False)
        self._mem_table.setMinimumHeight(200)
        lay.addWidget(self._mem_table, 1)

        # File operations bar
        fops = QHBoxLayout()
        for txt, fn in [("💾 Save .HEX", self._save_hex),
                        ("📂 Load .HEX", self._load_hex),
                        ("🗑 Clear RAM",  self._clear_ram),
                        ("📖 Opcode Ref (i)", self._open_opcode_reference)]:
            b = QPushButton(txt)
            b.setStyleSheet("QPushButton{background:#0D2510;color:#A0D8AF;border:1px solid #1A4020;"
                            "border-radius:3px;padding:3px 6px;font-size:8pt;}"
                            "QPushButton:hover{background:#1A4020;}")
            b.clicked.connect(fn)
            fops.addWidget(b)
        lay.addLayout(fops)

        return f

    # -----------------------------------------------------------------------
    def _build_keypad_board(self) -> QFrame:
        """Build the physical-layout keypad exactly matching the trainer image."""
        f = QFrame()
        f.setStyleSheet("""
            QFrame{
                background:#0A1A0C;
                border:2px solid #1A4020;
                border-radius:8px;
                padding:8px;
            }
        """)
        lay = QVBoxLayout(f)
        lay.setContentsMargins(6,6,6,6)
        lay.setSpacing(6)

        # PCB header
        ph = QLabel("8085  SYSTEM  TRAINER  –  KEYPAD  MATRIX")
        ph.setStyleSheet("color:#607060;font-size:7pt;font-weight:bold;letter-spacing:1px;")
        lay.addWidget(ph, 0, Qt.AlignmentFlag.AlignHCenter)

        # Key layout — exactly matches the image
        # Each entry: (display_text, key_id, is_function_key)
        # Key layout — 12 Blue Control Buttons on left (4x3 grid), 16 Hex Keys on right (4x4 grid)
        # Row 0
        r0 = [
            ("RESET",     "RESET",    True),
            ("MEM",       "MEM",      True),
            ("GO",        "GO",       True),
            ("C",         "C",        False),
            ("D",         "D",        False),
            ("E",         "E",        False),
            ("F",         "F",        False),
        ]
        # Row 1
        r1 = [
            ("EXEC",      "EXEC",     True),
            ("EXAM\nMEM", "EXAM_MEM", True),
            ("EXAM\nREG", "EXAM_REG", True),
            ("8\nH",       "8",       False),
            ("9\nL",       "9",       False),
            ("A",          "A",       False),
            ("B",          "B",       False),
        ]
        # Row 2
        r2 = [
            ("NEXT",      "NEXT",     True),
            ("PREV",      "PREV",     True),
            ("SHIFT",     "SHIFT",    True),
            ("4\nPCH",     "4",       False),
            ("5\nPCL",     "5",       False),
            ("6\nSPH",     "6",       False),
            ("7\nSPL",     "7",       False),
        ]
        # Row 3
        r3 = [
            ("CLEAR",     "CLEAR",    True),
            ("MEM\nWRI",  "INS",      True),
            ("DEL",       "DEL",      True),
            ("0",         "0",        False),
            ("1",         "1",        False),
            ("2\nSER",      "2",      False),
            ("3",         "3",        False),
        ]

        key_matrix = [r0, r1, r2, r3]
        self._keypad_btns = {}
        grid = QGridLayout()
        grid.setSpacing(5)

        # Divider column after index 2 (between function keys and hex keys)
        for r_idx, row in enumerate(key_matrix):
            for c_idx, (display, key_id, is_fn) in enumerate(row):
                btn = QPushButton(display)
                btn.setFixedSize(70 if c_idx < 3 else 62, 52)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setFont(QFont("Arial", 8, QFont.Weight.Bold))

                if is_fn:
                    btn.setStyleSheet("""
                        QPushButton{
                            background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                stop:0 #2A5CD8, stop:1 #1A3CA0);
                            color:#FFFFFF;
                            border:2px solid #1A3090;
                            border-bottom:4px solid #101A60;
                            border-radius:5px;
                            font-size:8pt; font-weight:bold;
                        }
                        QPushButton:pressed{
                            background:#1A3CA0;
                            border-bottom:2px solid #101A60;
                            margin-top:2px;
                        }
                        QPushButton:hover{background:#3A6CE8;}
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton{
                            background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                stop:0 #252525, stop:1 #151515);
                            color:#FFFFFF;
                            border:2px solid #333333;
                            border-bottom:4px solid #0A0A0A;
                            border-radius:5px;
                            font-size:9pt; font-weight:bold;
                        }
                        QPushButton:pressed{
                            background:#151515;
                            border-bottom:2px solid #0A0A0A;
                            margin-top:2px;
                        }
                        QPushButton:hover{
                            background:#2A2A2A;
                            color:#FFAA22;
                        }
                    """)

                # Add vertical divider gap after column 2
                col_offset = c_idx + (1 if c_idx >= 3 else 0)
                grid.addWidget(btn, r_idx, col_offset)
                btn.clicked.connect(lambda _, k=key_id: self._on_key(k))
                self._keypad_btns[key_id] = btn

        # Insert visual divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("color:#1A4020;background:#1A4020;")
        grid.addWidget(divider, 0, 3, 4, 1)

        lay.addLayout(grid)

        # Bottom: STEP, RUN, RESET execution buttons (prominent)
        exec_row = QHBoxLayout()
        exec_row.setSpacing(8)
        for txt, fn, clr in [
            ("⏯  STEP",   self._btn_step, "#1E6035"),
            ("▶  RUN",    self._btn_run,  "#1A5020"),
            ("⏸  PAUSE",  self._btn_pause,"#5A4010"),
            ("🔄 RESET",  self._btn_reset,"#5A1010"),
        ]:
            b = QPushButton(txt)
            b.setFixedHeight(36)
            b.setStyleSheet(f"""
                QPushButton{{
                    background:{clr}; color:#FFFFFF;
                    border:1px solid #333; border-radius:4px;
                    font-size:9pt; font-weight:bold;
                }}
                QPushButton:hover{{filter:brightness(1.3);background:lightyellow;color:black;}}
                QPushButton:pressed{{margin-top:2px;}}
            """)
            b.clicked.connect(fn)
            exec_row.addWidget(b)
        lay.addLayout(exec_row)

        return f

    # -----------------------------------------------------------------------
    def _build_console_panel(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:transparent;}")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(4,0,0,0)
        lay.setSpacing(4)

        hdr = QLabel("OUTPUT  CONSOLE")
        hdr.setStyleSheet("color:#A0D8AF;font-size:8pt;font-weight:bold;letter-spacing:1px;")
        lay.addWidget(hdr)

        self._console = QTextEdit()
        self._console.setReadOnly(True)
        self._console.setStyleSheet("""
            QTextEdit{
                background:#020D02;
                color:#33FF66;
                font-family:Consolas,'Courier New',monospace;
                font-size:8pt;
                border:1px solid #1A4020;
                border-radius:4px;
                selection-background-color:#1A4020;
            }
        """)
        lay.addWidget(self._console, 1)

        # Bus activity indicators
        bus_frame = QFrame()
        bus_frame.setStyleSheet("QFrame{background:#030D05;border:1px solid #1A4020;border-radius:4px;padding:4px;}")
        bf = QVBoxLayout(bus_frame)
        bf.setContentsMargins(4,4,4,4)
        bf.setSpacing(3)

        # Address bus LEDs
        a_row = QHBoxLayout()
        a_row.addWidget(QLabel("A15", styleSheet="color:#607060;font-size:6pt;"))
        self._a_leds = []
        for _ in range(16):
            led = LEDIndicator("#FF3300", "#2A0000")
            led.setFixedWidth(12)
            a_row.addWidget(led)
        a_row.addWidget(QLabel("A0", styleSheet="color:#607060;font-size:6pt;"))
        bf.addLayout(a_row)

        # Data bus LEDs
        d_row = QHBoxLayout()
        d_row.addWidget(QLabel("D7 ", styleSheet="color:#607060;font-size:6pt;"))
        self._d_leds = []
        for _ in range(8):
            led = LEDIndicator("#00FF44", "#002A10")
            led.setFixedWidth(12)
            d_row.addWidget(led)
        d_row.addWidget(QLabel("D0", styleSheet="color:#607060;font-size:6pt;"))
        bf.addLayout(d_row)

        lay.addWidget(bus_frame)

        # Speed control
        spd_row = QHBoxLayout()
        spd_row.addWidget(QLabel("RUN SPEED:", styleSheet="color:#607060;font-size:8pt;"))
        from PySide6.QtWidgets import QSlider
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(50, 2000)
        self._speed_slider.setValue(400)
        self._speed_slider.setStyleSheet("QSlider::handle{background:#1A8040;}")
        spd_row.addWidget(self._speed_slider)
        ms_lbl = QLabel("400 ms")
        ms_lbl.setStyleSheet("color:#607060;font-size:8pt;")
        self._speed_slider.valueChanged.connect(lambda v: ms_lbl.setText(f"{v} ms"))
        spd_row.addWidget(ms_lbl)
        lay.addLayout(spd_row)

        return f

    # =======================================================================
    # Key handler — FSM for 12 Blue Control Buttons + Hex Keypad
    # =======================================================================
    _REG_LIST = ["A", "B", "C", "D", "E", "H", "L", "PC", "SP", "FLAGS"]

    def _on_key(self, key: str):
        """
        Dispatch keypad press to TrainerController.
        All FSM logic lives in tc (TrainerController); we only apply the
        TrainerSnapshot to the UI widgets here.
        """
        snap: TrainerSnapshot | None = None
        is_hex = key in "0123456789ABCDEF"

        if   key == "RESET":    snap = self.tc.reset_cpu()
        elif key == "MEM":      snap = self.tc.enter_mem_mode()
        elif key == "GO":       self._btn_go(); return
        elif key == "EXEC":     self._exec_step(); return
        elif key == "EXAM_MEM": snap = self.tc.enter_exam_mem_mode()
        elif key == "EXAM_REG": snap = self.tc.enter_exam_reg_mode()
        elif key == "NEXT":     snap = self.tc.next_step()
        elif key == "PREV":     snap = self.tc.prev_step()
        elif key == "SHIFT":    self._do_shift(); return
        elif key == "CLEAR":    snap = self.tc.clear_action()
        elif key == "INS":      snap = self.tc.insert_staged_byte()
        elif key == "DEL":      snap = self.tc.delete_last_digit()
        elif is_hex:            snap = self.tc.input_hex_digit(key)

        if snap is not None:
            self._apply_snapshot(snap)

    # =======================================================================
    # Snapshot → UI bridge
    # =======================================================================
    def _apply_snapshot(self, snap: TrainerSnapshot) -> None:
        """
        Apply a TrainerSnapshot to all UI widgets.
        This is the ONLY place TrainerController output touches the UI.
        """
        try:
            # 7-segment displays
            self._seg_addr.set_value(snap.address_display)
            self._seg_data.set_value(snap.data_display)

            # Status bar
            self._update_status(snap.status_msg)

            # Sync legacy cur_addr mirror
            self._cur_addr = snap.current_address

            # LEDs
            is_mem = snap.mode in (TrainerController.DATA_ENTRY,
                                   TrainerController.ADDR_ENTRY,
                                   TrainerController.EXAM_MEM)
            is_reg = snap.mode == TrainerController.EXAM_REG
            self._set_led('MEM', is_mem)
            self._set_led('REG', is_reg)
            if snap.halted:
                self._set_led('HALT', True)
                self._set_led('RUN',  False)

            # Console log
            if snap.error:
                self._log(f'ERROR: {snap.error}')
            else:
                self._log(snap.status_msg)

            # Refresh register panel and memory table
            self._refresh_reg_display()
            print("[OK] Register panel refreshed")
            self._refresh_mem_table()
            print("[OK] Memory panel refreshed")
            # Always scroll (even when address = 0x0000)
            self._scroll_mem_to(snap.current_address)

        except Exception as _e:
            import traceback
            self._log(f'[_apply_snapshot error] {_e}\n{traceback.format_exc()}')

    # =======================================================================
    # Button Handler Implementations (legacy wrappers — kept for SHIFT, GO, EXEC)
    # =======================================================================
    def _enter_mem_write_mode(self):
        self._target_mode = "WRITE"
        self._state = self.STATE_ADDR_ENTRY
        self._addr_nibbles = []
        self._data_nibbles = []
        self._set_led("MEM", True)
        self._set_led("REG", False)
        self._seg_addr.set_value("----")
        self._seg_data.set_value("--")
        self._update_status("MEM WRITE MODE: Enter 4-digit start address (e.g. 2000)")

    def _enter_exam_mem_mode(self):
        self._target_mode = "EXAM_MEM"
        self._state = self.STATE_ADDR_ENTRY
        self._addr_nibbles = []
        self._set_led("MEM", True)
        self._set_led("REG", False)
        self._seg_addr.set_value("----")
        self._seg_data.set_value("--")
        self._update_status("EXAM MEM MODE: Enter 4-digit address to inspect (e.g. 2500)")

    def _enter_exam_reg_mode(self):
        self._state = self.STATE_EXAM_REG
        self._reg_index = 0
        self._set_led("REG", True)
        self._set_led("MEM", False)
        self._update_exam_reg_display()

    def _update_exam_reg_display(self):
        reg_name = self._REG_LIST[self._reg_index]
        s = self.cpu.get_state_snapshot()
        self._seg_addr.set_value(reg_name.center(4))
        if reg_name == "FLAGS":
            val = s['PSW']
        elif reg_name in ("PC", "SP"):
            val = s[reg_name] & 0xFF
        else:
            val = s[reg_name]
        self._seg_data.set_value(f"{val:02X}")
        self._log(f"EXAM REG: {reg_name} = {val:02X}H")
        self._update_status(f"EXAM REG: {reg_name} = {val:02X}H | Use NEXT / PREV to cycle registers")

    def _do_next(self):
        if self._state == self.STATE_EXAM_REG:
            self._reg_index = (self._reg_index + 1) % len(self._REG_LIST)
            self._update_exam_reg_display()
        else:
            self._cur_addr = (self._cur_addr + 1) & 0xFFFF
            self.cpu.PC = self._cur_addr
            val = self.cpu.memory[self._cur_addr]
            self._seg_addr.set_value(f"{self._cur_addr:04X}")
            self._seg_data.set_value(f"{val:02X}")
            self._refresh_mem_table()
            self._scroll_mem_to(self._cur_addr)
            self._log(f"NEXT: Address = {self._cur_addr:04X}H -> [{val:02X}H]")

    def _do_prev(self):
        if self._state == self.STATE_EXAM_REG:
            self._reg_index = (self._reg_index - 1) % len(self._REG_LIST)
            self._update_exam_reg_display()
        else:
            self._cur_addr = (self._cur_addr - 1) & 0xFFFF
            self.cpu.PC = self._cur_addr
            val = self.cpu.memory[self._cur_addr]
            self._seg_addr.set_value(f"{self._cur_addr:04X}")
            self._seg_data.set_value(f"{val:02X}")
            self._refresh_mem_table()
            self._scroll_mem_to(self._cur_addr)
            self._log(f"PREV: Address = {self._cur_addr:04X}H -> [{val:02X}H]")

    def _do_shift(self):
        self._shift_active = not getattr(self, "_shift_active", False)
        status = "ACTIVE" if self._shift_active else "INACTIVE"
        self._log(f"SHIFT: Secondary function mode {status}.")
        self._update_status(f"SHIFT: Secondary function mode {status}.")

    def _do_clear(self):
        # Always clear the input buffer first
        self._input_buf = []
        if self._state == self.STATE_ADDR_ENTRY:
            self._addr_nibbles.clear()
            self._update_addr_entry_display()
            self._log("CLEAR: Address entry reset.")
        elif self._state == self.STATE_DATA_ENTRY:
            self._data_nibbles.clear()
            self._seg_data.set_value("--")
            self._log("CLEAR: Byte entry reset.")
        else:
            # Restore data display to current memory byte, then clear RAM
            self._seg_data.set_value("--")
            self._clear_ram()

    def _clear_ram(self):
        self.cpu.memory.clear_ram()
        self._refresh_all()
        self._log("CLEAR: All user RAM (2000H-FFFFH) cleared.")
        self._update_status("CLEAR — User RAM cleared.")

    def _open_opcode_reference(self):
        """Open the local Intel 8085 Opcode Reference chart modal viewer."""
        import traceback
        from PySide6.QtWidgets import QMessageBox
        try:
            print("INFO button clicked")
            from src.ui.components.opcode_viewer_dialog import OpcodeViewerDialog
            dlg = OpcodeViewerDialog(self)
            print("Dialog created")

            img_path = dlg._resolve_image_path()
            print(f"Image path: {img_path}")

            exists = img_path.exists() if (img_path and hasattr(img_path, 'exists')) else False
            print(f"Image exists: {exists}")

            if hasattr(dlg, 'pixmap_item') and dlg.pixmap_item and not dlg.pixmap_item.pixmap().isNull():
                pm = dlg.pixmap_item.pixmap()
                print(f"Pixmap loaded: {pm.width()}x{pm.height()} px")
            else:
                print("Pixmap loaded: False")

            print("Dialog shown")
            dlg.exec()
        except Exception as e:
            print(f"ERROR in _open_opcode_reference: {e}")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error Opening Opcode Reference",
                f"Failed to open Intel 8085 Opcode Reference dialog:\n\n{e}\n\n{traceback.format_exc()}"
            )

    # =======================================================================
    # FSM helpers
    # =======================================================================
    def _enter_addr_mode(self):
        self._state        = self.STATE_ADDR_ENTRY
        self._addr_nibbles = []
        self._data_nibbles = []
        self._set_led("MEM", True)
        self._set_led("REG", False)
        self._seg_addr.set_value("----")
        self._seg_data.set_value("--")
        self._update_status("MEM MODE: Enter 4-digit hex address (e.g. 2000)")

    def _update_addr_entry_display(self):
        partial = "".join(self._addr_nibbles)
        display = partial.ljust(4, "-")[:4]
        self._seg_addr.set_value(display)

    def _commit_address(self):
        addr_str = "".join(self._addr_nibbles)
        self._cur_addr = int(addr_str, 16) & 0xFFFF
        val = self.cpu.memory[self._cur_addr]
        target = getattr(self, "_target_mode", "WRITE")

        if target == "EXAM_MEM":
            self._state = self.STATE_EXAM_MEM
            self._seg_addr.set_value(f"{self._cur_addr:04X}")
            self._seg_data.set_value(f"{val:02X}")
            self._update_status(f"EXAM MEM: [{self._cur_addr:04X}H] = {val:02X}H (Read-only) | Press NEXT / PREV")
            self._log(f"EXAM MEM: Address {self._cur_addr:04X}H -> [{val:02X}H]")
        elif target == "GO_EXEC":
            self.cpu.PC = self._cur_addr
            self._log(f"GO: Execution address = {self._cur_addr:04X}H.")
            self._btn_run()
        else:  # "WRITE"
            self._state = self.STATE_DATA_ENTRY
            self._data_nibbles = []
            self._seg_addr.set_value(f"{self._cur_addr:04X}")
            self._seg_data.set_value(f"{val:02X}")
            self._update_status(f"MEM WRITE: Address {self._cur_addr:04X}H -> current: {val:02X}H | Enter 2 hex digits")
            self._log(f"MEM WRITE: Cursor at {self._cur_addr:04X}H -> [{val:02X}H]")

        self._scroll_mem_to(self._cur_addr)

    def _update_data_entry_display(self):
        partial = "".join(self._data_nibbles)
        self._seg_data.set_value(partial.rjust(2, "_")[-2:])

    def _commit_data_byte(self):
        byte_val = int("".join(self._data_nibbles), 16) & 0xFF
        addr = self._cur_addr
        # Memory protection check
        if addr <= Virtual8085CPU.ROM_END:
            self._log(f"ERROR: Address {addr:04X}H is in ROM region (0000H–1FFFH). Write rejected.")
            self._data_nibbles = []
            self._seg_data.set_value("EE")
            return
        try:
            self.cpu.write_mem_direct(addr, byte_val)
        except Exception as e:
            self._log(f"ERROR: {e}")
            self._data_nibbles = []
            return

        self._log(f"  [{addr:04X}H] ← {byte_val:02X}H")
        # Auto advance to next address
        self._cur_addr = (self._cur_addr + 1) & 0xFFFF
        next_val = self.cpu.memory[self._cur_addr]
        self._data_nibbles = []
        self._seg_addr.set_value(f"{self._cur_addr:04X}")
        self._seg_data.set_value(f"{next_val:02X}")
        self._update_status(f"ADDR {self._cur_addr:04X}H  →  current: {next_val:02X}H  |  Enter 2 hex digits to overwrite")
        self._refresh_mem_table()
        self._scroll_mem_to(self._cur_addr)

    def _enter_reg_mode(self):
        self._state       = self.STATE_REG_SELECT
        self._reg_nibbles = []
        self._set_led("REG", True)
        self._set_led("MEM", False)
        self._seg_addr.set_value("rEG ")
        self._seg_data.set_value("--")
        self._update_status(
            "EXREG MODE: Select register:\n"
            "0=B  1=C  2=D  3=E  4=H  5=L  6=A  7=SP  8=PC"
        )

    def _commit_reg_value(self):
        val_str = "".join(self._reg_nibbles)
        val     = int(val_str, 16)
        rn      = self._reg_target
        if rn == "A":  self.cpu.A  = val & 0xFF
        elif rn == "B": self.cpu.B = val & 0xFF
        elif rn == "C": self.cpu.C = val & 0xFF
        elif rn == "D": self.cpu.D = val & 0xFF
        elif rn == "E": self.cpu.E = val & 0xFF
        elif rn == "H": self.cpu.H = val & 0xFF
        elif rn == "L": self.cpu.L = val & 0xFF
        elif rn == "SP": self.cpu.SP = val & 0xFFFF
        elif rn == "PC":
            self.cpu.PC = val & 0xFFFF
            self._cur_addr = self.cpu.PC
        self._log(f"EXREG: {rn} ← {val:0{'4' if rn in ('SP','PC') else '2'}X}H")
        self._state = self.STATE_IDLE
        self._set_led("REG", False)
        self._update_status("IDLE — register set. Press MEMC NEXT to continue memory edit.")
        self._refresh_all()

    def _insert_at_cursor(self):
        """Write the staged input buffer byte into current address, then advance.

        If no byte has been staged (buffer empty), writes 00H.
        This matches real 8085 trainer kit behaviour where INS stores the
        currently-displayed byte into RAM and moves the pointer forward.
        """
        addr = self._cur_addr
        if addr <= Virtual8085CPU.ROM_END:
            self._log(f"INS: Cannot write to ROM at {addr:04X}H.")
            return

        # Build byte from input buffer (default 00 if nothing typed)
        if self._input_buf:
            buf_str  = "".join(self._input_buf).rjust(2, "0")
            byte_val = int(buf_str[-2:], 16) & 0xFF
        else:
            byte_val = self.cpu.memory[addr] & 0xFF  # store whatever is shown

        try:
            self.cpu.write_mem_direct(addr, byte_val)
        except Exception as e:
            self._log(f"INS ERROR: {e}")
            return

        self._log(f"INS: [{addr:04X}H] ← {byte_val:02X}H")
        self._input_buf = []   # clear buffer after commit

        # Advance address pointer
        self._cur_addr = (addr + 1) & 0xFFFF
        next_val = self.cpu.memory[self._cur_addr]
        self._seg_addr.set_value(f"{self._cur_addr:04X}")
        self._seg_data.set_value(f"{next_val:02X}")
        self._update_status(
            f"INS: [{addr:04X}H]={byte_val:02X}H  →  next [{self._cur_addr:04X}H]={next_val:02X}H"
        )
        self._refresh_mem_table()
        self._scroll_mem_to(self._cur_addr)

    def _delete_at_cursor(self):
        """Backspace the input buffer (remove last typed digit).

        On a real 8085 trainer DEL removes the last entered nibble so you
        can retype a digit without re-entering the entire byte.
        If the buffer is already empty, fall through to memory-shift delete.
        """
        if self._input_buf:
            # Backspace: remove the last nibble from the staging buffer
            self._input_buf.pop()
            buf_str = "".join(self._input_buf).rjust(2, "0") if self._input_buf else "--"
            if self._input_buf:
                self._seg_data.set_value(buf_str[-2:])
            else:
                # Buffer empty — restore the memory byte at current address
                val = self.cpu.memory[self._cur_addr]
                self._seg_data.set_value(f"{val:02X}")
            self._log(f"DEL: Buffer backspace  →  {buf_str}")
            self._update_status(f"DEL: {buf_str}  |  Continue typing or press MEM WRITE to store")
            return

        # Buffer already empty — do a real memory-shift delete (advanced use)
        addr = self._cur_addr
        if addr > Virtual8085CPU.ROM_END:
            for a in range(addr, 0xFFFF):
                self.cpu.memory[a] = self.cpu.memory[a + 1]
            self.cpu.memory[0xFFFF] = 0x00
            self._log(f"DEL: Memory byte at {addr:04X}H deleted (shifted down).")
            val = self.cpu.memory[addr]
            self._seg_data.set_value(f"{val:02X}")
            self._refresh_mem_table()
            self._refresh_displays()
        else:
            self._log(f"DEL: Cannot delete at {addr:04X}H.")

    # =======================================================================
    # Execution controls
    # =======================================================================
    def _btn_step(self):
        self._stop_run()
        self._exec_step()

    def _btn_run(self):
        if self._is_running:
            return
        if self.cpu.halted:
            self._log("CPU halted. Press RESET to restart.")
            return

        exec_addr = self.cpu.PC
        self._log(f"GO: Executing from PC = {exec_addr:04X}H (ProgramStartAddress = {self.tc.read_program_start_address():04X}H)")
        if not self.cpu.memory.is_written(exec_addr):
            msg = f"No program found at {exec_addr:04X}H. Enter program with MEM first."
            self._log(msg)
            self._update_status(msg)
            return

        self._is_running = True
        self._set_led("RUN", True)
        self._set_led("HALT", False)
        self._run_timer.start(self._speed_slider.value())
        self._log("Execution started.")
        self._update_status("RUN MODE — executing until HLT or error.")

    def _btn_pause(self):
        self._stop_run()
        self._log("Execution paused.")

    def _btn_go(self):
        """
        GO: Start execution from ProgramStartAddress (NOT the cursor).
        Delegates to TrainerController which captured ProgramStartAddress when MEM was pressed.
        """
        self._stop_run()
        snap = self.tc.go_button()
        self._apply_snapshot(snap)
        if snap.error:
            return
        # Begin continuous run
        self._btn_run()

    def _btn_reset(self):
        self._stop_run()
        snap = self.tc.reset_cpu()
        self._cur_addr = 0x0000   # match controller default
        self._apply_snapshot(snap)
        self._set_led("HALT", False)
        self._set_led("RUN",  False)
        self._set_led("MEM",  False)
        self._set_led("REG",  False)
        self._refresh_all()


    def _exec_step(self):
        if self.cpu.halted:
            self._stop_run()
            self._set_led("HALT", True)
            self._log("Program completed successfully.\nHLT encountered.")
            self._update_status("HLT — Program completed successfully.")
            return
        try:
            res = self.cpu.step()
            self._cur_addr = res["pc"]
            self._refresh_displays()
            self._refresh_bus_leds()
            self._refresh_reg_display()
            self._refresh_mem_table()
            self._scroll_mem_to(res["pc"])
            self._seg_addr.set_value(f"{res['pc']:04X}")
            self._seg_data.set_value(f"{res['opcode']:02X}")
            self._log(f"[{res['pc']:04X}H] {res['instruction']:20s}  | {res['log']}")
            if res["halted"]:
                self._stop_run()
                self._set_led("HALT", True)
                self._log("Program completed successfully.\nHLT encountered.")
                self._update_status("HLT — Program completed successfully.")
        except CPUError as e:
            self._stop_run()
            self._log(f"{e}")
            self._update_status(f"{e}")
        except MemoryAccessError as e:
            self._stop_run()
            self._log(f"{e}")
            self._update_status(f"{e}")
        except Exception as e:
            self._stop_run()
            self._log(f"ERROR: {e}")
            self._update_status(f"ERROR: {e}")

    def _stop_run(self):
        self._run_timer.stop()
        self._is_running = False
        self._set_led("RUN", False)

    # =======================================================================
    # Display update helpers
    # =======================================================================
    def _refresh_all(self):
        self._refresh_displays()
        self._refresh_reg_display()
        self._refresh_bus_leds()
        self._refresh_mem_table()

    def _refresh_displays(self):
        self._seg_addr.set_value(f"{self._cur_addr:04X}")
        self._seg_data.set_value(f"{self.cpu.memory[self._cur_addr]:02X}")

    def _refresh_reg_display(self):
        s = self.cpu.get_state_snapshot()
        for key, lbl in self._reg_labels.items():
            if key == "SP":
                lbl.setText(f"{s['SP']:04X}H")
            elif key == "PC":
                lbl.setText(f"{s['PC']:04X}H")
            else:
                lbl.setText(f"{s[key]:02X}H")
        for fn, lbl in self._flag_labels.items():
            lbl.setText(f"{fn}={s[fn]}")

    def _refresh_bus_leds(self):
        addr = self.cpu.address_bus
        for i, led in enumerate(self._a_leds):
            led.set_state(bool((addr >> (15 - i)) & 1))
        data = self.cpu.data_bus
        for i, led in enumerate(self._d_leds):
            led.set_state(bool((data >> (7 - i)) & 1))

    def _refresh_mem_table(self):
        """Show 64 bytes around current cursor address (any address 0000H-FFFFH)."""
        VIEW_ROWS = 64
        # Do NOT clamp to RAM_START — trainer can write to any address
        base = (self._cur_addr - 16) & 0xFFFF
        base = base & 0xFFF0   # align to 16-byte boundary

        self._mem_table.blockSignals(True)
        self._mem_table.setRowCount(VIEW_ROWS)
        for r in range(VIEW_ROWS):
            addr = (base + r) & 0xFFFF
            val  = self.cpu.memory[addr]
            asc  = chr(val) if 0x20 <= val <= 0x7E else "."

            addr_item = QTableWidgetItem(f"{addr:04X}H")
            hex_item  = QTableWidgetItem(f"{val:02X}")
            sep_item  = QTableWidgetItem("│")
            asc_item  = QTableWidgetItem(asc)

            for item in (addr_item, hex_item, sep_item, asc_item):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Highlight cursor row
            if addr == self._cur_addr:
                for item in (addr_item, hex_item, sep_item, asc_item):
                    item.setBackground(QColor("#1A4020"))
                    item.setForeground(QColor("#AAFFCC"))

            self._mem_table.setItem(r, 0, addr_item)
            self._mem_table.setItem(r, 1, hex_item)
            self._mem_table.setItem(r, 2, sep_item)
            self._mem_table.setItem(r, 3, asc_item)
            self._mem_table.setRowHeight(r, 16)

        self._mem_table.blockSignals(False)

    def _scroll_mem_to(self, addr: int):
        base = max(Virtual8085CPU.RAM_START, addr - 16) & 0xFFF0
        target_row = addr - base
        target_row = max(0, min(target_row, self._mem_table.rowCount() - 1))
        self._mem_table.scrollToItem(
            self._mem_table.item(target_row, 0),
            QTableWidget.ScrollHint.PositionAtCenter
        )

    # =======================================================================
    # Status / LED helpers
    # =======================================================================
    def _set_led(self, name: str, state: bool):
        if name in self._leds:
            self._leds[name].set_state(state)

    def _update_status(self, msg: str):
        # Lower status bar removed; output console on right is the sole execution console
        pass

    def _log(self, msg: str):
        self._console.append(f"> {msg}")

    # =======================================================================
    # File operations
    # =======================================================================
    def _save_hex(self):
        """Save RAM content (2000H–) as Intel HEX format."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Intel HEX File", "", "Intel HEX (*.hex);;Binary (*.bin);;All Files (*)"
        )
        if not path:
            return
        try:
            if path.endswith(".bin"):
                with open(path, "wb") as fh:
                    fh.write(bytes(self.cpu.memory[0x2000:0x8000]))
            else:
                lines = []
                for base in range(0x2000, 0x8000, 16):
                    chunk = self.cpu.memory[base:base+16]
                    count = len(chunk)
                    checksum = (count + (base >> 8) + (base & 0xFF) + sum(chunk)) & 0xFF
                    checksum = ((~checksum) + 1) & 0xFF
                    data_str = "".join(f"{b:02X}" for b in chunk)
                    lines.append(f":{count:02X}{base:04X}00{data_str}{checksum:02X}")
                lines.append(":00000001FF")
                with open(path, "w") as fh:
                    fh.write("\n".join(lines))
            self._log(f"Saved to {path}")
        except Exception as e:
            self._log(f"Save error: {e}")

    def _load_hex(self):
        """Load Intel HEX or binary file into RAM."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Load HEX/BIN File", "", "Intel HEX (*.hex);;Binary (*.bin);;All Files (*)"
        )
        if not path:
            return
        try:
            if path.endswith(".bin"):
                with open(path, "rb") as fh:
                    data = fh.read()
                for i, b in enumerate(data[:0x6000]):
                    self.cpu.memory[0x2000 + i] = b
                self._log(f"Loaded {len(data)} bytes from {path}")
            else:
                count = 0
                with open(path, "r") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line.startswith(":"):
                            continue
                        rec_len  = int(line[1:3], 16)
                        addr     = int(line[3:7], 16)
                        rec_type = int(line[7:9], 16)
                        if rec_type == 0x01:  # EOF
                            break
                        if rec_type == 0x00:  # Data
                            for i in range(rec_len):
                                b = int(line[9+i*2:11+i*2], 16)
                                self.cpu.memory[(addr + i) & 0xFFFF] = b
                                count += 1
                self._log(f"Loaded {count} bytes from Intel HEX file {path}")
            self._cur_addr = 0x2000
            self._refresh_all()
        except Exception as e:
            self._log(f"Load error: {e}")

    def _clear_ram(self):
        reply = QMessageBox.question(
            self, "Clear RAM",
            "This will erase all user RAM (2000H–FFFFH).\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for i in range(0x2000, 0x10000):
                self.cpu.memory[i] = 0x00
            self._cur_addr = 0x2000
            self._log("RAM cleared (2000H–FFFFH).")
            self._refresh_all()
