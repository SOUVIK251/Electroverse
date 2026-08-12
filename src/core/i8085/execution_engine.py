"""
i8085.execution_engine — Fetch–Decode–Execute Loop
====================================================
Implements the complete Intel 8085A instruction set.

The engine operates on injected dependencies (Memory, Registers, Flags,
Stack, Logger) so every module remains independently testable.

Execution modes
---------------
step()          Execute exactly one instruction.
run(callback)   Execute continuously until HLT, illegal opcode, or caller
                invokes pause() / stop().

Each call to step() returns a result dict:
    pc          Address of the fetched opcode
    next_pc     PC value after execution
    opcode      Raw opcode byte (int)
    instruction Decoded mnemonic string
    A … L       Register values after execution
    SP, PC      Special-purpose register values
    flags       {S, Z, AC, P, CY}
    t_states    T-states consumed
    halted      True if HLT was executed
    log         Human-readable description

Bus signals updated on every memory access:
    address_bus, data_bus, ale_signal, rd_signal, wr_signal, iom_signal
"""

from typing import Dict, Any, Optional, Callable

from .memory             import Memory8085, MemoryError8085
from .registers          import Registers8085
from .flags              import Flags8085
from .stack              import Stack8085
from .execution_logger   import ExecutionLogger


class IllegalOpcodeError(Exception):
    """Raised when the CPU encounters an undefined opcode."""


