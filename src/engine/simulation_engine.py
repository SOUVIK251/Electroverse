import numpy as np

class BaseSimulation:
    """Base interface for all pure mathematical waveform simulations."""
    def __init__(self):
        # Default common parameters
        self.freq = 1000.0
        self.amp = 3.0
        self.offset = 0.0
        self.phase = 0.0
        self.noise_lvl = 0.0
        self.duty = 0.5
        
        # Default component parameters
        self.param_R = 1000.0
        self.param_C = 10e-6
        self.param_L = 10e-3
        self.param_Load = 10000.0
        self.param_Vcc = 5.0
        
        # Dual channel parameters
        self.ch1_type = "Sine"
        self.ch2_type = "Triangle"
        self.ch1_freq = 1000.0
        self.ch2_freq = 2000.0
        self.ch1_amp = 3.0
        self.ch2_amp = 2.0
        self.ch1_offset = 0.0
        self.ch2_offset = 0.0
        self.ch1_phase = 0.0
        self.ch2_phase = 0.0

    def update_parameters(self, **kwargs):
        """Standard interface to update parameters dynamically."""
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def reset(self):
        """Reset internal phase or timer states if needed."""
        pass

    def generate(self, time_array):
        """Generate CH1 and CH2 waveforms. Must return (ch1, ch2) numpy arrays."""
        raise NotImplementedError

    def get_channel_info(self):
        """Get default oscilloscope configurations for this simulation."""
        return {
            "ch1_label": "CH1",
            "ch2_label": "CH2",
            "recommended_tdiv": 0.001,
            "recommended_vdiv": 1.0,
            "recommended_vdiv_ch2": 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": 0.0,
            "ch1_enabled": True,
            "ch2_enabled": True
        }

    def get_measurements(self, t, ch1, ch2):
        """Optional mathematically expected measurements for verification."""
        return {}


class StandaloneSignalGenerator:
    """Helper class to generate standard signal generator waves."""
    @staticmethod
    def generate(t_array, sig_type, freq, amp, offset, phase, noise_lvl, duty=0.5):
        phi = np.radians(phase)
        if sig_type == "Sine":
            raw = offset + amp * np.sin(2.0 * np.pi * freq * t_array + phi)
        elif sig_type == "Square":
            raw = offset + amp * np.where(np.sin(2.0 * np.pi * freq * t_array + phi) >= 0, 1.0, -1.0)
        elif sig_type == "Triangle":
            raw = offset + 2.0 * amp * (2.0 * np.abs(((t_array * freq + phase / 360.0 - 0.25) % 1.0) - 0.5) - 0.5)
        elif sig_type == "Sawtooth":
            raw = offset + amp * (2.0 * ((t_array * freq + phase / 360.0) % 1.0) - 1.0)
        elif sig_type == "Pulse":
            raw = offset + amp * np.where(((t_array * freq + phase / 360.0) % 1.0) < duty, 1.0, -1.0)
        elif sig_type == "Noise":
            raw = offset + amp * np.random.uniform(-1.0, 1.0, len(t_array))
        else:
            raw = np.full_like(t_array, offset)

        if noise_lvl > 0 and sig_type != "Noise":
            raw += np.random.normal(0, noise_lvl * amp * 0.4, len(t_array))
        return raw


class StandaloneOscilloscopeSimulation(BaseSimulation):
    """Simulation representing the default Standalone DSO mode."""
    def generate(self, time_array):
        ch1 = StandaloneSignalGenerator.generate(
            time_array, self.ch1_type, self.ch1_freq,
            self.ch1_amp, self.ch1_offset, self.ch1_phase, self.noise_lvl, self.duty
        )
        ch2 = StandaloneSignalGenerator.generate(
            time_array, self.ch2_type, self.ch2_freq,
            self.ch2_amp, self.ch2_offset, self.ch2_phase, self.noise_lvl, self.duty
        )
        return ch1, ch2

    def get_channel_info(self):
        info = super().get_channel_info()
        info.update({
            "recommended_vdiv": self.ch1_amp / 3.0 if self.ch1_amp > 0 else 1.0,
            "recommended_vdiv_ch2": self.ch2_amp / 3.0 if self.ch2_amp > 0 else 1.0,
            "recommended_tdiv": 0.25 / self.ch1_freq if self.ch1_freq > 0 else 0.001
        })
        return info


