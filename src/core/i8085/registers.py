"""
i8085.registers — Intel 8085A Register File
============================================
Maintains all programmer-visible registers of the Intel 8085A:

    8-bit general-purpose  : A (accumulator), B, C, D, E, H, L
    16-bit special-purpose : SP (stack pointer), PC (program counter)

Register pairs (used by LXI, PUSH, POP, etc.):
    BC  = (B << 8) | C
    DE  = (D << 8) | E
    HL  = (H << 8) | L
    PSW = (A << 8) | flags_byte   (handled by Flags8085)

Default after power-on / RESET
-------------------------------
    A, B, C, D, E, H, L  →  00H
    SP                    →  FFFFH   (top of memory)
    PC                    →  2000H   (start of user RAM)
"""

from typing import Dict, Any


class Registers8085:
    """All programmer-visible registers of the Intel 8085A."""

    BOOT_PC : int = 0x2000   # default program start address
    BOOT_SP : int = 0xFFFF   # default stack pointer

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset all registers to power-on defaults."""
        self.A  : int = 0x00
        self.B  : int = 0x00
        self.C  : int = 0x00
        self.D  : int = 0x00
        self.E  : int = 0x00
        self.H  : int = 0x00
        self.L  : int = 0x00
        self.SP : int = self.BOOT_SP
        self.PC : int = self.BOOT_PC

    # ------------------------------------------------------------------
    # Register pair accessors (BC, DE, HL)
    # ------------------------------------------------------------------

    @property
    def BC(self) -> int:
        return (self.B << 8) | self.C

    @BC.setter
    def BC(self, val: int) -> None:
        val      &= 0xFFFF
        self.B    = (val >> 8) & 0xFF
        self.C    = val & 0xFF

    @property
    def DE(self) -> int:
        return (self.D << 8) | self.E

    @DE.setter
    def DE(self, val: int) -> None:
        val      &= 0xFFFF
        self.D    = (val >> 8) & 0xFF
        self.E    = val & 0xFF

    @property
    def HL(self) -> int:
        return (self.H << 8) | self.L

    @HL.setter
    def HL(self, val: int) -> None:
        val      &= 0xFFFF
        self.H    = (val >> 8) & 0xFF
        self.L    = val & 0xFF

    # ------------------------------------------------------------------
    # Index-based register access (8085 encoding: 0=B,1=C,…,7=A, 6=M)
    # ------------------------------------------------------------------

    # Register name lookup by 3-bit index
    _IDX_TO_NAME = {0:'B', 1:'C', 2:'D', 3:'E', 4:'H', 5:'L', 6:'M', 7:'A'}

    def get_by_index(self, idx: int) -> int:
        """
        Return the value of the register encoded by *idx* (0–7).
        Index 6 (M) is NOT handled here; the CPU resolves it to memory.
        """
        name = self._IDX_TO_NAME.get(idx & 7)
        if name and name != 'M':
            return getattr(self, name)
        raise ValueError(f"Register index {idx} not directly accessible.")

    def set_by_index(self, idx: int, val: int) -> None:
        """Set a register by its 3-bit opcode index (not index 6 / M)."""
        name = self._IDX_TO_NAME.get(idx & 7)
        if name and name != 'M':
            setattr(self, name, val & 0xFF)
        else:
            raise ValueError(f"Register index {idx} not directly settable.")

    def name_of(self, idx: int) -> str:
        """Return the human-readable name for a 3-bit register index."""
        return self._IDX_TO_NAME.get(idx & 7, '?')

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return an immutable dict of the current register state."""
        return {
            'A' : self.A,
            'B' : self.B,
            'C' : self.C,
            'D' : self.D,
            'E' : self.E,
            'H' : self.H,
            'L' : self.L,
            'SP': self.SP,
            'PC': self.PC,
            'BC': self.BC,
            'DE': self.DE,
            'HL': self.HL,
        }

    def __repr__(self) -> str:
        return (
            f"Registers8085("
            f"A={self.A:02X}H B={self.B:02X}H C={self.C:02X}H "
            f"D={self.D:02X}H E={self.E:02X}H "
            f"H={self.H:02X}H L={self.L:02X}H "
            f"SP={self.SP:04X}H PC={self.PC:04X}H)"
        )
