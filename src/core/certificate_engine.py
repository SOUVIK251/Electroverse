import os
import time
import random
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QPixmap, QImage
from PySide6.QtCore import Qt, QRect

class CertificateEngine:
    """Generates official ElectroVerse Certificate of Mastery for score >= 80%."""

    @staticmethod
    def generate_certificate_image(student_name, subject_title, score_pct, grade, cert_id=None):
        if cert_id is None:
            cert_id = f"EV-CERT-2026-{random.randint(100000, 999999)}"

        width, height = 1000, 700
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(QColor("#0B1020"))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Outer Gold Border
        pen_gold = QPen(QColor("#F59E0B"), 6)
        painter.setPen(pen_gold)
        painter.drawRect(20, 20, width - 40, height - 40)

        # Inner Cyan Border
        pen_cyan = QPen(QColor("#06B6D4"), 2)
        painter.setPen(pen_cyan)
        painter.drawRect(30, 30, width - 60, height - 60)

        # Header Title
        painter.setPen(QColor("#06B6D4"))
        font_hdr = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font_hdr)
        painter.drawText(QRect(50, 70, width - 100, 50), Qt.AlignmentFlag.AlignCenter, "⚡ ELECTROVERSE VIRTUAL ENGINEERING LAB ⚡")

        painter.setPen(QColor("#F59E0B"))
        font_sub = QFont("Segoe UI", 18, QFont.Weight.Bold)
        painter.setFont(font_sub)
        painter.drawText(QRect(50, 130, width - 100, 40), Qt.AlignmentFlag.AlignCenter, "CERTIFICATE OF ENGINEERING MASTERY")

        # Body Text
        painter.setPen(QColor("#C9D1E3"))
        font_body = QFont("Segoe UI", 12)
        painter.setFont(font_body)
        painter.drawText(QRect(50, 210, width - 100, 30), Qt.AlignmentFlag.AlignCenter, "This is to certify that")

        # Student Name
        painter.setPen(QColor("#FFFFFF"))
        font_name = QFont("Segoe UI", 26, QFont.Weight.Bold)
        painter.setFont(font_name)
        painter.drawText(QRect(50, 250, width - 100, 50), Qt.AlignmentFlag.AlignCenter, student_name.upper())

        painter.setPen(QColor("#C9D1E3"))
        painter.setFont(font_body)
        painter.drawText(QRect(50, 320, width - 100, 30), Qt.AlignmentFlag.AlignCenter, "has successfully passed the Computer-Based Examination in")

        # Subject Title
        painter.setPen(QColor("#06B6D4"))
        font_subj = QFont("Segoe UI", 20, QFont.Weight.Bold)
        painter.setFont(font_subj)
        painter.drawText(QRect(50, 360, width - 100, 40), Qt.AlignmentFlag.AlignCenter, subject_title)

        # Score & Grade Banner
        painter.setPen(QColor("#10B981"))
        font_score = QFont("Segoe UI", 16, QFont.Weight.Bold)
        painter.setFont(font_score)
        painter.drawText(QRect(50, 430, width - 100, 40), Qt.AlignmentFlag.AlignCenter, f"Final Score: {score_pct:.1f}%  |  Grade: {grade}  |  Status: PASSED")

        # Footer Credentials & QR Badge
        painter.setPen(QColor("#94A3B8"))
        font_foot = QFont("Segoe UI", 10)
        painter.setFont(font_foot)
        painter.drawText(QRect(60, 580, 400, 30), Qt.AlignmentFlag.AlignLeft, f"Certificate ID: {cert_id}")
        painter.drawText(QRect(60, 610, 400, 30), Qt.AlignmentFlag.AlignLeft, f"Issue Date: 2026-07-29")

        # Instructor Sign
        painter.setPen(QColor("#F8FAFC"))
        painter.drawText(QRect(width - 450, 580, 400, 30), Qt.AlignmentFlag.AlignRight, "Prof. Souvik Kundu")
        painter.drawText(QRect(width - 450, 610, 400, 30), Qt.AlignmentFlag.AlignRight, "Chief Academic Examiner, ElectroVerse")

        painter.end()
        return image
