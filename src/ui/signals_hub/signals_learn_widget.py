import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTreeWidget, QTreeWidgetItem, QScrollArea, QLineEdit, QSplitter,
    QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta

from src.core.logger import log

class SignalsLearnWidget(QWidget):
    """Interactive Engineering Textbook Reader for Signals & Systems.
    
    Features:
    - Compact Top Header (340px Search, Filter, Bookmarks & Curriculum Progress)
    - Left 25% Curriculum Tree Navigator (10 Modules & 40+ Topics)
    - Right 75% Scrollable Lesson Reader
    - Unified Bidirectional Lesson Navigator (Previous ▲ & Next ▼ buttons)
    - "🚀 Launch Interactive Simulation" Card connecting directly to Tab 2
    """
    
    # Signal emitted to launch a specific simulation mode in Tab 2
    launch_simulation_requested = Signal(int, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_dir = os.path.join("src", "data", "signals")
        self.curriculum = self.load_json("curriculum.json")
        
        # Flatten topics list for bidirectional navigation engine
        self.flat_topics = [] # List of dicts: {"file": str, "id": str, "title": str, "module_idx": int}
        self.current_flat_idx = 0
        self.tree_item_map = {} # (file, id) -> QTreeWidgetItem

        self.init_ui()

    def load_json(self, rel_path):
        p = os.path.join(self.data_dir, rel_path)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        # 1. Compact Search Bar & Header Toolbar (Height: 46px)
        header_frame = QFrame()
        header_frame.setObjectName("card-panel")
        header_frame.setFixedHeight(48)
        header_frame.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; }")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(10, 4, 10, 4)
        h_layout.setSpacing(12)

        # Compact Search Box (340px wide)
        search_box = QFrame()
        search_box.setFixedWidth(340)
        search_box.setStyleSheet("background-color: #0F172A; border: 1px solid #26334D; border-radius: 6px;")
        sb_lay = QHBoxLayout(search_box)
        sb_lay.setContentsMargins(8, 2, 8, 2)
        
        s_icon = QLabel()
        s_icon.setPixmap(qta.icon("fa5s.search", color="#06b6d4").pixmap(14, 14))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search lessons, theory, derivations...")
        self.search_input.setStyleSheet("QLineEdit { background: transparent; border: none; color: #FFFFFF; font-size: 9.5pt; }")
        self.search_input.textChanged.connect(self.filter_topics)

        sb_lay.addWidget(s_icon)
        sb_lay.addWidget(self.search_input)
        h_layout.addWidget(search_box)

        # Category Filter Dropdown
        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["All Categories", "Fundamentals", "Operations", "Systems", "Convolution", "Transforms", "Sampling", "Applications"])
        self.cat_filter.setFixedWidth(140)
        self.cat_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                border: 1px solid #26334D;
                color: #CBD5E1;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 9pt;
            }
        """)
        self.cat_filter.currentIndexChanged.connect(self.on_filter_changed)
        h_layout.addWidget(self.cat_filter)

        h_layout.addStretch()

        # Curriculum Progress Indicator
        prog_lbl = QLabel("Course Progress:")
        prog_lbl.setStyleSheet("color: #94A3B8; font-size: 9pt; font-weight: bold;")
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(12)
        self.prog_bar.setFixedWidth(130)
        self.prog_bar.setFixedHeight(12)
        self.prog_bar.setTextVisible(False)
        self.prog_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0F172A;
                border: 1px solid #26334D;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background-color: #06B6D4;
                border-radius: 5px;
            }
        """)
        h_layout.addWidget(prog_lbl)
        h_layout.addWidget(self.prog_bar)

        main_layout.addWidget(header_frame)

        # 2. Main 25%/75% Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #1e293b; } QSplitter::handle:hover { background-color: #06b6d4; }")

        # Left 25% Curriculum Tree Navigator
        left_container = QFrame()
        left_container.setObjectName("card-panel")
        left_container.setStyleSheet("QFrame#card-panel { background-color: #111827; border: 1px solid #26334D; border-radius: 8px; }")
        l_layout = QVBoxLayout(left_container)
        l_layout.setContentsMargins(8, 8, 8, 8)

        tree_header = QLabel("🗺️ Course Curriculum")
        tree_header.setStyleSheet("font-size: 11pt; font-weight: bold; color: #06b6d4; padding-bottom: 4px;")
        l_layout.addWidget(tree_header)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                color: #C9D1E3;
            }
            QTreeWidget::item {
                padding: 5px 4px;
                border-radius: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #1E293B;
                color: #FFFFFF;
            }
            QTreeWidget::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        l_layout.addWidget(self.tree)
        self.populate_curriculum_tree()

        self.splitter.addWidget(left_container)

        # Right 75% Scrollable Lesson Reader
        self.reader_scroll = QScrollArea()
        self.reader_scroll.setWidgetResizable(True)
        self.reader_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.reader_container = QWidget()
        self.reader_layout = QVBoxLayout(self.reader_container)
        self.reader_layout.setContentsMargins(15, 15, 15, 15)
        self.reader_layout.setSpacing(15)

        self.reader_scroll.setWidget(self.reader_container)
        self.splitter.addWidget(self.reader_scroll)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([280, 840])

        main_layout.addWidget(self.splitter)

        # Default load first topic
        self.load_default_topic()

    def populate_curriculum_tree(self):
        self.tree.clear()
        self.flat_topics.clear()
        self.tree_item_map.clear()

        modules = self.curriculum.get("modules", [])
        for m_idx, mod in enumerate(modules):
            mod_item = QTreeWidgetItem(self.tree)
            mod_item.setText(0, mod.get("title", ""))
            mod_item.setIcon(0, qta.icon(mod.get("icon", "fa5s.folder"), color="#06b6d4"))
            mod_item.setExpanded(True)
            
            for top in mod.get("topics", []):
                file_name = top.get("file")
                topic_id = top.get("id")
                title = top.get("title", "")

                top_item = QTreeWidgetItem(mod_item)
                top_item.setText(0, title)
                top_item.setIcon(0, qta.icon("fa5s.file-alt", color="#94a3b8"))
                
                flat_entry = {
                    "file": file_name,
                    "id": topic_id,
                    "title": title,
                    "module_idx": m_idx,
                    "flat_index": len(self.flat_topics)
                }
                top_item.setData(0, Qt.ItemDataRole.UserRole, flat_entry)

                self.flat_topics.append(flat_entry)
                self.tree_item_map[(file_name, topic_id)] = top_item

    def load_default_topic(self):
        if self.flat_topics:
            self.load_topic_by_index(0)

    def on_tree_item_clicked(self, item, col):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and isinstance(data, dict):
            f_idx = data.get("flat_index", 0)
            self.load_topic_by_index(f_idx)

    def navigate_prev_topic(self):
        if self.current_flat_idx > 0:
            self.load_topic_by_index(self.current_flat_idx - 1)

    def navigate_next_topic(self):
        if self.current_flat_idx < len(self.flat_topics) - 1:
            self.load_topic_by_index(self.current_flat_idx + 1)

    def load_topic_by_index(self, flat_idx):
        if not self.flat_topics or flat_idx < 0 or flat_idx >= len(self.flat_topics):
            return

        self.current_flat_idx = flat_idx
        entry = self.flat_topics[flat_idx]
        file_name = entry["file"]
        topic_id = entry["id"]

        # Synchronize Tree Selection
        tree_item = self.tree_item_map.get((file_name, topic_id))
        if tree_item:
            self.tree.setCurrentItem(tree_item)

        # Update Progress Bar percentage
        pct = int(((flat_idx + 1) / len(self.flat_topics)) * 100)
        self.prog_bar.setValue(pct)

        # Render Topic Content
        self.render_topic_content(file_name, topic_id, entry["module_idx"])

    def render_topic_content(self, file_name, topic_id, module_idx):
        full_data = self.load_json(os.path.join("topics", file_name))
        topic = full_data.get("topics", {}).get(topic_id, {})
        if not topic and "topics" in full_data:
            first_key = list(full_data["topics"].keys())[0]
            topic = full_data["topics"][first_key]

        # Clear existing reader layout
        while self.reader_layout.count():
            item = self.reader_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Header Card with Prev/Next Navigation
        title_str = topic.get("title", "Signal Theory")
        cat_str = topic.get("category", "General")
        time_str = topic.get("read_time", "5 min read")
        diff_str = topic.get("difficulty", "Basic")

        header_card = QFrame()
        header_card.setObjectName("card-panel")
        header_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-top: 4px solid #06B6D4; border-radius: 10px; padding: 15px; }")
        h_layout = QVBoxLayout(header_card)

        # Top row: Navigation Buttons & Badges
        nav_row = QHBoxLayout()
        
        prev_btn = QPushButton("◄ Previous Lesson")
        prev_btn.setEnabled(self.current_flat_idx > 0)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                border: 1px solid #26334D;
                color: #CBD5E1;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #06B6D4;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                color: #475569;
                border-color: #1E293B;
            }
        """)
        prev_btn.clicked.connect(self.navigate_prev_topic)

        next_btn = QPushButton("Next Lesson ►")
        next_btn.setEnabled(self.current_flat_idx < len(self.flat_topics) - 1)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                border: 1px solid #2563EB;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #3B82F6;
            }
            QPushButton:disabled {
                background-color: #1E293B;
                color: #475569;
                border-color: #1E293B;
            }
        """)
        next_btn.clicked.connect(self.navigate_next_topic)

        cat_lbl = QLabel(f"CATEGORY: {cat_str.upper()}")
        cat_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 9pt; letter-spacing: 1px;")

        nav_row.addWidget(prev_btn)
        nav_row.addWidget(next_btn)
        nav_row.addStretch()
        nav_row.addWidget(cat_lbl)
        h_layout.addLayout(nav_row)

        t_lbl = QLabel(title_str)
        t_lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: #FFFFFF; padding-top: 5px;")
        h_layout.addWidget(t_lbl)

        sum_lbl = QLabel(topic.get("summary", ""))
        sum_lbl.setStyleSheet("color: #C9D1E3; font-size: 10.5pt; line-height: 1.4;")
        sum_lbl.setWordWrap(True)
        h_layout.addWidget(sum_lbl)

        self.reader_layout.addWidget(header_card)

        # 2. Memory Trick Card (If present)
        if topic.get("memory_trick"):
            mem_card = QFrame()
            mem_card.setStyleSheet("background-color: #1F190D; border: 1px solid #F59E0B; border-radius: 8px; padding: 12px;")
            m_layout = QVBoxLayout(mem_card)
            m_lbl = QLabel(topic["memory_trick"])
            m_lbl.setStyleSheet("color: #FBBF24; font-size: 10.5pt; font-weight: 500;")
            m_lbl.setWordWrap(True)
            m_layout.addWidget(m_lbl)
            self.reader_layout.addWidget(mem_card)

        # Section Maker Helper
        def make_section(title, text, color="#06B6D4"):
            card = QFrame()
            card.setObjectName("card-panel")
            card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
            lay = QVBoxLayout(card)
            
            hdr = QLabel(title)
            hdr.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {color}; padding-bottom: 6px; border-bottom: 1px solid #26334D;")
            lay.addWidget(hdr)

            content = QLabel(text)
            content.setStyleSheet("color: #E2E8F0; font-size: 10pt; line-height: 1.5;")
            content.setWordWrap(True)
            lay.addWidget(content)
            return card

        # 3. Theory & Academic Concepts
        if topic.get("theory"):
            self.reader_layout.addWidget(make_section("📖 Theory & Academic Concepts", topic["theory"]))

        # 4. Mathematical Derivation
        if topic.get("derivation"):
            self.reader_layout.addWidget(make_section("📐 Mathematical Derivation & Proof", topic["derivation"], color="#38BDF8"))

        # 5. Important Formulas
        if topic.get("important_formulas"):
            f_card = QFrame()
            f_card.setStyleSheet("background-color: #0F172A; border: 1px solid #06B6D4; border-radius: 8px; padding: 12px;")
            f_lay = QVBoxLayout(f_card)
            f_title = QLabel("⚡ Key Governing Equations & Formulas")
            f_title.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 11pt; padding-bottom: 4px;")
            f_lay.addWidget(f_title)
            
            for form in topic["important_formulas"]:
                flbl = QLabel(f"•  {form}")
                flbl.setStyleSheet("color: #F8FAFC; font-size: 10.5pt; font-weight: 600; font-family: Consolas, monospace; padding: 3px 0px;")
                flbl.setWordWrap(True)
                f_lay.addWidget(flbl)
            self.reader_layout.addWidget(f_card)

        # 6. Interactive Simulation Banner Card
        sim_card = QFrame()
        sim_card.setStyleSheet("background-color: #0B1E2D; border: 2px solid #06B6D4; border-radius: 10px; padding: 16px;")
        sim_lay = QHBoxLayout(sim_card)

        sim_info = QVBoxLayout()
        sim_title = QLabel("🧪 Interactive Simulation Lab")
        sim_title.setStyleSheet("color: #06B6D4; font-size: 13pt; font-weight: bold;")
        sim_desc = QLabel(f"Explore '{title_str}' visually. Manipulate live signal parameters and observe waveforms in real time.")
        sim_desc.setStyleSheet("color: #CBD5E1; font-size: 10pt;")
        sim_desc.setWordWrap(True)
        sim_info.addWidget(sim_title)
        sim_info.addWidget(sim_desc)

        launch_btn = QPushButton("🚀 Launch Interactive Simulation")
        launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #06B6D4;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 10pt;
                border-radius: 8px;
                padding: 10px 18px;
            }
            QPushButton:hover {
                background-color: #0891B2;
            }
        """)
        
        sim_params = {
            "module_idx": module_idx,
            "title": title_str,
            "file": file_name,
            "id": topic_id
        }
        launch_btn.clicked.connect(lambda checked=False, m_idx=module_idx, p=sim_params: self.launch_simulation_requested.emit(m_idx, p))

        sim_lay.addLayout(sim_info, 1)
        sim_lay.addWidget(launch_btn)
        self.reader_layout.addWidget(sim_card)

        # 7. Worked Numerical Examples
        if topic.get("examples"):
            ex_card = QFrame()
            ex_card.setObjectName("card-panel")
            ex_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
            ex_lay = QVBoxLayout(ex_card)
            ex_hdr = QLabel("📝 Worked Numerical Example")
            ex_hdr.setStyleSheet("font-size: 12pt; font-weight: bold; color: #10B981; padding-bottom: 6px; border-bottom: 1px solid #26334D;")
            ex_lay.addWidget(ex_hdr)

            for ex in topic["examples"]:
                prob = QLabel(f"**Problem**: {ex.get('problem', '')}")
                prob.setStyleSheet("color: #F8FAFC; font-weight: bold; font-size: 10.5pt; padding-top: 6px;")
                prob.setWordWrap(True)
                sol = QLabel(f"**Solution**:\n{ex.get('solution', '')}")
                sol.setStyleSheet("color: #34D399; font-size: 10pt; background-color: #09121E; padding: 10px; border-radius: 6px; margin-top: 4px;")
                sol.setWordWrap(True)
                ex_lay.addWidget(prob)
                ex_lay.addWidget(sol)
            self.reader_layout.addWidget(ex_card)

        # 8. Common Mistakes
        if topic.get("common_mistakes"):
            cm_card = QFrame()
            cm_card.setStyleSheet("background-color: #2D1419; border: 1px solid #EF4444; border-radius: 8px; padding: 12px;")
            cm_lay = QVBoxLayout(cm_card)
            cm_hdr = QLabel("⚠️ Common Mistakes & Exam Traps")
            cm_hdr.setStyleSheet("color: #F87171; font-weight: bold; font-size: 11pt;")
            cm_lay.addWidget(cm_hdr)
            for cm in topic["common_mistakes"]:
                cmlbl = QLabel(f"• {cm}")
                cmlbl.setStyleSheet("color: #FCA5A5; font-size: 10pt;")
                cmlbl.setWordWrap(True)
                cm_lay.addWidget(cmlbl)
            self.reader_layout.addWidget(cm_card)

        # 9. Technical Interview & Viva Voce Q&A
        if topic.get("interview_questions") or topic.get("viva_questions"):
            qa_card = QFrame()
            qa_card.setObjectName("card-panel")
            qa_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
            qa_lay = QVBoxLayout(qa_card)
            qa_hdr = QLabel("🎓 Technical Interview & Viva Voce Q&A")
            qa_hdr.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F59E0B; padding-bottom: 6px; border-bottom: 1px solid #26334D;")
            qa_lay.addWidget(qa_hdr)

            all_qa = topic.get("interview_questions", []) + topic.get("viva_questions", [])
            for qa in all_qa:
                q = QLabel(f"Q: {qa.get('question', '')}")
                q.setStyleSheet("color: #FCD34D; font-weight: bold; font-size: 10pt; padding-top: 6px;")
                q.setWordWrap(True)
                a = QLabel(f"A: {qa.get('answer', '')}")
                a.setStyleSheet("color: #E2E8F0; font-size: 9.5pt; padding-bottom: 6px;")
                a.setWordWrap(True)
                qa_lay.addWidget(q)
                qa_lay.addWidget(a)
            self.reader_layout.addWidget(qa_card)

        # 10. Bottom Navigation Bar
        bot_nav_card = QFrame()
        bot_nav_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px;")
        bn_lay = QHBoxLayout(bot_nav_card)
        
        bot_prev = QPushButton("◄ Previous Lesson")
        bot_prev.setEnabled(self.current_flat_idx > 0)
        bot_prev.setStyleSheet(prev_btn.styleSheet())
        bot_prev.clicked.connect(self.navigate_prev_topic)

        bot_next = QPushButton("Next Lesson ►")
        bot_next.setEnabled(self.current_flat_idx < len(self.flat_topics) - 1)
        bot_next.setStyleSheet(next_btn.styleSheet())
        bot_next.clicked.connect(self.navigate_next_topic)

        bn_lay.addWidget(bot_prev)
        bn_lay.addStretch()
        bn_lay.addWidget(bot_next)
        self.reader_layout.addWidget(bot_nav_card)

        # Reset Scrollbar Position to Top
        self.reader_scroll.verticalScrollBar().setValue(0)

    def filter_topics(self, text):
        query = text.lower().strip()
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            mod_item = root.child(i)
            mod_visible = False
            for j in range(mod_item.childCount()):
                top_item = mod_item.child(j)
                title = top_item.text(0).lower()
                match = query in title
                top_item.setHidden(not match)
                if match:
                    mod_visible = True
            mod_item.setHidden(not mod_visible)
            if query:
                mod_item.setExpanded(True)

    def on_filter_changed(self, idx):
        cat = self.cat_filter.currentText()
        if cat == "All Categories":
            self.filter_topics("")
        else:
            self.filter_topics(cat)
