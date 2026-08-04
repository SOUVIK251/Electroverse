import json
import os

data_dir = 'src/data/signals'
topics_dir = os.path.join(data_dir, 'topics')
os.makedirs(topics_dir, exist_ok=True)

# Module 1
mod1 = {
    'id': 'module_1',
    'title': 'Module 1: Introduction to Signals',
    'topics': {
        'sig_def': {
            'title': 'Signal Definition & Classification',
            'read_time': '8 min read',
            'difficulty': 'Basic',
            'category': 'Fundamentals',
            'summary': 'A signal is a physical function carrying information about the state or behavior of a physical system.',
            'introduction': 'Signals are foundational to electronics, communications, control systems, and data processing.',
            'theory': (
                'Mathematically, a signal is represented as a function of one or more independent variables, '
                'most commonly time t or spatial coordinate x. For example, a speech voltage signal v(t) '
                'varies with time, while an image intensity I(x,y) varies with 2D spatial coordinates.'
            ),
            'derivation': (
                '**Classification Overview**:\n\n'
                '1. **Continuous-Time (CT) vs Discrete-Time (DT)**: CT signals x(t) defined for all t in R. DT signals x[n] defined only at integer indices n in Z.\n'
                '2. **Analog vs Digital**: Analog has continuous amplitude; Digital has quantized discrete amplitude levels.\n'
                '3. **Deterministic vs Random**: Deterministic signals can be modeled by exact mathematical formulas x(t) = A cos(w t). Random signals cannot be predicted deterministically and are modeled statistically (e.g., thermal noise).'
            ),
            'important_formulas': [
                'x(t) = Continuous-time signal defined for all t',
                'x[n] = x(n T_s) = Discrete-time signal sampled at interval T_s'
            ],
            'examples': [
                {
                    'problem': 'Classify the signal x(t) = 5 cos(200 pi t) + 2 sin(500 pi t).',
                    'solution': 'The signal is continuous-time, deterministic, analog, and periodic.'
                }
            ],
            'common_mistakes': [
                'Confusing discrete-time with digital: discrete-time refers to independent variable (time), digital refers to dependent variable (amplitude quantization).'
            ],
            'interview_questions': [
                {
                    'question': 'What is the fundamental difference between an analog signal and a digital signal?',
                    'answer': 'An analog signal has a continuous range of values for both time and amplitude. A digital signal has discrete quantized values in both time and amplitude.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'Give a real-world example of a 2D non-time signal.',
                    'answer': 'A digital photograph I(x,y), where light intensity varies across spatial coordinates x and y.'
                }
            ],
            'professor_notes': 'Always check the domain of independent variable first before analyzing frequency components!',
            'memory_trick': '🧠 **Memory Trick**: **Analog** = Continuous Everywhere (Time & Height). **Digital** = Staircase Everywhere (Grid & Steps).'
        },
        'sig_energy_power': {
            'title': 'Energy & Power Signals',
            'read_time': '10 min read',
            'difficulty': 'Intermediate',
            'category': 'Signal Metrics',
            'summary': 'Signals are classified as Energy signals or Power signals based on their total energy E and average power P.',
            'introduction': 'Understanding whether a signal is an Energy signal (0 < E < inf, P = 0) or a Power signal (0 < P < inf, E = inf) is essential for spectral analysis.',
            'theory': (
                'Total Energy E of a continuous-time signal x(t) is defined as:\n\n'
                '$$E = \\int_{-\\infty}^{\\infty} |x(t)|^2 dt$$\n\n'
                'Average Power P of a continuous-time signal x(t) is defined as:\n\n'
                '$$P = \\lim_{T \\to \\infty} \\frac{1}{2T} \\int_{-T}^{T} |x(t)|^2 dt$$'
            ),
            'derivation': (
                '**Energy vs Power Property Rules**:\n\n'
                '- An **Energy Signal** has finite energy 0 < E < inf and zero average power P = 0. (e.g., transient pulses, damped exponentials).\n'
                '- A **Power Signal** has finite non-zero average power 0 < P < inf and infinite energy E = inf. (e.g., periodic sinusoids, square waves).\n'
                '- Signals with infinite energy and infinite power are **Neither** (e.g., growing exponentials e^(2t)).'
            ),
            'important_formulas': [
                'E = \\int_{-\\infty}^{\\infty} |x(t)|^2 dt',
                'P = \\lim_{T \\to \\infty} \\frac{1}{2T} \\int_{-T}^{T} |x(t)|^2 dt',
                'P_{periodic} = \\frac{1}{T_0} \\int_{0}^{T_0} |x(t)|^2 dt'
            ],
            'examples': [
                {
                    'problem': 'Determine if x(t) = A e^(-a t) u(t) (where a > 0) is an Energy or Power signal.',
                    'solution': 'Calculate Energy: E = \\int_0^inf A^2 e^(-2at) dt = A^2 / (2a). Since 0 < E < inf, it is an Energy Signal with E = A^2/(2a) Joules and Power P = 0.'
                }
            ],
            'common_mistakes': [
                'A signal CANNOT be both an energy and a power signal simultaneously! If E < inf, then P = 0. If 0 < P < inf, then E = inf.'
            ],
            'interview_questions': [
                {
                    'question': 'What is the average power of a periodic signal x(t) = A cos(w_0 t + theta)?',
                    'answer': 'The average power of a sinusoidal signal with amplitude A is P = A^2 / 2, independent of frequency w_0 or phase theta.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the unit of Signal Energy in Signal Theory?',
                    'answer': 'Joules (assuming normalized 1-ohm load resistor).'
                }
            ],
            'professor_notes': 'For periodic signals with period T0, always use the 1/T0 single period integral shortcut to find Power directly!',
            'memory_trick': '🧠 **Memory Trick**: **Pulse = Energy** (Flashes & dies). **Periodic = Power** (Keeps going forever).'
        },
        'sig_elementary': {
            'title': 'Unit Step, Impulse, Ramp & Signum Function',
            'read_time': '9 min read',
            'difficulty': 'Basic',
            'category': 'Elementary Signals',
            'summary': 'Elementary signals serve as basic building blocks for constructing complex signals and testing system responses.',
            'introduction': 'Unit Step u(t), Unit Impulse delta(t), Unit Ramp r(t), and Signum sgn(t) are foundational mathematical signals.',
            'theory': (
                '1. **Unit Step u(t)**:\n'
                '$$u(t) = \\begin{cases} 1, & t > 0 \\\\ 0, & t < 0 \\end{cases}$$\n\n'
                '2. **Dirac Delta / Unit Impulse delta(t)**:\n'
                '$$\\delta(t) = 0 \\text{ for } t \\neq 0, \\quad \\int_{-\\infty}^{\\infty} \\delta(t) dt = 1$$\n\n'
                '3. **Unit Ramp r(t)**:\n'
                '$$r(t) = t u(t) = \\int_{-\\infty}^{t} u(\\tau) d\\tau$$\n\n'
                '4. **Signum Function sgn(t)**:\n'
                '$$\\operatorname{sgn}(t) = \\begin{cases} 1, & t > 0 \\\\ -1, & t < 0 \\end{cases} = 2 u(t) - 1$$'
            ),
            'derivation': (
                '**Key Calculus Relationships**:\n\n'
                '- Derivative of Ramp is Step: d/dt r(t) = u(t)\n'
                '- Derivative of Step is Impulse: d/dt u(t) = delta(t)\n'
                '- Sifting Property of Impulse: \\int_-inf^inf x(t) delta(t - t0) dt = x(t0)'
            ),
            'important_formulas': [
                'd/dt r(t) = u(t)',
                'd/dt u(t) = \\delta(t)',
                '\\int_{-\\infty}^{\\infty} x(t) \\delta(t - t_0) dt = x(t_0)',
                'x(t) \\delta(t - t_0) = x(t_0) \\delta(t - t_0)'
            ],
            'examples': [
                {
                    'problem': 'Evaluate the integral \\int_-inf^inf (t^3 + 4t + 2) delta(t - 2) dt.',
                    'solution': 'Using the sifting property: Substitute t = 2 into x(t) = t^3 + 4t + 2: Result = 2^3 + 4(2) + 2 = 8 + 8 + 2 = 18.'
                }
            ],
            'common_mistakes': [
                'Thinking delta(0) = 1. The height of delta(t) at t=0 is infinite; its AREA (integral) is 1!'
            ],
            'interview_questions': [
                {
                    'question': 'State the sifting property of the Dirac delta function.',
                    'answer': 'Integrating the product of a continuous function x(t) and delta(t - t0) over all time extracts the value of x(t) evaluated at t0.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'How is signum related to the unit step function?',
                    'answer': 'sgn(t) = 2 u(t) - 1.'
                }
            ],
            'professor_notes': 'The sampling property yields an impulse scaled by x(t0), whereas the sifting integral yields a scalar number x(t0)!',
            'memory_trick': '🧠 **Memory Trick**: **Ramp -> Step -> Impulse**. Integrate to go backwards!'
        }
    }
}

