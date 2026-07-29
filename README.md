# ⚡ ElectroVerse — Virtual Engineering Laboratory

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-PySide6%20%2F%20Qt6-cyan.svg)](https://doc.qt.io/qtforpython-6/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Theme](https://img.shields.io/badge/Theme-Laboratory%20Suite-blueviolet.svg)](#-premium-engineering-laboratory-theme)
[![Author](https://img.shields.io/badge/Author-Souvik%20Kundu-brightgreen.svg)](https://github.com/SOUVIK251)

> **Created & Lead Developed by [Souvik Kundu](https://github.com/SOUVIK251)**  
> *Designed to make offline electronics engineering education intuitive, visual, interactive, and accessible.*

**ElectroVerse** is a modern, laboratory-grade interactive desktop application designed for students, educators, and electrical engineers. Inspired by professional software suites like **NI Multisim**, **Keysight BenchVue**, and **MATLAB App Designer**, it combines digital logic design, 2D solderless breadboard simulation, 2,200+ viva voce prep questions, ECE/CSE textbook lessons, and real-time circuit transient solvers into a unified offline desktop suite.

---

## 🌟 Key Modules & Features

### 1. ⚡ Digital System Design Hub
A comprehensive digital electronics hub structured for maximum learning retention:
- **📖 Learn (Textbook Reader)**: 25% / 75% screen split layout. Features a sticky header bar, sequential 16-topic learning path, 320×220px diagram gallery with Zoom/Pan modal inspection, centered 22px Boolean equation banners, full-width truth tables, and **"🧠 Easy Memory Trick (How to Remember Instantly)"** cards.
- **🧪 Practice (Breadboard Trainer Kit)**: A full-screen 2D virtual solderless breadboard trainer (`DSDLabView`) supporting fundamental 74-Series TTL ICs (`7400, 7402, 7404, 7408, 7411, 7432, 7486, 74266`), DIP switches, LEDs, and logic timing graphs.
- **📝 Test (Assessment Suite)**: MCQ Quiz Bank, Viva Voce flashcards, technical interview prep, and printable Certificate of Mastery generator.
- **📚 Reference (IC & Formula Matrix)**: 74-Series TTL IC pinout matrix, DeMorgan's rule (*"Break the bar, change the sign!"*), and formula memorization shortcuts.

### 2. 🎓 Grand Viva & Core Technical Interview Prep
An extensive oral board examination simulator:
- **2,200+ Conceptual Questions**: Spanning 22 core ECE/CSE engineering subjects (Digital Electronics, Basic Electronics, Analog Circuits, Signals & Systems, Network Theory, Control Systems, Microprocessors, VLSI, DSP, IoT, Operating Systems, etc.).
- **Governing Equations & Variables**: Every question renders LaTeX math equations with exact variable definitions.
- **🧠 Instant Memorization Trick**: A dedicated gold-bordered card on every question explaining how to recognize, understand, and remember the concept instantly during interviews.

### 3. 🏠 Engineering Control Center (Dashboard)
Features workspace launch shortcuts, system status metrics, daily engineering challenges, recommended topics, scientific vector scope animations, and recent activity logs.

### 4. 📚 Component Library
An interactive electronic component database with deep physical insights, schematic symbols, pinout diagrams, real photos, formulas, SI units, and cross-module links.

### 5. 🎓 Learning Mode
Structured academic curriculum covering passive components, PN junction diodes, Zener voltage regulators, BJTs, MOSFETs, and operational amplifiers.

### 6. 🛠 Engineering Toolkit
Interactive calculators for Ohm's Law, Voltage/Current Dividers, LED Resistor Sizing, Capacitive/Inductive Reactance, RC/RL Time Constants, and RLC Resonance.

### 7. 🧪 Simulation Lab & Oscilloscope
Real-time physical solvers for RC/RL transients, RLC resonance sweeps, rectifiers, clippers, and clampers paired with a dual-channel virtual Digital Storage Oscilloscope (DSO).

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
- **Oscilloscope Waveforms**: CH1 `#FFD60A`, CH2 `#FF4FA3`, Math `#00E5FF`, Trigger `#FF3B30`, Measurements `#06B6D4`.

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

## 👨‍💻 Author & Developer

**Created & Lead Developed by Souvik Kundu**  
GitHub: [@SOUVIK251](https://github.com/SOUVIK251)

*Designed and engineered with passion by Souvik Kundu to advance offline engineering education.*

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
