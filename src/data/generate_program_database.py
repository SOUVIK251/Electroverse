import os
import json
from pathlib import Path

target_dir = Path(r"c:\Users\hp\OneDrive\Desktop\FOSSE\src\data\ProgramDatabase")
target_dir.mkdir(parents=True, exist_ok=True)

programs_data = [
    # ── Arithmetic Programs ───────────────────────────────────────────────
    {
        "id": "addition_8bit",
        "program_name": "8-Bit Addition of Two Numbers",
        "category": "Arithmetic Programs",
        "difficulty": "Basic",
        "objective": "Perform 8-bit addition of two hexadecimal numbers stored in memory and store the 8-bit result.",
        "theory": "The 8085 ALU uses the Accumulator (A register) as one operand for arithmetic operations. The ADD instruction adds the specified register or memory content to the Accumulator. If the result exceeds FFH (255), the Carry Flag (CY) is set to 1.",
        "algorithm": [
            "1. Load 8-bit first number from memory location 2050H into Accumulator A.",
            "2. Load 8-bit second number from memory location 2051H into Register B.",
            "3. Add contents of Register B to Accumulator A (ADD B).",
            "4. Store the 8-bit sum from Accumulator A into memory location 2052H (STA 2052H).",
            "5. Terminate program execution (HLT)."
        ],
        "flowchart": "START -> Load A from [2050H] -> Load B from [2051H] -> ADD B -> Store A to [2052H] -> HLT",
        "assembly_code": "LDA 2050H   ; Load 1st byte from 2050H into A\nMOV B, A    ; Copy 1st byte to Register B\nLDA 2051H   ; Load 2nd byte from 2051H into A\nADD B       ; Add B to A (A = A + B)\nSTA 2052H   ; Store sum at 2052H\nHLT         ; Stop execution",
        "machine_code_hex": ["3A", "50", "20", "47", "3A", "51", "20", "80", "32", "52", "20", "76"],
        "opcode_table": [
            {"address": "2000H", "mnemonic": "LDA 2050H", "hex": "3A 50 20", "bytes": 3, "cycles": 13},
            {"address": "2003H", "mnemonic": "MOV B, A", "hex": "47", "bytes": 1, "cycles": 4},
            {"address": "2004H", "mnemonic": "LDA 2051H", "hex": "3A 51 20", "bytes": 3, "cycles": 13},
            {"address": "2007H", "mnemonic": "ADD B", "hex": "80", "bytes": 1, "cycles": 4},
            {"address": "2008H", "mnemonic": "STA 2052H", "hex": "32 52 20", "bytes": 3, "cycles": 13},
            {"address": "200BH", "mnemonic": "HLT", "hex": "76", "bytes": 1, "cycles": 5}
        ],
        "sample_input": {"memory": {"2050H": "05H", "2051H": "03H"}},
        "sample_output": {"memory": {"2052H": "08H"}, "registers": {"A": "08H", "B": "05H"}},
        "register_changes": [
            {"step": 1, "reg": "A", "val": "05H", "desc": "Loaded 1st byte 05H"},
            {"step": 2, "reg": "B", "val": "05H", "desc": "Copied 05H to B"},
            {"step": 3, "reg": "A", "val": "03H", "desc": "Loaded 2nd byte 03H"},
            {"step": 4, "reg": "A", "val": "08H", "desc": "A = 03H + 05H = 08H"}
        ],
        "flag_changes": {"S": 0, "Z": 0, "AC": 0, "P": 1, "CY": 0},
        "memory_changes": {"2052H": "08H"},
        "step_by_step_execution": [
            "Fetch opcode 3A: Load 1st operand from RAM[2050H] -> A = 05H",
            "Fetch opcode 47: Move 05H from Accumulator to Register B",
            "Fetch opcode 3A: Load 2nd operand from RAM[2051H] -> A = 03H",
            "Fetch opcode 80: ADD B -> A = 03H + 05H = 08H",
            "Fetch opcode 32: Store result 08H at RAM[2052H]",
            "Fetch opcode 76: HLT -> Execution Halted"
        ],
        "viva_questions": [
            {"q": "Which register holds the result after an ADD instruction?", "a": "The Accumulator (A register)."},
            {"q": "What happens to the Carry flag if addition exceeds FFH?", "a": "The Carry Flag (CY) is set to 1."}
        ],
        "common_mistakes": ["Forgetting to store the result with STA before HLT.", "Overwriting the first input in Accumulator before saving it to another register."],
        "explanation": "This is the fundamental 8-bit addition program demonstrating how two memory locations are added using the Accumulator and Register B."
    },
    {
        "id": "addition_16bit",
        "program_name": "16-Bit Addition of Two Numbers",
        "category": "Arithmetic Programs",
        "difficulty": "Intermediate",
        "objective": "Perform 16-bit addition of two 16-bit numbers using register pairs BC and DE.",
        "theory": "16-bit numbers require register pairs in 8085 (HL, BC, DE). The DAD Rp instruction adds a 16-bit register pair to HL.",
        "algorithm": [
            "1. Load 16-bit number 1 into HL pair (LHLD 2050H).",
            "2. Load 16-bit number 2 into DE pair (XCHG & LHLD 2052H).",
            "3. Add DE to HL (DAD D).",
            "4. Store 16-bit sum from HL pair to 2054H (SHLD 2054H).",
            "5. HLT."
        ],
        "assembly_code": "LHLD 2050H   ; Load 1st 16-bit number into HL\nXCHG        ; Exchange HL with DE\nLHLD 2052H   ; Load 2nd 16-bit number into HL\nDAD D       ; HL = HL + DE\nSHLD 2054H   ; Store 16-bit sum at 2054H\nHLT         ; Stop execution",
        "machine_code_hex": ["2A", "50", "20", "EB", "2A", "52", "20", "19", "22", "54", "20", "76"],
        "sample_input": {"memory": {"2050H": "12H", "2051H": "34H", "2052H": "10H", "2053H": "20H"}},
        "sample_output": {"memory": {"2054H": "22H", "2055H": "54H"}, "registers": {"HL": "5422H"}},
        "viva_questions": [{"q": "Which 16-bit addition instruction exists in 8085?", "a": "DAD (Double Add) instruction."}]
    },
    {
        "id": "addition_with_carry",
        "program_name": "8-Bit Addition with Carry",
        "category": "Arithmetic Programs",
        "difficulty": "Basic",
        "objective": "Perform 8-bit addition of two numbers and record both 8-bit sum and carry byte.",
        "theory": "When addition results in a sum > 255 (FFH), the Carry Flag (CY) becomes 1. The ADC or JNC instruction tracks the carry byte.",
        "algorithm": [
            "1. Initialize Carry Register C = 0.",
            "2. Load 1st number into A from 2050H.",
            "3. Load 2nd number into B from 2051H.",
            "4. ADD B. If JNC SKIP is taken, skip incrementing C.",
            "5. If Carry set, INR C.",
            "6. Store Sum at 2052H and Carry at 2053H.",
            "7. HLT."
        ],
        "assembly_code": "MVI C, 00H   ; Clear C (Carry)\nLDA 2050H   ; Load 1st byte\nMOV B, A    ; Move to B\nLDA 2051H   ; Load 2nd byte\nADD B       ; Add B to A\nJNC SKIP    ; Jump if no carry\nINR C       ; Increment C if carry\nSKIP: STA 2052H ; Store Sum\nMOV A, C    ; Move Carry to A\nSTA 2053H   ; Store Carry\nHLT",
        "machine_code_hex": ["0E", "00", "3A", "50", "20", "47", "3A", "51", "20", "80", "D2", "0D", "20", "0C", "32", "52", "20", "79", "32", "53", "20", "76"],
        "sample_input": {"memory": {"2050H": "FFH", "2051H": "01H"}},
        "sample_output": {"memory": {"2052H": "00H", "2053H": "01H"}}
    },
    {
        "id": "subtraction_8bit",
        "program_name": "8-Bit Subtraction of Two Numbers",
        "category": "Arithmetic Programs",
        "difficulty": "Basic",
        "objective": "Subtract the contents of RAM[2051H] from RAM[2050H] and store the difference.",
        "theory": "The SUB B instruction subtracts Register B from Accumulator (A = A - B). If A < B, a borrow occurs and Carry Flag (CY) is set to 1.",
        "algorithm": [
            "1. Load minuend from 2050H into Accumulator A.",
            "2. Load subtrahend from 2051H into Register B.",
            "3. Perform SUB B.",
            "4. Store difference at 2052H.",
            "5. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load minuend from 2050H\nMOV B, A    ; Move minuend to B\nLDA 2051H   ; Load subtrahend from 2051H\nSUB B       ; Subtract B from A\nSTA 2052H   ; Store difference at 2052H\nHLT",
        "machine_code_hex": ["3A", "50", "20", "47", "3A", "51", "20", "90", "32", "52", "20", "76"],
        "sample_input": {"memory": {"2050H": "05H", "2051H": "08H"}},
        "sample_output": {"memory": {"2052H": "03H"}}
    },
    {
        "id": "subtraction_with_borrow",
        "program_name": "8-Bit Subtraction with Borrow",
        "category": "Arithmetic Programs",
        "difficulty": "Intermediate",
        "objective": "Perform 8-bit subtraction of two numbers and record borrow state if subtrahend is greater than minuend.",
        "theory": "When subtracting a larger number from a smaller number, 8085 sets CY=1 indicating a borrow. Result is in 2's complement form.",
        "algorithm": [
            "1. Clear Borrow register C = 0.",
            "2. Load minuend into A from 2050H.",
            "3. Load subtrahend into B from 2051H.",
            "4. SUB B. If no borrow (JNC), skip incrementing C.",
            "5. If borrow occurs, INR C and complement result (CMA + ADI 1).",
            "6. Store Difference at 2052H and Borrow at 2053H."
        ],
        "assembly_code": "MVI C, 00H   ; Clear Borrow register C\nLDA 2050H   ; Load minuend\nMOV B, A\nLDA 2051H   ; Load subtrahend\nSUB B       ; A = A - B\nJNC SKIP    ; Jump if no borrow\nINR C       ; Borrow occurred\nCMA         ; 2's complement to get positive magnitude\nADI 01H\nSKIP: STA 2052H ; Store magnitude\nMOV A, C    ;\nSTA 2053H   ; Store borrow flag\nHLT",
        "machine_code_hex": ["0E", "00", "3A", "50", "20", "47", "3A", "51", "20", "90", "D2", "0F", "20", "0C", "2F", "C6", "01", "32", "52", "20", "79", "32", "53", "20", "76"],
        "sample_input": {"memory": {"2050H": "03H", "2051H": "05H"}},
        "sample_output": {"memory": {"2052H": "02H", "2053H": "01H"}}
    },
    {
        "id": "multiplication_8bit",
        "program_name": "8-Bit Multiplication by Repeated Addition",
        "category": "Arithmetic Programs",
        "difficulty": "Intermediate",
        "objective": "Multiply two 8-bit numbers using repeated addition.",
        "theory": "Since 8085 lacks a hardware MUL instruction, multiplication (A x B) is implemented by adding A to itself B times.",
        "algorithm": [
            "1. Load multiplicand into B and multiplier into C.",
            "2. Clear Accumulator (MVI A, 00H).",
            "3. If C=0, jump to store.",
            "4. ADD B to Accumulator.",
            "5. Decrement counter C (DCR C).",
            "6. Loop until C=0.",
            "7. Store 16-bit or 8-bit product."
        ],
        "assembly_code": "LDA 2050H   ; Load multiplicand\nMOV B, A\nLDA 2051H   ; Load multiplier\nMOV C, A\nMVI A, 00H  ; Clear product accumulator\nLOOP: ADD B ; Add multiplicand\nDCR C       ; Decrement counter\nJNZ LOOP    ; Repeat\nSTA 2052H   ; Store product\nHLT",
        "machine_code_hex": ["3A", "50", "20", "47", "3A", "51", "20", "4F", "3E", "00", "80", "0D", "C2", "0A", "20", "32", "52", "20", "76"],
        "sample_input": {"memory": {"2050H": "06H", "2051H": "04H"}},
        "sample_output": {"memory": {"2052H": "18H"}}
    },
    {
        "id": "division_8bit",
        "program_name": "8-Bit Division by Repeated Subtraction",
        "category": "Arithmetic Programs",
        "difficulty": "Intermediate",
        "objective": "Divide dividend by divisor using repeated subtraction and find Quotient and Remainder.",
        "theory": "Division (A / B) is accomplished by subtracting B from A repeatedly until A < B. Count of subtractions = Quotient, remaining A = Remainder.",
        "algorithm": [
            "1. Clear quotient counter C = 0.",
            "2. Load dividend into A from 2050H.",
            "3. Load divisor into B from 2051H.",
            "4. Compare A with B (CMP B). If A < B, jump to END.",
            "5. Subtract B from A (SUB B).",
            "6. Increment quotient counter C (INR C).",
            "7. Repeat step 4.",
            "8. Store Quotient C at 2052H, Remainder A at 2053H."
        ],
        "assembly_code": "MVI C, 00H   ; Clear Quotient counter C\nLDA 2050H   ; Load Dividend\nMOV B, A\nLDA 2051H   ; Load Divisor\nMOV D, A    ; D = Divisor\nMOV A, B    ; A = Dividend\nLOOP: CMP D ; Compare Dividend with Divisor\nJC END      ; If A < D, division complete\nSUB D       ; Subtract Divisor\nINR C       ; Increment Quotient\nJMP LOOP    ; Repeat\nEND: STA 2053H ; Store Remainder\nMOV A, C    ;\nSTA 2052H   ; Store Quotient\nHLT",
        "machine_code_hex": ["0E", "00", "3A", "50", "20", "47", "3A", "51", "20", "57", "78", "BA", "DA", "16", "20", "92", "0C", "C3", "0B", "20", "32", "53", "20", "79", "32", "52", "20", "76"],
        "sample_input": {"memory": {"2050H": "0EH", "2051H": "03H"}},
        "sample_output": {"memory": {"2052H": "04H", "2053H": "02H"}}
    },

    # ── BCD Programs ──────────────────────────────────────────────────────
    {
        "id": "unpack_bcd",
        "program_name": "Unpack Packed BCD Number",
        "category": "BCD Programs",
        "difficulty": "Intermediate",
        "objective": "Unpack an 8-bit packed BCD number into two separate 8-bit unpacked BCD digits.",
        "theory": "A packed BCD byte contains two BCD digits (0-9) in its upper and lower 4 bits (nibbles). Unpacking separates lower nibble AND 0FH and upper nibble (ANI F0H -> RRC 4 times).",
        "algorithm": [
            "1. Load packed BCD byte from RAM[2050H] into Accumulator.",
            "2. Copy byte to B register for second digit.",
            "3. Mask upper nibble (ANI 0FH) to extract lower BCD digit.",
            "4. Store lower digit in RAM[2051H].",
            "5. Get original byte back into Accumulator from B.",
            "6. Mask lower nibble (ANI F0H) and rotate right 4 times (RRC x 4).",
            "7. Store upper digit in RAM[2052H].",
            "8. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load packed BCD (e.g. 45H)\nMOV B, A    ; Keep copy in B\nANI 0FH     ; Extract lower BCD digit (05H)\nSTA 2051H   ; Store lower digit at 2051H\nMOV A, B    ; Get original byte (45H)\nANI F0H     ; Extract upper BCD digit (40H)\nRRC         ; Rotate right 4 times to get 04H\nRRC\nRRC\nRRC\nSTA 2052H   ; Store upper digit at 2052H\nHLT         ; Stop execution",
        "machine_code_hex": ["3A", "50", "20", "47", "E6", "0F", "32", "51", "20", "78", "E6", "F0", "0F", "0F", "0F", "0F", "32", "52", "20", "76"],
        "sample_input": {"memory": {"2050H": "45H"}},
        "sample_output": {"memory": {"2051H": "05H", "2052H": "04H"}, "registers": {"A": "04H", "B": "45H"}},
        "viva_questions": [{"q": "What is the range of a valid BCD digit?", "a": "0 to 9 (0000 to 1001 binary)."}]
    },
    {
        "id": "pack_bcd",
        "program_name": "Pack Two Unpacked BCD Digits",
        "category": "BCD Programs",
        "difficulty": "Intermediate",
        "objective": "Combine two single-digit BCD numbers into a single packed BCD byte.",
        "theory": "The upper BCD digit is shifted left 4 times (RLC x 4) and logically ORed (ORA) with the lower BCD digit.",
        "algorithm": [
            "1. Load upper BCD digit from 2050H (e.g. 04H).",
            "2. Rotate left 4 times (RLC x 4) -> 40H.",
            "3. Store intermediate upper nibble in B.",
            "4. Load lower BCD digit from 2051H (e.g. 05H).",
            "5. Logical OR with B (ORA B) -> 45H.",
            "6. Store packed BCD byte in 2052H.",
            "7. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load upper BCD digit (04H)\nRLC         ; Shift to upper nibble (40H)\nRLC\nRLC\nRLC\nMOV B, A    ; Store in B\nLDA 2051H   ; Load lower BCD digit (05H)\nORA B       ; Combine nibbles (45H)\nSTA 2052H   ; Store packed byte\nHLT",
        "machine_code_hex": ["3A", "50", "20", "07", "07", "07", "07", "47", "3A", "51", "20", "B0", "32", "52", "20", "76"],
        "sample_input": {"memory": {"2050H": "04H", "2051H": "05H"}},
        "sample_output": {"memory": {"2052H": "45H"}, "registers": {"A": "45H", "B": "40H"}}
    },
    {
        "id": "bcd_addition",
        "program_name": "BCD Addition using DAA",
        "category": "BCD Programs",
        "difficulty": "Intermediate",
        "objective": "Perform addition of two BCD numbers and adjust result using DAA instruction.",
        "theory": "The DAA (Decimal Adjust Accumulator) instruction adjusts the 8-bit result in A to two 4-bit BCD digits if lower/upper nibbles exceed 9 or AC/CY flags are set.",
        "algorithm": [
            "1. Load 1st BCD number from 2050H into A.",
            "2. Load 2nd BCD number from 2051H into B.",
            "3. Add B to A (ADD B).",
            "4. Decimal adjust Accumulator (DAA).",
            "5. Store BCD sum at 2052H.",
            "6. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load 1st BCD byte\nMOV B, A    ; Copy to B\nLDA 2051H   ; Load 2nd BCD byte\nADD B       ; Add B to A\nDAA         ; Decimal Adjust Accumulator\nSTA 2052H   ; Store BCD result\nHLT",
        "machine_code_hex": ["3A", "50", "20", "47", "3A", "51", "20", "80", "27", "32", "52", "20", "76"],
        "sample_input": {"memory": {"2050H": "38H", "2051H": "45H"}},
        "sample_output": {"memory": {"2052H": "83H"}}
    },
    {
        "id": "ascii_to_bcd",
        "program_name": "ASCII to BCD Conversion",
        "category": "BCD Programs",
        "difficulty": "Intermediate",
        "objective": "Convert an ASCII character representing a digit ('0' to '9', hex 30H to 39H) to numeric BCD (00H to 09H).",
        "theory": "ASCII digits '0'-'9' have hex representations 30H-39H. Subtracting 30H (SUI 30H) converts ASCII to BCD.",
        "algorithm": [
            "1. Load ASCII byte from 2050H.",
            "2. Subtract 30H (SUI 30H).",
            "3. Store converted BCD digit in 2051H.",
            "4. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load ASCII char\nSUI 30H     ; Subtract 30H to get BCD digit\nSTA 2051H   ; Store BCD byte\nHLT",
        "machine_code_hex": ["3A", "50", "20", "D6", "30", "32", "51", "20", "76"],
        "sample_input": {"memory": {"2050H": "35H"}},
        "sample_output": {"memory": {"2051H": "05H"}}
    },

    # ── Comparison & Sorting ──────────────────────────────────────────────
    {
        "id": "largest_number",
        "program_name": "Find Largest Number in an Array",
        "category": "Comparison & Sorting",
        "difficulty": "Intermediate",
        "objective": "Search an array of N 8-bit numbers stored in memory and find the maximum value.",
        "theory": "The 8085 CMP instruction compares register/memory with A by subtracting internally and updating flags (CY=1 if A < M).",
        "algorithm": [
            "1. Load array length count N into C.",
            "2. Initialize HL pointer to start of array (2050H).",
            "3. Load first element into Accumulator A.",
            "4. Decrement count C and increment pointer HL.",
            "5. Compare M with A (CMP M).",
            "6. If Carry=1 (A >= M), skip updating A.",
            "7. If Carry=0 (A < M), update A = M.",
            "8. Repeat until count C reaches 0.",
            "9. Store maximum value in 2060H and HLT."
        ],
        "assembly_code": "LXI H, 2050H ; HL -> array start\nMOV C, M    ; C = count N\nINX H       ; HL -> 1st element\nMOV A, M    ; A = 1st element\nDCR C       ; Decrement count\nLOOP: INX H ; HL -> next element\nCMP M       ; Compare A with M\nJNC SKIP    ; If A >= M, jump to SKIP\nMOV A, M    ; Update max value A = M\nSKIP: DCR C  ; Decrement counter\nJNZ LOOP    ; Repeat if C != 0\nSTA 2060H   ; Store largest number at 2060H\nHLT         ; Stop",
        "machine_code_hex": ["21", "50", "20", "4E", "23", "7E", "0D", "23", "BE", "D2", "0C", "20", "7E", "0D", "C2", "07", "20", "32", "60", "20", "76"],
        "sample_input": {"memory": {"2050H": "04H", "2051H": "25H", "2052H": "89H", "2053H": "12H", "2054H": "42H"}},
        "sample_output": {"memory": {"2060H": "89H"}, "registers": {"A": "89H"}}
    },
    {
        "id": "smallest_number",
        "program_name": "Find Smallest Number in an Array",
        "category": "Comparison & Sorting",
        "difficulty": "Intermediate",
        "objective": "Scan an array of N numbers in memory and find the minimum value.",
        "theory": "Uses CMP M instruction. If JC (Carry = 1), then Accumulator A < M, so A remains unchanged; otherwise A is updated to M.",
        "algorithm": [
            "1. Load array length N into C.",
            "2. Set HL pointer to 2050H.",
            "3. Read 1st element into A.",
            "4. Decrement count C, advance HL pointer.",
            "5. Compare M with A (CMP M).",
            "6. If Carry=0 (A <= M), skip update.",
            "7. If Carry=1 (A > M), update A = M.",
            "8. Repeat until C=0.",
            "9. Store minimum value at 2060H."
        ],
        "assembly_code": "LXI H, 2050H ; HL -> array start\nMOV C, M    ; C = N\nINX H       ; HL -> 1st element\nMOV A, M    ; A = 1st element\nDCR C       ;\nLOOP: INX H ; HL -> next element\nCMP M       ; Compare A with M\nJC SKIP     ; If A < M, skip update\nMOV A, M    ; Update minimum A = M\nSKIP: DCR C ;\nJNZ LOOP    ; Repeat\nSTA 2060H   ; Store smallest number\nHLT",
        "machine_code_hex": ["21", "50", "20", "4E", "23", "7E", "0D", "23", "BE", "DA", "0C", "20", "7E", "0D", "C2", "07", "20", "32", "60", "20", "76"],
        "sample_input": {"memory": {"2050H": "04H", "2051H": "45H", "2052H": "12H", "2053H": "89H", "2054H": "03H"}},
        "sample_output": {"memory": {"2060H": "03H"}}
    },
    {
        "id": "bubble_sort_ascending",
        "program_name": "Bubble Sort in Ascending Order",
        "category": "Comparison & Sorting",
        "difficulty": "Advanced",
        "objective": "Sort an array of N numbers in memory in ascending order using Bubble Sort algorithm.",
        "theory": "Compares adjacent elements and swaps them if element i > element i+1. Repeats pass N-1 times.",
        "algorithm": [
            "1. Initialize outer loop counter N-1.",
            "2. Initialize inner loop counter N-1 and array pointer HL.",
            "3. Compare current element M with next element [HL+1].",
            "4. If current > next, swap elements.",
            "5. Advance HL pointer, decrement inner counter.",
            "6. Repeat inner loop until done, then repeat outer loop."
        ],
        "assembly_code": "LXI H, 2050H ; HL -> array size N\nMOV C, M    ; C = N\nDCR C       ; Outer loop count N-1\nOUTER: MOV D, C ; D = inner loop count\nLXI H, 2051H ; HL -> 1st element\nINNER: MOV A, M ; A = current element\nINX H       ; HL -> next element\nCMP M       ; Compare current with next\nJC NO_SWAP  ; If A < M, correct order\nMOV B, M    ; Swap M and A\nMOV M, A    ;\nDCX H       ;\nMOV M, B    ;\nINX H       ;\nNO_SWAP: DCR D\nJNZ INNER   ;\nDCR C       ;\nJNZ OUTER   ;\nHLT",
        "machine_code_hex": ["21", "50", "20", "4E", "0D", "51", "21", "51", "20", "7E", "23", "BE", "DA", "16", "20", "46", "77", "2B", "70", "23", "15", "C2", "09", "20", "0D", "C2", "03", "20", "76"],
        "sample_input": {"memory": {"2050H": "04H", "2051H": "42H", "2052H": "05H", "2053H": "12H", "2054H": "01H"}},
        "sample_output": {"memory": {"2051H": "01H", "2052H": "05H", "2053H": "12H", "2054H": "42H"}}
    },

    # ── Data Transfer ─────────────────────────────────────────────────────
    {
        "id": "block_transfer",
        "program_name": "Block Transfer of Data",
        "category": "Data Transfer",
        "difficulty": "Basic",
        "objective": "Copy a block of N data bytes from source memory location to destination memory location.",
        "theory": "Data block migration is achieved by using HL as source pointer and DE as destination pointer in a loop.",
        "algorithm": [
            "1. Initialize HL pair to Source address 2050H.",
            "2. Initialize DE pair to Destination address 2070H.",
            "3. Load block count N into C.",
            "4. Read byte from [HL] into Accumulator.",
            "5. Write byte from Accumulator into [DE].",
            "6. Increment HL, increment DE, decrement C.",
            "7. Loop until C becomes 0.",
            "8. HLT."
        ],
        "assembly_code": "LXI H, 2050H ; Source pointer\nLXI D, 2070H ; Destination pointer\nMVI C, 05H   ; Count N = 5\nLOOP: MOV A, M ; Read byte from source\nSTAX D      ; Store byte at destination\nINX H       ; Increment source ptr\nINX D       ; Increment dest ptr\nDCR C       ; Decrement count\nJNZ LOOP    ; Repeat\nHLT",
        "machine_code_hex": ["21", "50", "20", "11", "70", "20", "0E", "05", "7E", "12", "23", "13", "0D", "C2", "08", "20", "76"],
        "sample_input": {"memory": {"2050H": "A1H", "2051H": "B2H", "2052H": "C3H"}},
        "sample_output": {"memory": {"2070H": "A1H", "2071H": "B2H", "2072H": "C3H"}}
    },
    {
        "id": "block_exchange",
        "program_name": "Block Exchange of Data",
        "category": "Data Transfer",
        "difficulty": "Intermediate",
        "objective": "Exchange contents of two blocks of memory of size N.",
        "theory": "Uses HL as block 1 pointer and DE as block 2 pointer, using B as temporary storage byte.",
        "algorithm": [
            "1. LXI H, 2050H and LXI D, 2070H.",
            "2. Load count N into C.",
            "3. Read [HL] into A, read [DE] into B.",
            "4. Store A at [DE], store B at [HL].",
            "5. Increment pointers, decrement C, loop."
        ],
        "assembly_code": "LXI H, 2050H ; Block 1 ptr\nLXI D, 2070H ; Block 2 ptr\nMVI C, 03H   ; Count = 3\nLOOP: LDAX D ; A = [DE]\nMOV B, M    ; B = [HL]\nSTAX D      ; [DE] = B\nMOV M, A    ; [HL] = A\nINX H       ;\nINX D       ;\nDCR C       ;\nJNZ LOOP    ;\nHLT",
        "machine_code_hex": ["21", "50", "20", "11", "70", "20", "0E", "03", "1A", "46", "12", "77", "23", "13", "0D", "C2", "08", "20", "76"],
        "sample_input": {"memory": {"2050H": "11H", "2070H": "AAH"}},
        "sample_output": {"memory": {"2050H": "AAH", "2070H": "11H"}}
    },

    # ── Mathematical Programs ─────────────────────────────────────────────
    {
        "id": "factorial",
        "program_name": "Factorial of an 8-Bit Number",
        "category": "Mathematical Programs",
        "difficulty": "Advanced",
        "objective": "Compute the factorial of a small number (N <= 5) using repeated addition multiplication.",
        "theory": "Factorial N! = N * (N-1) * (N-2) ... * 1. Multiplication in 8085 is implemented using nested loops of repeated addition.",
        "algorithm": [
            "1. Load input N from RAM[2050H]. If N=0 or 1, result is 1.",
            "2. Initialize product in accumulator.",
            "3. Use nested loops: outer loop decrements multiplier, inner loop performs repeated addition.",
            "4. Store result at RAM[2051H]."
        ],
        "assembly_code": "LDA 2050H   ; Load N\nCPI 01H     ; Check if N <= 1\nJC ONE\nMOV C, A    ; C = N\nDCR C       ; Counter = N-1\nOUTER: MOV B, A ; B = current product\nMOV D, C    ; D = inner loop count\nDCR D\nINNER: ADD B; Add product\nDCR D\nJNZ INNER\nDCR C\nJNZ OUTER\nJMP STORE\nONE: MVI A, 01H\nSTORE: STA 2051H\nHLT",
        "machine_code_hex": ["3A", "50", "20", "FE", "01", "DA", "1A", "20", "4F", "0D", "47", "51", "15", "80", "15", "C2", "0D", "20", "0D", "C2", "0A", "20", "C3", "1D", "20", "3E", "01", "32", "51", "20", "76"],
        "sample_input": {"memory": {"2050H": "04H"}},
        "sample_output": {"memory": {"2051H": "18H"}}
    },
    {
        "id": "fibonacci",
        "program_name": "Generate Fibonacci Series",
        "category": "Mathematical Programs",
        "difficulty": "Intermediate",
        "objective": "Generate first N terms of the Fibonacci sequence in memory.",
        "theory": "Fibonacci sequence: F(0)=0, F(1)=1, F(n) = F(n-1) + F(n-2).",
        "algorithm": [
            "1. Set HL pointer to 2050H.",
            "2. Read term count N into C.",
            "3. Store 1st term 00H and 2nd term 01H.",
            "4. Add previous two terms (A = B + D) to get next term.",
            "5. Store term in memory, shift terms, repeat until C=0."
        ],
        "assembly_code": "LXI H, 2050H ; HL -> memory start\nMVI B, 00H   ; 1st term = 0\nMVI D, 01H   ; 2nd term = 1\nMOV M, B    ; Store 1st term\nINX H\nMOV M, D    ; Store 2nd term\nINX H\nMVI C, 05H   ; Remaining terms N-2 = 5\nLOOP: MOV A, B ; A = term 1\nADD D       ; A = term 1 + term 2\nMOV M, A    ; Store next term\nMOV B, D    ; Shift term 2 -> term 1\nMOV D, A    ; Shift next term -> term 2\nINX H\nDCR C\nJNZ LOOP\nHLT",
        "machine_code_hex": ["21", "50", "20", "06", "00", "16", "01", "70", "23", "72", "23", "0E", "05", "78", "82", "77", "42", "57", "23", "0D", "C2", "0D", "20", "76"],
        "sample_input": {"memory": {"2050H": "07H"}},
        "sample_output": {"memory": {"2050H": "00H", "2051H": "01H", "2052H": "01H", "2053H": "02H", "2054H": "03H", "2055H": "05H", "2056H": "08H"}}
    },
    {
        "id": "square_root",
        "program_name": "Find Square Root of a Perfect Square",
        "category": "Mathematical Programs",
        "difficulty": "Intermediate",
        "objective": "Find integer square root of a perfect square 8-bit number by subtracting consecutive odd numbers (1, 3, 5, ...).",
        "theory": "The sum of the first N odd numbers equals N^2 (1 + 3 + 5 + ... = N^2). Subtracting odd numbers from X until 0 gives N subtractions = sqrt(X).",
        "algorithm": [
            "1. Load number X from 2050H into A.",
            "2. Initialize odd subtractor B = 1 and root counter C = 0.",
            "3. Subtract B from A (SUB B).",
            "4. Increment root counter C (INR C).",
            "5. If A = 0, jump to STORE.",
            "6. Add 2 to B (INR B twice).",
            "7. Repeat step 3.",
            "8. Store square root C at 2051H."
        ],
        "assembly_code": "LDA 2050H   ; Load number\nMVI B, 01H  ; Initial odd number = 1\nMVI C, 00H  ; Root count = 0\nLOOP: SUB B ; Subtract odd number\nINR C       ; Increment root count\nJZ STORE    ; If A == 0, done\nINR B       ; B += 2 (next odd number)\nINR B\nJMP LOOP\nSTORE: MOV A, C\nSTA 2051H   ; Store square root\nHLT",
        "machine_code_hex": ["3A", "50", "20", "06", "01", "0E", "00", "90", "0C", "CA", "13", "20", "04", "04", "C3", "07", "20", "79", "32", "51", "20", "76"],
        "sample_input": {"memory": {"2050H": "10H"}},
        "sample_output": {"memory": {"2051H": "04H"}}
    },

    # ── Searching & Operations ────────────────────────────────────────────
    {
        "id": "even_odd_check",
        "program_name": "Check Even or Odd Number",
        "category": "Searching & Operations",
        "difficulty": "Basic",
        "objective": "Determine whether an 8-bit number is even or odd by checking LSB bit 0.",
        "theory": "An even number has Bit 0 = 0, while an odd number has Bit 0 = 1. Masking with 01H (ANI 01H) isolates Bit 0.",
        "algorithm": [
            "1. Load number from 2050H into Accumulator.",
            "2. Perform AND operation with 01H (ANI 01H).",
            "3. If Zero Flag Z=1 (result 00H), number is EVEN -> store 00H at 2051H.",
            "4. If Zero Flag Z=0 (result 01H), number is ODD -> store 01H at 2051H.",
            "5. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load number\nANI 01H     ; Mask bit 0\nJZ EVEN     ; Jump if result is 0 (even)\nMVI A, 01H  ; Odd indicator (01H)\nJMP STORE\nEVEN: MVI A, 00H ; Even indicator (00H)\nSTORE: STA 2051H ; Store result\nHLT",
        "machine_code_hex": ["3A", "50", "20", "E6", "01", "CA", "10", "20", "3E", "01", "C3", "12", "20", "3E", "00", "32", "51", "20", "76"],
        "sample_input": {"memory": {"2050H": "07H"}},
        "sample_output": {"memory": {"2051H": "01H"}}
    },
    {
        "id": "ones_complement",
        "program_name": "1's Complement of an 8-Bit Number",
        "category": "Searching & Operations",
        "difficulty": "Basic",
        "objective": "Find the 1's complement (bitwise NOT) of an 8-bit number.",
        "theory": "The CMA (Complement Accumulator) instruction inverts all 8 bits of the Accumulator (0 becomes 1, 1 becomes 0).",
        "algorithm": [
            "1. Load number from 2050H into Accumulator A.",
            "2. Complement Accumulator (CMA).",
            "3. Store result in 2051H.",
            "4. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load number from 2050H\nCMA         ; Complement Accumulator (1's complement)\nSTA 2051H   ; Store 1's complement at 2051H\nHLT",
        "machine_code_hex": ["3A", "50", "20", "2F", "32", "51", "20", "76"],
        "sample_input": {"memory": {"2050H": "55H"}},
        "sample_output": {"memory": {"2051H": "AAH"}}
    },
    {
        "id": "twos_complement",
        "program_name": "2's Complement of an 8-Bit Number",
        "category": "Searching & Operations",
        "difficulty": "Basic",
        "objective": "Find the 2's complement of an 8-bit number by taking 1's complement and adding 1.",
        "theory": "2's complement = 1's complement + 1. Used to represent negative numbers in binary signed arithmetic.",
        "algorithm": [
            "1. Load number from 2050H into Accumulator A.",
            "2. Complement Accumulator (CMA).",
            "3. Increment Accumulator (INR A or ADI 01H).",
            "4. Store 2's complement result in 2051H.",
            "5. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load number\nCMA         ; 1's complement\nADI 01H     ; Add 1 to get 2's complement\nSTA 2051H   ; Store result\nHLT",
        "machine_code_hex": ["3A", "50", "20", "2F", "C6", "01", "32", "51", "20", "76"],
        "sample_input": {"memory": {"2050H": "05H"}},
        "sample_output": {"memory": {"2051H": "FBH"}}
    },

    # ── Bit Manipulation ──────────────────────────────────────────────────
    {
        "id": "rotate_left",
        "program_name": "Rotate Left Accumulator (RLC / RAL)",
        "category": "Bit Manipulation",
        "difficulty": "Basic",
        "objective": "Demonstrate bit rotation to the left using RLC and RAL instructions.",
        "theory": "RLC rotates bits left with Bit 7 going into both Bit 0 and CY flag. RAL rotates bits left through the Carry flag.",
        "algorithm": [
            "1. Load byte from 2050H into A.",
            "2. Perform RLC (Rotate Left Circular).",
            "3. Store rotated byte at 2051H.",
            "4. HLT."
        ],
        "assembly_code": "LDA 2050H   ; Load number\nRLC         ; Rotate left circular\nSTA 2051H   ; Store result\nHLT",
        "machine_code_hex": ["3A", "50", "20", "07", "32", "51", "20", "76"],
        "sample_input": {"memory": {"2050H": "81H"}},
        "sample_output": {"memory": {"2051H": "03H"}}
    },

    # ── Delay & Stack ─────────────────────────────────────────────────────
    {
        "id": "stack_push_pop",
        "program_name": "Stack Operations PUSH and POP",
        "category": "Stack Programs",
        "difficulty": "Basic",
        "objective": "Demonstrate LIFO (Last-In-First-Out) stack operations using PUSH and POP.",
        "theory": "PUSH decrements SP by 2 and stores a 16-bit register pair on stack. POP loads 16-bit pair from stack and increments SP by 2.",
        "algorithm": [
            "1. Initialize Stack Pointer (LXI SP, 2090H).",
            "2. Load BC pair with 1234H.",
            "3. PUSH B onto stack (SP becomes 208EH).",
            "4. Clear BC pair (LXI B, 0000H).",
            "5. POP B from stack (BC restored to 1234H).",
            "6. HLT."
        ],
        "assembly_code": "LXI SP, 2090H ; Set SP\nLXI B, 1234H  ; BC = 1234H\nPUSH B        ; Push BC onto stack\nLXI B, 0000H  ; Clear BC\nPOP B         ; Pop stack into BC\nHLT",
        "machine_code_hex": ["31", "90", "20", "01", "34", "12", "C5", "01", "00", "00", "C1", "76"],
        "sample_input": {},
        "sample_output": {"registers": {"BC": "1234H", "SP": "2090H"}}
    },
    {
        "id": "software_delay",
        "program_name": "Software Delay Loop",
        "category": "Delay Programs",
        "difficulty": "Basic",
        "objective": "Generate precise software timing delay using nested register counting loops.",
        "theory": "Delay is generated by loading a 16-bit or 8-bit count into register(s) and decrementing until zero.",
        "algorithm": [
            "1. Load 16-bit delay count into BC pair (LXI B, 0500H).",
            "2. Decrement BC pair (DCX B).",
            "3. Check if BC is zero (MOV A, B -> ORA C -> JNZ LOOP).",
            "4. Loop until BC=0.",
            "5. HLT."
        ],
        "assembly_code": "LXI B, 0500H ; Load delay count\nLOOP: DCX B  ; Decrement BC pair\nMOV A, B    ; Copy B to A\nORA C       ; OR with C\nJNZ LOOP    ; Repeat if BC != 0\nHLT",
        "machine_code_hex": ["01", "00", "05", "0B", "78", "B1", "C2", "03", "20", "76"],
        "sample_input": {},
        "sample_output": {"registers": {"BC": "0000H"}}
    }
]

for prog in programs_data:
    fn = target_dir / f"{prog['id']}.json"
    with open(fn, "w", encoding="utf-8") as fh:
        json.dump(prog, fh, indent=4)
    print(f"Wrote {fn}")

print("Comprehensive Dataset Generation Complete!")
