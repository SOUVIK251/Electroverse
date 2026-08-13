# ⚡ ElectroVerse — Virtual Engineering Laboratory

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-PySide6%20%2F%20Qt6-cyan.svg)](https://doc.qt.io/qtforpython-6/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Theme](https://img.shields.io/badge/Theme-Laboratory%20Suite-blueviolet.svg)](#-premium-engineering-laboratory-theme)
[![Author](https://img.shields.io/badge/Author-Souvik%20Kundu-brightgreen.svg)](https://github.com/SOUVIK251)

> **Created & Lead Developed by [Souvik Kundu](https://github.com/SOUVIK251)**  
> *Designed to make offline electronics engineering education intuitive, visual, interactive, and accessible.*

**ElectroVerse** is a modern, laboratory-grade interactive desktop application designed for students, educators, and electrical engineers. Inspired by professional software suites like **NI Multisim**, **Keysight BenchVue**, and **MATLAB App Designer**, it combines digital logic design, 2D solderless breadboard simulation, 2,200+ viva voce prep questions, ECE/CSE textbook lessons, real-time circuit transient solvers, and interactive waveform visualizers into a unified offline desktop suite.

---

## 🌟 Key Modules & Features

### 1. 🌊 Analog Electronics Circuit Hub
A master learning and simulation platform for Analog Electronics aligned with ElectroVerse's standardized 5-tab hub architecture:
- **📖 Learn (Interactive Textbook)**: Course Roadmap progress header, 25% Sidebar | 75% Reader, Step-by-Step Interactive Derivations (`Step 1` ➔ `Next` ➔ `Final Equation`), LaTeX math derivations, memory tricks, professor notes, career applications (*Preamplifiers, SMPS, ECG Medical Monitors, Sensor Interfaces*), and conditional simulation launch buttons.
- **🧠 Problem Solving Lab**: Decision Tree recognition guides, step-by-step numerical solvers (Clippers, Clampers, Multivibrators), and an **offline rule-based hint engine**.
- **🧪 Interactive Simulation (Topic-Specific Waveform & Circuit Visualizations)**: Clean, experiment-tailored Matplotlib visualizers:
  - *Clippers*: Input vs Output waveform comparison + Clipping threshold line ($V_{\text{clip}}$).
  - *Clampers*: Input vs Output waveform + DC Shift level ($V_{dc}$).
  - *Rectifiers*: Rectified output waveform + Ripple curve + DC output level graph.
  - *Filters*: Bode Magnitude frequency response plot (dB) + Bode Phase response plot.
  - *Multivibrators*: Square wave output pulse train with adjustable frequency & duty cycle.
- **📝 Assessment**: Upgraded CBT Examination System with **900 Questions across 30 Exam Sets** (10 Easy, 10 Medium, 10 Hard per set), 30-min timer, auto-submit, topic analytics, and Certificates of Mastery.
- **📚 Reference**: Formula Explorer (live search), Interactive Calculators (*Clippers, Clampers, Filters*), Unit Converter, Constants.

---

### 2. ⚡ Digital System Design Hub
A comprehensive digital electronics hub structured for maximum learning retention:
- **📖 Learn (Textbook Reader)**: 25% / 75% screen split layout. Features a sticky header bar, sequential 16-topic learning path, 320×220px diagram gallery with Zoom/Pan modal inspection, centered 22px Boolean equation banners, full-width truth tables, and **"🧠 Easy Memory Trick (How to Remember Instantly)"** cards.
- **🧪 Practice (Breadboard Trainer Kit)**: A full-screen 2D virtual solderless breadboard trainer (`DSDLabView`) supporting fundamental 74-Series TTL ICs (`7400, 7402, 7404, 7408, 7411, 7432, 7486, 74266`), DIP switches, LEDs, wire-driven netlist logic propagation, and real-time output terminal inspection.
- **📝 Test (Assessment Suite)**: MCQ Quiz Bank, Viva Voce flashcards, technical interview prep, and printable Certificate of Mastery generator.
- **📚 Reference (IC & Formula Matrix)**: 74-Series TTL IC pinout matrix, DeMorgan's rule (*"Break the bar, change the sign!"*), and formula memorization shortcuts.

---

### 3. 📈 Signal & System Hub
A world-class interactive learning and analysis platform for Signals & Systems:
- **📖 Learn (Interactive Textbook)**: 25% / 75% screen split layout covering 10 Modules and 40+ Topics (Signal Classification, Operations, Linear Systems, Convolution, Fourier Series, Fourier Transform, Laplace Transform, Z-Transform, Nyquist Sampling, and Applications). Renders LaTeX math equations, worked numerical examples, professor notes, and **"🧠 Memory Trick"** cards.
- **🧪 Interactive Simulation**: Real-time Matplotlib interactive engine supporting Signal Generators (Step, Ramp, Sine, Square, Triangular), Signal Operations Transformer (Shift, Scale, Fold), Convolution Animator, Fourier Series Harmonics Synthesizer, Laplace & Z-Transform Pole-Zero & ROC Plotter, and Nyquist Sampling & Aliasing Demonstration.
- **📝 Assessment**: Interactive MCQ quiz bank, numerical problem sets, technical interview & viva voce Q&A with difficulty filters (Easy, Medium, Hard) and automated score tracking.
- **📚 Reference (Formula Matrix)**: Formula cheat sheets, lookup tables, and memorization shortcuts.

---

### 4. ⚡ Network Theory Hub (Virtual Engineering Laboratory Suite)
A world-class interactive learning, simulation, and problem-solving platform for Electrical Network Theory:
- **🏠 Learning Dashboard (Home Page)**: Metric cards (Modules Completed, Overall Progress %, Simulations Finished, CBT Average, Certificates Earned), Continue Learning quick jump cards, and recent activity logs.
- **📖 Learn (Interactive Textbook)**: Course Roadmap progress header, 25% Sidebar | 75% Reader, Step-by-Step Interactive Derivation revealer (`Step 1` ➔ `Next` ➔ `Final Equation`), LaTeX math derivations, memory tricks, professor notes, career applications (*Power Systems, Robotics, VLSI, Biomedical*), and related topic cross-links.
- **🧠 Problem Solving Lab**: 13-step learning loop (*Theory ➔ Recognition Decision Tree ➔ Memory Trick ➔ Flowchart Workflow ➔ Algorithm ➔ Worked Examples ➔ Interactive Solver ➔ Rule-Based Hints ➔ Simulation ➔ Practice ➔ Shortcuts ➔ Viva ➔ Summary*) featuring an **offline rule-based hint engine**.
- **🧪 Interactive Simulation**: Staged Matplotlib circuit simulators (Phases 1–5: Ohm's Law, KCL, KVL, Dividers, Mesh/Nodal, Source Transform, Superposition, Thevenin/Norton, Max Power, Phasors, Resonance, Filters, Circuit Builder) + **University Standard Engineering Laboratory Manuals**.
- **📝 Assessment**: Powered by `CBTExamWidget("network_theory")` with 900 questions across 30 Exam Sets (10 Easy, 10 Medium, 10 Hard per set), 30-min countdown timer, auto-submit, topic analytics, and Certificates of Mastery.
- **📚 Reference**: Formula Explorer (live search), 10 Interactive Calculators (*Resistance, Impedance, Power Triangle, Resonance, Thevenin/Norton, Dividers, Q-Factor, Reactance*), Unit Converter, IC Tables, Constants.
- **💼 Engineering Workspace**: Save circuits, notes, bookmarks, recent simulations, and export/import sessions.

---

### 5. 📝 Enterprise Computer-Based Testing (CBT) Examination System
A professional university-grade Computer-Based Test (CBT) examination platform powered by a **3,600-question database across 120 exam sets**:
- **Cross-Hub Standard**: Operates identically across Digital System Design Hub, Signal & System Hub, Analog Electronics Hub, and Network Theory Hub.
- **Adaptive Difficulty & 5 Exam Modes**: Easy Mode, Medium Mode, Hard Mode, Mixed Mode, and **Adaptive Mode** (dynamically shifts numeric difficulty 0–100 based on live correctness streaks).
- **Question Navigator Grid (1–30)**: Color-coded state indicators (Gray=Not Visited, Blue=Visited, Green=Answered, Yellow=Marked for Review).
- **Bloom's Taxonomy Levels**: Categorized across 6 cognitive levels (*Remember, Understand, Apply, Analyze, Evaluate, Create*).
- **Analytics Dashboard & Topic Heatmaps**: Matplotlib Pie Charts (Response Breakdown), Bar Graphs (Topic Mastery), and Radar Skill Profiles.
- **Answer Reviewer with Direct Links**: Reviews every question with explanations, student vs correct answers, and direct **`📖 Launch Theory`** and **`🧪 Launch Simulation`** buttons.
- **Smart Learning Recommendations**: Identifies weak topics and estimates recovery time (e.g., *"Weak in Fourier Series. Estimated Recovery Time: 38 minutes"*).
- **Official Certificate of Mastery**: Generates printable/saveable ElectroVerse Certificates (PNG/PDF) with unique Certificate ID and QR verification seal for scores $\ge 80\%$.
- **Instructor Portal Mode**: Toggle switch to unlock all 90 sets, view answer keys, build custom topic exams, and export batch reports.
- **100% Offline First**: Operates completely locally without cloud or API dependencies.

---

### 6. 🎓 Grand Viva & Core Technical Interview Prep
An extensive oral board examination simulator:
- **2,200+ Conceptual Questions**: Spanning 22 core ECE/CSE engineering subjects (Digital Electronics, Basic Electronics, Analog Circuits, Signals & Systems, Network Theory, Control Systems, Microprocessors, VLSI, DSP, IoT, Operating Systems, etc.).
- **Governing Equations & Variables**: Every question renders LaTeX math equations with exact variable definitions.
- **🧠 Instant Memorization Trick**: A dedicated gold-bordered card on every question explaining how to recognize, understand, and remember the concept instantly during interviews.

---

### 7. 🏠 Engineering Control Center (Dashboard)
Features workspace launch shortcuts, system status metrics, daily engineering challenges, recommended topics, scientific vector scope animations, and recent activity logs.

---

### 8. 📚 Component Library
An interactive electronic component database with deep physical insights, schematic symbols, pinout diagrams, real photos, formulas, SI units, and cross-module links.

---

## 🎨 Premium Engineering Laboratory Theme

ElectroVerse features a high-contrast, clean laboratory theme designed for long engineering sessions:

- **Window Background**: `#0B1020`
- **Sidebar Panel**: `#111827` (with `#26334D` border and 3px `#2563EB` active selection indicator)
- **Laboratory Cards**: `#141B2D` (Border `#26334D`, Hover `#1B2740`, 10px rounded corners)
- **Top Navigation Bar**: `#101827`
- **Primary Accent (`#06B6D4`)**: Active tabs, links, focus borders, active icons.
- **Secondary Accent (`#2563EB`)**: Primary action buttons (Hover `#3B82F6`, Pressed `#1D4ED8`).
- **Status Indicators**: Success `#22C55E` | Warning `#F59E0B` | Error `#EF4444` | Info `#38BDF8`.
- **Signal & Circuit Waveforms**: Primary `#06B6D4` | Secondary `#38BDF8` | Highlight `#22C55E` | Warning `#F59E0B`.

---

## 🛠 Tech Stack

- **GUI Framework**: [PySide6 (Qt 6)](https://doc.qt.io/qtforpython-6/) — Hardware-accelerated desktop interface.
- **Plotting & Analytics**: [Matplotlib](https://matplotlib.org/) & [PyQtGraph](https://www.pyqtgraph.org/) — Real-time waveform rendering and vector animations.
- **Numerical Solvers**: [NumPy](https://numpy.org/) & [SciPy](https://scipy.org/) — Fast differential equation transient solvers.
- **Vector Icons**: [QtAwesome](https://github.com/spyder-ide/qtawesome) — FontAwesome iconography.

---

## 🚦 Getting Started

### Prerequisites
- **Python 3.8 or higher** installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SOUVIK251/Electroverse.git
   cd Electroverse
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run ElectroVerse:**
   ```bash
   python main.py
   ```

---

## 👨‍💻 About & Author Credit

**Created & Lead Developed by Souvik Kundu**  
GitHub: [@SOUVIK251](https://github.com/SOUVIK251)

*Designed and engineered with passion by Souvik Kundu to make offline engineering education visual, intuitive, and accessible worldwide.*

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
