from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QRadioButton,
    QCheckBox, QButtonGroup, QLineEdit, QSplitter
)
from PySide6.QtCore import Qt, Signal

class QuestionCard(QWidget):
    """Multi-Format Question Renderer (LaTeX formulas, diagrams, MCQ/TrueFalse/FillBlank)."""

    answer_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_q = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Question Header Card
        self.q_card = QFrame()
        self.q_card.setObjectName("card-panel")
        self.q_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
        q_lay = QVBoxLayout(self.q_card)

        # Question Meta Row
        meta_row = QHBoxLayout()
        self.num_lbl = QLabel("Question 1 / 30")
        self.num_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 11pt;")
        
        self.bloom_lbl = QLabel("Level: Understand")
        self.bloom_lbl.setStyleSheet("color: #94A3B8; font-size: 9pt;")
        
        self.diff_lbl = QLabel("Easy")
        self.diff_lbl.setStyleSheet("background-color: #10B981; color: #FFF; font-weight: bold; font-size: 8pt; padding: 2px 8px; border-radius: 4px;")

        meta_row.addWidget(self.num_lbl)
        meta_row.addWidget(self.bloom_lbl)
        meta_row.addStretch()
        meta_row.addWidget(self.diff_lbl)
        q_lay.addLayout(meta_row)

        # Question Text
        self.q_text_lbl = QLabel()
        self.q_text_lbl.setStyleSheet("color: #F8FAFC; font-size: 11pt; font-weight: 600; line-height: 1.4; padding-top: 6px;")
        self.q_text_lbl.setWordWrap(True)
        q_lay.addWidget(self.q_text_lbl)

        # Formula Banner (LaTeX style)
        self.formula_card = QFrame()
        self.formula_card.setStyleSheet("background-color: #0F172A; border: 1px solid #06B6D4; border-radius: 6px; padding: 8px;")
        f_lay = QVBoxLayout(self.formula_card)
        self.formula_lbl = QLabel()
        self.formula_lbl.setStyleSheet("color: #38BDF8; font-weight: bold; font-family: Consolas, monospace; font-size: 11pt;")
        f_lay.addWidget(self.formula_lbl)
        self.formula_card.setVisible(False)
        q_lay.addWidget(self.formula_card)

        layout.addWidget(self.q_card)

        # Options Container
        self.opts_card = QFrame()
        self.opts_card.setObjectName("card-panel")
        self.opts_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
        self.opts_lay = QVBoxLayout(self.opts_card)
        layout.addWidget(self.opts_card, 1)

    def display_question(self, q_data, q_num, total_q, current_ans=None):
        self.current_q = q_data

        self.num_lbl.setText(f"Question {q_num} of {total_q}")
        self.q_text_lbl.setText(q_data.get("question", ""))
        self.bloom_lbl.setText(f"Bloom Level: {q_data.get('bloom_level', 'Understand')}")

        diff = q_data.get("difficulty", "Easy")
        diff_color = "#10B981" if diff == "Easy" else ("#F59E0B" if diff == "Medium" else "#EF4444")
        self.diff_lbl.setText(diff)
        self.diff_lbl.setStyleSheet(f"background-color: {diff_color}; color: #FFF; font-weight: bold; font-size: 8pt; padding: 2px 8px; border-radius: 4px;")

        # Formula display
        formula = q_data.get("formula", "")
        if formula:
            self.formula_lbl.setText(f"LaTeX Equation: {formula}")
            self.formula_card.setVisible(True)
        else:
            self.formula_card.setVisible(False)

        # Clear old options
        while self.opts_lay.count():
            item = self.opts_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        opts = q_data.get("options", [])
        q_type = q_data.get("question_type", "single_mcq")

        if q_type in ["single_mcq", "true_false"]:
            btn_group = QButtonGroup(self.opts_card)
            for idx, opt_text in enumerate(opts):
                radio = QRadioButton(opt_text)
                radio.setStyleSheet("QRadioButton { color: #CBD5E1; font-size: 10.5pt; padding: 6px; } QRadioButton:hover { color: #FFF; }")
                btn_group.addButton(radio, idx)
                self.opts_lay.addWidget(radio)

                if current_ans is not None and isinstance(current_ans, list) and len(current_ans) > 0 and current_ans[0] == idx:
                    radio.setChecked(True)

            btn_group.idClicked.connect(lambda b_id: self.answer_changed.emit([b_id]))

        elif q_type == "multiple_correct":
            cb_list = []
            for idx, opt_text in enumerate(opts):
                cb = QCheckBox(opt_text)
                cb.setStyleSheet("QCheckBox { color: #CBD5E1; font-size: 10.5pt; padding: 6px; } QCheckBox:hover { color: #FFF; }")
                self.opts_lay.addWidget(cb)
                cb_list.append((idx, cb))

                if current_ans is not None and isinstance(current_ans, list) and idx in current_ans:
                    cb.setChecked(True)

                def make_cb_handler():
                    def on_toggled(checked):
                        sel = [i for i, c in cb_list if c.isChecked()]
                        self.answer_changed.emit(sel)
                    return on_toggled

                cb.toggled.connect(make_cb_handler())

        elif q_type in ["fill_blank", "formula_based"]:
            txt_in = QLineEdit()
            txt_in.setPlaceholderText("Enter your numerical or formula answer here...")
            txt_in.setStyleSheet("QLineEdit { background-color: #0F172A; border: 1px solid #26334D; color: #FFF; padding: 10px; border-radius: 6px; font-size: 11pt; }")
            if current_ans is not None and isinstance(current_ans, list) and len(current_ans) > 0:
                txt_in.setText(str(current_ans[0]))
            txt_in.textChanged.connect(lambda val: self.answer_changed.emit([val.strip()]))
            self.opts_lay.addWidget(txt_in)

    def clear_selection(self):
        self.display_question(self.current_q, 1, 30, current_ans=None)
        self.answer_changed.emit([])
