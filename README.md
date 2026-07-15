# ⚡ ElectroVerse — Virtual Engineering Lab

[![Python Version](https://img.shields.counts/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.counts/badge/UI-PySide6-cyan.svg)](https://doc.qt.io/qtforpython-6/)
[![License](https://img.shields.counts/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

**ElectroVerse** is a modern, laboratory-grade interactive desktop application designed for students, educators, and electrical engineers. It bridges the gap between theoretical electronics and practical laboratory experiments by providing real-time solvers, interactive simulators, a comprehensive component database, and a high-performance virtual oscilloscope.

---

## 🚀 Key Features & Workflow

ElectroVerse is organized in a natural engineering learning flow to take users from theory to design and analysis:

### 1. 🏠 Dashboard
The command center of ElectroVerse. Featuring quick shortcuts, interactive system status statistics, and a sleek neon user interface that guides your session flow.

### 2. 📚 Component Library
A comprehensive, professional-grade electronic component database with deep insights for dozens of components. Includes:
- **Specifications & Construction details** (Pins, materials, ratings)
- **Mathematical equations & Formulas** with variable explanations and SI units
- **Practical engineering tips** and **interview preparation questions**
- Cross-references to relevant simulations and experiments

### 3. 🎓 Learning Mode
A structured, multi-module academic curriculum (from Basic passive elements to Semiconductors, Analog, and Digital Logic circuits). 
- **Context-Aware Navigation**: Automatically offers direct shortcuts to open components in the Component Library or test circuits in the Simulation Lab based on your current lesson.
- **LaTeX Math Equations**: Standard mathematical notations are fully rendered for clean, readable formulas.

### 4. 🛠 Engineering Toolkit
A suite of interactive engineering calculators to perform quick circuit design math:
- Ohm's Law & DC Power calculators
- Resistor network designs (Voltage & Current Dividers)
- LED Current-Limiting Resistor sizing
- Impedance explorers (Capacitive & Inductive Reactance)
- RC & RL time constants, RLC resonance solvers

### 5. 🧪 Simulation Lab
Real-time, interactive physical simulations built with high-performance mathematical solvers. Toggle parameters (frequency, resistance, capacitance, inductance) and watch the response adapt instantly:
- **Transients**: RC & RL charging/discharging curves
- **Resonance**: RLC series/parallel resonance with impedance and phase angle sweeps
- **Power**: Half-wave & Full-wave rectifiers
- **Signal Shaping**: Positive/Negative clippers, clampers, and attenuation networks

### 6. 📈 Digital Oscilloscope
A laboratory-grade, dual-channel virtual DSO (Digital Storage Oscilloscope). Capture, scale, offset, and measure simulated waveforms in real time. Perfect for analyzing rectifier outputs, phase shifts, and transient curves.

### 7. 📄 PDF Report Generator
Document your findings. Instantly compile your simulation settings, calculations, and analysis notes into a beautifully structured, ready-to-share PDF report.

### 8. ⚙️ Settings
Customize your workspace with theme adjustments (including premium dark modes) and manage configuration defaults.

---

## 🛠 Tech Stack

ElectroVerse is built upon high-performance Python libraries for numerical computing and visual rendering:
- **GUI Engine**: [PySide6](https://doc.qt.io/qtforpython-6/) (Qt 6 for Python) for a premium, hardware-accelerated desktop interface.
- **Plotting Engine**: [PyQtGraph](https://www.pyqtgraph.org/) for fluid, 60fps real-time waveform plotting.
- **Mathematical Solvers**: [NumPy](https://numpy.org/) & [SciPy](https://scipy.org/) for differential equations and transient simulation solvers.
- **Visualizations**: [Matplotlib](https://matplotlib.org/) for detailed sweep analytics.
- **Document Generation**: [ReportLab](https://www.reportlab.com/) for compiler-grade PDF reporting.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.8 or higher installed on your machine.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/electroverse.git
   cd electroverse
   ```

2. **Set up a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch ElectroVerse:**
   ```bash
   python main.py
   ```

---

## 💡 Why You'll Love ElectroVerse

- **No Dummy Content**: Zero placeholder equations or fake values. All lessons, formulas, SI units, and guidelines are fully audited and technically correct.
- **Fluid Visual Interactivity**: Drag sliders in the Simulation Lab and see the oscilloscope waves recalculate and replot instantly.
- **Professional Aesthetics**: Sleek Slate-900 backgrounds, cyber-neon cyan, emerald green accents, and custom font loading.
- **Offline First**: All component databases and calculators run locally with zero network requests needed.
