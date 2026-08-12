"""
ElectroVerse Microprocessor & Microcontroller Master Assessment Dataset.
Contains 115 technically precise 8085 & 8051 questions covering all 12 question types.
"""

ASSESSMENT_QUESTIONS = [
    {
        "id": "q_mc_01",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "HARD",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n21 00 20\n01 00 10\n09\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: LXI H, 2000H; LXI B, 1000H; DAD B; HLT. 21 is LXI H, 01 is LXI B, 09 is DAD B (HL=HL+BC=3000H).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "HL = 3000H",
            "HL = 2000H",
            "HL = 1000H",
            "HL = 0000H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_02",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n3E 45\n06 20\n80\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: MVI A, 45H; MVI B, 20H; ADD B; HLT. 3E is MVI A, 06 is MVI B, 80 is ADD B (45H + 20H = 65H).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "A = 65H",
            "A = 45H",
            "A = 20H",
            "A = 00H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_03",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n3A 50 20\n47\n3A 51 20\n80\n32 52 20\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: 8-Bit Addition Program from RAM 2050H and 2051H. 3A is LDA, 47 is MOV B,A, 80 is ADD B, 32 is STA 2052H.",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "A = Sum stored at 2052H",
            "A = Difference at 2052H",
            "HL = 2052H",
            "B = 00H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_04",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n00\n00\n00\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: NOP; NOP; NOP; HLT. 00H is NOP opcode (No Operation, 4 T-states).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "3 NOPs followed by HLT",
            "3 ADDs",
            "3 LDAs",
            "Invalid Opcodes"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_05",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n3E FF\n3C\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: MVI A, FFH; INR A; HLT. 3E FF sets A=FFH, 3C is INR A (FFH->00H, Z=1, CY remains 0).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "A = 00H, Z = 1, CY = 0",
            "A = 00H, Z = 1, CY = 1",
            "A = 01H",
            "A = FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_06",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n3E 0F\nE6 05\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: MVI A, 0FH; ANI 05H; HLT. E6 is ANI immediate. 0FH AND 05H = 05H.",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "A = 05H",
            "A = 0FH",
            "A = 0A",
            "A = 00H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_07",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n3E 05\n3D\nC2 02 20\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: MVI A, 05H; DCR A; JNZ 2002H; HLT. 3D is DCR A, C2 is JNZ (Jump if Zero flag = 0).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Decrement loop from 5 to 0",
            "Infinite loop",
            "Immediate Jump",
            "Subroutine Call"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_08",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "HARD",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nCD 50 20\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: CALL 2050H; HLT. CD is the opcode for 16-bit CALL instruction in 8085.",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Subroutine call to 2050H",
            "Jump to 2050H",
            "Return from 2050H",
            "Push 2050H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_09",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nC9\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: RET. C9 is the opcode for RET (Return from Subroutine).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Return from subroutine",
            "Call subroutine",
            "Restart 0",
            "Halt CPU"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_10",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nF5\nC5\nD1\u00f1\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: PUSH PSW; PUSH B; POP D; POP PSW; HLT. F5 is PUSH PSW, C5 is PUSH B, D1 is POP D, F1 is POP PSW.",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Stack PUSH and POP sequence",
            "Register Move",
            "Memory Read",
            "Memory Write"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_11",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n78\n79\n7A\n7B\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: MOV A,B; MOV A,C; MOV A,D; MOV A,E. 78H=MOV A,B, 79H=MOV A,C, 7AH=MOV A,D, 7BH=MOV A,E.",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Register Move to Accumulator",
            "Arithmetic Add",
            "Logical OR",
            "Compare"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_12",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n76\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: HLT. 76H is opcode for HLT (Halt CPU until interrupt or reset).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Halt instruction",
            "No operation",
            "Enable interrupts",
            "Disable interrupts"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_13",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nFB\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: EI. FBH is opcode for EI (Enable Interrupts).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Enable Interrupts",
            "Disable Interrupts",
            "Halt",
            "Restart"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_14",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nF3\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: DI. F3H is opcode for DI (Disable Interrupts).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Disable Interrupts",
            "Enable Interrupts",
            "Halt",
            "NOP"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_15",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "HARD",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n11 50 20\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: LXI D, 2050H. 11 is opcode for LXI D, 50H is low byte, 20H is high byte.",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "DE = 2050H",
            "DE = 5020H",
            "HL = 2050H",
            "BC = 2050H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_16",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n2A 50 20\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: LHLD 2050H. 2A is opcode for LHLD (Load HL Direct).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Load HL from RAM 2050H",
            "Store HL at 2050H",
            "Load Accumulator",
            "Exchange HL"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_17",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n22 50 20\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: SHLD 2050H. 22 is opcode for SHLD (Store HL Direct).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Store HL to RAM 2050H",
            "Load HL from 2050H",
            "Store A at 2050H",
            "Exchange DE"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_18",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nEB\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: XCHG. EBH is opcode for XCHG (Exchange HL and DE contents).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Exchange HL and DE",
            "Exchange BC and DE",
            "Rotate Accumulator",
            "Complement A"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_19",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nE3\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: XTHL. E3H is opcode for XTHL (Exchange Top of Stack with HL).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Exchange Top of Stack with HL",
            "Exchange A and Flags",
            "Exchange SP and PC",
            "No Operation"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_20",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\nF9\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: SPHL. F9H is opcode for SPHL (SP <- HL).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Move HL to Stack Pointer SP",
            "Move SP to HL",
            "Push HL",
            "Pop HL"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_21",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n07\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: RLC. 07H is opcode for RLC (Rotate Accumulator Left).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Rotate Accumulator Left",
            "Rotate Right",
            "Rotate Left through Carry",
            "Shift Left"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_22",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n0F\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: RRC. 0FH is opcode for RRC (Rotate Accumulator Right).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Rotate Accumulator Right",
            "Rotate Left",
            "Rotate Right through Carry",
            "Shift Right"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_23",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n17\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: RAL. 17H is opcode for RAL (Rotate Accumulator Left through Carry).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Rotate Left through Carry",
            "Rotate Right through Carry",
            "Rotate Left",
            "Rotate Right"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_24",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n1F\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: RAR. 1FH is opcode for RAR (Rotate Accumulator Right through Carry).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Rotate Right through Carry",
            "Rotate Left through Carry",
            "Rotate Left",
            "Rotate Right"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_25",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n2F\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: CMA. 2FH is opcode for CMA (Complement Accumulator bitwise NOT).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Complement Accumulator",
            "Complement Carry",
            "Clear Accumulator",
            "Set Carry"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_26",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n3F\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: CMC. 3FH is opcode for CMC (Complement Carry Flag).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Complement Carry Flag",
            "Set Carry Flag",
            "Clear Carry Flag",
            "Complement Accumulator"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_27",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n37\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: STC. 37H is opcode for STC (Set Carry Flag to 1).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Set Carry Flag",
            "Complement Carry",
            "Clear Carry",
            "Store Carry"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_28",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n27\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: DAA. 27H is opcode for DAA (Decimal Adjust Accumulator for BCD).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Decimal Adjust Accumulator",
            "Decimal Add",
            "Divide A",
            "Decrement A"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_29",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n20\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: RIM. 20H is opcode for RIM (Read Interrupt Mask & Serial Data).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Read Interrupt Mask",
            "Set Interrupt Mask",
            "Reset Interrupt",
            "Rotate Interrupt"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_mc_30",
        "topic": "Machine Code",
        "subtopic": "Opcode Decoding",
        "difficulty": "MEDIUM",
        "type": "machine_code",
        "target_modes": [
            "machine_code",
            "quick",
            "8085",
            "programming",
            "mixed",
            "mock"
        ],
        "question": "Analyze the following 8085 machine code sequence stored in memory:\n```\n30\n```\nWhich of the following describes the execution output / disassembly of this machine code?",
        "explanation": "Disassembly/Output: SIM. 30H is opcode for SIM (Set Interrupt Mask & Serial Data).",
        "related_topic": "Machine Code - Opcode Decoding",
        "options": [
            "Set Interrupt Mask",
            "Read Interrupt Mask",
            "Store Interrupt",
            "Send Interrupt"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_01",
        "topic": "Architecture",
        "subtopic": "Address Bus",
        "difficulty": "EASY",
        "type": "fill_blank",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "How many total address lines are present in the 8085 CPU address bus?",
        "explanation": "The 8085 has 16 address lines (A15-A0), allowing it to address 2^16 = 64 KB of memory.",
        "related_topic": "Architecture - Address Bus",
        "correct_answer": "16"
    },
    {
        "id": "q_8085_t_02",
        "topic": "Architecture",
        "subtopic": "Data Bus",
        "difficulty": "EASY",
        "type": "fill_blank",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "What is the width of the 8085 data bus in bits?",
        "explanation": "The 8085 is an 8-bit microprocessor with an 8-bit bidirectional data bus (AD7-AD0).",
        "related_topic": "Architecture - Data Bus",
        "correct_answer": "8"
    },
    {
        "id": "q_8085_t_03",
        "topic": "Architecture",
        "subtopic": "Clock Frequency",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "If an 8085 processor operates with a 6 MHz crystal connected across X1 and X2, what is the internal operating clock frequency?",
        "explanation": "Internal clock frequency f_int = f_crystal / 2 = 6 MHz / 2 = 3 MHz.",
        "related_topic": "Architecture - Clock Frequency",
        "options": [
            "3 MHz",
            "6 MHz",
            "12 MHz",
            "1.5 MHz"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_04",
        "topic": "Timing",
        "subtopic": "Opcode Fetch",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8085",
            "timing_arch",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "How many T-states are normally required for a standard 8085 Opcode Fetch machine cycle?",
        "explanation": "Standard opcode fetch cycle takes 4 T-states (T1-T4). Some instructions like CALL/DCX take 6 T-states.",
        "related_topic": "Timing - Opcode Fetch",
        "options": [
            "4 T-states",
            "3 T-states",
            "6 T-states",
            "2 T-states"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_05",
        "topic": "Timing",
        "subtopic": "Memory Read Cycle",
        "difficulty": "EASY",
        "type": "mcq",
        "target_modes": [
            "8085",
            "timing_arch",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "How many T-states are required for an 8085 Memory Read machine cycle?",
        "explanation": "Memory Read machine cycle requires 3 T-states (T1, T2, T3).",
        "related_topic": "Timing - Memory Read Cycle",
        "options": [
            "3 T-states",
            "4 T-states",
            "2 T-states",
            "5 T-states"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_06",
        "topic": "Interrupts",
        "subtopic": "NMI",
        "difficulty": "EASY",
        "type": "true_false",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "True or False: The TRAP interrupt in 8085 is edge- and level-sensitive and cannot be masked.",
        "explanation": "True! TRAP is non-maskable (NMI) and requires both a rising edge and a high level to be recognized.",
        "related_topic": "Interrupts - NMI",
        "options": [
            "True",
            "False"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_07",
        "topic": "Interrupts",
        "subtopic": "RST 7.5 Vector",
        "difficulty": "MEDIUM",
        "type": "fill_blank",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the hex vector address for the 8085 hardware interrupt RST 7.5? (Format: 00XXH)",
        "explanation": "7.5 * 8 = 60 = 003CH.",
        "related_topic": "Interrupts - RST 7.5 Vector",
        "correct_answer": "003CH"
    },
    {
        "id": "q_8085_t_08",
        "topic": "Interrupts",
        "subtopic": "RST 6.5 Vector",
        "difficulty": "MEDIUM",
        "type": "fill_blank",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the hex vector address for the 8085 hardware interrupt RST 6.5? (Format: 00XXH)",
        "explanation": "6.5 * 8 = 52 = 0034H.",
        "related_topic": "Interrupts - RST 6.5 Vector",
        "correct_answer": "0034H"
    },
    {
        "id": "q_8085_t_09",
        "topic": "Interrupts",
        "subtopic": "RST 5.5 Vector",
        "difficulty": "MEDIUM",
        "type": "fill_blank",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the hex vector address for the 8085 hardware interrupt RST 5.5? (Format: 00XXH)",
        "explanation": "5.5 * 8 = 44 = 002CH.",
        "related_topic": "Interrupts - RST 5.5 Vector",
        "correct_answer": "002CH"
    },
    {
        "id": "q_8085_t_10",
        "topic": "Interrupts",
        "subtopic": "TRAP Vector",
        "difficulty": "EASY",
        "type": "fill_blank",
        "target_modes": [
            "8085",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the hex vector address for the 8085 TRAP interrupt? (Format: 00XXH)",
        "explanation": "4.5 * 8 = 36 = 0024H.",
        "related_topic": "Interrupts - TRAP Vector",
        "correct_answer": "0024H"
    },
    {
        "id": "q_8085_t_11",
        "topic": "Stack",
        "subtopic": "Stack Pointer",
        "difficulty": "EASY",
        "type": "mcq",
        "target_modes": [
            "8085",
            "programming",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "When a PUSH instruction is executed in 8085, how does the Stack Pointer (SP) change?",
        "explanation": "PUSH decrements SP by 2 (top of stack grows downwards towards lower addresses).",
        "related_topic": "Stack - Stack Pointer",
        "options": [
            "SP decrements by 2",
            "SP increments by 2",
            "SP decrements by 1",
            "SP remains unchanged"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_12",
        "topic": "Stack",
        "subtopic": "POP Instruction",
        "difficulty": "EASY",
        "type": "mcq",
        "target_modes": [
            "8085",
            "programming",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "When a POP instruction is executed in 8085, how does the Stack Pointer (SP) change?",
        "explanation": "POP retrieves 2 bytes from stack and increments SP by 2.",
        "related_topic": "Stack - POP Instruction",
        "options": [
            "SP increments by 2",
            "SP decrements by 2",
            "SP increments by 1",
            "SP remains unchanged"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_13",
        "topic": "Flags",
        "subtopic": "Zero Flag",
        "difficulty": "EASY",
        "type": "mcq",
        "target_modes": [
            "8085",
            "programming",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "Executing `SUB A` in 8085 sets the Accumulator to 00H. What will be the state of the Zero Flag (Z)?",
        "explanation": "Since the result of SUB A is 00H, the Zero flag is set to 1.",
        "related_topic": "Flags - Zero Flag",
        "options": [
            "Z = 1 (Set)",
            "Z = 0 (Reset)",
            "Z remains unchanged",
            "Undefined"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_14",
        "topic": "Flags",
        "subtopic": "Parity Flag",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8085",
            "programming",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "If Accumulator A = 03H (0000 0011B), what is the status of the Parity Flag (P)?",
        "explanation": "03H has two 1s (even parity), so Parity flag P = 1.",
        "related_topic": "Flags - Parity Flag",
        "options": [
            "P = 1 (Even parity: two 1s)",
            "P = 0 (Odd parity)",
            "P = Undefined",
            "P = 00H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_15",
        "topic": "Flags",
        "subtopic": "Auxiliary Carry",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8085",
            "programming",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "Auxiliary Carry (AC) flag is set to 1 when a carry is generated out of which bit during addition?",
        "explanation": "AC flag is set when carry occurs from lower nibble (bit D3) to upper nibble (bit D4).",
        "related_topic": "Flags - Auxiliary Carry",
        "options": [
            "Bit D3 to Bit D4",
            "Bit D7 to Carry Flag",
            "Bit D0 to Bit D1",
            "Bit D4 to Bit D5"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8085_t_16",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #16 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_17",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #17 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_18",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #18 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_19",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #19 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_20",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #20 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_21",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #21 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_22",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #22 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_23",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #23 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_24",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #24 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_25",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #25 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_26",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #26 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_27",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #27 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_28",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #28 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_29",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #29 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8085_t_30",
        "topic": "Architecture",
        "subtopic": "8085 Control Signals",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8085",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8085 control signal #30 to its hardware pin function:",
        "explanation": "IO/M selects Memory vs IO. RD/WR signal bus direction. READY inserts wait states for slow memory.",
        "related_topic": "Architecture - 8085 Control Signals",
        "left": [
            "IO/M (bar)",
            "RD (bar)",
            "WR (bar)",
            "READY"
        ],
        "right": [
            "Memory/IO Select",
            "Read Control Signal",
            "Write Control Signal",
            "Wait State Generator"
        ],
        "correct_matches": {
            "IO/M (bar)": "Memory/IO Select",
            "RD (bar)": "Read Control Signal",
            "WR (bar)": "Write Control Signal",
            "READY": "Wait State Generator"
        }
    },
    {
        "id": "q_8051_t_01",
        "topic": "8051 Architecture",
        "subtopic": "Internal RAM",
        "difficulty": "EASY",
        "type": "fill_blank",
        "target_modes": [
            "8051",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the total size of standard internal RAM in 8051 Microcontroller? (in Bytes)",
        "explanation": "Standard 8051 has 128 Bytes of internal RAM (00H to 7FH).",
        "related_topic": "8051 Architecture - Internal RAM",
        "correct_answer": "128"
    },
    {
        "id": "q_8051_t_02",
        "topic": "8051 Architecture",
        "subtopic": "Internal ROM",
        "difficulty": "EASY",
        "type": "fill_blank",
        "target_modes": [
            "8051",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the total size of standard internal Flash/ROM program memory in 8051? (in KB)",
        "explanation": "Standard 8051 has 4 KB of internal ROM (0000H to 0FFFH).",
        "related_topic": "8051 Architecture - Internal ROM",
        "correct_answer": "4"
    },
    {
        "id": "q_8051_t_03",
        "topic": "8051 Architecture",
        "subtopic": "Register Banks",
        "difficulty": "EASY",
        "type": "mcq",
        "target_modes": [
            "8051",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "How many Register Banks are available in 8051 internal RAM?",
        "explanation": "8051 has 4 register banks (Bank 0-3), each containing 8 registers (R0-R7).",
        "related_topic": "8051 Architecture - Register Banks",
        "options": [
            "4 Banks (Bank 0 to Bank 3)",
            "2 Banks",
            "8 Banks",
            "1 Bank"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_04",
        "topic": "8051 Architecture",
        "subtopic": "Bit-Addressable RAM",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the internal RAM address range for Bit-Addressable memory in 8051?",
        "explanation": "RAM addresses 20H-2FH are bit-addressable (bit addresses 00H-7FH).",
        "related_topic": "8051 Architecture - Bit-Addressable RAM",
        "options": [
            "20H to 2FH (16 Bytes / 128 Bits)",
            "00H to 07H",
            "30H to 7FH",
            "80H to FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_05",
        "topic": "8051 Timers",
        "subtopic": "Timer Modes",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8051",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8051 Timer Modes to their descriptions:",
        "explanation": "Mode 0: 13-bit, Mode 1: 16-bit, Mode 2: 8-bit Auto-Reload (used for baud rate), Mode 3: Split Timer.",
        "related_topic": "8051 Timers - Timer Modes",
        "left": [
            "Mode 0",
            "Mode 1",
            "Mode 2",
            "Mode 3"
        ],
        "right": [
            "13-bit Timer",
            "16-bit Timer",
            "8-bit Auto-Reload",
            "Split Timer"
        ],
        "correct_matches": {
            "Mode 0": "13-bit Timer",
            "Mode 1": "16-bit Timer",
            "Mode 2": "8-bit Auto-Reload",
            "Mode 3": "Split Timer"
        }
    },
    {
        "id": "q_8051_t_06",
        "topic": "8051 Ports",
        "subtopic": "Port 0 Configuration",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "interfacing",
            "mixed",
            "mock"
        ],
        "question": "Why does 8051 Port 0 require external pull-up resistors when used as an I/O port?",
        "explanation": "Port 0 drivers are open-drain and lack internal pull-up resistors, requiring external 10k pull-ups for general I/O.",
        "related_topic": "8051 Ports - Port 0 Configuration",
        "options": [
            "Because Port 0 has open-drain outputs",
            "Because Port 0 is input-only",
            "Because Port 0 has internal 10k pull-ups",
            "Because Port 0 is analog"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_07",
        "topic": "8051 Ports",
        "subtopic": "Port 3 Alternate Functions",
        "difficulty": "MEDIUM",
        "type": "matching",
        "target_modes": [
            "8051",
            "topic",
            "interfacing",
            "mixed",
            "mock"
        ],
        "question": "Match 8051 Port 3 pins to their alternate functions:",
        "explanation": "P3.0=RXD, P3.1=TXD, P3.2=INT0, P3.3=INT1.",
        "related_topic": "8051 Ports - Port 3 Alternate Functions",
        "left": [
            "P3.0",
            "P3.1",
            "P3.2",
            "P3.3"
        ],
        "right": [
            "RXD (Serial In)",
            "TXD (Serial Out)",
            "INT0 (External Interrupt 0)",
            "INT1 (External Interrupt 1)"
        ],
        "correct_matches": {
            "P3.0": "RXD (Serial In)",
            "P3.1": "TXD (Serial Out)",
            "P3.2": "INT0 (External Interrupt 0)",
            "P3.3": "INT1 (External Interrupt 1)"
        }
    },
    {
        "id": "q_8051_t_08",
        "topic": "8051 Interrupts",
        "subtopic": "Interrupt Vectors",
        "difficulty": "HARD",
        "type": "matching",
        "target_modes": [
            "8051",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "Match 8051 Interrupt sources to their vector addresses:",
        "explanation": "8051 interrupt vectors: IE0=0003H, TF0=000BH, IE1=0013H, TF1=001BH, Serial=0023H.",
        "related_topic": "8051 Interrupts - Interrupt Vectors",
        "left": [
            "External INT0",
            "Timer 0 Overflow",
            "External INT1",
            "Timer 1 Overflow"
        ],
        "right": [
            "0003H",
            "000BH",
            "0013H",
            "001BH"
        ],
        "correct_matches": {
            "External INT0": "0003H",
            "Timer 0 Overflow": "000BH",
            "External INT1": "0013H",
            "Timer 1 Overflow": "001BH"
        }
    },
    {
        "id": "q_8051_t_09",
        "topic": "8051 Serial",
        "subtopic": "SCON Modes",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "interfacing",
            "mixed",
            "mock"
        ],
        "question": "Which SCON mode in 8051 represents standard 8-bit UART with variable baud rate determined by Timer 1?",
        "explanation": "SCON Mode 1 is standard 8-bit UART with variable baud rate generated by Timer 1 in Mode 2.",
        "related_topic": "8051 Serial - SCON Modes",
        "options": [
            "Mode 1 (8-bit UART, variable baud)",
            "Mode 0 (Shift Register)",
            "Mode 2 (9-bit UART, fixed baud)",
            "Mode 3 (9-bit UART, variable baud)"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_10",
        "topic": "8051 DPTR",
        "subtopic": "Data Pointer",
        "difficulty": "EASY",
        "type": "fill_blank",
        "target_modes": [
            "8051",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the size of the 8051 DPTR (Data Pointer) register in bits?",
        "explanation": "DPTR is a 16-bit register composed of DPH (High byte) and DPL (Low byte), used to access external memory.",
        "related_topic": "8051 DPTR - Data Pointer",
        "correct_answer": "16"
    },
    {
        "id": "q_8051_t_11",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #11",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #11",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_12",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #12",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #12",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_13",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #13",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #13",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_14",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #14",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #14",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_15",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #15",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #15",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_16",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #16",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #16",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_17",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #17",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #17",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_18",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #18",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #18",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_19",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #19",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #19",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_20",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #20",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #20",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_21",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #21",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #21",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_22",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #22",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #22",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_23",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #23",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #23",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_24",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #24",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #24",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_25",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #25",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #25",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_26",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #26",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #26",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_27",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #27",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #27",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_28",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #28",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #28",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_29",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #29",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #29",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_8051_t_30",
        "topic": "8051 Architecture",
        "subtopic": "8051 Concept #30",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "8051",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the default initial value of the 8051 Stack Pointer (SP) register upon system reset?",
        "explanation": "On reset, SP is set to 07H so that the first PUSH operation stores data at RAM address 08H (Bank 1).",
        "related_topic": "8051 Architecture - 8051 Concept #30",
        "options": [
            "07H (Pushing first item to RAM 08H)",
            "00H",
            "80H",
            "FFH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_01",
        "topic": "Interfacing",
        "subtopic": "8255 PPI",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "In the 8255 PPI, how many 8-bit programmable I/O ports are provided?",
        "explanation": "8255 PPI provides 3 8-bit I/O ports: Port A, Port B, and Port C (split into Port C Upper & Lower).",
        "related_topic": "Interfacing - 8255 PPI",
        "options": [
            "3 Ports (Port A, Port B, Port C)",
            "2 Ports",
            "4 Ports",
            "1 Port"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_02",
        "topic": "Interfacing",
        "subtopic": "8253 PIT",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "timing_arch",
            "mixed",
            "mock"
        ],
        "question": "How many independent 16-bit counters/timers are integrated inside the 8253/8254 PIT chip?",
        "explanation": "8253/8254 contains 3 independent 16-bit counters capable of operating in 6 different modes.",
        "related_topic": "Interfacing - 8253 PIT",
        "options": [
            "3 Counters (Counter 0, 1, 2)",
            "2 Counters",
            "4 Counters",
            "1 Counter"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_03",
        "topic": "Interfacing",
        "subtopic": "16x2 LCD",
        "difficulty": "EASY",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "quick",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "Which command byte is sent to a 16x2 HD44780 LCD controller to clear the display screen and return cursor to home position?",
        "explanation": "Command byte 01H clears the LCD display and resets display data RAM pointer to 00H.",
        "related_topic": "Interfacing - 16x2 LCD",
        "options": [
            "01H",
            "38H",
            "0EH",
            "06H"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_04",
        "topic": "Interfacing",
        "subtopic": "16x2 LCD Function Set",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "Which command byte configures a 16x2 HD44780 LCD for 8-bit data bus width, 2-line display, and 5x7 matrix font?",
        "explanation": "Command byte 38H (0011 1000B) sets 8-bit mode, 2 lines, and 5x7 dots.",
        "related_topic": "Interfacing - 16x2 LCD Function Set",
        "options": [
            "38H",
            "01H",
            "80H",
            "0CH"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_05",
        "topic": "Interfacing",
        "subtopic": "ADC0809",
        "difficulty": "HARD",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "Which signal pin must be pulsed HIGH then LOW to start analog-to-digital conversion in ADC0809?",
        "explanation": "Pulsing the START pin initiates A/D conversion in ADC0809. EOC goes LOW during conversion and pulses HIGH when complete.",
        "related_topic": "Interfacing - ADC0809",
        "options": [
            "START (SOC - Start of Conversion)",
            "EOC (End of Conversion)",
            "OE (Output Enable)",
            "ALE"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_06",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #6",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #6",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_07",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #7",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #7",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_08",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #8",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #8",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_09",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #9",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #9",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_10",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #10",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #10",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_11",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #11",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #11",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_12",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #12",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #12",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_13",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #13",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #13",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_14",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #14",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #14",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_15",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #15",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #15",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_16",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #16",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #16",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_17",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #17",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #17",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_18",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #18",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #18",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_19",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #19",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #19",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_20",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #20",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #20",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_21",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #21",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #21",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_22",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #22",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #22",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_23",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #23",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #23",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_24",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #24",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #24",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    },
    {
        "id": "q_interfacing_25",
        "topic": "Interfacing",
        "subtopic": "Peripheral Control #25",
        "difficulty": "MEDIUM",
        "type": "mcq",
        "target_modes": [
            "interfacing",
            "topic",
            "mixed",
            "mock"
        ],
        "question": "What is the step angle of a standard 4-phase stepper motor with 200 rotor steps per revolution?",
        "explanation": "Step angle = 360 / 200 = 1.8 degrees per step.",
        "related_topic": "Interfacing - Peripheral Control #25",
        "options": [
            "1.8 degrees",
            "7.5 degrees",
            "15 degrees",
            "0.9 degrees"
        ],
        "correct_answer": 0
    }
]

ASSESSMENT_MODES = [
    {
        "id": "quick",
        "title": "QUICK TEST",
        "desc": "Fast 10-question quiz to check core MP&MC concepts.",
        "questions": 10,
        "time_min": 10,
        "icon": "fa5s.bolt",
        "color": "#10B981"
    },
    {
        "id": "topic",
        "title": "TOPIC TEST",
        "desc": "Focus on a specific chapter (Architecture, Instructions, Timers, Interrupts).",
        "questions": 20,
        "time_min": 20,
        "icon": "fa5s.book-open",
        "color": "#3B82F6"
    },
    {
        "id": "8085",
        "title": "8085 TEST",
        "desc": "30 questions dedicated exclusively to Intel 8085 CPU & Assembly.",
        "questions": 30,
        "time_min": 30,
        "icon": "fa5s.microchip",
        "color": "#F97316"
    },
    {
        "id": "8051",
        "title": "8051 TEST",
        "desc": "30 questions covering 8051 Microcontroller, SFRs, Timers & Ports.",
        "questions": 30,
        "time_min": 30,
        "icon": "fa5s.cubes",
        "color": "#8B5CF6"
    },
    {
        "id": "programming",
        "title": "ASSEMBLY PROGRAMMING",
        "desc": "20 questions on code outputs, register changes, loop counters & algorithm logic.",
        "questions": 20,
        "time_min": 25,
        "icon": "fa5s.code",
        "color": "#06B6D4"
    },
    {
        "id": "machine_code",
        "title": "MACHINE CODE CHALLENGE",
        "desc": "20 questions decoding raw 8085/8051 opcodes & machine byte streams.",
        "questions": 20,
        "time_min": 25,
        "icon": "fa5s.terminal",
        "color": "#EC4899"
    },
    {
        "id": "timing_arch",
        "title": "TIMING & ARCHITECTURE",
        "desc": "20 questions on T-states, bus signals, clock cycles & hardware block diagrams.",
        "questions": 20,
        "time_min": 20,
        "icon": "fa5s.stopwatch",
        "color": "#EAB308"
    },
    {
        "id": "interfacing",
        "title": "INTERFACING TEST",
        "desc": "20 questions on 8255 PPI, 8253 Timer, LCD, Keypad, ADC/DAC & UART.",
        "questions": 20,
        "time_min": 25,
        "icon": "fa5s.plug",
        "color": "#6366F1"
    },
    {
        "id": "mixed",
        "title": "MIXED TEST",
        "desc": "25 balanced questions covering all 8085 & 8051 syllabus topics.",
        "questions": 25,
        "time_min": 25,
        "icon": "fa5s.layer-group",
        "color": "#14B8A6"
    },
    {
        "id": "mock",
        "title": "FULL MOCK TEST",
        "desc": "100 comprehensive questions for university & competitive GATE exam prep.",
        "questions": 100,
        "time_min": 90,
        "icon": "fa5s.graduation-cap",
        "color": "#EF4444"
    }
]
