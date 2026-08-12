from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

from src.core.certificate_engine import CertificateEngine
from src.core.screen_protection import screen_protection

class CertificateDialog(QDialog):
    """Interactive Certificate Viewer and Image/PDF Exporter."""

    def __init__(self, student_name, subject_title, score_pct, grade, parent=None):
        super().__init__(parent)
        screen_protection.apply_to_dialog(self)
        self.setWindowTitle("ElectroVerse Certificate of Mastery")
        self.setFixedSize(840, 620)
        self.setStyleSheet("background-color: #0B1020; color: #FFFFFF;")

        self.student_name = student_name
        self.subject_title = subject_title
        self.score_pct = score_pct
        self.grade = grade

        self.cert_image = CertificateEngine.generate_certificate_image(student_name, subject_title, score_pct, grade)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Image Viewer
        pixmap = QPixmap.fromImage(self.cert_image).scaled(800, 520, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        img_lbl = QLabel()
        img_lbl.setPixmap(pixmap)
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_lbl)

        # Action Row
        act_row = QHBoxLayout()
        save_btn = QPushButton("💾 Save Certificate Image (.png)")
        save_btn.setStyleSheet("background-color: #10B981; color: #FFF; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        save_btn.clicked.connect(self.save_certificate)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #1E293B; color: #FFF; padding: 8px 16px; border-radius: 6px;")
        close_btn.clicked.connect(self.accept)

        act_row.addWidget(save_btn)
        act_row.addStretch()
        act_row.addWidget(close_btn)
        layout.addLayout(act_row)

    def save_certificate(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Certificate", f"Certificate_{self.subject_title.replace(' ', '_')}.png", "PNG Image (*.png)")
        if path:
            self.cert_image.save(path, "PNG")
