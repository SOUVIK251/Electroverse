"""
i8085.instruction_decoder — 8085 Opcode Reference Table
=========================================================
Provides a complete static lookup table for every valid Intel 8085A opcode.

Each entry contains:
    mnemonic    Human-readable instruction mnemonic  (e.g. "MVI A, d8")
    length      Instruction length in bytes          (1, 2, or 3)
    t_states    T-state count (or range for branches)
    flags       Flags affected: S Z AC P CY (string)
    description One-line description

This module does NOT execute instructions.
Execution is handled by ExecutionEngine.

Usage
-----
    decoder = InstructionDecoder()
    info    = decoder.decode(0x3E)
    # → {'mnemonic': 'MVI A, d8', 'length': 2, 't_states': 7, ...}

    is_valid = decoder.is_valid(opcode)
    all_ops  = decoder.all_opcodes()  # sorted list of (opcode, info) pairs
"""

from typing import Dict, Any, List, Optional, Tuple


class InstructionDecoder:
    """Complete Intel 8085A opcode reference table."""

    # -----------------------------------------------------------------------
    # Full opcode table
    # Format: opcode → (mnemonic, bytes, t_states, flags_affected, description)
    # -----------------------------------------------------------------------
    _TABLE: Dict[int, Tuple] = {
        # ── Data Transfer ──────────────────────────────────────────────────
        0x7F:("MOV A,A",  1,4 ,"none","Copy A to A (no-op)"),
        0x78:("MOV A,B",  1,4 ,"none","Copy B into A"),
        0x79:("MOV A,C",  1,4 ,"none","Copy C into A"),
        0x7A:("MOV A,D",  1,4 ,"none","Copy D into A"),
        0x7B:("MOV A,E",  1,4 ,"none","Copy E into A"),
        0x7C:("MOV A,H",  1,4 ,"none","Copy H into A"),
        0x7D:("MOV A,L",  1,4 ,"none","Copy L into A"),
        0x7E:("MOV A,M",  1,7 ,"none","Copy [HL] into A"),
        0x47:("MOV B,A",  1,4 ,"none","Copy A into B"),
        0x40:("MOV B,B",  1,4 ,"none","Copy B to B (no-op)"),
        0x41:("MOV B,C",  1,4 ,"none","Copy C into B"),
        0x42:("MOV B,D",  1,4 ,"none","Copy D into B"),
        0x43:("MOV B,E",  1,4 ,"none","Copy E into B"),
        0x44:("MOV B,H",  1,4 ,"none","Copy H into B"),
        0x45:("MOV B,L",  1,4 ,"none","Copy L into B"),
        0x46:("MOV B,M",  1,7 ,"none","Copy [HL] into B"),
        0x4F:("MOV C,A",  1,4 ,"none","Copy A into C"),
        0x48:("MOV C,B",  1,4 ,"none","Copy B into C"),
        0x49:("MOV C,C",  1,4 ,"none","no-op"),
        0x4A:("MOV C,D",  1,4 ,"none","Copy D into C"),
        0x4B:("MOV C,E",  1,4 ,"none","Copy E into C"),
        0x4C:("MOV C,H",  1,4 ,"none","Copy H into C"),
        0x4D:("MOV C,L",  1,4 ,"none","Copy L into C"),
        0x4E:("MOV C,M",  1,7 ,"none","Copy [HL] into C"),
        0x57:("MOV D,A",  1,4 ,"none","Copy A into D"),
        0x50:("MOV D,B",  1,4 ,"none","Copy B into D"),
        0x51:("MOV D,C",  1,4 ,"none","Copy C into D"),
        0x52:("MOV D,D",  1,4 ,"none","no-op"),
        0x53:("MOV D,E",  1,4 ,"none","Copy E into D"),
        0x54:("MOV D,H",  1,4 ,"none","Copy H into D"),
        0x55:("MOV D,L",  1,4 ,"none","Copy L into D"),
        0x56:("MOV D,M",  1,7 ,"none","Copy [HL] into D"),
        0x5F:("MOV E,A",  1,4 ,"none","Copy A into E"),
        0x58:("MOV E,B",  1,4 ,"none","Copy B into E"),
        0x59:("MOV E,C",  1,4 ,"none","Copy C into E"),
        0x5A:("MOV E,D",  1,4 ,"none","Copy D into E"),
        0x5B:("MOV E,E",  1,4 ,"none","no-op"),
        0x5C:("MOV E,H",  1,4 ,"none","Copy H into E"),
        0x5D:("MOV E,L",  1,4 ,"none","Copy L into E"),
        0x5E:("MOV E,M",  1,7 ,"none","Copy [HL] into E"),
        0x67:("MOV H,A",  1,4 ,"none","Copy A into H"),
        0x60:("MOV H,B",  1,4 ,"none","Copy B into H"),
        0x61:("MOV H,C",  1,4 ,"none","Copy C into H"),
        0x62:("MOV H,D",  1,4 ,"none","Copy D into H"),
        0x63:("MOV H,E",  1,4 ,"none","Copy E into H"),
        0x64:("MOV H,H",  1,4 ,"none","no-op"),
        0x65:("MOV H,L",  1,4 ,"none","Copy L into H"),
        0x66:("MOV H,M",  1,7 ,"none","Copy [HL] into H"),
        0x6F:("MOV L,A",  1,4 ,"none","Copy A into L"),
        0x68:("MOV L,B",  1,4 ,"none","Copy B into L"),
        0x69:("MOV L,C",  1,4 ,"none","Copy C into L"),
        0x6A:("MOV L,D",  1,4 ,"none","Copy D into L"),
        0x6B:("MOV L,E",  1,4 ,"none","Copy E into L"),
        0x6C:("MOV L,H",  1,4 ,"none","Copy H into L"),
        0x6D:("MOV L,L",  1,4 ,"none","no-op"),
        0x6E:("MOV L,M",  1,7 ,"none","Copy [HL] into L"),
        0x77:("MOV M,A",  1,7 ,"none","Store A to [HL]"),
        0x70:("MOV M,B",  1,7 ,"none","Store B to [HL]"),
        0x71:("MOV M,C",  1,7 ,"none","Store C to [HL]"),
        0x72:("MOV M,D",  1,7 ,"none","Store D to [HL]"),
        0x73:("MOV M,E",  1,7 ,"none","Store E to [HL]"),
        0x74:("MOV M,H",  1,7 ,"none","Store H to [HL]"),
        0x75:("MOV M,L",  1,7 ,"none","Store L to [HL]"),
        # MVI
        0x3E:("MVI A,d8", 2,7 ,"none","Load immediate byte into A"),
        0x06:("MVI B,d8", 2,7 ,"none","Load immediate byte into B"),
        0x0E:("MVI C,d8", 2,7 ,"none","Load immediate byte into C"),
        0x16:("MVI D,d8", 2,7 ,"none","Load immediate byte into D"),
        0x1E:("MVI E,d8", 2,7 ,"none","Load immediate byte into E"),
        0x26:("MVI H,d8", 2,7 ,"none","Load immediate byte into H"),
        0x2E:("MVI L,d8", 2,7 ,"none","Load immediate byte into L"),
        0x36:("MVI M,d8", 2,10,"none","Store immediate byte to [HL]"),
        # LXI
        0x01:("LXI B,d16",3,10,"none","Load 16-bit immediate into BC"),
        0x11:("LXI D,d16",3,10,"none","Load 16-bit immediate into DE"),
        0x21:("LXI H,d16",3,10,"none","Load 16-bit immediate into HL"),
        0x31:("LXI SP,d16",3,10,"none","Load 16-bit immediate into SP"),
        # Direct memory
        0x3A:("LDA a16",  3,13,"none","Load [addr] into A"),
        0x32:("STA a16",  3,13,"none","Store A to [addr]"),
        0x2A:("LHLD a16", 3,16,"none","Load [addr],[addr+1] into L,H"),
        0x22:("SHLD a16", 3,16,"none","Store L,H to [addr],[addr+1]"),
        # Indirect via register pair
        0x0A:("LDAX B",   1,7 ,"none","Load [BC] into A"),
        0x1A:("LDAX D",   1,7 ,"none","Load [DE] into A"),
        0x02:("STAX B",   1,7 ,"none","Store A to [BC]"),
        0x12:("STAX D",   1,7 ,"none","Store A to [DE]"),
        # Exchange
        0xEB:("XCHG",     1,4 ,"none","Swap DE and HL"),
        0xE3:("XTHL",     1,18,"none","Swap [SP],[SP+1] with L,H"),
        0xF9:("SPHL",     1,5 ,"none","Copy HL to SP"),
        0xE9:("PCHL",     1,5 ,"none","Copy HL to PC (indirect jump)"),
        # ── Arithmetic ─────────────────────────────────────────────────────
        0x80:("ADD B",    1,4 ,"SZACP CY","A = A + B"),
        0x81:("ADD C",    1,4 ,"SZACP CY","A = A + C"),
        0x82:("ADD D",    1,4 ,"SZACP CY","A = A + D"),
        0x83:("ADD E",    1,4 ,"SZACP CY","A = A + E"),
        0x84:("ADD H",    1,4 ,"SZACP CY","A = A + H"),
        0x85:("ADD L",    1,4 ,"SZACP CY","A = A + L"),
        0x86:("ADD M",    1,7 ,"SZACP CY","A = A + [HL]"),
        0x87:("ADD A",    1,4 ,"SZACP CY","A = A + A"),
        0x88:("ADC B",    1,4 ,"SZACP CY","A = A + B + CY"),
        0x89:("ADC C",    1,4 ,"SZACP CY","A = A + C + CY"),
        0x8A:("ADC D",    1,4 ,"SZACP CY","A = A + D + CY"),
        0x8B:("ADC E",    1,4 ,"SZACP CY","A = A + E + CY"),
        0x8C:("ADC H",    1,4 ,"SZACP CY","A = A + H + CY"),
        0x8D:("ADC L",    1,4 ,"SZACP CY","A = A + L + CY"),
        0x8E:("ADC M",    1,7 ,"SZACP CY","A = A + [HL] + CY"),
        0x8F:("ADC A",    1,4 ,"SZACP CY","A = A + A + CY"),
        0x90:("SUB B",    1,4 ,"SZACP CY","A = A - B"),
        0x91:("SUB C",    1,4 ,"SZACP CY","A = A - C"),
        0x92:("SUB D",    1,4 ,"SZACP CY","A = A - D"),
        0x93:("SUB E",    1,4 ,"SZACP CY","A = A - E"),
        0x94:("SUB H",    1,4 ,"SZACP CY","A = A - H"),
        0x95:("SUB L",    1,4 ,"SZACP CY","A = A - L"),
        0x96:("SUB M",    1,7 ,"SZACP CY","A = A - [HL]"),
        0x97:("SUB A",    1,4 ,"SZACP CY","A = A - A (clears A)"),
        0x98:("SBB B",    1,4 ,"SZACP CY","A = A - B - CY"),
        0x99:("SBB C",    1,4 ,"SZACP CY","A = A - C - CY"),
        0x9A:("SBB D",    1,4 ,"SZACP CY","A = A - D - CY"),
        0x9B:("SBB E",    1,4 ,"SZACP CY","A = A - E - CY"),
        0x9C:("SBB H",    1,4 ,"SZACP CY","A = A - H - CY"),
        0x9D:("SBB L",    1,4 ,"SZACP CY","A = A - L - CY"),
        0x9E:("SBB M",    1,7 ,"SZACP CY","A = A - [HL] - CY"),
        0x9F:("SBB A",    1,4 ,"SZACP CY","A = A - A - CY"),
        0xC6:("ADI d8",   2,7 ,"SZACP CY","A = A + immediate"),
        0xCE:("ACI d8",   2,7 ,"SZACP CY","A = A + immediate + CY"),
        0xD6:("SUI d8",   2,7 ,"SZACP CY","A = A - immediate"),
        0xDE:("SBI d8",   2,7 ,"SZACP CY","A = A - immediate - CY"),
        # INR / DCR
        0x3C:("INR A",    1,4 ,"SZACP",   "A = A + 1  (CY unaffected)"),
        0x04:("INR B",    1,4 ,"SZACP",   "B = B + 1"),
        0x0C:("INR C",    1,4 ,"SZACP",   "C = C + 1"),
        0x14:("INR D",    1,4 ,"SZACP",   "D = D + 1"),
        0x1C:("INR E",    1,4 ,"SZACP",   "E = E + 1"),
        0x24:("INR H",    1,4 ,"SZACP",   "H = H + 1"),
        0x2C:("INR L",    1,4 ,"SZACP",   "L = L + 1"),
        0x34:("INR M",    1,10,"SZACP",   "[HL] = [HL] + 1"),
        0x3D:("DCR A",    1,4 ,"SZACP",   "A = A - 1  (CY unaffected)"),
        0x05:("DCR B",    1,4 ,"SZACP",   "B = B - 1"),
        0x0D:("DCR C",    1,4 ,"SZACP",   "C = C - 1"),
        0x15:("DCR D",    1,4 ,"SZACP",   "D = D - 1"),
        0x1D:("DCR E",    1,4 ,"SZACP",   "E = E - 1"),
        0x25:("DCR H",    1,4 ,"SZACP",   "H = H - 1"),
        0x2D:("DCR L",    1,4 ,"SZACP",   "L = L - 1"),
        0x35:("DCR M",    1,10,"SZACP",   "[HL] = [HL] - 1"),
        # 16-bit arithmetic
        0x09:("DAD B",    1,10,"CY",      "HL = HL + BC"),
        0x19:("DAD D",    1,10,"CY",      "HL = HL + DE"),
        0x29:("DAD H",    1,10,"CY",      "HL = HL + HL"),
        0x39:("DAD SP",   1,10,"CY",      "HL = HL + SP"),
        0x03:("INX B",    1,5 ,"none",    "BC = BC + 1"),
        0x13:("INX D",    1,5 ,"none",    "DE = DE + 1"),
        0x23:("INX H",    1,5 ,"none",    "HL = HL + 1"),
        0x33:("INX SP",   1,5 ,"none",    "SP = SP + 1"),
        0x0B:("DCX B",    1,5 ,"none",    "BC = BC - 1"),
        0x1B:("DCX D",    1,5 ,"none",    "DE = DE - 1"),
        0x2B:("DCX H",    1,5 ,"none",    "HL = HL - 1"),
        0x3B:("DCX SP",   1,5 ,"none",    "SP = SP - 1"),
        # DAA
        0x27:("DAA",      1,4 ,"SZACP CY","Decimal Adjust Accumulator"),
        # ── Logical ────────────────────────────────────────────────────────
        0xA0:("ANA B",    1,4 ,"SZACP",   "A = A AND B  (CY=0 AC=1)"),
        0xA1:("ANA C",    1,4 ,"SZACP",   "A = A AND C"),
        0xA2:("ANA D",    1,4 ,"SZACP",   "A = A AND D"),
        0xA3:("ANA E",    1,4 ,"SZACP",   "A = A AND E"),
        0xA4:("ANA H",    1,4 ,"SZACP",   "A = A AND H"),
        0xA5:("ANA L",    1,4 ,"SZACP",   "A = A AND L"),
        0xA6:("ANA M",    1,7 ,"SZACP",   "A = A AND [HL]"),
        0xA7:("ANA A",    1,4 ,"SZACP",   "A = A AND A (test)"),
        0xA8:("XRA B",    1,4 ,"SZACP",   "A = A XOR B  (CY=0 AC=0)"),
        0xA9:("XRA C",    1,4 ,"SZACP",   "A = A XOR C"),
        0xAA:("XRA D",    1,4 ,"SZACP",   "A = A XOR D"),
        0xAB:("XRA E",    1,4 ,"SZACP",   "A = A XOR E"),
        0xAC:("XRA H",    1,4 ,"SZACP",   "A = A XOR H"),
        0xAD:("XRA L",    1,4 ,"SZACP",   "A = A XOR L"),
        0xAE:("XRA M",    1,7 ,"SZACP",   "A = A XOR [HL]"),
        0xAF:("XRA A",    1,4 ,"SZACP",   "A = 0 (clear accumulator)"),
        0xB0:("ORA B",    1,4 ,"SZACP",   "A = A OR B  (CY=0 AC=0)"),
        0xB1:("ORA C",    1,4 ,"SZACP",   "A = A OR C"),
        0xB2:("ORA D",    1,4 ,"SZACP",   "A = A OR D"),
        0xB3:("ORA E",    1,4 ,"SZACP",   "A = A OR E"),
        0xB4:("ORA H",    1,4 ,"SZACP",   "A = A OR H"),
        0xB5:("ORA L",    1,4 ,"SZACP",   "A = A OR L"),
        0xB6:("ORA M",    1,7 ,"SZACP",   "A = A OR [HL]"),
        0xB7:("ORA A",    1,4 ,"SZACP",   "A = A OR A (test)"),
        0xB8:("CMP B",    1,4 ,"SZACP CY","Compare A with B"),
        0xB9:("CMP C",    1,4 ,"SZACP CY","Compare A with C"),
        0xBA:("CMP D",    1,4 ,"SZACP CY","Compare A with D"),
        0xBB:("CMP E",    1,4 ,"SZACP CY","Compare A with E"),
        0xBC:("CMP H",    1,4 ,"SZACP CY","Compare A with H"),
        0xBD:("CMP L",    1,4 ,"SZACP CY","Compare A with L"),
        0xBE:("CMP M",    1,7 ,"SZACP CY","Compare A with [HL]"),
        0xBF:("CMP A",    1,4 ,"SZACP CY","Compare A with A (sets Z=1)"),
        0xE6:("ANI d8",   2,7 ,"SZACP",   "A = A AND immediate"),
        0xEE:("XRI d8",   2,7 ,"SZACP",   "A = A XOR immediate"),
        0xF6:("ORI d8",   2,7 ,"SZACP",   "A = A OR immediate"),
        0xFE:("CPI d8",   2,7 ,"SZACP CY","Compare A with immediate"),
        # ── Rotate ─────────────────────────────────────────────────────────
        0x07:("RLC",      1,4 ,"CY",      "Rotate A left; old bit-7 → CY and bit-0"),
        0x0F:("RRC",      1,4 ,"CY",      "Rotate A right; old bit-0 → CY and bit-7"),
        0x17:("RAL",      1,4 ,"CY",      "Rotate A left through CY"),
        0x1F:("RAR",      1,4 ,"CY",      "Rotate A right through CY"),
        # ── Complement / Carry ─────────────────────────────────────────────
        0x2F:("CMA",      1,4 ,"none",    "A = ~A (one's complement)"),
        0x3F:("CMC",      1,4 ,"CY",      "CY = ~CY"),
        0x37:("STC",      1,4 ,"CY",      "CY = 1"),
        # ── Branch ─────────────────────────────────────────────────────────
        0xC3:("JMP a16",  3,10,"none","Unconditional jump"),
        0xC2:("JNZ a16",  3,10,"none","Jump if Z=0"),
        0xCA:("JZ a16",   3,10,"none","Jump if Z=1"),
        0xD2:("JNC a16",  3,10,"none","Jump if CY=0"),
        0xDA:("JC a16",   3,10,"none","Jump if CY=1"),
        0xE2:("JPO a16",  3,10,"none","Jump if P=0 (parity odd)"),
        0xEA:("JPE a16",  3,10,"none","Jump if P=1 (parity even)"),
        0xF2:("JP a16",   3,10,"none","Jump if S=0 (positive)"),
        0xFA:("JM a16",   3,10,"none","Jump if S=1 (minus)"),
        # ── Call / Return ──────────────────────────────────────────────────
        0xCD:("CALL a16", 3,17,"none","Call subroutine at addr"),
        0xC4:("CNZ a16",  3,"11/17","none","Call if Z=0"),
        0xCC:("CZ a16",   3,"11/17","none","Call if Z=1"),
        0xD4:("CNC a16",  3,"11/17","none","Call if CY=0"),
        0xDC:("CC a16",   3,"11/17","none","Call if CY=1"),
        0xE4:("CPO a16",  3,"11/17","none","Call if P=0"),
        0xEC:("CPE a16",  3,"11/17","none","Call if P=1"),
        0xF4:("CP a16",   3,"11/17","none","Call if S=0"),
        0xFC:("CM a16",   3,"11/17","none","Call if S=1"),
        0xC9:("RET",      1,10,"none","Return from subroutine"),
        0xC0:("RNZ",      1,"5/11","none","Return if Z=0"),
        0xC8:("RZ",       1,"5/11","none","Return if Z=1"),
        0xD0:("RNC",      1,"5/11","none","Return if CY=0"),
        0xD8:("RC",       1,"5/11","none","Return if CY=1"),
        0xE0:("RPO",      1,"5/11","none","Return if P=0"),
        0xE8:("RPE",      1,"5/11","none","Return if P=1"),
        0xF0:("RP",       1,"5/11","none","Return if S=0"),
        0xF8:("RM",       1,"5/11","none","Return if S=1"),
        # RST
        0xC7:("RST 0",    1,11,"none","Call 0000H"),
        0xCF:("RST 1",    1,11,"none","Call 0008H"),
        0xD7:("RST 2",    1,11,"none","Call 0010H"),
        0xDF:("RST 3",    1,11,"none","Call 0018H"),
        0xE7:("RST 4",    1,11,"none","Call 0020H"),
        0xEF:("RST 5",    1,11,"none","Call 0028H"),
        0xF7:("RST 6",    1,11,"none","Call 0030H"),
        0xFF:("RST 7",    1,11,"none","Call 0038H"),
        # ── Stack ──────────────────────────────────────────────────────────
        0xC5:("PUSH B",   1,11,"none","Push BC onto stack"),
        0xD5:("PUSH D",   1,11,"none","Push DE onto stack"),
        0xE5:("PUSH H",   1,11,"none","Push HL onto stack"),
        0xF5:("PUSH PSW", 1,11,"none","Push A and flags onto stack"),
        0xC1:("POP B",    1,10,"none","Pop stack into BC"),
        0xD1:("POP D",    1,10,"none","Pop stack into DE"),
        0xE1:("POP H",    1,10,"none","Pop stack into HL"),
        0xF1:("POP PSW",  1,10,"SZACP CY","Pop stack into A and flags"),
        # ── I/O ────────────────────────────────────────────────────────────
        0xD3:("OUT p8",   2,10,"none","Output A to port"),
        0xDB:("IN p8",    2,10,"none","Input from port into A"),
        # ── Interrupt control ──────────────────────────────────────────────
        0xFB:("EI",       1,4 ,"none","Enable interrupts"),
        0xF3:("DI",       1,4 ,"none","Disable interrupts"),
        0x76:("HLT",      1,5 ,"none","Halt processor"),
        0x00:("NOP",      1,4 ,"none","No operation"),
    }

    def __init__(self):
        self._table = self._TABLE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decode(self, opcode: int) -> Optional[Dict[str, Any]]:
        """
        Return the instruction descriptor for *opcode*, or None if invalid.

        Returns
        -------
        dict with keys: mnemonic, length, t_states, flags, description
        """
        entry = self._table.get(opcode & 0xFF)
        if entry is None:
            return None
        mnemonic, length, t_states, flags, description = entry
        return {
            "mnemonic"   : mnemonic,
            "length"     : length,
            "t_states"   : t_states,
            "flags"      : flags,
            "description": description,
            "opcode"     : opcode & 0xFF,
            "opcode_str" : f"{opcode & 0xFF:02X}H",
        }

    def is_valid(self, opcode: int) -> bool:
        """Return True if *opcode* is a known 8085 instruction."""
        return (opcode & 0xFF) in self._table

    def mnemonic(self, opcode: int) -> str:
        """Return just the mnemonic string, or 'ILLEGAL' if unknown."""
        entry = self._table.get(opcode & 0xFF)
        return entry[0] if entry else f"ILLEGAL {opcode:02X}H"

    def all_opcodes(self) -> List[Tuple[int, Dict]]:
        """
        Return all (opcode, info) pairs sorted by opcode.

        Useful for populating an opcode reference table in the UI.
        """
        result = []
        for op, entry in sorted(self._table.items()):
            mnemonic, length, t_states, flags, description = entry
            result.append((op, {
                "mnemonic"   : mnemonic,
                "length"     : length,
                "t_states"   : t_states,
                "flags"      : flags,
                "description": description,
                "opcode"     : op,
                "opcode_str" : f"{op:02X}H",
            }))
        return result

    def search(self, query: str) -> List[Tuple[int, Dict]]:
        """
        Return opcodes whose mnemonic or description contains *query*
        (case-insensitive).
        """
        q = query.lower()
        return [
            (op, info)
            for op, info in self.all_opcodes()
            if q in info["mnemonic"].lower() or q in info["description"].lower()
        ]
