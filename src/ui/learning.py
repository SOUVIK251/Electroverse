from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QScrollArea,
    QSplitter, QPushButton, QGridLayout, QSizePolicy, QStackedWidget,
    QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont
import qtawesome as qta

from src.core.logger import log
from src.ui.learning_content import get_lesson_data

def clear_layout(layout):
    """
    Recursively clears all widgets, sub-layouts, and spacers from the layout
    to avoid layout memory leaks and overlapping ghost elements.
    """
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            sub_layout = item.layout()
            if sub_layout is not None:
                clear_layout(sub_layout)


LESSON_RESOURCES = {
    "voltage": [
        {"type": "toolkit", "label": "🛠️ Voltage Divider Calculator", "target": 1},
        {"type": "toolkit", "label": "🛠️ Ohm's Law Calculator", "target": 0}
    ],
    "current": [
        {"type": "toolkit", "label": "🛠️ Current Divider Calculator", "target": 2},
        {"type": "toolkit", "label": "🛠️ Ohm's Law Calculator", "target": 0}
    ],
    "resistance": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "resistor"},
        {"type": "toolkit", "label": "🛠️ Ohm's Law Calculator", "target": 0}
    ],
    "ohm_law": [
        {"type": "toolkit", "label": "🛠️ Ohm's Law Calculator", "target": 0},
        {"type": "toolkit", "label": "🛠️ Power Calculator", "target": 3}
    ],
    "kvl": [
        {"type": "simulation", "label": "🧪 Try Voltage Divider Simulation", "target": 8},
        {"type": "toolkit", "label": "🛠️ Voltage Divider Calculator", "target": 1}
    ],
    "kcl": [
        {"type": "toolkit", "label": "🛠️ Current Divider Calculator", "target": 2}
    ],
    "resistor": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "resistor"},
        {"type": "toolkit", "label": "🛠️ Ohm's Law Calculator", "target": 0}
    ],
    "capacitor": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "capacitor"},
        {"type": "toolkit", "label": "🛠️ Capacitive Reactance Calculator", "target": 8}
    ],
    "inductor": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "inductor"},
        {"type": "toolkit", "label": "🛠️ Inductive Reactance Calculator", "target": 9}
    ],
    "pn_diode": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "pn_junction_diode"}
    ],
    "zener_diode": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "zener_diode"}
    ],
    "led": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "led"},
        {"type": "toolkit", "label": "🛠️ LED Series Resistor Calculator", "target": 10}
    ],
    "bjt": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "bjt"}
    ],
    "mosfet": [
        {"type": "library", "label": "📚 Open in Component Library", "target": "mosfet"}
    ],
    "half_wave": [
        {"type": "simulation", "label": "🧪 Try in Simulation Lab", "target": 5},
        {"type": "library", "label": "📚 View Diode Specs", "target": "pn_junction_diode"}
    ],
    "full_wave": [
        {"type": "simulation", "label": "🧪 Try in Simulation Lab", "target": 6},
        {"type": "library", "label": "📚 View Bridge Rectifier Specs", "target": "bridge_rectifier"}
    ],
    "pos_clipper": [
        {"type": "simulation", "label": "🧪 Try in Simulation Lab", "target": 7},
        {"type": "library", "label": "📚 View Zener Diode Specs", "target": "zener_diode"}
    ],
    "neg_clipper": [
        {"type": "simulation", "label": "🧪 Try in Simulation Lab", "target": 7},
        {"type": "library", "label": "📚 View Zener Diode Specs", "target": "zener_diode"}
    ],
    "pos_clamper": [
        {"type": "library", "label": "📚 View Capacitor", "target": "capacitor"},
        {"type": "library", "label": "📚 View Diode Specs", "target": "pn_junction_diode"}
    ],
    "neg_clamper": [
        {"type": "library", "label": "📚 View Capacitor", "target": "capacitor"},
        {"type": "library", "label": "📚 View Diode Specs", "target": "pn_junction_diode"}
    ],
    "low_pass": [
        {"type": "simulation", "label": "🧪 Try in Simulation Lab", "target": 3},
        {"type": "library", "label": "📚 View Resistor", "target": "resistor"},
        {"type": "library", "label": "📚 View Capacitor", "target": "capacitor"},
        {"type": "toolkit", "label": "🛠️ Frequency Calculator", "target": 7}
    ],
    "high_pass": [
        {"type": "simulation", "label": "🧪 Try in Simulation Lab", "target": 4},
        {"type": "library", "label": "📚 View Resistor", "target": "resistor"},
        {"type": "library", "label": "📚 View Capacitor", "target": "capacitor"},
        {"type": "toolkit", "label": "🛠️ Frequency Calculator", "target": 7}
    ],
    "rc_charging": [
        {"type": "library", "label": "📚 View Resistor", "target": "resistor"},
        {"type": "library", "label": "📚 View Capacitor", "target": "capacitor"},
        {"type": "toolkit", "label": "🛠️ RC Time Constant Calculator", "target": 4},
        {"type": "simulation", "label": "🧪 Open RC Charging Simulation", "target": 0}
    ],
    "rc_discharging": [
        {"type": "library", "label": "📚 View Resistor", "target": "resistor"},
        {"type": "library", "label": "📚 View Capacitor", "target": "capacitor"},
        {"type": "toolkit", "label": "🛠️ RC Time Constant Calculator", "target": 4},
        {"type": "simulation", "label": "🧪 Open RC Discharging Simulation", "target": 0}
    ],
    "rl_transient": [
        {"type": "library", "label": "📚 View Resistor", "target": "resistor"},
        {"type": "library", "label": "📚 View Inductor", "target": "inductor"},
        {"type": "toolkit", "label": "🛠️ RL Time Constant Calculator", "target": 5},
        {"type": "simulation", "label": "🧪 Open RL Transient Simulation", "target": 1}
    ],
    "rlc_resonance": [
        {"type": "library", "label": "📚 View Resistor", "target": "resistor"},
        {"type": "library", "label": "📚 View Capacitor", "target": "capacitor"},
        {"type": "library", "label": "📚 View Inductor", "target": "inductor"},
        {"type": "toolkit", "label": "🛠️ RLC Resonance Calculator", "target": 6},
        {"type": "simulation", "label": "🧪 Open Series RLC Resonance Simulation", "target": 2}
    ],
    "oscilloscope": [
        {"type": "simulation", "label": "🧪 Try in Simulation Lab", "target": 0}
    ],
    "multimeter": [
        {"type": "library", "label": "📚 View Resistor Specs", "target": "resistor"},
        {"type": "toolkit", "label": "🛠️ Ohm's Law Calculator", "target": 0}
    ],
    "func_gen": [
        {"type": "toolkit", "label": "🛠️ Frequency Calculator", "target": 7}
    ]
}


