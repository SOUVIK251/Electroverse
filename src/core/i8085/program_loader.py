"""
i8085.program_loader — Intel HEX / Binary Program File I/O
============================================================
Handles loading programs into and saving programs from the 8085 Memory.

Supported formats
-----------------
Intel HEX (.hex, .ihex)
    Industry-standard ASCII hex records (record types 00 = data, 01 = EOF).
    Checksum validated on load.

Binary (.bin)
    Raw byte stream loaded at a user-specified start address.

Assembly source (.asm)  [basic mnemonics only, single-pass]
    Parses lines like:
        2000H: 3E 45          ; MVI A, 45H
    and loads the hex bytes directly.  Label resolution is NOT supported.

Usage
-----
    loader  = ProgramLoader()
    records = loader.load_ihex("program.hex", memory)
    loader.save_ihex("output.hex", memory, start=0x2000, end=0x2050)
    loader.save_bin("output.bin",  memory, start=0x2000, end=0x2050)
"""

import os
from typing import List, Tuple, Optional
from .memory import Memory8085


class ProgramLoaderError(Exception):
    """Raised when a file cannot be loaded or saved."""


class ProgramLoader:
    """Load and save 8085 programs in Intel HEX or binary format."""

    # ------------------------------------------------------------------
    # Intel HEX load
    # ------------------------------------------------------------------

    def load_ihex(
        self,
        path: str,
        memory: Memory8085,
        *,
        start_addr_override: Optional[int] = None,
    ) -> List[Tuple[int, int]]:
        """
        Load an Intel HEX file into *memory*.

        Parameters
        ----------
        path                : Path to the .hex file.
        memory              : Target Memory8085 object.
        start_addr_override : If provided, all records are offset so the
                              first data byte lands at this address.

        Returns
        -------
        list of (address, byte) that were written.

        Raises
        ------
        ProgramLoaderError  on file-not-found, bad checksum, or format error.
        """
        if not os.path.isfile(path):
            raise ProgramLoaderError(f"File not found: {path}")

        written: List[Tuple[int, int]] = []
        first_addr: Optional[int]      = None
        offset: int                    = 0

        try:
            with open(path, "r", encoding="ascii", errors="replace") as fh:
                for line_no, raw in enumerate(fh, start=1):
                    line = raw.strip()
                    if not line:
                        continue
                    if not line.startswith(":"):
                        raise ProgramLoaderError(
                            f"Line {line_no}: missing ':' start code."
                        )
                    try:
                        rec_bytes = bytes.fromhex(line[1:])
                    except ValueError:
                        raise ProgramLoaderError(
                            f"Line {line_no}: invalid hex digits."
                        )

                    # Verify checksum
                    chk = sum(rec_bytes) & 0xFF
                    if chk != 0:
                        raise ProgramLoaderError(
                            f"Line {line_no}: checksum error "
                            f"(expected 0, got {chk:02X}H)."
                        )

                    rec_len  = rec_bytes[0]
                    addr     = (rec_bytes[1] << 8) | rec_bytes[2]
                    rec_type = rec_bytes[3]

                    if rec_type == 0x01:   # EOF
                        break

                    if rec_type == 0x00:   # Data
                        if first_addr is None:
                            first_addr = addr
                            if start_addr_override is not None:
                                offset = start_addr_override - first_addr

                        for i in range(rec_len):
                            dest = (addr + i + offset) & 0xFFFF
                            val  = rec_bytes[4 + i]
                            memory.write_direct(dest, val)
                            written.append((dest, val))

        except OSError as e:
            raise ProgramLoaderError(f"Cannot read file: {e}")

        return written

    # ------------------------------------------------------------------
    # Intel HEX save
    # ------------------------------------------------------------------

    def save_ihex(
        self,
        path: str,
        memory: Memory8085,
        start: int = 0x2000,
        end: int   = 0x7FFF,
        bytes_per_record: int = 16,
    ) -> int:
        """
        Save a region of *memory* as an Intel HEX file.

        Parameters
        ----------
        path             : Destination file path.
        memory           : Source Memory8085 object.
        start / end      : Inclusive address range to export.
        bytes_per_record : Bytes per data record (default 16).

        Returns
        -------
        Number of bytes written.
        """
        try:
            lines: List[str] = []
            total = 0
            addr  = start & 0xFFFF

            while addr <= (end & 0xFFFF):
                chunk_len = min(bytes_per_record, (end & 0xFFFF) - addr + 1)
                chunk     = [memory.read((addr + i) & 0xFFFF)
                             for i in range(chunk_len)]
                data_str  = "".join(f"{b:02X}" for b in chunk)
                checksum  = (
                    chunk_len + (addr >> 8) + (addr & 0xFF) + sum(chunk)
                ) & 0xFF
                checksum  = ((~checksum) + 1) & 0xFF
                lines.append(
                    f":{chunk_len:02X}{addr:04X}00{data_str}{checksum:02X}"
                )
                total += chunk_len
                addr  += chunk_len

            lines.append(":00000001FF")   # EOF record

            with open(path, "w", encoding="ascii") as fh:
                fh.write("\n".join(lines) + "\n")

            return total

        except OSError as e:
            raise ProgramLoaderError(f"Cannot write file: {e}")

    # ------------------------------------------------------------------
    # Binary load / save
    # ------------------------------------------------------------------

    def load_bin(
        self,
        path: str,
        memory: Memory8085,
        start_addr: int = 0x2000,
    ) -> int:
        """
        Load a raw binary file into *memory* at *start_addr*.

        Returns the number of bytes loaded.
        """
        if not os.path.isfile(path):
            raise ProgramLoaderError(f"File not found: {path}")
        try:
            with open(path, "rb") as fh:
                data = fh.read()
            for i, byte in enumerate(data):
                memory.write_direct((start_addr + i) & 0xFFFF, byte)
            return len(data)
        except OSError as e:
            raise ProgramLoaderError(f"Cannot read file: {e}")

    def save_bin(
        self,
        path: str,
        memory: Memory8085,
        start: int = 0x2000,
        end: int   = 0x7FFF,
    ) -> int:
        """
        Save a region of *memory* as a raw binary file.

        Returns the number of bytes saved.
        """
        try:
            data = bytes(
                memory.read(addr & 0xFFFF)
                for addr in range(start & 0xFFFF, (end & 0xFFFF) + 1)
            )
            with open(path, "wb") as fh:
                fh.write(data)
            return len(data)
        except OSError as e:
            raise ProgramLoaderError(f"Cannot write file: {e}")

    # ------------------------------------------------------------------
    # Inline hex string loader (for UI paste / manual entry)
    # ------------------------------------------------------------------

    def load_hex_string(
        self,
        hex_str: str,
        memory: Memory8085,
        start_addr: int = 0x2000,
    ) -> List[Tuple[int, int]]:
        """
        Load a space-separated hex string into *memory*.

        Example:
            hex_str = "3E 45 06 23 80 76"
            → stores [3EH, 45H, 06H, 23H, 80H, 76H] at start_addr

        Returns
        -------
        list of (address, byte) written.

        Raises
        ------
        ProgramLoaderError if any token is not a valid hex byte.
        """
        tokens  = hex_str.upper().replace(",", " ").split()
        written = []
        for i, tok in enumerate(tokens):
            tok = tok.rstrip("H")
            if len(tok) not in (1, 2) or not all(c in "0123456789ABCDEF" for c in tok):
                raise ProgramLoaderError(
                    f"Invalid hex byte at position {i}: '{tok}'"
                )
            addr = (start_addr + i) & 0xFFFF
            val  = int(tok, 16)
            memory.write_direct(addr, val)
            written.append((addr, val))
        return written
