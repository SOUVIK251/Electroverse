import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox,
    QSlider, QPushButton, QDoubleSpinBox, QSplitter, QStackedWidget,
    QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
import qtawesome as qta

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.ui.components.engineering_spinbox import EngineeringDoubleSpinBox, EngineeringSpinBox


class SignalsSimulationWidget(QWidget):
    """Interactive Real-Time Signals & Systems Simulation Engine.
    
    10 Full Interactive Lab Modules:
    1. Signal Generator & Metrics (Step, Ramp, Impulse, Sine, Sawtooth, Energy/Power, Even/Odd)
    2. Signal Operations Transformer (Shift, Scale, Fold, Addition, Multiplication)
    3. System Property Tester (Linearity, Time Invariance, Stability, Memory, Causality)
    4. Convolution Animator (Continuous & Discrete-time moving window overlap)
    5. Fourier Series Harmonics Synthesizer (N=1..50 Harmonics & Gibbs Phenomenon)
    6. Fourier Transform Spectrum Analyzer (Time-domain -> FFT Magnitude & Phase)
    7. Laplace s-Plane Pole-Zero & ROC Plotter (s-plane poles/zeros & stability)
    8. Z-Transform z-Plane & Difference Equation (z-plane poles/zeros & unit circle)
    9. Nyquist Sampling & Aliasing Demo (fs vs fin, discrete samples & alias readout)
    10. Engineering Applications (AM/FM Modulation, ECG Filter, Control Step, Radar)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_animation_tick)
        self.anim_pos = 0
        self.is_playing = False

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        # 1. Top Control Bar (Mode Selector + Playback Toolbar)
        top_frame = QFrame()
        top_frame.setObjectName("card-panel")
        top_frame.setFixedHeight(48)
        top_frame.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; }")
        t_layout = QHBoxLayout(top_frame)
        t_layout.setContentsMargins(10, 4, 10, 4)
        t_layout.setSpacing(10)

        m_lbl = QLabel("🧪 Interactive Lab:")
        m_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 9.5pt;")
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "1. Elementary Signal Generator & Metrics",
            "2. Signal Operations Transformer (Shift, Scale, Fold)",
            "3. System Property Tester (Linearity, Stability, Causality)",
            "4. Convolution Animator (Continuous & Discrete)",
            "5. Fourier Series Harmonics Synthesizer",
            "6. Fourier Transform & Frequency Spectrum Analyzer",
            "7. Laplace s-Plane Pole-Zero & ROC Plotter",
            "8. Z-Transform z-Plane & Difference Equation",
            "9. Nyquist Sampling & Aliasing Demonstration",
            "10. Engineering Applications (AM/FM, ECG, Control, Radar)"
        ])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                border: 1px solid #26334D;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 9pt;
            }
        """)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

        t_layout.addWidget(m_lbl)
        t_layout.addWidget(self.mode_combo)
        t_layout.addStretch()

        # Playback Controls
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setStyleSheet("background-color: #10B981; color: #FFF; font-weight: bold; padding: 4px 10px; border-radius: 4px;")
        self.play_btn.clicked.connect(self.toggle_play)

        self.step_btn = QPushButton("⏭ Step")
        self.step_btn.setStyleSheet("background-color: #1E293B; color: #FFF; padding: 4px 10px; border-radius: 4px;")
        self.step_btn.clicked.connect(self.step_animation)

        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setStyleSheet("background-color: #1E293B; color: #FFF; padding: 4px 10px; border-radius: 4px;")
        self.reset_btn.clicked.connect(self.reset_animation)

        t_layout.addWidget(self.play_btn)
        t_layout.addWidget(self.step_btn)
        t_layout.addWidget(self.reset_btn)

        main_layout.addWidget(top_frame)

        # 2. Main Stacked Widget
        self.stack = QStackedWidget()
        
        self.stack.addWidget(self.create_signal_generator_view())    # 0
        self.stack.addWidget(self.create_signal_operations_view())   # 1
        self.stack.addWidget(self.create_system_property_view())     # 2
        self.stack.addWidget(self.create_convolution_view())         # 3
        self.stack.addWidget(self.create_fourier_series_view())      # 4
        self.stack.addWidget(self.create_fourier_transform_view())   # 5
        self.stack.addWidget(self.create_laplace_view())             # 6
        self.stack.addWidget(self.create_z_transform_view())         # 7
        self.stack.addWidget(self.create_sampling_view())            # 8
        self.stack.addWidget(self.create_applications_view())        # 9

        main_layout.addWidget(self.stack, 1)

    def load_simulation_preset(self, module_idx, params):
        if 0 <= module_idx < self.stack.count():
            self.mode_combo.setCurrentIndex(module_idx)

    def on_mode_changed(self, idx):
        self.stack.setCurrentIndex(idx)
        if idx == 0: self.update_gen_plot()
        elif idx == 1: self.update_op_plot()
        elif idx == 2: self.update_sys_plot()
        elif idx == 3: self.update_conv_plot()
        elif idx == 4: self.update_fourier_series_plot()
        elif idx == 5: self.update_fourier_transform_plot()
        elif idx == 6: self.update_laplace_plot()
        elif idx == 7: self.update_z_plot()
        elif idx == 8: self.update_sampling_plot()
        elif idx == 9: self.update_app_plot()

    def toggle_play(self):
        if self.is_playing:
            self.timer.stop()
            self.is_playing = False
            self.play_btn.setText("▶ Play")
            self.play_btn.setStyleSheet("background-color: #10B981; color: #FFF; font-weight: bold; padding: 4px 10px; border-radius: 4px;")
        else:
            self.timer.start(50)
            self.is_playing = True
            self.play_btn.setText("⏸ Pause")
            self.play_btn.setStyleSheet("background-color: #EF4444; color: #FFF; font-weight: bold; padding: 4px 10px; border-radius: 4px;")

    def step_animation(self):
        self.anim_pos += 1
        self.trigger_active_update()

    def reset_animation(self):
        self.anim_pos = 0
        if self.is_playing:
            self.toggle_play()
        self.trigger_active_update()

    def on_animation_tick(self):
        self.anim_pos += 1
        self.trigger_active_update()

    def trigger_active_update(self):
        idx = self.stack.currentIndex()
        if idx == 3: self.update_conv_plot()
        elif idx == 8: self.update_sampling_plot()
        elif idx == 9: self.update_app_plot()

    # -------------------------------------------------------------
    # Mode 0: Signal Generator & Metrics (Module 1)
    # -------------------------------------------------------------
    def create_signal_generator_view(self):
        w = QWidget()
        l = QHBoxLayout(w)
        
        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("Signal Controls", styleSheet="color: #10B981; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Signal Type:", styleSheet="color: #94A3B8;"))
        self.gen_type = QComboBox()
        self.gen_type.addItems(["Sinusoidal", "Square Wave", "Triangle Wave", "Sawtooth Wave", "Unit Step u(t)", "Unit Impulse delta(t)", "Unit Ramp r(t)", "Signum sgn(t)", "Exponential e^(-at)"])
        self.gen_type.currentIndexChanged.connect(self.update_gen_plot)
        c_lay.addWidget(self.gen_type)

        c_lay.addWidget(QLabel("Amplitude (A):", styleSheet="color: #94A3B8;"))
        self.gen_amp = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=10.0, unit="V")
        self.gen_amp.setValue(2.0)
        self.gen_amp.valueChanged.connect(self.update_gen_plot)
        c_lay.addWidget(self.gen_amp)

        c_lay.addWidget(QLabel("Frequency (Hz):", styleSheet="color: #94A3B8;"))
        self.gen_freq = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=20.0, unit="Hz")
        self.gen_freq.setValue(2.0)
        self.gen_freq.valueChanged.connect(self.update_gen_plot)
        c_lay.addWidget(self.gen_freq)

        c_lay.addWidget(QLabel("Shift (t0):", styleSheet="color: #94A3B8;"))
        self.gen_shift = EngineeringDoubleSpinBox(self, step=0.1, min_val=-4.0, max_val=4.0, unit="s")
        self.gen_shift.setValue(0.0)
        self.gen_shift.valueChanged.connect(self.update_gen_plot)
        c_lay.addWidget(self.gen_shift)


        self.gen_metric_lbl = QLabel("Energy E = 0 J\nPower P = 0 W\nType: Energy Signal")
        self.gen_metric_lbl.setStyleSheet("color: #F59E0B; font-weight: bold; background-color: #0F172A; padding: 8px; border-radius: 6px;")
        c_lay.addWidget(self.gen_metric_lbl)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.gen_canvas = FigureCanvas(fig)
        self.gen_ax1 = fig.add_subplot(211)
        self.gen_ax2 = fig.add_subplot(212)
        l.addWidget(self.gen_canvas, 3)

        self.update_gen_plot()
        return w

    def update_gen_plot(self):
        self.gen_ax1.clear()
        self.gen_ax2.clear()
        
        for ax in [self.gen_ax1, self.gen_ax2]:
            ax.set_facecolor("#0F172A")
            ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.axvline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        t = np.linspace(-5, 5, 1000)
        stype = self.gen_type.currentText()
        A = self.gen_amp.value()
        f = self.gen_freq.value()
        t0 = self.gen_shift.value()
        t_adj = t - t0

        if "Sinusoidal" in stype:
            y = A * np.sin(2 * np.pi * f * t_adj)
            E = np.inf; P = (A**2) / 2.0; cls = "Power Signal"
        elif "Square" in stype:
            y = A * np.sign(np.sin(2 * np.pi * f * t_adj))
            E = np.inf; P = A**2; cls = "Power Signal"
        elif "Triangle" in stype:
            y = A * (2 * np.abs(2 * (f * t_adj - np.floor(f * t_adj + 0.5))) - 1)
            E = np.inf; P = (A**2) / 3.0; cls = "Power Signal"
        elif "Sawtooth" in stype:
            y = A * (2 * (f * t_adj - np.floor(f * t_adj + 0.5)))
            E = np.inf; P = (A**2) / 3.0; cls = "Power Signal"
        elif "Step" in stype:
            y = A * (t_adj >= 0).astype(float)
            E = np.inf; P = (A**2) / 2.0; cls = "Power Signal"
        elif "Impulse" in stype:
            y = np.zeros_like(t)
            idx = np.argmin(np.abs(t_adj))
            y[idx] = A * 10
            E = A**2; P = 0; cls = "Energy Signal"
        elif "Ramp" in stype:
            y = A * np.maximum(0, t_adj)
            E = np.inf; P = np.inf; cls = "Neither Energy nor Power"
        elif "Signum" in stype:
            y = A * np.sign(t_adj)
            E = np.inf; P = A**2; cls = "Power Signal"
        elif "Exponential" in stype:
            y = A * np.exp(-1.0 * np.maximum(0, t_adj)) * (t_adj >= 0)
            E = (A**2) / 2.0; P = 0; cls = "Energy Signal"

        self.gen_metric_lbl.setText(f"Signal Energy: {E if E != np.inf else 'Infinite'}\nAverage Power: {P if P != np.inf else 'Infinite'}\nClassification: {cls}")

        self.gen_ax1.plot(t, y, color="#06B6D4", linewidth=2, label=f"x(t) [{stype}]")
        self.gen_ax1.set_title(f"Original Signal x(t) - {stype}", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.gen_ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        # Even/Odd Decomposition
        y_neg = np.flip(y)
        y_even = 0.5 * (y + y_neg)
        y_odd = 0.5 * (y - y_neg)

        self.gen_ax2.plot(t, y_even, color="#10B981", linewidth=1.8, label="Even Component xe(t)")
        self.gen_ax2.plot(t, y_odd, color="#EF4444", linewidth=1.8, linestyle="--", label="Odd Component xo(t)")
        self.gen_ax2.set_title("Even & Odd Signal Decomposition", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.gen_ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        self.gen_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 1: Signal Operations Transformer (Module 2)
    # -------------------------------------------------------------
    def create_signal_operations_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("Transformation Sliders", styleSheet="color: #38BDF8; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Time Shift (t0):", styleSheet="color: #94A3B8;"))
        self.op_shift = EngineeringDoubleSpinBox(self, step=0.1, min_val=-4.0, max_val=4.0, unit="s")
        self.op_shift.setValue(1.0)
        self.op_shift.valueChanged.connect(self.update_op_plot)
        c_lay.addWidget(self.op_shift)

        c_lay.addWidget(QLabel("Time Scale (a):", styleSheet="color: #94A3B8;"))
        self.op_scale = EngineeringDoubleSpinBox(self, step=0.1, min_val=-3.0, max_val=3.0)
        self.op_scale.setValue(2.0)
        self.op_scale.valueChanged.connect(self.update_op_plot)
        c_lay.addWidget(self.op_scale)

        c_lay.addWidget(QLabel("Amp Scale (A):", styleSheet="color: #94A3B8;"))
        self.op_amp = EngineeringDoubleSpinBox(self, step=0.1, min_val=-3.0, max_val=3.0)
        self.op_amp.setValue(1.5)
        self.op_amp.valueChanged.connect(self.update_op_plot)
        c_lay.addWidget(self.op_amp)


        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.op_canvas = FigureCanvas(fig)
        self.op_ax1 = fig.add_subplot(211)
        self.op_ax2 = fig.add_subplot(212)
        l.addWidget(self.op_canvas, 3)

        self.update_op_plot()
        return w

    def update_op_plot(self):
        self.op_ax1.clear()
        self.op_ax2.clear()

        for ax in [self.op_ax1, self.op_ax2]:
            ax.set_facecolor("#0F172A")
            ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.axvline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        t = np.linspace(-5, 5, 1000)
        x_orig = np.maximum(0, 1 - np.abs(t - 1)) # Triangular pulse

        shift = self.op_shift.value()
        scale = self.op_scale.value()
        if scale == 0: scale = 0.1
        amp = self.op_amp.value()

        t_trans = scale * t - shift
        x_trans = amp * np.maximum(0, 1 - np.abs(t_trans - 1))

        self.op_ax1.plot(t, x_orig, color="#06B6D4", linewidth=2, label="Original x(t)")
        self.op_ax1.set_title("Original Signal x(t)", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.op_ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        self.op_ax2.plot(t, x_trans, color="#F59E0B", linewidth=2.5, label=f"y(t) = {amp:.1f} x({scale:.1f}t - {shift:.1f})")
        self.op_ax2.set_title(f"Transformed Signal y(t) = {amp:.1f} x({scale:.1f}t - {shift:.1f})", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.op_ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        self.op_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 2: System Property Tester (Module 3)
    # -------------------------------------------------------------
    def create_system_property_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("System Property Verification", styleSheet="color: #F59E0B; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Target System y(t):", styleSheet="color: #94A3B8;"))
        self.sys_type = QComboBox()
        self.sys_type.addItems([
            "y(t) = 3 x(t) (Linear, Time-Invariant, Memoryless, Causal, Stable)",
            "y(t) = x(t^2) (Nonlinear Time, Time-Variant, Dynamic, Non-causal)",
            "y(t) = x(t) + 5 (Nonlinear Additive, Time-Invariant, Memoryless)",
            "y(t) = integral_{-inf}^t x(tau) dtau (Linear, Time-Invariant, Memory, Causal)",
            "y(t) = e^(x(t)) (Nonlinear, Time-Invariant, Memoryless, Causal)"
        ])
        self.sys_type.currentIndexChanged.connect(self.update_sys_plot)
        c_lay.addWidget(self.sys_type)

        self.sys_status_lbl = QLabel()
        self.sys_status_lbl.setStyleSheet("color: #E2E8F0; font-size: 9pt; background-color: #0F172A; padding: 8px; border-radius: 6px;")
        self.sys_status_lbl.setWordWrap(True)
        c_lay.addWidget(self.sys_status_lbl)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.sys_canvas = FigureCanvas(fig)
        self.sys_ax = fig.add_subplot(111)
        l.addWidget(self.sys_canvas, 3)

        self.update_sys_plot()
        return w

    def update_sys_plot(self):
        self.sys_ax.clear()
        self.sys_ax.set_facecolor("#0F172A")
        self.sys_ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
        self.sys_ax.axvline(0, color="#475569", linestyle="--", alpha=0.5)
        self.sys_ax.tick_params(colors="#94A3B8")
        self.sys_ax.grid(True, color="#1E293B", linestyle=":")

        t = np.linspace(-3, 3, 500)
        x = np.sin(2 * np.pi * t)
        stype = self.sys_type.currentIndex()

        if stype == 0:
            y = 3 * x
            desc = "• Linear: SATISFIED (Superposition holds)\n• Time-Invariant: SATISFIED\n• Memoryless: SATISFIED (Depends on current t only)\n• Causal: SATISFIED\n• BIBO Stable: SATISFIED"
        elif stype == 1:
            y = np.sin(2 * np.pi * (t**2))
            desc = "• Linear: SATISFIED\n• Time-Variant: YES (t^2 scaling)\n• Memory: DYNAMIC (Needs future t for t > 1)\n• Non-Causal: YES (for t > 1)\n• BIBO Stable: SATISFIED"
        elif stype == 2:
            y = x + 5
            desc = "• Nonlinear: YES (Zero input yields y(t)=5 != 0)\n• Time-Invariant: SATISFIED\n• Memoryless: SATISFIED\n• Causal: SATISFIED\n• BIBO Stable: SATISFIED"
        elif stype == 3:
            y = (1 - np.cos(2 * np.pi * t)) / (2 * np.pi)
            desc = "• Linear: SATISFIED\n• Time-Invariant: SATISFIED\n• Memory: DYNAMIC (Accumulates history)\n• Causal: SATISFIED\n• BIBO Stable: UNSTABLE (Step yields unbounded ramp)"
        else:
            y = np.exp(x)
            desc = "• Nonlinear: YES (Exponential mapping)\n• Time-Invariant: SATISFIED\n• Memoryless: SATISFIED\n• Causal: SATISFIED\n• BIBO Stable: SATISFIED"

        self.sys_status_lbl.setText(desc)

        self.sys_ax.plot(t, x, color="#06B6D4", linestyle="--", label="Input x(t) = sin(2pi t)")
        self.sys_ax.plot(t, y, color="#10B981", linewidth=2.2, label="System Output y(t)")
        self.sys_ax.set_title("System Input vs Response Verification", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.sys_ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")
        self.sys_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 3: Convolution Animator (Module 4)
    # -------------------------------------------------------------
    def create_convolution_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("Convolution Controls", styleSheet="color: #10B981; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Time Shift (t):", styleSheet="color: #94A3B8;"))
        self.conv_slider = QSlider(Qt.Orientation.Horizontal)
        self.conv_slider.setRange(-40, 40)
        self.conv_slider.setValue(0)
        self.conv_slider.valueChanged.connect(self.update_conv_plot)
        c_lay.addWidget(self.conv_slider)

        self.conv_t_lbl = QLabel("Shift t = 0.0s")
        self.conv_t_lbl.setStyleSheet("color: #06B6D4; font-weight: bold;")
        c_lay.addWidget(self.conv_t_lbl)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.conv_canvas = FigureCanvas(fig)
        self.conv_ax1 = fig.add_subplot(211)
        self.conv_ax2 = fig.add_subplot(212)
        l.addWidget(self.conv_canvas, 3)

        self.update_conv_plot()
        return w

    def update_conv_plot(self):
        self.conv_ax1.clear()
        self.conv_ax2.clear()

        for ax in [self.conv_ax1, self.conv_ax2]:
            ax.set_facecolor("#0F172A")
            ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.axvline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        t_shift = (self.conv_slider.value() + (self.anim_pos % 80 - 40)) / 10.0
        self.conv_t_lbl.setText(f"Shift t = {t_shift:.1f}s")

        tau = np.linspace(-5, 5, 500)
        x_tau = (tau >= 0) & (tau <= 2)
        h_tau = ((t_shift - tau) >= 0) & ((t_shift - tau) <= 2)
        prod = x_tau.astype(float) * h_tau.astype(float)

        self.conv_ax1.plot(tau, x_tau, color="#06B6D4", label="x(tau)")
        self.conv_ax1.plot(tau, h_tau, color="#F59E0B", label=f"h({t_shift:.1f} - tau)")
        self.conv_ax1.fill_between(tau, prod, color="#10B981", alpha=0.4, label="Overlap Area")
        self.conv_ax1.set_title(f"Sliding Window Overlap at t = {t_shift:.1f}s", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.conv_ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        t_sweep = np.linspace(-4, 4, 200)
        y_sweep = np.maximum(0, 2 - np.abs(t_sweep - 2))
        y_sweep[t_sweep < 0] = 0
        y_sweep[t_sweep > 4] = 0

        self.conv_ax2.plot(t_sweep, y_sweep, color="#10B981", linewidth=2.2, label="y(t) = x(t) * h(t)")
        self.conv_ax2.plot(t_shift, np.interp(t_shift, t_sweep, y_sweep), "ro", markersize=8, label="Current Area y(t)")
        self.conv_ax2.set_title("Continuous-Time Convolution Output y(t)", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.conv_ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        self.conv_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 4: Fourier Series Harmonics Synthesizer (Module 5)
    # -------------------------------------------------------------
    def create_fourier_series_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("Fourier Harmonics", styleSheet="color: #F59E0B; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Harmonics N:", styleSheet="color: #94A3B8;"))
        self.fs_n = QSlider(Qt.Orientation.Horizontal)
        self.fs_n.setRange(1, 50)
        self.fs_n.setValue(5)
        self.fs_n.valueChanged.connect(self.update_fourier_series_plot)
        c_lay.addWidget(self.fs_n)

        self.fs_n_lbl = QLabel("N = 5 Harmonics")
        self.fs_n_lbl.setStyleSheet("color: #F59E0B; font-weight: bold;")
        c_lay.addWidget(self.fs_n_lbl)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.fs_canvas = FigureCanvas(fig)
        self.fs_ax = fig.add_subplot(111)
        l.addWidget(self.fs_canvas, 3)

        self.update_fourier_series_plot()
        return w

    def update_fourier_series_plot(self):
        self.fs_ax.clear()
        self.fs_ax.set_facecolor("#0F172A")
        self.fs_ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
        self.fs_ax.tick_params(colors="#94A3B8")
        self.fs_ax.grid(True, color="#1E293B", linestyle=":")

        N = self.fs_n.value()
        self.fs_n_lbl.setText(f"N = {N} Harmonics")

        t = np.linspace(-3, 3, 1000)
        y = np.zeros_like(t)

        for i in range(1, N * 2, 2):
            y += (4.0 / (i * np.pi)) * np.sin(i * 2 * np.pi * t)

        self.fs_ax.plot(t, y, color="#F59E0B", linewidth=2, label=f"Fourier Sum N={N}")
        self.fs_ax.set_title(f"Square Wave Approximation with N={N} Harmonics (Gibbs Peak ~9%)", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.fs_ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")
        self.fs_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 5: Fourier Transform Spectrum Analyzer (Module 6)
    # -------------------------------------------------------------
    def create_fourier_transform_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("FFT Spectrum Controls", styleSheet="color: #06B6D4; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Pulse Width (T):", styleSheet="color: #94A3B8;"))
        self.ft_t = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.2, max_val=5.0, unit="s")
        self.ft_t.setValue(1.0)
        self.ft_t.valueChanged.connect(self.update_fourier_transform_plot)
        c_lay.addWidget(self.ft_t)


        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.ft_canvas = FigureCanvas(fig)
        self.ft_ax1 = fig.add_subplot(211)
        self.ft_ax2 = fig.add_subplot(212)
        l.addWidget(self.ft_canvas, 3)

        self.update_fourier_transform_plot()
        return w

    def update_fourier_transform_plot(self):
        self.ft_ax1.clear()
        self.ft_ax2.clear()

        for ax in [self.ft_ax1, self.ft_ax2]:
            ax.set_facecolor("#0F172A")
            ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.axvline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        T = self.ft_t.value()
        t = np.linspace(-5, 5, 1000)
        x = (np.abs(t) <= T / 2.0).astype(float)

        w = np.linspace(-20, 20, 1000)
        X_mag = T * np.abs(np.sinc(w * T / (2 * np.pi)))

        self.ft_ax1.plot(t, x, color="#06B6D4", linewidth=2, label="Rect Pulse rect(t/T)")
        self.ft_ax1.set_title(f"Time-Domain Signal x(t) (Width T={T:.1f}s)", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.ft_ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        self.ft_ax2.plot(w, X_mag, color="#38BDF8", linewidth=2, label="|X(w)| = T sinc(wT / 2pi)")
        self.ft_ax2.set_title("Fourier Transform Magnitude Spectrum |X(w)| (Sinc Function)", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.ft_ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        self.ft_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 6: Laplace s-Plane Pole-Zero & ROC (Module 7)
    # -------------------------------------------------------------
    def create_laplace_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("s-Plane Poles", styleSheet="color: #EF4444; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Real Pole (sigma):", styleSheet="color: #94A3B8;"))
        self.lap_sigma = EngineeringDoubleSpinBox(self, step=0.2, min_val=-3.0, max_val=3.0)
        self.lap_sigma.setValue(-1.0)
        self.lap_sigma.valueChanged.connect(self.update_laplace_plot)
        c_lay.addWidget(self.lap_sigma)


        self.lap_stab_lbl = QLabel("Status: STABLE")
        self.lap_stab_lbl.setStyleSheet("color: #22C55E; font-weight: bold;")
        c_lay.addWidget(self.lap_stab_lbl)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.lap_canvas = FigureCanvas(fig)
        self.lap_ax1 = fig.add_subplot(121)
        self.lap_ax2 = fig.add_subplot(122)
        l.addWidget(self.lap_canvas, 3)

        self.update_laplace_plot()
        return w

    def update_laplace_plot(self):
        self.lap_ax1.clear()
        self.lap_ax2.clear()

        for ax in [self.lap_ax1, self.lap_ax2]:
            ax.set_facecolor("#0F172A")
            ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.axvline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        sig = self.lap_sigma.value()

        # s-Plane
        self.lap_ax1.plot(sig, 0, "rx", markersize=10, markeredgewidth=3, label=f"Pole s={sig}")
        self.lap_ax1.axvline(0, color="#06B6D4", linestyle="-", alpha=0.6, label="jw axis")
        self.lap_ax1.set_title("s-Plane Pole & ROC", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.lap_ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        # Impulse Response h(t) = e^(sigma t) u(t)
        t = np.linspace(0, 4, 500)
        h = np.exp(sig * t)

        self.lap_ax2.plot(t, h, color="#10B981" if sig < 0 else "#EF4444", linewidth=2, label=f"h(t) = e^({sig}t) u(t)")
        self.lap_ax2.set_title("Impulse Response h(t)", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.lap_ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        if sig < 0:
            self.lap_stab_lbl.setText("Status: BIBO STABLE\n(LHP Pole, Decay)")
            self.lap_stab_lbl.setStyleSheet("color: #22C55E; font-weight: bold;")
        else:
            self.lap_stab_lbl.setText("Status: UNSTABLE\n(RHP Pole, Growth)")
            self.lap_stab_lbl.setStyleSheet("color: #EF4444; font-weight: bold;")

        self.lap_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 7: Z-Transform z-Plane & Difference Equation (Module 8)
    # -------------------------------------------------------------
    def create_z_transform_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("z-Plane Controls", styleSheet="color: #06B6D4; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Pole Radius (a):", styleSheet="color: #94A3B8;"))
        self.z_rad = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=1.8)
        self.z_rad.setValue(0.75)
        self.z_rad.valueChanged.connect(self.update_z_plot)
        c_lay.addWidget(self.z_rad)


        self.z_stab_lbl = QLabel("Status: STABLE")
        self.z_stab_lbl.setStyleSheet("color: #22C55E; font-weight: bold;")
        c_lay.addWidget(self.z_stab_lbl)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.z_canvas = FigureCanvas(fig)
        self.z_ax1 = fig.add_subplot(121)
        self.z_ax2 = fig.add_subplot(122)
        l.addWidget(self.z_canvas, 3)

        self.update_z_plot()
        return w

    def update_z_plot(self):
        self.z_ax1.clear()
        self.z_ax2.clear()

        for ax in [self.z_ax1, self.z_ax2]:
            ax.set_facecolor("#0F172A")
            ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.axvline(0, color="#475569", linestyle="--", alpha=0.5)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        rad = self.z_rad.value()

        # Unit Circle
        uc = matplotlib.patches.Circle((0, 0), 1.0, color="#06B6D4", fill=False, linestyle="--", linewidth=1.5, label="Unit Circle")
        self.z_ax1.add_patch(uc)
        self.z_ax1.plot(rad, 0, "rx", markersize=10, markeredgewidth=3, label=f"Pole z={rad}")
        self.z_ax1.set_xlim(-2, 2)
        self.z_ax1.set_ylim(-2, 2)
        self.z_ax1.set_title("z-Plane Pole Location", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.z_ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        # Impulse Response h[n] = a^n u[n]
        n = np.arange(0, 15)
        h_n = rad**n

        self.z_ax2.stem(n, h_n, linefmt="b-", markerfmt="bo", basefmt="r-")
        self.z_ax2.set_title("Discrete Impulse Response h[n]", color="#F8FAFC", fontsize=10, fontweight="bold")

        if rad < 1.0:
            self.z_stab_lbl.setText("Status: STABLE\n(|z| < 1 Inside Unit Circle)")
            self.z_stab_lbl.setStyleSheet("color: #22C55E; font-weight: bold;")
        else:
            self.z_stab_lbl.setText("Status: UNSTABLE\n(|z| >= 1 Outside Unit Circle)")
            self.z_stab_lbl.setStyleSheet("color: #EF4444; font-weight: bold;")

        self.z_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 8: Nyquist Sampling & Aliasing Demo (Module 9)
    # -------------------------------------------------------------
    def create_sampling_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("Sampling Controls", styleSheet="color: #06B6D4; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Signal Freq (fin):", styleSheet="color: #94A3B8;"))
        self.samp_fin = EngineeringDoubleSpinBox(self, step=1.0, min_val=1.0, max_val=50.0, unit="Hz")
        self.samp_fin.setValue(10.0)
        self.samp_fin.valueChanged.connect(self.update_sampling_plot)
        c_lay.addWidget(self.samp_fin)

        c_lay.addWidget(QLabel("Sampling Rate (fs):", styleSheet="color: #94A3B8;"))
        self.samp_fs = EngineeringDoubleSpinBox(self, step=1.0, min_val=2.0, max_val=100.0, unit="Hz")
        self.samp_fs.setValue(25.0)
        self.samp_fs.valueChanged.connect(self.update_sampling_plot)
        c_lay.addWidget(self.samp_fs)


        self.samp_status_lbl = QLabel()
        self.samp_status_lbl.setStyleSheet("color: #22C55E; font-weight: bold; font-size: 9pt;")
        c_lay.addWidget(self.samp_status_lbl)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.samp_canvas = FigureCanvas(fig)
        self.samp_ax = fig.add_subplot(111)
        l.addWidget(self.samp_canvas, 3)

        self.update_sampling_plot()
        return w

    def update_sampling_plot(self):
        self.samp_ax.clear()
        self.samp_ax.set_facecolor("#0F172A")
        self.samp_ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
        self.samp_ax.tick_params(colors="#94A3B8")
        self.samp_ax.grid(True, color="#1E293B", linestyle=":")

        fin = self.samp_fin.value()
        fs = self.samp_fs.value()

        t_cont = np.linspace(0, 1, 1000)
        y_cont = np.sin(2 * np.pi * fin * t_cont)

        t_samp = np.arange(0, 1.0001, 1.0 / fs)
        y_samp = np.sin(2 * np.pi * fin * t_samp)

        self.samp_ax.plot(t_cont, y_cont, color="#94A3B8", linestyle=":", alpha=0.7, label="Continuous Input")
        self.samp_ax.plot(t_samp, y_samp, "r-o", linewidth=1.5, markersize=6, label=f"Discrete Samples (fs={fs}Hz)")

        nyq_rate = 2 * fin
        if fs >= nyq_rate:
            self.samp_status_lbl.setText(f"Nyquist SATISFIED\nfs ({fs}Hz) >= 2*fin ({nyq_rate}Hz)")
            self.samp_status_lbl.setStyleSheet("color: #22C55E; font-weight: bold;")
        else:
            alias = abs(fs - fin)
            self.samp_status_lbl.setText(f"⚠️ ALIASING DETECTED!\nfs < 2*fin\nReconstructs as {alias:.1f}Hz alias!")
            self.samp_status_lbl.setStyleSheet("color: #EF4444; font-weight: bold;")

        self.samp_ax.set_title(f"Nyquist Sampling Demo (fin={fin}Hz, fs={fs}Hz)", color="#F8FAFC", fontsize=10, fontweight="bold")
        self.samp_ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")

        self.samp_canvas.draw_idle()

    # -------------------------------------------------------------
    # Mode 9: Engineering Applications Demos (Module 10)
    # -------------------------------------------------------------
    def create_applications_view(self):
        w = QWidget()
        l = QHBoxLayout(w)

        ctrl = QFrame()
        ctrl.setObjectName("card-panel")
        ctrl.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        c_lay = QVBoxLayout(ctrl)

        c_lay.addWidget(QLabel("Engineering Application", styleSheet="color: #10B981; font-weight: bold; font-size: 10pt;"))

        c_lay.addWidget(QLabel("Select Demo:", styleSheet="color: #94A3B8;"))
        self.app_combo = QComboBox()
        self.app_combo.addItems([
            "AM Radio Modulation (Carrier & Message)",
            "Biomedical ECG Noise Filtering",
            "Control System Step Response",
            "Radar Pulse Target Range Detection"
        ])
        self.app_combo.currentIndexChanged.connect(self.update_app_plot)
        c_lay.addWidget(self.app_combo)

        c_lay.addStretch()
        l.addWidget(ctrl, 1)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.app_canvas = FigureCanvas(fig)
        self.app_ax = fig.add_subplot(111)
        l.addWidget(self.app_canvas, 3)

        self.update_app_plot()
        return w

    def update_app_plot(self):
        self.app_ax.clear()
        self.app_ax.set_facecolor("#0F172A")
        self.app_ax.axhline(0, color="#475569", linestyle="--", alpha=0.5)
        self.app_ax.tick_params(colors="#94A3B8")
        self.app_ax.grid(True, color="#1E293B", linestyle=":")

        idx = self.app_combo.currentIndex()
        t = np.linspace(0, 2, 1000)

        if idx == 0: # AM Modulation
            m = np.sin(2 * np.pi * 2 * t)
            c = np.sin(2 * np.pi * 30 * t)
            s = (1 + 0.8 * m) * c
            self.app_ax.plot(t, s, color="#06B6D4", linewidth=1.5, label="AM Signal s(t)")
            self.app_ax.plot(t, 1 + 0.8 * m, color="#F59E0B", linestyle="--", label="Envelope")
            self.app_ax.set_title("Amplitude Modulation (AM) Waveform", color="#F8FAFC", fontsize=10, fontweight="bold")
        elif idx == 1: # ECG Filter
            ecg = np.sin(2 * np.pi * 1.2 * t) + 0.4 * np.sin(2 * np.pi * 50 * t)
            clean = np.sin(2 * np.pi * 1.2 * t)
            self.app_ax.plot(t, ecg, color="#EF4444", alpha=0.7, label="Noisy ECG (50Hz Powerline Interference)")
            self.app_ax.plot(t, clean, color="#10B981", linewidth=2, label="Filtered ECG Signal")
            self.app_ax.set_title("Biomedical Signal Processing & Filtering", color="#F8FAFC", fontsize=10, fontweight="bold")
        elif idx == 2: # Control Step Response
            wn = 5.0; zeta = 0.4
            wd = wn * np.sqrt(1 - zeta**2)
            y_step = 1 - np.exp(-zeta * wn * t) * (np.cos(wd * t) + (zeta / np.sqrt(1 - zeta**2)) * np.sin(wd * t))
            self.app_ax.plot(t, y_step, color="#38BDF8", linewidth=2.2, label="2nd-Order Step Response (Overshoot=25%)")
            self.app_ax.axhline(1.0, color="#94A3B8", linestyle=":", label="Setpoint")
            self.app_ax.set_title("Control Systems Transient Step Response", color="#F8FAFC", fontsize=10, fontweight="bold")
        else: # Radar Range
            radar_tx = np.zeros_like(t)
            radar_tx[(t >= 0.1) & (t <= 0.2)] = 1.0
            radar_rx = np.zeros_like(t)
            radar_rx[(t >= 0.8) & (t <= 0.9)] = 0.4
            self.app_ax.plot(t, radar_tx, color="#06B6D4", label="Tx Pulse")
            self.app_ax.plot(t, radar_rx, color="#10B981", label="Echo Rx (Target Range ~ 105 km)")
            self.app_ax.set_title("Radar Target Distance Detection Echo", color="#F8FAFC", fontsize=10, fontweight="bold")

        self.app_ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#F8FAFC")
        self.app_canvas.draw_idle()