# Module 2
mod2 = {
    'id': 'module_2',
    'title': 'Module 2: Signal Operations',
    'topics': {
        'op_time_shift': {
            'title': 'Time Shifting',
            'read_time': '7 min read',
            'difficulty': 'Basic',
            'category': 'Operations',
            'summary': 'Time shifting delays or advances a signal in time: x(t - t0) delays right, x(t + t0) advances left.',
            'introduction': 'Shifting a signal along the time axis is fundamental to delay lines, radar processing, and echo analysis.',
            'theory': (
                'Given a signal x(t):\n'
                '- **Delay**: $x(t - t_0)$ shifts the signal to the RIGHT by $t_0$ units ($t_0 > 0$).\n'
                '- **Advance**: $x(t + t_0)$ shifts the signal to the LEFT by $t_0$ units ($t_0 > 0$).'
            ),
            'derivation': (
                'To plot y(t) = x(t - t0):\n'
                'Set argument (t - t0) = t_old => t_new = t_old + t0. Every feature occurring at t_old moves to t_old + t0.'
            ),
            'important_formulas': [
                'y(t) = x(t - t_0) \\quad (\\text{Delay right by } t_0)',
                'y(t) = x(t + t_0) \\quad (\\text{Advance left by } t_0)'
            ],
            'examples': [
                {
                    'problem': 'If a gate pulse x(t) is non-zero between t = 0 and t = 2, find the non-zero duration of y(t) = x(t - 3).',
                    'solution': 'Shift right by 3: New duration is 0 + 3 <= t <= 2 + 3, so t = [3, 5].'
                }
            ],
            'common_mistakes': [
                'Mistaking x(t - 3) as a shift to the left because of the minus sign! Minus means DELAY = shift RIGHT.'
            ],
            'interview_questions': [
                {
                    'question': 'How does time shifting affect the energy of a signal?',
                    'answer': 'Time shifting does NOT change the total energy or average power of a signal: E_shifted = E_original.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'Does time shifting change the shape or area of a signal?',
                    'answer': 'No, time shifting only changes the position on the time axis; shape, amplitude, and area remain identical.'
                }
            ],
            'professor_notes': 'When combining operations, perform Time Shift FIRST, then Time Scaling!',
            'memory_trick': '🧠 **Memory Trick**: **Minus = Delay (Right)**. **Plus = Advance (Left)**.'
        },
        'op_time_scale': {
            'title': 'Time Scaling & Folding',
            'read_time': '9 min read',
            'difficulty': 'Intermediate',
            'category': 'Operations',
            'summary': 'Time scaling compresses or expands a signal: x(at) compresses if a > 1, expands if 0 < a < 1. Time folding reflects across y-axis: x(-t).',
            'introduction': 'Scaling alters signal speed (fast playback vs slow motion). Folding reverses time playback.',
            'theory': (
                '1. **Time Scaling x(at)**:\n'
                '- If |a| > 1: Signal is **compressed** in time by factor a.\n'
                '- If 0 < |a| < 1: Signal is **expanded** in time by factor 1/a.\n\n'
                '2. **Time Folding x(-t)**:\n'
                '- Reflects the signal across the vertical axis t = 0.'
            ),
            'derivation': (
                '**Order of Operations Rule** for y(t) = x(at - b):\n'
                '1. Method A (Shift then Scale): x(t) -> x(t - b) -> x(at - b).\n'
                '2. Method B (Scale then Shift): x(t) -> x(at) -> x(a(t - b/a)) = x(at - b).'
            ),
            'important_formulas': [
                'y(t) = x(at) \\quad (a > 1 \\Rightarrow \\text{compress by } a)',
                'y(t) = x(-t) \\quad (\\text{Time reflection / folding})'
            ],
            'examples': [
                {
                    'problem': 'A triangular signal x(t) extends from t = -2 to t = 4. Find the range of y(t) = x(2t).',
                    'solution': 'Time scaling compresses by 2: New range is -2/2 <= t <= 4/2 -> -1 <= t <= 2.'
                }
            ],
            'common_mistakes': [
                'Forgetting that time compression increases signal bandwidth proportionally in frequency domain!'
            ],
            'interview_questions': [
                {
                    'question': 'How does time scaling by factor a affect signal energy?',
                    'answer': 'If y(t) = x(at), the energy E_y = E_x / |a|.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What happens to the duration of a signal when scaled by x(0.5t)?',
                    'answer': 'The duration doubles (expands by factor of 2).'
                }
            ],
            'professor_notes': 'Always rewrite x(at - b) as x(a(t - b/a)) to avoid shift errors when scaling first!',
            'memory_trick': '🧠 **Memory Trick**: **Multiply time = Compress**. **Divide time = Expand**.'
        },
        'op_decomposition': {
            'title': 'Signal Decomposition (Even & Odd Parts)',
            'read_time': '8 min read',
            'difficulty': 'Intermediate',
            'category': 'Decomposition',
            'summary': 'Any arbitrary real signal x(t) can be uniquely decomposed into an even symmetric part x_e(t) and an odd antisymmetric part x_o(t).',
            'introduction': 'Symmetry decomposition simplifies Fourier analysis and integration.',
            'theory': (
                'Any signal x(t) = x_e(t) + x_o(t) where:\n\n'
                '$$x_e(t) = \\frac{x(t) + x(-t)}{2} \\quad (\\text{Even part: } x_e(-t) = x_e(t))$$\n\n'
                '$$x_o(t) = \\frac{x(t) - x(-t)}{2} \\quad (\\text{Odd part: } x_o(-t) = -x_o(t))$$'
            ),
            'derivation': (
                'Proof: x_e(t) + x_o(t) = (x(t) + x(-t))/2 + (x(t) - x(-t))/2 = 2x(t)/2 = x(t).'
            ),
            'important_formulas': [
                'x_e(t) = 0.5 * (x(t) + x(-t))',
                'x_o(t) = 0.5 * (x(t) - x(-t))',
                '\\int_{-T}^{T} x_o(t) dt = 0'
            ],
            'examples': [
                {
                    'problem': 'Find the even and odd parts of x(t) = e^(jt).',
                    'solution': 'x_e(t) = (e^(jt) + e^(-jt))/2 = cos(t). x_o(t) = (e^(jt) - e^(-jt))/2 = j sin(t).'
                }
            ],
            'common_mistakes': [
                'Thinking a signal must be either strictly even or strictly odd. Most signals are NEITHER, but can be split into both parts!'
            ],
            'interview_questions': [
                {
                    'question': 'What is the integral of an odd signal over a symmetric interval [-T, T]?',
                    'answer': 'Zero, because the positive area on one side cancels the negative area on the other side.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the even part of a unit step u(t)?',
                    'answer': 'x_e(t) = 0.5 * (u(t) + u(-t)) = 0.5 for all t != 0.'
                }
            ],
            'professor_notes': 'Even times Even = Even. Odd times Odd = Even. Even times Odd = Odd!',
            'memory_trick': '🧠 **Memory Trick**: **Even = Cosine (Mirror)**. **Odd = Sine (Upside-down flip)**.'
        }
    }
}

