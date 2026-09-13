"""
ElectroVerse AI Tutor PySide6 Interface Panel
Hardware-accelerated, non-blocking side-drawer panel styled in ElectroVerse laboratory theme.
Features asynchronous worker threading, context indicators, quick prompt pills, and chat history.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QScrollArea, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QSize
from PySide6.QtGui import QFont, QColor
import qtawesome as qta

from src.core.logger import log
from src.ai.context_manager import context_manager
from src.ai.tutor import electroverse_tutor


class AIWorkerThread(QThread):
    """Asynchronous worker thread to execute AI Tutor requests without blocking the UI."""
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, query: str, mode: str, extra_context: dict = None):
        super().__init__()
        self.query = query
        self.mode = mode
        self.extra_context = extra_context or {}

    def run(self):
        try:
            res = electroverse_tutor.ask(self.query, self.mode, self.extra_context)
            self.response_ready.emit(res)
        except Exception as e:
            log.error(f"[AIWorkerThread] Exception in tutor execution: {e}")
            self.error_occurred.emit(str(e))


class AITutorPanel(QFrame):
    """Side-Drawer Dock Panel for ElectroVerse AI Tutor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ai-tutor-panel")
        self.setFixedWidth(380)
        self.setStyleSheet("""
            QFrame#ai-tutor-panel {
                background-color: #0b1020;
                border-left: 2px solid #0284c7;
            }
        """)

        self.worker_thread: Optional[AIWorkerThread] = None
        self.init_ui()
        self.refresh_context_pill()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 1. Header Card
        header_card = QFrame()
        header_card.setStyleSheet("background-color: #141b2d; border: 1px solid #26334d; border-radius: 8px; padding: 10px;")
        h_lay = QVBoxLayout(header_card)
        h_lay.setContentsMargins(8, 8, 8, 8)
        h_lay.setSpacing(4)

        t_row = QHBoxLayout()
        icon_lbl = QLabel("🤖")
        icon_lbl.setStyleSheet("font-size: 14pt;")
        t_row.addWidget(icon_lbl)

        title_lbl = QLabel("ElectroVerse AI Tutor")
        title_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #38bdf8;")
        t_row.addWidget(title_lbl)

        t_row.addStretch()

        close_btn = QPushButton()
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setIcon(qta.icon("fa5s.times", color="#94a3b8"))
        close_btn.setStyleSheet("background: transparent; border: none;")
        close_btn.clicked.connect(self.hide)
        t_row.addWidget(close_btn)

        h_lay.addLayout(t_row)

        sub_lbl = QLabel('"Understand engineering, don\'t just memorize it."')
        sub_lbl.setStyleSheet("color: #94a3b8; font-size: 8pt; font-style: italic;")
        h_lay.addWidget(sub_lbl)

        # Context Indicator Pill
        self.context_pill = QLabel("[Context: Dashboard]")
        self.context_pill.setWordWrap(True)
        self.context_pill.setStyleSheet("""
            background-color: #0b1329;
            color: #06b6d4;
            border: 1px solid #0284c7;
            border-radius: 4px;
            padding: 3px 6px;
            font-size: 8pt;
            font-weight: bold;
            margin-top: 4px;
        """)
        h_lay.addWidget(self.context_pill)

        main_layout.addWidget(header_card)

        # 2. Mode Selector Row
        mode_row = QHBoxLayout()
        mode_lbl = QLabel("Mode:")
        mode_lbl.setStyleSheet("color: #cbd5e1; font-weight: bold; font-size: 8.5pt;")
        mode_row.addWidget(mode_lbl)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Tutor", "Viva Examiner", "Problem Solver", "Debug Assistant"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 8.5pt;
                font-weight: bold;
            }
            QComboBox::drop-down { border: none; }
        """)
        mode_row.addWidget(self.mode_combo, 1)

        clear_btn = QPushButton(" Clear")
        clear_btn.setIcon(qta.icon("fa5s.trash", color="#94a3b8"))
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 8pt;
            }
            QPushButton:hover { background-color: #475569; color: white; }
        """)
        clear_btn.clicked.connect(self.clear_chat)
        mode_row.addWidget(clear_btn)

        main_layout.addLayout(mode_row)

        # 3. Quick Prompt Pills
        pills_frame = QFrame()
        pills_frame.setStyleSheet("background: transparent;")
        pills_lay = QHBoxLayout(pills_frame)
        pills_lay.setContentsMargins(0, 0, 0, 0)
        pills_lay.setSpacing(4)

        prompts = [
            ("Explain Concept", "Explain this concept in simple terms."),
            ("Why Output?", "Why is this output occurring in the current simulation?"),
            ("Step-by-Step", "Show me a step by step breakdown of this problem."),
            ("Viva Me", "Ask me a viva voce question based on the current topic.")
        ]

        for p_label, p_text in prompts:
            p_btn = QPushButton(p_label)
            p_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            p_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0b1329;
                    color: #38bdf8;
                    border: 1px solid #0369a1;
                    border-radius: 4px;
                    padding: 3px 6px;
                    font-size: 7.5pt;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #0284c7; color: white; }
            """)
            p_btn.clicked.connect(lambda _, txt=p_text: self.send_prompt(txt))
            pills_lay.addWidget(p_btn)

        main_layout.addWidget(pills_frame)

        # 4. Chat History Display Area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #090d16;
                color: #f8fafc;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 10px;
                font-size: 9pt;
                line-height: 1.5;
            }
        """)
        main_layout.addWidget(self.chat_display, 1)

        # 5. Progress / Thinking Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setRange(0, 0)  # Indeterminate spinner
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #1e293b; border: none; border-radius: 2px; }
            QProgressBar::chunk { background-color: #06b6d4; }
        """)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # 6. Input Row
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask ElectroVerse AI Tutor...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #1e293b;
                color: #ffffff;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
            QLineEdit:focus { border-color: #06b6d4; }
        """)
        self.input_field.returnPressed.connect(self.on_send_clicked)
        input_row.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("Send ")
        self.send_btn.setIcon(qta.icon("fa5s.paper-plane", color="#ffffff"))
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: #ffffff;
                font-weight: bold;
                font-size: 9pt;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
            }
            QPushButton:hover { background-color: #0369a1; }
            QPushButton:disabled { background-color: #334155; color: #64748b; }
        """)
        self.send_btn.clicked.connect(self.on_send_clicked)
        input_row.addWidget(self.send_btn)

        main_layout.addLayout(input_row)

        # Welcome message in chat
        self.append_tutor_message(
            "👋 **Welcome to ElectroVerse AI Tutor!**\n\n"
            "I'm your engineering assistant. I can explain formulas, circuit behavior, 8085 assembly instructions, or test your knowledge with viva questions.\n\n"
            "Ask me anything or click a quick prompt above!"
        )

    def refresh_context_pill(self):
        """Updates the context pill indicator based on live ContextManager state."""
        ctx = context_manager.get_summary_context()
        hub = ctx.get("current_hub", "Dashboard")
        topic = ctx.get("topic_title", "Overview")

        pill_text = f"📍 {hub}"
        if topic and topic != "Overview":
            pill_text += f" › {topic}"

        if "8085_registers" in ctx:
            regs = ctx["8085_registers"]
            pill_text += f" | A={regs.get('A', '00H')} HL={regs.get('HL', '0000H')}"

        self.context_pill.setText(pill_text)

    def clear_chat(self):
        self.chat_display.clear()
        self.append_tutor_message("Chat history cleared. How can I help you with your engineering study?")

    def append_user_message(self, text: str):
        html = f"""
        <div style="margin: 8px 0; text-align: right;">
            <span style="background-color: #0369a1; color: #ffffff; padding: 6px 10px; border-radius: 8px; font-weight: bold; font-size: 8.5pt;">
                👤 You
            </span>
            <div style="background-color: #1e293b; color: #f8fafc; padding: 8px 12px; border-radius: 8px; margin-top: 4px; text-align: left; border: 1px solid #334155;">
                {text}
            </div>
        </div>
        """
        self.chat_display.append(html)

    def append_tutor_message(self, md_text: str):
        # Format basic markdown to HTML for display
        formatted = md_text.replace("\n", "<br>")
        formatted = formatted.replace("**", "<b>").replace("**", "</b>")
        formatted = formatted.replace("```assembly", "<pre style='background:#0f172a; color:#38bdf8; padding:6px; border-radius:4px;'>").replace("```", "</pre>")

        html = f"""
        <div style="margin: 8px 0;">
            <span style="background-color: #0f766e; color: #ffffff; padding: 6px 10px; border-radius: 8px; font-weight: bold; font-size: 8.5pt;">
                🤖 ElectroVerse AI Tutor
            </span>
            <div style="background-color: #0b1329; color: #f8fafc; padding: 10px 12px; border-radius: 8px; margin-top: 4px; border: 1px solid #0284c7;">
                {formatted}
            </div>
        </div>
        """
        self.chat_display.append(html)

    def send_prompt(self, prompt_text: str, extra_context: dict = None):
        self.input_field.setText(prompt_text)
        self.on_send_clicked(extra_context=extra_context)

    def on_send_clicked(self, extra_context: dict = None):
        query = self.input_field.text().strip()
        if not query:
            return

        self.input_field.clear()
        self.refresh_context_pill()
        self.append_user_message(query)

        # UI Loading State
        self.send_btn.setEnabled(False)
        self.progress_bar.show()

        mode = self.mode_combo.currentText()

        # Asynchronous execution thread
        self.worker_thread = AIWorkerThread(query, mode, extra_context)
        self.worker_thread.response_ready.connect(self.on_ai_response)
        self.worker_thread.error_occurred.connect(self.on_ai_error)
        self.worker_thread.start()

    @Slot(str)
    def on_ai_response(self, response_text: str):
        self.progress_bar.hide()
        self.send_btn.setEnabled(True)
        self.append_tutor_message(response_text)

    @Slot(str)
    def on_ai_error(self, err_msg: str):
        self.progress_bar.hide()
        self.send_btn.setEnabled(True)
        self.append_tutor_message(f"⚠️ **Notice**: {err_msg}")
