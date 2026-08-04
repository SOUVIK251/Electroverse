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
                'To plot $y(t) = x(t - t_0)$:\n'
                'Set argument $(t - t_0) = t_{old} \\Rightarrow t_{new} = t_{old} + t_0$. '
                'Every feature occurring at $t_{old}$ moves to $t_{old} + t_0$.'
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
                    'answer': 'Time shifting does NOT change the total energy or average power of a signal: E_{shifted} = E_{original}.'
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
                '1. **Time Scaling $x(at)$**:\n'
                '- If $|a| > 1$: Signal is **compressed** in time by factor $a$.\n'
                '- If $0 < |a| < 1$: Signal is **expanded** in time by factor $1/a$.\n\n'
                '2. **Time Folding $x(-t)$**:\n'
                '- Reflects the signal across the vertical axis $t = 0$.'
            ),
            'derivation': (
                '**Order of Operations Rule** for $y(t) = x(at - b)$:\n'
                '1. **Method A (Shift then Scale)**: $x(t) \\rightarrow x(t - b) \\rightarrow x(at - b)$.\n'
                '2. **Method B (Scale then Shift)**: $x(t) \\rightarrow x(at) \\rightarrow x(a(t - b/a)) = x(at - b)$.'
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
                'Any signal $x(t) = x_e(t) + x_o(t)$ where:\n\n'
                '$$x_e(t) = \\frac{x(t) + x(-t)}{2} \\quad (\\text{Even part: } x_e(-t) = x_e(t))$$\n\n'
                '$$x_o(t) = \\frac{x(t) - x(-t)}{2} \\quad (\\text{Odd part: } x_o(-t) = -x_o(t))$$'
            ),
            'derivation': (
                'Proof: $x_e(t) + x_o(t) = \\frac{x(t) + x(-t)}{2} + \\frac{x(t) - x(-t)}{2} = \\frac{2x(t)}{2} = x(t)$.'
            ),
            'important_formulas': [
                'x_e(t) = 0.5 * (x(t) + x(-t))',
                'x_o(t) = 0.5 * (x(t) - x(-t))',
                '\\int_{-T}^{T} x_o(t) dt = 0'
            ],
            'examples': [
                {
                    'problem': 'Find the even and odd parts of x(t) = e^{jt}.',
                    'solution': 'x_e(t) = (e^{jt} + e^{-jt})/2 = cos(t). x_o(t) = (e^{jt} - e^{-jt})/2 = j sin(t).'
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
                'A system $T$ is **Linear** if for inputs $x_1(t) \\rightarrow y_1(t)$ and $x_2(t) \\rightarrow y_2(t)$:\n\n'
                '$$T\\{a x_1(t) + b x_2(t)\\} = a T\\{x_1(t)\\} + b T\\{x_2(t)\\} = a y_1(t) + b y_2(t)$$'
            ),
            'derivation': (
                '**Test Procedure**:\n'
                '1. Compute $y_{combined}(t) = T\\{a x_1(t) + b x_2(t)\\}$.\n'
                '2. Compute $a y_1(t) + b y_2(t) = a T\\{x_1(t)\\} + b T\\{x_2(t)\\}$.\n'
                '3. Check if $y_{combined}(t) \\equiv a y_1(t) + b y_2(t)$. If YES -> Linear. If NO -> Nonlinear.'
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
                'A system $y(t) = T\\{x(t)\\}$ is **Time Invariant (TIV)** if:\n\n'
                '$$T\\{x(t - t_0)\\} = y(t - t_0)$$'
            ),
            'derivation': (
                '**Test Procedure**:\n'
                '1. **Shift Input**: Replace $x(t)$ with $x(t - t_0)$ to get $y(t, t_0)$.\n'
                '2. **Shift Output**: Replace $t$ with $(t - t_0)$ in the expression of $y(t)$ to get $y(t - t_0)$.\n'
                '3. Compare $y(t, t_0)$ and $y(t - t_0)$. If equal -> Time Invariant. If not -> Time Variant.'
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
                'If $|x(t)| \\le M_x < \\infty$, then $|y(t)| \\le M_y < \\infty$.\n'
                'For an LTI system with impulse response $h(t)$:\n'
                '$$\\int_{-\\infty}^{\\infty} |h(t)| dt < \\infty \\quad (\\text{Absolutely integrable impulse response})$$\n\n'
                '2. **Causality**:\n'
                'Output $y(t_0)$ depends ONLY on input $x(t)$ for $t \\le t_0$. For an LTI system, $h(t) = 0$ for $t < 0$.'
            ),
            'derivation': (
                '**Causality Check**:\n'
                '- $y(t) = x(t - 2)$: Causal (depends on past $t - 2$).\n'
                '- $y(t) = x(t + 1)$: Non-causal / Anti-causal (depends on future $t + 1$).\n'
                '- $y(t) = x(-t)$: Non-causal (for $t = -2$, $y(-2) = x(2)$ which is future).'
            ),
            'important_formulas': [
                '\\int_{-\\infty}^{\\infty} |h(t)| dt < \\infty \\quad (\\text{LTI BIBO Stability})',
                'h(t) = 0 \\text{ for } t < 0 \\quad (\\text{LTI Causality})'
            ],
            'examples': [
                {
                    'problem': 'Is the integrator y(t) = \\int_-inf^t x(tau) dtau BIBO stable?',
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
                'Where $x(t)$ is the input signal and $h(t)$ is the system impulse response.'
            ),
            'derivation': (
                '**Graphical Convolution Steps (The 4 Steps)**:\n\n'
                '1. **Change variable**: Express $x(t)$ as $x(\\tau)$ and $h(t)$ as $h(\\tau)$.\n'
                '2. **Time Fold**: Reflect $h(\\tau)$ to get $h(-\\tau)$.\n'
                '3. **Time Shift**: Shift $h(-\\tau)$ by $t$ to get $h(t - \\tau)$.\n'
                '4. **Multiply & Integrate**: Multiply $x(\\tau) h(t - \\tau)$ and compute the area under the product curve for varying $t$.'
            ),
            'important_formulas': [
                'y(t) = x(t) * h(t) = \\int_{-\\infty}^{\\infty} x(\\tau) h(t - \\tau) d\\tau',
                'x(t) * \\delta(t - t_0) = x(t - t_0)',
                '\\text{Duration of } y(t) = (T_{x1} + T_{h1}) \\le t \\le (T_{x2} + T_{h2})'
            ],
            'examples': [
                {
                    'problem': 'Convolve x(t) = u(t) with h(t) = e^{-a t} u(t) (a > 0).',
                    'solution': 'y(t) = \\int_0^t 1 * e^{-a(t-\\tau)} d\\tau = e^{-at} \\int_0^t e^{a\\tau} d\\tau = \\frac{1 - e^{-at}}{a} u(t).'
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
                'If $x[n]$ has length $N_1$ and $h[n]$ has length $N_2$, the output $y[n]$ has length:\n'
                '$$L = N_1 + N_2 - 1$$\n\n'
                '**Tabular Method (Matrix Multiplication)**:\n'
                'Arrange $x[k]$ as column and $h[n-k]$ as row, compute diagonal sums.'
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

# Write files for Module 1 to 4
for mod in [mod1, mod2, mod3, mod4]:
    fname = f"{mod['id']}_{mod['title'].split(':')[1].strip().lower().replace(' ', '_')}.json"
    if mod['id'] == 'module_1': fname = 'module_1_introduction.json'
    elif mod['id'] == 'module_2': fname = 'module_2_operations.json'
    elif mod['id'] == 'module_3': fname = 'module_3_systems.json'
    elif mod['id'] == 'module_4': fname = 'module_4_convolution.json'
    
    with open(os.path.join(topics_dir, fname), 'w', encoding='utf-8') as f:
        json.dump(mod, f, indent=2)
    print(f'Wrote {fname}')
"