class SignalGeneratorSimulation(BaseSimulation):
    """Signal Generator mode - CH1 only, CH2 grounded."""
    def generate(self, time_array):
        ch1 = StandaloneSignalGenerator.generate(
            time_array, self.ch1_type, self.ch1_freq,
            self.ch1_amp, self.ch1_offset, self.ch1_phase, self.noise_lvl, self.duty
        )
        ch2 = np.zeros_like(time_array)
        return ch1, ch2

    def get_channel_info(self):
        return {
            "ch1_label": f"Gen ({self.ch1_type})",
            "ch2_label": "GND",
            "recommended_tdiv": 0.25 / self.ch1_freq if self.ch1_freq > 0 else 0.001,
            "recommended_vdiv": self.ch1_amp / 3.0 if self.ch1_amp > 0 else 1.0,
            "recommended_vdiv_ch2": 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": self.ch1_offset,
            "ch1_enabled": True,
            "ch2_enabled": False
        }


class VoltageDividerSimulation(BaseSimulation):
    """Voltage Divider Transient Simulation."""
    def generate(self, time_array):
        ch1 = StandaloneSignalGenerator.generate(
            time_array, "Sine", self.freq, self.amp, self.offset, self.phase, self.noise_lvl
        )
        r1 = self.param_R
        r2 = self.param_Load
        gain = r2 / (r1 + r2) if (r1 + r2) > 0 else 1.0
        ch2 = ch1 * gain
        return ch1, ch2

    def get_channel_info(self):
        r1 = self.param_R
        r2 = self.param_Load
        gain = r2 / (r1 + r2) if (r1 + r2) > 0 else 1.0
        return {
            "ch1_label": "Vin (Input)",
            "ch2_label": "Vout (Divided)",
            "recommended_tdiv": 0.25 / self.freq if self.freq > 0 else 0.001,
            "recommended_vdiv": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_vdiv_ch2": (self.amp * gain) / 3.0 if (self.amp * gain) > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": self.offset,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class RCTransientSimulation(BaseSimulation):
    """RC Charging and Discharging transient response simulation."""
    def __init__(self, mode="Charging"):
        super().__init__()
        self.mode = mode

    def generate(self, time_array):
        r = self.param_R
        c = self.param_C
        tau = r * c
        vcc = self.param_Vcc
        period = max(0.001, 20.0 * tau)
        
        ch1 = []
        ch2 = []
        for t in time_array:
            t_cycle = t % period
            if self.mode == "Charging":
                if t_cycle < period / 2.0:
                    v_in = vcc
                    v_out = vcc * (1.0 - np.exp(-t_cycle / (tau if tau > 0 else 1e-6)))
                else:
                    v_in = 0.0
                    v_out = vcc * np.exp(-(t_cycle - period/2.0) / (tau if tau > 0 else 1e-6))
            else:  # Discharging mode
                v_in = vcc  # Supply voltage is constant Vcc
                if t_cycle < period / 2.0:
                    v_out = vcc * np.exp(-t_cycle / (tau if tau > 0 else 1e-6))
                else:
                    v_out = vcc * (1.0 - np.exp(-(t_cycle - period/2.0) / (tau if tau > 0 else 1e-6)))
            ch1.append(v_in)
            ch2.append(v_out)
            
        return np.array(ch1), np.array(ch2)

    def get_channel_info(self):
        tau = self.param_R * self.param_C
        vcc = self.param_Vcc
        return {
            "ch1_label": "Vin (Pulse)" if self.mode == "Charging" else "Vcc (Supply)",
            "ch2_label": "Vc (Capacitor)",
            "recommended_tdiv": tau,
            "recommended_vdiv": vcc / 3.0 if vcc > 0 else 1.0,
            "recommended_vdiv_ch2": vcc / 3.0 if vcc > 0 else 1.0,
            "recommended_trig_src": "CH1" if self.mode == "Charging" else "CH2",
            "recommended_trig_edge": "Rising" if self.mode == "Charging" else "Falling",
            "recommended_trig_level": vcc / 2.0 if self.mode == "Charging" else vcc * 0.9,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class RLTransientSimulation(BaseSimulation):
    """RL Transient response simulation (Inductor voltage)."""
    def generate(self, time_array):
        r = self.param_R
        l = self.param_L
        tau = l / r if r > 0 else 1e-6
        vcc = self.param_Vcc
        period = max(0.001, 20.0 * tau)
        
        ch1 = []
        ch2 = []
        for t in time_array:
            t_cycle = t % period
            if t_cycle < period / 2.0:
                v_in = vcc
                v_out = vcc * np.exp(-t_cycle / tau)
            else:
                v_in = 0.0
                v_out = -vcc * np.exp(-(t_cycle - period/2.0) / tau)
            ch1.append(v_in)
            ch2.append(v_out)
        return np.array(ch1), np.array(ch2)

    def get_channel_info(self):
        tau = self.param_L / self.param_R if self.param_R > 0 else 1e-6
        vcc = self.param_Vcc
        return {
            "ch1_label": "Vin (Pulse)",
            "ch2_label": "Vl (Inductor)",
            "recommended_tdiv": tau,
            "recommended_vdiv": vcc / 3.0 if vcc > 0 else 1.0,
            "recommended_vdiv_ch2": vcc / 3.0 if vcc > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": vcc / 2.0,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class RectifierSimulation(BaseSimulation):
    """Diode Rectifier Simulation (Half-Wave / Full-Wave)."""
    def __init__(self, mode="HalfWave"):
        super().__init__()
        self.mode = mode

    def generate(self, time_array):
        ch1 = StandaloneSignalGenerator.generate(
            time_array, "Sine", self.freq, self.amp, 0.0, self.phase, self.noise_lvl
        )
        if self.mode == "HalfWave":
            ch2 = np.maximum(0.0, ch1 - 0.7)  # Diode drop of 0.7V
        else:
            ch2 = np.maximum(0.0, np.abs(ch1) - 1.4)  # Bridge rectifier: two diode drops (1.4V)
        return ch1, ch2

    def get_channel_info(self):
        return {
            "ch1_label": "Vin (AC)",
            "ch2_label": "Vout (Rectified)",
            "recommended_tdiv": 0.25 / self.freq if self.freq > 0 else 0.001,
            "recommended_vdiv": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_vdiv_ch2": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": 0.0,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class ClipperSimulation(BaseSimulation):
    """Clipper Simulation (Positive / Negative)."""
    def __init__(self, mode="Positive"):
        super().__init__()
        self.mode = mode

    def generate(self, time_array):
        ch1 = StandaloneSignalGenerator.generate(
            time_array, "Sine", self.freq, self.amp, self.offset, self.phase, self.noise_lvl
        )
        v_clip = self.param_Vcc
        if self.mode == "Positive":
            ch2 = np.minimum(v_clip, ch1)
        else:
            ch2 = np.maximum(-v_clip, ch1)
        return ch1, ch2

    def get_channel_info(self):
        return {
            "ch1_label": "Vin (AC)",
            "ch2_label": "Vout (Clipped)",
            "recommended_tdiv": 0.25 / self.freq if self.freq > 0 else 0.001,
            "recommended_vdiv": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_vdiv_ch2": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": self.offset,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class ClamperSimulation(BaseSimulation):
    """Clamper Simulation (Positive / Negative)."""
    def __init__(self, mode="Positive"):
        super().__init__()
        self.mode = mode

    def generate(self, time_array):
        ch1 = StandaloneSignalGenerator.generate(
            time_array, "Sine", self.freq, self.amp, self.offset, self.phase, self.noise_lvl
        )
        # Shift positive peak or negative peak to diode drop offset
        v_diode = 0.7
        if self.mode == "Positive":
            # Clamps negative peak to -0.7V
            shift = self.amp - self.offset - v_diode
            ch2 = ch1 + shift
        else:
            # Clamps positive peak to 0.7V
            shift = self.amp + self.offset - v_diode
            ch2 = ch1 - shift
        return ch1, ch2

    def get_channel_info(self):
        return {
            "ch1_label": "Vin (AC)",
            "ch2_label": "Vout (Clamped)",
            "recommended_tdiv": 0.25 / self.freq if self.freq > 0 else 0.001,
            "recommended_vdiv": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_vdiv_ch2": self.amp / 1.5 if self.amp > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": self.offset,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class AttenuatorSimulation(BaseSimulation):
    """Signal Attenuation Simulation."""
    def generate(self, time_array):
        ch1 = StandaloneSignalGenerator.generate(
            time_array, "Sine", self.freq, self.amp, self.offset, self.phase, self.noise_lvl
        )
        r = self.param_R
        rl = self.param_Load
        gain = rl / (r + rl) if (r + rl) > 0 else 1.0
        ch2 = ch1 * gain
        return ch1, ch2

    def get_channel_info(self):
        r = self.param_R
        rl = self.param_Load
        gain = rl / (r + rl) if (r + rl) > 0 else 1.0
        return {
            "ch1_label": "Vin (Original)",
            "ch2_label": "Vout (Attenuated)",
            "recommended_tdiv": 0.25 / self.freq if self.freq > 0 else 0.001,
            "recommended_vdiv": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_vdiv_ch2": (self.amp * gain) / 3.0 if (self.amp * gain) > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": self.offset,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class FilterSimulation(BaseSimulation):
    """RC Low-Pass and High-Pass Filter Simulation."""
    def __init__(self, mode="LowPass"):
        super().__init__()
        self.mode = mode

    def generate(self, time_array):
        r = self.param_R
        c = self.param_C
        fc = 1.0 / (2.0 * np.pi * r * c) if (r * c) > 0 else 1000.0
        
        ch1 = StandaloneSignalGenerator.generate(
            time_array, "Sine", self.freq, self.amp, self.offset, self.phase, self.noise_lvl
        )
        
        f = self.freq
        if self.mode == "LowPass":
            gain = 1.0 / np.sqrt(1.0 + (f / fc)**2)
            phase_shift = -np.arctan2(f, fc)
        else:
            gain = (f / fc) / np.sqrt(1.0 + (f / fc)**2)
            phase_shift = np.arctan2(fc, f)
            
        t_shift = phase_shift / (2.0 * np.pi * f) if f > 0 else 0.0
        
        ch2 = StandaloneSignalGenerator.generate(
            time_array + t_shift, "Sine", self.freq,
            self.amp * gain, self.offset * gain, self.phase, self.noise_lvl
        )
        return ch1, ch2

    def get_channel_info(self):
        r = self.param_R
        c = self.param_C
        fc = 1.0 / (2.0 * np.pi * r * c) if (r * c) > 0 else 1000.0
        f = self.freq
        gain = 1.0 / np.sqrt(1.0 + (f / fc)**2) if self.mode == "LowPass" else (f / fc) / np.sqrt(1.0 + (f / fc)**2)
        return {
            "ch1_label": "Vin (Input)",
            "ch2_label": "Vout (Filtered)",
            "recommended_tdiv": 0.25 / self.freq if self.freq > 0 else 0.001,
            "recommended_vdiv": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_vdiv_ch2": (self.amp * gain) / 3.0 if (self.amp * gain) > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": self.offset,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class ResonanceSimulation(BaseSimulation):
    """Series RLC Resonance Simulation."""
    def generate(self, time_array):
        r = self.param_R
        l = self.param_L
        c = self.param_C
        
        f0 = 1.0 / (2.0 * np.pi * np.sqrt(l * c)) if (l * c) > 0 else 1000.0
        f = self.freq
        
        xl = 2.0 * np.pi * f * l
        xc = 1.0 / (2.0 * np.pi * f * c) if c > 0 else 0.0
        z = np.sqrt(r**2 + (xl - xc)**2)
        
        gain = r / z if z > 0 else 1.0
        phase = -np.arctan2((xl - xc), r)
        
        ch1 = StandaloneSignalGenerator.generate(
            time_array, "Sine", f, self.amp, self.offset, self.phase, self.noise_lvl
        )
        t_shift = phase / (2.0 * np.pi * f) if f > 0 else 0.0
        ch2 = StandaloneSignalGenerator.generate(
            time_array + t_shift, "Sine", f, self.amp * gain, self.offset * gain, self.phase, self.noise_lvl
        )
        return ch1, ch2

    def get_channel_info(self):
        r = self.param_R
        l = self.param_L
        c = self.param_C
        f = self.freq
        xl = 2.0 * np.pi * f * l
        xc = 1.0 / (2.0 * np.pi * f * c) if c > 0 else 0.0
        z = np.sqrt(r**2 + (xl - xc)**2)
        gain = r / z if z > 0 else 1.0
        return {
            "ch1_label": "Vin (Input)",
            "ch2_label": "Vr (Resistor)",
            "recommended_tdiv": 0.25 / self.freq if self.freq > 0 else 0.001,
            "recommended_vdiv": self.amp / 3.0 if self.amp > 0 else 1.0,
            "recommended_vdiv_ch2": (self.amp * gain) / 3.0 if (self.amp * gain) > 0 else 1.0,
            "recommended_trig_src": "CH1",
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": self.offset,
            "ch1_enabled": True,
            "ch2_enabled": True
        }


class CommunicationSimulation(BaseSimulation):
    """AM, FM, ASK, FSK, PSK, BPSK, QPSK Modulation Simulation."""
    def __init__(self, mode="AM"):
        super().__init__()
        self.mode = mode

    def generate(self, time_array):
        fm = self.ch1_freq
        fc = self.ch2_freq
        am_index = 0.7
        
        if self.mode == "AM":
            # CH1: Carrier wave (fc)
            ch1 = np.sin(2.0 * np.pi * fc * time_array) * self.ch1_amp
            # CH2: AM modulated wave (carrier envelope tracks the modulator wave fm)
            modulator = 1.0 + am_index * np.sin(2.0 * np.pi * fm * time_array)
            ch2 = modulator * np.sin(2.0 * np.pi * fc * time_array) * self.ch2_amp
        elif self.mode == "FM":
            # CH1: Carrier wave (fc)
            ch1 = np.sin(2.0 * np.pi * fc * time_array) * self.ch1_amp
            # CH2: FM modulated wave (modulator fm varies carrier fc frequency)
            beta = 5.0  # modulation index
            ch2 = np.sin(2.0 * np.pi * fc * time_array + beta * np.sin(2.0 * np.pi * fm * time_array)) * self.ch2_amp
        elif self.mode == "ASK":
            # CH1: Binary Data (fm bits)
            ch1 = np.where(np.sin(2.0 * np.pi * fm * time_array) >= 0, 5.0, 0.0)
            # CH2: ASK output (carrier switches ON when bit is 1, OFF when 0)
            ch2 = np.where(ch1 > 2.5, np.sin(2.0 * np.pi * fc * time_array) * self.ch2_amp, 0.0)
        elif self.mode == "FSK":
            # CH1: Binary Data (fm bits)
            ch1 = np.where(np.sin(2.0 * np.pi * fm * time_array) >= 0, 5.0, 0.0)
            # CH2: Phase-Continuous FSK output
            f1 = fc
            f2 = fc * 2.0
            Tm = 1.0 / fm
            N = np.floor(time_array / Tm)
            t_cycle = time_array % Tm
            phi_cycle = np.pi * Tm * (f1 + f2)
            phi_frac = np.where(t_cycle < Tm / 2.0, 
                                2.0 * np.pi * f2 * t_cycle, 
                                np.pi * f2 * Tm + 2.0 * np.pi * f1 * (t_cycle - Tm / 2.0))
            phase = N * phi_cycle + phi_frac
            ch2 = np.sin(phase) * self.ch2_amp
        elif self.mode == "PSK":
            # CH1: Binary Data
            ch1 = np.where(np.sin(2.0 * np.pi * fm * time_array) >= 0, 5.0, 0.0)
            # CH2: PSK output (phase shift of 90 degrees when data is 0)
            phase = np.where(ch1 > 2.5, 0.0, np.pi / 2.0)
            ch2 = np.sin(2.0 * np.pi * fc * time_array + phase) * self.ch2_amp
        elif self.mode == "BPSK":
            # CH1: Binary Data
            ch1 = np.where(np.sin(2.0 * np.pi * fm * time_array) >= 0, 5.0, 0.0)
            # CH2: BPSK output (180 degrees phase shift when data is 0)
            phase = np.where(ch1 > 2.5, 0.0, np.pi)
            ch2 = np.sin(2.0 * np.pi * fc * time_array + phase) * self.ch2_amp
        elif self.mode == "QPSK":
            # CH1: I Channel (binary modulated carrier)
            i_data = np.where(np.sin(2.0 * np.pi * (fm / 2.0) * time_array) >= 0, 1.0, -1.0)
            # CH2: Q Channel (binary modulated quadrature carrier)
            q_data = np.where(np.cos(2.0 * np.pi * (fm / 2.0) * time_array) >= 0, 1.0, -1.0)
            ch1 = i_data * np.cos(2.0 * np.pi * fc * time_array) * self.ch1_amp
            ch2 = q_data * np.sin(2.0 * np.pi * fc * time_array) * self.ch2_amp
        else:
            ch1 = np.zeros_like(time_array)
            ch2 = np.zeros_like(time_array)
            
        return ch1, ch2

    def get_channel_info(self):
        fm = self.ch1_freq
        trig_src = "CH1"
        trig_lvl = 2.5 if self.mode in ["ASK", "FSK", "PSK", "BPSK"] else 0.0
        return {
            "ch1_label": "Carrier" if self.mode in ["AM", "FM"] else ("I Channel" if self.mode == "QPSK" else "Data"),
            "ch2_label": "Modulated" if self.mode != "QPSK" else "Q Channel",
            "recommended_tdiv": 0.25 / fm if fm > 0 else 0.001,
            "recommended_vdiv": max(self.ch1_amp, 5.0) / 3.0 if self.ch1_amp > 0 else 2.0,
            "recommended_vdiv_ch2": self.ch2_amp / 3.0 if self.ch2_amp > 0 else 1.0,
            "recommended_trig_src": trig_src,
            "recommended_trig_edge": "Rising",
            "recommended_trig_level": trig_lvl,
            "ch1_enabled": True,
            "ch2_enabled": True
        }
