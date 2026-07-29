"""
Textbook-Grade Interactive Lesson Reader Widget (75% Screen Width)
Features Sticky Lesson Header, Single Continuous Scrollable Body,
Large 320x220 Diagram Cards, Full-Width Truth Tables, Centered Boolean Equation Banners,
Prominent "🧠 Easy Memory Trick" Cards, 15px Readable Body Typography with 1.5 Line Spacing, and 1-Click Trainer Kit Launcher.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPixmap

from .image_viewer_dialog import ImageViewerDialog

class LessonReaderWidget(QWidget):
    launch_experiment_requested = Signal(str) # experiment_id or ic_key
    cross_link_clicked = Signal(str) # topic_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_topic_data = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. STICKY HEADER PANEL (Fixed at top, never scrolls)
        self.sticky_header = QFrame()
        self.sticky_header.setFixedHeight(56)
        self.sticky_header.setStyleSheet("background-color: #101827; border-bottom: 1px solid #26334D;")
        
        h_lay = QHBoxLayout(self.sticky_header)
        h_lay.setContentsMargins(20, 0, 20, 0)
        h_lay.setSpacing(15)
        
        v_title = QVBoxLayout()
        v_title.setSpacing(2)
        
        self.lbl_sticky_title = QLabel("Lesson Reader")
        self.lbl_sticky_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_sticky_title.setStyleSheet("color: #06B6D4;")
        v_title.addWidget(self.lbl_sticky_title)
        
        self.lbl_sticky_meta = QLabel("Digital Electronics Curriculum")
        self.lbl_sticky_meta.setStyleSheet("color: #22C55E; font-weight: bold; font-size: 9pt;")
        v_title.addWidget(self.lbl_sticky_meta)
        
        h_lay.addLayout(v_title, 1)
        
        self.btn_sticky_launch = QPushButton(" 🧪 Launch Trainer Kit Experiment ➡ ")
        self.btn_sticky_launch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sticky_launch.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 9.5pt;
                padding: 8px 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3B82F6;
            }
        """)
        self.btn_sticky_launch.clicked.connect(self.on_sticky_launch_clicked)
        h_lay.addWidget(self.btn_sticky_launch)
        
        main_layout.addWidget(self.sticky_header)
        
        # 2. SINGLE INDEPENDENT SCROLL AREA FOR LESSON BODY
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #0B1020; }")
        
        self.content_container = QWidget()
        self.c_layout = QVBoxLayout(self.content_container)
        self.c_layout.setContentsMargins(20, 20, 20, 20)
        self.c_layout.setSpacing(18)
        
        self.scroll.setWidget(self.content_container)
        main_layout.addWidget(self.scroll, 1)

    def load_topic_json(self, topic_data_or_path):
        data = None
        if isinstance(topic_data_or_path, str):
            rel_path = topic_data_or_path.replace("/", os.sep).replace("\\", os.sep)
            base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "theory")
            full_path = os.path.abspath(os.path.join(base, rel_path))
            
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                except Exception as e:
                    print(f"Error loading topic json {full_path}: {e}")
            else:
                print(f"Topic JSON not found at: {full_path}")
        elif isinstance(topic_data_or_path, dict):
            data = topic_data_or_path
            
        if data:
            self.current_topic_data = data
            self.render_lesson()
            # Scroll body to top
            self.scroll.verticalScrollBar().setValue(0)
        else:
            self.render_error_card(topic_data_or_path)

    def on_sticky_launch_clicked(self):
        if self.current_topic_data:
            exp_id = self.current_topic_data.get("experiment_id", "half_adder")
            self.launch_experiment_requested.emit(exp_id)

    def render_error_card(self, path_attempted):
        while self.c_layout.count():
            item = self.c_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
                
        card = QFrame()
        card.setStyleSheet("background-color: #450a0a; border: 2px solid #ef4444; border-radius: 8px; padding: 20px;")
        lay = QVBoxLayout(card)
        
        t = QLabel("⚠️ Lesson Dataset Warning")
        t.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t.setStyleSheet("color: #fca5a5;")
        lay.addWidget(t)
        
        lbl = QLabel(f"Attempted to load topic from: {path_attempted}.\nFile could not be found or read. Please select another lesson from the left syllabus sidebar.")
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #ffffff; font-size: 11pt;")
        lay.addWidget(lbl)
        
        self.c_layout.addWidget(card)

    def render_lesson(self):
        # Clear existing layout
        while self.c_layout.count():
            item = self.c_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
                
        data = self.current_topic_data
        
        # 1. Update Sticky Header
        self.lbl_sticky_title.setText(data.get("title", "Lesson Reader"))
        meta_str = f"Difficulty: {data.get('difficulty', '★☆☆☆☆')}  |  Est Time: {data.get('est_time', '15 Mins')}  |  Category: {data.get('category', 'Logic')}"
        self.lbl_sticky_meta.setText(meta_str)
        
        # 2. Main Title & Introduction Banner (26px Bold Title)
        title_card = QFrame()
        title_card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 18px;")
        t_lay = QVBoxLayout(title_card)
        
        lbl_h1 = QLabel(data.get("title", ""))
        lbl_h1.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        lbl_h1.setStyleSheet("color: #38bdf8; font-size: 26px; font-weight: bold; margin-bottom: 6px;")
        t_lay.addWidget(lbl_h1)
        
        lbl_summary = QLabel(data.get("summary", ""))
        lbl_summary.setWordWrap(True)
        lbl_summary.setStyleSheet("color: #e2e8f0; font-size: 15px; line-height: 1.5; margin-top: 4px;")
        t_lay.addWidget(lbl_summary)
        
        self.c_layout.addWidget(title_card)
        
        # 3. Large Image Cards (320x220 with KeepAspectRatio)
        images = data.get("images", [])
        if images:
            self.render_large_image_gallery(images)
            
        # 4. Working Principle Section (18px Heading, 15px Body)
        self.render_section_card("⚙️ Working Principle", data.get("working_principle", ""))
        
        # 5. Truth Table Section (Spans almost full width)
        tt_data = data.get("truth_table", {})
        if tt_data:
            self.render_full_width_truth_table(tt_data)
            
        # 6. Boolean Equation Section (Centered 22px Highlight Banner)
        eq_str = data.get("boolean_equation", "")
        if eq_str:
            self.render_equation_banner(eq_str)
            
        # 7. EASY MEMORY TRICK CARD
        mnemonic = data.get("mnemonic_trick", "")
        if mnemonic:
            self.render_mnemonic_card(mnemonic)
            
        # 8. Applications, Advantages, Disadvantages, Common Mistakes, Professor Notes
        self.render_bullet_card("🚀 Real-World Applications", data.get("applications", []), color="#06b6d4")
        self.render_bullet_card("✅ Advantages", data.get("advantages", []), color="#10b981")
        self.render_bullet_card("⚠️ Disadvantages & Limitations", data.get("disadvantages", []), color="#ef4444")
        self.render_bullet_card("❌ Common Student Mistakes", data.get("common_mistakes", []), color="#f97316")
        self.render_bullet_card("💡 Quick Notes & Professor Tips", data.get("quick_notes", []), color="#eab308")
        
        # 9. Viva & Technical Interview Questions
        viva = data.get("viva_questions", [])
        if viva:
            self.render_qa_card("🎓 Exam & Viva Voce Questions", viva)
            
        interviews = data.get("interview_questions", [])
        if interviews:
            self.render_qa_card("💼 Technical Interview Questions", interviews)
            
        # 10. Cross-Links & Knowledge Graph
        links = data.get("cross_links", [])
        if links:
            self.render_cross_links_card(links)
            
        kg = data.get("knowledge_graph", [])
        if kg:
            self.render_knowledge_graph_card(kg)
            
        # 11. Bottom Action Banner
        exp_id = data.get("experiment_id", "")
        if exp_id:
            self.render_bottom_launch_banner(exp_id, data.get("title", ""))

    def render_large_image_gallery(self, images):
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 16px;")
        lay = QVBoxLayout(card)
        
        title = QLabel("🖼️ Visual Learning Gallery (Click image or button to Zoom/Pan)")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #38bdf8; font-size: 18px;")
        lay.addWidget(title)
        
        g_lay = QHBoxLayout()
        g_lay.setSpacing(16)
        
        for idx, img in enumerate(images):
            box = QFrame()
            box.setStyleSheet("background-color: #090d16; border: 1px solid #334155; border-radius: 6px; padding: 10px;")
            b_lay = QVBoxLayout(box)
            
            lbl_type = QLabel(f"[{img.get('type', 'img').upper()}] {img.get('title', 'Diagram')}")
            lbl_type.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            lbl_type.setStyleSheet("color: #10b981;")
            b_lay.addWidget(lbl_type)
            
            # Large Image Preview 320x220 with KeepAspectRatio
            lbl_img = QLabel()
            lbl_img.setFixedSize(320, 220)
            lbl_img.setScaledContents(False)
            lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            pix = QPixmap(img.get("path", ""))
            if not pix.isNull():
                scaled_pix = pix.scaled(320, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                lbl_img.setPixmap(scaled_pix)
            else:
                lbl_img.setText(f"📷 {img.get('title', 'Diagram')}")
                lbl_img.setStyleSheet("color: #38bdf8; border: 1px dashed #0284c7; background: #0b1329; font-size: 11pt;")
            b_lay.addWidget(lbl_img)
            
            caption = QLabel(img.get("caption", ""))
            caption.setWordWrap(True)
            caption.setStyleSheet("color: #94a3b8; font-size: 8.5pt; margin-top: 4px;")
            b_lay.addWidget(caption)
            
            btn_inspect = QPushButton(" 🔍 Inspect Fullscreen / Zoom ")
            btn_inspect.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_inspect.setStyleSheet("background-color: #0284c7; color: white; font-size: 9pt; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
            btn_inspect.clicked.connect(lambda _, i=idx: self.open_image_viewer(images, i))
            b_lay.addWidget(btn_inspect)
            
            g_lay.addWidget(box)
            
        g_lay.addStretch()
        lay.addLayout(g_lay)
        self.c_layout.addWidget(card)

    def open_image_viewer(self, images, idx):
        dlg = ImageViewerDialog(images, idx, self)
        dlg.exec()

    def render_section_card(self, title_str, body_text):
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 16px;")
        lay = QVBoxLayout(card)
        
        t = QLabel(title_str)
        t.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t.setStyleSheet("color: #38bdf8; font-size: 18px;")
        lay.addWidget(t)
        
        lbl_content = QLabel(body_text)
        lbl_content.setWordWrap(True)
        lbl_content.setStyleSheet("color: #f8fafc; font-size: 15px; line-height: 1.5; margin-top: 6px;")
        lay.addWidget(lbl_content)
        
        self.c_layout.addWidget(card)

    def render_full_width_truth_table(self, tt_data):
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 16px;")
        lay = QVBoxLayout(card)
        
        t = QLabel("📊 Truth Table Verification")
        t.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t.setStyleSheet("color: #34d399; font-size: 18px;")
        lay.addWidget(t)
        
        table = QTableWidget()
        inputs = tt_data.get("inputs", [])
        outputs = tt_data.get("outputs", [])
        rows = tt_data.get("rows", [])
        
        table.setColumnCount(len(inputs) + len(outputs))
        table.setHorizontalHeaderLabels(inputs + outputs)
        table.setRowCount(len(rows))
        table.setStyleSheet("""
            QTableWidget { background-color: #090d16; color: #f8fafc; gridline-color: #1e293b; border: 1px solid #1e293b; border-radius: 6px; font-size: 14px; }
            QHeaderView::section { background-color: #1e293b; color: #38bdf8; font-weight: bold; padding: 6px; font-size: 14px; }
        """)
        
        for r_idx, r in enumerate(rows):
            col_idx = 0
            for in_val in r.get("inputs", []):
                item = QTableWidgetItem(str(in_val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(r_idx, col_idx, item)
                col_idx += 1
            for out_val in r.get("outputs", []):
                item = QTableWidgetItem(str(out_val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor("#10b981" if str(out_val) in ["1", "1, 1"] else "#ef4444"))
                table.setItem(r_idx, col_idx, item)
                col_idx += 1
                
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setFixedHeight(min(240, (len(rows)+1)*36))
        lay.addWidget(table)
        
        self.c_layout.addWidget(card)

    def render_equation_banner(self, eq_str):
        banner = QFrame()
        banner.setStyleSheet("background-color: #0c4a6e; border: 2px solid #0284c7; border-radius: 8px; padding: 16px;")
        lay = QVBoxLayout(banner)
        
        t = QLabel("🧮 Boolean Expression")
        t.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        t.setStyleSheet("color: #38bdf8;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)
        
        lbl_eq = QLabel(eq_str)
        lbl_eq.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_eq.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_eq.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold; margin-top: 4px;")
        lay.addWidget(lbl_eq)
        
        self.c_layout.addWidget(banner)

    def render_mnemonic_card(self, mnemonic_str):
        card = QFrame()
        card.setStyleSheet("background-color: #172554; border: 2px solid #eab308; border-radius: 8px; padding: 16px;")
        lay = QVBoxLayout(card)
        
        t = QLabel("🧠 Easy Memory Trick (How to Remember Instantly)")
        t.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t.setStyleSheet("color: #eab308; font-size: 18px;")
        lay.addWidget(t)
        
        lbl_m = QLabel(mnemonic_str)
        lbl_m.setWordWrap(True)
        lbl_m.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: bold; line-height: 1.5; margin-top: 4px;")
        lay.addWidget(lbl_m)
        
        self.c_layout.addWidget(card)

    def render_bullet_card(self, title_str, bullet_list, color="#38bdf8"):
        if not bullet_list:
            return
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 16px;")
        lay = QVBoxLayout(card)
        
        t = QLabel(title_str)
        t.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {color}; font-size: 18px;")
        lay.addWidget(t)
        
        for item in bullet_list:
            lbl = QLabel(f"• {item}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #f8fafc; font-size: 15px; line-height: 1.5; margin-top: 4px;")
            lay.addWidget(lbl)
            
        self.c_layout.addWidget(card)

    def render_qa_card(self, title_str, qa_list):
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 16px;")
        lay = QVBoxLayout(card)
        
        t = QLabel(title_str)
        t.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t.setStyleSheet("color: #eab308; font-size: 18px;")
        lay.addWidget(t)
        
        for qa in qa_list:
            q_lbl = QLabel(f"Q: {qa.get('q', '')}")
            q_lbl.setWordWrap(True)
            q_lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 15px; margin-top: 8px;")
            lay.addWidget(q_lbl)
            
            a_lbl = QLabel(f"A: {qa.get('a', '')}")
            a_lbl.setWordWrap(True)
            a_lbl.setStyleSheet("color: #34d399; font-size: 15px; font-style: italic; line-height: 1.4; margin-bottom: 4px;")
            lay.addWidget(a_lbl)
            
        self.c_layout.addWidget(card)

    def make_cross_link_callback(self, link_id):
        def callback():
            self.cross_link_clicked.emit(link_id)
        return callback

    def render_cross_links_card(self, links):
        card = QFrame()
        card.setStyleSheet("background-color: #0f172a; border: 1px solid #0284c7; border-radius: 8px; padding: 12px;")
        lay = QHBoxLayout(card)
        
        t = QLabel("🔗 Connected Topics:")
        t.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        t.setStyleSheet("color: #06b6d4;")
        lay.addWidget(t)
        
        for link in links:
            btn = QPushButton(f" ➡ {link.get('name', 'Topic')} ")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("background-color: #1e293b; color: #38bdf8; font-size: 9pt; font-weight: bold; padding: 4px 10px; border-radius: 4px;")
            btn.clicked.connect(self.make_cross_link_callback(link.get("id", "")))
            lay.addWidget(btn)
            
        lay.addStretch()
        self.c_layout.addWidget(card)

    def render_knowledge_graph_card(self, kg_chain):
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 12px;")
        lay = QHBoxLayout(card)
        
        t = QLabel("🌐 Knowledge Chain:")
        t.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        t.setStyleSheet("color: #a855f7;")
        lay.addWidget(t)
        
        chain_str = " ➔ ".join(kg_chain)
        lbl_chain = QLabel(chain_str)
        lbl_chain.setStyleSheet("color: #cbd5e1; font-weight: bold; font-size: 9.5pt;")
        lay.addWidget(lbl_chain)
        
        lay.addStretch()
        self.c_layout.addWidget(card)

    def render_bottom_launch_banner(self, exp_id, topic_title):
        banner = QFrame()
        banner.setStyleSheet("background-color: #032b45; border: 2px solid #0284c7; border-radius: 8px; padding: 18px;")
        lay = QHBoxLayout(banner)
        
        v_info = QVBoxLayout()
        t1 = QLabel(f"⚡ Ready to perform the {topic_title} experiment?")
        t1.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t1.setStyleSheet("color: #ffffff;")
        v_info.addWidget(t1)
        
        t2 = QLabel("Launch the interactive 2D breadboard trainer kit to wire and verify this circuit in real-time.")
        t2.setStyleSheet("color: #38bdf8; font-size: 14px;")
        v_info.addWidget(t2)
        
        lay.addLayout(v_info, 1)
        
        btn_launch = QPushButton(" 🧪 Launch Trainer Kit Experiment ➡ ")
        btn_launch.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_launch.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; font-size: 11pt; padding: 10px 20px; border-radius: 6px;")
        btn_launch.clicked.connect(lambda: self.launch_experiment_requested.emit(exp_id))
        lay.addWidget(btn_launch)
        
        self.c_layout.addWidget(banner)
