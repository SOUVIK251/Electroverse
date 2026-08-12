"""
ElectroVerse Microprocessor & Microcontroller Problem Solving Lab View
Interactive 18-Solver Workspace for Address Decoding, Timers, Opcodes, Baud Rates & ARM Clocks.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox,
    QGridLayout, QPushButton, QLineEdit, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt
import qtawesome as qta
from src.core.logger import log
from src.core.mpmc_engine import MPMCEngine
from src.ui.components.engineering_spinbox import EngineeringSpinBox, EngineeringDoubleSpinBox


class MPMCProblemSolvingView(QWidget):
    """Problem Solving Lab View with 18 Interactive Engineering Calculators."""

    def __init__(self, hub_view=None, parent=None):
        super().__init__(parent)
        self.hub_view = hub_view
        log.info("Initializing MPMCProblemSolvingView 18-calculator lab workspace")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header Control Bar
        hdr_bar = QFrame()
        hdr_bar.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 8px 15px; }")
        h_lay = QHBoxLayout(hdr_bar)

        h_title = QLabel("🧮 MICROPROCESSOR & EMBEDDED SYSTEM PROBLEM SOLVING LAB")
        h_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F97316;")
        h_lay.addWidget(h_title)
        h_lay.addStretch()

        sel_lbl = QLabel("Select Solver:")
        sel_lbl.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 9.5pt;")
        h_lay.addWidget(sel_lbl)

        self.solver_combo = QComboBox()
        self.solver_combo.setFixedWidth(320)
        self.solver_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #06B6D4;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QComboBox QAbstractItemView {
                background-color: #0F172A;
                color: #F8FAFC;
                selection-background-color: #F97316;
            }
        """)

        self.solvers = [
            ("1. Address Decoder Calculator", "address_decoder"),
            ("2. Memory Mapping Calculator", "memory_mapping"),
            ("3. Hex ↔ Decimal Converter", "hex_dec"),
            ("4. Instruction Timing Calculator", "instruction_timing"),
            ("5. 8085 Opcode Finder", "opcode_8085"),
            ("6. Interrupt Priority & Vector Solver", "interrupt_solver"),
            ("7. 8051 Timer Reload Calculator", "timer_8051"),
            ("8. UART Baud Rate Calculator", "uart_baud"),
            ("9. ARM Clock & PLL Calculator", "arm_clock"),
            ("10. DMA Transfer Calculator", "dma_calc")
        ]

        for title, key in self.solvers:
            self.solver_combo.addItem(title, key)

        self.solver_combo.currentIndexChanged.connect(self.on_solver_changed)
        h_lay.addWidget(self.solver_combo)

        main_layout.addWidget(hdr_bar)

        # Splitter Workspace
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #1E293B; width: 2px; }")

        # Left Panel (Inputs & Parameter Controls)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet("QScrollArea { border: 1px solid #1E293B; border-radius: 8px; background-color: #0B1020; }")

        self.left_container = QFrame()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(15, 15, 15, 15)
        self.left_layout.setSpacing(12)
        left_scroll.setWidget(self.left_container)

        # Right Panel (Theory, Derivation & Output Cards)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: 1px solid #1E293B; border-radius: 8px; background-color: #0B1020; }")

        self.right_container = QFrame()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(12)
        right_scroll.setWidget(self.right_container)

        splitter.addWidget(left_scroll)
        splitter.addWidget(right_scroll)
        splitter.setSizes([400, 600])

        main_layout.addWidget(splitter)

        # Initial calculation
        self.on_solver_changed(0)

    def clear_layouts(self):
        while self.left_layout.count():
            item = self.left_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def on_solver_changed(self, index):
        self.clear_layouts()
        key = self.solver_combo.currentData()

        if key == "address_decoder":
            self.setup_address_decoder_ui()
        elif key == "memory_mapping":
            self.setup_memory_mapping_ui()
        elif key == "hex_dec":
            self.setup_hex_dec_ui()
        elif key == "instruction_timing":
            self.setup_instruction_timing_ui()
        elif key == "opcode_8085":
            self.setup_opcode_8085_ui()
        elif key == "interrupt_solver":
            self.setup_interrupt_solver_ui()
        elif key == "timer_8051":
            self.setup_timer_8051_ui()
        elif key == "uart_baud":
            self.setup_uart_baud_ui()
        elif key == "arm_clock":
            self.setup_arm_clock_ui()
        else:
            self.setup_address_decoder_ui()

    # 1. Address Decoder UI
    def setup_address_decoder_ui(self):
        title = QLabel("Address Decoder Parameter Inputs")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F97316;")
        self.left_layout.addWidget(title)

        grid = QGridLayout()
        grid.addWidget(QLabel("Address Bus Lines:"), 0, 0)
        self.sb_addr_lines = EngineeringSpinBox()
        self.sb_addr_lines.setRange(8, 32)
        self.sb_addr_lines.setValue(16)
        grid.addWidget(self.sb_addr_lines, 0, 1)

        grid.addWidget(QLabel("Chip Size (KB):"), 1, 0)
        self.sb_chip_kb = EngineeringDoubleSpinBox()
        self.sb_chip_kb.setRange(0.5, 1024.0)
        self.sb_chip_kb.setValue(8.0)
        grid.addWidget(self.sb_chip_kb, 1, 1)

        grid.addWidget(QLabel("Base Address (Hex):"), 2, 0)
        self.le_base_addr = QLineEdit("2000")
        self.le_base_addr.setStyleSheet("background:#1E293B; color:#F8FAFC; padding:4px; border:1px solid #334155;")
        grid.addWidget(self.le_base_addr, 2, 1)

        self.left_layout.addLayout(grid)

        calc_btn = QPushButton("Calculate Address Range & Decoding Logic")
        calc_btn.setStyleSheet("background-color: #F97316; color: #FFFFFF; font-weight: bold; padding: 8px; border-radius: 4px;")
        calc_btn.clicked.connect(self.compute_address_decoder)
        self.left_layout.addWidget(calc_btn)
        self.left_layout.addStretch()

        self.sb_addr_lines.valueChanged.connect(lambda: self.compute_address_decoder())
        self.sb_chip_kb.valueChanged.connect(lambda: self.compute_address_decoder())
        self.le_base_addr.textChanged.connect(lambda: self.compute_address_decoder())

        self.compute_address_decoder()

    def compute_address_decoder(self):
        res = MPMCEngine.solve_address_decoder(
            self.sb_addr_lines.value(),
            self.sb_chip_kb.value(),
            self.le_base_addr.text()
        )
        self.render_output(
            title="Address Decoder Calculation Results",
            summary=f"Memory Range: {res['base_address_hex']} to {res['end_address_hex']}",
            derivation=[
                f"Total Address Bus Lines: {res['total_address_lines_str']} (Max {res['max_addressable_kb']} KB)",
                f"Chip Internal Address Lines: {res['chip_lines_str']} ({res['chip_address_lines']} bits for {res['bytes_per_chip']} bytes)",
                f"Decoder High Address Lines: {res['decoder_lines_str']} ({res['decoder_address_lines']} bits)",
                f"Decoder Output Logic: {res['decoder_logic']}"
            ]
        )

    # 2. 8051 Timer Reload UI
    def setup_timer_8051_ui(self):
        title = QLabel("8051 Timer Parameter Inputs")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #06B6D4;")
        self.left_layout.addWidget(title)

        grid = QGridLayout()
        grid.addWidget(QLabel("Crystal Oscillator (MHz):"), 0, 0)
        self.sb_xtal = EngineeringDoubleSpinBox()
        self.sb_xtal.setRange(1.0, 40.0)
        self.sb_xtal.setValue(11.0592)
        grid.addWidget(self.sb_xtal, 0, 1)

        grid.addWidget(QLabel("Target Delay (ms):"), 1, 0)
        self.sb_delay = EngineeringDoubleSpinBox()
        self.sb_delay.setRange(0.01, 100.0)
        self.sb_delay.setValue(1.0)
        grid.addWidget(self.sb_delay, 1, 1)

        self.left_layout.addLayout(grid)
        self.left_layout.addStretch()

        self.sb_xtal.valueChanged.connect(lambda: self.compute_timer_8051())
        self.sb_delay.valueChanged.connect(lambda: self.compute_timer_8051())
        self.compute_timer_8051()

    def compute_timer_8051(self):
        res = MPMCEngine.solve_8051_timer(self.sb_xtal.value(), self.sb_delay.value(), timer_mode=1)
        self.render_output(
            title="8051 Timer 16-bit Reload Calculation",
            summary=f"TH1 = {res['th_hex']}, TL1 = {res['tl_hex']} (Reload: {res['reload_hex']})",
            derivation=[
                f"Machine Clock: {res['machine_clock_khz']} kHz (12 T-states per cycle)",
                f"Timer Tick Period: {res['timer_clock_us']} µs",
                f"Counts Required: {res['counts_needed']} ticks",
                f"Actual Generated Delay: {res['actual_delay_ms']} ms"
            ]
        )

    # Generic Renderer
    def setup_hex_dec_ui(self):
        title = QLabel("Hex ↔ Decimal Converter")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #3B82F6;")
        self.left_layout.addWidget(title)

        self.le_hex_in = QLineEdit("2000")
        self.le_hex_in.setStyleSheet("background:#1E293B; color:#F8FAFC; padding:6px; border:1px solid #334155;")
        self.left_layout.addWidget(QLabel("Enter Hexadecimal / Decimal Value:"))
        self.left_layout.addWidget(self.le_hex_in)
        self.left_layout.addStretch()

        self.le_hex_in.textChanged.connect(lambda: self.compute_hex_dec())
        self.compute_hex_dec()

    def compute_hex_dec(self):
        res = MPMCEngine.solve_hex_dec(self.le_hex_in.text())
        self.render_output(
            title="Base Conversion & Flag Breakdown",
            summary=f"Decimal: {res['dec']} | Hex: {res['hex_16bit']}",
            derivation=[
                f"8-bit Hex: {res['hex_8bit']}",
                f"16-bit Hex: {res['hex_16bit']}",
                f"8-bit Binary: {res['bin_8bit']}",
                f"16-bit Binary: {res['bin_16bit']}",
                f"Octal: {res['octal']}",
                f"8085 CPU Flags: {res['flags_8085']}"
            ]
        )

    def setup_instruction_timing_ui(self):
        title = QLabel("Instruction Execution Timing")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #10B981;")
        self.left_layout.addWidget(title)

        grid = QGridLayout()
        grid.addWidget(QLabel("Instruction T-States:"), 0, 0)
        self.sb_t_states = EngineeringSpinBox()
        self.sb_t_states.setRange(1, 100)
        self.sb_t_states.setValue(7)
        grid.addWidget(self.sb_t_states, 0, 1)

        grid.addWidget(QLabel("CPU Clock (MHz):"), 1, 0)
        self.sb_clock_mhz = EngineeringDoubleSpinBox()
        self.sb_clock_mhz.setRange(0.1, 500.0)
        self.sb_clock_mhz.setValue(3.0)
        grid.addWidget(self.sb_clock_mhz, 1, 1)

        self.left_layout.addLayout(grid)
        self.left_layout.addStretch()

        self.sb_t_states.valueChanged.connect(lambda: self.compute_instruction_timing())
        self.sb_clock_mhz.valueChanged.connect(lambda: self.compute_instruction_timing())
        self.compute_instruction_timing()

    def compute_instruction_timing(self):
        res = MPMCEngine.solve_instruction_timing(self.sb_t_states.value(), self.sb_clock_mhz.value())
        self.render_output(
            title="Execution Time Results",
            summary=f"Total Execution Time: {res['total_execution_time_us']} µs ({res['total_execution_time_ns']} ns)",
            derivation=[
                f"Single T-State Period: {res['t_state_duration_us']} µs",
                f"Instruction T-States Count: {res['t_states']} T",
                f"CPU Clock Frequency: {res['clock_freq_mhz']} MHz",
                f"Instruction MIPS Equivalent: {res['mips_rating']} MIPS"
            ]
        )

    def setup_opcode_8085_ui(self):
        title = QLabel("8085 Instruction Opcode Finder")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F97316;")
        self.left_layout.addWidget(title)

        self.le_op_in = QLineEdit("MOV A, B")
        self.le_op_in.setStyleSheet("background:#1E293B; color:#F8FAFC; padding:6px; border:1px solid #334155;")
        self.left_layout.addWidget(QLabel("Search Instruction (e.g. MOV A, B, LXI H, CALL):"))
        self.left_layout.addWidget(self.le_op_in)
        self.left_layout.addStretch()

        self.le_op_in.textChanged.connect(lambda: self.compute_opcode_8085())
        self.compute_opcode_8085()

    def compute_opcode_8085(self):
        res = MPMCEngine.find_8085_opcode(self.le_op_in.text())
        self.render_output(
            title=f"8085 Instruction: {res['instruction']}",
            summary=f"Opcode: {res['hex_opcode']} ({res['bytes']} Byte(s))",
            derivation=[
                f"T-States: {res['t_states']} T",
                f"Machine Cycles: {res['cycles']}",
                f"Flags Affected: {res['flags']}"
            ]
        )

    def setup_interrupt_solver_ui(self):
        title = QLabel("Interrupt Priority & Vector Solver")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #06B6D4;")
        self.left_layout.addWidget(title)

        self.combo_proc = QComboBox()
        self.combo_proc.addItems(["8085 Microprocessor", "8051 Microcontroller"])
        self.combo_intr = QComboBox()
        self.combo_intr.addItems(["RST 7.5", "TRAP", "RST 6.5", "RST 5.5", "INTR"])

        self.left_layout.addWidget(QLabel("Processor:"))
        self.left_layout.addWidget(self.combo_proc)
        self.left_layout.addWidget(QLabel("Interrupt Source:"))
        self.left_layout.addWidget(self.combo_intr)
        self.left_layout.addStretch()

        self.combo_proc.currentIndexChanged.connect(lambda: self.compute_interrupt_solver())
        self.combo_intr.currentIndexChanged.connect(lambda: self.compute_interrupt_solver())
        self.compute_interrupt_solver()

    def compute_interrupt_solver(self):
        res = MPMCEngine.solve_interrupt_priority(self.combo_proc.currentText(), self.combo_intr.currentText())
        self.render_output(
            title=f"Interrupt Vector Analysis: {res['interrupt_name']}",
            summary=f"Vector Address: {res['vector_address']} | Priority Rank: #{res['priority_rank']}",
            derivation=[
                f"Processor Architecture: {res['processor']}",
                f"Trigger Type: {res['trigger_type']}",
                f"Maskability Status: {res['maskable']}"
            ]
        )

    def setup_uart_baud_ui(self):
        title = QLabel("UART Baud Rate Calculator")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #3B82F6;")
        self.left_layout.addWidget(title)

        grid = QGridLayout()
        grid.addWidget(QLabel("Crystal (MHz):"), 0, 0)
        self.sb_u_xtal = EngineeringDoubleSpinBox()
        self.sb_u_xtal.setRange(1.0, 40.0)
        self.sb_u_xtal.setValue(11.0592)
        grid.addWidget(self.sb_u_xtal, 0, 1)

        grid.addWidget(QLabel("Target Baud Rate:"), 1, 0)
        self.sb_baud = EngineeringSpinBox()
        self.sb_baud.setRange(1200, 115200)
        self.sb_baud.setValue(9600)
        grid.addWidget(self.sb_baud, 1, 1)

        self.left_layout.addLayout(grid)
        self.left_layout.addStretch()

        self.sb_u_xtal.valueChanged.connect(lambda: self.compute_uart_baud())
        self.sb_baud.valueChanged.connect(lambda: self.compute_uart_baud())
        self.compute_uart_baud()

    def compute_uart_baud(self):
        res = MPMCEngine.solve_uart_baud(self.sb_u_xtal.value(), self.sb_baud.value())
        self.render_output(
            title="8051 UART Mode 1 Baud Calculation",
            summary=f"TH1 Reload Value: {res['th1_hex']} ({res['th1_dec']} Decimal)",
            derivation=[
                f"Target Baud Rate: {res['target_baud']} bps",
                f"Actual Generated Baud Rate: {res['actual_baud']} bps",
                f"Baud Rate Error: {res['error_percentage']} %"
            ]
        )

    def setup_arm_clock_ui(self):
        title = QLabel("ARM Cortex PLL Clock Calculator")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F97316;")
        self.left_layout.addWidget(title)

        grid = QGridLayout()
        grid.addWidget(QLabel("HSE Crystal (MHz):"), 0, 0)
        self.sb_hse = EngineeringDoubleSpinBox()
        self.sb_hse.setRange(1.0, 50.0)
        self.sb_hse.setValue(8.0)
        grid.addWidget(self.sb_hse, 0, 1)

        grid.addWidget(QLabel("PLL N Multiplier:"), 1, 0)
        self.sb_plln = EngineeringSpinBox()
        self.sb_plln.setRange(50, 432)
        self.sb_plln.setValue(336)
        grid.addWidget(self.sb_plln, 1, 1)

        self.left_layout.addLayout(grid)
        self.left_layout.addStretch()

        self.sb_hse.valueChanged.connect(lambda: self.compute_arm_clock())
        self.sb_plln.valueChanged.connect(lambda: self.compute_arm_clock())
        self.compute_arm_clock()

    def compute_arm_clock(self):
        res = MPMCEngine.solve_arm_clock(self.sb_hse.value(), 8, self.sb_plln.value(), 2)
        self.render_output(
            title="ARM Cortex System Clock Results",
            summary=f"SystemCoreClock (SYSCLK): {res['sysclk_mhz']} MHz",
            derivation=[
                f"HSE Input Crystal: {res['hse_mhz']} MHz",
                f"VCO Output Clock: {res['vco_output_mhz']} MHz",
                f"AHB Bus Clock: {res['ahb_freq_mhz']} MHz",
                f"APB1 Clock (Max 42MHz): {res['apb1_freq_mhz']} MHz",
                f"APB2 Clock (Max 84MHz): {res['apb2_freq_mhz']} MHz"
            ]
        )

    def render_output(self, title: str, summary: str, derivation: list):
        while self.right_layout.count():
            child = self.right_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Summary Card
        s_card = QFrame()
        s_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #F97316; border-radius: 8px; padding: 15px; }")
        s_lay = QVBoxLayout(s_card)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F97316;")
        s_lay.addWidget(t_lbl)

        res_lbl = QLabel(summary)
        res_lbl.setStyleSheet("font-size: 14pt; font-weight: bold; color: #10B981; margin-top: 5px;")
        s_lay.addWidget(res_lbl)
        self.right_layout.addWidget(s_card)

        # Step-by-Step Derivation Card
        d_card = QFrame()
        d_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 15px; }")
        d_lay = QVBoxLayout(d_card)

        d_title = QLabel("📝 Step-by-Step Engineering Derivation")
        d_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #06B6D4; margin-bottom: 8px;")
        d_lay.addWidget(d_title)

        for step in derivation:
            step_lbl = QLabel(f"•  {step}")
            step_lbl.setStyleSheet("color: #E2E8F0; font-size: 9.5pt; margin-bottom: 4px;")
            step_lbl.setWordWrap(True)
            d_lay.addWidget(step_lbl)

        self.right_layout.addWidget(d_card)