# Module 3
mod3 = {
    'id': 'module_3',
    'title': 'Module 3: System Fundamentals',
    'topics': {
        'sys_linear': {
            'title': 'Linearity (Superposition & Homogeneity)',
            'read_time': '10 min read',
            'difficulty': 'Intermediate',
            'category': 'System Properties',
            'summary': 'A system is linear if it satisfies both Superposition (Additivity) and Homogeneity (Scaling).',
            'introduction': 'Linear systems (LTI) allow powerful analysis using transfer functions, impulse responses, and frequency response.',
            'theory': (
                'A system T is **Linear** if for inputs x_1(t) -> y_1(t) and x_2(t) -> y_2(t):\n\n'
                '$$T\\{a x_1(t) + b x_2(t)\\} = a T\\{x_1(t)\\} + b T\\{x_2(t)\\} = a y_1(t) + b y_2(t)$$'
            ),
            'derivation': (
                '**Test Procedure**:\n'
                '1. Compute y_combined(t) = T{a x1(t) + b x2(t)}.\n'
                '2. Compute a y1(t) + b y2(t) = a T{x1(t)} + b T{x2(t)}.\n'
                '3. Check if y_combined(t) = a y1(t) + b y2(t). If YES -> Linear. If NO -> Nonlinear.'
            ),
            'important_formulas': [
                'T\\{a x_1(t) + b x_2(t)\\} = a y_1(t) + b y_2(t)',
                'T\\{0\\} = 0 \\quad (\\text{Zero input gives zero output})'
            ],
            'examples': [
                {
                    'problem': 'Test if y(t) = 3 x(t) + 2 is linear.',
                    'solution': 'Check zero input test: T{0} = 3(0) + 2 = 2 != 0. Since zero input gives non-zero output, it is NONLINEAR (it is incrementally linear / affine).'
                }
            ],
            'common_mistakes': [
                'Assuming y(t) = m x(t) + c is linear. In system theory, the constant offset c makes it NONLINEAR because T{0} != 0!'
            ],
            'interview_questions': [
                {
                    'question': 'What is a quick necessary condition to disprove linearity?',
                    'answer': 'If zero input produces a non-zero output (T{0} != 0), the system is guaranteed to be nonlinear.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'Is y(t) = x^2(t) linear?',
                    'answer': 'No, squaring violates homogeneity: T{a x(t)} = a^2 x^2(t) != a y(t).'
                }
            ],
            'professor_notes': 'Any system with powers (x^2), roots, abs(x), sin(x), or constant additions (+C) is NONLINEAR!',
            'memory_trick': '🧠 **Memory Trick**: **Linear** = Double input -> Double output. Zero input -> Zero output.'
        },
        'sys_time_inv': {
            'title': 'Time Invariance (TIV vs TV)',
            'read_time': '9 min read',
            'difficulty': 'Intermediate',
            'category': 'System Properties',
            'summary': 'A system is Time Invariant if a time shift in the input produces an identical time shift in the output.',
            'introduction': 'Time invariance means the system parameters do not change over time.',
            'theory': (
                'A system y(t) = T{x(t)} is **Time Invariant (TIV)** if:\n\n'
                '$$T\\{x(t - t_0)\\} = y(t - t_0)$$'
            ),
            'derivation': (
                '**Test Procedure**:\n'
                '1. Shift Input: Replace x(t) with x(t - t0) to get y(t, t0).\n'
                '2. Shift Output: Replace t with (t - t0) in expression of y(t) to get y(t - t0).\n'
                '3. Compare y(t, t0) and y(t - t0). If equal -> Time Invariant. If not -> Time Variant.'
            ),
            'important_formulas': [
                'T\\{x(t - t_0)\\} = y(t - t_0)'
            ],
            'examples': [
                {
                    'problem': 'Test if y(t) = t x(t) is Time Invariant.',
                    'solution': '1) Shift input: y(t, t0) = t x(t - t0). 2) Shift output: y(t - t0) = (t - t0) x(t - t0). Compare: t x(t - t0) != (t - t0) x(t - t0). Result: TIME VARIANT (because coefficient t varies with time).'
                }
            ],
            'common_mistakes': [
                'Confusing time scaling x(2t) with time invariance. Systems with time-scaled inputs x(at), x(t^2), or time-varying coefficients t x(t), cos(wt) x(t) are TIME VARIANT!'
            ],
            'interview_questions': [
                {
                    'question': 'Is an ideal sampler y[n] = x(n M) time invariant?',
                    'answer': 'No, downsampling by M is a time-variant operation.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'Why are LTI systems so important in engineering?',
                    'answer': 'Because LTI systems can be completely characterized by their impulse response h(t) using convolution.'
                }
            ],
            'professor_notes': 'Look at coefficients and argument of x! If t appears outside x() or as a multiplier inside x(at), it is Time Variant!',
            'memory_trick': '🧠 **Memory Trick**: **Time Invariant** = System behavior is the SAME today, tomorrow, or next year.'
        },
        'sys_stability': {
            'title': 'BIBO Stability & Causality',
            'read_time': '10 min read',
            'difficulty': 'Intermediate',
            'category': 'System Properties',
            'summary': 'BIBO Stability requires every Bounded Input to produce a Bounded Output. Causality requires output to depend only on present and past inputs.',
            'introduction': 'Real-world physical systems must be stable and causal to operate safely in real time.',
            'theory': (
                '1. **BIBO Stability**:\n'
                'If |x(t)| <= M_x < inf, then |y(t)| <= M_y < inf.\n'
                'For an LTI system with impulse response h(t):\n'
                '$$\\int_{-\\infty}^{\\infty} |h(t)| dt < \\infty \\quad (\\text{Absolutely integrable impulse response})$$\n\n'
                '2. **Causality**:\n'
                'Output y(t0) depends ONLY on input x(t) for t <= t0. For an LTI system, h(t) = 0 for t < 0.'
            ),
            'derivation': (
                '**Causality Check**:\n'
                '- y(t) = x(t - 2): Causal (depends on past t - 2).\n'
                '- y(t) = x(t + 1): Non-causal / Anti-causal (depends on future t + 1).\n'
                '- y(t) = x(-t): Non-causal (for t = -2, y(-2) = x(2) which is future).'
            ),
            'important_formulas': [
                '\\int_{-\\infty}^{\\infty} |h(t)| dt < \\infty \\quad (\\text{LTI BIBO Stability})',
                'h(t) = 0 \\text{ for } t < 0 \\quad (\\text{LTI Causality})'
            ],
            'examples': [
                {
                    'problem': 'Is the integrator y(t) = integral_-inf^t x(tau) dtau BIBO stable?',
                    'solution': 'Test with bounded input u(t) (bounded by 1): y(t) = t u(t) which grows to infinity as t -> inf. Result: UNSTABLE (Integrator has a pole at origin s=0).'
                }
            ],
            'common_mistakes': [
                'Assuming x(-t) is causal for t > 0. At t = -1, y(-1) = x(1) which requires FUTURE input at t = +1!'
            ],
            'interview_questions': [
                {
                    'question': 'Can a non-causal system be implemented in real time?',
                    'answer': 'No, physical real-time systems cannot predict the future. Non-causal systems can only be processed offline (e.g., recorded signals, image processing).'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the condition for stability of an LTI system in terms of its poles?',
                    'answer': 'All poles must lie strictly in the left-half of the s-plane (for CT) or inside the unit circle of the z-plane (for DT).'
                }
            ],
            'professor_notes': 'Causality = No future vision. Stability = No blow up to infinity!',
            'memory_trick': '🧠 **Memory Trick**: **Causal** = Memory of past + present only. **BIBO Stable** = Never explodes to infinity.'
        }
    }
}

