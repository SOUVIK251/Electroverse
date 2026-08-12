"""
ElectroVerse Microprocessor & Microcontroller Reference View
1000+ Multi-Processor Educational Program Knowledge Base & Opcode Matrix Explorer.
"""

import os
import json
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView,
    QTreeWidget, QTreeWidgetItem, QSplitter, QTextEdit, QPushButton, QScrollArea, QComboBox
)
from PySide6.QtCore import Qt
from src.core.logger import log
from src.core.i8085.program_database_manager import ProgramDatabaseManager


class MPMCReferenceView(QWidget):
    """Engineering Reference Tables & 1000+ Multi-Processor Knowledge Base Explorer."""

    def __init__(self, hub_view=None, parent=None):
        super().__init__(parent)
        self.hub_view = hub_view
        self.db_mgr = ProgramDatabaseManager()
        log.info("Initializing MPMCReferenceView with 1000+ program database explorer")
        self.init_ui()
        self.load_reference_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header Search & Filter Bar
        hdr_bar = QFrame()
        hdr_bar.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 8px 15px; }")
        h_lay = QHBoxLayout(hdr_bar)

        h_title = QLabel("📚 1000+ MULTI-PROCESSOR EDUCATIONAL PROGRAM KNOWLEDGE BASE")
        h_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #10B981;")
        h_lay.addWidget(h_title)
        h_lay.addStretch()

        self.family_filter = QComboBox()
        self.family_filter.addItems([
            "All Processor Families",
            "Intel 8085",
            "Intel 8086",
            "Intel 8051",
            "AVR (ATmega32/328P)",
            "ARM Cortex-M (STM32)",
            "RISC-V (RV32I)",
            "PIC Microcontroller (PIC16F)",
            "MSP430 Microcontroller"
        ])
        self.family_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #10B981;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
            }
        """)
        self.family_filter.currentTextChanged.connect(self.populate_program_tree)
        h_lay.addWidget(self.family_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter 1000+ Programs & Tables...")
        self.search_input.setFixedWidth(260)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #10B981;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        h_lay.addWidget(self.search_input)
        layout.addWidget(hdr_bar)

        # Reference Tabs
        self.ref_tabs = QTabWidget()
        self.ref_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1E293B; background-color: #0B1020; border-radius: 8px; }
            QTabBar::tab {
                background-color: #141B2D;
                color: #94A3B8;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 9pt;
                border: 1px solid #1E293B;
                border-bottom: none;
                margin-right: 3px;
            }
            QTabBar::tab:selected { background-color: #10B981; color: #FFFFFF; border-color: #10B981; }
        """)
        layout.addWidget(self.ref_tabs)

        # Tab 0: 📖 1000+ Program Explorer
        prog_db_tab = self.create_program_explorer_tab()
        self.ref_tabs.addTab(prog_db_tab, "📖 1000+ Program Library")

    def create_program_explorer_tab(self) -> QWidget:
        tab = QWidget()
        t_lay = QHBoxLayout(tab)
        t_lay.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #1E293B; width: 2px; }")

        # Left: Program Tree
        left_frame = QFrame()
        left_frame.setStyleSheet("QFrame { background-color: #0B1020; border: 1px solid #1E293B; border-radius: 6px; }")
        l_lay = QVBoxLayout(left_frame)
        l_lay.setContentsMargins(8, 8, 8, 8)

        self.tree_hdr = QLabel("UNIVERSITY LAB PROGRAM DATABASE")
        self.tree_hdr.setStyleSheet("color:#A0D8AF; font-weight:bold; font-size:8.5pt;")
        l_lay.addWidget(self.tree_hdr)

        self.prog_tree = QTreeWidget()
        self.prog_tree.setHeaderHidden(True)
        self.prog_tree.setStyleSheet("""
            QTreeWidget { background: transparent; border: none; color: #94A3B8; font-size: 9pt; }
            QTreeWidget::item { padding: 5px; }
            QTreeWidget::item:hover { background-color: #1E293B; color: #F8FAFC; border-radius: 4px; }
            QTreeWidget::item:selected { background-color: #0F172A; color: #10B981; font-weight: bold; border-radius: 4px; }
        """)
        self.prog_tree.itemClicked.connect(self.on_program_selected)
        l_lay.addWidget(self.prog_tree)

        # Right: Detailed Program View
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: 1px solid #1E293B; border-radius: 6px; background-color: #0B1020; }")

        self.detail_container = QFrame()
        self.detail_lay = QVBoxLayout(self.detail_container)
        self.detail_lay.setContentsMargins(16, 16, 16, 16)
        self.detail_lay.setSpacing(12)

        right_scroll.setWidget(self.detail_container)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_scroll)
        splitter.setSizes([340, 660])

        t_lay.addWidget(splitter)
        return tab

    def load_reference_data(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        json_path = os.path.join(project_root, "src", "data", "mpmc", "reference_tables.json")

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for sec in data.get("reference_sections", []):
                        self.create_table_tab(sec)
            except Exception as e:
                log.error(f"Error loading reference_tables.json: {e}")

        self.populate_program_tree()

    def populate_program_tree(self):
        self.prog_tree.clear()
        all_programs = self.db_mgr.get_all_programs()
        selected_family = self.family_filter.currentText()

        # Group programs by family and category
        family_tree: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for prog in all_programs:
            fam = prog.get("processor_family", "Intel 8085")
            cat = prog.get("category", "General")

            if selected_family != "All Processor Families" and fam != selected_family:
                continue

            if fam not in family_tree:
                family_tree[fam] = {}
            if cat not in family_tree[fam]:
                family_tree[fam][cat] = []
            family_tree[fam][cat].append(prog)

        total_visible = 0
        for fam_name, cat_dict in family_tree.items():
            fam_count = sum(len(progs) for progs in cat_dict.values())
            total_visible += fam_count
            fam_item = QTreeWidgetItem(self.prog_tree, [f"💻 {fam_name} ({fam_count})"])
            fam_item.setExpanded(True if len(family_tree) == 1 else False)
            fam_item.setData(0, Qt.ItemDataRole.UserRole, None)

            for cat_name, progs in cat_dict.items():
                cat_item = QTreeWidgetItem(fam_item, [f"📂 {cat_name} ({len(progs)})"])
                cat_item.setData(0, Qt.ItemDataRole.UserRole, None)

                for prog in progs:
                    prog_item = QTreeWidgetItem(cat_item, [f"📄 {prog.get('program_name', 'Program')}"])
                    prog_item.setData(0, Qt.ItemDataRole.UserRole, prog)

        self.tree_hdr.setText(f"PROGRAM DATABASE ({total_visible} PROGRAMS LOADED)")

        if self.prog_tree.topLevelItemCount() > 0:
            first_fam = self.prog_tree.topLevelItem(0)
            if first_fam.childCount() > 0 and first_fam.child(0).childCount() > 0:
                first_prog_item = first_fam.child(0).child(0)
                self.prog_tree.setCurrentItem(first_prog_item)
                self.on_program_selected(first_prog_item)

    def on_program_selected(self, item: QTreeWidgetItem):
        prog = item.data(0, Qt.ItemDataRole.UserRole)
        if not prog:
            return

        # Clear container
        while self.detail_lay.count():
            child = self.detail_lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Header Title Bar
        title_box = QFrame()
        title_box.setStyleSheet("background: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 12px;")
        tb_lay = QVBoxLayout(title_box)

        p_name = QLabel(prog.get("program_name", "Microprocessor Program"))
        p_name.setStyleSheet("color: #10B981; font-size: 13pt; font-weight: bold;")
        tb_lay.addWidget(p_name)

        meta_lbl = QLabel(f"Processor: {prog.get('processor_family')}  |  Category: {prog.get('category')}  |  Difficulty: {prog.get('difficulty', 'Basic')}")
        meta_lbl.setStyleSheet("color: #94A3B8; font-size: 9pt;")
        tb_lay.addWidget(meta_lbl)

        # Load into Trainer Button (if 8085)
        if "8085" in prog.get("processor_family", ""):
            load_btn = QPushButton("🚀 Load Program into 8085 Trainer Kit")
            load_btn.setStyleSheet("""
                QPushButton {
                    background: #10B981; color: #FFFFFF; font-weight: bold;
                    border-radius: 5px; padding: 8px 16px; font-size: 9.5pt;
                }
                QPushButton:hover { background: #059669; }
            """)
            load_btn.clicked.connect(lambda _, p=prog: self.load_program_into_trainer(p))
            tb_lay.addWidget(load_btn, 0, Qt.AlignmentFlag.AlignRight)

        self.detail_lay.addWidget(title_box)

        # Objective & Theory
        self._add_section("🎯 Objective", prog.get("objective", ""))
        self._add_section("📖 Theory & Overview", prog.get("theory", ""))

        # Algorithm
        algo_lines = prog.get("algorithm", [])
        if isinstance(algo_lines, list):
            algo_text = "\n".join(algo_lines)
        else:
            algo_text = str(algo_lines)
        self._add_section("⚙️ Algorithm", algo_text)

        # Assembly Code
        code_widget = QTextEdit()
        code_widget.setReadOnly(True)
        code_widget.setPlainText(prog.get("assembly_code", ""))
        code_widget.setStyleSheet("""
            QTextEdit {
                background-color: #020D02;
                color: #33FF66;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 9.5pt;
                border: 1px solid #1A4020;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        code_box = QFrame()
        cb_lay = QVBoxLayout(code_box)
        cb_lay.setContentsMargins(0, 0, 0, 0)
        c_lbl = QLabel(f"💻 {prog.get('processor_family')} Assembly Program & Machine Hex")
        c_lbl.setStyleSheet("color: #A0D8AF; font-weight: bold; font-size: 10pt;")
        cb_lay.addWidget(c_lbl)
        cb_lay.addWidget(code_widget)

        # Machine Code Bytes
        hex_bytes = prog.get("machine_code_hex", [])
        if hex_bytes:
            hex_str = " ".join(hex_bytes)
            hex_lbl = QLabel(f"Machine Hex Bytes:  {hex_str}")
            hex_lbl.setStyleSheet("color: #FACC15; font-family: Consolas, monospace; font-size: 9.5pt; font-weight: bold; padding: 4px 0;")
            cb_lay.addWidget(hex_lbl)

        self.detail_lay.addWidget(code_box)

        # Sample Input / Output
        s_in = json.dumps(prog.get("sample_input", {}), indent=2)
        s_out = json.dumps(prog.get("sample_output", {}), indent=2)
        self._add_section("🧪 Sample Input & Expected Output", f"Sample Input:\n{s_in}\n\nExpected Output:\n{s_out}")

        # Viva Questions
        viva = prog.get("viva_questions", [])
        if viva:
            v_lines = []
            for item in viva:
                v_lines.append(f"Q: {item.get('q')}\nA: {item.get('a')}\n")
            self._add_section("❓ University Viva & Exam Questions", "\n".join(v_lines))

        # Practical Applications
        apps = prog.get("practical_applications", [])
        if apps:
            app_lines = "\n".join([f"• {app}" for app in apps])
            self._add_section("💡 Practical Applications & Real-World Use", app_lines)

    def _add_section(self, title: str, content: str):
        sec_box = QFrame()
        sec_box.setStyleSheet("background: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 10px;")
        lay = QVBoxLayout(sec_box)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #10B981; font-weight: bold; font-size: 10pt;")
        lay.addWidget(t_lbl)

        c_lbl = QLabel(content)
        c_lbl.setWordWrap(True)
        c_lbl.setStyleSheet("color: #E2E8F0; font-size: 9pt; font-family: Consolas, sans-serif; line-height: 1.4;")
        lay.addWidget(c_lbl)

        self.detail_lay.addWidget(sec_box)

    def load_program_into_trainer(self, prog: Dict[str, Any]):
        """Write 8085 program's machine code into the Trainer at address 2000H and switch to Trainer tab."""
        if not self.hub_view:
            return

        self.hub_view.main_tabs.setCurrentIndex(3)

        sim_view = self.hub_view.sim_widget
        if hasattr(sim_view, "trainer"):
            trainer = sim_view.trainer
            cpu = trainer.cpu

            hex_bytes = prog.get("machine_code_hex", [])
            for i, byte_hex in enumerate(hex_bytes):
                try:
                    val = int(byte_hex, 16) & 0xFF
                    cpu.write_mem_direct(0x2000 + i, val)
                except ValueError:
                    pass

            sample_in = prog.get("sample_input", {}).get("memory", {})
            for addr_str, val_str in sample_in.items():
                try:
                    a = int(addr_str.replace("H", ""), 16) & 0xFFFF
                    v = int(val_str.replace("H", ""), 16) & 0xFF
                    cpu.write_mem_direct(a, v)
                except ValueError:
                    pass

            trainer.tc._program_start_address = 0x2000
            trainer.tc._current_address = 0x2000
            trainer._refresh_all()
            trainer._log(f"Loaded '{prog.get('program_name')}' into RAM starting at 2000H. Press GO to execute!")

    def create_table_tab(self, section):
        tab = QWidget()
        t_lay = QVBoxLayout(tab)
        t_lay.setContentsMargins(10, 10, 10, 10)

        table = QTableWidget()
        headers = section.get("headers", [])
        rows = section.get("rows", [])

        table.setColumnCount(len(headers))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #0F172A;
                color: #E2E8F0;
                gridline-color: #1E293B;
                border: 1px solid #1E293B;
                border-radius: 6px;
                font-size: 9.5pt;
            }
            QHeaderView::section {
                background-color: #1E293B;
                color: #10B981;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background-color: #10B981; color: #FFFFFF; }
        """)

        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                table.setItem(r_idx, c_idx, item)

        t_lay.addWidget(table)
        self.ref_tabs.addTab(tab, section.get("title", "Reference Table"))

    def on_search_changed(self, text: str):
        query = text.lower().strip()
        self.filter_current_table(query)

        if query:
            matching = self.db_mgr.search_programs(query)
            for i in range(self.prog_tree.topLevelItemCount()):
                fam_item = self.prog_tree.topLevelItem(i)
                for j in range(fam_item.childCount()):
                    cat_item = fam_item.child(j)
                    for k in range(cat_item.childCount()):
                        child = cat_item.child(k)
                        prog = child.data(0, Qt.ItemDataRole.UserRole)
                        child.setHidden(prog not in matching)
        else:
            for i in range(self.prog_tree.topLevelItemCount()):
                fam_item = self.prog_tree.topLevelItem(i)
                for j in range(fam_item.childCount()):
                    cat_item = fam_item.child(j)
                    for k in range(cat_item.childCount()):
                        cat_item.child(k).setHidden(False)

    def filter_current_table(self, text):
        curr_widget = self.ref_tabs.currentWidget()
        if not curr_widget:
            return
        table = curr_widget.findChild(QTableWidget)
        if not table:
            return

        query = text.lower().strip()
        for r in range(table.rowCount()):
            match = False
            for c in range(table.columnCount()):
                item = table.item(r, c)
                if item and query in item.text().lower():
                    match = True
                    break
            table.setRowHidden(r, not match and query != "")
