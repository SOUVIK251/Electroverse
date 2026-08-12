from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt
import qtawesome as qta
from src.core.screen_protection import screen_protection

class EngineeringWorkspaceDialog(QDialog):
    """Engineering Workspace for saving notes, circuits & bookmarks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        screen_protection.apply_to_dialog(self)
        self.setWindowTitle("💼 Engineering Workspace & Saved Notebook")
        self.resize(700, 500)
        self.setStyleSheet("background-color: #0B1020; color: #FFFFFF;")
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)

        hdr = QLabel("💼 Engineering Workspace & Notebook")
        hdr.setStyleSheet("color: #06B6D4; font-size: 14pt; font-weight: bold;")
        lay.addWidget(hdr)

        content = QHBoxLayout()

        # Left List
        self.list_w = QListWidget()
        self.list_w.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; color: #FFF;")
        self.list_w.addItem("📌 Saved Circuit 1: Thevenin Equivalent (Vth=6.8V, Rth=0.68kΩ)")
        self.list_w.addItem("📌 Saved Note: Remember to short voltage sources during Superposition")
        self.list_w.addItem("⭐ Bookmark: Series & Parallel Resonance Quality Factor")
        content.addWidget(self.list_w, 1)

        # Right Note Editor
        right_box = QFrame()
        right_box.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 10px;")
        rl = QVBoxLayout(right_box)
        rl.addWidget(QLabel("Note Details / Solved Circuit Notes:", styleSheet="color: #94A3B8;"))

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Type your engineering notes, saved formulas, or laboratory observation notes here...")
        self.editor.setStyleSheet("background-color: #0F172A; color: #FFF; border: 1px solid #26334D;")
        rl.addWidget(self.editor)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Note")
        save_btn.setStyleSheet("background-color: #10B981; color: #FFF; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        rl.addLayout(btn_row)

        content.addWidget(right_box, 2)
        lay.addLayout(content)
