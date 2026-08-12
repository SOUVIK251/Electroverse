"""
ElectroVerse Intel 8085 Opcode Reference Viewer Dialog
======================================================
Displays the user-provided Intel 8085 Opcode Table image in high resolution.
Validates file path integrity, handles missing/invalid files gracefully with
a clear error message, and preserves all interactive zoom, fit, and panning controls.
"""

import os
import hashlib
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem
)
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QPixmap, QWheelEvent, QTransform, QKeySequence, QShortcut, QPainter, QFont


class ZoomableGraphicsView(QGraphicsView):
    """Custom QGraphicsView with smooth mouse-wheel zooming, drag-panning, and antialiased scaling."""

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("""
            QGraphicsView {
                background-color: #0B1020;
                border: 1px solid #1E293B;
                border-radius: 6px;
            }
        """)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom in/out with mouse scroll wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        current_scale = self.transform().m11()
        if (current_scale * zoom_factor < 0.1 and zoom_factor < 1.0) or (current_scale * zoom_factor > 10.0 and zoom_factor > 1.0):
            return

        self.scale(zoom_factor, zoom_factor)


from src.core.screen_protection import screen_protection


class OpcodeViewerDialog(QDialog):
    """Modal Dialog displaying the Intel 8085 Opcode Reference Chart."""

    ERROR_MESSAGE_NOT_FOUND = "Intel 8085 Opcode Reference image not found."

    def __init__(self, parent=None, custom_image_path=None):
        super().__init__(parent)
        screen_protection.apply_to_dialog(self)
        self.setWindowTitle("Intel 8085 Opcode Reference")
        self.resize(1200, 850)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #F8FAFC;
            }
        """)

        self._custom_image_path = custom_image_path
        self._is_fit_mode = True
        self.pixmap_item = None
        self.error_item = None

        self._init_ui()
        self._load_and_validate_image()

        # Shortcut: Esc closes dialog
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.accept)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Header Toolbar Bar
        hdr_bar = QFrame()
        hdr_bar.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)
        h_lay = QHBoxLayout(hdr_bar)
        h_lay.setContentsMargins(4, 4, 4, 4)
        h_lay.setSpacing(8)

        title_lbl = QLabel("📖  Intel 8085 Instruction Set & Opcode Reference")
        title_lbl.setStyleSheet("font-size: 11pt; font-weight: bold; color: #10B981;")
        h_lay.addWidget(title_lbl)

        h_lay.addStretch()

        # Toolbar Control Buttons (Preserved UI Controls)
        btn_style = """
            QPushButton {
                background-color: #0F172A;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: #FFFFFF;
                border-color: #10B981;
            }
        """

        self.btn_zoom_in = QPushButton("➕ Zoom In")
        self.btn_zoom_in.setStyleSheet(btn_style)
        self.btn_zoom_in.setToolTip("Zoom In (Mouse Wheel Up)")
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        h_lay.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("➖ Zoom Out")
        self.btn_zoom_out.setStyleSheet(btn_style)
        self.btn_zoom_out.setToolTip("Zoom Out (Mouse Wheel Down)")
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        h_lay.addWidget(self.btn_zoom_out)

        self.btn_fit = QPushButton("📐 Fit Window")
        self.btn_fit.setStyleSheet(btn_style)
        self.btn_fit.setToolTip("Fit Chart to Window Viewport")
        self.btn_fit.clicked.connect(self._fit_to_window)
        h_lay.addWidget(self.btn_fit)

        self.btn_reset = QPushButton("↺ Reset (1:1)")
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_reset.setToolTip("Reset Zoom to Original Resolution 100%")
        self.btn_reset.clicked.connect(self._reset_zoom)
        h_lay.addWidget(self.btn_reset)

        self.btn_full = QPushButton("⛶ Fullscreen")
        self.btn_full.setStyleSheet(btn_style)
        self.btn_full.setToolTip("Toggle Fullscreen View")
        self.btn_full.clicked.connect(self._toggle_fullscreen)
        h_lay.addWidget(self.btn_full)

        self.btn_close = QPushButton("❌ Close")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #7F1D1D;
                color: #FFFFFF;
                border: 1px solid #991B1B;
                border-radius: 4px;
                padding: 5px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #EF4444;
            }
        """)
        self.btn_close.clicked.connect(self.accept)
        h_lay.addWidget(self.btn_close)

        layout.addWidget(hdr_bar)

        # Graphics Scene & View
        self.scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene, self)
        layout.addWidget(self.view, 1)

        # Footer Hint
        hint_lbl = QLabel("💡 Tip: Use Mouse Scroll Wheel to Zoom  |  Click & Drag to Pan  |  Press Esc or Close button to Exit")
        hint_lbl.setStyleSheet("color: #94A3B8; font-size: 8.5pt;")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_lbl)

    def _resolve_image_path(self):
        """Resolve target path for the user-provided Intel 8085 Opcode Table image."""
        if self._custom_image_path:
            p = Path(self._custom_image_path)
            if p.exists() and p.is_file():
                return p
            else:
                return None  # Explicit custom path specified but invalid -> no fallback

        base_dir = Path(__file__).resolve().parent.parent.parent  # src/
        repo_dir = base_dir.parent                                 # repo root

        candidates = [
            base_dir / "assets" / "images" / "8085_opcode_reference.png",
            repo_dir / "assets" / "images" / "8085_opcode_reference.png",
            repo_dir / "8085_opcode_reference.png",
        ]

        for p in candidates:
            if p.exists() and p.is_file():
                return p

        return None

    def _validate_image_file(self, file_path: Path) -> bool:
        """
        Validation step to confirm the file is indeed the valid Intel 8085 Opcode Table image.
        Checks existence, non-empty size, and image pixmap validity.
        """
        if not file_path or not file_path.exists():
            return False

        if file_path.stat().st_size == 0:
            return False

        pixmap = QPixmap(str(file_path))
        if pixmap.isNull() or pixmap.width() <= 0 or pixmap.height() <= 0:
            return False

        return True

    def _display_error(self, message: str):
        """Display clear error message in the scene without loading any image or substitute."""
        self.scene.clear()
        self.pixmap_item = None

        text_item = QGraphicsTextItem(message)
        font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        text_item.setFont(font)
        text_item.setDefaultTextColor(Qt.GlobalColor.red)
        self.scene.addItem(text_item)
        self.scene.setSceneRect(text_item.boundingRect())
        self.error_item = text_item

    def _load_and_validate_image(self):
        """Validate path and load Intel 8085 Opcode Table image or render error state."""
        img_path = self._resolve_image_path()

        if not img_path or not self._validate_image_file(img_path):
            print(f"[OpcodeViewerDialog] Error: {self.ERROR_MESSAGE_NOT_FOUND}")
            self._display_error(self.ERROR_MESSAGE_NOT_FOUND)
            return

        pixmap = QPixmap(str(img_path))
        print(f"[OpcodeViewerDialog] Loaded Intel 8085 Opcode Table ({pixmap.width()}x{pixmap.height()} px) from: {img_path}")

        self.scene.clear()
        self.error_item = None
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

    def showEvent(self, event):
        """When dialog opens, fit image automatically to the window viewport."""
        super().showEvent(event)
        QTimer.singleShot(10, self._fit_to_window)

    def resizeEvent(self, event):
        """When window is resized, update fit if currently in fit mode."""
        super().resizeEvent(event)
        if self._is_fit_mode:
            QTimer.singleShot(10, self._apply_fit)

    def _zoom_in(self):
        self._is_fit_mode = False
        self.view.scale(1.25, 1.25)

    def _zoom_out(self):
        self._is_fit_mode = False
        self.view.scale(0.8, 0.8)

    def _fit_to_window(self):
        self._is_fit_mode = True
        self._apply_fit()

    def _apply_fit(self):
        if self.pixmap_item and self.view:
            self.view.resetTransform()
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
            self.view.centerOn(self.pixmap_item)

    def _reset_zoom(self):
        self._is_fit_mode = False
        self.view.setTransform(QTransform())
        if self.pixmap_item:
            self.view.centerOn(self.pixmap_item)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_full.setText("⛶ Fullscreen")
        else:
            self.showFullScreen()
            self.btn_full.setText("❐ Exit Fullscreen")
        QTimer.singleShot(50, self._apply_fit)
