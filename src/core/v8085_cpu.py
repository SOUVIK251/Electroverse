"""
v8085_cpu — Virtual 8085 CPU Façade
=====================================
Public interface for the 8085 backend used by the trainer UI.

This module is a thin façade over the clean modular backend in
src/core/i8085/.  All CPU logic now lives in separate modules:

    i8085.memory             → Memory8085
    i8085.registers          → Registers8085
    i8085.flags              → Flags8085
    i8085.stack              → Stack8085
    i8085.instruction_decoder → InstructionDecoder
    i8085.execution_engine   → ExecutionEngine
    i8085.program_loader     → ProgramLoader
    i8085.execution_logger   → ExecutionLogger

The UI only ever instantiates Virtual8085CPU and calls:
    reset()           – reset registers & flags; memory preserved
    step()            – single instruction; returns result dict
    run(callback)     – continuous until HLT
    load_program()    – load raw bytes at an address
    read_mem()        – read from memory (bus-aware)
    write_mem()       – write to memory (with ROM protection)
    write_mem_direct()– write bypassing protection
    get_state_snapshot() – full CPU state dict

Public exceptions re-exported for callers that import from here:
    CPUError          → IllegalOpcodeError
    MemoryAccessError → MemoryError8085
"""

from typing import Dict, Any, List, Optional, Callable

from src.core.i8085.memory             import Memory8085, MemoryError8085
from src.core.i8085.registers          import Registers8085
from src.core.i8085.flags              import Flags8085
from src.core.i8085.stack              import Stack8085
from src.core.i8085.instruction_decoder import InstructionDecoder
from src.core.i8085.execution_engine   import ExecutionEngine, IllegalOpcodeError
from src.core.i8085.program_loader     import ProgramLoader, ProgramLoaderError
from src.core.i8085.execution_logger   import ExecutionLogger


# Aliases so existing callers that do
#   from src.core.v8085_cpu import CPUError, MemoryAccessError
# continue to work without change.
CPUError          = IllegalOpcodeError
MemoryAccessError = MemoryError8085


