"""
Interactive Multi-Aspect Image Viewer Dialog
Supports Zoom (in/out/fit), Pan, Fullscreen toggle, Image Captions, and Prev/Next slide navigation.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QColor, QTransform
from src.core.screen_protection import screen_protection

class ImageViewerDialog(QDialog):
    def __init__(self, images_list, current_idx=0, parent=None):
        super().__init__(parent)
        screen_protection.apply_to_dialog(self)
        self.images_list = images_list
        self.current_idx = current_idx
        self.zoom_factor = 1.0
        self.setWindowTitle("🔍 Interactive Image & Diagram Inspector")
        self.setMinimumSize(850, 600)
        self.setStyleSheet("background-color: #0b0f19; color: #f8fafc;")
        self.init_ui()
        self.load_current_image()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header Controls
        hdr = QHBoxLayout()
        self.lbl_title = QLabel("Diagram Viewer")
        self.lbl_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #38bdf8;")
        hdr.addWidget(self.lbl_title)
        
        hdr.addStretch()
        
        btn_zoom_in = QPushButton(" 🔍+ Zoom In ")
        btn_zoom_in.setStyleSheet("background-color: #1e293b; color: white; padding: 4px 8px; border-radius: 4px;")
        btn_zoom_in.clicked.connect(self.zoom_in)
        hdr.addWidget(btn_zoom_in)
        
        btn_zoom_out = QPushButton(" 🔍- Zoom Out ")
        btn_zoom_out.setStyleSheet("background-color: #1e293b; color: white; padding: 4px 8px; border-radius: 4px;")
        btn_zoom_out.clicked.connect(self.zoom_out)
        hdr.addWidget(btn_zoom_out)
        
        btn_reset = QPushButton(" ↺ Reset Fit ")
        btn_reset.setStyleSheet("background-color: #1e293b; color: white; padding: 4px 8px; border-radius: 4px;")
        btn_reset.clicked.connect(self.zoom_reset)
        hdr.addWidget(btn_reset)
        
        btn_full = QPushButton(" ⛶ Fullscreen ")
        btn_full.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 4px 8px; border-radius: 4px;")
        btn_full.clicked.connect(self.toggle_fullscreen)
        hdr.addWidget(btn_full)
        
        layout.addLayout(hdr)
        
        # Center Interactive View
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setStyleSheet("border: 1px solid #1e293b; background-color: #090d16; border-radius: 6px;")
        layout.addWidget(self.view, 1)
        
        # Caption & Slide Controls Footer
        ftr = QHBoxLayout()
        self.btn_prev = QPushButton(" ⬅ Previous ")
        self.btn_prev.setStyleSheet("background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 5px 12px; border-radius: 4px;")
        self.btn_prev.clicked.connect(self.prev_image)
        ftr.addWidget(self.btn_prev)
        
        self.lbl_caption = QLabel("Caption Text")
        self.lbl_caption.setWordWrap(True)
        self.lbl_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_caption.setStyleSheet("color: #cbd5e1; font-size: 8.5pt; font-style: italic;")
        ftr.addWidget(self.lbl_caption, 1)
        
        self.btn_next = QPushButton(" Next ➡ ")
        self.btn_next.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 5px 12px; border-radius: 4px;")
        self.btn_next.clicked.connect(self.next_image)
        ftr.addWidget(self.btn_next)
        
        layout.addLayout(ftr)

    def load_current_image(self):
        if not self.images_list:
            return
        img_info = self.images_list[self.current_idx]
        self.lbl_title.setText(f"Image ({self.current_idx+1}/{len(self.images_list)}): {img_info.get('title', 'Diagram')}")
        self.lbl_caption.setText(img_info.get("caption", ""))
        
        self.scene.clear()
        pixmap = QPixmap(img_info.get("path", ""))
        if pixmap.isNull():
            # Fallback text item if image file not present
            txt = self.scene.addText(f"📷 [{img_info.get('title', 'Diagram Image')}]\nPath: {img_info.get('path', '')}")
            txt.setDefaultTextColor(QColor("#38bdf8"))
            txt.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        else:
            item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(item)
            self.view.setSceneRect(item.boundingRect())
            
        self.btn_prev.setEnabled(self.current_idx > 0)
        self.btn_next.setEnabled(self.current_idx < len(self.images_list) - 1)

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(0.8, 0.8)

    def zoom_reset(self):
        self.view.setTransform(QTransform())

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def prev_image(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.load_current_image()

    def next_image(self):
        if self.current_idx < len(self.images_list) - 1:
            self.current_idx += 1
            self.load_current_image()
