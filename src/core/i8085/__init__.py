"""
i8085 Backend Package
=====================
Clean, modular Intel 8085A microprocessor simulation backend.

Modules
-------
memory              64 KB address space with ROM write-protection
registers           All 8085 registers (A, B, C, D, E, H, L, SP, PC)
flags               Status flags (S, Z, AC, P, CY) with PSW encode/decode
stack               Hardware stack using SP + memory
instruction_decoder Opcode → mnemonic, length, description table
execution_engine    Fetch–Decode–Execute loop with full instruction set
program_loader      Intel HEX / binary file import & export
execution_logger    Step-by-step execution audit trail

The public façade (Virtual8085CPU in v8085_cpu.py) wraps these modules
and keeps the same interface expected by the UI layer.
"""

from .memory             import Memory8085
from .registers          import Registers8085
from .flags              import Flags8085
from .stack              import Stack8085
from .instruction_decoder import InstructionDecoder
from .execution_engine   import ExecutionEngine
from .program_loader     import ProgramLoader
from .execution_logger   import ExecutionLogger

__all__ = [
    "Memory8085",
    "Registers8085",
    "Flags8085",
    "Stack8085",
    "InstructionDecoder",
    "ExecutionEngine",
    "ProgramLoader",
    "ExecutionLogger",
]
