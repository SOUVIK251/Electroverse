"""
i8085.execution_logger — Step-by-Step Execution Audit Trail
=============================================================
Records every instruction executed by the 8085 CPU engine.

Each log entry contains:
    step        Sequential step number (1-based)
    pc          PC value at time of fetch (address of opcode)
    opcode      Raw opcode byte
    instruction Decoded mnemonic string  (e.g. "MVI A, 05H")
    registers   Full register snapshot after execution
    flags       Full flag snapshot after execution
    t_states    T-states consumed by this instruction
    log         Human-readable description of what happened

Usage
-----
    logger = ExecutionLogger()
    logger.log_step(pc=0x2000, opcode=0x3E, instruction="MVI A, 05H",
                    registers={...}, flags={...}, t_states=7,
                    log_msg="Loaded 05H into A.")
    entries = logger.get_log()     # list of dicts
    text    = logger.get_text()    # formatted string for display
    logger.clear()
"""

from typing import Dict, Any, List
from datetime import datetime


class ExecutionLogger:
    """
    Records each instruction execution step for display and debugging.

    The logger is purely a data store — it has no dependencies on other
    backend modules.
    """

    MAX_ENTRIES : int = 10_000   # cap to prevent unbounded growth

    def __init__(self, max_entries: int = MAX_ENTRIES):
        self._max    : int        = max_entries
        self._entries: List[Dict] = []
        self._step   : int        = 0

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log_step(
        self,
        pc          : int,
        opcode      : int,
        instruction : str,
        registers   : Dict[str, Any],
        flags       : Dict[str, int],
        t_states    : int  = 0,
        log_msg     : str  = "",
    ) -> None:
        """
        Record one instruction execution.

        Parameters
        ----------
        pc          : Program counter at the time of fetch.
        opcode      : Raw opcode byte.
        instruction : Decoded mnemonic string.
        registers   : Snapshot dict from Registers8085.snapshot().
        flags       : Snapshot dict from Flags8085.snapshot().
        t_states    : T-state count for this instruction.
        log_msg     : Human-readable description of side-effects.
        """
        if len(self._entries) >= self._max:
            # Drop oldest entries (circular behaviour)
            self._entries = self._entries[-(self._max // 2):]

        self._step += 1
        entry = {
            "step"        : self._step,
            "pc"          : pc,
            "pc_str"      : f"{pc:04X}H",
            "opcode"      : opcode,
            "opcode_str"  : f"{opcode:02X}H",
            "instruction" : instruction,
            "registers"   : dict(registers),
            "flags"       : dict(flags),
            "t_states"    : t_states,
            "log"         : log_msg,
            "timestamp"   : datetime.now().isoformat(timespec='milliseconds'),
        }
        self._entries.append(entry)

    def log_event(self, message: str) -> None:
        """Log a non-instruction event (e.g. RESET, HLT, error)."""
        self._entries.append({
            "step"        : None,
            "pc"          : None,
            "pc_str"      : "--",
            "opcode"      : None,
            "opcode_str"  : "--",
            "instruction" : "EVENT",
            "registers"   : {},
            "flags"       : {},
            "t_states"    : 0,
            "log"         : message,
            "timestamp"   : datetime.now().isoformat(timespec='milliseconds'),
        })

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_log(self) -> List[Dict]:
        """Return all log entries as a list of dicts (newest last)."""
        return list(self._entries)

    def get_last(self, n: int = 1) -> List[Dict]:
        """Return the last *n* entries."""
        return self._entries[-n:]

    def get_text(self, max_lines: int = 200) -> str:
        """
        Return a formatted multi-line string of the execution log
        suitable for display in a console widget.
        """
        lines = []
        for e in self._entries[-max_lines:]:
            if e["step"] is None:
                lines.append(f">>> {e['log']}")
            else:
                reg_a  = e["registers"].get("A", 0)
                reg_pc = e["registers"].get("PC", 0)
                lines.append(
                    f"Step {e['step']:4d}  "
                    f"[{e['pc_str']}]  "
                    f"{e['opcode_str']}  "
                    f"{e['instruction']:<22s}  "
                    f"A={reg_a:02X}H PC={reg_pc:04X}H  "
                    f"{e['log']}"
                )
        return "\n".join(lines)

    def get_program_list(self, memory_data: List[tuple]) -> str:
        """
        Format a list of (address, byte) pairs as an assembly listing.

        Parameters
        ----------
        memory_data : list of (addr, byte) returned by Memory8085.dump()

        Returns
        -------
        str  — formatted two-column listing:
               Address     Opcode
               2000H       3E
               2001H       05
               ...
        """
        lines  = ["Address     Opcode", "-" * 22]
        for addr, byte in memory_data:
            if byte != 0x00:   # skip uninitialized
                lines.append(f"{addr:04X}H       {byte:02X}H")
        return "\n".join(lines) if len(lines) > 2 else "No program stored."

    def total_t_states(self) -> int:
        """Return the cumulative T-state count over all logged steps."""
        return sum(
            e["t_states"] for e in self._entries if e["step"] is not None
        )

    def step_count(self) -> int:
        """Return the total number of instruction steps logged."""
        return self._step

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Erase all log entries and reset the step counter."""
        self._entries.clear()
        self._step = 0