class ExecutionEngine:
    """
    Intel 8085A Fetch–Decode–Execute engine.

    Parameters
    ----------
    memory    : Memory8085
    regs      : Registers8085
    flags     : Flags8085
    stack     : Stack8085
    logger    : ExecutionLogger
    """

    def __init__(
        self,
        memory  : Memory8085,
        regs    : Registers8085,
        flags   : Flags8085,
        stack   : Stack8085,
        logger  : ExecutionLogger,
    ):
        self._mem    = memory
        self._regs   = regs
        self._flags  = flags
        self._stack  = stack
        self._logger = logger

        # Bus state (updated on every memory transaction)
        self.address_bus : int  = 0x2000
        self.data_bus    : int  = 0x00
        self.ale_signal  : bool = False
        self.rd_signal   : bool = False
        self.wr_signal   : bool = False
        self.iom_signal  : bool = False   # False = Memory, True = I/O

        # Execution state
        self.halted      : bool = False
        self._paused     : bool = False
        self._stopped    : bool = False
        self.t_states_total : int = 0

        # Register index → name mapping (8085 opcode encoding)
        self._REG = {0:'B',1:'C',2:'D',3:'E',4:'H',5:'L',6:'M',7:'A'}

    # ==================================================================
    # Public control
    # ==================================================================

    def pause(self)  -> None: self._paused  = True
    def resume(self) -> None: self._paused  = False
    def stop(self)   -> None: self._stopped = True

    def reset(self) -> None:
        """Reset execution state (does NOT reset memory or registers)."""
        self.halted         = False
        self._paused        = False
        self._stopped       = False
        self.t_states_total = 0
        self.address_bus    = self._regs.PC
        self.data_bus       = 0x00
        self.ale_signal     = False
        self.rd_signal      = False
        self.wr_signal      = False

    # ==================================================================
    # Single step
    # ==================================================================

    def step(self) -> Dict[str, Any]:
        """
        Execute exactly one instruction.

        Returns a result dict; raises IllegalOpcodeError or
        MemoryError8085 on fault.
        """
        if self.halted:
            return self._make_result(
                self._regs.PC, 0x76, "HLT",
                "Program completed successfully.\nHLT encountered.", 0
            )

        fetch_pc = self._regs.PC
        if not self._mem.is_written(fetch_pc):
            raise MemoryError8085(f"No program found at execution address {fetch_pc:04X}H.")

        self.ale_signal = True
        opcode = self._fetch8()
        self.ale_signal = False

        inst, ts, log_msg = self._execute(opcode, fetch_pc)
        self.t_states_total += ts

        result = self._make_result(fetch_pc, opcode, inst, log_msg, ts)

        # Log the step
        self._logger.log_step(
            pc          = fetch_pc,
            opcode      = opcode,
            instruction = inst,
            registers   = self._regs.snapshot(),
            flags       = self._flags.snapshot(),
            t_states    = ts,
            log_msg     = log_msg,
        )

        return result

    # ==================================================================
    # Continuous run
    # ==================================================================

    def run(
        self,
        step_callback: Optional[Callable[[Dict], None]] = None,
        max_steps: int = 1_000_000,
    ) -> Dict[str, Any]:
        """
        Execute instructions continuously until HLT, illegal opcode,
        pause(), stop(), or *max_steps* is exceeded.

        *step_callback* is called after every instruction with the
        result dict.  Use this for UI updates in a worker thread.

        Returns the last result dict.
        """
        self._paused  = False
        self._stopped = False
        last_result: Dict[str, Any] = {}
        steps = 0

        while not self.halted and not self._stopped and steps < max_steps:
            if self._paused:
                break
            last_result = self.step()
            steps      += 1
            if step_callback:
                step_callback(last_result)
            if self.halted:
                break

        return last_result

    # ==================================================================
    # Memory access helpers (update bus state)
    # ==================================================================

    def _fetch8(self) -> int:
        addr = self._regs.PC & 0xFFFF
        self.address_bus = addr
        self.iom_signal  = False
        self.rd_signal   = True
        self.wr_signal   = False
        val = self._mem.read(addr)
        self.data_bus    = val
        self._regs.PC    = (self._regs.PC + 1) & 0xFFFF
        return val

    def _fetch16(self) -> int:
        lo = self._fetch8()
        hi = self._fetch8()
        return (hi << 8) | lo

    def _mem_read(self, addr: int) -> int:
        addr &= 0xFFFF
        self.address_bus = addr
        self.iom_signal  = False
        self.rd_signal   = True
        self.wr_signal   = False
        val = self._mem.read(addr)
        self.data_bus    = val
        return val

    def _mem_write(self, addr: int, val: int) -> None:
        addr &= 0xFFFF
        val  &= 0xFF
        self.address_bus = addr
        self.data_bus    = val
        self.iom_signal  = False
        self.rd_signal   = False
        self.wr_signal   = True
        self._mem.write(addr, val)

    # ==================================================================
    # Register read/write by 3-bit opcode index
    # ==================================================================

    def _get_reg(self, idx: int) -> int:
        name = self._REG[idx & 7]
        if name == 'A': return self._regs.A
        if name == 'M': return self._mem_read(self._regs.HL)
        return getattr(self._regs, name)

    def _set_reg(self, idx: int, val: int) -> None:
        name = self._REG[idx & 7]
        val &= 0xFF
        if name == 'A':
            self._regs.A = val
        elif name == 'M':
            self._mem_write(self._regs.HL, val)
        else:
            setattr(self._regs, name, val)

    # ==================================================================
    # Instruction execution dispatcher
    # ==================================================================

    def _execute(self, opcode: int, fetch_pc: int):
        """
        Decode and execute *opcode*.  Returns (instruction_str, t_states, log_msg).
        Raises IllegalOpcodeError for unknown opcodes.
        """
        R = self._regs
        F = self._flags

        # ── NOP ──────────────────────────────────────────────────────────
        if opcode == 0x00:
            return "NOP", 4, "No operation."

        # ── HLT ──────────────────────────────────────────────────────────
        if opcode == 0x76:
            self.halted = True
            return "HLT", 5, "Program completed successfully.\nHLT encountered."

        # ── MOV Rd, Rs  (0x40–0x7F, skip 0x76) ─────────────────────────
        if 0x40 <= opcode <= 0x7F:
            di, si = (opcode >> 3) & 7, opcode & 7
            dn, sn = self._REG[di], self._REG[si]
            val    = self._get_reg(si)
            self._set_reg(di, val)
            ts     = 7 if (di == 6 or si == 6) else 4
            return f"MOV {dn},{sn}", ts, f"Moved {val:02X}H → {dn}."

        # ── MVI Rd, d8  (06,0E,16,1E,26,2E,36,3E) ──────────────────────
        if opcode in (0x06,0x0E,0x16,0x1E,0x26,0x2E,0x36,0x3E):
            di  = (opcode >> 3) & 7
            dn  = self._REG[di]
            d   = self._fetch8()
            self._set_reg(di, d)
            ts  = 10 if di == 6 else 7
            return f"MVI {dn},{d:02X}H", ts, f"Loaded {d:02X}H → {dn}."

        # ── LXI Rp, d16  (01,11,21,31) ──────────────────────────────────
        if opcode in (0x01,0x11,0x21,0x31):
            d16 = self._fetch16()
            p   = {0x01:'B',0x11:'D',0x21:'H',0x31:'SP'}[opcode]
            if   p=='B':  R.BC = d16
            elif p=='D':  R.DE = d16
            elif p=='H':  R.HL = d16
            else:         R.SP = d16
            return f"LXI {p},{d16:04X}H", 10, f"Loaded {d16:04X}H → {p}."

        # ── INX Rp ──────────────────────────────────────────────────────
        if opcode in (0x03,0x13,0x23,0x33):
            p = {0x03:'B',0x13:'D',0x23:'H',0x33:'SP'}[opcode]
            if   p=='B':  R.BC = (R.BC+1) & 0xFFFF
            elif p=='D':  R.DE = (R.DE+1) & 0xFFFF
            elif p=='H':  R.HL = (R.HL+1) & 0xFFFF
            else:         R.SP = (R.SP+1) & 0xFFFF
            return f"INX {p}", 5, f"Incremented {p}."

        # ── DCX Rp ──────────────────────────────────────────────────────
        if opcode in (0x0B,0x1B,0x2B,0x3B):
            p = {0x0B:'B',0x1B:'D',0x2B:'H',0x3B:'SP'}[opcode]
            if   p=='B':  R.BC = (R.BC-1) & 0xFFFF
            elif p=='D':  R.DE = (R.DE-1) & 0xFFFF
            elif p=='H':  R.HL = (R.HL-1) & 0xFFFF
            else:         R.SP = (R.SP-1) & 0xFFFF
            return f"DCX {p}", 5, f"Decremented {p}."

        # ── DAD Rp ──────────────────────────────────────────────────────
        if opcode in (0x09,0x19,0x29,0x39):
            p = {0x09:'B',0x19:'D',0x29:'H',0x39:'SP'}[opcode]
            rp = {'B':R.BC,'D':R.DE,'H':R.HL,'SP':R.SP}[p]
            res = R.HL + rp
            F.CY = 1 if res > 0xFFFF else 0
            R.HL = res & 0xFFFF
            return f"DAD {p}", 10, f"HL = {R.HL:04X}H. CY={F.CY}."

        # ── INR Rd ──────────────────────────────────────────────────────
        if opcode in (0x04,0x0C,0x14,0x1C,0x24,0x2C,0x34,0x3C):
            di  = (opcode >> 3) & 7
            dn  = self._REG[di]
            val = F.update_after_inr(self._get_reg(di))
            self._set_reg(di, val)
            ts  = 10 if di == 6 else 4
            return f"INR {dn}", ts, f"Incremented {dn} → {val:02X}H."

        # ── DCR Rd ──────────────────────────────────────────────────────
        if opcode in (0x05,0x0D,0x15,0x1D,0x25,0x2D,0x35,0x3D):
            di  = (opcode >> 3) & 7
            dn  = self._REG[di]
            val = F.update_after_dcr(self._get_reg(di))
            self._set_reg(di, val)
            ts  = 10 if di == 6 else 4
            return f"DCR {dn}", ts, f"Decremented {dn} → {val:02X}H."

        # ── ADD Rs  (80–87) ──────────────────────────────────────────────
        if 0x80 <= opcode <= 0x87:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            R.A = F.update_after_add(R.A, val)
            ts  = 7 if si == 6 else 4
            return f"ADD {sn}", ts, f"A + {sn}({val:02X}H) = {R.A:02X}H."

        # ── ADC Rs  (88–8F) ──────────────────────────────────────────────
        if 0x88 <= opcode <= 0x8F:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            cy  = F.CY
            R.A = F.update_after_add(R.A, val, cy)
            ts  = 7 if si == 6 else 4
            return f"ADC {sn}", ts, f"A + {sn} + CY({cy}) = {R.A:02X}H."

        # ── SUB Rs  (90–97) ──────────────────────────────────────────────
        if 0x90 <= opcode <= 0x97:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            R.A = F.update_after_sub(R.A, val)
            ts  = 7 if si == 6 else 4
            return f"SUB {sn}", ts, f"A - {sn}({val:02X}H) = {R.A:02X}H."

        # ── SBB Rs  (98–9F) ──────────────────────────────────────────────
        if 0x98 <= opcode <= 0x9F:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            cy  = F.CY
            R.A = F.update_after_sub(R.A, val, cy)
            ts  = 7 if si == 6 else 4
            return f"SBB {sn}", ts, f"A - {sn} - CY = {R.A:02X}H."

        # ── ANA Rs  (A0–A7) ──────────────────────────────────────────────
        if 0xA0 <= opcode <= 0xA7:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            R.A = F.update_after_logic(R.A & val, ac_val=1)
            ts  = 7 if si == 6 else 4
            return f"ANA {sn}", ts, f"A AND {sn} = {R.A:02X}H."

        # ── XRA Rs  (A8–AF) ──────────────────────────────────────────────
        if 0xA8 <= opcode <= 0xAF:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            R.A = F.update_after_logic(R.A ^ val)
            ts  = 7 if si == 6 else 4
            return f"XRA {sn}", ts, f"A XOR {sn} = {R.A:02X}H."

        # ── ORA Rs  (B0–B7) ──────────────────────────────────────────────
        if 0xB0 <= opcode <= 0xB7:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            R.A = F.update_after_logic(R.A | val)
            ts  = 7 if si == 6 else 4
            return f"ORA {sn}", ts, f"A OR {sn} = {R.A:02X}H."

        # ── CMP Rs  (B8–BF) ──────────────────────────────────────────────
        if 0xB8 <= opcode <= 0xBF:
            si  = opcode & 7
            sn  = self._REG[si]
            val = self._get_reg(si)
            F.update_after_sub(R.A, val)    # result discarded
            ts  = 7 if si == 6 else 4
            return f"CMP {sn}", ts, f"Compare A({R.A:02X}H) vs {sn}({val:02X}H). Z={F.Z} CY={F.CY}."

        # ── Immediate arithmetic ──────────────────────────────────────────
        if opcode == 0xC6:
            d = self._fetch8(); R.A = F.update_after_add(R.A, d)
            return f"ADI {d:02X}H", 7, f"A + {d:02X}H = {R.A:02X}H."
        if opcode == 0xCE:
            d=self._fetch8(); cy=F.CY; R.A=F.update_after_add(R.A,d,cy)
            return f"ACI {d:02X}H", 7, f"A + {d:02X}H + CY = {R.A:02X}H."
        if opcode == 0xD6:
            d=self._fetch8(); R.A=F.update_after_sub(R.A,d)
            return f"SUI {d:02X}H", 7, f"A - {d:02X}H = {R.A:02X}H."
        if opcode == 0xDE:
            d=self._fetch8(); cy=F.CY; R.A=F.update_after_sub(R.A,d,cy)
            return f"SBI {d:02X}H", 7, f"A - {d:02X}H - CY = {R.A:02X}H."
        if opcode == 0xE6:
            d=self._fetch8(); R.A=F.update_after_logic(R.A&d,ac_val=1)
            return f"ANI {d:02X}H", 7, f"A AND {d:02X}H = {R.A:02X}H."
        if opcode == 0xEE:
            d=self._fetch8(); R.A=F.update_after_logic(R.A^d)
            return f"XRI {d:02X}H", 7, f"A XOR {d:02X}H = {R.A:02X}H."
        if opcode == 0xF6:
            d=self._fetch8(); R.A=F.update_after_logic(R.A|d)
            return f"ORI {d:02X}H", 7, f"A OR {d:02X}H = {R.A:02X}H."
        if opcode == 0xFE:
            d=self._fetch8(); F.update_after_sub(R.A,d)
            return f"CPI {d:02X}H", 7, f"Compare A({R.A:02X}H) vs {d:02X}H. Z={F.Z} CY={F.CY}."

        # ── Rotate ───────────────────────────────────────────────────────
        if opcode == 0x07:  # RLC
            cy=( R.A>>7)&1; R.A=((R.A<<1)|cy)&0xFF; F.CY=cy
            return "RLC",4,f"Rotate A left. A={R.A:02X}H CY={cy}."
        if opcode == 0x0F:  # RRC
            cy=R.A&1; R.A=((cy<<7)|(R.A>>1))&0xFF; F.CY=cy
            return "RRC",4,f"Rotate A right. A={R.A:02X}H CY={cy}."
        if opcode == 0x17:  # RAL
            new_cy=(R.A>>7)&1; R.A=((R.A<<1)|F.CY)&0xFF; F.CY=new_cy
            return "RAL",4,f"Rotate A left through CY. A={R.A:02X}H."
        if opcode == 0x1F:  # RAR
            new_cy=R.A&1; R.A=((F.CY<<7)|(R.A>>1))&0xFF; F.CY=new_cy
            return "RAR",4,f"Rotate A right through CY. A={R.A:02X}H."

        # ── CMA / CMC / STC ──────────────────────────────────────────────
        if opcode == 0x2F: R.A=(~R.A)&0xFF; return "CMA",4,f"A = ~A = {R.A:02X}H."
        if opcode == 0x3F: F.CY^=1; return "CMC",4,f"CY = {F.CY}."
        if opcode == 0x37: F.CY=1;  return "STC",4,"CY = 1."

        # ── LDA / STA / LHLD / SHLD / LDAX / STAX ───────────────────────
        if opcode == 0x3A:
            a = self._fetch16()
            print(f"Reading RAM[{a:04X}H]")
            R.A = self._mem_read(a)
            print(f"Value = {R.A:02X}H")
            return f"LDA {a:04X}H", 13, f"Reading RAM[{a:04X}H] -> Value = {R.A:02X}H | A ← [{a:04X}H] = {R.A:02X}H"
        if opcode == 0x32:
            a = self._fetch16()
            old_v = self._mem.read(a)
            self._mem_write(a, R.A)
            print(f"RAM[{a:04X}H] changed\nOld = {old_v:02X}H\nNew = {R.A:02X}H")
            return f"STA {a:04X}H", 13, f"RAM[{a:04X}H] changed: Old = {old_v:02X}H, New = {R.A:02X}H | [{a:04X}H] ← A = {R.A:02X}H"
        if opcode == 0x2A:
            a=self._fetch16(); R.L=self._mem_read(a); R.H=self._mem_read((a+1)&0xFFFF)
            return f"LHLD {a:04X}H",16,f"HL ← {R.HL:04X}H from [{a:04X}H]."
        if opcode == 0x22:
            a=self._fetch16(); self._mem_write(a,R.L); self._mem_write((a+1)&0xFFFF,R.H)
            return f"SHLD {a:04X}H",16,f"[{a:04X}H] ← HL = {R.HL:04X}H."
        if opcode == 0x0A:
            R.A=self._mem_read(R.BC); return "LDAX B",7,f"A ← [BC={R.BC:04X}H] = {R.A:02X}H."
        if opcode == 0x1A:
            R.A=self._mem_read(R.DE); return "LDAX D",7,f"A ← [DE={R.DE:04X}H] = {R.A:02X}H."
        if opcode == 0x02:
            self._mem_write(R.BC,R.A); return "STAX B",7,f"[BC={R.BC:04X}H] ← A = {R.A:02X}H."
        if opcode == 0x12:
            self._mem_write(R.DE,R.A); return "STAX D",7,f"[DE={R.DE:04X}H] ← A = {R.A:02X}H."

        # ── XCHG / XTHL / SPHL / PCHL ────────────────────────────────────
        if opcode == 0xEB:
            R.D,R.H=R.H,R.D; R.E,R.L=R.L,R.E
            return "XCHG",4,f"DE↔HL. DE={R.DE:04X}H HL={R.HL:04X}H."
        if opcode == 0xE3:
            lm=self._mem_read(R.SP); hm=self._mem_read((R.SP+1)&0xFFFF)
            self._mem_write(R.SP,R.L); self._mem_write((R.SP+1)&0xFFFF,R.H)
            R.L=lm; R.H=hm
            return "XTHL",18,f"HL ↔ [SP]. New HL={R.HL:04X}H."
        if opcode == 0xF9: R.SP=R.HL; return "SPHL",5,f"SP = HL = {R.SP:04X}H."
        if opcode == 0xE9: R.PC=R.HL; return "PCHL",5,f"PC = HL = {R.PC:04X}H."

        # ── PUSH / POP ───────────────────────────────────────────────────
        if opcode == 0xC5: self._stack.push_bc();  return "PUSH B",11,f"Pushed BC({R.BC:04X}H). SP={R.SP:04X}H."
        if opcode == 0xD5: self._stack.push_de();  return "PUSH D",11,f"Pushed DE({R.DE:04X}H). SP={R.SP:04X}H."
        if opcode == 0xE5: self._stack.push_hl();  return "PUSH H",11,f"Pushed HL({R.HL:04X}H). SP={R.SP:04X}H."
        if opcode == 0xF5: self._stack.push_psw(); return "PUSH PSW",11,f"Pushed A({R.A:02X}H)+flags. SP={R.SP:04X}H."
        if opcode == 0xC1: self._stack.pop_bc();   return "POP B",10,f"Popped → BC={R.BC:04X}H. SP={R.SP:04X}H."
        if opcode == 0xD1: self._stack.pop_de();   return "POP D",10,f"Popped → DE={R.DE:04X}H. SP={R.SP:04X}H."
        if opcode == 0xE1: self._stack.pop_hl();   return "POP H",10,f"Popped → HL={R.HL:04X}H. SP={R.SP:04X}H."
        if opcode == 0xF1: self._stack.pop_psw();  return "POP PSW",10,f"Popped → A={R.A:02X}H flags restored. SP={R.SP:04X}H."

        # ── Jump family ───────────────────────────────────────────────────
        def _jump(cond, mnem, ts_true=10, ts_false=10):
            a = self._fetch16()
            if cond: R.PC = a; taken = "taken"
            else:            taken = "not taken"
            ts = ts_true if cond else ts_false
            return f"{mnem} {a:04X}H", ts, f"Branch {taken} → {a:04X}H."

        if opcode == 0xC3: a=self._fetch16(); R.PC=a; return f"JMP {a:04X}H",10,f"Jump → {a:04X}H."
        if opcode == 0xC2: return _jump(not F.Z,  "JNZ")
        if opcode == 0xCA: return _jump(    F.Z,  "JZ")
        if opcode == 0xD2: return _jump(not F.CY, "JNC")
        if opcode == 0xDA: return _jump(    F.CY, "JC")
        if opcode == 0xE2: return _jump(not F.P,  "JPO")
        if opcode == 0xEA: return _jump(    F.P,  "JPE")
        if opcode == 0xF2: return _jump(not F.S,  "JP")
        if opcode == 0xFA: return _jump(    F.S,  "JM")

        # ── Call / Return ─────────────────────────────────────────────────
        def _call(cond, mnem):
            a = self._fetch16()
            if cond:
                self._stack.push_pc(); R.PC=a
                return f"{mnem} {a:04X}H", 17, f"Call → {a:04X}H. SP={R.SP:04X}H."
            return f"{mnem} {a:04X}H", 11, "Condition false; no call."

        def _ret(cond, mnem):
            if cond:
                self._stack.pop_pc()
                return mnem, 11, f"Return → {R.PC:04X}H."
            return mnem, 5, "Condition false; no return."

        if opcode == 0xCD: a=self._fetch16(); self._stack.push_pc(); R.PC=a; return f"CALL {a:04X}H",17,f"Call {a:04X}H."
        if opcode == 0xC9: self._stack.pop_pc(); return "RET",10,f"Return → {R.PC:04X}H."
        if opcode == 0xC4: return _call(not F.Z,  "CNZ")
        if opcode == 0xCC: return _call(    F.Z,  "CZ")
        if opcode == 0xD4: return _call(not F.CY, "CNC")
        if opcode == 0xDC: return _call(    F.CY, "CC")
        if opcode == 0xE4: return _call(not F.P,  "CPO")
        if opcode == 0xEC: return _call(    F.P,  "CPE")
        if opcode == 0xF4: return _call(not F.S,  "CP")
        if opcode == 0xFC: return _call(    F.S,  "CM")
        if opcode == 0xC0: return _ret(not F.Z,   "RNZ")
        if opcode == 0xC8: return _ret(    F.Z,   "RZ")
        if opcode == 0xD0: return _ret(not F.CY,  "RNC")
        if opcode == 0xD8: return _ret(    F.CY,  "RC")
        if opcode == 0xE0: return _ret(not F.P,   "RPO")
        if opcode == 0xE8: return _ret(    F.P,   "RPE")
        if opcode == 0xF0: return _ret(not F.S,   "RP")
        if opcode == 0xF8: return _ret(    F.S,   "RM")

        # ── RST n ────────────────────────────────────────────────────────
        if opcode in (0xC7,0xCF,0xD7,0xDF,0xE7,0xEF,0xF7,0xFF):
            n = (opcode >> 3) & 7
            a = n * 8
            self._stack.push_pc(); R.PC = a
            return f"RST {n}", 11, f"Call {a:04X}H (RST {n})."

        # ── I/O ──────────────────────────────────────────────────────────
        if opcode == 0xD3:
            port = self._fetch8()
            self.iom_signal = True
            return f"OUT {port:02X}H", 10, f"Output A({R.A:02X}H) → port {port:02X}H."
        if opcode == 0xDB:
            port = self._fetch8()
            self.iom_signal = True
            R.A = 0x00      # no physical I/O ports; input = 0
            return f"IN {port:02X}H", 10, f"Input port {port:02X}H → A = {R.A:02X}H."

        # ── Interrupt control ─────────────────────────────────────────────
        if opcode == 0xFB: return "EI", 4, "Interrupts enabled."
        if opcode == 0xF3: return "DI", 4, "Interrupts disabled."

        # ── DAA ──────────────────────────────────────────────────────────
        if opcode == 0x27:
            a  = R.A; cy = F.CY
            if (a & 0x0F) > 9 or F.AC: a += 0x06
            if a > 0x9F or cy:         a += 0x60; cy = 1
            R.A = F.update_after_daa(a, cy)
            return "DAA", 4, f"Decimal Adjust A = {R.A:02X}H."

        # ── Unknown opcode ────────────────────────────────────────────────
        raise IllegalOpcodeError(
            f"Invalid opcode at {fetch_pc:04X}H\nExecution halted."
        )

    # ==================================================================
    # Result builder
    # ==================================================================

    def _make_result(
        self, fetch_pc: int, opcode: int, inst: str, log: str, ts: int
    ) -> Dict[str, Any]:
        R = self._regs
        F = self._flags
        return {
            "pc"         : fetch_pc,
            "next_pc"    : R.PC,
            "opcode"     : opcode,
            "instruction": inst,
            "A"          : R.A,
            "B"          : R.B, "C": R.C,
            "D"          : R.D, "E": R.E,
            "H"          : R.H, "L": R.L,
            "SP"         : R.SP,
            "PC"         : R.PC,
            "HL"         : R.HL,
            "BC"         : R.BC,
            "DE"         : R.DE,
            "flags"      : F.snapshot(),
            "address_bus": self.address_bus,
            "data_bus"   : self.data_bus,
            "halted"     : self.halted,
            "t_states"   : ts,
            "log"        : log,
        }
