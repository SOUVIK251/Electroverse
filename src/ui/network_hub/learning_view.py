import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTreeWidget, QTreeWidgetItem, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta

class NetworkLearningView(QWidget):
    """Interactive Engineering Textbook Reader for Network Theory with Topic-Aware Visibility."""

    open_problem_solving_signal = Signal(str)
    launch_simulation_signal = Signal(str)
    topic_selected_signal = Signal(dict) # Emits full topic metadata dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_dir = os.path.join("src", "data", "network_theory")
        self.curriculum = self.load_json("curriculum.json")
        self.flat_topics = []
        self.current_idx = 0
        self.derivation_step_index = 0
        self.current_topic_data = None

        self.init_ui()

    def load_json(self, rel_path):
        p = os.path.join(self.data_dir, rel_path)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(4, 4, 4, 4)
        main_lay.setSpacing(6)

        # 1. Course Roadmap Header Card
        roadmap_card = QFrame()
        roadmap_card.setObjectName("card-panel")
        roadmap_card.setFixedHeight(50)
        roadmap_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; }")
        rm_lay = QHBoxLayout(roadmap_card)
        rm_lay.setContentsMargins(10, 4, 10, 4)

        rm_lbl = QLabel("🗺️ Course Roadmap:")
        rm_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 9pt;")
        
        flow_lbl = QLabel("● Fundamentals  ➔  ● Circuit Laws  ➔  ● Analysis  ➔  ● Theorems  ➔  ● AC Networks  ➔  ● Filters")
        flow_lbl.setStyleSheet("color: #94A3B8; font-size: 8.5pt; font-weight: 500;")

        prog_lbl = QLabel("Overall Progress: 48%")
        prog_lbl.setStyleSheet("color: #10B981; font-weight: bold; font-size: 9pt;")

        rm_lay.addWidget(rm_lbl)
        rm_lay.addWidget(flow_lbl, 1)
        rm_lay.addWidget(prog_lbl)

        main_lay.addWidget(roadmap_card)

        # 2. Main Splitter (Left 280px Tree | Right Reader)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(4)

        # Left 25% Tree
        left_container = QFrame()
        left_container.setObjectName("card-panel")
        left_container.setStyleSheet("QFrame#card-panel { background-color: #111827; border: 1px solid #26334D; border-radius: 8px; padding: 8px; }")
        l_lay = QVBoxLayout(left_container)

        tree_header = QLabel("🗺️ Network Theory Curriculum")
        tree_header.setStyleSheet("font-size: 10.5pt; font-weight: bold; color: #06b6d4; padding-bottom: 4px;")
        l_lay.addWidget(tree_header)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("QTreeWidget { background-color: transparent; border: none; color: #C9D1E3; } QTreeWidget::item { padding: 5px; } QTreeWidget::item:selected { background-color: #2563EB; color: #FFF; font-weight: bold; }")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        l_lay.addWidget(self.tree)

        self.populate_tree()
        self.splitter.addWidget(left_container)

        # Right 75% Scrollable Lesson Reader
        self.reader_scroll = QScrollArea()
        self.reader_scroll.setWidgetResizable(True)
        self.reader_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.reader_container = QWidget()
        self.reader_lay = QVBoxLayout(self.reader_container)
        self.reader_lay.setContentsMargins(15, 15, 15, 15)
        self.reader_lay.setSpacing(15)

        self.reader_scroll.setWidget(self.reader_container)
        self.splitter.addWidget(self.reader_scroll)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([280, 840])

        main_lay.addWidget(self.splitter, 1)

        self.load_default_topic()

    def populate_tree(self):
        self.tree.clear()
        self.flat_topics.clear()
        modules = self.curriculum.get("modules", [])

        for mod in modules:
            m_item = QTreeWidgetItem(self.tree)
            m_item.setText(0, mod.get("title", ""))
            m_item.setIcon(0, qta.icon(mod.get("icon", "fa5s.folder"), color="#06b6d4"))
            m_item.setExpanded(True)

            for top in mod.get("topics", []):
                t_item = QTreeWidgetItem(m_item)
                t_item.setText(0, top.get("title", ""))
                t_item.setIcon(0, qta.icon("fa5s.file-alt", color="#94a3b8"))
                
                entry = {
                    "file": top.get("file"),
                    "id": top.get("id"),
                    "title": top.get("title"),
                    "module": mod.get("title"),
                    "flat_index": len(self.flat_topics)
                }
                t_item.setData(0, Qt.ItemDataRole.UserRole, entry)
                self.flat_topics.append(entry)

    def load_default_topic(self):
        if self.flat_topics:
            self.load_topic_by_index(0)

    def on_tree_item_clicked(self, item, col):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and isinstance(data, dict):
            self.load_topic_by_index(data["flat_index"])

    def load_topic_by_index(self, idx):
        if idx < 0 or idx >= len(self.flat_topics): return
        self.current_idx = idx
        entry = self.flat_topics[idx]

        full_data = self.load_json(os.path.join("topics", entry["file"]))
        topic = full_data.get("topics", {}).get(entry["id"], {})
        self.current_topic_data = topic
        self.derivation_step_index = 0

        # Emit topic metadata signal for dynamic tab visibility
        self.topic_selected_signal.emit(topic)

        self.render_reader(topic, entry["title"])

    def render_reader(self, topic, title_str):
        while self.reader_lay.count():
            item = self.reader_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Header Card
        hdr_card = QFrame()
        hdr_card.setObjectName("card-panel")
        hdr_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-top: 4px solid #06B6D4; border-radius: 10px; padding: 15px; }")
        h_lay = QVBoxLayout(hdr_card)

        top_r = QHBoxLayout()
        cat_lbl = QLabel(f"CATEGORY: {topic.get('category', 'Network Theory').upper()}")
        cat_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 9pt;")
        
        diff_str = topic.get("difficulty", "Intermediate")
        diff_badge = QLabel(f"🟡 {diff_str}")
        diff_badge.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 9pt;")

        top_r.addWidget(cat_lbl)
        top_r.addStretch()
        top_r.addWidget(diff_badge)
        h_lay.addLayout(top_r)

        t_lbl = QLabel(title_str)
        t_lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: #FFF; padding-top: 4px;")
        h_lay.addWidget(t_lbl)

        sum_lbl = QLabel(topic.get("summary", ""))
        sum_lbl.setStyleSheet("color: #C9D1E3; font-size: 10pt;")
        sum_lbl.setWordWrap(True)
        h_lay.addWidget(sum_lbl)

        self.reader_lay.addWidget(hdr_card)

        # 2. Memory Trick Card
        if topic.get("memory_trick"):
            m_card = QFrame()
            m_card.setStyleSheet("background-color: #1F190D; border: 1px solid #F59E0B; border-radius: 8px; padding: 12px;")
            m_lay = QVBoxLayout(m_card)
            m_lbl = QLabel(topic["memory_trick"])
            m_lbl.setStyleSheet("color: #FBBF24; font-size: 10pt; font-weight: 500;")
            m_lbl.setWordWrap(True)
            m_lay.addWidget(m_lbl)
            self.reader_lay.addWidget(m_card)

        # 3. Theory & Concepts
        if topic.get("theory"):
            t_card = QFrame()
            t_card.setObjectName("card-panel")
            t_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
            t_lay = QVBoxLayout(t_card)
            th_lbl = QLabel("📖 Theory & Working Principle")
            th_lbl.setStyleSheet("font-size: 12pt; font-weight: bold; color: #06B6D4; padding-bottom: 6px; border-bottom: 1px solid #26334D;")
            content = QLabel(topic["theory"])
            content.setStyleSheet("color: #E2E8F0; font-size: 10pt; line-height: 1.5;")
            content.setWordWrap(True)
            t_lay.addWidget(th_lbl)
            t_lay.addWidget(content)
            self.reader_lay.addWidget(t_card)

        # 4. Interactive Step-by-Step Derivation Revealer Mode
        if topic.get("derivation_steps"):
            d_card = QFrame()
            d_card.setObjectName("card-panel")
            d_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
            d_lay = QVBoxLayout(d_card)

            d_hdr = QHBoxLayout()
            d_title = QLabel("📐 Step-by-Step Interactive Derivation")
            d_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #38BDF8;")
            
            step_next_btn = QPushButton("Next Step ➔")
            step_next_btn.setStyleSheet("background-color: #2563EB; color: #FFF; font-weight: bold; padding: 4px 10px; border-radius: 4px;")
            
            d_hdr.addWidget(d_title)
            d_hdr.addStretch()
            d_hdr.addWidget(step_next_btn)
            d_lay.addLayout(d_hdr)

            steps_container = QVBoxLayout()
            steps = topic["derivation_steps"]

            def update_steps():
                while steps_container.count():
                    item = steps_container.takeAt(0)
                    if item.widget(): item.widget().deleteLater()

                for s_idx in range(self.derivation_step_index + 1):
                    if s_idx < len(steps):
                        slbl = QLabel(steps[s_idx])
                        slbl.setStyleSheet("color: #34D399; font-size: 10pt; background-color: #09121E; padding: 8px; border-radius: 6px; margin-top: 4px;")
                        slbl.setWordWrap(True)
                        steps_container.addWidget(slbl)

            def on_next_step():
                if self.derivation_step_index < len(steps) - 1:
                    self.derivation_step_index += 1
                    update_steps()

            step_next_btn.clicked.connect(on_next_step)
            d_lay.addLayout(steps_container)
            update_steps()

            self.reader_lay.addWidget(d_card)

        # 5. Formulas Card
        if topic.get("important_formulas"):
            f_card = QFrame()
            f_card.setStyleSheet("background-color: #0F172A; border: 1px solid #06B6D4; border-radius: 8px; padding: 12px;")
            f_lay = QVBoxLayout(f_card)
            f_title = QLabel("⚡ Key Governing Equations & Formulas")
            f_title.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 11pt;")
            f_lay.addWidget(f_title)
            for form in topic["important_formulas"]:
                flbl = QLabel(f"• {form}")
                flbl.setStyleSheet("color: #F8FAFC; font-size: 10.5pt; font-weight: bold; font-family: Consolas, monospace;")
                f_lay.addWidget(flbl)
            self.reader_lay.addWidget(f_card)

        # 6. Real-World Career Applications Card
        if topic.get("career_applications"):
            c_card = QFrame()
            c_card.setStyleSheet("background-color: #111C2E; border: 1px solid #2563EB; border-radius: 8px; padding: 12px;")
            c_lay = QVBoxLayout(c_card)
            c_hdr = QLabel("💼 Real-World Career Applications")
            c_hdr.setStyleSheet("color: #60A5FA; font-weight: bold; font-size: 11pt;")
            c_lay.addWidget(c_hdr)
            for app in topic["career_applications"]:
                albl = QLabel(f"• {app}")
                albl.setStyleSheet("color: #93C5FD; font-size: 9.5pt;")
                c_lay.addWidget(albl)
            self.reader_lay.addWidget(c_card)

        # 7. TOPIC-AWARE ACTION BUTTONS (Problem Solving & Simulation)
        has_ps = topic.get("has_problem_solving", False)
        has_sim = topic.get("has_simulation", False)

        if has_ps or has_sim:
            act_card = QFrame()
            act_card.setStyleSheet("background-color: #0B1E2D; border: 2px solid #06B6D4; border-radius: 10px; padding: 15px;")
            a_lay = QHBoxLayout(act_card)

            if has_ps:
                ps_btn = QPushButton("🧠 Open Problem Solving Lab")
                ps_btn.setStyleSheet("background-color: #F59E0B; color: #FFF; font-weight: bold; font-size: 10pt; padding: 10px 16px; border-radius: 6px;")
                ps_btn.clicked.connect(lambda: self.open_problem_solving_signal.emit(title_str))
                a_lay.addWidget(ps_btn)

            if has_sim:
                sim_btn = QPushButton("🚀 Launch Interactive Simulation")
                sim_btn.setStyleSheet("background-color: #06B6D4; color: #FFF; font-weight: bold; font-size: 10pt; padding: 10px 16px; border-radius: 6px;")
                sim_btn.clicked.connect(lambda: self.launch_simulation_signal.emit(title_str))
                a_lay.addWidget(sim_btn)

            self.reader_lay.addWidget(act_card)

        self.reader_scroll.verticalScrollBar().setValue(0)