# Module 4
mod4 = {
    'id': 'module_4',
    'title': 'Module 4: Convolution',
    'topics': {
        'conv_ct': {
            'title': 'Continuous-Time Convolution Integral',
            'read_time': '12 min read',
            'difficulty': 'Advanced',
            'category': 'LTI Analysis',
            'summary': 'Convolution describes the response y(t) of a continuous-time LTI system to any arbitrary input x(t) using its impulse response h(t).',
            'introduction': 'Convolution is the single most important mathematical operation in Linear System Theory.',
            'theory': (
                'The continuous-time convolution integral is defined as:\n\n'
                '$$y(t) = x(t) * h(t) = \\int_{-\\infty}^{\\infty} x(\\tau) h(t - \\tau) d\\tau$$\n\n'
                'Where x(t) is the input signal and h(t) is the system impulse response.'
            ),
            'derivation': (
                '**Graphical Convolution Steps (The 4 Steps)**:\n\n'
                '1. **Change variable**: Express x(t) as x(tau) and h(t) as h(tau).\n'
                '2. **Time Fold**: Reflect h(tau) to get h(-tau).\n'
                '3. **Time Shift**: Shift h(-tau) by t to get h(t - tau).\n'
                '4. **Multiply & Integrate**: Multiply x(tau) h(t - tau) and compute the area under the product curve for varying t.'
            ),
            'important_formulas': [
                'y(t) = x(t) * h(t) = \\int_{-\\infty}^{\\infty} x(\\tau) h(t - \\tau) d\\tau',
                'x(t) * \\delta(t - t_0) = x(t - t_0)',
                '\\text{Duration of } y(t) = (T_{x1} + T_{h1}) \\le t \\le (T_{x2} + T_{h2})'
            ],
            'examples': [
                {
                    'problem': 'Convolve x(t) = u(t) with h(t) = e^(-at) u(t) (a > 0).',
                    'solution': 'y(t) = integral_0^t 1 * e^(-a(t-tau)) dtau = e^(-at) integral_0^t e^(a tau) dtau = (1 - e^(-at))/a u(t).'
                }
            ],
            'common_mistakes': [
                'Forgetting to change the integration variable to tau! The integral is evaluated over tau, leaving t as the shift parameter.'
            ],
            'interview_questions': [
                {
                    'question': 'What is the convolution of two rectangular pulses of equal width T?',
                    'answer': 'A triangular pulse of duration 2T.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What corresponds to convolution in the time domain when converted to the frequency domain?',
                    'answer': 'Multiplication in the frequency domain: Y(w) = X(w) * H(w).'
                }
            ],
            'professor_notes': 'Commutative property: x(t) * h(t) = h(t) * x(t). Always flip the simpler signal to make integration easier!',
            'memory_trick': '🧠 **Memory Trick**: **Fold, Shift, Multiply, Integrate (FSMI)**.'
        },
        'conv_dt': {
            'title': 'Discrete-Time Convolution Sum',
            'read_time': '11 min read',
            'difficulty': 'Advanced',
            'category': 'LTI Analysis',
            'summary': 'Discrete-time convolution calculates the output y[n] of a discrete LTI system as y[n] = sum_k x[k] h[n - k].',
            'introduction': 'Discrete convolution is the core algorithm used in digital FIR filters and DSP chips.',
            'theory': (
                'The discrete-time convolution sum is defined as:\n\n'
                '$$y[n] = x[n] * h[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n - k]$$'
            ),
            'derivation': (
                '**Length Property**:\n'
                'If x[n] has length N1 and h[n] has length N2, the output y[n] has length:\n'
                '$$L = N_1 + N_2 - 1$$\n\n'
                '**Tabular Method (Matrix Multiplication)**:\n'
                'Arrange x[k] as column and h[n-k] as row, compute diagonal sums.'
            ),
            'important_formulas': [
                'y[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n - k]',
                '\\text{Length}(y[n]) = N_1 + N_2 - 1'
            ],
            'examples': [
                {
                    'problem': 'Convolve x[n] = {1, 2, 3} at n=0,1,2 with h[n] = {1, 1} at n=0,1.',
                    'solution': 'Length = 3 + 2 - 1 = 4 points. y[0]=1*1=1, y[1]=1*1+2*1=3, y[2]=2*1+3*1=5, y[3]=3*1=3. y[n] = {1, 3, 5, 3}.'
                }
            ],
            'common_mistakes': [
                'Incorrect starting index of output y[n]. Start index n_start = n_start_x + n_start_h!'
            ],
            'interview_questions': [
                {
                    'question': 'How do you calculate the starting index of a discrete convolution result?',
                    'answer': 'n_start(y) = n_start(x) + n_start(h).'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the sum of all samples in y[n] = x[n] * h[n]?',
                    'answer': 'Sum(y) = Sum(x) * Sum(h).'
                }
            ],
            'professor_notes': 'Use the tabular matrix method for quick verification in exam calculations!',
            'memory_trick': '🧠 **Memory Trick**: **Output Length = N1 + N2 - 1**. **Start Index = Start1 + Start2**.'
        }
    }
}

