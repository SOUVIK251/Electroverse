"""
ElectroVerse Microprocessor & Microcontroller Engine
Comprehensive Mathematical & System Computation Backend for 8085, 8086, 8051, ARM,
Address Decoding, Memory Mapping, Interrupt Vectors, Timers, and UART Baud Rates.
"""

import math
from typing import Dict, Any, List, Tuple


class MPMCEngine:
    """Core Microprocessor & Microcontroller Engineering Calculation Backend."""

    # 1. Address Decoder Calculator
    @staticmethod
    def solve_address_decoder(total_address_lines: int = 16, chip_size_kb: float = 8.0, base_address_hex: str = "2000") -> Dict[str, Any]:
        try:
            base_addr = int(base_address_hex.replace("H", "").replace("h", "").strip(), 16)
        except ValueError:
            base_addr = 0x2000

        bytes_per_chip = int(chip_size_kb * 1024)
        if bytes_per_chip <= 0:
            bytes_per_chip = 8192

        chip_address_lines = int(math.ceil(math.log2(bytes_per_chip)))
        decoder_address_lines = total_address_lines - chip_address_lines

        end_addr = base_addr + bytes_per_chip - 1
        max_addressable = (1 << total_address_lines) - 1

        total_address_lines_str = f"A0 - A{total_address_lines - 1}"
        chip_lines_str = f"A0 - A{chip_address_lines - 1}"
        decoder_lines_str = f"A{chip_address_lines} - A{total_address_lines - 1}" if decoder_address_lines > 0 else "None"

        return {
            "base_address_hex": f"{base_addr:04X}H",
            "end_address_hex": f"{end_addr:04X}H",
            "chip_size_kb": chip_size_kb,
            "bytes_per_chip": bytes_per_chip,
            "chip_address_lines": chip_address_lines,
            "decoder_address_lines": decoder_address_lines,
            "total_address_lines_str": total_address_lines_str,
            "chip_lines_str": chip_lines_str,
            "decoder_lines_str": decoder_lines_str,
            "max_addressable_kb": round((1 << total_address_lines) / 1024.0, 2),
            "decoder_logic": f"Select chip when {decoder_lines_str} = 0x{base_addr >> chip_address_lines:X}"
        }

    # 2. Memory Mapping Calculator
    @staticmethod
    def solve_memory_mapping(rom_kb: float = 16.0, ram_kb: float = 16.0, start_hex: str = "0000") -> Dict[str, Any]:
        try:
            start_addr = int(start_hex.replace("H", "").strip(), 16)
        except ValueError:
            start_addr = 0x0000

        rom_bytes = int(rom_kb * 1024)
        ram_bytes = int(ram_kb * 1024)

        rom_start = start_addr
        rom_end = rom_start + rom_bytes - 1

        ram_start = rom_end + 1
        ram_end = ram_start + ram_bytes - 1

        total_mapped_kb = rom_kb + ram_kb

        return {
            "rom_range": f"{rom_start:04X}H - {rom_end:04X}H",
            "ram_range": f"{ram_start:04X}H - {ram_end:04X}H",
            "rom_kb": rom_kb,
            "ram_kb": ram_kb,
            "total_mapped_kb": total_mapped_kb,
            "rom_chip_enable": f"CE_ROM = active LOW when A15-A14 logic = {rom_start >> 14:02b}",
            "ram_chip_enable": f"CE_RAM = active LOW when A15-A14 logic = {ram_start >> 14:02b}"
        }

    # 3. Hex / Dec / Bin Converter
    @staticmethod
    def solve_hex_dec(input_val: str) -> Dict[str, Any]:
        val_str = str(input_val).strip().upper().replace("H", "").replace("0X", "")
        dec_val = 0
        try:
            if val_str.isdigit():
                dec_val = int(val_str)
            else:
                dec_val = int(val_str, 16)
        except ValueError:
            dec_val = 0

        hex_8bit = f"{dec_val & 0xFF:02X}H"
        hex_16bit = f"{dec_val & 0xFFFF:04X}H"
        bin_8bit = f"{dec_val & 0xFF:08b}"
        bin_16bit = f"{dec_val & 0xFFFF:016b}"
        oct_val = f"{dec_val:o}"

        # 8085 Flags breakdown (S, Z, Aux, P, CY)
        val8 = dec_val & 0xFF
        flag_s = 1 if (val8 & 0x80) else 0
        flag_z = 1 if (val8 == 0) else 0
        flag_p = 1 if (bin(val8).count('1') % 2 == 0) else 0

        return {
            "dec": dec_val,
            "hex_8bit": hex_8bit,
            "hex_16bit": hex_16bit,
            "bin_8bit": bin_8bit,
            "bin_16bit": bin_16bit,
            "octal": oct_val,
            "flags_8085": f"S={flag_s}, Z={flag_z}, P={flag_p}"
        }

    # 4. Instruction Timing Calculator
    @staticmethod
    def solve_instruction_timing(t_states: int = 7, clock_freq_mhz: float = 3.0) -> Dict[str, Any]:
        freq_hz = clock_freq_mhz * 1e6
        t_state_us = (1.0 / freq_hz) * 1e6 if freq_hz > 0 else 0.333
        total_time_us = t_states * t_state_us

        return {
            "t_states": t_states,
            "clock_freq_mhz": clock_freq_mhz,
            "t_state_duration_us": round(t_state_us, 4),
            "total_execution_time_us": round(total_time_us, 4),
            "total_execution_time_ns": round(total_time_us * 1000, 2),
            "mips_rating": round((clock_freq_mhz * 1e6) / (t_states * 1e6), 3) if t_states > 0 else 0
        }

    # 5. 8085 Opcode Finder
    @staticmethod
    def find_8085_opcode(query: str = "MOV A, B") -> Dict[str, Any]:
        opcodes_db = {
            "MOV A, B": {"hex": "78H", "bytes": 1, "t_states": 4, "cycles": "Fetch (4T)", "flags": "None"},
            "MOV A, M": {"hex": "7EH", "bytes": 1, "t_states": 7, "cycles": "Fetch (4T), Mem Read (3T)", "flags": "None"},
            "MVI A, DATA": {"hex": "3E [DATA]", "bytes": 2, "t_states": 7, "cycles": "Fetch (4T), Mem Read (3T)", "flags": "None"},
            "LXI H, ADDR": {"hex": "21 [LOW] [HIGH]", "bytes": 3, "t_states": 10, "cycles": "Fetch (4T), Mem Read (3T), Mem Read (3T)", "flags": "None"},
            "ADD B": {"hex": "80H", "bytes": 1, "t_states": 4, "cycles": "Fetch (4T)", "flags": "All Flags (S, Z, AC, P, CY)"},
            "SUB C": {"hex": "91H", "bytes": 1, "t_states": 4, "cycles": "Fetch (4T)", "flags": "All Flags (S, Z, AC, P, CY)"},
            "INR A": {"hex": "3CH", "bytes": 1, "t_states": 4, "cycles": "Fetch (4T)", "flags": "S, Z, AC, P (CY unaffected)"},
            "DCR B": {"hex": "05H", "bytes": 1, "t_states": 4, "cycles": "Fetch (4T)", "flags": "S, Z, AC, P (CY unaffected)"},
            "IN PORT": {"hex": "DB [PORT]", "bytes": 2, "t_states": 10, "cycles": "Fetch (4T), Mem Read (3T), IO Read (3T)", "flags": "None"},
            "OUT PORT": {"hex": "D3 [PORT]", "bytes": 2, "t_states": 10, "cycles": "Fetch (4T), Mem Read (3T), IO Write (3T)", "flags": "None"},
            "JMP ADDR": {"hex": "C3 [LOW] [HIGH]", "bytes": 3, "t_states": 10, "cycles": "Fetch (4T), Mem Read (3T), Mem Read (3T)", "flags": "None"},
            "CALL ADDR": {"hex": "CD [LOW] [HIGH]", "bytes": 3, "t_states": 18, "cycles": "Fetch (4T), Mem Read (3T), Mem Read (3T), Mem Write (3T), Mem Write (3T)", "flags": "None"},
            "RET": {"hex": "C9H", "bytes": 1, "t_states": 10, "cycles": "Fetch (4T), Mem Read (3T), Mem Read (3T)", "flags": "None"},
            "PUSH PSW": {"hex": "F5H", "bytes": 1, "t_states": 12, "cycles": "Fetch (4T), Mem Read (3T), Mem Write (3T), Mem Write (2T)", "flags": "None"},
            "POP H": {"hex": "E1H", "bytes": 1, "t_states": 10, "cycles": "Fetch (4T), Mem Read (3T), Mem Read (3T)", "flags": "Restores H & L"},
            "NOP": {"hex": "00H", "bytes": 1, "t_states": 4, "cycles": "Fetch (4T)", "flags": "None"},
            "HLT": {"hex": "76H", "bytes": 1, "t_states": 5, "cycles": "Fetch (5T)", "flags": "Halts CPU till Interrupt/Reset"}
        }

        q_clean = query.strip().upper()
        match = opcodes_db.get(q_clean)
        if not match:
            # Fallback partial search
            for k, v in opcodes_db.items():
                if q_clean in k:
                    match = v
                    q_clean = k
                    break

        if not match:
            match = opcodes_db["MOV A, B"]
            q_clean = "MOV A, B"

        return {
            "instruction": q_clean,
            "hex_opcode": match["hex"],
            "bytes": match["bytes"],
            "t_states": match["t_states"],
            "cycles": match["cycles"],
            "flags": match["flags"]
        }

    # 6. Interrupt Priority & Vector Solver
    @staticmethod
    def solve_interrupt_priority(processor: str = "8085", interrupt: str = "RST 7.5") -> Dict[str, Any]:
        db_8085 = {
            "TRAP": {"vector_hex": "0024H", "priority": 1, "type": "Edge & Level", "maskable": "No (NMI)"},
            "RST 7.5": {"vector_hex": "003CH", "priority": 2, "type": "Rising Edge", "maskable": "Yes (SIM)"},
            "RST 6.5": {"vector_hex": "0034H", "priority": 3, "type": "High Level", "maskable": "Yes (SIM)"},
            "RST 5.5": {"vector_hex": "002CH", "priority": 4, "type": "High Level", "maskable": "Yes (SIM)"},
            "INTR": {"vector_hex": "Ext (RST n / CALL)", "priority": 5, "type": "High Level", "maskable": "Yes (EI/DI)"}
        }

        db_8051 = {
            "INT0": {"vector_hex": "0003H", "priority": 1, "type": "Low Level / Falling Edge", "maskable": "EX0 in IE"},
            "TF0": {"vector_hex": "000BH", "priority": 2, "type": "Timer 0 Overflow", "maskable": "ET0 in IE"},
            "INT1": {"vector_hex": "0013H", "priority": 3, "type": "Low Level / Falling Edge", "maskable": "EX1 in IE"},
            "TF1": {"vector_hex": "001BH", "priority": 4, "type": "Timer 1 Overflow", "maskable": "ET1 in IE"},
            "RI/TI": {"vector_hex": "0023H", "priority": 5, "type": "Serial Interrupt", "maskable": "ES in IE"}
        }

        p_clean = processor.strip().upper()
        if "8051" in p_clean:
            db = db_8051
            name = interrupt if interrupt in db else "INT0"
        else:
            db = db_8085
            name = interrupt if interrupt in db else "RST 7.5"

        info = db[name]
        return {
            "processor": p_clean,
            "interrupt_name": name,
            "vector_address": info["vector_hex"],
            "priority_rank": info["priority"],
            "trigger_type": info["type"],
            "maskable": info["maskable"]
        }

    # 7. 8051 Timer Calculator
    @staticmethod
    def solve_8051_timer(crystal_freq_mhz: float = 11.0592, delay_ms: float = 1.0, timer_mode: int = 1) -> Dict[str, Any]:
        machine_clk_hz = (crystal_freq_mhz * 1e6) / 12.0
        timer_period_us = (1.0 / machine_clk_hz) * 1e6

        counts_needed = int(round((delay_ms * 1000.0) / timer_period_us))
        if timer_mode == 1:
            max_counts = 65536
            reload_val = max_counts - counts_needed
            if reload_val < 0:
                reload_val = 0
            th_val = (reload_val >> 8) & 0xFF
            tl_val = reload_val & 0xFF
        else:
            max_counts = 256
            reload_val = max_counts - (counts_needed % 256)
            th_val = reload_val & 0xFF
            tl_val = reload_val & 0xFF

        return {
            "crystal_freq_mhz": crystal_freq_mhz,
            "machine_clock_khz": round(machine_clk_hz / 1000.0, 3),
            "timer_clock_us": round(timer_period_us, 4),
            "requested_delay_ms": delay_ms,
            "counts_needed": counts_needed,
            "reload_hex": f"{reload_val:04X}H" if timer_mode == 1 else f"{reload_val:02X}H",
            "th_hex": f"{th_val:02X}H",
            "tl_hex": f"{tl_val:02X}H",
            "actual_delay_ms": round((counts_needed * timer_period_us) / 1000.0, 4)
        }

    # 8. UART Baud Rate Calculator
    @staticmethod
    def solve_uart_baud(crystal_freq_mhz: float = 11.0592, baud_rate: int = 9600, smod: int = 0) -> Dict[str, Any]:
        machine_clk_hz = (crystal_freq_mhz * 1e6) / 12.0
        timer1_clk_hz = machine_clk_hz / (32.0 if smod == 0 else 16.0)

        required_counts = timer1_clk_hz / baud_rate
        th1_val = int(round(256 - required_counts))
        if th1_val < 0:
            th1_val = 0

        actual_baud = timer1_clk_hz / (256 - th1_val) if (256 - th1_val) > 0 else 0
        error_pct = ((actual_baud - baud_rate) / baud_rate) * 100.0 if baud_rate > 0 else 0.0

        return {
            "crystal_freq_mhz": crystal_freq_mhz,
            "target_baud": baud_rate,
            "smod_bit": smod,
            "th1_hex": f"{th1_val & 0xFF:02X}H",
            "th1_dec": th1_val & 0xFF,
            "actual_baud": round(actual_baud, 1),
            "error_percentage": round(error_pct, 2)
        }

    # 9. ARM Clock & PLL Calculator
    @staticmethod
    def solve_arm_clock(hse_mhz: float = 8.0, pll_m: int = 8, pll_n: int = 336, pll_p: int = 2) -> Dict[str, Any]:
        vco_in = hse_mhz / pll_m if pll_m > 0 else 1.0
        vco_out = vco_in * pll_n
        sysclk = vco_out / pll_p if pll_p > 0 else 168.0

        return {
            "hse_mhz": hse_mhz,
            "pll_m": pll_m,
            "pll_n": pll_n,
            "pll_p": pll_p,
            "vco_input_mhz": round(vco_in, 2),
            "vco_output_mhz": round(vco_out, 2),
            "sysclk_mhz": round(sysclk, 2),
            "ahb_freq_mhz": round(sysclk, 2),
            "apb1_freq_mhz": round(sysclk / 4.0, 2),
            "apb2_freq_mhz": round(sysclk / 2.0, 2)
        }