class Virtual8085CPU:
    """
    Complete Virtual Intel 8085A Microprocessor.

    Delegates all logic to the i8085 backend modules.
    The UI layer only calls this class.
    """

    def __init__(self):
        # ── Instantiate all backend modules ─────────────────────────
        self.memory   = Memory8085()
        self.regs     = Registers8085()
        self.flags    = Flags8085()
        self.stack    = Stack8085(self.memory, self.regs, self.flags)
        self.decoder  = InstructionDecoder()
        self.logger   = ExecutionLogger()
        self.loader   = ProgramLoader()
        self.engine   = ExecutionEngine(
            self.memory, self.regs, self.flags, self.stack, self.logger
        )

    # ------------------------------------------------------------------
    # Convenience properties — expose bus signals from engine
    # ------------------------------------------------------------------

    @property
    def address_bus(self) -> int:  return self.engine.address_bus
    @property
    def data_bus(self)    -> int:  return self.engine.data_bus
    @property
    def ale_signal(self)  -> bool: return self.engine.ale_signal
    @property
    def rd_signal(self)   -> bool: return self.engine.rd_signal
    @property
    def wr_signal(self)   -> bool: return self.engine.wr_signal
    @property
    def iom_signal(self)  -> bool: return self.engine.iom_signal

    @property
    def halted(self) -> bool: return self.engine.halted
    @halted.setter
    def halted(self, v: bool): self.engine.halted = v

    # ── Register shortcuts (UI reads these directly) ──────────────────

    @property
    def A(self)  -> int:  return self.regs.A
    @A.setter
    def A(self, v): self.regs.A = v & 0xFF

    @property
    def B(self)  -> int:  return self.regs.B
    @B.setter
    def B(self, v): self.regs.B = v & 0xFF

    @property
    def C(self)  -> int:  return self.regs.C
    @C.setter
    def C(self, v): self.regs.C = v & 0xFF

    @property
    def D(self)  -> int:  return self.regs.D
    @D.setter
    def D(self, v): self.regs.D = v & 0xFF

    @property
    def E(self)  -> int:  return self.regs.E
    @E.setter
    def E(self, v): self.regs.E = v & 0xFF

    @property
    def H(self)  -> int:  return self.regs.H
    @H.setter
    def H(self, v): self.regs.H = v & 0xFF

    @property
    def L(self)  -> int:  return self.regs.L
    @L.setter
    def L(self, v): self.regs.L = v & 0xFF

    @property
    def SP(self) -> int:  return self.regs.SP
    @SP.setter
    def SP(self, v): self.regs.SP = v & 0xFFFF

    @property
    def PC(self) -> int:  return self.regs.PC
    @PC.setter
    def PC(self, v): self.regs.PC = v & 0xFFFF

    # ── Flag shortcuts ────────────────────────────────────────────────

    @property
    def flag_S(self)  -> int: return self.flags.S
    @flag_S.setter
    def flag_S(self, v): self.flags.S = v & 1

    @property
    def flag_Z(self)  -> int: return self.flags.Z
    @flag_Z.setter
    def flag_Z(self, v): self.flags.Z = v & 1

    @property
    def flag_AC(self) -> int: return self.flags.AC
    @flag_AC.setter
    def flag_AC(self, v): self.flags.AC = v & 1

    @property
    def flag_P(self)  -> int: return self.flags.P
    @flag_P.setter
    def flag_P(self, v): self.flags.P = v & 1

    @property
    def flag_CY(self) -> int: return self.flags.CY
    @flag_CY.setter
    def flag_CY(self, v): self.flags.CY = v & 1

    # ── ROM boundary (used by trainer widget for protection check) ────

    ROM_END   = Memory8085.ROM_END
    RAM_START = Memory8085.RAM_START

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset all registers, flags, and execution state.
        Memory is NOT cleared (trainer-kit behaviour).
        """
        self.regs.reset()
        self.flags.reset()
        self.engine.reset()
        self.logger.log_event("CPU RESET — registers and flags cleared. Memory intact.")

    def step(self) -> Dict[str, Any]:
        """
        Execute exactly one instruction.

        Returns
        -------
        result dict with keys:
            pc, next_pc, opcode, instruction,
            A, B, C, D, E, H, L, SP, PC,
            flags {S, Z, AC, P, CY},
            address_bus, data_bus, halted, t_states, log
        """
        return self.engine.step()

    def run(
        self,
        step_callback: Optional[Callable[[Dict], None]] = None,
        max_steps: int = 1_000_000,
    ) -> Dict[str, Any]:
        """
        Execute continuously until HLT, illegal opcode, or max_steps.

        *step_callback* is called after each instruction with the result
        dict — useful for updating the UI from a worker thread.
        """
        return self.engine.run(step_callback, max_steps)

    def pause(self)  -> None: self.engine.pause()
    def resume(self) -> None: self.engine.resume()
    def stop(self)   -> None: self.engine.stop()

    # ------------------------------------------------------------------
    # Memory helpers (UI-facing)
    # ------------------------------------------------------------------

    def read_mem(self, addr: int) -> int:
        """Read one byte with bus-state update (CPU-style access)."""
        addr &= 0xFFFF
        self.engine.address_bus = addr
        self.engine.rd_signal   = True
        self.engine.wr_signal   = False
        val = self.memory.read(addr)
        self.engine.data_bus    = val
        return val

    def write_mem(self, addr: int, val: int) -> None:
        """Write one byte with ROM protection (CPU-style access)."""
        addr &= 0xFFFF
        self.memory.write(addr, val & 0xFF)
        self.engine.address_bus = addr
        self.engine.data_bus    = val & 0xFF
        self.engine.wr_signal   = True
        self.engine.rd_signal   = False

    def write_mem_direct(self, addr: int, val: int) -> None:
        """Write one byte bypassing ROM protection (monitor/keypad use)."""
        self.memory.write_direct(addr & 0xFFFF, val & 0xFF)

    def load_program(self, start_addr: int, program_bytes: List[int]) -> None:
        """Load raw bytes at *start_addr* and set PC to start_addr."""
        self.memory.load(start_addr, program_bytes)
        self.regs.PC = start_addr & 0xFFFF

    # ------------------------------------------------------------------
    # File I/O delegation
    # ------------------------------------------------------------------

    def load_ihex(self, path: str) -> List:
        """Load an Intel HEX file; returns list of (addr, byte) written."""
        return self.loader.load_ihex(path, self.memory)

    def save_ihex(self, path: str, start: int = 0x2000, end: int = 0x7FFF) -> int:
        """Save RAM region as Intel HEX; returns byte count."""
        return self.loader.save_ihex(path, self.memory, start, end)

    def load_bin(self, path: str, start_addr: int = 0x2000) -> int:
        """Load a binary file at start_addr; returns byte count."""
        return self.loader.load_bin(path, self.memory, start_addr)

    def save_bin(self, path: str, start: int = 0x2000, end: int = 0x7FFF) -> int:
        """Save RAM region as binary; returns byte count."""
        return self.loader.save_bin(path, self.memory, start, end)

    def load_hex_string(self, hex_str: str, start_addr: int = 0x2000) -> List:
        """Load a space-separated hex string into RAM."""
        return self.loader.load_hex_string(hex_str, self.memory, start_addr)

    # ------------------------------------------------------------------
    # Snapshot (used by trainer UI to refresh all displays at once)
    # ------------------------------------------------------------------

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Return a complete CPU state dictionary.

        Keys:
            A, B, C, D, E, H, L, SP, PC, HL, BC, DE
            S, Z, AC, P, CY, PSW
            address_bus, data_bus
            halted, t_states
        """
        r  = self.regs
        f  = self.flags
        return {
            "A"  : r.A,  "B": r.B, "C": r.C,
            "D"  : r.D,  "E": r.E,
            "H"  : r.H,  "L": r.L,
            "SP" : r.SP, "PC": r.PC,
            "HL" : r.HL, "BC": r.BC, "DE": r.DE,
            "S"  : f.S,  "Z": f.Z, "AC": f.AC, "P": f.P, "CY": f.CY,
            "PSW": f.get_psw(),
            "address_bus": self.engine.address_bus,
            "data_bus"   : self.engine.data_bus,
            "halted"     : self.engine.halted,
            "t_states"   : self.engine.t_states_total,
        }

    # ------------------------------------------------------------------
    # Execution log (trainer UI console output)
    # ------------------------------------------------------------------

    def get_execution_log(self) -> str:
        """Return a formatted execution log string for console display."""
        return self.logger.get_text()

    def get_log_entries(self) -> list:
        """Return raw log entry dicts."""
        return self.logger.get_log()

    def clear_log(self) -> None:
        """Erase the execution log."""
        self.logger.clear()

    def get_program_listing(
        self, start: int = 0x2000, end: int = 0x20FF
    ) -> str:
        """Return a formatted address/opcode listing of the loaded program."""
        dump = self.memory.dump(start, end - start + 1)
        return self.logger.get_program_listing(dump)

    # ------------------------------------------------------------------
    # Legacy helpers kept for backward compatibility
    # ------------------------------------------------------------------

    def get_hl(self) -> int: return self.regs.HL
    def set_hl(self, v: int): self.regs.HL = v
    def get_bc(self) -> int: return self.regs.BC
    def set_bc(self, v: int): self.regs.BC = v
    def get_de(self) -> int: return self.regs.DE
    def set_de(self, v: int): self.regs.DE = v

    def get_flag_byte(self) -> int: return self.flags.get_psw()
    def set_flag_byte(self, f: int): self.flags.set_psw(f)
