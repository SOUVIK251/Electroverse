from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QRadioButton, QButtonGroup, QScrollArea, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt
import qtawesome as qta

class SignalsAssessmentWidget(QWidget):
    """Interactive Assessment Suite for Signals & Systems.
    
    Includes:
    - MCQ Practice Quiz Bank with auto-grading
    - Numerical Problem Exercises
    - University / Technical Interview Q&A
    - Difficulty Filtering (Easy, Medium, Hard)
    - Live Score & Progress Tracking
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.score = 0
        self.total_attempted = 0
        
        self.quiz_data = [
            {
                "question": "1. What is the fundamental period T0 of the signal x(t) = 5 cos(10 pi t + pi/4)?",
                "options": ["0.1 s", "0.2 s", "0.5 s", "1.0 s"],
                "correct": 1,
                "explanation": "w0 = 10 pi => T0 = 2 pi / w0 = 2 pi / (10 pi) = 0.2 seconds.",
                "difficulty": "Easy"
            },
            {
                "question": "2. If a signal x(t) has energy E, what is the energy of y(t) = x(3t)?",
                "options": ["3 E", "E / 3", "9 E", "E / 9"],
                "correct": 1,
                "explanation": "Time scaling by factor a scales energy by E / |a|. Here a = 3, so E_y = E / 3.",
                "difficulty": "Medium"
            },
            {
                "question": "3. The continuous-time signal x(t) = e^(-2t) u(t) is an example of:",
                "options": ["Power Signal", "Energy Signal", "Neither Energy nor Power", "Both Energy and Power"],
                "correct": 1,
                "explanation": "E = integral_0^inf e^(-4t) dt = 1/4 Joules (finite), Average Power P = 0. Thus it is an Energy Signal.",
                "difficulty": "Easy"
            },
            {
                "question": "4. What is the continuous-time convolution of u(t) with u(t)?",
                "options": ["u(t)", "delta(t)", "r(t) = t u(t)", "t^2 u(t)"],
                "correct": 2,
                "explanation": "u(t) * u(t) = integral_0^t 1 dt = t u(t) = r(t) (Unit Ramp Function).",
                "difficulty": "Medium"
            },
            {
                "question": "5. According to the Nyquist Sampling Theorem, what is the Nyquist rate for x(t) = sin(400 pi t) + cos(1000 pi t)?",
                "options": ["500 Hz", "1000 Hz", "2000 Hz", "400 Hz"],
                "correct": 1,
                "explanation": "f_max = 1000 pi / (2 pi) = 500 Hz. Nyquist Rate f_s >= 2 * f_max = 2 * 500 = 1000 Hz.",
                "difficulty": "Medium"
            },
            {
                "question": "6. For a causal LTI system to be BIBO stable, where must its s-plane poles lie?",
                "options": ["On the jw axis", "Entirely in the Left-Half s-Plane (LHP)", "In the Right-Half s-Plane (RHP)", "Anywhere in the s-plane"],
                "correct": 1,
                "explanation": "Stability for a causal system requires all poles of H(s) to lie strictly in the LHP (Re{s} < 0).",
                "difficulty": "Hard"
            },
            {
                "question": "7. What is the Z-transform of x[n] = a^n u[n] and its ROC?",
                "options": ["z / (z - a), |z| > |a|", "z / (z - a), |z| < |a|", "1 / (z - a), |z| > 1", "z / (z + a), |z| < 1"],
                "correct": 0,
                "explanation": "Z{a^n u[n]} = z / (z - a) = 1 / (1 - a z^-1) with causal ROC |z| > |a|.",
                "difficulty": "Medium"
            },
            {
                "question": "8. What is the Initial Value Theorem for the Laplace Transform X(s)?",
                "options": ["lim_{t->0} x(t) = lim_{s->0} s X(s)", "lim_{t->0} x(t) = lim_{s->inf} s X(s)", "lim_{t->0} x(t) = lim_{s->inf} X(s)", "lim_{t->0} x(t) = 0"],
                "correct": 1,
                "explanation": "Initial Value Theorem states lim_{t->0+} x(t) = lim_{s->inf} s X(s).",
                "difficulty": "Hard"
            }
        ]
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(10)

        # Top Score Banner
        score_card = QFrame()
        score_card.setObjectName("card-panel")
        score_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-top: 3px solid #10B981; border-radius: 10px; padding: 12px; }")
        s_lay = QHBoxLayout(score_card)
        
        self.score_lbl = QLabel("🎯 Assessment Mastery Score: 0 / 0 (0%)")
        self.score_lbl.setStyleSheet("color: #FFFFFF; font-size: 12pt; font-weight: bold;")
        
        self.diff_filter = QComboBox()
        self.diff_filter.addItems(["All Difficulty Levels", "Easy", "Medium", "Hard"])
        self.diff_filter.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFFFFF; padding: 5px; border-radius: 6px;")
        self.diff_filter.currentIndexChanged.connect(self.reload_questions)

        s_lay.addWidget(self.score_lbl)
        s_lay.addStretch()
        s_lay.addWidget(QLabel("Filter Difficulty:", styleSheet="color: #94A3B8;"))
        s_lay.addWidget(self.diff_filter)
        main_layout.addWidget(score_card)

        # Questions Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.q_container = QWidget()
        self.q_layout = QVBoxLayout(self.q_container)
        self.q_layout.setSpacing(15)

        scroll.setWidget(self.q_container)
        main_layout.addWidget(scroll, 1)

        self.reload_questions()

    def reload_questions(self):
        while self.q_layout.count():
            item = self.q_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        selected_diff = self.diff_filter.currentText()

        for idx, q_data in enumerate(self.quiz_data):
            if selected_diff != "All Difficulty Levels" and q_data["difficulty"] != selected_diff:
                continue

            card = QFrame()
            card.setObjectName("card-panel")
            card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
            c_lay = QVBoxLayout(card)

            top_row = QHBoxLayout()
            q_lbl = QLabel(q_data["question"])
            q_lbl.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F8FAFC;")
            q_lbl.setWordWrap(True)
            
            diff_lbl = QLabel(q_data["difficulty"])
            diff_color = "#10B981" if q_data["difficulty"] == "Easy" else ("#F59E0B" if q_data["difficulty"] == "Medium" else "#EF4444")
            diff_lbl.setStyleSheet(f"background-color: {diff_color}; color: #FFFFFF; font-weight: bold; font-size: 8pt; padding: 2px 8px; border-radius: 4px;")

            top_row.addWidget(q_lbl, 1)
            top_row.addWidget(diff_lbl)
            c_lay.addLayout(top_row)

            # Options Group
            btn_group = QButtonGroup(card)
            opt_widgets = []

            for o_idx, opt_text in enumerate(q_data["options"]):
                radio = QRadioButton(opt_text)
                radio.setStyleSheet("QRadioButton { color: #CBD5E1; font-size: 10pt; padding: 4px; } QRadioButton:hover { color: #FFFFFF; }")
                btn_group.addButton(radio, o_idx)
                c_lay.addWidget(radio)
                opt_widgets.append(radio)

            exp_lbl = QLabel(f"💡 **Explanation**: {q_data['explanation']}")
            exp_lbl.setStyleSheet("color: #34D399; font-size: 9.5pt; background-color: #09121E; padding: 8px; border-radius: 6px; margin-top: 6px;")
            exp_lbl.setWordWrap(True)
            exp_lbl.setVisible(False)
            c_lay.addWidget(exp_lbl)

            submit_btn = QPushButton("Submit Answer")
            submit_btn.setStyleSheet("QPushButton { background-color: #2563EB; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 6px 14px; max-width: 140px; } QPushButton:hover { background-color: #3B82F6; }")

            def make_checker(group, correct_idx, expl_label, s_btn):
                def check():
                    sel = group.checkedId()
                    if sel == -1:
                        return
                    s_btn.setEnabled(False)
                    expl_label.setVisible(True)
                    self.total_attempted += 1
                    if sel == correct_idx:
                        self.score += 1
                        s_btn.setText("✓ Correct!")
                        s_btn.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 6px 14px;")
                    else:
                        s_btn.setText("✗ Incorrect")
                        s_btn.setStyleSheet("background-color: #EF4444; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 6px 14px;")
                    
                    pct = (self.score / self.total_attempted) * 100 if self.total_attempted > 0 else 0
                    self.score_lbl.setText(f"🎯 Assessment Mastery Score: {self.score} / {self.total_attempted} ({pct:.1f}%)")
                return check

            submit_btn.clicked.connect(make_checker(btn_group, q_data["correct"], exp_lbl, submit_btn))
            c_lay.addWidget(submit_btn)

            self.q_layout.addWidget(card)