# Module 5: Fourier Series
mod5 = {
    'id': 'module_5',
    'title': 'Module 5: Fourier Series',
    'topics': {
        'fs_trig': {
            'title': 'Trigonometric Fourier Series',
            'read_time': '10 min read',
            'difficulty': 'Intermediate',
            'category': 'Fourier Analysis',
            'summary': 'Represents any periodic signal x(t) with fundamental period T0 as a sum of DC, sines, and cosines.',
            'introduction': 'Fourier series proves that periodic waveforms are composed of a fundamental frequency and integer harmonics.',
            'theory': (
                '$$x(t) = a_0 + \\sum_{n=1}^{\\infty} \\left( a_n \\cos(n w_0 t) + b_n \\sin(n w_0 t) \\right)$$\n\n'
                'Where $w_0 = 2 \\pi / T_0$ is the fundamental angular frequency.\n\n'
                'Coefficients:\n'
                '$$a_0 = \\frac{1}{T_0} \\int_{0}^{T_0} x(t) dt$$\n'
                '$$a_n = \\frac{2}{T_0} \\int_{0}^{T_0} x(t) \\cos(n w_0 t) dt$$\n'
                '$$b_n = \\frac{2}{T_0} \\int_{0}^{T_0} x(t) \\sin(n w_0 t) dt$$'
            ),
            'derivation': (
                '**Dirichlet Conditions for Convergence**:\n'
                '1. x(t) is single-valued and bounded.\n'
                '2. x(t) has a finite number of discontinuities in any one period.\n'
                '3. x(t) has a finite number of maxima and minima in any one period.'
            ),
            'important_formulas': [
                'x(t) = a_0 + \\sum_{n=1}^{\\infty} [a_n \\cos(n w_0 t) + b_n \\sin(n w_0 t)]',
                'a_0 = \\frac{1}{T_0} \\int_{0}^{T_0} x(t) dt',
                'a_n = \\frac{2}{T_0} \\int_{0}^{T_0} x(t) \\cos(n w_0 t) dt',
                'b_n = \\frac{2}{T_0} \\int_{0}^{T_0} x(t) \\sin(n w_0 t) dt'
            ],
            'examples': [
                {
                    'problem': 'Find the Fourier series coefficients for an even square wave of amplitude A.',
                    'solution': 'Since x(t) is even, b_n = 0 for all n. a_0 = A/2. a_n = 4A/(n pi) for odd n, and 0 for even n.'
                }
            ],
            'common_mistakes': [
                'Forgetting that for EVEN signals, b_n = 0. For ODD signals, a_0 = 0 and a_n = 0!'
            ],
            'interview_questions': [
                {
                    'question': 'What are the Dirichlet conditions?',
                    'answer': 'Conditions guaranteeing that a periodic function can be expanded into a convergent Fourier series.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the physical meaning of a_0 in Fourier Series?',
                    'answer': 'a_0 is the average value (DC component) of the signal over one period.'
                }
            ],
            'professor_notes': 'Exploit symmetry! If x(t) is even, b_n = 0 automatically. If x(t) is odd, a_n = 0 and a_0 = 0!',
            'memory_trick': '🧠 **Memory Trick**: **Even = Cosine terms (a_n)**. **Odd = Sine terms (b_n)**.'
        }
    }
}

# Module 6: Fourier Transform
mod6 = {
    'id': 'module_6',
    'title': 'Module 6: Fourier Transform',
    'topics': {
        'ft_ctft': {
            'title': 'Continuous-Time Fourier Transform (CTFT)',
            'read_time': '12 min read',
            'difficulty': 'Advanced',
            'category': 'Frequency Analysis',
            'summary': 'Extends Fourier Analysis to aperiodic signals, mapping time-domain x(t) to frequency spectrum X(w).',
            'introduction': 'The Fourier Transform decomposes a non-periodic signal into a continuous spectrum of complex sinusoids.',
            'theory': (
                '**Forward CTFT**:\n'
                '$$X(\\omega) = \\mathcal{F}\\{x(t)\\} = \\int_{-\\infty}^{\\infty} x(t) e^{-j \\omega t} dt$$\n\n'
                '**Inverse CTFT (IFT)**:\n'
                '$$x(t) = \\mathcal{F}^{-1}\\{X(\\omega)\\} = \\frac{1}{2\\pi} \\int_{-\\infty}^{\\infty} X(\\omega) e^{j \\omega t} d\\omega$$'
            ),
            'derivation': (
                '**Parseval\'s Energy Theorem**:\n'
                '$$\\int_{-\\infty}^{\\infty} |x(t)|^2 dt = \\frac{1}{2\\pi} \\int_{-\\infty}^{\\infty} |X(\\omega)|^2 d\\omega$$\n'
                'States that total energy in time domain equals total energy in frequency domain.'
            ),
            'important_formulas': [
                'X(\\omega) = \\int_{-\\infty}^{\\infty} x(t) e^{-j \\omega t} dt',
                'x(t) = \\frac{1}{2\\pi} \\int_{-\\infty}^{\\infty} X(\\omega) e^{j \\omega t} d\\omega',
                '\\mathcal{F}\\{e^{-a t} u(t)\\} = \\frac{1}{a + j \\omega} \\quad (a > 0)',
                '\\mathcal{F}\\{\\delta(t)\\} = 1'
            ],
            'examples': [
                {
                    'problem': 'Find the Fourier Transform of a rectangular pulse x(t) = 1 for -T <= t <= T.',
                    'solution': 'X(w) = integral_-T^T 1 * e^(-jwt) dt = [e^(-jwt)/(-jw)]_-T^T = (e^(jwT) - e^(-jwT))/(jw) = 2 sin(wT)/w = 2T sinc(wT).'
                }
            ],
            'common_mistakes': [
                'Forgetting the 1/(2 pi) factor in the Inverse Fourier Transform integral equation!'
            ],
            'interview_questions': [
                {
                    'question': 'What is the Fourier Transform of a rectangular pulse in the time domain?',
                    'answer': 'A sinc function X(w) = 2T sinc(wT) in the frequency domain.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the duality property of the Fourier Transform?',
                    'answer': 'If F{x(t)} = X(w), then F{X(t)} = 2 pi x(-w).'
                }
            ],
            'professor_notes': 'Rectangular pulse in time <=> Sinc function in frequency! Sinc in time <=> Rectangular pulse in frequency!',
            'memory_trick': '🧠 **Memory Trick**: **Rect in Time = Sinc in Frequency**. **Narrow in time = Wide in frequency**.'
        }
    }
}

