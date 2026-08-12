"""
i8085.flags — Intel 8085A Status Flags
=======================================
The 8085 has five status flags stored in the F (PSW low byte) register:

    Bit 7  S   Sign flag       (1 = negative result, i.e., bit-7 of result = 1)
    Bit 6  Z   Zero flag       (1 = result is zero)
    Bit 5  —   (always 0 in F byte)
    Bit 4  AC  Auxiliary Carry (carry out of bit-3 into bit-4)
    Bit 3  —   (always 0 in F byte)
    Bit 2  P   Parity flag     (1 = even number of 1-bits in result)
    Bit 1  —   (always 1 in 8085 PSW)
    Bit 0  CY  Carry flag      (1 = carry/borrow out of bit-7)

PSW byte encoding:  S Z 0 AC 0 P 1 CY

Affected flags per instruction class
--------------------------------------
Arithmetic (ADD, ADC, SUB, SBB, INR, DCR, ADI, ACI, SUI, SBI, DAA):
    S, Z, AC, P are always updated.
    CY is updated by ADD/SUB family but NOT by INR/DCR.

Logical (ANA, ORA, XRA, ANI, ORI, XRI):
    S, Z, P are updated.
    CY is always cleared.
    AC: set by ANA/ANI, cleared by ORA/XRA/ORI/XRI.

Compare (CMP, CPI):
    S, Z, AC, P, CY updated (same as SUB but result not stored).

Rotate (RLC, RRC, RAL, RAR):
    Only CY is affected.
"""

from typing import Dict


class Flags8085:
    """Intel 8085A status flags with hardware-accurate update rules."""

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Set all flags to their power-on / RESET state (all 0)."""
        self.S  : int = 0   # Sign
        self.Z  : int = 0   # Zero
        self.AC : int = 0   # Auxiliary Carry
        self.P  : int = 0   # Parity
        self.CY : int = 0   # Carry

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parity(val: int) -> int:
        """Return 1 if *val* has an even number of 1-bits (even parity)."""
        return 1 if bin(val & 0xFF).count('1') % 2 == 0 else 0

    def _update_szp(self, result: int) -> None:
        """Update S, Z, and P from *result* (8-bit)."""
        r       = result & 0xFF
        self.S  = 1 if (r & 0x80) else 0
        self.Z  = 1 if (r == 0)   else 0
        self.P  = self._parity(r)

    # ------------------------------------------------------------------
    # Flag update methods
    # ------------------------------------------------------------------

    def update_after_add(self, a: int, b: int, cy_in: int = 0) -> int:
        """
        Update all flags for an addition  result = A + B + cy_in.

        Returns the 8-bit result.
        """
        full    = a + b + cy_in
        result  = full & 0xFF
        self._update_szp(result)
        self.CY = 1 if full > 0xFF else 0
        self.AC = 1 if ((a & 0x0F) + (b & 0x0F) + cy_in) > 0x0F else 0
        return result

    def update_after_sub(self, a: int, b: int, cy_in: int = 0) -> int:
        """
        Update all flags for a subtraction  result = A - B - cy_in.

        Returns the 8-bit result.
        """
        full    = a - b - cy_in
        result  = full & 0xFF
        self._update_szp(result)
        self.CY = 1 if full < 0 else 0
        self.AC = 1 if ((a & 0x0F) - (b & 0x0F) - cy_in) < 0 else 0
        return result

    def update_after_inr(self, before: int) -> int:
        """
        Update flags for INR (increment).  CY is NOT affected.

        Returns the incremented 8-bit result.
        """
        result  = (before + 1) & 0xFF
        cy_save = self.CY
        self._update_szp(result)
        self.AC = 1 if (result & 0x0F) == 0 else 0   # carry out of bit-3
        self.CY = cy_save                              # CY unaffected by INR
        return result

    def update_after_dcr(self, before: int) -> int:
        """
        Update flags for DCR (decrement).  CY is NOT affected.

        Returns the decremented 8-bit result.
        """
        result  = (before - 1) & 0xFF
        cy_save = self.CY
        self._update_szp(result)
        self.AC = 1 if (result & 0x0F) == 0x0F else 0  # borrow into bit-3
        self.CY = cy_save
        return result

    def update_after_logic(self, result: int, ac_val: int = 0) -> int:
        """
        Update flags for logical operations (ANA, ORA, XRA, ANI, ORI, XRI).

        *ac_val* = 1 for ANA/ANI (AC set), 0 for ORA/XRA/ORI/XRI (AC cleared).
        CY is always cleared.

        Returns the 8-bit result.
        """
        r      = result & 0xFF
        self._update_szp(r)
        self.CY = 0
        self.AC = ac_val
        return r

    def update_after_rotate_cy(self, cy: int) -> None:
        """Update only the CY flag (for RLC, RRC, RAL, RAR)."""
        self.CY = cy & 1

    def update_after_daa(self, result: int, cy_new: int) -> int:
        """Update S, Z, P, CY, AC after DAA."""
        r      = result & 0xFF
        self._update_szp(r)
        self.CY = cy_new
        return r

    # ------------------------------------------------------------------
    # PSW encode / decode
    # ------------------------------------------------------------------

    def get_psw(self) -> int:
        """
        Encode flags as the 8-bit PSW byte.

        Layout:  S Z 0 AC 0 P 1 CY
        """
        f  = 0x02              # bit-1 is always 1 in 8085 PSW
        if self.S:  f |= 0x80
        if self.Z:  f |= 0x40
        if self.AC: f |= 0x10
        if self.P:  f |= 0x04
        if self.CY: f |= 0x01
        return f

    def set_psw(self, byte: int) -> None:
        """Decode a PSW byte and restore flags (used by POP PSW)."""
        self.S  = 1 if (byte & 0x80) else 0
        self.Z  = 1 if (byte & 0x40) else 0
        self.AC = 1 if (byte & 0x10) else 0
        self.P  = 1 if (byte & 0x04) else 0
        self.CY = 1 if (byte & 0x01) else 0

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, int]:
        """Return an immutable dict of current flag values."""
        return {
            'S' : self.S,
            'Z' : self.Z,
            'AC': self.AC,
            'P' : self.P,
            'CY': self.CY,
        }

    def __repr__(self) -> str:
        return (
            f"Flags8085(S={self.S} Z={self.Z} AC={self.AC} "
            f"P={self.P} CY={self.CY} PSW={self.get_psw():02X}H)"
        )
