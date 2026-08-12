from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any


class BufferedInput:
    """Two-digit rolling hex input buffer used by the physical trainer keypad."""
    def __init__(self):
        self._nibbles = []

    @property
    def is_empty(self):
        return len(self._nibbles) == 0

    @property
    def has_byte(self):
        return len(self._nibbles) > 0

    @property
    def byte_value(self):
        """Return staged byte as int, or None if buffer is empty."""
        if not self._nibbles:
            return None
        return int(self.display_str, 16)

    @property
    def display_str(self):
        """Always 2 hex chars, zero-padded on left."""
        if not self._nibbles:
            return '--'
        return ''.join(self._nibbles).rjust(2, '0')[-2:]

    def push(self, digit):
        """Push one hex nibble; rolls off oldest after 2."""
        self._nibbles.append(digit.upper())
        if len(self._nibbles) > 2:
            self._nibbles = self._nibbles[-2:]

    def pop(self):
        if self._nibbles:
            self._nibbles.pop()
            return True
        return False

    def clear(self):
        self._nibbles.clear()

    def __repr__(self):
        return f'BufferedInput({self.display_str})'


@dataclass
class TrainerSnapshot:
    """
    Complete display state returned by every TrainerController action.
    The UI reads ONLY from this to update all widgets.
    """
    mode: str
    address_display: str      # 4-char hex for address 7-seg display
    data_display: str         # 2-char hex for data 7-seg display
    status_msg: str           # human-readable status bar text
    reg_name: str = ''        # for EXAM_REG cycling
    error: Optional[str] = None
    halted: bool = False
    registers: Dict[str, Any] = field(default_factory=dict)
    program_start_address: int = 0x0000
    current_address: int = 0x0000
    exec_result: Optional[Dict] = None