# Module 7: Laplace Transform
mod7 = {
    'id': 'module_7',
    'title': 'Module 7: Laplace Transform',
    'topics': {
        'lt_def': {
            'title': 'Laplace Transform & ROC',
            'read_time': '12 min read',
            'difficulty': 'Advanced',
            'category': 's-Domain Analysis',
            'summary': 'Generalizes Fourier transform using s = sigma + j w to analyze unstable signals and LTI differential equations.',
            'introduction': 'Laplace transform converts differential equations into algebraic equations in the complex s-plane.',
            'theory': (
                '**Bilateral Laplace Transform**:\n'
                '$$X(s) = \\mathcal{L}\\{x(t)\\} = \\int_{-\\infty}^{\\infty} x(t) e^{-s t} dt \\quad (s = \\sigma + j \\omega)$$\n\n'
                '**Unilateral Laplace Transform** (for causal systems $t \\ge 0$):\n'
                '$$X(s) = \\int_{0^{-}}^{\\infty} x(t) e^{-s t} dt$$\n\n'
                '**Region of Convergence (ROC)**: The range of $\\text{Re}\\{s\\} = \\sigma$ for which the Laplace integral converges.'
            ),
            'derivation': (
                '**Initial & Final Value Theorems**:\n\n'
                '- **Initial Value Theorem**: $\\lim_{t \\to 0^+} x(t) = \\lim_{s \\to \\infty} s X(s)$\n'
                '- **Final Value Theorem**: $\\lim_{t \\to \\infty} x(t) = \\lim_{s \\to 0} s X(s)$ (valid if all poles of $sX(s)$ lie in LHP).'
            ),
            'important_formulas': [
                'X(s) = \\int_{0^{-}}^{\\infty} x(t) e^{-s t} dt',
                '\\mathcal{L}\\{e^{-at} u(t)\\} = \\frac{1}{s + a} \\quad (\\text{ROC: } \\text{Re}\\{s\\} > -a)',
                '\\lim_{t \\to 0^+} x(t) = \\lim_{s \\to \\infty} s X(s)',
                '\\lim_{t \\to \\infty} x(t) = \\lim_{s \\to 0} s X(s)'
            ],
            'examples': [
                {
                    'problem': 'Find Laplace transform and ROC for x(t) = 3 e^{-2t} u(t) - 2 e^{-3t} u(t).',
                    'solution': 'X(s) = 3/(s + 2) - 2/(s + 3). ROC for e^{-2t} is Re{s} > -2, for e^{-3t} is Re{s} > -3. Overall ROC is Re{s} > -2.'
                }
            ],
            'common_mistakes': [
                'Applying Final Value Theorem when poles lie on jw-axis or RHP! FVT is ONLY valid if all poles of sX(s) are strictly in Left Half Plane.'
            ],
            'interview_questions': [
                {
                    'question': 'How does ROC indicate system stability for a causal LTI system?',
                    'answer': 'For a causal system, stability requires the ROC to include the jw-axis (Re{s} = 0), which means all poles must be in the Left Half Plane.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the Laplace transform of a unit impulse delta(t)?',
                    'answer': 'L{delta(t)} = 1 for all s.'
                }
            ],
            'professor_notes': 'ROC never contains any poles! For causal signals, ROC is to the right of the rightmost pole.',
            'memory_trick': '🧠 **Memory Trick**: **Causal = Right-sided ROC**. **Stable = ROC includes jw-axis**.'
        }
    }
}

# Module 8: Z-Transform
mod8 = {
    'id': 'module_8',
    'title': 'Module 8: Z-Transform',
    'topics': {
        'zt_def': {
            'title': 'Z-Transform & z-Plane ROC',
            'read_time': '11 min read',
            'difficulty': 'Advanced',
            'category': 'z-Domain Analysis',
            'summary': 'The discrete-time counterpart of the Laplace Transform, mapping x[n] to the complex z-plane (z = r e^(j w)).',
            'introduction': 'Z-transform is essential for designing digital FIR/IIR filters, analyzing difference equations, and DSP system stability.',
            'theory': (
                '**Bilateral Z-Transform**:\n'
                '$$X(z) = \\mathcal{Z}\\{x[n]\\} = \\sum_{n=-\\infty}^{\\infty} x[n] z^{-n} \\quad (z = r e^{j \\omega})$$\n\n'
                '**ROC in z-Plane**: Concentric ring $|z_{min}| < |z| < |z_{max}|$.\n'
                '- **Causal Signal**: ROC is outside circle $|z| > r_{max}$.\n'
                '- **Anti-Causal Signal**: ROC is inside circle $|z| < r_{min}$.\n'
                '- **Stable LTI System**: ROC includes the unit circle $|z| = 1$.'
            ),
            'derivation': (
                '**LTI System Transfer Function H(z)**:\n'
                '$$H(z) = \\frac{Y(z)}{X(z)} = \\frac{\\sum_{k=0}^{M} b_k z^{-k}}{1 + \\sum_{k=1}^{N} a_k z^{-k}}$$'
            ),
            'important_formulas': [
                'X(z) = \\sum_{n=-\\infty}^{\\infty} x[n] z^{-n}',
                '\\mathcal{Z}\\{a^n u[n]\\} = \\frac{1}{1 - a z^{-1}} = \\frac{z}{z - a} \\quad (|z| > |a|)',
                '\\mathcal{Z}\\{x[n - k]\\} = z^{-k} X(z)'
            ],
            'examples': [
                {
                    'problem': 'Find Z-transform of x[n] = (0.5)^n u[n].',
                    'solution': 'X(z) = sum_{n=0}^inf (0.5 z^{-1})^n = 1 / (1 - 0.5 z^{-1}) = z / (z - 0.5). ROC: |z| > 0.5.'
                }
            ],
            'common_mistakes': [
                'Omitting the Region of Convergence (ROC). Two completely different signals (e.g. a^n u[n] vs -a^n u[-n-1]) have identical X(z) algebraic form, distinguished ONLY by ROC!'
            ],
            'interview_questions': [
                {
                    'question': 'What is the relation between s-plane and z-plane?',
                    'answer': 'z = e^{s T_s}. Left-half s-plane maps inside unit circle |z| < 1. jw-axis maps onto unit circle |z| = 1.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'When is a discrete-time LTI system stable?',
                    'answer': 'When all poles of H(z) lie strictly inside the unit circle |z| < 1.'
                }
            ],
            'professor_notes': 'z-plane unit circle |z|=1 corresponds to s-plane jw-axis!',
            'memory_trick': '🧠 **Memory Trick**: **Inside Unit Circle = Stable**. **Outside Circle = Causal ROC**.'
        }
    }
}

