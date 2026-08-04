"""
ElectroVerse Professional Electrical Network Theory Engine
Comprehensive 30-Solver Mathematical Computation Backend for Network Theory & Circuit Analysis.
"""

import math
import numpy as np
from typing import Dict, Any, List, Tuple


class NetworkEngine:
    """Core Electrical Network Theory Solver Engine supporting 30 professional solvers."""

    # 1. Ohm's Law & Power
    @staticmethod
    def solve_ohms_law(v=None, i=None, r=None) -> Dict[str, Any]:
        if v is None and i is not None and r is not None:
            v = i * r
        elif i is None and v is not None and r is not None:
            i = v / r if r != 0 else 0.0
        elif r is None and v is not None and i is not None:
            r = v / i if i != 0 else 0.0

        p = (v * i) if (v is not None and i is not None) else 0.0
        p_r = (i ** 2 * r) if (i is not None and r is not None) else 0.0
        p_v = (v ** 2 / r) if (v is not None and r is not None and r != 0) else 0.0

        return {
            "v": round(v or 0.0, 4),
            "i": round(i or 0.0, 4),
            "r": round(r or 0.0, 4),
            "p": round(p or p_r or p_v, 4)
        }

    # 2. KCL Solver
    @staticmethod
    def solve_kcl(currents_in: List[float], currents_out: List[float]) -> Dict[str, Any]:
        sum_in = sum(currents_in)
        sum_out = sum(currents_out)
        diff = sum_in - sum_out
        is_balanced = math.isclose(sum_in, sum_out, rel_tol=1e-5, abs_tol=1e-5)
        return {
            "sum_in": round(sum_in, 4),
            "sum_out": round(sum_out, 4),
            "diff": round(diff, 4),
            "is_balanced": is_balanced,
            "unknown_branch_required": round(abs(diff), 4)
        }

    # 3. KVL Solver
    @staticmethod
    def solve_kvl(sources: List[float], drops: List[float]) -> Dict[str, Any]:
        sum_sources = sum(sources)
        sum_drops = sum(drops)
        net_voltage = sum_sources - sum_drops
        is_balanced = math.isclose(sum_sources, sum_drops, rel_tol=1e-5, abs_tol=1e-5)
        return {
            "sum_sources": round(sum_sources, 4),
            "sum_drops": round(sum_drops, 4),
            "net_voltage": round(net_voltage, 4),
            "is_balanced": is_balanced
        }

    # 4. Series Circuit Solver
    @staticmethod
    def solve_series(vs: float, resistors: List[float]) -> Dict[str, Any]:
        req = sum(resistors)
        current = vs / req if req != 0 else 0.0
        v_drops = [current * r for r in resistors]
        p_drops = [current**2 * r for r in resistors]
        total_p = vs * current
        return {
            "req": round(req, 4),
            "current": round(current, 4),
            "v_drops": [round(v, 4) for v in v_drops],
            "p_drops": [round(p, 4) for p in p_drops],
            "total_power": round(total_p, 4)
        }

    # 5. Parallel Circuit Solver
    @staticmethod
    def solve_parallel(vs: float, resistors: List[float]) -> Dict[str, Any]:
        inv_sum = sum([1.0 / r for r in resistors if r != 0])
        req = 1.0 / inv_sum if inv_sum != 0 else 0.0
        currents = [vs / r if r != 0 else 0.0 for r in resistors]
        total_i = sum(currents)
        p_drops = [vs * i for i in currents]
        total_p = vs * total_i
        return {
            "req": round(req, 4),
            "total_current": round(total_i, 4),
            "branch_currents": [round(i, 4) for i in currents],
            "p_drops": [round(p, 4) for p in p_drops],
            "total_power": round(total_p, 4)
        }

    # 6. Voltage Divider Calculator
    @staticmethod
    def solve_voltage_divider(vin: float, r1: float, r2: float) -> Dict[str, Any]:
        r_total = r1 + r2
        vout = vin * (r2 / r_total) if r_total != 0 else 0.0
        ratio = r2 / r_total if r_total != 0 else 0.0
        return {
            "vout": round(vout, 4),
            "ratio": round(ratio, 4),
            "v_r1": round(vin - vout, 4)
        }

    # 7. Current Divider Calculator
    @staticmethod
    def solve_current_divider(itotal: float, r1: float, r2: float) -> Dict[str, Any]:
        r_sum = r1 + r2
        i1 = itotal * (r2 / r_sum) if r_sum != 0 else 0.0
        i2 = itotal * (r1 / r_sum) if r_sum != 0 else 0.0
        return {
            "i1": round(i1, 4),
            "i2": round(i2, 4)
        }

    # 8. Mesh Analysis Solver (2-Loop)
    @staticmethod
    def solve_mesh_analysis(vs1: float, r1: float, rm: float, r2: float, vs2: float) -> Dict[str, Any]:
        A = np.array([
            [r1 + rm, -rm],
            [-rm, r2 + rm]
        ])
        B = np.array([vs1, -vs2])
        try:
            I = np.linalg.solve(A, B)
            i1, i2 = I[0], I[1]
            irm = i1 - i2
            return {
                "i1": round(i1, 4),
                "i2": round(i2, 4),
                "irm": round(irm, 4),
                "p_rm": round(irm**2 * rm, 4)
            }
        except np.linalg.LinAlgError:
            return {"i1": 0.0, "i2": 0.0, "irm": 0.0, "p_rm": 0.0}

    # 9. Nodal Analysis Solver (2-Node)
    @staticmethod
    def solve_nodal_analysis(is1: float, r1: float, rm: float, r2: float, is2: float) -> Dict[str, Any]:
        g1, gm, g2 = 1.0/r1 if r1!=0 else 0, 1.0/rm if rm!=0 else 0, 1.0/r2 if r2!=0 else 0
        A = np.array([
            [g1 + gm, -gm],
            [-gm, g2 + gm]
        ])
        B = np.array([is1, -is2])
        try:
            V = np.linalg.solve(A, B)
            v1, v2 = V[0], V[1]
            v_rm = v1 - v2
            return {
                "v1": round(v1, 4),
                "v2": round(v2, 4),
                "v_rm": round(v_rm, 4),
                "i_rm": round(v_rm * gm, 4)
            }
        except np.linalg.LinAlgError:
            return {"v1": 0.0, "v2": 0.0, "v_rm": 0.0, "i_rm": 0.0}

    # 10. Source Transformation Solver
    @staticmethod
    def solve_source_transformation(val: float, r_s: float, from_voltage: bool = True) -> Dict[str, Any]:
        if from_voltage:
            vs = val
            is_src = vs / r_s if r_s != 0 else 0.0
            return {"vs": round(vs, 4), "is_src": round(is_src, 4), "r_s": round(r_s, 4), "mode": "V -> I"}
        else:
            is_src = val
            vs = is_src * r_s
            return {"vs": round(vs, 4), "is_src": round(is_src, 4), "r_s": round(r_s, 4), "mode": "I -> V"}

    # 11. Thevenin's Theorem Solver
    @staticmethod
    def solve_thevenin(vs: float, r1: float, r2: float, rl: float) -> Dict[str, Any]:
        vth = vs * (r2 / (r1 + r2)) if (r1 + r2) != 0 else 0.0
        rth = (r1 * r2) / (r1 + r2) if (r1 + r2) != 0 else 0.0
        il = vth / (rth + rl) if (rth + rl) != 0 else 0.0
        vl = il * rl
        pl = (il ** 2) * rl
        pmax = (vth ** 2) / (4.0 * rth) if rth != 0 else 0.0

        return {
            "vth": round(vth, 4),
            "rth": round(rth, 4),
            "il": round(il, 4),
            "vl": round(vl, 4),
            "pl": round(pl, 4),
            "pmax": round(pmax, 4)
        }

    # 12. Norton's Theorem Solver
    @staticmethod
    def solve_norton(vs: float, r1: float, r2: float, rl: float) -> Dict[str, Any]:
        in_src = vs / r1 if r1 != 0 else 0.0
        rn = (r1 * r2) / (r1 + r2) if (r1 + r2) != 0 else 0.0
        il = in_src * (rn / (rn + rl)) if (rn + rl) != 0 else 0.0
        vl = il * rl
        pl = il**2 * rl

        return {
            "in_src": round(in_src, 4),
            "rn": round(rn, 4),
            "il": round(il, 4),
            "vl": round(vl, 4),
            "pl": round(pl, 4)
        }

    # 13. Superposition Theorem Solver
    @staticmethod
    def solve_superposition(v1: float, v2: float, r1: float, r2: float, rl: float) -> Dict[str, Any]:
        r2_rl = (r2 * rl) / (r2 + rl) if (r2 + rl) != 0 else 0.0
        i_total1 = v1 / (r1 + r2_rl) if (r1 + r2_rl) != 0 else 0.0
        i_l1 = i_total1 * (r2 / (r2 + rl)) if (r2 + rl) != 0 else 0.0

        r1_rl = (r1 * rl) / (r1 + rl) if (r1 + rl) != 0 else 0.0
        i_total2 = v2 / (r2 + r1_rl) if (r2 + r1_rl) != 0 else 0.0
        i_l2 = i_total2 * (r1 / (r1 + rl)) if (r1 + rl) != 0 else 0.0

        i_total = i_l1 + i_l2
        return {
            "il_v1_only": round(i_l1, 4),
            "il_v2_only": round(i_l2, 4),
            "il_total": round(i_total, 4)
        }

    # 14. Maximum Power Transfer Solver
    @staticmethod
    def solve_max_power_transfer(vth: float, rth: float, rl: float) -> Dict[str, Any]:
        rl_opt = rth
        pmax = (vth ** 2) / (4.0 * rth) if rth != 0 else 0.0
        il = vth / (rth + rl) if (rth + rl) != 0 else 0.0
        pl = il**2 * rl
        eta = (rl / (rth + rl)) * 100.0 if (rth + rl) != 0 else 0.0

        return {
            "rl_opt": round(rl_opt, 4),
            "pmax": round(pmax, 4),
            "pl": round(pl, 4),
            "efficiency_pct": round(eta, 2)
        }

    # 15. Millman's Theorem Solver
    @staticmethod
    def solve_millman(e1: float, r1: float, e2: float, r2: float, e3: float, r3: float) -> Dict[str, Any]:
        num = (e1/r1 if r1!=0 else 0) + (e2/r2 if r2!=0 else 0) + (e3/r3 if r3!=0 else 0)
        den = (1.0/r1 if r1!=0 else 0) + (1.0/r2 if r2!=0 else 0) + (1.0/r3 if r3!=0 else 0)
        v_millman = num / den if den != 0 else 0.0
        r_millman = 1.0 / den if den != 0 else 0.0
        return {
            "v_millman": round(v_millman, 4),
            "r_millman": round(r_millman, 4)
        }

    # 16. Reciprocity Theorem Checker
    @staticmethod
    def solve_reciprocity(vs: float, r1: float, r2: float, r3: float) -> Dict[str, Any]:
        req1 = r1 + (r2 * r3) / (r2 + r3) if (r2 + r3) != 0 else r1
        is1 = vs / req1 if req1 != 0 else 0.0
        i_out1 = is1 * (r2 / (r2 + r3)) if (r2 + r3) != 0 else 0.0

        req2 = r3 + (r1 * r2) / (r1 + r2) if (r1 + r2) != 0 else r3
        is2 = vs / req2 if req2 != 0 else 0.0
        i_out2 = is2 * (r2 / (r1 + r2)) if (r1 + r2) != 0 else 0.0

        is_verified = math.isclose(i_out1, i_out2, rel_tol=1e-4)
        return {
            "i_out1": round(i_out1, 4),
            "i_out2": round(i_out2, 4),
            "transfer_impedance": round(vs / i_out1 if i_out1 != 0 else 0.0, 4),
            "is_verified": is_verified
        }

    # 17. Compensation Theorem Solver
    @staticmethod
    def solve_compensation(i_orig: float, delta_r: float, rth: float, r_orig: float) -> Dict[str, Any]:
        v_comp = i_orig * delta_r
        delta_i = v_comp / (rth + r_orig + delta_r) if (rth + r_orig + delta_r) != 0 else 0.0
        i_new = i_orig - delta_i
        return {
            "v_comp": round(v_comp, 4),
            "delta_i": round(delta_i, 4),
            "i_new": round(i_new, 4)
        }

    # 18. Tellegen's Theorem Verification
    @staticmethod
    def solve_tellegen(p1: float, p2: float, p3: float, p4: float) -> Dict[str, Any]:
        total_p = p1 + p2 + p3 + p4
        is_verified = math.isclose(total_p, 0.0, abs_tol=1e-4)
        return {
            "total_power": round(total_p, 4),
            "is_verified": is_verified
        }

    # 19. Delta-Star Conversion
    @staticmethod
    def solve_delta_star(r12: float, r23: float, r31: float, to_star: bool = True) -> Dict[str, Any]:
        if to_star:
            denom = r12 + r23 + r31
            r1 = (r12 * r31) / denom if denom != 0 else 0.0
            r2 = (r12 * r23) / denom if denom != 0 else 0.0
            r3 = (r23 * r31) / denom if denom != 0 else 0.0
            return {"r1": round(r1, 4), "r2": round(r2, 4), "r3": round(r3, 4), "mode": "Delta -> Star"}
        else:
            ra, rb, rc = r12, r23, r31
            num = ra*rb + rb*rc + rc*ra
            r12_out = num / rc if rc != 0 else 0.0
            r23_out = num / ra if ra != 0 else 0.0
            r31_out = num / rb if rb != 0 else 0.0
            return {"r12": round(r12_out, 4), "r23": round(r23_out, 4), "r31": round(r31_out, 4), "mode": "Star -> Delta"}

    # 20. Bridge Network Solver (Wheatstone)
    @staticmethod
    def solve_bridge(vs: float, r1: float, r2: float, r3: float, r4: float, rg: float) -> Dict[str, Any]:
        is_balanced = math.isclose(r1 * r4, r2 * r3, rel_tol=1e-4)
        v_cd = vs * ((r3 / (r1 + r3)) - (r4 / (r2 + r4))) if (r1+r3)!=0 and (r2+r4)!=0 else 0.0
        r_eq_c = (r1*r3)/(r1+r3) + (r2*r4)/(r2+r4) if (r1+r3)!=0 and (r2+r4)!=0 else 0.0
        ig = v_cd / (r_eq_c + rg) if (r_eq_c + rg) != 0 else 0.0
        rx_calc = (r2 * r3) / r1 if r1 != 0 else 0.0

        return {
            "is_balanced": is_balanced,
            "v_cd": round(v_cd, 4),
            "ig": round(ig, 4),
            "rx_calc": round(rx_calc, 4)
        }

    # 21. Resonance Calculator (RLC)
    @staticmethod
    def solve_resonance(r: float, l: float, c: float) -> Dict[str, Any]:
        fr = 1.0 / (2.0 * math.pi * math.sqrt(l * c)) if (l > 0 and c > 0) else 0.0
        w0 = 2.0 * math.pi * fr
        q = (w0 * l) / r if r != 0 else 0.0
        bw = fr / q if q != 0 else 0.0
        z_res = r
        return {
            "fr_hz": round(fr, 2),
            "w0_rad": round(w0, 2),
            "q_factor": round(q, 2),
            "bandwidth_hz": round(bw, 2),
            "z_res": round(z_res, 2)
        }

    # 22. Quality Factor Calculator
    @staticmethod
    def solve_quality_factor(f: float, l: float, c: float, r: float) -> Dict[str, Any]:
        w = 2.0 * math.pi * f
        q_series = (w * l) / r if r != 0 else 0.0
        q_parallel = r / (w * l) if (w * l) != 0 else 0.0
        return {
            "q_series": round(q_series, 2),
            "q_parallel": round(q_parallel, 2)
        }

    # 23. Time Constant Calculator
    @staticmethod
    def solve_time_constant(r: float, c: float, l: float) -> Dict[str, Any]:
        tau_rc = r * c
        tau_rl = l / r if r != 0 else 0.0
        return {
            "tau_rc_ms": round(tau_rc * 1000.0, 4),
            "tau_rl_ms": round(tau_rl * 1000.0, 4),
            "settling_5tau_rc_ms": round(5.0 * tau_rc * 1000.0, 4)
        }

    # 24. AC Impedance Calculator
    @staticmethod
    def solve_ac_impedance(f: float, r: float, l: float, c: float) -> Dict[str, Any]:
        w = 2.0 * math.pi * f
        xl = w * l
        xc = 1.0 / (w * c) if (w * c) != 0 else 0.0
        x_net = xl - xc
        z = math.sqrt(r**2 + x_net**2)
        theta_rad = math.atan2(x_net, r)
        theta_deg = math.degrees(theta_rad)
        pf = math.cos(theta_rad)

        return {
            "xl": round(xl, 4),
            "xc": round(xc, 4),
            "z_mag": round(z, 4),
            "theta_deg": round(theta_deg, 2),
            "pf": round(pf, 4)
        }

    # 25. Power Factor Calculator
    @staticmethod
    def solve_power_factor(v: float, i: float, pf_curr: float, pf_target: float, f: float) -> Dict[str, Any]:
        s = v * i
        p = s * pf_curr
        q1 = math.sqrt(max(0, s**2 - p**2))

        theta1 = math.acos(min(1.0, max(0.0, pf_curr)))
        theta2 = math.acos(min(1.0, max(0.0, pf_target)))

        qc = p * (math.tan(theta1) - math.tan(theta2))
        c_req = qc / (2.0 * math.pi * f * (v**2)) if (v != 0 and f != 0) else 0.0

        return {
            "real_power_p": round(p, 2),
            "reactive_power_q": round(q1, 2),
            "apparent_power_s": round(s, 2),
            "c_req_uf": round(c_req * 1e6, 4)
        }

    # 26. RMS / Average Calculator
    @staticmethod
    def solve_rms_average(vm: float, wave_type: str = "sine") -> Dict[str, Any]:
        w = wave_type.lower()
        if "sine" in w:
            v_rms = vm / math.sqrt(2)
            v_avg = (2.0 * vm) / math.pi
        elif "square" in w:
            v_rms = vm
            v_avg = vm
        elif "triangle" in w or "sawtooth" in w:
            v_rms = vm / math.sqrt(3)
            v_avg = vm / 2.0
        elif "half" in w:
            v_rms = vm / 2.0
            v_avg = vm / math.pi
        else: # full wave
            v_rms = vm / math.sqrt(2)
            v_avg = (2.0 * vm) / math.pi

        form_factor = v_rms / v_avg if v_avg != 0 else 0.0
        peak_factor = vm / v_rms if v_rms != 0 else 0.0

        return {
            "v_rms": round(v_rms, 4),
            "v_avg": round(v_avg, 4),
            "form_factor": round(form_factor, 4),
            "peak_factor": round(peak_factor, 4)
        }

    # 27. Phasor Calculator
    @staticmethod
    def solve_phasor(r1: float, i1: float, r2: float, i2: float, op: str = "+") -> Dict[str, Any]:
        c1 = complex(r1, i1)
        c2 = complex(r2, i2)

        if op == "+":
            res = c1 + c2
        elif op == "-":
            res = c1 - c2
        elif op == "*":
            res = c1 * c2
        else:
            res = c1 / c2 if c2 != 0 else complex(0, 0)

        mag = abs(res)
        ang_deg = math.degrees(math.atan2(res.imag, res.real))

        return {
            "rect_real": round(res.real, 4),
            "rect_imag": round(res.imag, 4),
            "polar_mag": round(mag, 4),
            "polar_ang_deg": round(ang_deg, 2)
        }

    # 28. Laplace Circuit Solver
    @staticmethod
    def solve_laplace_circuit(r: float, l: float, c: float, s_val: float) -> Dict[str, Any]:
        z_r = r
        z_l = s_val * l
        z_c = 1.0 / (s_val * c) if (s_val * c) != 0 else 0.0
        z_total_series = z_r + z_l + z_c
        return {
            "z_r_s": round(z_r, 4),
            "z_l_s": round(z_l, 4),
            "z_c_s": round(z_c, 4),
            "z_total_series": round(z_total_series, 4)
        }

    # 29. Two-Port Network Calculator
    @staticmethod
    def solve_two_port(z11: float, z12: float, z21: float, z22: float) -> Dict[str, Any]:
        det_z = z11 * z22 - z12 * z21
        if det_z != 0:
            y11 = z22 / det_z
            y12 = -z12 / det_z
            y21 = -z21 / det_z
            y22 = z11 / det_z
        else:
            y11 = y12 = y21 = y22 = 0.0

        a_param = z11 / z21 if z21 != 0 else 0.0
        b_param = det_z / z21 if z21 != 0 else 0.0
        c_param = 1.0 / z21 if z21 != 0 else 0.0
        d_param = z22 / z21 if z21 != 0 else 0.0

        return {
            "det_z": round(det_z, 4),
            "y11": round(y11, 4), "y12": round(y12, 4),
            "y21": round(y21, 4), "y22": round(y22, 4),
            "A": round(a_param, 4), "B": round(b_param, 4),
            "C": round(c_param, 4), "D": round(d_param, 4)
        }

    # 30. Unit Converter
    @staticmethod
    def convert_electrical_units(val: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        multipliers = {
            "Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6,
            "mA": 1e-3, "A": 1.0,
            "pF": 1e-12, "nF": 1e-9, "μF": 1e-6, "F": 1.0,
            "mH": 1e-3, "H": 1.0,
            "Hz": 1.0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9
        }

        mult_from = multipliers.get(from_unit, 1.0)
        mult_to = multipliers.get(to_unit, 1.0)

        base_val = val * mult_from
        converted = base_val / mult_to if mult_to != 0 else 0.0

        return {
            "val": val,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "base_si_value": base_val,
            "converted_value": round(converted, 6)
        }

    # Helper Hints & Exam Tricks
    @staticmethod
    def get_hints_for_theorem(theorem_name: str, step_idx: int) -> str:
        hints_map = {
            "Thevenin": [
                "Hint 1: Open-circuit the load terminals A-B to measure Vth.",
                "Hint 2: Deactivate independent sources (short Vs, open Is).",
                "Hint 3: Rth is equivalent resistance looking into open terminals A-B."
            ],
            "Norton": [
                "Hint 1: Short-circuit terminals A-B to calculate Norton current In.",
                "Hint 2: Rn is equal to Rth (equivalent resistance with sources deactivated).",
                "Hint 3: Load current IL = In * (Rn / (Rn + RL))."
            ],
            "Superposition": [
                "Hint 1: Activate ONE independent source at a time.",
                "Hint 2: Short voltage sources (0V) and open current sources (0A).",
                "Hint 3: Sum the individual sub-circuit current/voltage contributions algebraically."
            ]
        }
        for k, v in hints_map.items():
            if k in theorem_name:
                return v[min(step_idx, len(v) - 1)]
        return "Hint 1: Verify circuit equations using KCL or KVL."
