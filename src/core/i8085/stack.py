"""
i8085.stack — Hardware Stack for the Intel 8085A
=================================================
The 8085 uses a 16-bit Stack Pointer (SP) with a descending, full stack:

    PUSH  →  SP–1 ← high_byte,  SP–2 ← low_byte,  SP = SP – 2
    POP   →  low = [SP], high = [SP+1],             SP = SP + 2

The stack lives in RAM and requires no separate storage — it shares the
same Memory8085 object used by the CPU.

Valid PUSH/POP register pairs:
    B   (B, C)
    D   (D, E)
    H   (H, L)
    PSW (A, flags_byte)
"""

from .memory    import Memory8085, MemoryError8085
from .registers import Registers8085
from .flags     import Flags8085


class StackError8085(Exception):
    """Raised when an illegal stack operation is attempted."""


class Stack8085:
    """
    Hardware stack for the Intel 8085A.

    Operates directly on the shared Memory and Registers objects so that
    all stack state is visible through the normal memory map.
    """

    def __init__(self, memory: Memory8085, regs: Registers8085, flags: Flags8085):
        self._mem   = memory
        self._regs  = regs
        self._flags = flags

    # ------------------------------------------------------------------
    # Core push / pop
    # ------------------------------------------------------------------

    def push_word(self, high: int, low: int) -> None:
        """
        Push a 16-bit value (high, low) onto the stack.

        SP = SP – 1 ; [SP] = high
        SP = SP – 1 ; [SP] = low
        """
        self._regs.SP = (self._regs.SP - 1) & 0xFFFF
        self._mem.write_direct(self._regs.SP, high & 0xFF)
        self._regs.SP = (self._regs.SP - 1) & 0xFFFF
        self._mem.write_direct(self._regs.SP, low  & 0xFF)

    def pop_word(self) -> tuple:
        """
        Pop a 16-bit value from the stack.

        low  = [SP] ; SP = SP + 1
        high = [SP] ; SP = SP + 1
        Returns (high, low).
        """
        low           = self._mem.read(self._regs.SP)
        self._regs.SP = (self._regs.SP + 1) & 0xFFFF
        high          = self._mem.read(self._regs.SP)
        self._regs.SP = (self._regs.SP + 1) & 0xFFFF
        return high, low

    # ------------------------------------------------------------------
    # Pair-level helpers (called by PUSH/POP instructions)
    # ------------------------------------------------------------------

    def push_bc(self) -> None:
        self.push_word(self._regs.B, self._regs.C)

    def pop_bc(self) -> None:
        high, low       = self.pop_word()
        self._regs.B    = high
        self._regs.C    = low

    def push_de(self) -> None:
        self.push_word(self._regs.D, self._regs.E)

    def pop_de(self) -> None:
        high, low       = self.pop_word()
        self._regs.D    = high
        self._regs.E    = low

    def push_hl(self) -> None:
        self.push_word(self._regs.H, self._regs.L)

    def pop_hl(self) -> None:
        high, low       = self.pop_word()
        self._regs.H    = high
        self._regs.L    = low

    def push_psw(self) -> None:
        """Push A and the flags byte (PSW)."""
        self.push_word(self._regs.A, self._flags.get_psw())

    def pop_psw(self) -> None:
        """Pop A and the flags byte (PSW)."""
        high, low           = self.pop_word()
        self._regs.A        = high
        self._flags.set_psw(low)

    # ------------------------------------------------------------------
    # CALL / RET helpers (push/pop return address)
    # ------------------------------------------------------------------

    def push_pc(self) -> None:
        """Push the current PC (return address) onto the stack."""
        self.push_word((self._regs.PC >> 8) & 0xFF, self._regs.PC & 0xFF)

    def pop_pc(self) -> None:
        """Pop the return address from the stack into PC."""
        high, low       = self.pop_word()
        self._regs.PC   = (high << 8) | low

    # ------------------------------------------------------------------
    # Stack inspection (debugging / memory viewer)
    # ------------------------------------------------------------------

    def peek(self, depth: int = 8) -> list:
        """
        Return up to *depth* stack entries starting from current SP.

        Returns a list of (address, byte) tuples.
        """
        result = []
        sp = self._regs.SP
        for i in range(depth):
            addr = (sp + i) & 0xFFFF
            result.append((addr, self._mem.read(addr)))
        return result