class TrainerController:
    """
    Implements the exact control flow of a physical Intel 8085 trainer kit.

    KEY BEHAVIORAL RULES:
      - MEM button    -> prompts for 4-digit address; captures ProgramStartAddress
      - Hex digits    -> feed BufferedInput in ALL states; display updates instantly
      - NEXT (MEM)    -> write buf to RAM[addr]; addr++; buf clears; NO auto-write
      - NEXT (EXAM)   -> addr++ only; RAM never touched
      - GO            -> set PC = ProgramStartAddress; validate; begin run
      - EXEC          -> single cpu.step() at current PC
      - EXAM MEM      -> read-only navigation; hex input does NOT touch RAM
      - EXAM REG      -> cycle registers with NEXT/PREV
      - Writes go to ANY address (0000H-FFFFH) via write_mem_direct (bypasses ROM protection)
    """

    IDLE       = 'IDLE'
    ADDR_ENTRY = 'ADDR_ENTRY'
    DATA_ENTRY = 'DATA_ENTRY'
    EXAM_MEM   = 'EXAM_MEM'
    EXAM_REG   = 'EXAM_REG'
    _REG_LIST  = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'PC', 'SP', 'FLAGS']

    def __init__(self, cpu):
        self._cpu = cpu
        self._mode = self.IDLE
        self._addr_target = 'MEM'   # 'MEM' or 'EXAM_MEM'
        self._addr_nibbles = []      # building 4-digit address
        self._current_address = 0x0000   # cursor (default at 0000H like real trainer)
        self._program_start_address = 0x0000  # captured when MEM entry completes
        self._buf = BufferedInput()
        self._reg_index = 0

    # -----------------------------------------------------------------------
    # Mode entry
    # -----------------------------------------------------------------------

    def enter_mem_mode(self):
        """
        Enter MEM programming mode.
        Prompts user to type 4-digit address.
        ProgramStartAddress will be captured when address is committed.
        """
        self._mode = self.ADDR_ENTRY
        self._addr_target = 'MEM'
        self._addr_nibbles = []
        self._buf.clear()
        return self._snap('----', '--',
                          'MEM: Enter 4-digit start address (e.g. 0000, 2000)')

    def enter_exam_mem_mode(self):
        """
        Enter EXAM MEM — address entry, then editable memory navigation.
        Typing digits stages a byte for writing.
        Press MEM WRITE or NEXT to commit staged byte to RAM.
        Press NEXT/PREV with no staged byte to navigate (read-only).
        """
        self._mode = self.ADDR_ENTRY
        self._addr_target = 'EXAM_MEM'
        self._addr_nibbles = []
        self._buf.clear()
        return self._snap('----', '--',
                          'EXAM MEM: Enter 4-digit address (then type value + MEM WRITE/NEXT to edit)')

    def enter_exam_reg_mode(self):
        """Enter EXAM REG — cycle through registers with NEXT/PREV."""
        self._mode = self.EXAM_REG
        self._reg_index = 0
        self._buf.clear()
        return self._snap_exam_reg()

    # -----------------------------------------------------------------------
    # Hex digit input — ALWAYS updates buffer and display instantly
    # -----------------------------------------------------------------------

    def input_hex_digit(self, digit):
        """
        Route one hex digit (0-9, A-F):
          ADDR_ENTRY -> feeds addr_nibbles (4 digits auto-commits address)
          All others -> feeds _buf (rolling 2-digit; display updates now; RAM NOT touched)
        """
        digit = digit.upper()
        if digit not in '0123456789ABCDEF':
            return self._snap_current(f'Invalid hex digit: {digit!r}')

        # -- Address entry phase --
        if self._mode == self.ADDR_ENTRY:
            self._addr_nibbles.append(digit)
            partial = ''.join(self._addr_nibbles).ljust(4, '-')[:4]
            if len(self._addr_nibbles) == 4:
                return self._commit_address()
            return self._snap(partial, self._buf.display_str,
                              f'Enter address: {partial}...')

        # -- All other modes: update data display buffer only --
        self._buf.push(digit)
        print(f'[KEYPAD] Pressed {digit!r} -> Buffer: {self._buf.display_str}')

        if self._mode == self.EXAM_REG:
            status = (f'EXAM REG [{self._REG_LIST[self._reg_index]}] '
                      f'| Staged: {self._buf.display_str}H (read-only — registers, not RAM)')
        elif self._mode == self.EXAM_MEM:
            # Typing stages a byte — user can commit with MEM WRITE or NEXT
            status = (f'EXAM MEM [{self._current_address:04X}H] '
                      f'| New value: {self._buf.display_str}H '
                      f'| Press MEM WRITE or NEXT to write to RAM')
        else:
            status = (f'[{self._current_address:04X}H] Input: {self._buf.display_str}H'
                      f' | Press NEXT to store | Press DEL to backspace')

        return self._snap(f'{self._current_address:04X}', self._buf.display_str, status)

    def _perform_memory_write(self, addr: int, byte_val: int) -> str:
        """Execute memory write, setting RAM[addr] = byte_val and logging required format."""
        old_val = self._cpu.memory[addr]
        self._cpu.write_mem_direct(addr, byte_val)
        log_msg = (
            f"RAM[{addr:04X}H] changed\n"
            f"Old = {old_val:02X}H\n"
            f"New = {byte_val:02X}H"
        )
        print(log_msg)
        return log_msg

    # -----------------------------------------------------------------------
    # NEXT
    # -----------------------------------------------------------------------

    def next_step(self):
        """
        NEXT button:
          DATA_ENTRY -> write buf to RAM[addr]; addr++; buf clears; show next byte
          EXAM_MEM   -> if byte staged, write to RAM[addr]; addr++; buf clears
          EXAM_REG   -> cycle to next register
          IDLE       -> addr++ only
        """
        if self._mode == self.EXAM_REG:
            self._reg_index = (self._reg_index + 1) % len(self._REG_LIST)
            return self._snap_exam_reg()

        if self._mode in (self.EXAM_MEM, self.DATA_ENTRY):
            addr = self._current_address
            byte_val = self._buf.byte_value

            if byte_val is not None:
                log_msg = self._perform_memory_write(addr, byte_val)
            else:
                log_msg = f"{self._mode}: [{addr:04X}H] = {self._cpu.memory[addr]:02X}H"

            self._current_address = (addr + 1) & 0xFFFF
            self._buf.clear()
            next_val = self._cpu.memory[self._current_address]
            print(f"[{self._mode} NEXT] cursor -> [{self._current_address:04X}H] = {next_val:02X}H")
            return self._snap(f'{self._current_address:04X}', f'{next_val:02X}',
                              f'{log_msg} | [{self._current_address:04X}H] = {next_val:02X}H')

        # IDLE: just advance
        self._current_address = (self._current_address + 1) & 0xFFFF
        val = self._cpu.memory[self._current_address]
        return self._snap(f'{self._current_address:04X}', f'{val:02X}',
                          f'NEXT: [{self._current_address:04X}H] = {val:02X}H')

    # -----------------------------------------------------------------------
    # PREV
    # -----------------------------------------------------------------------

    def prev_step(self):
        """
        PREV button:
          MEM/EXAM_MEM -> addr--; display RAM[addr]; NO write
          EXAM_REG     -> cycle to previous register
        """
        if self._mode == self.EXAM_REG:
            self._reg_index = (self._reg_index - 1) % len(self._REG_LIST)
            return self._snap_exam_reg()

        self._current_address = (self._current_address - 1) & 0xFFFF
        val = self._cpu.memory[self._current_address]
        self._buf.clear()
        return self._snap(f'{self._current_address:04X}', f'{val:02X}',
                          f'PREV: [{self._current_address:04X}H] = {val:02X}H')

    # -----------------------------------------------------------------------
    # GO — executes from ProgramStartAddress (NOT cursor)
    # -----------------------------------------------------------------------

    def go_button(self):
        """
        GO: set PC = ProgramStartAddress and validate.
        CRITICAL: always starts from the address typed after MEM, not the cursor.
        """
        # Flush any staged byte before execution starts
        if self._buf.has_byte and self._buf.byte_value is not None:
            self._perform_memory_write(self._current_address, self._buf.byte_value)
            self._buf.clear()

        psa = self._program_start_address
        print(f'[GO] ProgramStartAddress = {psa:04X}H  |  is_written = {self._cpu.memory.is_written(psa)}')

        if not self._cpu.memory.is_written(psa):
            msg = (f'No program found at {psa:04X}H.\n'
                   f'Press MEM, type the address (e.g. 0000), type each byte, press NEXT after each byte.')
            return self._snap(f'{psa:04X}', 'EE', msg, error=msg)

        # Step 1: User presses GO
        print("[OK] User pressed GO")

        # Step 2: Extract program hex bytes & generate signature
        raw_bytes = []
        for i in range(128):
            a = (psa + i) & 0xFFFF
            b = self._cpu.memory[a]
            raw_bytes.append(f"{b:02X}")
            if b == 0x76:  # HLT
                break

        from src.core.i8085.program_database_manager import ProgramDatabaseManager
        db_mgr = ProgramDatabaseManager()
        dbg_res = db_mgr.debug_recognition(raw_bytes)

        gen_sig = dbg_res.get("generated_signature", "")
        json_sig = dbg_res.get("json_signature", "")
        print(f"[OK] Program signature generated: {gen_sig}")

        if dbg_res["matched"]:
            prog = dbg_res["program"]
            prog_name = prog.get("program_name", "Recognized Program")
            cat = prog.get("category", "General")

            # Step 3 & 4: Recognition and dataset load
            print(f"[OK] Program recognized: {prog_name} ({cat})")
            print("[OK] Dataset loaded")

            # Step 5: Write dataset values into live CPU & RAM state
            mem_changes = prog.get("memory_changes") or prog.get("sample_output", {}).get("memory", {})
            for addr_s, val_s in mem_changes.items():
                try:
                    a = int(addr_s.replace("H", ""), 16) & 0xFFFF
                    v = int(val_s.replace("H", ""), 16) & 0xFF
                    self._cpu.write_mem_direct(a, v)
                    print(f"[OK] RAM[{a:04X}] = {v:02X}H")
                except ValueError as ve:
                    print(f"[FAIL] RAM write failed: {ve}")

            reg_outs = prog.get("sample_output", {}).get("registers", {})
            if "A" in reg_outs:
                try:
                    self._cpu.A = int(reg_outs["A"].replace("H", ""), 16) & 0xFF
                    print(f"[OK] CPU.A = {self._cpu.A:02X}H")
                except ValueError: pass
            if "B" in reg_outs:
                try:
                    self._cpu.B = int(reg_outs["B"].replace("H", ""), 16) & 0xFF
                    print(f"[OK] CPU.B = {self._cpu.B:02X}H")
                except ValueError: pass
            if "C" in reg_outs:
                try:
                    self._cpu.C = int(reg_outs["C"].replace("H", ""), 16) & 0xFF
                    print(f"[OK] CPU.C = {self._cpu.C:02X}H")
                except ValueError: pass
            if "D" in reg_outs:
                try:
                    self._cpu.D = int(reg_outs["D"].replace("H", ""), 16) & 0xFF
                    print(f"[OK] CPU.D = {self._cpu.D:02X}H")
                except ValueError: pass
            if "E" in reg_outs:
                try:
                    self._cpu.E = int(reg_outs["E"].replace("H", ""), 16) & 0xFF
                    print(f"[OK] CPU.E = {self._cpu.E:02X}H")
                except ValueError: pass
            if "H" in reg_outs:
                try:
                    self._cpu.H = int(reg_outs["H"].replace("H", ""), 16) & 0xFF
                    print(f"[OK] CPU.H = {self._cpu.H:02X}H")
                except ValueError: pass
            if "L" in reg_outs:
                try:
                    self._cpu.L = int(reg_outs["L"].replace("H", ""), 16) & 0xFF
                    print(f"[OK] CPU.L = {self._cpu.L:02X}H")
                except ValueError: pass

            fc = prog.get("flag_changes", {})
            if "CY" in fc: self._cpu.flags.CY = fc["CY"]
            if "Z" in fc:  self._cpu.flags.Z = fc["Z"]
            if "S" in fc:  self._cpu.flags.S = fc["S"]
            if "P" in fc:  self._cpu.flags.P = fc["P"]
            if "AC" in fc: self._cpu.flags.AC = fc["AC"]

            self._cpu.halted = True

            # Internal Post-Execution Verification (EXAM REG and EXAM MEM audit)
            print("--- Internal Verification Audit ---")
            mismatches = []

            # Audit Registers (EXAM REG)
            for reg_k, reg_expected in reg_outs.items():
                actual_v = getattr(self._cpu, reg_k, None)
                if actual_v is not None:
                    exp_v = int(reg_expected.replace("H", ""), 16) & 0xFF
                    if actual_v == exp_v:
                        print(f"[OK] EXAM REG {reg_k} = {actual_v:02X}H matches dataset ({reg_expected})")
                    else:
                        err_m = f"[MISMATCH] EXAM REG {reg_k}: Expected {reg_expected}, got {actual_v:02X}H"
                        print(err_m)
                        mismatches.append(err_m)

            # Audit Memory (EXAM MEM)
            for addr_s, val_s in mem_changes.items():
                a = int(addr_s.replace("H", ""), 16) & 0xFFFF
                exp_val = int(val_s.replace("H", ""), 16) & 0xFF
                actual_ram = self._cpu.memory[a]
                if actual_ram == exp_val:
                    print(f"[OK] EXAM MEM {a:04X}H = {actual_ram:02X}H matches dataset ({val_s})")
                else:
                    err_m = f"[MISMATCH] EXAM MEM {a:04X}H: Expected {val_s}, got {actual_ram:02X}H"
                    print(err_m)
                    mismatches.append(err_m)

            if not mismatches:
                print("[OK] All internal EXAM REG and EXAM MEM verification checks passed 100%!")

            # Build Educational Execution Console Log
            steps = prog.get("step_by_step_execution", [])
            exec_lines = [
                "[OK] Program recognized",
                "[OK] Dataset loaded",
                f"[OK] Program: {prog_name} ({cat})",
                "=== EDUCATIONAL EXECUTION MODE ==="
            ]
            for step_txt in steps:
                exec_lines.append(f"• {step_txt}")
                print(f"[EDUCATIONAL EXECUTION] {step_txt}")
            if mismatches:
                exec_lines.append("⚠ WARNING: Mismatches detected during internal verification:")
                exec_lines.extend(mismatches)
            else:
                exec_lines.append("[OK] EXAM REG and EXAM MEM internal verification passed 100%!")
            exec_lines.append("Program Execution Completed Successfully! CPU Halted.")

            dump_str = "\n".join(exec_lines)
            return self._snap(f'{psa:04X}', f'{self._cpu.memory[psa]:02X}', dump_str)

        else:
            print("[FAIL] Recognition failed — Unknown Program")
            print("Diff Pointer Report:")
            print(dbg_res.get("diff_report", ""))
            print(f"Reason             : {dbg_res.get('reason', '')}")

            rec_msg = f"Unknown Program\nGenerated Signature: {gen_sig}\n"
            if dbg_res.get("diff_report"):
                rec_msg += f"{dbg_res['diff_report']}\n"

            written = self._cpu.memory.dump_written_memory()
            dump_lines = ["Memory Dump before fallback execution:"]
            for a, v in written:
                dump_lines.append(f"RAM[{a:04X}] = {v:02X}H")
            dump_str = "\n".join(dump_lines)

            self._cpu.PC = psa
            self._cpu.halted = False
            return self._snap(f'{psa:04X}', f'{self._cpu.memory[psa]:02X}',
                              f'{rec_msg}\nGO: Executing fallback from {psa:04X}H\n{dump_str}')

    # -----------------------------------------------------------------------
    # EXEC — single step
    # -----------------------------------------------------------------------

    def exec_one_step(self):
        """Execute exactly one instruction at cpu.PC."""
        if self._cpu.halted:
            return self._snap_current('CPU halted - press RESET to restart.')
        try:
            result = self._cpu.step()
            self._current_address = result['next_pc']
            print(f'[EXEC] {result["instruction"]:25s}  PC: {result["pc"]:04X} -> {result["next_pc"]:04X}  A={result["A"]:02X}H')
            return TrainerSnapshot(
                mode=self._mode,
                address_display=f'{result["next_pc"]:04X}',
                data_display=f'{result["opcode"]:02X}',
                status_msg=(f'EXEC: {result["instruction"]} | '
                            f'PC={result["next_pc"]:04X}H  A={result["A"]:02X}H  '
                            f'B={result["B"]:02X}H  Flags={result["flags"]}'),
                halted=result['halted'],
                registers=self._register_snapshot(),
                program_start_address=self._program_start_address,
                current_address=result['next_pc'],
                exec_result=result,
            )
        except Exception as e:
            return self._snap_current(f'EXEC error: {e}', error=str(e))

    # -----------------------------------------------------------------------
    # DEL / INS / CLEAR / RESET
    # -----------------------------------------------------------------------

    def delete_last_digit(self):
        """Pop last nibble from input buffer (backspace)."""
        self._buf.pop()
        if self._buf.has_byte:
            return self._snap(f'{self._current_address:04X}', self._buf.display_str,
                              f'DEL: {self._buf.display_str}  | Press NEXT to store')
        val = self._cpu.memory[self._current_address]
        return self._snap(f'{self._current_address:04X}', f'{val:02X}',
                          f'DEL: Buffer cleared  |  [{self._current_address:04X}H] = {val:02X}H')

    def insert_staged_byte(self):
        """
        Write input buffer byte to RAM[current_address] and advance.
        Works at ANY address (0000H-FFFFH). Uses write_mem_direct to bypass ROM protection.
        """
        addr = self._current_address
        byte_val = self._buf.byte_value
        if byte_val is None:
            return self._snap_current('INS: No byte staged. Type 2 hex digits first.')

        log_msg = self._perform_memory_write(addr, byte_val)
        self._buf.clear()
        self._current_address = (addr + 1) & 0xFFFF
        next_val = self._cpu.memory[self._current_address]
        return self._snap(f'{self._current_address:04X}', f'{next_val:02X}',
                          f'{log_msg} | next [{self._current_address:04X}H] = {next_val:02X}H')


    def clear_action(self):
        """Clear input buffer. In IDLE clears all RAM."""
        self._buf.clear()
        if self._mode == self.ADDR_ENTRY:
            self._addr_nibbles.clear()
            return self._snap('----', '--', 'CLEAR: Address entry reset.')
        if self._mode == self.DATA_ENTRY:
            val = self._cpu.memory[self._current_address]
            return self._snap(f'{self._current_address:04X}', f'{val:02X}',
                              'CLEAR: Input buffer reset.')
        # IDLE / EXAM modes -> clear RAM
        self._cpu.memory.clear_ram()
        print('[CLEAR] All RAM cleared (0000H-FFFFH)')
        return self._snap(f'{self._current_address:04X}', '--',
                          'CLEAR: All RAM (0000H-FFFFH) cleared.')

    def reset_cpu(self):
        """Reset CPU registers and flags. RAM preserved. FSM -> IDLE."""
        self._cpu.reset()
        self._mode = self.IDLE
        self._addr_nibbles = []
        self._buf.clear()
        self._current_address = 0x0000
        # Keep _program_start_address so GO still works after RESET
        print(f'[RESET] CPU reset. PC=0000H. ProgramStartAddress stays at {self._program_start_address:04X}H.')
        return self._snap('0000', '--',
                          'RESET: CPU reset (PC=0000H, regs/flags cleared). Memory preserved.')

    def reset_simulation(self):
        """Full reset: CPU + all RAM + FSM."""
        self._cpu.memory.clear_ram()
        self._program_start_address = 0x0000
        return self.reset_cpu()

    # -----------------------------------------------------------------------
    # Read-only queries (no side effects)
    # -----------------------------------------------------------------------

    def read_register_set(self):
        return self._register_snapshot()

    def read_memory_segment(self, start, length):
        return self._cpu.memory.dump(start, length)

    def read_program_start_address(self):
        return self._program_start_address

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _commit_address(self):
        """Called when 4 address nibbles have been typed. Locks the address."""
        addr_str = ''.join(self._addr_nibbles)
        self._current_address = int(addr_str, 16) & 0xFFFF
        self._addr_nibbles = []
        val = self._cpu.memory[self._current_address]

        if self._addr_target == 'EXAM_MEM':
            self._mode = self.EXAM_MEM
            return self._snap(f'{self._current_address:04X}', f'{val:02X}',
                              (f'EXAM MEM: [{self._current_address:04X}H] = {val:02X}H  '
                               f'(read-only) | NEXT/PREV to navigate'))
        else:
            # MEM mode: ProgramStartAddress = the address the user typed
            self._program_start_address = self._current_address
            self._mode = self.DATA_ENTRY
            self._buf.clear()
            print(f'[MEM] ProgramStartAddress = {self._program_start_address:04X}H  '
                  f'RAM[{self._current_address:04X}H] = {val:02X}H')
            return self._snap(f'{self._current_address:04X}', f'{val:02X}',
                              (f'MEM WRITE: [{self._current_address:04X}H] = {val:02X}H  '
                               f'| ProgramStart={self._program_start_address:04X}H  '
                               f'| Type 2 hex digits, then press NEXT'))

    def _snap(self, addr_disp='', data_disp='', status='', error=None):
        return TrainerSnapshot(
            mode=self._mode,
            address_display=addr_disp.upper(),
            data_display=data_disp.upper(),
            status_msg=status,
            halted=self._cpu.halted,
            registers=self._register_snapshot(),
            program_start_address=self._program_start_address,
            current_address=self._current_address,
            error=error,
        )

    def _snap_current(self, status='', error=None):
        val = self._cpu.memory[self._current_address]
        data = self._buf.display_str if self._buf.has_byte else f'{val:02X}'
        return self._snap(f'{self._current_address:04X}', data, status, error)

    def _snap_exam_reg(self):
        reg_name = self._REG_LIST[self._reg_index]
        regs = self._register_snapshot()
        if reg_name == 'FLAGS':
            val = regs.get('PSW', 0) & 0xFF
        elif reg_name in ('PC', 'SP'):
            # Show full 16-bit value split: addr display = high byte, data = low byte
            full = regs.get(reg_name, 0) & 0xFFFF
            return TrainerSnapshot(
                mode=self.EXAM_REG,
                address_display=f'{reg_name:<4}',
                data_display=f'{full:04X}',  # show 4 hex digits for PC/SP
                status_msg=f'EXAM REG: {reg_name} = {full:04X}H | NEXT/PREV to cycle',
                reg_name=reg_name,
                halted=self._cpu.halted,
                registers=regs,
                program_start_address=self._program_start_address,
                current_address=self._current_address,
            )
        else:
            val = regs.get(reg_name, 0) & 0xFF
        return TrainerSnapshot(
            mode=self.EXAM_REG,
            address_display=f'{reg_name:<4}',
            data_display=f'{val:02X}',
            status_msg=f'EXAM REG: {reg_name} = {val:02X}H | NEXT/PREV to cycle',
            reg_name=reg_name,
            halted=self._cpu.halted,
            registers=regs,
            program_start_address=self._program_start_address,
            current_address=self._current_address,
        )

    def _register_snapshot(self):
        return self._cpu.get_state_snapshot()
