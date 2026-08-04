import numpy as np

class AnalogEngine:
    """Complete Engineering Math & Waveform Solver Engine for Analog Electronics."""

    @staticmethod
    def solve_clipper(vin_arr, vbias=3.0, mode="pos_series", vgamma=0.7):
        vout = vin_arr.copy()
        vclip = vbias + vgamma

        if "pos_series" in mode or mode == "pos_series":
            vout = np.minimum(vin_arr, vgamma)
        elif "neg_series" in mode or mode == "neg_series":
            vout = np.maximum(vin_arr, -vgamma)
        elif "pos_shunt" in mode or mode == "pos_shunt":
            vout = np.minimum(vin_arr, vgamma)
        elif "neg_shunt" in mode or mode == "neg_shunt":
            vout = np.maximum(vin_arr, -vgamma)
        elif "biased_pos" in mode or mode == "biased_pos":
            vout = np.minimum(vin_arr, vclip)
        elif "biased_neg" in mode or mode == "biased_neg":
            vout = np.maximum(vin_arr, -vclip)
        elif "combination" in mode or mode == "combination":
            vout = np.clip(vin_arr, -vclip, vclip)
        else:
            vout = np.minimum(vin_arr, vclip)

        v_peak = np.max(vout)
        v_rms = np.sqrt(np.mean(vout**2))
        v_avg = np.mean(vout)
        return vout, vclip, round(v_peak, 2), round(v_rms, 2), round(v_avg, 2)

    @staticmethod
    def solve_clamper(vin_arr, vbias=0.0, mode="pos"):
        vp = np.max(vin_arr)
        if "pos" in mode:
            vdc = vp + vbias
            vout = vin_arr + vdc
        else: # neg
            vdc = -(vp + vbias)
            vout = vin_arr + vdc

        v_peak = np.max(vout)
        v_avg = np.mean(vout)
        return vout, round(vdc, 2), round(v_peak, 2), round(v_avg, 2)

    @staticmethod
    def solve_rectifier(vin_arr, mode="bridge", filter_on=True, filter_c_uf=10.0, rl_k=1.0, freq=50):
        if mode == "half_wave":
            vout = np.maximum(0, vin_arr - 0.7)
            piv = np.max(vin_arr)
        elif mode == "center_tapped":
            vout = np.abs(vin_arr) - 0.7
            vout = np.maximum(0, vout)
            piv = 2 * np.max(vin_arr)
        else: # bridge
            vout = np.abs(vin_arr) - 1.4
            vout = np.maximum(0, vout)
            piv = np.max(vin_arr)

        if filter_on and filter_c_uf > 0:
            # Simple peak-hold smoothing approximation
            decay_factor = 1.0 / (freq * (rl_k * 1e3) * (filter_c_uf * 1e-6))
            ripple_p2p = (np.max(vout) * decay_factor) if decay_factor < 1.0 else np.max(vout)
            vdc = np.max(vout) - (ripple_p2p / 2.0)
            ripple = ripple_p2p / (2 * np.sqrt(3) * (vdc if vdc != 0 else 1))
        else:
            vdc = np.mean(vout)
            ripple = 1.21 if mode == "half_wave" else 0.482

        vrms = np.sqrt(np.mean(vout**2))
        efficiency = 40.6 if mode == "half_wave" else 81.2
        il_ma = (vdc / (rl_k * 1e3)) * 1000.0 if rl_k > 0 else 0.0

        return vout, round(vdc, 2), round(vrms, 2), round(ripple, 3), round(efficiency, 1), round(piv, 1), round(il_ma, 2)

    @staticmethod
    def solve_filter(mode="rc_low_pass", r_k=10.0, c_uf=0.1, l_mh=10.0):
        r_val = r_k * 1e3
        c_val = c_uf * 1e-6
        l_val = l_mh * 1e-3

        f_arr = np.logspace(1, 5, 300)
        w_arr = 2 * np.pi * f_arr

        if mode == "rc_low_pass":
            fc = 1.0 / (2 * np.pi * r_val * c_val)
            h_mag = 1.0 / np.sqrt(1 + (w_arr * r_val * c_val)**2)
            phase = -np.degrees(np.arctan(w_arr * r_val * c_val))
        elif mode == "rc_high_pass":
            fc = 1.0 / (2 * np.pi * r_val * c_val)
            h_mag = (w_arr * r_val * c_val) / np.sqrt(1 + (w_arr * r_val * c_val)**2)
            phase = 90 - np.degrees(np.arctan(w_arr * r_val * c_val))
        elif mode == "rl_low_pass":
            fc = r_val / (2 * np.pi * l_val)
            h_mag = r_val / np.sqrt(r_val**2 + (w_arr * l_val)**2)
            phase = -np.degrees(np.arctan((w_arr * l_val) / r_val))
        elif mode == "rl_high_pass":
            fc = r_val / (2 * np.pi * l_val)
            h_mag = (w_arr * l_val) / np.sqrt(r_val**2 + (w_arr * l_val)**2)
            phase = 90 - np.degrees(np.arctan((w_arr * l_val) / r_val))
        elif mode == "band_pass":
            fc = 1.0 / (2 * np.pi * np.sqrt(l_val * c_val))
            bw = r_val / (2 * np.pi * l_val)
            h_mag = (w_arr * (l_val / r_val)) / np.sqrt((1 - w_arr**2 * l_val * c_val)**2 + (w_arr * l_val / r_val)**2)
            phase = 90 - np.degrees(np.arctan(w_arr * l_val / r_val))
        elif mode == "band_reject":
            fc = 1.0 / (2 * np.pi * np.sqrt(l_val * c_val))
            h_mag = np.abs(1 - w_arr**2 * l_val * c_val) / np.sqrt((1 - w_arr**2 * l_val * c_val)**2 + (w_arr * l_val / r_val)**2)
            phase = np.degrees(np.arctan(w_arr * l_val / r_val))
        else: # all_pass
            fc = 1.0 / (2 * np.pi * r_val * c_val)
            h_mag = np.ones_like(f_arr)
            phase = -2 * np.degrees(np.arctan(w_arr * r_val * c_val))

        h_db = 20 * np.log10(np.maximum(1e-4, h_mag))
        return f_arr, h_db, phase, round(fc, 1)

    @staticmethod
    def solve_rc_transient(vs=10.0, r_k=10.0, c_uf=10.0):
        r_val = r_k * 1e3
        c_val = c_uf * 1e-6
        tau = r_val * c_val

        t = np.linspace(0, 5 * tau, 300)
        vc_charge = vs * (1 - np.exp(-t / tau))
        vc_discharge = vs * np.exp(-t / tau)
        ic_charge = (vs / r_val) * np.exp(-t / tau)
        energy_mJ = 0.5 * (c_val) * (vs**2) * 1000.0

        return t, vc_charge, vc_discharge, ic_charge, round(tau * 1000, 2), round(energy_mJ, 2)

    @staticmethod
    def solve_rl_transient(vs=10.0, r_k=1.0, l_mh=100.0):
        r_val = r_k * 1e3
        l_val = l_mh * 1e-3
        tau = l_val / r_val

        t = np.linspace(0, 5 * tau, 300)
        il_charge = (vs / r_val) * (1 - np.exp(-t / tau))
        vl_charge = vs * np.exp(-t / tau)
        i_final = vs / r_val
        energy_mJ = 0.5 * l_val * (i_final**2) * 1000.0

        return t, il_charge, vl_charge, round(tau * 1000, 3), round(energy_mJ, 3)

    @staticmethod
    def solve_rlc_resonance(mode="series", r_ohm=10.0, l_mh=10.0, c_uf=1.0, vs=10.0):
        l_h = l_mh * 1e-3
        c_f = c_uf * 1e-6

        fr = 1.0 / (2 * np.pi * np.sqrt(l_h * c_f))
        f_arr = np.linspace(fr * 0.2, fr * 2.0, 300)
        w_arr = 2 * np.pi * f_arr

        xl = w_arr * l_h
        xc = 1.0 / (w_arr * c_f)

        if mode == "series":
            z = np.sqrt(r_ohm**2 + (xl - xc)**2)
            i_arr = vs / z
            q_factor = (2 * np.pi * fr * l_h) / r_ohm if r_ohm != 0 else 0
            bw = fr / q_factor if q_factor != 0 else 0
            vr = i_arr * r_ohm
            vl = i_arr * xl
            vc = i_arr * xc
            phase_deg = np.degrees(np.arctan((xl - xc) / r_ohm))
            return f_arr, i_arr, z, round(fr, 1), round(q_factor, 2), round(bw, 1), round(np.max(vr), 2), round(np.max(vl), 2), round(np.max(vc), 2)
        else: # parallel
            y = np.sqrt((1 / r_ohm)**2 + (1 / xl - 1 / xc)**2)
            z = 1.0 / y
            i_arr = vs / z
            q_factor = r_ohm / (2 * np.pi * fr * l_h) if (2 * np.pi * fr * l_h) != 0 else 0
            bw = fr / q_factor if q_factor != 0 else 0
            return f_arr, i_arr, z, round(fr, 1), round(q_factor, 2), round(bw, 1), 0, 0, 0

    @staticmethod
    def solve_multivibrator(r_a_k=10.0, r_b_k=10.0, c_uf=0.1):
        ra = r_a_k * 1e3
        rb = r_b_k * 1e3
        c = c_uf * 1e-6

        freq = 1.44 / ((ra + 2 * rb) * c)
        duty = ((ra + rb) / (ra + 2 * rb)) * 100.0

        t = np.linspace(0, 3 / freq, 500) if freq > 0 else np.linspace(0, 0.01, 500)
        signal = np.where(np.sin(2 * np.pi * freq * t) >= 0, 5.0, 0.0)

        return t, signal, round(freq, 1), round(duty, 1)

    @staticmethod
    def get_hints_for_topic(topic_name, step_idx):
        hints_map = {
            "Clipper Circuits": [
                "Hint 1: A clipper circuit removes a portion of the input AC waveform above/below a threshold.",
                "Hint 2: Account for the diode barrier drop V_gamma (0.7V for Silicon) in series with bias V_B.",
                "Hint 3: Clipping threshold is V_clip = V_B + V_gamma."
            ],
            "Clamper Circuits": [
                "Hint 1: A clamper adds a DC voltage level shift to the input signal without changing its peak-to-peak amplitude.",
                "Hint 2: Capacitor charges to peak input voltage V_m during diode conduction.",
                "Hint 3: Total DC offset shift is V_dc = V_m - V_B."
            ]
        }
        hints = hints_map.get(topic_name, hints_map["Clipper Circuits"])
        return hints[min(step_idx, len(hints) - 1)]