class LearningView(QWidget):
    """
    A premium interactive course engine layout.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing LearningView")
        
        self.active_lesson_id = "voltage"
        
        # Base horizontal split layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        
        # Left Panel (Collapsible course tree explorer)
        self.left_panel = QFrame()
        self.left_panel.setObjectName("course-tree-panel")
        self.left_panel.setFixedWidth(270)
        self.left_panel.setStyleSheet("""
            QFrame#course-tree-panel {
                background-color: #0b0f19;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)
        
        # Explorer Title Row
        exp_header = QHBoxLayout()
        exp_title = QLabel("📚 Course Syllabus")
        exp_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;")
        exp_header.addWidget(exp_title)
        exp_header.addStretch()
        left_layout.addLayout(exp_header)
        
        # Course Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search lessons...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 9pt;
            }
            QLineEdit:focus {
                border-color: #06b6d4;
            }
        """)
        self.search_input.textChanged.connect(self.filter_syllabus_tree)
        left_layout.addWidget(self.search_input)
        
        # Syllabus Tree Widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                color: #94a3b8;
                font-size: 9.5pt;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:hover {
                background-color: #1e293b;
                border-radius: 4px;
                color: #f8fafc;
            }
            QTreeWidget::item:selected {
                background-color: rgba(6, 182, 212, 0.15);
                color: #06b6d4;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(self.tree_widget)
        
        # Right Panel Stack
        self.right_stack = QStackedWidget()
        
        # Setup catalog page
        self.setup_catalog_dashboard()
        
        # Setup lesson viewer page wrapper
        self.setup_lesson_viewer()
        
        # Assemble split container
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
                width: 6px;
            }
        """)
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_stack)
        self.splitter.setSizes([270, 930])
        
        self.main_layout.addWidget(self.splitter)
        
        # Build Syllabus
        self.build_syllabus_tree()
        
        # Open catalog initially
        self.right_stack.setCurrentIndex(0)

    # -------------------------------------------------------------
    # Collapse/Expand Toggle
    # -------------------------------------------------------------
    def toggle_explorer(self):
        is_hidden = self.left_panel.width() <= 0
        self.left_panel.setFixedWidth(270 if is_hidden else 0)

    # -------------------------------------------------------------
    # Tree Syllabus Builder
    # -------------------------------------------------------------
    def build_syllabus_tree(self):
        self.tree_widget.clear()
        
        syllabus_structure = [
            ("📘 Basic Electronics", ["voltage", "current", "resistance", "ohm_law", "kvl", "kcl"]),
            ("📗 Passive Components", ["resistor", "capacitor", "inductor"]),
            ("📙 Semiconductor Devices", ["pn_diode", "zener_diode", "led", "bjt", "mosfet"]),
            ("📘 Rectifier Circuits", ["half_wave", "full_wave"]),
            ("📙 Clippers & Clampers", ["pos_clipper", "neg_clipper", "pos_clamper", "neg_clamper"]),
            ("📘 Filters", ["low_pass", "high_pass"]),
            ("📙 Transient Circuits", ["rc_charging", "rc_discharging", "rl_transient"]),
            ("📘 Resonance", ["rlc_resonance"]),
            ("📙 Instruments", ["oscilloscope", "multimeter", "func_gen"])
        ]
        
        self.syllabus_items = {}
        for cat_title, lessons in syllabus_structure:
            cat_item = QTreeWidgetItem(self.tree_widget)
            cat_item.setText(0, cat_title)
            cat_item.setFont(0, QFont("Segoe UI", 9.5, QFont.Weight.Bold))
            cat_item.setForeground(0, QColor("#e2e8f0"))
            
            for lid in lessons:
                data = get_lesson_data(lid)
                if data:
                    child_item = QTreeWidgetItem(cat_item)
                    child_item.setText(0, f"• {data['name']}")
                    child_item.setData(0, Qt.ItemDataRole.UserRole, lid)
                    child_item.setForeground(0, QColor("#94a3b8"))
            
            cat_item.setExpanded(True)

    def filter_syllabus_tree(self, text):
        query = text.lower().strip()
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            match_count = 0
            for j in range(cat_item.childCount()):
                child_item = cat_item.child(j)
                comp_name = child_item.text(0).lower()
                if query in comp_name:
                    child_item.setHidden(False)
                    match_count += 1
                else:
                    child_item.setHidden(True)
            cat_item.setHidden(match_count == 0 and query != "")

    def on_tree_item_clicked(self, item):
        lid = item.data(0, Qt.ItemDataRole.UserRole)
        if lid:
            self.load_lesson(lid)

    # -------------------------------------------------------------
    # Page 0: Catalog Dashboard Setup
    # -------------------------------------------------------------
    def setup_catalog_dashboard(self):
        catalog_scroll = QScrollArea()
        catalog_scroll.setWidgetResizable(True)
        catalog_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        catalog_container = QFrame()
        catalog_container.setObjectName("catalog-panel")
        catalog_container.setStyleSheet("QFrame#catalog-panel { background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; }")
        
        cat_layout = QVBoxLayout(catalog_container)
        cat_layout.setContentsMargins(25, 25, 25, 25)
        cat_layout.setSpacing(20)
        
        # 1. Main Banner
        banner_card = QFrame()
        banner_card.setStyleSheet("background-color: #0f172a; border: 1px solid #06b6d4; border-radius: 8px; padding: 20px;")
        banner_layout = QVBoxLayout(banner_card)
        
        starts = QLabel("★★★★★")
        starts.setStyleSheet("color: #f59e0b; font-size: 14pt; font-weight: bold;")
        banner_layout.addWidget(starts)
        
        banner_title = QLabel("Learning Mode")
        banner_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #f8fafc;")
        banner_layout.addWidget(banner_title)
        
        banner_sub = QLabel("Professional Electronics Course | 29 Lessons | 120+ Diagrams | 30+ Experiments | Interactive Quizzes")
        banner_sub.setStyleSheet("font-size: 10.5pt; color: #06b6d4; margin-top: 5px;")
        banner_layout.addWidget(banner_sub)
        
        cat_layout.addWidget(banner_card)
        
        # 2. Topic Pill Filters & Catalog Search
        dash_search_layout = QHBoxLayout()
        self.dash_search = QLineEdit()
        self.dash_search.setPlaceholderText("Search course modules...")
        self.dash_search.setStyleSheet("""
            QLineEdit {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9.5pt;
            }
        """)
        self.dash_search.textChanged.connect(self.filter_dashboard_cards)
        dash_search_layout.addWidget(self.dash_search)
        cat_layout.addLayout(dash_search_layout)
        
        # 3. Course Cards Grid
        self.grid_widget = QWidget()
        self.cards_grid = QGridLayout(self.grid_widget)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setSpacing(15)
        
        self.populate_course_cards()
        cat_layout.addWidget(self.grid_widget)
        cat_layout.addStretch()
        
        catalog_scroll.setWidget(catalog_container)
        self.right_stack.addWidget(catalog_scroll)

    def populate_course_cards(self):
        modules = [
            ("Basic Electronics", "Fundamentals of current, EMF potential, Ohm's Law and network loop algorithms.", 6, "Beginner", "#06b6d4"),
            ("Passive Components", "Detailed behavior of resistors, capacitive storage plates, and inductor magnetic reactors.", 3, "Beginner", "#10b981"),
            ("Semiconductor Devices", "PN diodes, LED properties, Zener clamp breakdown switches, BJT & MOSFET operations.", 5, "Intermediate", "#f59e0b"),
            ("Rectifier Circuits", "Converting alternating waves to pulsating DC supplies with single and bridge diodes.", 2, "Intermediate", "#3b82f6"),
            ("Clippers & Clampers", "Clipping input waveform peaks and clamping references upwards or downwards.", 4, "Intermediate", "#a855f7"),
            ("Filters", "Low-pass and high-pass RC filter circuits and signal conditioning parameters.", 2, "Intermediate", "#ec4899"),
            ("Transient Circuits", "RC time constant transients charging, discharging, and RL loops.", 3, "Advanced", "#ef4444"),
            ("Resonance", "Series resonant RLC networks exploring frequency response spikes.", 1, "Advanced", "#14b8a6"),
            ("Instruments", "Operation of DSO digital scopes, diagnostic multimeters, and function generators.", 3, "Beginner", "#64748b")
        ]
        
        self.dashboard_cards = []
        for i, (title, desc, size, diff, color) in enumerate(modules):
            card = QFrame()
            card.setStyleSheet(f"background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
            lay = QVBoxLayout(card)
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f8fafc;")
            
            diff_lbl = QLabel(diff)
            diff_lbl.setStyleSheet(f"background-color: {color}22; color: {color}; border: 1px solid {color}; border-radius: 4px; padding: 2px 6px; font-size: 8pt; font-weight: bold;")
            
            hdr = QHBoxLayout()
            hdr.addWidget(lbl_title)
            hdr.addStretch()
            hdr.addWidget(diff_lbl)
            lay.addLayout(hdr)
            
            lbl_desc = QLabel(desc)
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("color: #94a3b8; font-size: 9.5pt; margin-top: 5px;")
            lay.addWidget(lbl_desc)
            
            foot = QHBoxLayout()
            foot.addWidget(QLabel(f"📚 {size} Lessons"))
            foot.addStretch()
            
            btn = QPushButton("Open Module")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #f8fafc;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #06b6d4;
                }
            """)
            # Connect opening first lesson of target module
            mapping = {
                "Basic Electronics": "voltage",
                "Passive Components": "resistor",
                "Semiconductor Devices": "pn_diode",
                "Rectifier Circuits": "half_wave",
                "Clippers & Clampers": "pos_clipper",
                "Filters": "low_pass",
                "Transient Circuits": "rc_charging",
                "Resonance": "rlc_resonance",
                "Instruments": "oscilloscope"
            }
            target_lid = mapping.get(title, "voltage")
            btn.clicked.connect(lambda checked, lid=target_lid: self.load_lesson(lid))
            
            foot.addWidget(btn)
            lay.addLayout(foot)
            
            row = i // 2
            col = i % 2
            self.cards_grid.addWidget(card, row, col)
            self.dashboard_cards.append((card, title))

    def filter_dashboard_cards(self, text):
        query = text.lower().strip()
        for card, title in self.dashboard_cards:
            card.setVisible(query in title.lower())

    # -------------------------------------------------------------
    # Page 1: Lesson Viewer Setup
    # -------------------------------------------------------------
    def setup_lesson_viewer(self):
        viewer_scroll = QScrollArea()
        viewer_scroll.setWidgetResizable(True)
        viewer_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.viewer_container = QFrame()
        self.viewer_container.setObjectName("viewer-panel")
        self.viewer_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.viewer_container.setStyleSheet("QFrame#viewer-panel { background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; }")
        
        self.viewer_layout = QVBoxLayout(self.viewer_container)
        self.viewer_layout.setContentsMargins(25, 25, 25, 25)
        self.viewer_layout.setSpacing(20)
        
        viewer_scroll.setWidget(self.viewer_container)
        self.right_stack.addWidget(viewer_scroll)

    # -------------------------------------------------------------
    # Dynamic Lesson Loader (Renders all required sections under the 60/40 visual rule)
    # -------------------------------------------------------------
    def load_lesson(self, lesson_id: str):
        self.active_lesson_id = lesson_id
        data = get_lesson_data(lesson_id)
        if not data:
            return
            
        # Highlight in tree view
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                if child.data(0, Qt.ItemDataRole.UserRole) == lesson_id:
                    self.tree_widget.setCurrentItem(child)
                    break
                    
        # Clear previous layout cleanly using recursive helper
        clear_layout(self.viewer_layout)
                
        self.right_stack.setCurrentIndex(1)
        
        # COLLAPSE SYLLABUS TOGGLE ON HEADER ROW
        top_ctrl = QHBoxLayout()
        collapse_btn = QPushButton(" ◧ Toggle Syllabus")
        collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        collapse_btn.clicked.connect(self.toggle_explorer)
        top_ctrl.addWidget(collapse_btn)
        
        back_btn = QPushButton(" Back to Catalog")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        back_btn.clicked.connect(lambda: self.right_stack.setCurrentIndex(0))
        top_ctrl.addWidget(back_btn)
        top_ctrl.addStretch()
        self.viewer_layout.addLayout(top_ctrl)
        
        # 1. Lesson Header Card
        header_card = QFrame()
        header_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        hdr_layout = QVBoxLayout(header_card)
        
        title_row = QHBoxLayout()
        name_lbl = QLabel(data["name"])
        name_lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: #f8fafc;")
        title_row.addWidget(name_lbl)
        
        diff_val = data["difficulty"]
        diff_color = "#10b981" if diff_val == "Beginner" else "#f59e0b" if diff_val == "Intermediate" else "#ef4444"
        diff_lbl = QLabel(f"● {diff_val}")
        diff_lbl.setStyleSheet(f"color: {diff_color}; font-weight: bold; font-size: 10pt; padding: 4px;")
        title_row.addWidget(diff_lbl)
        title_row.addStretch()
        hdr_layout.addLayout(title_row)
        
        meta_row = QHBoxLayout()
        cat_lbl = QLabel(f"Module: {data['category']}")
        cat_lbl.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 10pt;")
        time_lbl = QLabel(f"📖 {data['read_time']}")
        time_lbl.setStyleSheet("color: #94a3b8; font-weight: 500; font-size: 10pt;")
        meta_row.addWidget(cat_lbl)
        meta_row.addWidget(time_lbl)
        meta_row.addStretch()
        hdr_layout.addLayout(meta_row)
        
        # Objectives Subcard
        obj_box = QFrame()
        obj_box.setStyleSheet("background-color: rgba(6, 182, 212, 0.05); border-left: 3px solid #06b6d4; padding: 10px; margin-top: 10px;")
        obj_lay = QVBoxLayout(obj_box)
        obj_lay.addWidget(QLabel("Learning Objectives:"))
        for obj in data["objectives"]:
            obj_lbl = QLabel(f" • {obj}")
            obj_lbl.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
            obj_lay.addWidget(obj_lbl)
        hdr_layout.addWidget(obj_box)
        
        self.viewer_layout.addWidget(header_card)
        
        # 2. Quick Revision Card
        rev_card = QFrame()
        rev_card.setStyleSheet("background-color: #0f172a; border: 2px solid #ef4444; border-radius: 8px; padding: 15px;")
        rev_lay = QVBoxLayout(rev_card)
        rev_hdr = QLabel("⚡ QUICK REVISION (20-Second Check)")
        rev_hdr.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #1e293b; padding-bottom: 5px;")
        rev_lay.addWidget(rev_hdr)
        
        rev_grid = QGridLayout()
        rev_grid.addWidget(QLabel("📌 Definition:"), 0, 0)
        lbl_def = QLabel(data["revision"]["def"])
        lbl_def.setWordWrap(True)
        lbl_def.setStyleSheet("color: #cbd5e1;")
        rev_grid.addWidget(lbl_def, 0, 1)
        
        rev_grid.addWidget(QLabel("📌 Formula:"), 1, 0)
        lbl_form = QLabel(data["revision"]["formula"])
        lbl_form.setStyleSheet("color: #06b6d4; font-weight: bold;")
        rev_grid.addWidget(lbl_form, 1, 1)
        
        rev_grid.addWidget(QLabel("📌 Components:"), 2, 0)
        rev_grid.addWidget(QLabel(data["revision"]["components"]), 2, 1)
        
        rev_grid.addWidget(QLabel("📌 Applications:"), 3, 0)
        rev_grid.addWidget(QLabel(data["revision"]["apps"]), 3, 1)
        
        rev_lay.addLayout(rev_grid)
        self.viewer_layout.addWidget(rev_card)
        
        # 3. Skills Learned Badges Grid
        skills_card = QFrame()
        skills_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        skills_grid = QGridLayout(skills_card)
        skills_grid.setContentsMargins(10, 10, 10, 10)
        skills_grid.setHorizontalSpacing(20)
        skills_grid.setVerticalSpacing(15)
        
        skills_title = QLabel("🎯 Skills You'll Learn:")
        skills_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 10pt;")
        skills_grid.addWidget(skills_title, 0, 0)
        
        for idx, sk in enumerate(data["skills"]):
            badge = QLabel(f"✔ {sk}")
            badge.setStyleSheet("background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981; border-radius: 4px; padding: 4px 10px; font-size: 9pt; font-weight: bold;")
            skills_grid.addWidget(badge, 0, idx + 1)
            
        self.viewer_layout.addWidget(skills_card)
        
        # 4. Introduction
        intro_lbl = QLabel(data["introduction"])
        intro_lbl.setWordWrap(True)
        intro_lbl.setStyleSheet("color: #cbd5e1; font-size: 11pt; line-height: 1.5; padding: 5px;")
        self.viewer_layout.addWidget(intro_lbl)
        
        # 5. Theory
        theory_card = QFrame()
        theory_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        t_lay = QVBoxLayout(theory_card)
        t_hdr = QLabel("📚 Detailed Theory")
        t_hdr.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f8fafc; border-bottom: 1px solid #1e293b; padding-bottom: 5px;")
        t_lay.addWidget(t_hdr)
        for sec in data["theory_sections"]:
            sec_title = QLabel(f"\n📎 {sec['title']}")
            sec_title.setStyleSheet("font-weight: bold; color: #06b6d4; font-size: 10.5pt;")
            sec_desc = QLabel(sec["content"])
            sec_desc.setWordWrap(True)
            sec_desc.setStyleSheet("color: #cbd5e1; font-size: 10pt; line-height: 1.45;")
            t_lay.addWidget(sec_title)
            t_lay.addWidget(sec_desc)
        self.viewer_layout.addWidget(theory_card)
        
        # 6. Experiment Workflow Flow Steps
        workflow_card = QFrame()
        workflow_card.setStyleSheet("background-color: #0f172a; border: 1px solid #06b6d4; border-radius: 8px; padding: 15px;")
        wf_lay = QVBoxLayout(workflow_card)
        wf_hdr = QLabel("🧪 ElectroVerse Experiment Workflow")
        wf_hdr.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #1e293b; padding-bottom: 5px;")
        wf_lay.addWidget(wf_hdr)
        
        wf_flow = QHBoxLayout()
        steps = ["Read Theory", "Watch Waveforms", "Launch Sim Lab", "Observe Scope", "Tweak Values", "Export Report"]
        for idx, step in enumerate(steps):
            box = QLabel(f"Step {idx+1}\n{step}")
            box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.setStyleSheet("background-color: #1e293b; border: 1px solid #334155; border-radius: 4px; padding: 8px; color: #f8fafc; font-size: 8.5pt; font-weight: bold;")
            wf_flow.addWidget(box)
            if idx < len(steps) - 1:
                arrow = QLabel("➔")
                arrow.setStyleSheet("color: #06b6d4; font-size: 12pt;")
                wf_flow.addWidget(arrow)
        wf_lay.addLayout(wf_flow)
        self.viewer_layout.addWidget(workflow_card)
        
        # 7. Working Principle
        wp_card = QFrame()
        wp_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        wp_lay = QVBoxLayout(wp_card)
        wp_hdr = QLabel("⚙️ Working Principle (Step-by-Step)")
        wp_hdr.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f8fafc; border-bottom: 1px solid #1e293b; padding-bottom: 5px;")
        wp_lay.addWidget(wp_hdr)
        for i, step in enumerate(data["working_steps"]):
            step_lbl = QLabel(f"{i+1}. {step}")
            step_lbl.setWordWrap(True)
            step_lbl.setStyleSheet("color: #cbd5e1; font-size: 10pt; padding-top: 5px;")
            wp_lay.addWidget(step_lbl)
        self.viewer_layout.addWidget(wp_card)
        
        # 8. Mathematical Formula Cards Section
        from src.ui.learning_content import get_lesson_formulas
        formulas_list = get_lesson_formulas(lesson_id)
        
        for fidx, f_data in enumerate(formulas_list):
            formula_box = QFrame()
            formula_box.setStyleSheet("background-color: #090d16; border: 1px solid #1e293b; border-radius: 8px; padding: 15px; margin-bottom: 5px;")
            f_lay = QVBoxLayout(formula_box)
            
            # Formula Name
            f_title = QLabel(f"📖 Formula {fidx+1}: {f_data['name']}")
            f_title.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 11pt;")
            f_lay.addWidget(f_title)
            
            # Equation
            eq_lbl = QLabel(f_data["eq"])
            eq_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            eq_lbl.setStyleSheet("font-size: 16pt; font-weight: bold; color: #10b981; padding: 12px; background-color: #0b0f19; border-radius: 6px; margin: 5px 0px;")
            f_lay.addWidget(eq_lbl)
            
            # Purpose & When to use
            purpose_lbl = QLabel(f"<b>Purpose:</b> {f_data['purpose']}")
            purpose_lbl.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
            purpose_lbl.setWordWrap(True)
            f_lay.addWidget(purpose_lbl)
            
            when_lbl = QLabel(f"<b>When to Use:</b> {f_data['when']}")
            when_lbl.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
            when_lbl.setWordWrap(True)
            f_lay.addWidget(when_lbl)
            
            # Symbols Used Table
            table_html = """
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; border: 1px solid #1e293b; width: 100%; margin-top: 10px;">
                <tr style="background-color: #1e293b; color: #f8fafc;">
                    <th align="left" style="font-weight: bold; padding: 6px; font-size: 9pt;">Symbol</th>
                    <th align="left" style="font-weight: bold; padding: 6px; font-size: 9pt;">Represents</th>
                    <th align="left" style="font-weight: bold; padding: 6px; font-size: 9pt;">SI Unit</th>
                </tr>
            """
            for sym, rep, unit in f_data["symbols"]:
                table_html += f"""
                <tr style="color: #cbd5e1;">
                    <td style="padding: 6px; border: 1px solid #1e293b; font-size: 9pt;"><b>{sym}</b></td>
                    <td style="padding: 6px; border: 1px solid #1e293b; font-size: 9pt;">{rep}</td>
                    <td style="padding: 6px; border: 1px solid #1e293b; color: #06b6d4; font-size: 9pt;">{unit}</td>
                </tr>
                """
            table_html += "</table>"
            
            sym_title = QLabel("Symbols Used:")
            sym_title.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 9.5pt; margin-top: 10px;")
            f_lay.addWidget(sym_title)
            
            table_lbl = QLabel(table_html)
            table_lbl.setStyleSheet("background-color: transparent;")
            f_lay.addWidget(table_lbl)
            
            self.viewer_layout.addWidget(formula_box)
        
        # 9. Circuit Breakdown Breakdown Card
        ckt_card = QFrame()
        ckt_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        ckt_lay = QVBoxLayout(ckt_card)
        ckt_hdr = QLabel("🛠️ Circuit Breakdown")
        ckt_hdr.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f8fafc; border-bottom: 1px solid #1e293b; padding-bottom: 5px;")
        ckt_lay.addWidget(ckt_hdr)
        for comp in data["circuit_components"]:
            row = QHBoxLayout()
            comp_lbl = QLabel(f"• {comp['component']}:  ")
            comp_lbl.setStyleSheet("font-weight: bold; color: #06b6d4;")
            role_lbl = QLabel(comp["role"])
            role_lbl.setStyleSheet("color: #cbd5e1;")
            role_lbl.setWordWrap(True)
            row.addWidget(comp_lbl)
            row.addWidget(role_lbl, 1)
            ckt_lay.addLayout(row)
        self.viewer_layout.addWidget(ckt_card)
        
        # 10. Practical Applications Grid Container (Layout Refined)
        app_lbl = QLabel("🏭 Industry Practical Applications")
        app_lbl.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;")
        self.viewer_layout.addWidget(app_lbl)
        
        apps_container = QFrame()
        apps_container.setStyleSheet("background-color: transparent;")
        app_grid = QGridLayout(apps_container)
        app_grid.setContentsMargins(0, 0, 0, 0)
        app_grid.setHorizontalSpacing(20)
        app_grid.setVerticalSpacing(20)
        
        for idx, app in enumerate(data["apps_cards"]):
            acard = QFrame()
            acard.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
            al = QVBoxLayout(acard)
            al.setSpacing(5)
            at = QLabel(app["field"])
            at.setStyleSheet("font-weight: bold; color: #06b6d4; font-size: 10.5pt;")
            ad = QLabel(app["desc"])
            ad.setWordWrap(True)
            ad.setStyleSheet("color: #cbd5e1; font-size: 9.5pt; line-height: 1.3;")
            al.addWidget(at)
            al.addWidget(ad)
            
            # Form a responsive 2x2 grid
            row = idx // 2
            col = idx % 2
            app_grid.addWidget(acard, row, col)
            
        self.viewer_layout.addWidget(apps_container)
        
        # 11. Advantages & Disadvantages Side-by-Side Grid (Layout Refined)
        adv_dis_container = QFrame()
        adv_dis_container.setStyleSheet("background-color: transparent;")
        adv_dis_grid = QGridLayout(adv_dis_container)
        adv_dis_grid.setContentsMargins(0, 0, 0, 0)
        adv_dis_grid.setHorizontalSpacing(20)
        adv_dis_grid.setVerticalSpacing(20)
        
        adv_card = QFrame()
        adv_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        adv_lay = QVBoxLayout(adv_card)
        adv_hdr = QLabel("🟢 Advantages:")
        adv_hdr.setStyleSheet("font-weight: bold; color: #10b981; font-size: 10.5pt; border-bottom: 1px solid #1e293b; padding-bottom: 5px;")
        adv_lay.addWidget(adv_hdr)
        for adv in data["advantages"]:
            adv_lbl = QLabel(f" • {adv}")
            adv_lbl.setWordWrap(True)
            adv_lbl.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
            adv_lay.addWidget(adv_lbl)
        
        dis_card = QFrame()
        dis_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        dis_lay = QVBoxLayout(dis_card)
        dis_hdr = QLabel("🔴 Disadvantages:")
        dis_hdr.setStyleSheet("font-weight: bold; color: #ef4444; font-size: 10.5pt; border-bottom: 1px solid #1e293b; padding-bottom: 5px;")
        dis_lay.addWidget(dis_hdr)
        for dis in data["disadvantages"]:
            dis_lbl = QLabel(f" • {dis}")
            dis_lbl.setWordWrap(True)
            dis_lbl.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
            dis_lay.addWidget(dis_lbl)
            
        adv_dis_grid.addWidget(adv_card, 0, 0)
        adv_dis_grid.addWidget(dis_card, 0, 1)
        self.viewer_layout.addWidget(adv_dis_container)
        
        # 12. Remember & Did You Know Shunt Alerts Grid (Layout Refined)
        quick_facts_container = QFrame()
        quick_facts_container.setStyleSheet("background-color: transparent;")
        qf_grid = QGridLayout(quick_facts_container)
        qf_grid.setContentsMargins(0, 0, 0, 0)
        qf_grid.setHorizontalSpacing(20)
        qf_grid.setVerticalSpacing(20)
        
        remember_box = QFrame()
        remember_box.setStyleSheet("background-color: rgba(239, 68, 68, 0.05); border-left: 3px solid #ef4444; border-radius: 4px; padding: 12px;")
        rlay = QVBoxLayout(remember_box)
        r_title = QLabel("⚠️ REMEMBER")
        r_title.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 10pt;")
        rlay.addWidget(r_title)
        rc_lbl = QLabel(data["remember"])
        rc_lbl.setWordWrap(True)
        rc_lbl.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
        rlay.addWidget(rc_lbl)
        
        dyk_box = QFrame()
        dyk_box.setStyleSheet("background-color: rgba(245, 158, 11, 0.05); border-left: 3px solid #f59e0b; border-radius: 4px; padding: 12px;")
        dlay = QVBoxLayout(dyk_box)
        d_title = QLabel("💡 DID YOU KNOW?")
        d_title.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 10pt;")
        dlay.addWidget(d_title)
        dc_lbl = QLabel(data["did_you_know"])
        dc_lbl.setWordWrap(True)
        dc_lbl.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
        dlay.addWidget(dc_lbl)
        
        qf_grid.addWidget(remember_box, 0, 0)
        qf_grid.addWidget(dyk_box, 0, 1)
        self.viewer_layout.addWidget(quick_facts_container)
        
        # 13. Common Mistakes
        mistake_card = QFrame()
        mistake_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        m_lay = QVBoxLayout(mistake_card)
        m_lay.addWidget(QLabel("⚠️ Common Student Mistakes:"))
        for mist in data["mistakes"]:
            ml = QLabel(f" • {mist}")
            ml.setWordWrap(True)
            ml.setStyleSheet("color: #f87171; font-size: 9.5pt;")
            m_lay.addWidget(ml)
        self.viewer_layout.addWidget(mistake_card)
        
        # 14. Real World Example & Tips
        extra_card = QFrame()
        extra_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        ex_lay = QVBoxLayout(extra_card)
        
        ex_title = QLabel("🏭 Real World Industrial Example")
        ex_title.setStyleSheet("font-weight: bold; color: #f8fafc;")
        ex_text = QLabel(data["real_world"])
        ex_text.setWordWrap(True)
        ex_text.setStyleSheet("color: #cbd5e1; margin-top: 5px;")
        
        tip_title = QLabel("\n💡 Practical Engineering Tips")
        tip_title.setStyleSheet("font-weight: bold; color: #06b6d4;")
        tip_text = QLabel(data["engineering_tips"])
        tip_text.setWordWrap(True)
        tip_text.setStyleSheet("color: #cbd5e1; margin-top: 5px;")
        
        ex_lay.addWidget(ex_title)
        ex_lay.addWidget(ex_text)
        ex_lay.addWidget(tip_title)
        ex_lay.addWidget(tip_text)
        self.viewer_layout.addWidget(extra_card)
        
        # 15. Expandable Interview Questions Accordion
        iq_lbl = QLabel("💬 Job Interview Preparation Q&A")
        iq_lbl.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;")
        self.viewer_layout.addWidget(iq_lbl)
        
        for idx, item in enumerate(data["interview"]):
            acc = QFrame()
            acc.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px;")
            aclay = QVBoxLayout(acc)
            
            btn_q = QPushButton(f"Q{idx+1}: {item['question']}")
            btn_q.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_q.setStyleSheet("QPushButton { border: none; text-align: left; color: #06b6d4; font-weight: bold; font-size: 9.5pt; padding: 5px; }")
            
            ans_lbl = QLabel(item["answer"])
            ans_lbl.setWordWrap(True)
            ans_lbl.setStyleSheet("color: #cbd5e1; padding: 8px; background-color: #0b0f19; border-radius: 4px;")
            ans_lbl.setVisible(False)
            
            btn_q.clicked.connect(lambda checked, lbl=ans_lbl: lbl.setVisible(not lbl.isVisible()))
            
            aclay.addWidget(btn_q)
            aclay.addWidget(ans_lbl)
            self.viewer_layout.addWidget(acc)
            
        # 16. Summary
        sum_card = QFrame()
        sum_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        sum_lay = QVBoxLayout(sum_card)
        sum_lay.addWidget(QLabel("📝 Lesson Summary Key Takeaways:"))
        for s in data["summary"]:
            sum_lay.addWidget(QLabel(f" • {s}"))
        self.viewer_layout.addWidget(sum_card)
        
        # 17. Related Resources & Cross-Lab Navigation Section
        resources = LESSON_RESOURCES.get(lesson_id, [])
        if resources:
            res_box = QFrame()
            res_box.setStyleSheet("background-color: rgba(6, 182, 212, 0.08); border: 1px solid #06b6d4; border-radius: 8px; padding: 15px;")
            res_lay = QVBoxLayout(res_box)
            
            res_title = QLabel("⚡ Related Resources & Cross-Lab Navigation")
            res_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; border-bottom: 1px solid rgba(6, 182, 212, 0.2); padding-bottom: 5px;")
            res_lay.addWidget(res_title)
            
            res_desc = QLabel("Navigate to corresponding simulation labs, detailed component specifications, or toolkit calculators:")
            res_desc.setStyleSheet("color: #cbd5e1; font-size: 9.5pt; margin-top: 5px;")
            res_lay.addWidget(res_desc)
            
            # Grid of resource links
            buttons_container = QWidget()
            buttons_grid = QGridLayout(buttons_container)
            buttons_grid.setContentsMargins(0, 5, 0, 0)
            buttons_grid.setHorizontalSpacing(15)
            buttons_grid.setVerticalSpacing(10)
            
            for ridx, res in enumerate(resources):
                r_type = res["type"]
                label = res["label"]
                
                btn = QPushButton(label)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Pick correct style
                if r_type == "library":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1e293b;
                            color: #f8fafc;
                            border: 1px solid #334155;
                            border-radius: 6px;
                            padding: 8px 12px;
                            font-weight: bold;
                            font-size: 9.5pt;
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #334155;
                            border-color: #06b6d4;
                        }
                    """)
                    btn.clicked.connect(lambda checked=False, r=res: self.launch_related_resource("library", r["target"]))
                elif r_type == "toolkit":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1e293b;
                            color: #f8fafc;
                            border: 1px solid #334155;
                            border-radius: 6px;
                            padding: 8px 12px;
                            font-weight: bold;
                            font-size: 9.5pt;
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #334155;
                            border-color: #ef4444;
                        }
                    """)
                    btn.clicked.connect(lambda checked=False, r=res: self.launch_related_resource("toolkit", r["target"]))
                elif r_type == "simulation":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #06b6d4;
                            color: #ffffff;
                            border-radius: 6px;
                            padding: 8px 12px;
                            font-weight: bold;
                            font-size: 9.5pt;
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #0891b2;
                        }
                    """)
                    btn.clicked.connect(lambda checked=False, r=res: self.launch_related_resource("simulation", r["target"]))
                
                row = ridx // 2
                col = ridx % 2
                buttons_grid.addWidget(btn, row, col)
                
            res_lay.addWidget(buttons_container)
            self.viewer_layout.addWidget(res_box)
        
        # 18. Interactive Mini Quiz (5 MCQs with scoreboard/grading)
        self.quiz_card = QFrame()
        self.quiz_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 20px;")
        self.quiz_lay = QVBoxLayout(self.quiz_card)
        
        quiz_hdr = QLabel("📝 Knowledge Check Quiz")
        quiz_hdr.setStyleSheet("font-size: 13pt; font-weight: bold; color: #f8fafc; border-bottom: 1px solid #1e293b; padding-bottom: 8px;")
        self.quiz_lay.addWidget(quiz_hdr)
        
        self.radio_groups = []
        for qidx, q in enumerate(data["quiz"]):
            qbox = QWidget()
            qlay = QVBoxLayout(qbox)
            qlay.addWidget(QLabel(f"\nQ{qidx+1}. {q['question']}"))
            
            btn_group = QButtonGroup(self)
            self.radio_groups.append(btn_group)
            
            for oidx, opt in enumerate(q["options"]):
                rad = QRadioButton(opt)
                rad.setStyleSheet("color: #cbd5e1; font-size: 9.5pt;")
                btn_group.addButton(rad, oidx)
                qlay.addWidget(rad)
                
            self.quiz_lay.addWidget(qbox)
            
        # Submit Quiz Button
        self.submit_btn = QPushButton("Submit Quiz Answers")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px;
                font-size: 10pt;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.submit_btn.clicked.connect(lambda: self.evaluate_quiz(data["quiz"]))
        self.quiz_lay.addWidget(self.submit_btn)
        
        self.viewer_layout.addWidget(self.quiz_card)
        
        # 19. Recommended Next Lesson Roadmap & Navigation Footer
        roadmap_card = QFrame()
        roadmap_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        rm_lay = QVBoxLayout(roadmap_card)
        
        rm_lbl = QLabel("What should I learn next?")
        rm_lbl.setStyleSheet("font-weight: bold; color: #94a3b8; font-size: 9.5pt;")
        rm_lay.addWidget(rm_lbl)
        
        if data["next_id"]:
            next_data = get_lesson_data(data["next_id"])
            rm_lbl_next = QLabel(f"Recommended Next: {next_data['name']}")
            rm_lbl_next.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-top: 5px;")
            rm_lay.addWidget(rm_lbl_next)
            
            start_btn = QPushButton("Start Next Lesson →")
            start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #06b6d4;
                    color: #ffffff;
                    font-weight: bold;
                    border-radius: 4px;
                    padding: 6px 12px;
                    margin-top: 8px;
                }
                QPushButton:hover {
                    background-color: #0891b2;
                }
            """)
            start_btn.clicked.connect(lambda: self.load_lesson(data["next_id"]))
            rm_lay.addWidget(start_btn)
        else:
            rm_lay.addWidget(QLabel("🎉 Congratulations! You have reached the end of the course."))
            
        self.viewer_layout.addWidget(roadmap_card)
        
        # Bottom Navigation Row
        nav_row = QHBoxLayout()
        if data["prev_id"]:
            prev_btn = QPushButton("← Previous Lesson")
            prev_btn.setStyleSheet("QPushButton { background-color: #1e293b; border: 1px solid #334155; border-radius: 4px; padding: 8px; color: #f8fafc; } QPushButton:hover { background-color: #334155; }")
            prev_btn.clicked.connect(lambda: self.load_lesson(data["prev_id"]))
            nav_row.addWidget(prev_btn)
            
        nav_row.addStretch()
        
        catalog_btn = QPushButton("Back to Topics")
        catalog_btn.setStyleSheet("QPushButton { background-color: #1e293b; border: 1px solid #334155; border-radius: 4px; padding: 8px; color: #cbd5e1; } QPushButton:hover { background-color: #334155; }")
        catalog_btn.clicked.connect(lambda: self.right_stack.setCurrentIndex(0))
        nav_row.addWidget(catalog_btn)
        
        nav_row.addStretch()
        
        if data["next_id"]:
            next_btn = QPushButton("Next Lesson →")
            next_btn.setStyleSheet("QPushButton { background-color: #1e293b; border: 1px solid #334155; border-radius: 4px; padding: 8px; color: #f8fafc; } QPushButton:hover { background-color: #334155; }")
            next_btn.clicked.connect(lambda: self.load_lesson(data["next_id"]))
            nav_row.addWidget(next_btn)
            
        self.viewer_layout.addLayout(nav_row)
        
        # Add a stretch spacer at the end of the scroll area's main layout
        # to ensure that the layout behaves as a textbook page and doesn't squish elements
        self.viewer_layout.addStretch(1)

    # -------------------------------------------------------------
    # Cross-Lab Integration Link
    # -------------------------------------------------------------
    def launch_related_resource(self, res_type: str, target):
        main_win = self.window()
        if not main_win or not hasattr(main_win, "switch_view"):
            return
            
        if res_type == "library":
            # Switch to Component Library (Index 1)
            main_win.switch_view(1)
            lib_view = main_win.views[1]
            if lib_view and hasattr(lib_view, "tree_widget"):
                root = lib_view.tree_widget.invisibleRootItem()
                matched = False
                for i in range(root.childCount()):
                    cat_item = root.child(i)
                    for j in range(cat_item.childCount()):
                        child = cat_item.child(j)
                        comp_id = child.data(0, Qt.ItemDataRole.UserRole)
                        if comp_id == target:
                            lib_view.tree_widget.setCurrentItem(child)
                            lib_view.on_item_clicked(child)
                            matched = True
                            break
                    if matched:
                        break
        elif res_type == "toolkit":
            # Switch to Engineering Toolkit (Index 3)
            main_win.switch_view(3)
            toolkit_view = main_win.views[3]
            if toolkit_view and hasattr(toolkit_view, "list_widget"):
                toolkit_view.list_widget.setCurrentRow(target)
        elif res_type == "simulation":
            # Switch to Simulation Lab (Index 4)
            main_win.switch_view(4)
            sim_view = main_win.views[4]
            if sim_view and hasattr(sim_view, "list_widget"):
                sim_view.list_widget.setCurrentRow(target)

    # -------------------------------------------------------------
    # Interactive Quiz Score Evaluator
    # -------------------------------------------------------------
    def evaluate_quiz(self, quiz_data):
        score = 0
        feedback_report = []
        
        for qidx, q in enumerate(quiz_data):
            group = self.radio_groups[qidx]
            selected_id = group.checkedId()
            
            is_correct = (selected_id == q["answer_idx"])
            if is_correct:
                score += 1
                
            # Create a nice layout box for the explanation card
            status_text = "🟢 Correct" if is_correct else "🔴 Incorrect"
            status_color = "#10b981" if is_correct else "#ef4444"
            
            card = QFrame()
            card.setStyleSheet(f"background-color: #0b0f19; border: 1px solid {status_color}; border-radius: 6px; padding: 10px; margin-top: 5px;")
            l = QVBoxLayout(card)
            
            header = QLabel(f"Question {qidx+1}: {status_text}")
            header.setStyleSheet(f"color: {status_color}; font-weight: bold;")
            l.addWidget(header)
            
            q_lbl = QLabel(q["question"])
            q_lbl.setWordWrap(True)
            l.addWidget(q_lbl)
            
            correct_opt = q["options"][q["answer_idx"]]
            ans_lbl = QLabel(f"Correct Answer: {correct_opt}")
            ans_lbl.setStyleSheet("color: #10b981; font-weight: bold;")
            l.addWidget(ans_lbl)
            
            exp_lbl = QLabel(f"Explanation: {q['explanation']}")
            exp_lbl.setWordWrap(True)
            exp_lbl.setStyleSheet("color: #94a3b8; font-style: italic;")
            l.addWidget(exp_lbl)
            
            feedback_report.append(card)

        # Clear Submit button
        self.submit_btn.deleteLater()
        
        # Display Score Card
        score_card = QFrame()
        score_card.setStyleSheet("background-color: #0b0f19; border: 2px solid #f59e0b; border-radius: 8px; padding: 15px; margin-top: 15px;")
        s_lay = QVBoxLayout(score_card)
        
        grade_text = "Excellent" if score >= 4 else "Pass" if score >= 3 else "Needs Review"
        grade_color = "#10b981" if score >= 3 else "#ef4444"
        pct = int((score / 5.0) * 100)
        
        score_title = QLabel(f"⭐⭐ Your Score: {score} / 5")
        score_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #f59e0b;")
        s_lay.addWidget(score_title)
        
        grade_lbl = QLabel(f"{grade_text} ({pct}%)")
        grade_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grade_lbl.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {grade_color};")
        s_lay.addWidget(grade_lbl)
        
        self.quiz_lay.addWidget(score_card)
        
        # Add feedback reports
        for card in feedback_report:
            self.quiz_lay.addWidget(card)