# Module 9: Sampling Theorem
mod9 = {
    'id': 'module_9',
    'title': 'Module 9: Sampling Theorem',
    'topics': {
        'samp_nyquist': {
            'title': 'Nyquist-Shannon Sampling Theorem & Aliasing',
            'read_time': '10 min read',
            'difficulty': 'Intermediate',
            'category': 'Sampling & DSP',
            'summary': 'Establishes the minimum sampling rate required to convert a continuous signal to discrete samples without loss of information.',
            'introduction': 'The bridge between continuous-time analog signals and discrete digital processing.',
            'theory': (
                '**Nyquist-Shannon Sampling Theorem**:\n'
                'A band-limited continuous-time signal $x(t)$ with maximum frequency component $f_{max} = B$ Hz can be completely reconstructed from its samples if the sampling rate $f_s$ satisfies:\n\n'
                '$$f_s \\ge 2 f_{max} = 2 B \\quad (\\text{Nyquist Rate})$$\n\n'
                '- **Nyquist Rate**: $f_{Nyquist} = 2 f_{max}$\n'
                '- **Nyquist Interval**: $T_{Nyquist} = 1 / (2 f_{max})$\n\n'
                '**Aliasing**: When $f_s < 2 f_{max}$, high-frequency components overlap into lower frequencies, distorting the signal.'
            ),
            'derivation': (
                '**Mathematical Derivation**:\n'
                'Ideal sampling in time domain: $x_s(t) = x(t) \\cdot p(t)$ where $p(t) = \\sum_{n=-\\infty}^{\\infty} \\delta(t - n T_s)$.\n'
                'In frequency domain:\n'
                '$$X_s(\\omega) = \\frac{1}{T_s} \\sum_{k=-\\infty}^{\\infty} X(\\omega - k \\omega_s)$$\n'
                'If $\\omega_s \\ge 2 \\omega_{max}$, spectral replicas $X(\\omega - k \\omega_s)$ do not overlap and can be perfectly isolated using an ideal low-pass filter with cutoff $\\omega_c = \\omega_s / 2$.'
            ),
            'important_formulas': [
                'f_s \\ge 2 f_{max} \\quad (\\text{Nyquist Criterion})',
                'f_{Nyquist} = 2 f_{max}',
                'T_s \\le \\frac{1}{2 f_{max}}',
                'f_{alias} = |f_s - f_{in}|'
            ],
            'examples': [
                {
                    'problem': 'Find the Nyquist rate for x(t) = 3 cos(500 pi t) + 10 sin(1200 pi t) - 4 cos(800 pi t).',
                    'solution': 'Frequencies: f1 = 500/2 = 250 Hz, f2 = 1200/2 = 600 Hz, f3 = 800/2 = 400 Hz. Maximum frequency f_max = 600 Hz. Nyquist Rate = 2 * 600 = 1200 Hz (or 1200 samples/sec).'
                }
            ],
            'common_mistakes': [
                'Calculating Nyquist rate using angular frequency w_max without dividing by 2 pi! f_max = w_max / (2 pi).'
            ],
            'interview_questions': [
                {
                    'question': 'How do real-world ADCs prevent aliasing?',
                    'answer': 'By placing an Analog Anti-Aliasing Low-Pass Filter before the ADC sampler to attenuate any signal frequencies above f_s / 2.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is the wagon-wheel effect seen in movies?',
                    'answer': 'An optical example of temporal aliasing caused by the camera frame rate (sampling frequency) being lower than the wheel rotation rate.'
                }
            ],
            'professor_notes': 'Over-sampling (fs >> 2 fmax) makes anti-aliasing filter design much easier and cheaper in real DSP systems!',
            'memory_trick': '🧠 **Memory Trick**: **Sample at LEAST TWICE as fast as the highest speed component**.'
        }
    }
}

# Module 10: Applications
mod10 = {
    'id': 'module_10',
    'title': 'Module 10: Applications of Signals & Systems',
    'topics': {
        'app_overview': {
            'title': 'Engineering Applications Overview',
            'read_time': '8 min read',
            'difficulty': 'Basic',
            'category': 'Applications',
            'summary': 'Signals & Systems theory powers modern digital communication, medical imaging, control systems, and speech AI.',
            'introduction': 'From 5G smartphones to MRI scanners, Signals & Systems is the core mathematical foundation.',
            'theory': (
                '**Key Field Applications**:\n\n'
                '1. **Wireless Communication**: Amplitude/Frequency Modulation (AM/FM), OFDM, Channel estimation, Equalization.\n'
                '2. **Biomedical Engineering**: ECG/EEG noise filtering using notch filters, QRS complex detection, MRI spatial k-space reconstructions.\n'
                '3. **Control Systems**: Feedback stability analysis, PID control, Root Locus and Bode plot design for aircraft and robotics.\n'
                '4. **Speech & Audio**: Spectrogram analysis, noise suppression, MP3 compression, voice recognition (MFCCs).\n'
                '5. **Image Processing**: 2D Fourier Transform for image sharpening, JPEG compression (DCT), edge detection filters.'
            ),
            'derivation': (
                '**Example: Notch Filter for 50Hz/60Hz Power-line Noise Suppression**:\n'
                'A narrow band-stop filter with zeros placed on unit circle at $z = e^{\\pm j \\omega_0}$ removes 50Hz/60Hz hum from sensitive biomedical ECG recordings.'
            ),
            'important_formulas': [
                'H_{notch}(z) = \\frac{1 - 2 \\cos(\\omega_0) z^{-1} + z^{-2}}{1 - 2 r \\cos(\\omega_0) z^{-1} + r^2 z^{-2}} \\quad (r \\approx 0.95)',
                '\\text{AM Signal}: s(t) = [A_c + m(t)] \\cos(\\omega_c t)'
            ],
            'examples': [
                {
                    'problem': 'Why is 2D FFT used in MRI medical imaging?',
                    'solution': 'MRI scanners collect raw magnetic resonance data in "k-space" (spatial frequency domain). Applying 2D Inverse FFT reconstructs the 2D cross-sectional slice image of human tissue.'
                }
            ],
            'common_mistakes': [
                'Thinking DSP is software-only: real-time DSP applications require tight hardware-level pipelining and ADC/DAC interface timing!'
            ],
            'interview_questions': [
                {
                    'question': 'How does JPEG image compression use signal processing?',
                    'answer': 'JPEG divides images into 8x8 blocks, computes 2D Discrete Cosine Transform (DCT), quantizes high-frequency coefficients (which human eye is less sensitive to), and entropy encodes the rest.'
                }
            ],
            'viva_questions': [
                {
                    'question': 'What is an ECG QRS complex?',
                    'answer': 'The graphical deflection corresponding to the depolarization of the main heart ventricles, detected using bandpass signal filtering.'
                }
            ],
            'professor_notes': 'Every real-world engineer uses frequency-domain filtering daily to eliminate noise!',
            'memory_trick': '🧠 **Memory Trick**: **Signals = Information**. **Systems = Processing**. Applied everywhere in modern tech!'
        }
    }
}

