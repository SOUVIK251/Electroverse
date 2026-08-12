"""
i8085.memory — 64 KB Address Space
====================================
Models the complete Intel 8085 memory map:

    0000H – 1FFFH  : ROM / Monitor area  (write-protected by default)
    2000H – FFFFH  : User RAM            (fully read/write)

Usage
-----
    mem = Memory8085()
    mem.write(0x2000, 0x3E)   # store byte in RAM
    val = mem.read(0x2000)    # read byte
    mem.write_direct(0x2000, 0xFF)  # bypass protection (monitor/loader use)
"""

from typing import List, Tuple


class MemoryError8085(Exception):
    """Raised when an illegal memory operation is attempted."""


class Memory8085:
    """
    64 KB flat memory for the Intel 8085A.

    Parameters
    ----------
    rom_end : int
        Last address of the write-protected ROM region (default 0x1FFF).
    write_protect : bool
        Enforce ROM write-protection (default True).
    """

    ROM_END   : int = 0x1FFF   # 0000H–1FFFH  protected ROM
    RAM_START : int = 0x2000   # 2000H–FFFFH  user RAM

    def __init__(self, rom_end: int = 0x1FFF, write_protect: bool = True):
        self._data          : bytearray = bytearray(65536)
        self._written_mask  : bytearray = bytearray(65536)
        self._rom_end       : int       = rom_end & 0xFFFF
        self._write_protect : bool      = write_protect

    # ------------------------------------------------------------------
    # Core read / write
    # ------------------------------------------------------------------

    def read(self, addr: int) -> int:
        """Read one byte from *addr* (0000H–FFFFH)."""
        return self._data[addr & 0xFFFF]

    def is_written(self, addr: int) -> bool:
        """Return True if *addr* has been written to by user or program loader."""
        return bool(self._written_mask[addr & 0xFFFF])

    def write(self, addr: int, val: int) -> None:
        """
        Write *val* to *addr*.

        Raises
        ------
        MemoryError8085
            If write-protection is active and *addr* is in the ROM region.
        """
        addr &= 0xFFFF
        if self._write_protect and addr <= self._rom_end:
            raise MemoryError8085(
                f"Write to ROM region {addr:04X}H is protected "
                f"(ROM: 0000H–{self._rom_end:04X}H)."
            )
        self._data[addr] = val & 0xFF
        self._written_mask[addr] = 1

    def write_direct(self, addr: int, val: int) -> None:
        """
        Write *val* to *addr* bypassing write-protection.

        Used by the monitor / program loader, not by the CPU during
        normal program execution.
        """
        addr &= 0xFFFF
        self._data[addr] = val & 0xFF
        self._written_mask[addr] = 1

    # ------------------------------------------------------------------
    # Bulk helpers
    # ------------------------------------------------------------------

    def load(self, start_addr: int, data: List[int]) -> None:
        """
        Load a sequence of bytes into memory starting at *start_addr*.
        Always bypasses write-protection (loader operation).
        """
        for i, byte in enumerate(data):
            addr = (start_addr + i) & 0xFFFF
            self._data[addr] = byte & 0xFF
            self._written_mask[addr] = 1

    def fill(self, start_addr: int, end_addr: int, val: int) -> None:
        """
        Fill addresses [*start_addr*, *end_addr*] with *val*.
        Respects write-protection; raises MemoryError8085 on violation.
        """
        val &= 0xFF
        for addr in range(start_addr & 0xFFFF, (end_addr & 0xFFFF) + 1):
            self.write(addr, val)

    def clear_ram(self) -> None:
        """Zero all RAM locations (2000H–FFFFH). ROM region is untouched."""
        for i in range(self.RAM_START, 0x10000):
            self._data[i] = 0x00
            self._written_mask[i] = 0

    def clear_all(self) -> None:
        """Zero the entire 64 KB address space (including ROM region)."""
        for i in range(0x10000):
            self._data[i] = 0x00
            self._written_mask[i] = 0

    # ------------------------------------------------------------------
    # Inspection helpers
    # ------------------------------------------------------------------

    def dump(self, start_addr: int, count: int) -> List[Tuple[int, int]]:
        """
        Return a list of (address, byte) pairs.

        Parameters
        ----------
        start_addr : int
            First address to include.
        count : int
            Number of bytes to return.

        Returns
        -------
        list of (int, int)
            [(addr, byte), ...]
        """
        result = []
        for i in range(count):
            addr = (start_addr + i) & 0xFFFF
            result.append((addr, self._data[addr]))
        return result

    def get_raw(self) -> bytearray:
        """Return a read-only view of the raw memory bytearray."""
        return self._data

    def dump_written_memory(self) -> List[Tuple[int, int]]:
        """Return list of (addr, byte) pairs for all addresses written."""
        result = []
        for i in range(65536):
            if self._written_mask[i]:
                result.append((i, self._data[i]))
        return result

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def write_protect(self) -> bool:
        return self._write_protect

    @write_protect.setter
    def write_protect(self, enabled: bool) -> None:
        self._write_protect = enabled

    @property
    def rom_end(self) -> int:
        return self._rom_end

    def __getitem__(self, addr: int) -> int:
        return self._data[addr & 0xFFFF]

    def __setitem__(self, addr: int, val: int) -> None:
        self._data[addr & 0xFFFF] = val & 0xFF

    def __len__(self) -> int:
        return 65536