# Write modules
for mod in [mod1, mod2, mod3, mod4, mod5, mod6, mod7, mod8, mod9, mod10]:
    fname = f"{mod['id']}_{mod['title'].split(':')[1].strip().lower().replace(' ', '_')}.json"
    if mod['id'] == 'module_1': fname = 'module_1_introduction.json'
    elif mod['id'] == 'module_2': fname = 'module_2_operations.json'
    elif mod['id'] == 'module_3': fname = 'module_3_systems.json'
    elif mod['id'] == 'module_4': fname = 'module_4_convolution.json'
    elif mod['id'] == 'module_5': fname = 'module_5_fourier_series.json'
    elif mod['id'] == 'module_6': fname = 'module_6_fourier_transform.json'
    elif mod['id'] == 'module_7': fname = 'module_7_laplace_transform.json'
    elif mod['id'] == 'module_8': fname = 'module_8_z_transform.json'
    elif mod['id'] == 'module_9': fname = 'module_9_sampling.json'
    elif mod['id'] == 'module_10': fname = 'module_10_applications.json'

    with open(os.path.join(topics_dir, fname), 'w', encoding='utf-8') as f:
        json.dump(mod, f, indent=2)
    print(f'Wrote {fname}')

# Formula Sheet JSON
formula_sheet = {
    'categories': [
        {
            'name': 'Elementary Signals',
            'formulas': [
                {'name': 'Unit Step u(t)', 'formula': 'u(t) = 1 (t > 0), 0 (t < 0)'},
                {'name': 'Unit Impulse delta(t)', 'formula': 'delta(t) = 0 (t != 0), integral delta(t) dt = 1'},
                {'name': 'Unit Ramp r(t)', 'formula': 'r(t) = t u(t)'},
                {'name': 'Signum sgn(t)', 'formula': 'sgn(t) = 2 u(t) - 1'}
            ]
        },
        {
            'name': 'Signal Metrics & Operations',
            'formulas': [
                {'name': 'Signal Energy E', 'formula': 'E = integral_{-inf}^{inf} |x(t)|^2 dt'},
                {'name': 'Signal Power P', 'formula': 'P = lim_{T->inf} (1/2T) integral_{-T}^{T} |x(t)|^2 dt'},
                {'name': 'Even Part x_e(t)', 'formula': 'x_e(t) = 0.5 * (x(t) + x(-t))'},
                {'name': 'Odd Part x_o(t)', 'formula': 'x_o(t) = 0.5 * (x(t) - x(-t))'}
            ]
        },
        {
            'name': 'Convolution',
            'formulas': [
                {'name': 'Continuous Convolution', 'formula': 'y(t) = integral_{-inf}^{inf} x(tau) h(t - tau) dtau'},
                {'name': 'Discrete Convolution', 'formula': 'y[n] = sum_{k=-inf}^{inf} x[k] h[n - k]'}
            ]
        },
        {
            'name': 'Transforms',
            'formulas': [
                {'name': 'Fourier Transform CTFT', 'formula': 'X(w) = integral_{-inf}^{inf} x(t) e^{-j w t} dt'},
                {'name': 'Inverse FT', 'formula': 'x(t) = (1 / 2 pi) integral_{-inf}^{inf} X(w) e^{j w t} dw'},
                {'name': 'Laplace Transform', 'formula': 'X(s) = integral_{0}^{inf} x(t) e^{-s t} dt'},
                {'name': 'Z-Transform', 'formula': 'X(z) = sum_{n=-inf}^{inf} x[n] z^{-n}'},
                {'name': 'Nyquist Rate', 'formula': 'f_s >= 2 f_{max}'}
            ]
        }
    ]
}

with open(os.path.join(data_dir, 'formula_sheet.json'), 'w', encoding='utf-8') as f:
    json.dump(formula_sheet, f, indent=2)
print('formula_sheet.json written')

# Reference Tables JSON
reference_tables = {
    'fourier_transform_table': [
        {'signal': 'delta(t)', 'transform': '1', 'roc_notes': 'All w'},
        {'signal': '1', 'transform': '2 pi delta(w)', 'roc_notes': 'All w'},
        {'signal': 'u(t)', 'transform': 'pi delta(w) + 1 / (j w)', 'roc_notes': 'All w'},
        {'signal': 'e^{-a t} u(t) (a > 0)', 'transform': '1 / (a + j w)', 'roc_notes': 'Re{a} > 0'},
        {'signal': 'rect(t / T)', 'transform': 'T sinc(w T / 2)', 'roc_notes': 'All w'},
        {'signal': 'cos(w_0 t)', 'transform': 'pi [delta(w - w_0) + delta(w + w_0)]', 'roc_notes': 'All w'},
        {'signal': 'sin(w_0 t)', 'transform': '-j pi [delta(w - w_0) - delta(w + w_0)]', 'roc_notes': 'All w'}
    ],
    'laplace_transform_table': [
        {'signal': 'delta(t)', 'transform': '1', 'roc': 'Entire s-plane'},
        {'signal': 'u(t)', 'transform': '1 / s', 'roc': 'Re{s} > 0'},
        {'signal': 't u(t)', 'transform': '1 / s^2', 'roc': 'Re{s} > 0'},
        {'signal': 'e^{-a t} u(t)', 'transform': '1 / (s + a)', 'roc': 'Re{s} > -a'},
        {'signal': 't e^{-a t} u(t)', 'transform': '1 / (s + a)^2', 'roc': 'Re{s} > -a'},
        {'signal': 'cos(w_0 t) u(t)', 'transform': 's / (s^2 + w_0^2)', 'roc': 'Re{s} > 0'},
        {'signal': 'sin(w_0 t) u(t)', 'transform': 'w_0 / (s^2 + w_0^2)', 'roc': 'Re{s} > 0'}
    ],
    'z_transform_table': [
        {'signal': 'delta[n]', 'transform': '1', 'roc': 'Entire z-plane'},
        {'signal': 'u[n]', 'transform': '1 / (1 - z^{-1}) = z / (z - 1)', 'roc': '|z| > 1'},
        {'signal': 'a^n u[n]', 'transform': '1 / (1 - a z^{-1}) = z / (z - a)', 'roc': '|z| > |a|'},
        {'signal': '-a^n u[-n-1]', 'transform': '1 / (1 - a z^{-1}) = z / (z - a)', 'roc': '|z| < |a|'},
        {'signal': 'n a^n u[n]', 'transform': 'a z^{-1} / (1 - a z^{-1})^2', 'roc': '|z| > |a|'},
        {'signal': 'cos(w_0 n) u[n]', 'transform': '(1 - cos(w_0) z^{-1}) / (1 - 2 cos(w_0) z^{-1} + z^{-2})', 'roc': '|z| > 1'}
    ]
}

with open(os.path.join(data_dir, 'reference_tables.json'), 'w', encoding='utf-8') as f:
    json.dump(reference_tables, f, indent=2)
print('reference_tables.json written')

# Search Index JSON
search_index = []
for fname in os.listdir(topics_dir):
    if fname.endswith('.json'):
        with open(os.path.join(topics_dir, fname), 'r', encoding='utf-8') as f:
            m = json.load(f)
            for top_id, top in m.get('topics', {}).items():
                search_index.append({
                    'id': top_id,
                    'title': top.get('title'),
                    'category': top.get('category'),
                    'summary': top.get('summary'),
                    'path': f"{fname}#{top_id}"
                })

with open(os.path.join(data_dir, 'search_index.json'), 'w', encoding='utf-8') as f:
    json.dump(search_index, f, indent=2)
print('search_index.json written')
