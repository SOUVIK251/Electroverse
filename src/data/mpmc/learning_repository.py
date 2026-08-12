"""
ElectroVerse Microprocessor & Microcontroller Master Learning Repository.
Contains structured engineering data for all major categories.
"""

LEARNING_CATEGORIES = [   {   'color': '#3B82F6',
        'icon': 'fa5s.microchip',
        'id': 'cat_1',
        'title': '1. MICROPROCESSOR FUNDAMENTALS',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------+\n'
                                     '|                       MICROPROCESSOR SYSTEM                           |\n'
                                     '|  +--------------------+     +-------------------+     +------------+  |\n'
                                     '|  |  CONTROL UNIT (CU) |<--->| REGISTER ARRAY    |<--->|  ALU       |  |\n'
                                     '|  +--------------------+     +-------------------+     +------------+  |\n'
                                     '|            ^                         ^                      ^         |\n'
                                     '|            +-------------------------+----------------------+         |\n'
                                     '|                                 | System Bus                          |\n'
                                     '+---------------------------------|-------------------------------------+\n'
                                     '                                  v\n'
                                     '+------------------+    +------------------+    +-----------------------+\n'
                                     '|  PROGRAM MEMORY  |    |   DATA MEMORY    |    |  INPUT / OUTPUT (I/O) |\n'
                                     '+------------------+    +------------------+    +-----------------------+\n',
                          'example': 'Executing MVI A, 45H:\n'
                                     '- Fetch byte 3EH (MVI A opcode) from memory.\n'
                                     '- Decode byte 3EH -> identifies 2-byte instruction loading immediate data into '
                                     'Accumulator.\n'
                                     '- Fetch byte 45H (data) from memory location PC+1.\n'
                                     '- Store 45H into Accumulator A.',
                          'how_it_works': '1. Fetch: Reads an instruction byte from memory pointed to by the Program '
                                          'Counter (PC).\n'
                                          '2. Decode: Decodes the opcode byte in the Instruction Register (IR) into '
                                          'control signals.\n'
                                          '3. Execute: Performs the required operation (e.g. ADD, SUB, MOV) using the '
                                          'ALU and updates registers or memory.',
                          'id': 'mp_intro',
                          'important_points': [   'Silicon IC chip containing millions of transistors forming ALU, '
                                                  'Registers, and Control Unit.',
                                                  'Operates strictly on binary machine code (0s and 1s).',
                                                  'Clock-driven: Execution speed is synchronized by an external '
                                                  'crystal oscillator clock signal.',
                                                  'Communicates with memory and peripherals using Address, Data, and '
                                                  'Control buses.'],
                          'practical_application': 'Forms the central processing core of industrial controllers, PC '
                                                   'mainboards, robotics control units, and automotive ECUs.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'The Control Unit (CU) decodes instructions and generates '
                                                     'synchronization timing signals across all buses.',
                                      'options': [   'Arithmetic Logic Unit (ALU)',
                                                     'Control Unit (CU)',
                                                     'Register Array',
                                                     'Program Counter'],
                                      'question': 'Which component of the microprocessor is responsible for generating '
                                                  'timing and control signals?'},
                          'register_state': {   'after': 'A = 45H, PC = 2002H, Flags = Unchanged',
                                                'before': 'A = 00H, PC = 2000H',
                                                'operation': 'MVI A, 45H (Opcode: 3E 45)'},
                          'summary': 'A multipurpose, programmable, clock-driven, semiconductor IC that fetches binary '
                                     'instructions from memory, decodes them, and executes arithmetic/logical '
                                     'operations.',
                          'title': 'What is a Microprocessor?',
                          'try_it': 'Switch to Interactive Simulation to test MVI A, 45H on the Virtual 8085 Trainer '
                                    'Kit.'},
                      {   'diagram': '\n'
                                     'MICROPROCESSOR (CPU Only)             MICROCONTROLLER (System-on-Chip)\n'
                                     '+-----------------------+             +---------------------------------------+\n'
                                     '|  +-----+  +---------+ |  External   |  +-----+  +---------+  +------------+ |\n'
                                     '|  | ALU |  | REGISTERS| |  Buses      |  | ALU |  | REGISTERS| | RAM (128B) | '
                                     '|\n'
                                     '|  +-----+  +---------+ | ========>   |  +-----+  +---------+  +------------+ |\n'
                                     '|  +------------------+ | Memory &    |  +------------------+  +------------+ |\n'
                                     '|  |   CONTROL UNIT   | | Peripherals |  |   CONTROL UNIT   |  | ROM (4KB)  | |\n'
                                     '|  +------------------+ | (RAM, ROM,  |  +------------------+  +------------+ |\n'
                                     '+-----------------------+  I/O, Timer)|  | TIMERS | I/O PORTS | UART | ADC | |\n'
                                     '                                      '
                                     '+---------------------------------------+\n',
                          'example': 'Microprocessor Application: PC Workstation running Linux.\n'
                                     'Microcontroller Application: Microwave Oven control board, Washing machine '
                                     'controller, Smart TV remote.',
                          'how_it_works': 'Microprocessors use external bus lines to access memory chips soldered on a '
                                          'PCB mainboard. Microcontrollers route signals on-chip, delivering '
                                          'sub-microsecond response times for direct sensor reading.',
                          'id': 'mp_vs_mcu',
                          'important_points': [   'Microprocessor: CPU-only IC (e.g. 8085, 8086, Core i7). Requires '
                                                  'external RAM, ROM, I/O ports, and timers.',
                                                  'Microcontroller: Single-chip computer (e.g. 8051, AVR, PIC, STM32) '
                                                  'with built-in RAM, Flash ROM, I/O ports, and peripherals.',
                                                  'Cost & Compactness: Microcontrollers are cheaper and require far '
                                                  'smaller PCB footprints for embedded devices.',
                                                  'Flexibility: Microprocessors allow scalable RAM/ROM expansion up to '
                                                  'Gigabytes.'],
                          'practical_application': 'Use Microprocessors for intensive data processing (image '
                                                   'processing, OS execution); use Microcontrollers for dedicated '
                                                   'embedded control (sensor monitoring, motor control).',
                          'quiz': {   'correct': 1,
                                      'explanation': 'Microcontrollers integrate memory, timer, and I/O hardware '
                                                     'directly on the same silicon die.',
                                      'options': [   'Unlimited RAM expansion',
                                                     'Integrated RAM, ROM, and I/O ports on a single chip',
                                                     'Higher clock frequency (>4 GHz)',
                                                     'Support for desktop Operating Systems'],
                                      'question': 'Which of the following is an advantage of a Microcontroller over a '
                                                  'Microprocessor?'},
                          'register_state': {   'after': 'MPU: High Computing Power  |  MCU: Ultra-low Power & Direct '
                                                         'Pin I/O',
                                                'before': 'MPU: External Bus Fetch  |  MCU: On-chip Flash Fetch',
                                                'operation': 'System Architecture Comparison'},
                          'summary': 'Comparing general-purpose CPU chips requiring external peripherals with '
                                     'single-chip microcontrollers containing integrated RAM, ROM, Timers, and I/O '
                                     'ports.',
                          'title': 'Microprocessor vs Microcontroller',
                          'try_it': 'Compare the 8085 Trainer Kit (Microprocessor) with the 8051 Microcontroller Hub '
                                    'in ElectroVerse.'},
                      {   'diagram': '\n'
                                     '+--------------------+   16-Bit Address Bus (Unidirectional A15-A0)   '
                                     '+--------------------+\n'
                                     '|                    '
                                     '|================================================>|                    |\n'
                                     '|                    |    8-Bit Data Bus (Bidirectional D7-D0)        |   MEMORY '
                                     '/ I/O     |\n'
                                     '|   MICROPROCESSOR   |<===============================================>|     '
                                     'DEVICES        |\n'
                                     '|       (8085)       |   Control Bus (RD#, WR#, IO/M#, ALE, etc.)    | (RAM, '
                                     'ROM, 8255)   |\n'
                                     '|                    '
                                     '|------------------------------------------------>|                    |\n'
                                     '+--------------------+                                                 '
                                     '+--------------------+\n',
                          'example': 'Address lines = 16 -> 2^16 = 64 KB.\n'
                                     'Address lines = 20 (8086) -> 2^20 = 1 MB.\n'
                                     'Address lines = 32 (80386) -> 2^32 = 4 GB.',
                          'how_it_works': 'To read memory at address 2050H:\n'
                                          '1. MPU places 2050H on Address Bus.\n'
                                          '2. MPU asserts IO/M# = 0 (Memory) and RD# = 0 (Read active).\n'
                                          '3. Memory chip places data byte stored at 2050H onto the Data Bus.\n'
                                          '4. MPU latches the Data Bus byte into Accumulator.',
                          'id': 'cpu_buses',
                          'important_points': [   'Address Bus (A15-A0): Unidirectional 16 lines. Determines memory '
                                                  'capacity = 2^16 = 65,536 locations (64 KB).',
                                                  'Data Bus (D7-D0): Bidirectional 8 lines. Transfers data bytes '
                                                  'to/from memory and I/O.',
                                                  'Control Bus: Carries synchronization signals like RD# (Read), WR# '
                                                  '(Write), IO/M#, ALE, RESET, HOLD.'],
                          'practical_application': 'Bus width determines system bandwidth and addressable memory '
                                                   'capacity in all computer architectures.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'The CPU outputs addresses to select memory/IO locations, but '
                                                     'data must flow both OUT (writing) and IN (reading).',
                                      'options': [   'Data flows in two directions (read/write), whereas CPU always '
                                                     'outputs addresses',
                                                     'Address bus carries more current',
                                                     'Control unit limits address flow',
                                                     'Data bus operates at double clock speed'],
                                      'question': 'Why is the Data Bus bidirectional while the Address Bus is '
                                                  'unidirectional?'},
                          'register_state': {   'after': 'Data Bus = 45H, Latching into Accumulator A',
                                                'before': 'Address Bus = 2050H, Control: RD# = 1',
                                                'operation': 'Memory Read Cycle (RD# = 0)'},
                          'summary': 'Understanding the 3 fundamental parallel bus highways: Address Bus '
                                     '(unidirectional), Data Bus (bidirectional), and Control Bus.',
                          'title': 'Buses & System Architecture (Address, Data, Control)',
                          'try_it': 'Inspect bus signal LEDs (ALE, RD#, WR#, IO/M#) during step-by-step execution in '
                                    'the 8085 Trainer.'}]},
    {   'color': '#F97316',
        'icon': 'fa5s.cubes',
        'id': 'cat_2',
        'title': '2. INTEL 8085 ARCHITECTURE',
        'topics': [   {   'diagram': '\n'
                                     '+-------------------------------------------------------------------------------------------------+\n'
                                     '|                                 INTEL 8085 INTERNAL '
                                     'ARCHITECTURE                                |\n'
                                     '|                                                                                                 '
                                     '|\n'
                                     '|  +--------------------+  +-------------------+  +-------------------+  '
                                     '+---------------------+  |\n'
                                     '|  | ACCUMULATOR (A-8)  |  | TEMP REG (W,Z-8)  |  | FLAG REG (F-8)    |  | '
                                     'INSTRUCTION REG (IR)|  |\n'
                                     '|  +---------+----------+  +---------+---------+  +---------+---------+  '
                                     '+----------+----------+  |\n'
                                     '|            |                       |                      '
                                     '|                       |             |\n'
                                     '|            +-----------+-----------+                      '
                                     'v                       v             |\n'
                                     '|                        v                               +-----+           '
                                     '+------------------+   |\n'
                                     '|                 +--------------+                       | ALU |           | '
                                     'INSTR DECODER    |   |\n'
                                     '|                 | 8-BIT ALU    |<----------------------|     |           | & '
                                     'TIMING CONTROL |   |\n'
                                     '|                 +--------------+                       +-----+           '
                                     '+------------------+   |\n'
                                     '|                        '
                                     '|                                                          |             |\n'
                                     '|                        '
                                     'v                                                          v             |\n'
                                     '|                 '
                                     '+-----------------------------------------------------------------------+       '
                                     '|\n'
                                     '|                 | INTERNAL 8-BIT DATA '
                                     'BUS                                               |       |\n'
                                     '|                 '
                                     '+-----------------------------------------------------------------------+       '
                                     '|\n'
                                     '|                        |                  |                  |                 '
                                     '|                |\n'
                                     '|                        v                  v                  v                 '
                                     'v                |\n'
                                     '|                  +-----------+      +-----------+      +-----------+     '
                                     '+-----------+          |\n'
                                     '|                  | B (8) C(8)|      | D (8) E(8)|      | H (8) L(8)|     | SP '
                                     '(16)   |          |\n'
                                     '|                  +-----------+      +-----------+      +-----------+     '
                                     '+-----------+          |\n'
                                     '|                                                                          | PC '
                                     '(16)   |          |\n'
                                     '|                                                                          '
                                     '+-----------+          |\n'
                                     '|                                                                          | '
                                     'ADDR BUFF |          |\n'
                                     '|                                                                          '
                                     '+-----------+          |\n'
                                     '+-------------------------------------------------------------------------------------------------+\n',
                          'example': 'During T1 state of Opcode Fetch: 8085 outputs upper address A15-A8 on address '
                                     'lines, lower address A7-A0 on AD7-AD0, and pulses ALE high to latch lower '
                                     'address into external 74LS373 latch.',
                          'how_it_works': 'The Instruction Register (IR) holds fetched opcodes. The Instruction '
                                          'Decoder sends decoded state signals to the Timing & Control unit, which '
                                          'sequences state machine T-states (T1-T6) to trigger internal register '
                                          'transfers.',
                          'id': '8085_block_diagram',
                          'important_points': [   '8-bit NMOS CPU operating on +5V DC supply.',
                                                  'Built-in clock generator: Requires 6.144 MHz crystal to produce '
                                                  '3.072 MHz internal CPU clock.',
                                                  '16-bit Address Bus (A15-A8 high byte, AD7-AD0 low byte '
                                                  'multiplexed).',
                                                  '5 Hardware Interrupts: TRAP (non-maskable), RST 7.5, RST 6.5, RST '
                                                  '5.5, INTR.'],
                          'practical_application': 'Demultiplexing AD7-AD0 saves 8 IC pins, allowing the 8085 to fit '
                                                   'into a compact 40-pin DIP package.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'ALE pulses high during the T1 state to latch the low-order '
                                                     'address byte from multiplexed AD7-AD0 lines.',
                                      'options': [   'To signal an interrupt request',
                                                     'To demultiplex the combined Address/Data bus AD7-AD0',
                                                     'To select internal register bank',
                                                     'To reset the Program Counter'],
                                      'question': 'What is the primary purpose of the ALE (Address Latch Enable) '
                                                  'signal in 8085?'},
                          'register_state': {   'after': 'Latch Output = A7-A0, AD7-AD0 freed for Data Bus',
                                                'before': 'ALE = 1, AD7-AD0 = Low Address Byte',
                                                'operation': 'ALE Falling Edge Latch'},
                          'summary': 'Detailed analysis of the 8085 functional blocks: ALU, Accumulator, Register '
                                     'Array, Timing & Control, Interrupts, and Serial I/O.',
                          'title': '8085 Internal Block Diagram & Functional Units',
                          'try_it': 'Click on the 8085 Block Diagram in the Reference section to view interactive pin '
                                    'signals.'},
                      {   'diagram': '\n'
                                     '                       +--\\/--+\n'
                                     '              X1  1  |        | 40  VCC (+5V)\n'
                                     '              X2  2  |        | 39  HOLD\n'
                                     '        RESET OUT 3  |        | 38  HLDA\n'
                                     '             SOD  4  |        | 37  CLK (OUT)\n'
                                     '             SID  5  |        | 36  RESET IN#\n'
                                     '            TRAP  6  |        | 35  READY\n'
                                     '         RST 7.5  7  |  8085  | 34  IO/M#\n'
                                     '         RST 6.5  8  |   CPU  | 33  S1\n'
                                     '         RST 5.5  9  |        | 32  RD#\n'
                                     '            INTR 10  |        | 31  WR#\n'
                                     '            INTA 11  |        | 30  ALE\n'
                                     '             AD0 12  |        | 29  S0\n'
                                     '             AD1 13  |        | 28  A15\n'
                                     '             AD2 14  |        | 27  A14\n'
                                     '             AD3 15  |        | 26  A13\n'
                                     '             AD4 16  |        | 25  A12\n'
                                     '             AD5 17  |        | 24  A11\n'
                                     '             AD6 18  |        | 23  A10\n'
                                     '             AD7 19  |        | 22  A9\n'
                                     '             GND 20  |        | 21  A8\n'
                                     '                     +--------+\n',
                          'example': 'During LDA 2050H execution:\n'
                                     '1. Opcode Fetch: IO/M#=0, RD#=0, S1=1, S0=1\n'
                                     '2. Read Address Bytes: IO/M#=0, RD#=0, S1=1, S0=0\n'
                                     '3. Read Data at 2050H: IO/M#=0, RD#=0, S1=1, S0=0',
                          'how_it_works': 'Control Status decoding table:\n'
                                          '- IO/M#=0, S1=1, S0=1 -> Opcode Fetch\n'
                                          '- IO/M#=0, S1=1, S0=0 -> Memory Read\n'
                                          '- IO/M#=0, S1=0, S0=1 -> Memory Write\n'
                                          '- IO/M#=1, S1=1, S0=0 -> I/O Read\n'
                                          '- IO/M#=1, S1=0, S0=1 -> I/O Write',
                          'id': '8085_pin_diagram',
                          'important_points': [   'Pins 1 & 2 (X1, X2): Crystal oscillator inputs.',
                                                  'Pin 30 (ALE): Address Latch Enable pulse.',
                                                  'Pins 31 & 32 (WR#, RD#): Active-low Write and Read control lines.',
                                                  'Pin 34 (IO/M#): High for I/O operations, Low for Memory operations.',
                                                  'Pins 38 & 39 (HLDA, HOLD): Direct Memory Access (DMA) control '
                                                  'lines.'],
                          'practical_application': 'System designers use status pins S0, S1, and IO/M# to generate '
                                                   'chip enable (CE#) signals for memory and peripheral ICs.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'During Opcode Fetch, IO/M# is LOW (0) and both status lines S1 '
                                                     'and S0 are HIGH (1).',
                                      'options': [   'IO/M#=1, S1=0, S0=1',
                                                     'IO/M#=0, S1=1, S0=1',
                                                     'IO/M#=0, S1=1, S0=0',
                                                     'IO/M#=1, S1=1, S0=0'],
                                      'question': 'What are the states of IO/M#, S1, and S0 during an Opcode Fetch '
                                                  'machine cycle?'},
                          'register_state': {   'after': 'IO/M# = 0, RD# = 0 (Data placed on bus)',
                                                'before': 'IO/M# = 0, RD# = 1, WR# = 1',
                                                'operation': 'Memory Read Cycle'},
                          'summary': 'Comprehensive 40-pin DIP layout analysis: Power, Clock, Address/Data, '
                                     'Control/Status, Interrupts, and DMA signals.',
                          'title': '8085 Pin Diagram & Signal Classification',
                          'try_it': 'View live pin state transitions in the Bus Animation panel of ElectroVerse.'}]},
    {   'color': '#10B981',
        'icon': 'fa5s.flag',
        'id': 'cat_3',
        'title': '3. 8085 REGISTERS & FLAGS',
        'topics': [   {   'diagram': '\n'
                                     '+---------------------------------------------------------------+\n'
                                     '|                      8085 FLAG REGISTER (PSW)                 |\n'
                                     '|   Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit 0|\n'
                                     '| +-------+-------+-------+-------+-------+-------+-------+----+ |\n'
                                     '| |   S   |   Z   |   X   |  AC   |   X   |   P   |   X   | CY | |\n'
                                     '| +-------+-------+-------+-------+-------+-------+-------+----+ |\n'
                                     '|   Sign    Zero    Unused  Aux     Unused Parity  Unused Carry |\n'
                                     '|                          Carry                                |\n'
                                     '+---------------------------------------------------------------+\n',
                          'example': 'MVI A, FFH -> INR A\n'
                                     '- Result: A = 00H\n'
                                     '- Flags: Z = 1 (result is 0), S = 0, P = 1 (zero ones = even), AC = 1 (carry '
                                     'D3->D4), CY = Unchanged (INR does NOT alter CY!).',
                          'how_it_works': 'Example Calculation: ADD 95H + 83H\n'
                                          '  95H = 1001 0101\n'
                                          '+ 83H = 1000 0011\n'
                                          '-----------------\n'
                                          ' Sum = 0001 1000 = 18H with Carry out of D7 = 1\n'
                                          'Flags Update:\n'
                                          '- CY = 1 (Carry out of MSB)\n'
                                          '- S = 0 (MSB D7 is 0)\n'
                                          '- Z = 0 (Result 18H != 00H)\n'
                                          '- AC = 0 (No carry from D3 to D4)\n'
                                          '- P = 1 (Result 0001 1000 has 2 ones -> Even parity)',
                          'id': '8085_flag_register',
                          'important_points': [   'S (Sign - Bit 7): Set to 1 if D7 of ALU result is 1 (negative '
                                                  "number in 2's complement).",
                                                  'Z (Zero - Bit 6): Set to 1 if the ALU operation result is exactly '
                                                  '00H.',
                                                  'AC (Auxiliary Carry - Bit 4): Set to 1 if carry is generated from '
                                                  'bit D3 to D4 (used by DAA).',
                                                  'P (Parity - Bit 2): Set to 1 if result has an EVEN number of 1s '
                                                  '(even parity).',
                                                  'CY (Carry - Bit 0): Set to 1 if carry/borrow is generated out of '
                                                  'MSB D7.'],
                          'practical_application': 'Flag registers drive conditional jumps (`JZ`, `JNZ`, `JC`, `JNC`, '
                                                   '`JM`, `JP`), controlling loop execution and branching logic.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'INR and DCR instructions modify S, Z, AC, and P flags, but '
                                                     'preserve the Carry Flag (CY) to allow loop counters without '
                                                     'destroying addition carries.',
                                      'options': [   'Zero Flag (Z)',
                                                     'Sign Flag (S)',
                                                     'Carry Flag (CY)',
                                                     'Parity Flag (P)'],
                                      'question': 'Which 8085 status flag is NOT affected by the INR (Increment) '
                                                  'instruction?'},
                          'register_state': {   'after': 'A = 00H, Flags: S=0, Z=1, AC=1, P=1, CY=0 (CY unchanged!)',
                                                'before': 'A = FFH, Flags: S=0, Z=0, AC=0, P=0, CY=0',
                                                'operation': 'INR A'},
                          'summary': 'Complete breakdown of the 8-bit status flag register (PSW): Sign (S), Zero (Z), '
                                     'Auxiliary Carry (AC), Parity (P), and Carry (CY).',
                          'title': '8085 Flag Register Format & Detailed Mechanics',
                          'try_it': 'Test flag updates step-by-step using the Flag Register display in ElectroVerse '
                                    'Trainer.'}]},
    {   'color': '#06B6D4',
        'icon': 'fa5s.code',
        'id': 'cat_4',
        'title': '4. 8085 INSTRUCTION SET',
        'topics': [   {   'diagram': '\n'
                                     '+---------------------------------------------------------------+\n'
                                     '|                       DAD B OPERATION                         |\n'
                                     '|                                                               |\n'
                                     '|   HL Pair (High: H, Low: L)  <---  HL (2000H) + BC (1000H)    |\n'
                                     '|                                                               |\n'
                                     '|   H (20H) L (00H)  +  B (10H) C (00H)  ===>  H (30H) L (00H)   |\n'
                                     '|                                                               |\n'
                                     '|   Flags Affected: ONLY Carry Flag (CY). S, Z, AC, P Unchanged.|\n'
                                     '+---------------------------------------------------------------+\n',
                          'example': 'LXI H, 2000H\nLXI B, 1000H\nDAD B\nResult: HL = 3000H, CY = 0',
                          'how_it_works': '1. 8085 fetches opcode 09H (4 T-states).\n'
                                          '2. Internal 16-bit bus adds Low registers (L + C) and High registers (H + B '
                                          '+ carry).\n'
                                          '3. Writes 16-bit sum back into HL pair.',
                          'id': 'inst_dad_b',
                          'important_points': [   'Mnemonic: DAD B',
                                                  'Meaning: Double Add BC pair to HL pair',
                                                  'Opcode: 09H | Bytes: 1 | Machine Cycles: 3 (10 T-states)',
                                                  'Addressing Mode: Register (16-bit operand)',
                                                  'Flags Affected: ONLY Carry Flag (CY). S, Z, AC, P remain '
                                                  'unchanged!'],
                          'practical_application': 'Used for 16-bit memory address calculation, array indexing, and '
                                                   '16-bit arithmetic in 8085 software.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'DAD modifies ONLY the Carry Flag (CY). The Sign, Zero, Auxiliary '
                                                     'Carry, and Parity flags remain unchanged.',
                                      'options': [   'All status flags (S, Z, AC, P, CY)',
                                                     'Zero flag only',
                                                     'Carry flag (CY) only',
                                                     'No flags are affected'],
                                      'question': 'Which flags are modified by the 8085 DAD instruction?'},
                          'register_state': {   'after': 'H = 30H, L = 00H (HL = 3000H) | CY = 0, Other Flags = '
                                                         'Unchanged',
                                                'before': 'H = 20H, L = 00H (HL = 2000H) | B = 10H, C = 00H (BC = '
                                                          '1000H)',
                                                'operation': 'DAD B (Opcode: 09H)'},
                          'summary': 'Adds the 16-bit contents of BC register pair to HL register pair and stores the '
                                     '16-bit sum in HL.',
                          'title': 'DAD B - 16-Bit Register Pair Addition',
                          'try_it': 'Run DAD B on the 8085 Trainer Kit to observe 16-bit register pair addition.'},
                      {   'diagram': '\n'
                                     '+-------------------------------------------------------------------+\n'
                                     '|                        DAA ADJUSTMENT RULES                       |\n'
                                     '|                                                                   |\n'
                                     '|  1. If lower nibble (D3-D0) > 9 or AC = 1  ===> Add 06H to A     |\n'
                                     '|  2. If upper nibble (D7-D4) > 9 or CY = 1  ===> Add 60H to A     |\n'
                                     '|                                                                   |\n'
                                     '|  Example: 38H + 45H = 7DH  ---[ DAA ]---> 83H (Correct BCD Sum)  |\n'
                                     '+-------------------------------------------------------------------+\n',
                          'example': 'MVI A, 38H\n'
                                     'ADI 45H -> A = 7DH (Binary Sum)\n'
                                     'DAA -> A = 83H (Valid BCD Sum: 38 + 45 = 83)',
                          'how_it_works': 'DAA tests lower nibble (D3-D0) and AC flag. If D3-D0 > 9 or AC=1, adds 06H. '
                                          'Then tests upper nibble (D7-D4) and CY flag. If D7-D4 > 9 or CY=1, adds 60H '
                                          'and sets CY=1.',
                          'id': 'inst_daa',
                          'important_points': [   'Mnemonic: DAA',
                                                  'Meaning: Decimal Adjust Accumulator for BCD arithmetic',
                                                  'Opcode: 27H | Bytes: 1 | Machine Cycles: 1 (4 T-states)',
                                                  'Addressing Mode: Implied',
                                                  'Flags Affected: All status flags (S, Z, AC, P, CY)'],
                          'practical_application': 'Essential for digital clocks, calculators, digital meters, and '
                                                   'financial BCD arithmetic.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'DAA adds 06H to the lower nibble if D3-D0 exceeds 9 or if '
                                                     'Auxiliary Carry (AC) flag is set to 1.',
                                      'options': [   'If lower nibble > 9 OR AC = 1',
                                                     'If lower nibble > 5',
                                                     'If Carry Flag CY = 1',
                                                     'If Zero Flag Z = 1'],
                                      'question': 'What condition triggers DAA to add 06H to the lower nibble of the '
                                                  'Accumulator?'},
                          'register_state': {   'after': 'A = 83H, AC = 1, CY = 0, Z = 0, S = 1',
                                                'before': 'A = 7DH, AC = 0, CY = 0',
                                                'operation': 'DAA (Opcode: 27H)'},
                          'summary': 'Adjusts the 8-bit binary ALU sum in the Accumulator to form two 4-bit Binary '
                                     'Coded Decimal (BCD) digits.',
                          'title': 'DAA - Decimal Adjust Accumulator',
                          'try_it': 'Test DAA after BCD addition programs in ElectroVerse.'}]},
    {   'color': '#8B5CF6',
        'icon': 'fa5s.map-marker-alt',
        'id': 'cat_5',
        'title': '5. 8085 ADDRESSING MODES',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                           8085 ADDRESSING '
                                     'MODES                                   |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  1. IMMEDIATE          : Data is part of instruction     e.g., MVI A, '
                                     '45H        |\n'
                                     '|  2. REGISTER           : Data in CPU registers           e.g., MOV A, '
                                     'B          |\n'
                                     '|  3. DIRECT             : Address specified in instruction e.g., LDA '
                                     '2050H        |\n'
                                     '|  4. REGISTER INDIRECT  : Address stored in HL pair       e.g., MOV A, '
                                     'M          |\n'
                                     '|  5. IMPLIED / IMPLICIT : Operand implied in opcode       e.g., CMA, '
                                     'RLC          |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'If HL = 2050H and RAM[2050H] = 45H:\nExecuting `MOV A, M` loads `45H` into `A`.',
                          'how_it_works': 'Register Indirect `MOV A, M` execution:\n'
                                          '1. 8085 reads 16-bit memory address currently held in HL pair.\n'
                                          '2. Sends HL address over bus to RAM.\n'
                                          '3. Latches RAM data byte into Accumulator A.',
                          'id': 'addr_modes_overview',
                          'important_points': [   'Immediate Addressing: Operand data immediately follows opcode in '
                                                  'byte 2 or 3 (MVI, LXI, ADI, ANI).',
                                                  'Register Addressing: Operands are 8-bit or 16-bit registers (MOV '
                                                  'A,B; ADD C; DAD B). Zero memory cycles.',
                                                  'Direct Addressing: 16-bit memory or 8-bit port address explicitly '
                                                  'stated in instruction bytes (LDA 2050H; STA 2051H; IN 01H).',
                                                  'Register Indirect Addressing: 16-bit memory address stored in HL '
                                                  'pair (M) or BC/DE pair (LDAX B, STAX D, MOV A,M).',
                                                  'Implied/Implicit Addressing: Operand specified implicitly by the '
                                                  'operation itself (CMA, RLC, STC, HLT).'],
                          'practical_application': 'Register indirect addressing enables fast array traversal and '
                                                   'pointer-based data processing.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'LDAX B uses Register Indirect Addressing because the memory '
                                                     'address is stored inside the BC register pair.',
                                      'options': [   'Direct Addressing',
                                                     'Register Indirect Addressing',
                                                     'Immediate Addressing',
                                                     'Implied Addressing'],
                                      'question': 'Which addressing mode is used by the instruction `LDAX B`?'},
                          'register_state': {   'after': 'A = 45H, HL = 2050H (Unchanged)',
                                                'before': 'HL = 2050H, RAM[2050H] = 45H, A = 00H',
                                                'operation': 'MOV A, M (Opcode: 7EH)'},
                          'summary': 'The 5 fundamental methods used by instructions to specify operand locations: '
                                     'Immediate, Register, Direct, Register Indirect, and Implied.',
                          'title': 'Classification of 8085 Addressing Modes',
                          'try_it': 'Experiment with MOV A, M using HL pointers in the Virtual 8085 Trainer.'}]},
    {   'color': '#EC4899',
        'icon': 'fa5s.stopwatch',
        'id': 'cat_6',
        'title': '6. 8085 TIMING & MACHINE CYCLES',
        'topics': [   {   'diagram': '\n'
                                     '           T1                T2                T3                T4\n'
                                     '      +---------+       +---------+       +---------+       +---------+\n'
                                     'CLK   |    _    |       |    _    |       |    _    |       |    _    |\n'
                                     ' _____|   / \\   |_______|   / \\   |_______|   / \\   |_______|   / \\   '
                                     '|_____\n'
                                     '      +--+   +--+       +--+   +--+       +--+   +--+       +--+   +--+\n'
                                     'A15-A8====[  PC High Address  ]===============================================\n'
                                     'AD7-AD0===[ PC Low  ]====================[ Opcode Byte Data ]=================\n'
                                     'ALE   +------+\n'
                                     ' _____|      |________________________________________________________________\n'
                                     'RD#                     +-----------------+\n'
                                     ' _______________________|                 |___________________________________\n',
                          'example': 'Opcode Fetch for 3EH (MVI A):\n'
                                     'T1: PC=2000H -> A15-A8=20H, AD7-AD0=00H, ALE=1\n'
                                     'T2: RD#=0, AD7-AD0 floats\n'
                                     'T3: Memory outputs 3EH on AD7-AD0, RD#=1 latches 3EH\n'
                                     'T4: Internal instruction decoder decodes 3EH as MVI A.',
                          'how_it_works': 'Total Opcode Fetch time = 4 T-states (or 6 T-states for 16-bit register '
                                          'pair fetch like `DCX` or `INX`).\n'
                                          'If CPU clock = 3 MHz -> T-state = 1/3MHz = 333.3 ns. Opcode Fetch = 4 * '
                                          '333.3 ns = 1.33 us.',
                          'id': 'timing_opcode_fetch',
                          'important_points': [   'T1 State: MPU places High PC address on A15-A8, Low PC address on '
                                                  'AD7-AD0, and pulses ALE High.',
                                                  'T2 State: ALE goes Low to latch low address. MPU floats AD7-AD0 and '
                                                  'asserts RD# Low.',
                                                  'T3 State: Selected memory chip outputs opcode byte onto AD7-AD0. '
                                                  'MPU latches byte into Instruction Register (IR) on RD# rising edge.',
                                                  'T4 State: MPU decodes opcode and prepares internal execution '
                                                  'control signals.'],
                          'practical_application': 'Timing diagrams allow hardware engineers to calculate exact '
                                                   'instruction execution delays for real-time control systems.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'A standard 8085 Opcode Fetch cycle requires 4 T-states (T1 to '
                                                     'T4).',
                                      'options': ['3 T-states', '4 T-states', '6 T-states', '2 T-states'],
                                      'question': 'How many T-states are required for a standard 8085 Opcode Fetch '
                                                  'machine cycle?'},
                          'register_state': {   'after': 'PC = 2001H, IR = 3EH (MVI A decoded)',
                                                'before': 'PC = 2000H, IR = 00H',
                                                'operation': 'Opcode Fetch Cycle (T1-T4)'},
                          'summary': 'Detailed T-state timing breakdown of the fundamental Opcode Fetch machine cycle.',
                          'title': 'Opcode Fetch Machine Cycle (T1 - T4 States)',
                          'try_it': 'Watch T-state progression in the 8085 Execution Animator.'}]},
    {   'color': '#14B8A6',
        'icon': 'fa5s.server',
        'id': 'cat_7',
        'title': '7. 8085 MEMORY & I/O',
        'topics': [   {   'diagram': '\n'
                                     'MEMORY-MAPPED I/O                          I/O-MAPPED I/O (ISOLATED I/O)\n'
                                     '+------------------------------------+     '
                                     '+------------------------------------+\n'
                                     '| 64 KB Unified Address Space        |     | 64 KB Memory Space (IO/M# = 0)     '
                                     '|\n'
                                     '| [0000H - FFFFH]                    |     | [0000H - FFFFH]                    '
                                     '|\n'
                                     '|                                    |     '
                                     '+------------------------------------+\n'
                                     '| Memory & I/O Ports share address   |     | 256 I/O Port Space (IO/M# = 1)     '
                                     '|\n'
                                     '| space (e.g. Port at 2050H)         |     | [00H - FFH] (IN 01H / OUT 02H)     '
                                     '|\n'
                                     '+------------------------------------+     '
                                     '+------------------------------------+\n',
                          'example': 'Reading DIP Switch at Port 05H:\n'
                                     '`IN 05H` -> Data from port 05H loaded into Accumulator A.',
                          'how_it_works': 'Isolated I/O `OUT 01H` execution:\n'
                                          '1. MPU outputs port address `01H` on both A15-A8 and AD7-AD0.\n'
                                          '2. Asserts IO/M# = 1, WR# = 0 -> active IOW# pulse.\n'
                                          '3. Latching 8-bit Accumulator contents to output port 01H.',
                          'id': 'mem_io_mapping',
                          'important_points': [   'Memory-Mapped I/O: I/O devices treated as memory locations (16-bit '
                                                  'address). Accessed via LDA, STA, MOV, ADD instructions.',
                                                  'I/O-Mapped I/O: Isolated 8-bit port addresses (00H to FFH = 256 '
                                                  'ports). Accessed ONLY via IN and OUT instructions.',
                                                  'Control Lines: Memory-Mapped uses MEMR#/MEMW# (IO/M#=0). Isolated '
                                                  'I/O uses IOR#/IOW# (IO/M#=1).',
                                                  'Accumulator Freedom: Memory-Mapped allows arithmetic directly on '
                                                  'ports (e.g., ADD M). Isolated I/O strictly routes data through '
                                                  'Accumulator A.'],
                          'practical_application': 'Isolated I/O preserves the full 64KB RAM address space for '
                                                   'application code while supporting 256 I/O devices.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'An 8-bit port address allows 2^8 = 256 input ports and 256 '
                                                     'output ports.',
                                      'options': ['65,536 ports', '256 ports', '512 ports', '1,024 ports'],
                                      'question': 'How many total I/O ports can be addressed in 8085 Isolated '
                                                  '(I/O-Mapped) I/O mode?'},
                          'register_state': {   'after': 'A = F0H',
                                                'before': 'Port 05H = F0H, A = 00H',
                                                'operation': 'IN 05H (Opcode: DB 05)'},
                          'summary': 'Comparing 16-bit Memory-Mapped I/O interfacing with 8-bit Isolated I/O-Mapped '
                                     'interfacing.',
                          'title': 'Memory-Mapped I/O vs I/O-Mapped I/O (Peripheral I/O)',
                          'try_it': 'Test IN and OUT port operations on the 8255 PPI simulator.'}]},
    {   'color': '#EF4444',
        'icon': 'fa5s.bolt',
        'id': 'cat_8',
        'title': '8. 8085 INTERRUPTS',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------------+\n'
                                     '|                              8085 INTERRUPT PRIORITY & VECTOR '
                                     'TABLE                     |\n'
                                     '|                                                                                         '
                                     '|\n'
                                     '|  Interrupt Pin   Priority   Trigger Type      Maskable?   Vector Address '
                                     '(Hex)          |\n'
                                     '|  -------------   --------   ------------      ---------   '
                                     '--------------------          |\n'
                                     '|  TRAP (RST 4.5)  1 (High)   Edge + Level      No (NMI)    0024H (4.5 * '
                                     '8)               |\n'
                                     '|  RST 7.5          2          Falling Edge      Yes         003CH (7.5 * '
                                     '8)               |\n'
                                     '|  RST 6.5          3          High Level        Yes         0034H (6.5 * '
                                     '8)               |\n'
                                     '|  RST 5.5          4          High Level        Yes         002CH (5.5 * '
                                     '8)               |\n'
                                     '|  INTR             5 (Low)    High Level        Yes         Non-vectored (from '
                                     'bus)       |\n'
                                     '+-----------------------------------------------------------------------------------------+\n',
                          'example': 'RST 7.5 Triggered -> 8085 saves PC to Stack and jumps immediately to 003CH to '
                                     'run the Interrupt Service Routine (ISR).',
                          'how_it_works': 'When an interrupt occurs:\n'
                                          '1. 8085 completes current instruction.\n'
                                          '2. Pushes current PC onto Stack.\n'
                                          '3. Disables further interrupts (FF = 0).\n'
                                          '4. Jumps to corresponding ISR Vector Address.',
                          'id': '8085_interrupt_structure',
                          'important_points': [   'TRAP: Highest priority, Non-Maskable Interrupt (NMI). Vector = '
                                                  '0024H.',
                                                  'RST 7.5: 2nd priority, edge-triggered falling edge, maskable via '
                                                  'SIM. Vector = 003CH.',
                                                  'RST 6.5 & 5.5: Level-triggered, maskable via SIM. Vectors = 0034H '
                                                  'and 002CH.',
                                                  'INTR: Lowest priority, non-vectored. Requires external INTA# '
                                                  'acknowledgment to receive RST opcode.',
                                                  'EI / DI: Enable Interrupts (EI) and Disable Interrupts (DI) machine '
                                                  'instructions.'],
                          'practical_application': 'TRAP is reserved for emergency power-fail handling; RST 7.5 '
                                                   'handles high-speed encoder pulses.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'Vector Address = Interrupt Number * 8 = 4.5 * 8 = 36 decimal = '
                                                     '0024H.',
                                      'options': ['003CH', '0024H', '0034H', '0000H'],
                                      'question': 'What is the fixed vector memory address for the 8085 TRAP (RST 4.5) '
                                                  'interrupt?'},
                          'register_state': {   'after': 'RAM[27FEH]=20H, RAM[27FDH]=50H, SP=27FDH, PC=003CH',
                                                'before': 'PC = 2050H, SP = 27FFH',
                                                'operation': 'RST 7.5 Interrupt Triggered'},
                          'summary': 'Detailed analysis of TRAP, RST 7.5, RST 6.5, RST 5.5, INTR, SIM, and RIM '
                                     'interrupt processing.',
                          'title': '8085 Interrupt System, Vector Addresses & Priorities',
                          'try_it': 'Trigger hardware interrupts in the ElectroVerse 8085 Interrupt Visualizer.'}]},
    {   'color': '#F59E0B',
        'icon': 'fa5s.layer-group',
        'id': 'cat_9',
        'title': '9. 8085 STACK & SUBROUTINES',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                           8085 STACK PUSH / POP '
                                     'MECHANICS                         |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|    PUSH B (SP decrements before '
                                     'write):                                           |\n'
                                     '|    1. SP <-- SP - 1,  RAM[SP] <-- High Register '
                                     'B                                 |\n'
                                     '|    2. SP <-- SP - 1,  RAM[SP] <-- Low Register '
                                     'C                                  |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|    POP B (SP increments after '
                                     'read):                                              |\n'
                                     '|    1. Low Register C <-- RAM[SP],   SP <-- SP + '
                                     '1                                 |\n'
                                     '|    2. High Register B <-- RAM[SP],  SP <-- SP + '
                                     '1                                 |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'LXI SP, 27FFH\n'
                                     'PUSH B (with B=12H, C=34H)\n'
                                     'Result: RAM[27FEH] = 12H, RAM[27FDH] = 34H, SP = 27FDH.',
                          'how_it_works': 'CALL 3000H at PC = 2000H:\n'
                                          '1. 8085 calculates return address PC+3 = 2003H.\n'
                                          '2. Pushes 20H to RAM[SP-1], 03H to RAM[SP-2].\n'
                                          '3. Updates SP = SP - 2.\n'
                                          '4. Sets PC = 3000H.',
                          'id': 'stack_push_pop',
                          'important_points': [   'Stack Pointer (SP): 16-bit register holding top-of-stack memory '
                                                  'address in RAM.',
                                                  'Stack Growth: Grows DOWNWARDS toward lower memory addresses.',
                                                  'PUSH rp: Decrements SP by 2, stores 16-bit register pair into RAM.',
                                                  'POP rp: Reads 16-bit register pair from RAM, increments SP by 2.',
                                                  'CALL addr: Pushes 16-bit return address (PC) onto Stack, jumps to '
                                                  'subroutine.',
                                                  'RET: Pops 16-bit return address from Stack into PC to return to '
                                                  'main program.'],
                          'practical_application': 'Enables recursive programming, nested subroutine calls, and '
                                                   'context preservation during interrupts.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'PUSH stores a 2-byte register pair onto the stack, decrementing '
                                                     'SP by 2.',
                                      'options': [   'Decrements by 2',
                                                     'Increments by 2',
                                                     'Decrements by 1',
                                                     'Remains unchanged'],
                                      'question': 'How does the Stack Pointer (SP) change during a PUSH instruction?'},
                          'register_state': {   'after': 'SP = 27FDH, RAM[27FEH] = 12H, RAM[27FDH] = 34H',
                                                'before': 'SP = 27FFH, B = 12H, C = 34H',
                                                'operation': 'PUSH B (Opcode: C5H)'},
                          'summary': 'LIFO stack operation, PUSH/POP register pair manipulation, and subroutine '
                                     'call/return mechanics.',
                          'title': 'Stack Pointer (SP), PUSH, POP, CALL & RET Mechanics',
                          'try_it': 'Observe Stack Pointer movement during PUSH and CALL operations in the 8085 '
                                    'Trainer.'}]},
    {   'color': '#10B981',
        'icon': 'fa5s.terminal',
        'id': 'cat_10',
        'title': '10. 8085 ASSEMBLY LANGUAGE PROGRAMMING',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        BCD UNPACKING DATA FLOW '
                                     'DIAGRAM                            |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  Packed Input [2050H] = 45H  ======>  '
                                     '[45H]                                       |\n'
                                     '|                                         '
                                     '|                                         |\n'
                                     '|                 '
                                     '+-----------------------+-----------------------+                 |\n'
                                     '|                 v                                               '
                                     'v                 |\n'
                                     '|            ANI 0FH (Lower)                                 ANI F0H + 4 '
                                     'RRCs       |\n'
                                     '|                 |                                               '
                                     '|                 |\n'
                                     '|                 v                                               '
                                     'v                 |\n'
                                     '|  Lower Digit [2051H] = 05H                      Upper Digit [2052H] = '
                                     '04H        |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Input: RAM[2050H] = 45H\n'
                                     'Output: RAM[2051H] = 05H, RAM[2052H] = 04H\n'
                                     'Final CPU State: A = 04H, B = 45H, HLT = True',
                          'how_it_works': 'Assembly Code:\n'
                                          '```assembly\n'
                                          'LDA 2050H   ; A = 45H\n'
                                          'MOV B, A    ; B = 45H\n'
                                          'ANI 0FH     ; A = 05H\n'
                                          'STA 2051H   ; RAM[2051H] = 05H\n'
                                          'MOV A, B    ; A = 45H\n'
                                          'ANI F0H     ; A = 40H\n'
                                          'RRC         ; A = 20H\n'
                                          'RRC         ; A = 10H\n'
                                          'RRC         ; A = 08H\n'
                                          'RRC         ; A = 04H\n'
                                          'STA 2052H   ; RAM[2052H] = 04H\n'
                                          'HLT         ; Halt\n'
                                          '```',
                          'id': 'prog_bcd_unpack',
                          'important_points': [   'Problem: Convert Packed BCD byte (e.g. 45H) at 2050H into 05H at '
                                                  '2051H and 04H at 2052H.',
                                                  'Algorithm: Load byte -> Copy to B -> Mask upper nibble (ANI 0FH) -> '
                                                  'Store 2051H -> Restore B -> Mask lower nibble (ANI F0H) -> Rotate '
                                                  'right 4 times -> Store 2052H -> HLT.',
                                                  'Opcodes: 3A 50 20 47 E6 0F 32 51 20 78 E6 F0 0F 0F 0F 0F 32 52 20 '
                                                  '76',
                                                  'Total Bytes: 20 bytes.'],
                          'practical_application': 'Used in 7-segment LED display drivers, digital meters, and '
                                                   'financial calculators to separate BCD digits for display '
                                                   'multiplexing.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'Masking with ANI F0H leaves 40H (bits D7-D4). Four RRC rotations '
                                                     'shift the bits 4 positions right to form 04H (bits D3-D0).',
                                      'options': [   'To multiply the upper nibble by 4',
                                                     'To shift bits D7-D4 down into position D3-D0',
                                                     'To clear the Carry flag',
                                                     'To complement the nibble'],
                                      'question': 'Why are 4 RRC (Rotate Right) instructions required when processing '
                                                  'the upper BCD nibble?'},
                          'register_state': {   'after': 'RAM[2051H] = 05H, RAM[2052H] = 04H | A = 04H, B = 45H, Z = '
                                                         '0, S = 0',
                                                'before': 'RAM[2050H] = 45H, A = 00H, B = 00H',
                                                'operation': 'Execute Unpack BCD Program (2000H - 2013H)'},
                          'summary': 'Full practical program breakdown: Problem statement, algorithm, assembly code, '
                                     'machine code, memory map, register/flag changes, and step-by-step execution.',
                          'title': 'Unpacking a Packed BCD Number (Complete Program Analysis)',
                          'try_it': 'Run this exact Unpack BCD program on the Virtual 8085 Trainer Kit.'}]},
    {   'color': '#3B82F6',
        'icon': 'fa5s.plug',
        'id': 'cat_11',
        'title': '11. 8085 INTERFACING',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8255 PPI HARDWARE '
                                     'INTERFACING                              |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|   8085 CPU                     8255 PPI                         '
                                     'PERIPHERALS       |\n'
                                     '|   +-------+                    +--------+                      '
                                     '+---------------+  |\n'
                                     '|   | AD0-7 |===================>| D0-D7  |====== Port A (PA0-7)====>| 7-Seg '
                                     'LED     |  |\n'
                                     '|   | A0-A1 |===================>| A0-A1  |====== Port B (PB0-7)====>| DIP '
                                     'Switches  |  |\n'
                                     '|   | RD#   |===================>| RD#    |====== Port C (PC0-7)====>| Relays / '
                                     'LEDs |  |\n'
                                     '|   | WR#   |===================>| WR#    |                      '
                                     '+---------------+  |\n'
                                     '|   | IO/M# |----[ Decoder ]---->| CS#    '
                                     '|                                         |\n'
                                     '|   +-------+                    '
                                     '+--------+                                         |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'If 8255 base address = 80H:\n'
                                     'Port A = 80H, Port B = 81H, Port C = 82H, Control Reg = 83H.\n'
                                     'Code:\n'
                                     '`MVI A, 80H` -> `OUT 83H` (Configures Ports A, B, C as outputs).\n'
                                     '`MVI A, FFH` -> `OUT 80H` (Turns ON all Port A LEDs).',
                          'how_it_works': 'Configuring Mode 0 All Output:\n'
                                          'Control Word = 80H (1000 0000B).\n'
                                          'MVI A, 80H -> OUT [Control Port Address].',
                          'id': 'interfacing_8255',
                          'important_points': [   '24 programmable parallel I/O pins organized into Port A, Port B, '
                                                  'and Port C (PC Upper & PC Lower).',
                                                  'Control Register Address: Selected when A1 = 1, A0 = 1 with CS# = '
                                                  '0.',
                                                  'Mode 0: Basic Input/Output (no handshake).',
                                                  'Mode 1: Strobed I/O with handshake control lines.',
                                                  'Mode 2: Bi-directional bus I/O on Port A.'],
                          'practical_application': '8255 PPI is used worldwide to interface LED displays, DIP '
                                                   'switches, relays, stepper motors, and printer ports.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'Control Word 80H (1000 0000B) sets D7=1 (Mode Definition), Mode '
                                                     '0 for all ports, and Ports A, B, C as Output.',
                                      'options': ['80H', '82H', '90H', '00H'],
                                      'question': 'What is the Control Word byte to configure 8255 Ports A, B, and C '
                                                  'as basic outputs in Mode 0?'},
                          'register_state': {   'after': 'Port A = FFH (All 8 LEDs illuminated)',
                                                'before': 'Port A = 00H, Control Reg = Uninitialized',
                                                'operation': 'MVI A, 80H -> OUT 83H followed by MVI A, FFH -> OUT 80H'},
                          'summary': 'Interfacing 8255 PPI with 8085 for parallel I/O, control word formats, and mode '
                                     'configuration.',
                          'title': '8255 Programmable Peripheral Interface (PPI) Architecture',
                          'try_it': 'Experiment with the 8255 PPI Tri-Port Simulator in ElectroVerse.'}]},
    {   'color': '#6366F1',
        'icon': 'fa5s.exchange-alt',
        'id': 'cat_12',
        'title': '12. SERIAL COMMUNICATION',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                     ASYNCHRONOUS SERIAL FRAME '
                                     'FORMAT                              |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|   IDLE   +---+   +---+   +---+   +---+   +---+   +---+   +---+   +---+   '
                                     '+---+    |\n'
                                     '|  (MARK)  |ST |   |D0 |   |D1 |   |D2 |   |D3 |   |D4 |   |D5 |   |D6 |   |D7 | '
                                     'PAR|STOP|\n'
                                     '| ---------+   '
                                     '+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+----+|\n'
                                     '|          Start  <------------------ 8 Data Bits -------------------> Parity '
                                     'Stop |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Bit Time at 9600 Baud = 1 / 9600 = 104.16 microseconds.',
                          'how_it_works': "Transmitting 'A' (41H = 01000001B) at 9600 Baud:\n"
                                          '1. TXD line drops LOW for 1 bit time (Start Bit = 104.16 us).\n'
                                          '2. TXD transmits D0 to D7 sequentially (LSB first).\n'
                                          '3. TXD goes HIGH for Stop Bit time.',
                          'id': 'serial_usart_8251',
                          'important_points': [   'Serial Transmission: Sends data bit-by-bit over a single conductor '
                                                  'pair.',
                                                  'Asynchronous Format: Uses Start Bit (LOW logic 0), 5-8 Data Bits, '
                                                  'Parity Bit, and Stop Bit(s) (HIGH logic 1).',
                                                  'Baud Rate: Number of signal transitions per second (e.g. 9600 '
                                                  'Baud).',
                                                  '8251 USART: Universal Synchronous/Asynchronous Receiver Transmitter '
                                                  'IC.'],
                          'practical_application': 'Forms the baseline for RS-232, RS-485, USB-to-UART serial bridges, '
                                                   'and wireless Bluetooth/Wi-Fi module interfacing.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'Bit duration = 1 / Baud Rate = 1 / 9600 seconds = 104.16 '
                                                     'microseconds.',
                                      'options': [   '104.16 microseconds',
                                                     '1.04 milliseconds',
                                                     '96 microseconds',
                                                     '10.4 microseconds'],
                                      'question': 'What is the duration of 1 bit at a baud rate of 9600 Baud?'},
                          'register_state': {   'after': 'TXD Line = 10-bit serial stream sent to RS-232 driver',
                                                'before': 'TXD Line = HIGH (Idle MARK state)',
                                                'operation': 'Transmitting byte 41H via 8251 USART'},
                          'summary': 'Synchronous vs Asynchronous serial transmission, Baud Rate calculations, RS-232C '
                                     'standards, and 8251 USART.',
                          'title': 'Serial Communication & 8251 USART Principles',
                          'try_it': 'Launch the 8051 UART / Serial Baud Animator in the Simulation tab.'}]},
    {   'color': '#14B8A6',
        'icon': 'fa5s.microchip',
        'id': 'cat_13',
        'title': '13. MICROCONTROLLERS',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        HARVARD ARCHITECTURE '
                                     '(MICROCONTROLLER)                     |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|    +--------------------+    Separate 16-Bit Program Bus   '
                                     '+------------------+  |\n'
                                     '|    |                    |==================================>|  PROGRAM MEMORY  '
                                     '|  |\n'
                                     '|    |                    |                                   |   (FLASH ROM)    '
                                     '|  |\n'
                                     '|    |   CPU CORE (8051)  |                                   '
                                     '+------------------+  |\n'
                                     '|    |                    |    Separate 8-Bit Data Bus        '
                                     '+------------------+  |\n'
                                     '|    |                    |<=================================>|   DATA MEMORY    '
                                     '|  |\n'
                                     '|    +--------------------+                                   |   (INTERNAL RAM) '
                                     '|  |\n'
                                     '|                                                             '
                                     '+------------------+  |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': '8051 Microcontroller fetching instruction from Flash ROM at 0000H while reading '
                                     'internal RAM bank 0 at 08H.',
                          'how_it_works': 'Harvard architecture eliminates the bus bottleneck found in von Neumann '
                                          'microprocessors, allowing single-cycle execution of memory instructions.',
                          'id': 'mcu_overview',
                          'important_points': [   'Harvard Architecture: Separate memory spaces and buses for Program '
                                                  'Code (ROM) and Data (RAM).',
                                                  'Simultaneous Fetch & Read: CPU can fetch code instructions from ROM '
                                                  'while reading data from RAM.',
                                                  'Embedded Control: Optimized for low power, real-time interrupts, '
                                                  'and direct bit manipulation of I/O pins.'],
                          'practical_application': 'Used in modern microcontrollers (ARM Cortex-M, AVR, PIC) for '
                                                   'high-performance automotive ABS, medical devices, and drones.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'Harvard architecture uses physically separate memory spaces and '
                                                     'buses for instruction ROM and data RAM.',
                                      'options': [   'Shared memory bus for code and data',
                                                     'Separate memory spaces and independent buses for code and data',
                                                     'No internal RAM',
                                                     'Slower instruction execution'],
                                      'question': 'What is the key characteristic of Harvard Architecture used in '
                                                  'Microcontrollers?'},
                          'register_state': {   'after': 'Dual bus transfer completed in 1 machine cycle',
                                                'before': 'PC = 0000H (Program ROM), R0 = 08H (Data RAM)',
                                                'operation': 'Concurrent Code Fetch and Data Read'},
                          'summary': 'Overview of microcontroller hardware integration, Harvard architecture, memory '
                                     'partitioning, and real-time control.',
                          'title': 'Microcontroller Concepts & Embedded System Architecture',
                          'try_it': 'Compare 8051 Harvard Architecture with 8085 Von Neumann architecture.'}]},
    {   'color': '#8B5CF6',
        'icon': 'fa5s.microchip',
        'id': 'cat_14',
        'title': '14. 8051 MICROCONTROLLER',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8051 MICROCONTROLLER BLOCK '
                                     'DIAGRAM                   |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  +--------------+  +---------------+  +--------------+  '
                                     '+----------------------+  |\n'
                                     '|  | 8-BIT CPU    |  | 4KB FLASH ROM |  | 128B INT RAM |  | 128B SFRs            '
                                     '|  |\n'
                                     '|  +--------------+  +---------------+  +--------------+  '
                                     '+----------------------+  |\n'
                                     '|         |                  |                 |                     '
                                     '|              |\n'
                                     '|  '
                                     '=======+==================+=================+=====================+============  '
                                     '|\n'
                                     '|         |                  |                 |                     '
                                     '|              |\n'
                                     '|  +--------------+  +---------------+  +--------------+  '
                                     '+----------------------+  |\n'
                                     '|  | TIMER 0 & 1  |  | UART SERIAL   |  | INTERRUPTS   |  | PORTS P0, P1, P2, P3 '
                                     '|  |\n'
                                     '|  +--------------+  +---------------+  +--------------+  '
                                     '+----------------------+  |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Setting P1.0 High: `SETB P1.0` (Opcode: D2 90).\n'
                                     'Clearing P1.0 Low: `CLR P1.0` (Opcode: C2 90).',
                          'how_it_works': 'Port 3 Alternate Functions:\n'
                                          '- P3.0 (RXD), P3.1 (TXD)\n'
                                          '- P3.2 (INT0#), P3.3 (INT1#)\n'
                                          '- P3.4 (T0), P3.5 (T1)\n'
                                          '- P3.6 (WR#), P3.7 (RD#)',
                          'id': '8051_architecture_details',
                          'important_points': [   'Internal RAM (128 Bytes): 00H-1FH (Register Banks 0-3), 20H-2FH '
                                                  '(Bit-addressable RAM), 30H-7FH (Scratchpad).',
                                                  'Special Function Registers (SFRs): 128 bytes (80H-FFH) controlling '
                                                  'ports, timers, serial, and interrupts.',
                                                  'Four 8-bit I/O Ports: Port 0 (open drain multiplexed AD0-AD7), Port '
                                                  '1, Port 2 (A8-A15), Port 3 (alternate functions).',
                                                  'Oscillator & Clock: Machine cycle = 12 clock periods (12 MHz '
                                                  'crystal -> 1 us machine cycle).'],
                          'practical_application': 'Direct bit-addressability of I/O ports makes 8051 highly efficient '
                                                   'for toggling LEDs, driving stepper motors, and relay control.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'One 8051 machine cycle consists of 12 oscillator clock periods.',
                                      'options': [   '4 clock cycles',
                                                     '6 clock cycles',
                                                     '12 clock cycles',
                                                     '2 clock cycles'],
                                      'question': 'How many clock cycles make up one 8051 Machine Cycle?'},
                          'register_state': {   'after': 'P1.0 = 1 (5V output), P1 = 01H',
                                                'before': 'P1 = 00H (Port 1 pins LOW)',
                                                'operation': 'SETB P1.0'},
                          'summary': 'Comprehensive 8051 hardware analysis: 4KB ROM, 128-byte RAM, Ports P0-P3, Timers '
                                     '0/1, and Special Function Registers.',
                          'title': '8051 Microcontroller Internal Architecture & Pinout',
                          'try_it': 'Test 8051 Port I/O and Bit manipulation instructions in ElectroVerse.'}]},
    {   'color': '#F97316',
        'icon': 'fa5s.sliders-h',
        'id': 'cat_15',
        'title': '15. 8051 REGISTERS',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8051 PROGRAM STATUS WORD (PSW) '
                                     'FORMAT                      |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|   Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit '
                                     '0                   |\n'
                                     '| '
                                     '+-------+-------+-------+-------+-------+-------+-------+-------+                 '
                                     '|\n'
                                     '| |  CY   |  AC   |  F0   | RS1   | RS0   |  OV   |   --  |   P   '
                                     '|                 |\n'
                                     '| '
                                     '+-------+-------+-------+-------+-------+-------+-------+-------+                 '
                                     '|\n'
                                     '|   Carry  Aux.    User   Register Bank   Overflow Unused '
                                     'Parity                    |\n'
                                     '|          Carry   Flag   Select '
                                     'Bits                                               |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'MUL AB:\n'
                                     'If A = 25 (19H) and B = 10 (0AH):\n'
                                     '`MUL AB` -> Result 250 (00FAH).\n'
                                     'Accumulator A = FAH (Low byte), Register B = 00H (High byte), Overflow flag OV = '
                                     '0.',
                          'how_it_works': 'Register Bank Switching:\n'
                                          '- SETB RS0 (RS1=0, RS0=1) -> Switches active R0-R7 registers to Bank 1 (RAM '
                                          'addresses 08H-0FH).',
                          'id': '8051_sfr_registers',
                          'important_points': [   'Accumulator (A / E0H): Primary 8-bit register for all arithmetic '
                                                  'and logic instructions.',
                                                  'B Register (F0H): Used exclusively with A for MUL AB and DIV AB '
                                                  'operations.',
                                                  'DPTR (Data Pointer - 82H/83H): 16-bit register composed of DPH and '
                                                  'DPL for external memory addressing.',
                                                  'Register Bank Selection: RS1, RS0 bits in PSW select Bank 0 '
                                                  '(00H-07H), Bank 1 (08H-0FH), Bank 2 (10H-17H), or Bank 3 '
                                                  '(18H-1FH).'],
                          'practical_application': 'Register banks allow instant context switching in real-time '
                                                   'interrupt service routines without pushing registers to stack.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'Bits RS1 (PSW.4) and RS0 (PSW.3) select one of the 4 internal '
                                                     'RAM register banks.',
                                      'options': ['CY and AC', 'RS1 and RS0', 'OV and P', 'F0 and F1'],
                                      'question': 'Which two bits in the 8051 PSW register select the active Register '
                                                  'Bank (Banks 0-3)?'},
                          'register_state': {   'after': 'A = FAH, B = 00H, OV = 0',
                                                'before': 'A = 19H, B = 0AH, OV = 0',
                                                'operation': 'MUL AB (Opcode: A4H)'},
                          'summary': 'Analysis of Accumulator (A), B Register, Data Pointer (DPTR), Program Status '
                                     'Word (PSW), and Register Banks.',
                          'title': '8051 Special Function Registers (SFRs) & PSW',
                          'try_it': 'Switch register banks in the 8051 Register Inspector.'}]},
    {   'color': '#10B981',
        'icon': 'fa5s.code-branch',
        'id': 'cat_16',
        'title': '16. 8051 INSTRUCTION SET',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8051 INSTRUCTION '
                                     'CATEGORIES                                |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  1. DATA TRANSFER : MOV, MOVX, MOVC, PUSH, POP, '
                                     'XCH                             |\n'
                                     '|  2. ARITHMETIC    : ADD, ADDC, SUBB, INC, DEC, MUL AB, DIV AB, DA '
                                     'A               |\n'
                                     '|  3. LOGICAL       : ANL, ORL, XRL, CLR, CPL, RL, RRC, RR, '
                                     'SWAP                    |\n'
                                     '|  4. BOOLEAN (BIT) : SETB, CLR, CPL, ANL C, ORL C, MOV C, JB, JNB, '
                                     'JBC            |\n'
                                     '|  5. BRANCHING     : LJMP, AJMP, SJMP, JZ, JNZ, CJNE, DJNZ, LCALL, ACALL, '
                                     'RET       |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': '`SWAP A` with A = 45H:\n'
                                     'Executing `SWAP A` turns `45H` into `54H` instantly in 1 machine cycle.',
                          'how_it_works': 'Delay Loop using `DJNZ R0, Label`:\n'
                                          '```assembly\n'
                                          'MOV R0, #100\n'
                                          'LOOP: DJNZ R0, LOOP   ; Decrements R0, jumps to LOOP until R0 = 0\n'
                                          '```\n'
                                          'Execution time = 100 * 2 machine cycles = 200 us at 12 MHz.',
                          'id': '8051_inst_categories',
                          'important_points': [   'MOVX: Move external RAM data (`MOVX A, @DPTR` or `MOVX @DPTR, A`).',
                                                  'MOVC: Move code memory ROM data (`MOVC A, @A+DPTR` or `MOVC A, '
                                                  '@A+PC`).',
                                                  'DJNZ Rx, rel: Decrement Register Rx and Jump if Not Zero (perfect '
                                                  'for delay loops!).',
                                                  'CJNE: Compare and Jump if Not Equal (`CJNE A, #data, target`).',
                                                  'SWAP A: Swaps upper and lower 4-bit nibbles of Accumulator A.'],
                          'practical_application': 'DJNZ provides single-instruction hardware loop counters; SWAP A '
                                                   'enables instant BCD nibble processing.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'MOVC (Move Code) is designed to read constants and lookup tables '
                                                     'stored in Code ROM.',
                                      'options': ['MOVX A, @DPTR', 'MOVC A, @A+DPTR', 'MOV A, R0', 'PUSH ACC'],
                                      'question': 'Which 8051 instruction is specifically used to read data from '
                                                  'external Flash ROM / Code Memory?'},
                          'register_state': {   'after': 'A = 54H (0101 0100B)',
                                                'before': 'A = 45H (0100 0101B)',
                                                'operation': 'SWAP A (Opcode: C4H)'},
                          'summary': 'Data Transfer, Arithmetic, Logical, Boolean (Bit-oriented), and Branching '
                                     'instructions with syntax, bytes, and machine cycles.',
                          'title': '8051 Instruction Set Categories & Detailed Operations',
                          'try_it': 'Run 8051 assembly code snippets in the 8051 Learning Workspace.'}]},
    {   'color': '#EC4899',
        'icon': 'fa5s.search-location',
        'id': 'cat_17',
        'title': '17. 8051 ADDRESSING MODES',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8051 ADDRESSING MODES '
                                     'OVERVIEW                             |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  1. IMMEDIATE          : MOV A, #45H          (Data prefixed with '
                                     '#)             |\n'
                                     '|  2. REGISTER           : MOV A, R0            (Operands '
                                     'R0-R7)                    |\n'
                                     '|  3. DIRECT             : MOV A, 30H           (RAM or SFR address '
                                     '30H)           |\n'
                                     '|  4. REGISTER INDIRECT  : MOV A, @R0           (Address stored in R0 or '
                                     'R1)        |\n'
                                     '|  5. INDEXED            : MOVC A, @A+DPTR      (Base DPTR + Offset '
                                     'A)             |\n'
                                     '|  6. RELATIVE           : SJMP LABEL           (Relative offset -128 to '
                                     '+127)     |\n'
                                     '|  7. BIT ADDRESSABLE    : SETB 90H             (Individual bit '
                                     'P1.0)              |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Lookup Table Access:\n'
                                     '`MOV DPTR, #2000H`\n'
                                     '`MOV A, #02H`\n'
                                     '`MOVC A, @A+DPTR` -> Loads 3rd entry of table into A.',
                          'how_it_works': 'Indexed Addressing `MOVC A, @A+DPTR`:\n'
                                          '- If DPTR = 2000H (Table Base Address) and A = 03H (Index 3):\n'
                                          '- Effective Code ROM Address = 2000H + 03H = 2003H.\n'
                                          '- Fetches ROM byte at 2003H into Accumulator A.',
                          'id': '8051_addr_modes',
                          'important_points': [   'Immediate Addressing (#): Data operand prefixed with `#` (e.g. `MOV '
                                                  'A, #45H`).',
                                                  'Direct Addressing: Specifies RAM byte address `00H-7FH` or SFR '
                                                  'address `80H-FFH` directly.',
                                                  'Register Indirect (@): Uses `@R0` or `@R1` as pointers for internal '
                                                  'RAM, or `@DPTR` for external RAM.',
                                                  'Bit Addressing: Operates directly on individual bits in RAM '
                                                  '`20H-2FH` or Bit-addressable SFRs.'],
                          'practical_application': 'Indexed addressing enables 7-segment display lookup tables, '
                                                   'sine-wave synthesis, and key-code translation matrices.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'The `#` hash symbol indicates immediate data (e.g. MOV A, #45H). '
                                                     'Without `#`, MOV A, 45H is direct address 45H.',
                                      'options': [   'The `@` symbol',
                                                     'The `#` symbol',
                                                     'The `$` symbol',
                                                     'The `%` symbol'],
                                      'question': 'What symbol distinguishes Immediate Addressing from Direct '
                                                  'Addressing in 8051 assembly?'},
                          'register_state': {   'after': 'A = 77H',
                                                'before': 'DPTR = 2000H, A = 02H, ROM[2002H] = 77H',
                                                'operation': 'MOVC A, @A+DPTR (Opcode: 93H)'},
                          'summary': 'Exploring the 7 addressing modes of 8051: Immediate (#), Register (Rn), Direct '
                                     '(addr), Register Indirect (@), Indexed (@A+DPTR), Relative (rel), and Bit '
                                     'Addressing.',
                          'title': '8051 Addressing Modes (Immediate, Direct, Indirect, Indexed, Bit)',
                          'try_it': 'Inspect lookup table indexing in the 8051 Reference area.'}]},
    {   'color': '#06B6D4',
        'icon': 'fa5s.clock',
        'id': 'cat_18',
        'title': '18. 8051 TIMERS & COUNTERS',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8051 TMOD REGISTER FORMAT '
                                     '(88H)                            |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|     <-------- TIMER 1 -------->          <-------- TIMER 0 '
                                     '-------->              |\n'
                                     '|  +------+------+------+------+        '
                                     '+------+------+------+------+               |\n'
                                     '|  | GATE | C/T# |  M1  |  M0  |        | GATE | C/T# |  M1  |  M0  '
                                     '|               |\n'
                                     '|  +------+------+------+------+        '
                                     '+------+------+------+------+               |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  Mode 0: 13-Bit Timer           Mode 1: 16-Bit '
                                     'Timer                              |\n'
                                     '|  Mode 2: 8-Bit Auto-Reload      Mode 3: Split '
                                     'Timer                               |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Mode 2 Baud Rate Generator:\n'
                                     '`MOV TMOD, #20H` (Timer 1 Mode 2 Auto-Reload)\n'
                                     '`MOV TH1, #0FDH` (Reload value for 9600 Baud at 11.0592 MHz)\n'
                                     '`SETB TR1`.',
                          'how_it_works': 'Generating 1 ms Delay in Mode 1 (12 MHz Crystal):\n'
                                          'Machine Cycle = 1 us. Required Count N = 1000 us.\n'
                                          'Reload Value = 65536 - 1000 = 64536 = FC18H.\n'
                                          '`MOV TH0, #0FCH`, `MOV TL0, #18H`, `SETB TR0`.',
                          'id': '8051_timer_modes',
                          'important_points': [   'Timer vs Counter: C/T# bit = 0 operates as Timer (clocked by '
                                                  'f_osc/12). C/T# bit = 1 operates as Counter (clocked by T0/T1 pin).',
                                                  'Mode 1 (16-Bit): Uses THx and TLx combined (0000H to FFFFH). '
                                                  'Requires reloading count after overflow.',
                                                  'Mode 2 (8-Bit Auto-Reload): TLx counts 00H to FFH. On overflow, THx '
                                                  'automatically reloads TLx without software intervention!',
                                                  'TCON Register: Controls TR0/TR1 (Start/Stop timer) and TF0/TF1 '
                                                  '(Overflow flags).'],
                          'practical_application': 'Mode 2 Timer 1 is standard across all 8051 applications to '
                                                   'generate precise serial UART baud rates.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'Mode 2 is 8-bit Auto-Reload, automatically refreshing TLx with '
                                                     'THx content upon overflow.',
                                      'options': [   'Mode 0 (13-bit)',
                                                     'Mode 1 (16-bit)',
                                                     'Mode 2 (8-bit Auto-Reload)',
                                                     'Mode 3 (Split)'],
                                      'question': 'Which 8051 timer mode automatically reloads TLx from THx upon '
                                                  'counter overflow?'},
                          'register_state': {   'after': 'TMOD = 20H, TH1 = FDH, TR1 = 1 (Timer 1 running in Mode 2)',
                                                'before': 'TMOD = 00H, TCON = 00H',
                                                'operation': 'MOV TMOD, #20H -> MOV TH1, #0FDH -> SETB TR1'},
                          'summary': 'Configuring TMOD, TCON registers for Mode 0 (13-bit), Mode 1 (16-bit), Mode 2 '
                                     '(8-bit auto-reload), and exact delay timing calculation.',
                          'title': '8051 Timers/Counters (Timer 0 & 1, TMOD, TCON & Delay Generation)',
                          'try_it': 'Calculate timer count values using the 8051 Timer Calculator.'}]},
    {   'color': '#EF4444',
        'icon': 'fa5s.bell',
        'id': 'cat_19',
        'title': '19. 8051 INTERRUPTS',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                     8051 INTERRUPT VECTOR TABLE & '
                                     'PRIORITIES                      |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|   Interrupt Source      Flag     Vector Address    Priority '
                                     '(Default)             |\n'
                                     '|   ------------------    ----     --------------    '
                                     '------------------             |\n'
                                     '|   Reset                 --       0000H             '
                                     'Highest                        |\n'
                                     '|   External Interrupt 0  IE0      0003H             '
                                     '1                              |\n'
                                     '|   Timer 0 Overflow      TF0      000BH             '
                                     '2                              |\n'
                                     '|   External Interrupt 1  IE1      0013H             '
                                     '3                              |\n'
                                     '|   Timer 1 Overflow      TF1      001BH             '
                                     '4                              |\n'
                                     '|   Serial Comm (RI/TI)   RI+TI    0023H             5 '
                                     '(Lowest)                     |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'When INT0# pin (P3.2) goes LOW:\n'
                                     '1. CPU completes current instruction.\n'
                                     '2. Saves PC to Stack.\n'
                                     '3. Jumps to vector address 0003H to execute ISR.',
                          'how_it_works': 'Enabling INT0# and Timer 0 Interrupts:\n'
                                          '`MOV IE, #85H` (1000 0101B -> EA=1, EX0=1, ET0=1).',
                          'id': '8051_interrupt_ie_ip',
                          'important_points': [   'Interrupt Enable (IE - A8H): EA bit (Global Enable IE.7), EX0, ET0, '
                                                  'EX1, ET1, ES.',
                                                  'Interrupt Priority (IP - B8H): Allows setting High (1) or Low (0) '
                                                  'priority levels for each interrupt.',
                                                  'Global Enable EA: Must be set to 1 (`SETB EA`) for any interrupt to '
                                                  'function.'],
                          'practical_application': 'External interrupts INT0#/INT1# handle emergency stop switches and '
                                                   'external encoder pulses.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'External Interrupt 0 (INT0#) jumps directly to vector address '
                                                     '0003H in Code ROM.',
                                      'options': ['0000H', '0003H', '000BH', '0023H'],
                                      'question': 'What is the vector address for 8051 External Interrupt 0 (INT0#)?'},
                          'register_state': {   'after': 'IE = 85H (EA = 1, EX0 = 1, ET0 = 1)',
                                                'before': 'IE = 00H (Interrupts disabled)',
                                                'operation': 'MOV IE, #85H'},
                          'summary': 'Understanding 8051 interrupt sources: INT0#, TF0, INT1#, TF1, RI/TI, Interrupt '
                                     'Enable (IE), and Priority (IP) registers.',
                          'title': '8051 Interrupt Structure (IE, IP & Vector Table)',
                          'try_it': 'Simulate external interrupts on P3.2 in ElectroVerse 8051 Simulator.'}]},
    {   'color': '#3B82F6',
        'icon': 'fa5s.wifi',
        'id': 'cat_20',
        'title': '20. 8051 SERIAL COMMUNICATION',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8051 SCON REGISTER FORMAT '
                                     '(98H)                            |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|   Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit '
                                     '0                   |\n'
                                     '| '
                                     '+-------+-------+-------+-------+-------+-------+-------+-------+                 '
                                     '|\n'
                                     '| | SM0   | SM1   | SM2   | REN   | TB8   | RB8   |  TI   |  RI   '
                                     '|                 |\n'
                                     '| '
                                     '+-------+-------+-------+-------+-------+-------+-------+-------+                 '
                                     '|\n'
                                     '|   Mode Select    Multi   Receive Trans   Recv    Trans   '
                                     'Recv                     |\n'
                                     '|   (01 = Mode 1)  Comm    Enable   Bit 8  Bit 8   Flag    '
                                     'Flag                     |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Receiving a Byte:\n`WAIT_RX: JNB RI, WAIT_RX`\n`MOV A, SBUF`\n`CLR RI`',
                          'how_it_works': "Transmitting Character 'A' via UART:\n"
                                          '```assembly\n'
                                          'MOV SCON, #50H   ; Mode 1, REN=1\n'
                                          'MOV TMOD, #20H   ; Timer 1 Mode 2\n'
                                          'MOV TH1, #0FDH   ; 9600 Baud\n'
                                          'SETB TR1         ; Start Timer 1\n'
                                          "MOV SBUF, #'A'   ; Load character into SBUF\n"
                                          'WAIT: JNB TI, WAIT; Wait until TI = 1\n'
                                          'CLR TI           ; Clear TI flag\n'
                                          '```',
                          'id': '8051_uart_scon',
                          'important_points': [   'SCON (98H): Serial Control Register. Sets SM0/SM1 for Mode 1 (8-bit '
                                                  'UART, variable baud rate).',
                                                  'REN (SCON.4): Receive Enable bit. Must be 1 to allow serial data '
                                                  'reception.',
                                                  'SBUF (99H): Serial Data Buffer. Two physically separate registers '
                                                  '(Write to TX buffer, Read from RX buffer).',
                                                  'TI & RI Flags: Transmit Interrupt (TI) set when byte transmitted; '
                                                  'Receive Interrupt (RI) set when byte received.'],
                          'practical_application': '8051 UART serial port connects directly to PC COM ports via MAX232 '
                                                   'or wireless Bluetooth HC-05 modules.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'REN (Receive Enable) bit SCON.4 must be set to 1 (`SETB REN`) to '
                                                     'enable data reception on P3.0 RXD pin.',
                                      'options': ['REN (SCON.4)', 'TI (SCON.1)', 'RI (SCON.0)', 'SM0 (SCON.7)'],
                                      'question': 'Which bit in the SCON register must be set to 1 to enable serial '
                                                  'reception on RXD pin?'},
                          'register_state': {   'after': 'SBUF = 41H, TI = 1 (Transmit complete)',
                                                'before': 'SBUF = 00H, TI = 0, RI = 0',
                                                'operation': "MOV SBUF, #'A' followed by serial transmission"},
                          'summary': 'Full-duplex UART serial mode configuration, SCON register format, SBUF buffer, '
                                     'and baud rate generation.',
                          'title': '8051 Serial UART Communication (SCON, SBUF & PCON)',
                          'try_it': 'Run the Serial UART Baud animator in the Simulation tab.'}]},
    {   'color': '#10B981',
        'icon': 'fa5s.microchip',
        'id': 'cat_21',
        'title': '21. 8051 INTERFACING & PROGRAMMING',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8051 TO 16x2 LCD HARDWARE '
                                     'INTERFACING                      |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|    8051 MCU                                        16x2 HD44780 '
                                     'LCD               |\n'
                                     '|    +---------+                                     '
                                     '+---------------+              |\n'
                                     '|    | Port 1  |====================================>| D0 - D7       '
                                     '|              |\n'
                                     '|    | P2.0    |------------------------------------>| RS (Reg Sel)  '
                                     '|              |\n'
                                     '|    | P2.1    |------------------------------------>| RW '
                                     '(Read/Write|              |\n'
                                     '|    | P2.2    |------------------------------------>| EN (Enable)   '
                                     '|              |\n'
                                     '|    +---------+                                     '
                                     '+---------------+              |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': "Displaying 'A':\n"
                                     "`MOV P1, #'A'`\n"
                                     '`SETB P2.0` (RS = 1 Data)\n'
                                     '`CLR P2.1` (RW = 0 Write)\n'
                                     '`SETB P2.2` -> `CLR P2.2` (Enable pulse).',
                          'how_it_works': 'Sending Command 01H (Clear LCD):\n'
                                          '`MOV P1, #01H` (Data bus)\n'
                                          '`CLR P2.0` (RS = 0 Command)\n'
                                          '`CLR P2.1` (RW = 0 Write)\n'
                                          '`SETB P2.2` -> `CLR P2.2` (Enable pulse).',
                          'id': '8051_lcd_keypad',
                          'important_points': [   'LCD Control Lines: RS = 0 (Command), RS = 1 (Data); RW = 0 (Write); '
                                                  'EN = Strobe pulse (High-to-Low).',
                                                  'LCD Initialization Commands: `38H` (8-bit 2-line mode), `0EH` '
                                                  '(Display ON, cursor ON), `01H` (Clear screen).',
                                                  'Matrix Keypad Scanning: Ground 1 row at a time and read column '
                                                  'inputs to detect pressed key.'],
                          'practical_application': '16x2 LCD displays and 4x4 matrix keypads form the user interface '
                                                   'for ATMs, security systems, and industrial equipment.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'RS = 1 selects the LCD Data Register to print ASCII characters; '
                                                     'RS = 0 selects the Command Register for setup.',
                                      'options': [   'RS = 1 (Data Register)',
                                                     'RS = 0 (Command Register)',
                                                     'RS = High Z',
                                                     'RS = Toggle'],
                                      'question': 'What logic state must the RS (Register Select) pin be set to when '
                                                  'sending ASCII data characters to a 16x2 LCD?'},
                          'register_state': {   'after': "P1 = 41H, LCD displays character 'A'",
                                                'before': 'P1 = 00H, P2 = 00H',
                                                'operation': "Send LCD Data Byte 'A' (41H)"},
                          'summary': 'Hardware connections and assembly routines for HD44780 16x2 LCD character '
                                     'displays and 4x4 matrix keypads.',
                          'title': 'Interfacing 16x2 LCD, Matrix Keypad & ADC0804 with 8051',
                          'try_it': 'Test 16x2 LCD commands in ElectroVerse 8051 Interfacing Lab.'}]},
    {   'color': '#8B5CF6',
        'icon': 'fa5s.robot',
        'id': 'cat_22',
        'title': '22. MICROCONTROLLER APPLICATIONS',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                   EMBEDDED MICROCONTROLLER APPLICATION '
                                     'SPECTRUM                   |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  +-------------------+   +--------------------+   '
                                     '+----------------------------+  |\n'
                                     '|  | AUTOMOTIVE ECUs   |   | INDUSTRIAL CONTROL |   | SMART IOT & HOME '
                                     'AUTOMATION|  |\n'
                                     '|  | Engine Control    |   | PLC Controllers    |   | Smart Thermostats          '
                                     '|  |\n'
                                     '|  | ABS Braking       |   | Motor Drivers      |   | Wireless Sensor Nodes      '
                                     '|  |\n'
                                     '|  | Airbag Deployment |   | Conveyor Belts     |   | Wearable Health Monitors   '
                                     '|  |\n'
                                     '|  +-------------------+   +--------------------+   '
                                     '+----------------------------+  |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Smart Thermostat: ADC reads thermistor voltage -> MCU converts voltage to '
                                     'Temperature -> Compares setpoint -> Triggers relay to turn AC ON/OFF.',
                          'how_it_works': 'PWM Motor Speed Control:\n'
                                          'Timer generates a variable duty cycle output pin. 25% duty cycle = 25% '
                                          'motor speed; 75% duty cycle = 75% motor speed.',
                          'id': 'mcu_realworld_apps',
                          'important_points': [   'Automotive Systems: CAN bus interconnected microcontrollers manage '
                                                  'engine timing, ABS braking, and infotainment.',
                                                  'Robotics & Motor Control: PWM (Pulse Width Modulation) timers '
                                                  'control servo angles and stepper motor speeds.',
                                                  'IoT Sensor Nodes: Ultra-low-power microcontrollers read analog '
                                                  'sensors, package MQTT packets, and transmit over Wi-Fi/LoRa.'],
                          'practical_application': 'Embedded microcontrollers power over 30 billion devices '
                                                   'manufactured globally each year across consumer, medical, '
                                                   'aerospace, and defense industries.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'Pulse Width Modulation (PWM) varies the high-time ratio of a '
                                                     'digital square wave to control effective output power.',
                                      'options': [   'Amplitude Modulation (AM)',
                                                     'Pulse Width Modulation (PWM)',
                                                     'Frequency Shift Keying (FSK)',
                                                     'Phase Modulation (PM)'],
                                      'question': 'Which signal modulation technique is standard in microcontrollers '
                                                  'for controlling motor speed and LED brightness?'},
                          'register_state': {   'after': 'Port Pin High -> Relay ON -> Cooling activated',
                                                'before': 'ADC Voltage = 2.5V (Temp = 28°C), Setpoint = 24°C',
                                                'operation': 'MCU Comparison & Relay Output Trigger'},
                          'summary': 'Real-world engineering applications of microcontrollers in automotive ECUs, '
                                     'robotics, smart IoT sensors, and industrial automation.',
                          'title': 'Embedded Systems, Robotics & IoT Applications',
                          'try_it': 'Explore stepper motor and PWM visualizers in the Simulation tab.'}]},
    {   'color': '#06B6D4',
        'icon': 'fa5s.microchip',
        'id': 'cat_8086',
        'title': '23. INTEL 8086 MICROPROCESSOR',
        'topics': [   {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8086 MICROPROCESSOR '
                                     'OVERVIEW                         |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  +--------------------+     +---------------------+     '
                                     '+----------------------+  |\n'
                                     '|  | 16-BIT ALU         |     | 20-BIT ADDRESS BUS  |     | 16-BIT DATA BUS      '
                                     '|  |\n'
                                     '|  | Arithmetic/Logical |     | 1 MB Physical Memory|     | Bidirectional Data   '
                                     '|  |\n'
                                     '|  +--------------------+     +---------------------+     '
                                     '+----------------------+  |\n'
                                     '|            ^                           ^                           '
                                     '^              |\n'
                                     '|            '
                                     '+---------------------------+---------------------------+              |\n'
                                     '|                                        '
                                     'v                                          |\n'
                                     '|  '
                                     '+-----------------------------------------------------------------------------+  '
                                     '|\n'
                                     '|  | DUAL-CORE PIPELINED ARCHITECTURE: BIU (Bus Interface) + EU (Execution)      '
                                     '|  |\n'
                                     '|  '
                                     '+-----------------------------------------------------------------------------+  '
                                     '|\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Executing MOV AX, 1234H:\n'
                                     '1. BIU fetches 3-byte opcode [B8 34 12] into 6-byte Queue.\n'
                                     '2. EU pulls opcode from Queue, decodes 16-bit immediate load.\n'
                                     '3. AL receives 34H (low byte), AH receives 12H (high byte) -> AX = 1234H.',
                          'how_it_works': 'The 8086 uses a dual-processing pipeline. While the Execution Unit (EU) '
                                          'decodes and executes an instruction, the Bus Interface Unit (BIU) fetches '
                                          'upcoming instruction bytes from memory into a 6-byte FIFO queue.',
                          'id': '8086_intro',
                          'important_points': [   '16-bit HMOS Microprocessor introduced by Intel in 1978 in a 40-pin '
                                                  'Dual In-line Package (DIP).',
                                                  '20-bit Address Bus: Addresses up to 2^20 = 1,048,576 bytes = 1 MB '
                                                  'of physical memory.',
                                                  '16-bit Data Bus: Transfers 16-bit words (or 8-bit bytes) in a '
                                                  'single bus cycle.',
                                                  'Clock Frequencies: 5 MHz (8086), 8 MHz (8086-2), and 10 MHz '
                                                  '(8086-1).',
                                                  'Instruction Prefetch Queue: 6-byte instruction queue in Bus '
                                                  'Interface Unit enables instruction pipelining.',
                                                  'Operating Modes: Minimum Mode (single CPU) and Maximum Mode '
                                                  '(multiprocessor with 8087 coprocessor).'],
                          'practical_application': 'Formed the foundational x86 architecture for IBM PC/XT computers, '
                                                   'industrial automation controllers, avionics systems, and embedded '
                                                   'computing.',
                          'quiz': {   'correct': 2,
                                      'explanation': '8086 has a 20-bit address bus: 2^20 = 1,048,576 bytes = 1 '
                                                     'Megabyte.',
                                      'options': ['64 KB', '512 KB', '1 MB (1,048,576 bytes)', '4 GB'],
                                      'question': 'What is the physical memory capacity addressable by the Intel 8086 '
                                                  'microprocessor?'},
                          'register_state': {   'after': 'AX = 1234H, IP = 0103H, Flags = Unchanged',
                                                'before': 'AX = 0000H, IP = 0100H, CS = 1000H',
                                                'operation': 'MOV AX, 1234H (Opcode: B8 34 12)'},
                          'summary': 'Overview of Intel 8086: 16-bit architecture, 20-bit address bus (1 MB physical '
                                     'RAM space), features, comparison with 8085, and industrial applications.',
                          'title': '1. Introduction to 8086 Microprocessor',
                          'try_it': 'Compare 8086 16-bit register execution with 8085 8-bit register execution in the '
                                    'Learn workstation.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8086 INTERNAL '
                                     'ARCHITECTURE                           |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  '
                                     '+-----------------------------------------------------------------------------+  '
                                     '|\n'
                                     '|  | BUS INTERFACE UNIT (BIU)                                                    '
                                     '|  |\n'
                                     '|  | +------------------+   +-------------------+   +-------------------------+  '
                                     '|  |\n'
                                     '|  | | SEGMENT REGS     |   | INSTR POINTER (IP)|   | 6-BYTE INSTRUCTION QUEUE|  '
                                     '|  |\n'
                                     '|  | | CS, DS, SS, ES   |   | (16-bit)          |   | [B1][B2][B3][B4][B5][B6]|  '
                                     '|  |\n'
                                     '|  | +--------+---------+   +---------+---------+   +------------+------------+  '
                                     '|  |\n'
                                     '|  |          |                       |                          v               '
                                     '|  |\n'
                                     '|  |          +----------+------------+                To EU Control Unit        '
                                     '|  |\n'
                                     '|  |                     v                                                       '
                                     '|  |\n'
                                     '|  |            +------------------+                                             '
                                     '|  |\n'
                                     '|  |            | 20-BIT BUS ADDER |====> 20-Bit Address Bus (A19-A0)            '
                                     '|  |\n'
                                     '|  |            +------------------+                                             '
                                     '|  |\n'
                                     '|  '
                                     '+-----------------------------------------------------------------------------+  '
                                     '|\n'
                                     '|                                     || Internal '
                                     'Bus                               |\n'
                                     '|  '
                                     '+----------------------------------v------------------------------------------+  '
                                     '|\n'
                                     '|  | EXECUTION UNIT (EU)                                                         '
                                     '|  |\n'
                                     '|  | +------------------+   +-------------------+   +-------------------------+  '
                                     '|  |\n'
                                     '|  | | GENERAL REGS     |   | INDEX/POINTER REGS|   | 16-BIT ALU & FLAGS      |  '
                                     '|  |\n'
                                     '|  | | AX, BX, CX, DX   |   | SP, BP, SI, DI    |   | Status & Control Flags  |  '
                                     '|  |\n'
                                     '|  | +------------------+   +-------------------+   +-------------------------+  '
                                     '|  |\n'
                                     '|  '
                                     '+-----------------------------------------------------------------------------+  '
                                     '|\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Executing sequence: MOV AX, 5  |  ADD AX, 10\n'
                                     '- While EU computes 5+10 in ALU, BIU fetches opcode for next instruction into '
                                     'Queue[0..1].',
                          'how_it_works': 'Pipelined Execution Sequence:\n'
                                          '1. T1-T4: EU executes ADD AX, BX.\n'
                                          '2. Simultaneously: BIU fetches next instruction byte at CS:IP+2 and pushes '
                                          'into 6-byte queue.\n'
                                          '3. Upon instruction completion, EU immediately reads next byte from Queue '
                                          'without waiting for memory fetch.',
                          'id': '8086_architecture',
                          'important_points': [   'Dual Independent Processing Units: BIU (Bus Interface Unit) handles '
                                                  'bus activity; EU (Execution Unit) decodes and executes '
                                                  'instructions.',
                                                  'Bus Interface Unit (BIU): Contains CS, DS, SS, ES segment '
                                                  'registers, 16-bit IP, 6-byte FIFO Queue, and 20-bit address adder.',
                                                  'Execution Unit (EU): Contains 16-bit ALU, 16-bit Flag Register, '
                                                  'Control Unit, AX/BX/CX/DX registers, and SP/BP/SI/DI index '
                                                  'registers.',
                                                  'Instruction Prefetching: BIU fetches next instruction bytes from '
                                                  'memory whenever 2 bytes in the queue become empty.',
                                                  'Pipelining Advantage: Eliminates fetch latency because EU receives '
                                                  'prefetched instruction bytes directly from the internal queue.'],
                          'practical_application': 'Instruction queue pipelining dramatically increased execution '
                                                   'speed compared to 8085 non-pipelined single-bus architecture.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'The 6-byte Queue prefetches instructions from memory while the '
                                                     'EU executes current instructions, implementing pipelining.',
                                      'options': [   'To store memory addresses',
                                                     'To prefetch instruction bytes and enable pipelining',
                                                     'To hold ALU calculation overflow',
                                                     'To store stack pointer offsets'],
                                      'question': 'What is the primary function of the 6-byte Instruction Queue in the '
                                                  '8086 BIU?'},
                          'register_state': {   'after': 'Queue = [B8 05 00 05 0A 00], IP = 0106H, EU ready for '
                                                         'instant execution',
                                                'before': 'Queue = Empty, IP = 0100H',
                                                'operation': 'BIU Prefetch 6 Bytes into Queue'},
                          'summary': 'Internal dual-unit architecture: Bus Interface Unit (BIU) and Execution Unit '
                                     '(EU), instruction prefetching, and pipelined execution.',
                          'title': '2. 8086 Architecture & BIU/EU Pipelining',
                          'try_it': 'Observe how BIU and EU operate asynchronously in 8086 architecture diagrams.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8086 REGISTER '
                                     'ARCHITECTURE                           |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  GENERAL PURPOSE REGISTERS (16-Bit / 8-Bit)   SEGMENT REGISTERS '
                                     '(16-Bit)          |\n'
                                     '|  +-------------------+-------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|  | AH (8)            | AL (8)            | AX | CS (Code Segment)              '
                                     '|  |\n'
                                     '|  +-------------------+-------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|  | BH (8)            | BL (8)            | BX | DS (Data Segment)              '
                                     '|  |\n'
                                     '|  +-------------------+-------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|  | CH (8)            | CL (8)            | CX | SS (Stack Segment)             '
                                     '|  |\n'
                                     '|  +-------------------+-------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|  | DH (8)            | DL (8)            | DX | ES (Extra Segment)             '
                                     '|  |\n'
                                     '|  +-------------------+-------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  POINTER & INDEX REGISTERS (16-Bit)           SPECIAL CONTROL '
                                     'REGISTERS           |\n'
                                     '|  +---------------------------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|  | SP (Stack Pointer)                    |    | IP (Instruction Pointer)       '
                                     '|  |\n'
                                     '|  +---------------------------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|  | BP (Base Pointer)                     |    | FLAGS Register (16-Bit)        '
                                     '|  |\n'
                                     '|  +---------------------------------------+    '
                                     '+--------------------------------+  |\n'
                                     '|  | SI (Source Index)                     '
                                     '|                                        |\n'
                                     '|  '
                                     '+---------------------------------------+                                        '
                                     '|\n'
                                     '|  | DI (Destination Index)                '
                                     '|                                        |\n'
                                     '|  '
                                     '+---------------------------------------+                                        '
                                     '|\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'MOV AX, 1234H -> AH = 12H, AL = 34H.\n'
                                     'MOV CL, 4  |  SHL AX, CL -> Shifts 16-bit AX left by 4 bit positions using CL '
                                     'count register.',
                          'how_it_works': 'Register Pair Split: AX, BX, CX, DX can be accessed as full 16-bit '
                                          'registers or as separate 8-bit high (AH, BH, CH, DH) and low (AL, BL, CL, '
                                          'DL) registers.',
                          'id': '8086_registers',
                          'important_points': [   'AX (Accumulator): Used in arithmetic, logic, I/O operations '
                                                  '(IN/OUT), and string instructions.',
                                                  'BX (Base Register): Used as base register to hold memory offset '
                                                  'addresses in indirect addressing.',
                                                  'CX (Count Register): Loop counter for LOOP instructions, '
                                                  'shift/rotate count in CL, string REP count.',
                                                  'DX (Data Register): Holds upper 16-bit word in 32-bit MUL/DIV '
                                                  'operations, I/O port address for IN/OUT.',
                                                  'CS (Code Segment): Points to base of 64 KB segment containing '
                                                  'executable code instructions.',
                                                  'DS (Data Segment): Points to base of 64 KB segment containing '
                                                  'program data and variables.',
                                                  'SS (Stack Segment): Points to base of 64 KB stack memory area.',
                                                  'ES (Extra Segment): Points to base of extra data segment (used for '
                                                  'string operations).',
                                                  'SP (Stack Pointer): Holds 16-bit offset of top of stack (SS:SP).',
                                                  'BP (Base Pointer): Holds offset in stack segment for function '
                                                  'parameters.',
                                                  'SI (Source Index): Holds source data offset for string operations '
                                                  '(DS:SI).',
                                                  'DI (Destination Index): Holds destination data offset for string '
                                                  'operations (ES:DI).',
                                                  'IP (Instruction Pointer): Holds offset of next instruction byte to '
                                                  'fetch in Code Segment (CS:IP).'],
                          'practical_application': 'Dedicated register roles allow compact instruction encoding (e.g. '
                                                   'LOOP uses CX implicitly without specifying register byte).',
                          'quiz': {   'correct': 2,
                                      'explanation': 'CX (Count Register) is implicitly decremented by the LOOP '
                                                     'instruction until CX = 0.',
                                      'options': ['AX', 'BX', 'CX', 'DX'],
                                      'question': 'Which 8086 register is used as an implicit loop counter by the LOOP '
                                                  'instruction?'},
                          'register_state': {   'after': 'AX = 5678H, AH = 56H, AL = 78H',
                                                'before': 'AX = 0000H, AH = 00H, AL = 00H',
                                                'operation': 'MOV AX, 5678H'},
                          'summary': 'Complete 8086 register architecture: 16-bit General-Purpose (AX, BX, CX, DX), '
                                     'Segment (CS, DS, SS, ES), Pointers (SP, BP), Indexes (SI, DI), IP, and Flags.',
                          'title': '3. 8086 Register Organization',
                          'try_it': 'Inspect register values in 16-bit mode in the Learn Workstation.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8086 16-BIT FLAG REGISTER '
                                     'FORMAT                     |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  15  14  13  12  11   10   9    8    7    6   5   4   3   2   1   '
                                     '0              |\n'
                                     '| '
                                     '+---+---+---+---+----+----+----+----+----+----+---+---+---+---+---+---+           '
                                     '|\n'
                                     '| | X | X | X | X | OF | DF | IF | TF | SF | ZF | X | AF| X | PF| X | '
                                     'CF|           |\n'
                                     '| '
                                     '+---+---+---+---+----+----+----+----+----+----+---+---+---+---+---+---+           '
                                     '|\n'
                                     '|                   |    |    |    |    |    |      |       |       '
                                     '|              |\n'
                                     '|                   |    |    |    |    |    |      |       |       +--> '
                                     'Carry     |\n'
                                     '|                   |    |    |    |    |    |      |       +----------> '
                                     'Parity    |\n'
                                     '|                   |    |    |    |    |    |      +------------------> Aux '
                                     'Carry |\n'
                                     '|                   |    |    |    |    |    +-------------------------> '
                                     'Zero      |\n'
                                     '|                   |    |    |    |    +------------------------------> '
                                     'Sign      |\n'
                                     '|                   |    |    |    +-----------------------------------> '
                                     'Trap      |\n'
                                     '|                   |    |    +----------------------------------------> '
                                     'Interrupt |\n'
                                     '|                   |    +---------------------------------------------> '
                                     'Direction |\n'
                                     '|                   +--------------------------------------------------> '
                                     'Overflow  |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': "MOV AL, 7FH (+127)  |  ADD AL, 01H (+1) -> Result AL = 80H (-128 in signed 2's "
                                     'complement).\n'
                                     'Flags set: SF = 1 (MSB=1), ZF = 0, OF = 1 (Signed overflow from +127 to -128).',
                          'how_it_works': 'Status flags are set automatically by the ALU based on result values. '
                                          'Control flags are set or cleared by specific instructions (STI, CLI, CLD, '
                                          'STD).',
                          'id': '8086_flag_register',
                          'important_points': [   '16-bit register with 9 active flags (6 Status Flags + 3 Control '
                                                  'Flags).',
                                                  'CF (Carry Flag, Bit 0): Set if arithmetic operation generates '
                                                  'carry/borrow out of MSB.',
                                                  'PF (Parity Flag, Bit 2): Set if lower byte of result contains EVEN '
                                                  'number of 1-bits.',
                                                  'AF (Auxiliary Carry Flag, Bit 4): Set if carry generated from bit 3 '
                                                  'to bit 4 (BCD arithmetic).',
                                                  'ZF (Zero Flag, Bit 6): Set if result of operation is 0.',
                                                  'SF (Sign Flag, Bit 7): Set equal to MSB of result (1 = Negative, 0 '
                                                  '= Positive).',
                                                  'TF (Trap Flag, Bit 8, Control): Enables single-step debugging mode '
                                                  'when set to 1.',
                                                  'IF (Interrupt Flag, Bit 9, Control): Enables maskable INTR hardware '
                                                  'interrupts when set (STI/CLI).',
                                                  'DF (Direction Flag, Bit 10, Control): Controls auto-increment '
                                                  '(DF=0, CLD) or auto-decrement (DF=1, STD) for string ops.',
                                                  "OF (Overflow Flag, Bit 11, Status): Set if signed 2's complement "
                                                  'arithmetic result exceeds valid range (-32768 to +32767).'],
                          'practical_application': 'Trap Flag (TF) is used by debugger software (GDB, DEBUG.EXE) to '
                                                   'execute code line-by-line via Interrupt Type 1.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'Direction Flag (DF) determines string pointer movement: DF=0 '
                                                     '(CLD) auto-increments SI/DI; DF=1 (STD) auto-decrements.',
                                      'options': [   'Trap Flag (TF)',
                                                     'Interrupt Flag (IF)',
                                                     'Direction Flag (DF)',
                                                     'Overflow Flag (OF)'],
                                      'question': 'Which flag in 8086 controls string instruction SI/DI auto-increment '
                                                  'vs auto-decrement?'},
                          'register_state': {   'after': 'AL = 80H, SF = 1, ZF = 0, PF = 0, CF = 0, OF = 1',
                                                'before': 'AL = 7FH, Flags = 0000H',
                                                'operation': 'ADD AL, 01H -> Result = 80H'},
                          'summary': 'Comprehensive guide to 8086 16-bit Flag Register: 6 Status Flags (CF, PF, AF, '
                                     'ZF, SF, OF) and 3 Control Flags (TF, IF, DF).',
                          'title': '4. 8086 Flag Register (Status & Control Flags)',
                          'try_it': 'Test flag updates after ADD and SUB instructions in the simulator.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                     8086 1 MB SEGMENTED MEMORY '
                                     'ARCHITECTURE                       |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  PHYSICAL MEMORY (1 MB)                 ACTIVE 64 KB LOGICAL '
                                     'SEGMENTS             |\n'
                                     '|  FFFFFH '
                                     '+-------------------+                                                     |\n'
                                     '|         |                   |           '
                                     '+----------------------------------+      |\n'
                                     '|  E0000H | EXTRA SEGMENT     |<==========| ES (Extra Segment)   = E000H     '
                                     '|      |\n'
                                     '|         | (64 KB)           |           '
                                     '+----------------------------------+      |\n'
                                     '|  D0000H '
                                     '+-------------------+                                                     |\n'
                                     '|         | STACK SEGMENT     |<==========| SS (Stack Segment)   = C000H     '
                                     '|      |\n'
                                     '|  C0000H | (64 KB)           |           '
                                     '+----------------------------------+      |\n'
                                     '|         '
                                     '+-------------------+                                                     |\n'
                                     '|  B0000H | DATA SEGMENT      |<==========| DS (Data Segment)    = A000H     '
                                     '|      |\n'
                                     '|         | (64 KB)           |           '
                                     '+----------------------------------+      |\n'
                                     '|  A0000H '
                                     '+-------------------+                                                     |\n'
                                     '|         | CODE SEGMENT      |<==========| CS (Code Segment)    = 1000H     '
                                     '|      |\n'
                                     '|  10000H | (64 KB)           |           '
                                     '+----------------------------------+      |\n'
                                     '|  00000H '
                                     '+-------------------+                                                     |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Example 1 (CS:IP): CS = 1000H, IP = 0200H -> Physical Address = 10000H + 0200H = '
                                     '10200H.\n'
                                     'Example 2 (DS:BX): DS = 3000H, BX = 0100H -> Physical Address = 30000H + 0100H = '
                                     '30100H.\n'
                                     'Example 3 (SS:SP): SS = 5000H, SP = 2000H -> Physical Address = 50000H + 2000H = '
                                     '52000H.',
                          'how_it_works': 'Physical Address Calculation Step-by-Step:\n'
                                          '1. Take 16-bit Segment Register value (e.g. CS = 2000H).\n'
                                          '2. Shift Left by 4 bits (multiply by 10H hexadecimal): 2000H -> 20000H.\n'
                                          '3. Add 16-bit Offset Register value (e.g. IP = 0150H): 20000H + 0150H = '
                                          '20150H Physical Address.',
                          'id': '8086_memory_org',
                          'important_points': [   '1 MB Address Space: 20-bit address bus generates physical addresses '
                                                  'from 00000H to FFFFFH.',
                                                  'Logical Segmentation: 1 MB memory divided into 64 KB segments to '
                                                  'allow 16-bit registers to address 1 MB.',
                                                  'Four Active Segments: Code Segment (CS), Data Segment (DS), Stack '
                                                  'Segment (SS), Extra Segment (ES).',
                                                  'Segment Base Address: 16-bit segment register value shifted left by '
                                                  '4 bits (multiplied by 16).',
                                                  'Offset Address: 16-bit distance from segment base address (0000H to '
                                                  'FFFFH).',
                                                  'Physical Address Formula: Physical Address = (Segment Register * '
                                                  '10H) + Offset Register.'],
                          'practical_application': 'Segmentation allows relocatable code: program modules can be moved '
                                                   'anywhere in 1 MB memory simply by changing segment register base '
                                                   'values.',
                          'quiz': {   'correct': 0,
                                      'explanation': 'Physical Address = (2000H * 10H) + 0400H = 20000H + 0400H = '
                                                     '20400H.',
                                      'options': ['20400H', '20040H', '24000H', '02400H'],
                                      'question': 'What is the 20-bit physical address generated when CS = 2000H and '
                                                  'IP = 0400H?'},
                          'register_state': {   'after': 'CS Shifted = 20000H, IP = 0150H, 20-Bit Physical Address = '
                                                         '20150H',
                                                'before': 'CS = 2000H, IP = 0150H',
                                                'operation': 'Physical Address Calculation: (CS * 10H) + IP'},
                          'summary': '1 MB memory segmentation, Segment:Offset concept, and step-by-step physical '
                                     'address calculation formula.',
                          'title': '5. Memory Organization & Physical Address Calculation',
                          'try_it': 'Calculate physical address for CS=4000H, IP=0500H in your notebook.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8086 ADDRESSING MODES '
                                     'SPECTRUM                             |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  1. Immediate Addressing     : MOV AX, 1234H       (Data in '
                                     'instruction)        |\n'
                                     '|  2. Register Addressing      : MOV AX, BX          (Operand in '
                                     'register)        |\n'
                                     '|  3. Direct Addressing        : MOV AX, [2050H]     (Offset in '
                                     'instruction)      |\n'
                                     '|  4. Register Indirect        : MOV AX, [BX]        (Offset in '
                                     'BX/BP/SI/DI)      |\n'
                                     '|  5. Based Addressing         : MOV AX, [BX + 08H]  (Offset = Base + '
                                     'Disp)       |\n'
                                     '|  6. Indexed Addressing       : MOV AX, [SI + 04H]  (Offset = Index + '
                                     'Disp)      |\n'
                                     '|  7. Based-Indexed            : MOV AX, [BX + SI]   (Offset = Base + '
                                     'Index)      |\n'
                                     '|  8. Based-Indexed + Disp     : MOV AX, [BX+SI+04H] (Offset = '
                                     'Base+Index+Disp)    |\n'
                                     '|  9. Relative Addressing      : JMP SHORT LABEL     (Offset relative to '
                                     'IP)      |\n'
                                     '| 10. Implied Addressing       : CLC                 (Operand implicit in '
                                     'opcode) |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'MOV AX, [BX + SI + 04H]:\n'
                                     '- Reads 16-bit word from physical address (DS*10H + BX + SI + 4) into AX.',
                          'how_it_works': 'Effective Address (EA) Computation for Based-Indexed with Displacement:\n'
                                          'Given DS = 2000H, BX = 0100H, SI = 0050H, Disp = 0008H:\n'
                                          '1. EA = BX + SI + Disp = 0100H + 0050H + 0008H = 0158H.\n'
                                          '2. Physical Address = (DS * 10H) + EA = 20000H + 0158H = 20158H.',
                          'id': '8086_addressing_modes',
                          'important_points': [   'Immediate: Constant data provided directly in instruction (e.g. MOV '
                                                  'AL, 55H).',
                                                  'Register: Both source and destination operands are registers (e.g. '
                                                  'MOV AX, CX).',
                                                  'Direct: 16-bit offset address stated directly in brackets (e.g. MOV '
                                                  'AX, [1000H]).',
                                                  'Register Indirect: Memory offset stored in BX, BP, SI, or DI (e.g. '
                                                  'MOV AL, [BX]). Default segment is DS for BX/SI/DI, SS for BP.',
                                                  'Based: Effective Address = Base Register (BX or BP) + Displacement '
                                                  '(e.g. MOV AX, [BX + 10H]).',
                                                  'Indexed: Effective Address = Index Register (SI or DI) + '
                                                  'Displacement (e.g. MOV AX, [SI + 06H]).',
                                                  'Based-Indexed: Effective Address = Base Register + Index Register '
                                                  '(e.g. MOV AX, [BX + SI]).',
                                                  'Based-Indexed with Displacement: Effective Address = Base Register '
                                                  '+ Index Register + Displacement (e.g. MOV AX, [BX + SI + 08H]).',
                                                  'Relative: Target address is offset relative to Instruction Pointer '
                                                  '(IP) for jump instructions (e.g. JZ AHEAD).',
                                                  'Implied: Operand is implicitly defined in opcode (e.g. CLC clears '
                                                  'Carry Flag).'],
                          'practical_application': 'Based-indexed with displacement addressing is essential for '
                                                   'accessing 2D arrays, structure fields, and compiler stack frames.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'When Base Pointer (BP) is used in an effective address, the '
                                                     'default segment register is Stack Segment (SS).',
                                      'options': ['DS:BP', 'SS:BP', 'CS:BP', 'ES:BP'],
                                      'question': 'Which register pair is used as default segment:offset for '
                                                  'instruction MOV AX, [BP + SI]?'},
                          'register_state': {   'after': 'Effective Address = 0240H, Physical Address = 10240H, AX '
                                                         'loaded with word at 10240H',
                                                'before': 'DS = 1000H, BX = 0200H, SI = 0030H',
                                                'operation': 'MOV AX, [BX + SI + 10H]'},
                          'summary': 'Detailed breakdown of all 8086 addressing modes: Immediate, Register, Direct, '
                                     'Register Indirect, Based, Indexed, Based-Indexed, Displacement, Relative, and '
                                     'Implied.',
                          'title': '6. 8086 Addressing Modes',
                          'try_it': 'Practice calculating Effective Address for MOV AX, [BX + DI + 02H].'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8086 INSTRUCTION SET '
                                     'CATEGORIES                      |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  1. DATA TRANSFER     : MOV, PUSH, POP, XCHG, IN, OUT, LEA, LDS, '
                                     'LES              |\n'
                                     '|  2. ARITHMETIC        : ADD, ADC, SUB, SBB, INC, DEC, CMP, MUL, IMUL, DIV, '
                                     'IDIV,NEG|\n'
                                     '|  3. LOGICAL           : AND, OR, XOR, NOT, '
                                     'TEST                                   |\n'
                                     '|  4. SHIFT & ROTATE    : SHL/SAL, SHR, SAR, ROL, ROR, RCL, '
                                     'RCR                     |\n'
                                     '|  5. BRANCH / CONTROL  : JMP, CALL, RET, LOOP, JZ, JNZ, JC, JNC, INT, '
                                     'IRET          |\n'
                                     '|  6. STRING INSTRUCTIONS: MOVS, LODS, STOS, CMPS, SCAS, REP, REPE, '
                                     'REPNE             |\n'
                                     '|  7. PROCESSOR CONTROL : NOP, HLT, WAIT, LOCK, STI, CLI, CLC, STC, CMC, CLD, '
                                     'STD     |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'String Copy Program:\n'
                                     '`LEA SI, SRC_BUF`\n'
                                     '`LEA DI, DST_BUF`\n'
                                     '`MOV CX, 100`\n'
                                     '`CLD`\n'
                                     '`REP MOVSB` -> Automatically copies 100 bytes from DS:SI to ES:DI in 1 line!',
                          'how_it_works': 'LEA vs MOV Example:\n'
                                          '`LEA SI, [BX + 10H]` -> Loads calculated offset (BX+10H) directly into SI '
                                          'register without accessing memory data.\n'
                                          '`MOV SI, [BX + 10H]` -> Accesses memory data at address (BX+10H) and loads '
                                          'value into SI.',
                          'id': '8086_instruction_set',
                          'important_points': [   'Data Transfer: MOV (copy), PUSH/POP (stack), XCHG (swap), IN/OUT '
                                                  '(I/O ports), LEA (Load Effective Address), LDS/LES (Load Segment & '
                                                  'Reg).',
                                                  'Arithmetic: ADD/ADC, SUB/SBB, INC/DEC, CMP (compare), MUL/IMUL '
                                                  '(unsigned/signed multiply), DIV/IDIV (unsigned/signed divide), NEG '
                                                  "(2's complement).",
                                                  'Logical: AND (masking), OR (combine bits), XOR (clear register), '
                                                  "NOT (1's complement), TEST (non-destructive AND for flags).",
                                                  'Shift & Rotate: SHL/SAL (shift left), SHR (logical right), SAR '
                                                  '(arithmetic right preserves sign), ROL/ROR (rotate), RCL/RCR '
                                                  '(rotate through carry).',
                                                  'Branch & Control: JMP (unconditional), CALL/RET (subroutines), LOOP '
                                                  '(decrement CX and jump if CX!=0), JZ/JNZ/JC/JNC (conditional '
                                                  'jumps), INT/IRET (interrupts).',
                                                  'String Instructions: MOVSB/MOVSW, LODSB/LODSW, STOSB/STOSW, '
                                                  'CMPSB/CMPSW, SCASB/SCASW with REP, REPE, REPNE prefixes.',
                                                  'Processor Control: NOP (no operation), HLT (halt CPU), WAIT (wait '
                                                  'for TEST# pin), LOCK (bus lock prefix), STI/CLI (interrupt flag), '
                                                  'CLC/STC/CMC (carry flag), CLD/STD (direction flag).'],
                          'practical_application': 'Hardware string instructions (MOVS, STOS, SCAS with REP) provide '
                                                   'microcoded block memory transfers operating at full bus speed.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'LEA (Load Effective Address) computes the memory offset address '
                                                     'and stores it in the destination register.',
                                      'options': ['MOV', 'LDS', 'LEA (Load Effective Address)', 'LES'],
                                      'question': 'Which instruction loads the 16-bit memory offset address directly '
                                                  'into a register without accessing memory data?'},
                          'register_state': {   'after': '5 bytes copied, SI = 0105H, DI = 0205H, CX = 0000H',
                                                'before': 'SI = 0100H, DI = 0200H, CX = 0005H, DF = 0',
                                                'operation': 'REP MOVSB'},
                          'summary': 'Complete 8086 instruction set organized into 7 functional categories: Data '
                                     'Transfer, Arithmetic, Logical, Shift/Rotate, Control, String, and Processor '
                                     'Control.',
                          'title': '7. 8086 Instruction Set Architecture (7 Categories)',
                          'try_it': 'Review instruction categories in the Learn workstation.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8086 MACHINE CODE BYTE '
                                     'ENCODING                      |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  BYTE 1: OPCODE & CONTROL BITS      BYTE 2: MOD - REG - R/M '
                                     'BYTE                  |\n'
                                     '|  7   6   5   4   3   2   1   0      7   6   5   4   3   2   1   '
                                     '0                 |\n'
                                     '| +-----------------------+---+---+  '
                                     '+-------+-----------+-----------+              |\n'
                                     '| | 6-BIT OPCODE FIELD    | D | W |  | MOD   | REG FIELD | R/M FIELD '
                                     '|              |\n'
                                     '| +-----------------------+---+---+  '
                                     '+-------+-----------+-----------+              |\n'
                                     '|                           |   |      |       |           '
                                     '|                        |\n'
                                     '|                           |   +----->|       |           +-> Reg/Memory '
                                     'Specifier |\n'
                                     '|                           |   Width: |       +-------------> Register '
                                     'Specifier   |\n'
                                     '|                           |   0=Byte | Mode '
                                     'Selector:                             |\n'
                                     '|                           |   1=Word | 00=No Disp, 01=8-bit, 10=16-bit, '
                                     '11=Register|\n'
                                     '|                           +---------> Direction: 0=Reg Source, 1=Reg '
                                     'Destination  |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  BYTES 3-4: DISPLACEMENT (Low/High)   BYTES 5-6: IMMEDIATE DATA '
                                     '(Low/High)        |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'MOV AX, BX -> Machine Code: [8B C3] (2 bytes).\n'
                                     'MOV AL, 55H -> Machine Code: [B0 55] (2 bytes).\n'
                                     'MOV [2050H], AX -> Machine Code: [89 06 50 20] (4 bytes).',
                          'how_it_works': 'Encoding MOV AX, BX Step-by-Step:\n'
                                          '1. Opcode for MOV = 100010.\n'
                                          '2. Destination is AX (REG), so D = 1.\n'
                                          '3. 16-bit word operation, so W = 1.\n'
                                          '4. Byte 1 = 10001011 = 8BH.\n'
                                          '5. Register-to-Register mode, so MOD = 11.\n'
                                          '6. REG = 000 (AX), R/M = 011 (BX).\n'
                                          '7. Byte 2 = 11000011 = C3H.\n'
                                          '8. Resulting Machine Code = 8B C3.',
                          'id': '8086_instruction_format',
                          'important_points': [   'Instruction Length: Ranges from 1 byte (e.g. NOP = 90H, CLC = F8H) '
                                                  'to 6 bytes (e.g. MOV [BX+SI+1234H], 5678H).',
                                                  'Byte 1 Opcode Field: Upper 6 bits contain instruction opcode; Bit 1 '
                                                  '(D) = Direction; Bit 0 (W) = Word width.',
                                                  'D Bit (Direction): D = 1 -> REG field is Destination; D = 0 -> REG '
                                                  'field is Source.',
                                                  'W Bit (Width): W = 0 -> 8-bit byte operation; W = 1 -> 16-bit word '
                                                  'operation.',
                                                  'Byte 2 MOD Field (Bits 7-6): 00 = Memory mode no displacement; 01 = '
                                                  'Memory mode 8-bit disp; 10 = Memory mode 16-bit disp; 11 = Register '
                                                  'to Register mode.',
                                                  'Byte 2 REG Field (Bits 5-3): Encodes 8-bit or 16-bit register '
                                                  '(000=AL/AX, 001=CL/CX, 010=DL/DX, 011=BL/BX, 100=AH/SP, 101=CH/BP, '
                                                  '110=DH/SI, 111=BH/DI).',
                                                  'Byte 2 R/M Field (Bits 2-0): Specifies register or memory '
                                                  'addressing mode combination (e.g. 000=[BX+SI], 001=[BX+DI], '
                                                  '111=[BX]).'],
                          'practical_application': 'Understanding Mod-Reg-R/M byte encoding allows assembly '
                                                   'programmers and disassemblers to decode machine code binary '
                                                   'streams.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'D specifies Direction (D=1 if REG is destination) and W '
                                                     'specifies Width (W=0 for byte, W=1 for word).',
                                      'options': [   'Data and Write',
                                                     'Direction (Reg Dest/Source) and Width (Byte/Word)',
                                                     'Destination and Wait',
                                                     'Decoder and Word'],
                                      'question': 'In the 8086 instruction encoding Byte 1, what do the D and W bits '
                                                  'specify?'},
                          'register_state': {   'after': 'Machine Code Bytes = 8B C3',
                                                'before': 'Instruction: MOV AX, BX',
                                                'operation': 'Opcode Assembly: Byte1=8BH, Byte2=C3H'},
                          'summary': 'Machine code instruction byte layout: Opcode, Direction (D), Width (W), '
                                     'MOD-REG-R/M Byte, Displacement, and Immediate Data encoding.',
                          'title': '8. 8086 Instruction Format & Encoding',
                          'try_it': 'Verify machine code bytes for MOV AX, BX (8B C3).'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8086 MULTIPLEXED BUS '
                                     'DEMULTIPLEXING                        |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|   INTEL 8086 '
                                     'MPU                                                                  |\n'
                                     '|   +---------------+     AD15 - AD0      +-------------------+   A15 - '
                                     'A0          |\n'
                                     '|   | AD15 - AD0    |====================>| 74LS373 LATCH     '
                                     '|==============>      |\n'
                                     '|   |               |                     | (Octal D-Latch)   | Address '
                                     'Bus         |\n'
                                     '|   | ALE Pin 25    |------ STROBE ------>| G (Enable)        '
                                     '|                     |\n'
                                     '|   |               |                     '
                                     '+-------------------+                     |\n'
                                     '|   |               |                     +-------------------+   D15 - '
                                     'D0          |\n'
                                     '|   |               |====================>| 74LS245 '
                                     'TRANSCEIVER|=============>      |\n'
                                     '|   | DEN# Pin 26   |---- ENABLE -------->| OE#               | Data '
                                     'Bus            |\n'
                                     '|   | DT/R# Pin 27  |---- DIRECTION ----->| DIR               '
                                     '|                     |\n'
                                     '|   +---------------+                     '
                                     '+-------------------+                     |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'During Memory Read: ALE pulses -> Address 10000H latched -> RD# goes low -> '
                                     'Memory outputs data -> DEN# enables data to CPU.',
                          'how_it_works': 'Bus Demultiplexing Sequence:\n'
                                          '1. T1 State: 8086 places A15-A0 on AD15-AD0 lines and pulses ALE high.\n'
                                          '2. ALE High-to-Low Transition: Latches address A15-A0 into 74LS373 latches, '
                                          'holding valid address on system bus.\n'
                                          '3. T2-T4 States: AD15-AD0 lines switch to Data Bus D15-D0. DEN# goes low to '
                                          'enable data transceivers.',
                          'id': '8086_address_data_bus',
                          'important_points': [   '20-bit Address Bus (A19-A0): Addresses 1 MB physical memory.',
                                                  '16-bit Data Bus (D15-D0): Transfers 16-bit words or 8-bit bytes.',
                                                  'Multiplexed Pins AD15-AD0: Carry Address A15-A0 during T1 state, '
                                                  'and Data D15-D0 during T2, T3, T4 states.',
                                                  'Multiplexed Pins A16/S3 - A19/S6: Carry Address A19-A16 during T1 '
                                                  'state, and Status signals S3-S6 during T2-T4.',
                                                  'BHE# (Bus High Enable, Pin 34): Active-low signal used with A0 to '
                                                  'enable high data byte (D15-D8) on odd memory bank.',
                                                  'ALE (Address Latch Enable, Pin 25): Pulses high during T1 state to '
                                                  'latch address bits A15-A0 into 74LS373 latches.',
                                                  'DT/R# (Data Transmit/Receive, Pin 27): Controls direction of '
                                                  '74LS245 data transceivers (1 = Transmit/Write, 0 = Receive/Read).',
                                                  'DEN# (Data Enable, Pin 26): Active-low signal enables 74LS245 data '
                                                  'transceivers onto system data bus during T2-T4.'],
                          'practical_application': 'Multiplexing pins reduced CPU package pin count from 36+ pins to '
                                                   '40 pins, enabling standard 40-pin DIP manufacturing.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'DEN# (Data Enable, active low) enables 74LS245 transceivers to '
                                                     'connect CPU data lines to system data bus.',
                                      'options': ['ALE', 'DEN# (Data Enable)', 'DT/R#', 'BHE#'],
                                      'question': 'Which signal is asserted low by the 8086 to enable data onto the '
                                                  'system data bus via transceivers?'},
                          'register_state': {   'after': 'Latch Output = A15-A0, AD15-AD0 freed for Data D15-D0, DEN# '
                                                         '= 0',
                                                'before': 'T1 State: AD15-AD0 = Address, ALE = 1',
                                                'operation': 'ALE Falling Edge Latch'},
                          'summary': 'Multiplexed address/data bus lines (AD0-AD15, A16/S3-A19/S6), BHE# bus high '
                                     'enable, and bus demultiplexing hardware.',
                          'title': '9. 8086 Address/Data Bus Architecture',
                          'try_it': 'Trace ALE and DEN# timing pulses in the bus timing diagram.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                     MINIMUM MODE VS MAXIMUM MODE SYSTEM '
                                     'DIAGRAM                   |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  MINIMUM MODE (MN/MX# = +5V)            MAXIMUM MODE (MN/MX# = '
                                     'GND)               |\n'
                                     '|  +-----------------------+              +------------------+   '
                                     '+---------------+  |\n'
                                     '|  | INTEL 8086 CPU        |              | INTEL 8086 CPU   |   | INTEL 8288    '
                                     '|  |\n'
                                     '|  | Direct Control Pins:  |              | Status Outputs:  |==>| BUS '
                                     'CONTROLLER|  |\n'
                                     '|  | ALE, RD#, WR#, IO/M#  |              | S0#, S1#, S2#    |   | Generates:    '
                                     '|  |\n'
                                     '|  | DT/R#, DEN#, HOLD,HLDA|              +------------------+   | MRDC#, MWTC#  '
                                     '|  |\n'
                                     '|  +-----------------------+                                     | IORC#, IOWC#  '
                                     '|  |\n'
                                     '|  (Single-CPU System)                    (Multiprocessor System)| INTA#, '
                                     'ALE,DEN|  |\n'
                                     '|                                         with 8087 Math Coproc  '
                                     '+---------------+  |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Adding an 8087 Math Coprocessor requires setting MN/MX# = GND (Maximum Mode) and '
                                     'connecting RQ#/GT0# for bus sharing.',
                          'how_it_works': 'Maximum Mode Status Decoding Table (S2#, S1#, S0#):\n'
                                          '- 000: Interrupt Acknowledge (INTA#)\n'
                                          '- 001: Read I/O Port (IORC#)\n'
                                          '- 010: Write I/O Port (IOWC#)\n'
                                          '- 011: Halt\n'
                                          '- 100: Code Access / Opcode Fetch (MRDC#)\n'
                                          '- 101: Read Memory (MRDC#)\n'
                                          '- 110: Write Memory (MWTC#)\n'
                                          '- 111: Passive / Inactive',
                          'id': '8086_min_max_mode',
                          'important_points': [   'Mode Pin MN/MX# (Pin 33): Tied to +5V for Minimum Mode; tied to GND '
                                                  'for Maximum Mode.',
                                                  'Minimum Mode (Single Processor): 8086 directly generates all bus '
                                                  'control signals (ALE, RD#, WR#, IO/M#, DT/R#, DEN#, HOLD, HLDA).',
                                                  'Maximum Mode (Multiprocessor): Used for multi-CPU or coprocessor '
                                                  'systems (8087 Numeric Processor / 8089 I/O Processor).',
                                                  'Status Pins S0#, S1#, S2# (Pins 26-28 in Max Mode): Output 3-bit '
                                                  'encoded processor status to external 8288 Bus Controller.',
                                                  '8288 Bus Controller: Decodes S0#, S1#, S2# to generate system '
                                                  'control signals (MRDC#, MWTC#, IORC#, IOWC#, AMWC#, AIOWC#, INTA#, '
                                                  'ALE, DEN, DT/R#).',
                                                  'Multiprocessor Control Signals: LOCK# (bus lock), RQ#/GT0# and '
                                                  'RQ#/GT1# (request/grant for bus arbitration), QS0/QS1 (queue '
                                                  'status).'],
                          'practical_application': 'Maximum Mode allowed IBM PC architectures to integrate 8087 '
                                                   'floating-point math coprocessors for high-speed scientific '
                                                   'calculations.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'The Intel 8288 Bus Controller decodes status bits S0#, S1#, S2# '
                                                     'to generate system bus command signals in Maximum Mode.',
                                      'options': [   '74LS373 Latch',
                                                     '8259 Interrupt Controller',
                                                     '8288 Bus Controller',
                                                     '8255 Programmable Peripheral Interface'],
                                      'question': 'In 8086 Maximum Mode, which IC chip decodes status lines S0#, S1#, '
                                                  'S2# to generate memory and I/O command signals?'},
                          'register_state': {   'after': '8288 asserts MRDC# = 0 (Memory Read Command)',
                                                'before': 'MN/MX# = 0V (Max Mode), S2#=1, S1#=0, S0#=1',
                                                'operation': '8288 Bus Controller Status Decode'},
                          'summary': 'Detailed comparison of 8086 Minimum Mode (single processor) and Maximum Mode '
                                     '(multiprocessor with 8288 Bus Controller).',
                          'title': '10. Minimum Mode vs Maximum Mode Architecture',
                          'try_it': 'Review Minimum Mode vs Maximum Mode pin assignment differences.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8086 40-PIN DIP PINOUT '
                                     'DIAGRAM                       |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|                       '
                                     '+---------------------\\/---------------------+              |\n'
                                     '|              GND (0V) |  1                                      40 | VCC '
                                     '(+5V)    |\n'
                                     '|              AD14     |  2                                      39 | '
                                     'AD15         |\n'
                                     '|              AD13     |  3                                      38 | '
                                     'A16/S3       |\n'
                                     '|              AD12     |  4                                      37 | '
                                     'A17/S4       |\n'
                                     '|              AD11     |  5                                      36 | '
                                     'A18/S5       |\n'
                                     '|              AD10     |  6                                      35 | '
                                     'A19/S6       |\n'
                                     '|               AD9     |  7                                      34 | '
                                     'BHE#/S7      |\n'
                                     '|               AD8     |  8                                      33 | '
                                     'MN/MX#       |\n'
                                     '|               AD7     |  9            INTEL 8086                32 | '
                                     'RD#          |\n'
                                     '|               AD6     | 10             CPU DIP                  31 | HOLD '
                                     '(RQ/GT0)|\n'
                                     '|               AD5     | 11                                      30 | HLDA '
                                     '(RQ/GT1)|\n'
                                     '|               AD4     | 12                                      29 | WR#  '
                                     '(LOCK#) |\n'
                                     '|               AD3     | 13                                      28 | '
                                     'IO/M#(S2#)   |\n'
                                     '|               AD2     | 14                                      27 | '
                                     'DT/R#(S1#)   |\n'
                                     '|               AD1     | 15                                      26 | DEN# '
                                     '(S0#)   |\n'
                                     '|               AD0     | 16                                      25 | ALE  '
                                     '(QS0)   |\n'
                                     '|               NMI     | 17                                      24 | '
                                     'INTA#(QS1)   |\n'
                                     '|              INTR     | 18                                      23 | '
                                     'TEST#        |\n'
                                     '|               CLK     | 19                                      22 | '
                                     'READY        |\n'
                                     '|              GND (0V) | 20                                      21 | '
                                     'RESET        |\n'
                                     '|                       '
                                     '+--------------------------------------------+              |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Pins 24-31 change function completely depending on whether MN/MX# (Pin 33) is '
                                     'connected to +5V or GND.',
                          'how_it_works': 'Reset Vector Execution:\n'
                                          'When RESET pin 21 is pulsed high for 4 clock cycles, 8086 clears flags, '
                                          'sets CS = FFFFH and IP = 0000H. CPU begins fetching instructions from '
                                          'physical address FFFF0H (EPROM boot code).',
                          'id': '8086_pin_diagram',
                          'important_points': [   '40-Pin Dual In-line Package (DIP) operating on +5V VCC (Pin 40) and '
                                                  'Ground (Pins 1 & 20).',
                                                  'AD15-AD0 (Pins 2-16, 39): Multiplexed Address/Data bus lines.',
                                                  'A19/S6 - A16/S3 (Pins 35-38): Multiplexed upper Address / Status '
                                                  'lines.',
                                                  'BHE#/S7 (Pin 34): Bus High Enable / Status S7.',
                                                  'MN/MX# (Pin 33): Minimum / Maximum mode select pin (+5V = Min Mode, '
                                                  'GND = Max Mode).',
                                                  'RD# (Pin 32): Active-low Memory or I/O Read strobe.',
                                                  'WR# / LOCK# (Pin 29): Write strobe in Min Mode / Bus Lock signal in '
                                                  'Max Mode.',
                                                  'IO/M# / S2# (Pin 28): I/O or Memory select in Min Mode / Status S2# '
                                                  'in Max Mode.',
                                                  'DT/R# / S1# (Pin 27): Data Transmit/Receive in Min Mode / Status '
                                                  'S1# in Max Mode.',
                                                  'DEN# / S0# (Pin 26): Data Enable in Min Mode / Status S0# in Max '
                                                  'Mode.',
                                                  'ALE / QS0 (Pin 25): Address Latch Enable in Min Mode / Queue Status '
                                                  '0 in Max Mode.',
                                                  'INTA# / QS1 (Pin 24): Interrupt Acknowledge in Min Mode / Queue '
                                                  'Status 1 in Max Mode.',
                                                  'TEST# (Pin 23): Examined by WAIT instruction; CPU waits if TEST# is '
                                                  'High until low pulse.',
                                                  'READY (Pin 22): Input for inserting Wait States for slow memory/IO '
                                                  'devices.',
                                                  'RESET (Pin 21): Resets CPU (CS set to FFFFH, IP set to 0000H, reset '
                                                  'vector = FFFF0H).'],
                          'practical_application': 'System designers connect EPROM boot ROM at physical address FFFF0H '
                                                   'to ensure BIOS execution on startup.',
                          'quiz': {   'correct': 2,
                                      'explanation': 'On RESET, CS is loaded with FFFFH and IP with 0000H. Physical '
                                                     'Address = (FFFFH * 10H) + 0000H = FFFF0H.',
                                      'options': ['00000H', '00100H', 'FFFF0H', 'FFFFFFH'],
                                      'question': 'At what physical memory address does the Intel 8086 begin fetching '
                                                  'instructions immediately after a hardware RESET?'},
                          'register_state': {   'after': 'CS = FFFFH, IP = 0000H, Flags = 0000H, Fetch Address = '
                                                         'FFFF0H',
                                                'before': 'RESET Pin 21 Pulsed High',
                                                'operation': 'CPU Hardware Reset Sequence'},
                          'summary': 'Comprehensive 40-pin DIP layout, pin descriptions, dual-mode pin functions, and '
                                     'signal groupings.',
                          'title': '11. 8086 Pin Diagram & Signal Classification',
                          'try_it': 'Locate RESET vector address FFFF0H in the 8086 memory map.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                       8086 EVEN AND ODD MEMORY '
                                     'BANKING                            |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|        8086 CPU DATA BUS (D15 - '
                                     'D0)                                               |\n'
                                     '|        '
                                     '+--------------------------------------------------+                       |\n'
                                     '|        |                                                  '
                                     '|                       |\n'
                                     '|        v (D15 - D8 Upper Byte)                            v (D7 - D0 Lower '
                                     'Byte)  |\n'
                                     '|  +---------------------------+                      '
                                     '+---------------------------+ |\n'
                                     '|  | ODD MEMORY BANK (512 KB)  |                      | EVEN MEMORY BANK (512 '
                                     'KB) | |\n'
                                     '|  | Addresses: 00001H,00003H..|                      | Addresses: '
                                     '00000H,00002H..| |\n'
                                     '|  | Enabled by: BHE# = 0      |                      | Enabled by: A0 = '
                                     '0        | |\n'
                                     '|  +---------------------------+                      '
                                     '+---------------------------+ |\n'
                                     '|                ^                                                  '
                                     '^               |\n'
                                     '|                |                                                  '
                                     '|               |\n'
                                     '|          BHE# (Pin 34)                                        A0 (Address Bit '
                                     '0)  |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Always align 16-bit data words at EVEN memory addresses (e.g. 20000H) to allow '
                                     'single-cycle 16-bit bus transfer.',
                          'how_it_works': 'Misaligned Word Access Penalty:\n'
                                          'Reading 16-bit word at odd address 20001H:\n'
                                          '1. Bus Cycle 1: BHE#=0, A0=1 -> Reads byte at odd address 20001H via D15-D8 '
                                          'into AL.\n'
                                          '2. Bus Cycle 2: BHE#=1, A0=0 -> Reads byte at even address 20002H via D7-D0 '
                                          'into AH.\n'
                                          'Total = 2 Bus Cycles (Performance Penalty!).',
                          'id': '8086_memory_interfacing',
                          'important_points': [   '16-bit Memory Split: 1 MB memory divided into two 512 KB memory '
                                                  'banks: Even Bank and Odd Bank.',
                                                  'Even (Low) Bank: Connected to lower data lines D7-D0. Stores data '
                                                  'at even physical addresses (00000H, 00002H, etc.). Activated when '
                                                  'A0 = 0.',
                                                  'Odd (High) Bank: Connected to upper data lines D15-D8. Stores data '
                                                  'at odd physical addresses (00001H, 00003H, etc.). Activated when '
                                                  'BHE# = 0.',
                                                  'Bank Selection Control:\n'
                                                  '- BHE# = 0, A0 = 0: Reads/Writes 16-bit Word at Even Address in 1 '
                                                  'Bus Cycle.\n'
                                                  '- BHE# = 1, A0 = 0: Reads/Writes 8-bit Byte at Even Address in 1 '
                                                  'Bus Cycle.\n'
                                                  '- BHE# = 0, A0 = 1: Reads/Writes 8-bit Byte at Odd Address in 1 Bus '
                                                  'Cycle.\n'
                                                  '- BHE# = 1, A0 = 1: Unaligned 16-bit Word access -> Requires 2 Bus '
                                                  'Cycles!',
                                                  'Address Decoding: 74LS138 3-to-8 line decoders convert upper '
                                                  'address lines A19-A17 into chip select (CS#) lines for RAM/ROM '
                                                  'chips.'],
                          'practical_application': 'Compilers automatically align 16-bit variables at even memory '
                                                   'boundaries to optimize 8086 memory execution speed.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'Misaligned word access requires 2 bus cycles: Cycle 1 fetches '
                                                     'odd byte via D15-D8; Cycle 2 fetches even byte via D7-D0.',
                                      'options': ['1 Bus Cycle', '2 Bus Cycles', '3 Bus Cycles', '4 Bus Cycles'],
                                      'question': 'How many bus cycles does 8086 require to read a 16-bit word stored '
                                                  'at an ODD memory address?'},
                          'register_state': {   'after': 'Full 16-bit word transferred in 1 bus cycle via D15-D0',
                                                'before': 'Access 16-bit Word at Address 20000H (Even Aligned)',
                                                'operation': 'Single Bus Cycle: BHE# = 0, A0 = 0'},
                          'summary': '16-bit memory organization split into Even (Low) and Odd (High) 512 KB banks, '
                                     'A0/BHE# bank selection, and address decoding.',
                          'title': '12. 8086 Memory Interfacing & Banking (Even/Odd)',
                          'try_it': 'Compare aligned vs misaligned memory transfer cycle counts.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                  8086 INTERRUPT VECTOR TABLE (IVT) MEMORY '
                                     'MAP                     |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  PHYSICAL ADDRESS   IVT MEMORY CONTENTS (00000H - 003FFH = 1 '
                                     'KB)                  |\n'
                                     '|  003FFH '
                                     '+-----------------------------------------------------------------------+ |\n'
                                     '|         | Type 255 Interrupt Vector (IP Low, IP High, CS Low, CS '
                                     'High)          | |\n'
                                     '|         | '
                                     '...                                                                   | |\n'
                                     '|  00014H '
                                     '+-----------------------------------------------------------------------+ |\n'
                                     '|         | Type 5 - 254 User / Hardware Interrupt '
                                     'Vectors                        | |\n'
                                     '|  00010H '
                                     '+-----------------------------------------------------------------------+ |\n'
                                     '|         | Type 4 Vector: Overflow Exception '
                                     '(INTO)                              | |\n'
                                     '|  0000CH '
                                     '+-----------------------------------------------------------------------+ |\n'
                                     '|         | Type 3 Vector: Breakpoint Interrupt (INT '
                                     '3)                           | |\n'
                                     '|  00008H '
                                     '+-----------------------------------------------------------------------+ |\n'
                                     '|         | Type 2 Vector: Non-Maskable Interrupt (NMI '
                                     'pin)                       | |\n'
                                     '|  00004H '
                                     '+-----------------------------------------------------------------------+ |\n'
                                     '|         | Type 1 Vector: Single-Step Trap (TF = '
                                     '1)                              | |\n'
                                     '|  00000H '
                                     '+-----------------------------------------------------------------------+ |\n'
                                     '|         | Type 0 Vector: Divide-by-Zero '
                                     'Exception                               | |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'how_it_works': 'Interrupt Processing Sequence:\n'
                                          '1. Push FLAGS register onto stack (SP = SP - 2).\n'
                                          '2. Clear IF (0) and TF (0) to disable nested interrupts.\n'
                                          '3. Push CS register onto stack (SP = SP - 2).\n'
                                          '4. Push IP register onto stack (SP = SP - 2).\n'
                                          '5. Read IP from (Type * 4) and CS from (Type * 4 + 2).\n'
                                          '6. Jump to ISR routine. End ISR with IRET (pops IP, CS, FLAGS).',
                          'id': '8086_interrupts',
                          'important_points': [   '256 Interrupt Vectors: Numbered Type 0 to Type 255.',
                                                  'Interrupt Vector Table (IVT): Occupies first 1 KB of memory (00000H '
                                                  'to 003FFH).',
                                                  'IVT Address Calculation: IVT Address = Interrupt Type * 4.',
                                                  'Each vector stores 4 bytes: 2 bytes for CS (Code Segment) + 2 bytes '
                                                  'for IP (Instruction Pointer).',
                                                  'Dedicated Interrupts (Types 0-4):\n'
                                                  '- Type 0: Divide-by-Zero Exception (triggered when division '
                                                  'quotient overflows).\n'
                                                  '- Type 1: Single-Step Trap (triggered after each instruction when '
                                                  'TF = 1).\n'
                                                  '- Type 2: Non-Maskable Interrupt (NMI pin rising edge input).\n'
                                                  '- Type 3: Breakpoint Interrupt (INT 3 1-byte opcode CC).\n'
                                                  '- Type 4: Overflow Exception (INTO instruction when OF = 1).',
                                                  'Software Interrupts: INT N instruction (N = 0 to 255).',
                                                  'Hardware Interrupts: Maskable INTR (pin 18, enabled by STI/IF=1) '
                                                  'and Non-Maskable NMI (pin 17).'],
                          'summary': '256 Interrupt Vectors, Interrupt Vector Table (IVT) calculation, dedicated '
                                     'interrupts (Type 0-4), hardware INTR/NMI, and IRET.',
                          'title': '13. 8086 Interrupt System & IVT'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8086 BASIC MEMORY READ BUS CYCLE '
                                     'TIMING                    |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|         |<-- T1 -->|<-- T2 -->|<-- T3 -->|<-- Tw -->|<-- T4 '
                                     '-->|                |\n'
                                     '|  CLK   --\\__/  \\__/  \\__/  \\__/  \\__/  \\__/  \\__/  \\__/  \\__/  '
                                     '\\--                |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  ALE   __/  '
                                     '\\___________________________________________________                  |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  ADDR  ==== Valid A19-A0 '
                                     '======X================================                  |\n'
                                     '|  AD15-0==== Address A15-A0 ====X======== Valid Data In '
                                     '=======X==                  |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  RD#   ________________________/                         '
                                     '\\______                  |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  READY ____________________________________/  '
                                     '\\_________________                  |\n'
                                     '|                                            (Sampled at '
                                     'T2)                        |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'At 5 MHz (T-state = 200 ns), a standard 4-T bus cycle takes 800 ns. Adding 1 '
                                     'Wait State (Tw) extends cycle to 1000 ns (1 µs).',
                          'how_it_works': 'Slow Memory Wait State Insertion:\n'
                                          'If memory access time is longer than 2 T-states, external hardware pulls '
                                          'READY pin LOW during T2. 8086 inserts extra T-states (Tw) between T3 and T4 '
                                          'until READY goes HIGH.',
                          'id': '8086_timing',
                          'important_points': [   'T-State: Single clock cycle of internal CPU clock (e.g. 200 ns at 5 '
                                                  'MHz clock).',
                                                  'Bus Cycle: Time required to perform one memory or I/O read/write '
                                                  'operation. Minimum 4 T-states (T1, T2, T3, T4).',
                                                  'T1 State: Address output phase. 8086 outputs 20-bit address on '
                                                  'AD15-AD0 and A19/S6-A16/S3; ALE pulses high.',
                                                  'T2 State: Bus direction phase. Address removed from AD15-AD0; RD# '
                                                  'or WR# control signal asserted low.',
                                                  'T3 State: Data transfer phase. Memory/IO device puts data on bus '
                                                  '(Read) or latches data from bus (Write).',
                                                  'Wait States (Tw): Inserted between T3 and T4 if READY pin is '
                                                  'sampled LOW at end of T2.',
                                                  'T4 State: Bus cycle completion phase. Data latched into CPU; '
                                                  'RD#/WR# control signals return high.'],
                          'practical_application': 'READY pin interfacing allows 8086 systems to operate reliably with '
                                                   'low-cost slow EPROM chips.',
                          'quiz': {   'correct': 1,
                                      'explanation': '8086 samples the READY pin input at the end of T2 state; if LOW, '
                                                     'it inserts Wait State (Tw) before T4.',
                                      'options': ['State T1', 'End of State T2', 'State T3', 'State T4'],
                                      'question': 'At which T-state does the 8086 CPU sample the READY pin to '
                                                  'determine if a Wait State (Tw) must be inserted?'},
                          'register_state': {   'after': '8086 inserts Tw cycle, holds bus signals active until READY '
                                                         '= HIGH',
                                                'before': 'T2 State End: READY pin sampled LOW',
                                                'operation': 'Wait State Insertion (Tw)'},
                          'summary': 'T-states, basic 4-T-state bus cycle, opcode fetch, memory read/write timing, '
                                     'wait states, and READY signal logic.',
                          'title': '14. 8086 Timing Diagrams & Bus Cycles',
                          'try_it': 'Calculate bus cycle time at 8 MHz clock (T = 125 ns).'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8086 STACK MEMORY OPERATION '
                                     'TRACE                          |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  BEFORE PUSH AX (AX = 1234H, SP = 2000H)      AFTER PUSH AX (SP = '
                                     '1FEH)           |\n'
                                     '|  ADDRESS   CONTENTS                           ADDRESS   '
                                     'CONTENTS                  |\n'
                                     '|  SS:2000H  [ Top of Stack ]                   SS:2000H  [ Top of Stack '
                                     ']          |\n'
                                     '|  SS:1FFFH  [ Unused ]                         SS:1FFFH  [ 12H (AH High Byte) '
                                     ']   |\n'
                                     '|  SS:1FEH   [ Unused ]  <-- SP (2000H)         SS:1FEH   [ 34H (AL Low Byte)  ] '
                                     '<--|\n'
                                     '|                                                                             '
                                     'SP    |\n'
                                     '|  PUSH Sequence: SP = SP - 2 -> Write AH to SS:SP+1 -> Write AL to '
                                     'SS:SP         |\n'
                                     '|  POP Sequence : Read AL from SS:SP -> Read AH from SS:SP+1 -> SP = SP + '
                                     '2        |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Given SS = 5000H, SP = 1000H, AX = AABBH:\n'
                                     'PUSH AX -> SP = 0FFEH. Memory 50FFE = BH, 50FFF = AH.',
                          'how_it_works': 'Executing CALL SUBROUTINE:\n'
                                          '1. SP decremented by 2.\n'
                                          '2. Return offset IP stored on stack.\n'
                                          '3. IP loaded with target subroutine address.\n'
                                          '4. Subroutine executes.\n'
                                          '5. RET pops return IP from stack into IP register.',
                          'id': '8086_stack',
                          'important_points': [   'LIFO Memory Area: Stack operates in 64 KB Stack Segment (SS) with '
                                                  '16-bit Stack Pointer (SP).',
                                                  'Downward Growth: Stack grows downwards from higher memory addresses '
                                                  'to lower memory addresses.',
                                                  'PUSH Register (16-bit Word):\n'
                                                  '1. Decrement SP by 2: SP = SP - 2.\n'
                                                  '2. Write High Byte (AH) to physical address SS:SP + 1.\n'
                                                  '3. Write Low Byte (AL) to physical address SS:SP.',
                                                  'POP Register (16-bit Word):\n'
                                                  '1. Read Low Byte (AL) from physical address SS:SP.\n'
                                                  '2. Read High Byte (AH) from physical address SS:SP + 1.\n'
                                                  '3. Increment SP by 2: SP = SP + 2.',
                                                  'Near CALL: Subroutine in same Code Segment. Pushes 16-bit IP onto '
                                                  'stack (SP=SP-2), loads target IP.',
                                                  'Far CALL: Subroutine in different Code Segment. Pushes CS then IP '
                                                  'onto stack (SP=SP-4), loads target CS:IP.',
                                                  'RET / IRET: Restores IP (and CS) from stack, restoring program '
                                                  'execution flow.'],
                          'practical_application': 'Stack preserves register values across subroutine calls and passes '
                                                   'arguments in high-level language functions (C/C++).',
                          'quiz': {   'correct': 2,
                                      'explanation': 'Because 8086 stack grows downwards, PUSH decrements SP by 2 '
                                                     'before writing the 16-bit word to stack memory.',
                                      'options': [   'SP is incremented by 1',
                                                     'SP is incremented by 2',
                                                     'SP is decremented by 2',
                                                     'SP remains unchanged'],
                                      'question': 'What happens to the Stack Pointer (SP) when a 16-bit PUSH '
                                                  'instruction is executed in 8086?'},
                          'register_state': {   'after': 'SP = 0FFEH, [SS:0FFEH] = BBH, [SS:0FFFH] = AAH',
                                                'before': 'SS = 5000H, SP = 1000H, AX = AABBH',
                                                'operation': 'PUSH AX'},
                          'summary': 'Stack Segment (SS), Stack Pointer (SP), PUSH, POP, CALL (Near/Far), RET, and '
                                     'step-by-step stack memory traces.',
                          'title': '15. 8086 Stack Operations & Subroutines',
                          'try_it': 'Trace SP value after 3 consecutive PUSH instructions.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8086 ASSEMBLY PROGRAMMING '
                                     'WORKSTATION                      |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  1. 8-Bit Addition           7. Smallest Array Element  13. Count '
                                     'Pos/Neg         |\n'
                                     '|  2. 16-Bit Addition          8. Bubble Sorting          14. Array '
                                     'Sum             |\n'
                                     '|  3. 16-Bit Subtraction       9. Linear Search           15. String '
                                     'Length         |\n'
                                     '|  4. 16-Bit Multiplication   10. Block Data Transfer     16. Time '
                                     'Delay            |\n'
                                     '|  5. 16-Bit/8-Bit Division   11. BCD Addition (DAA)     17. Even/Odd '
                                     'Check        |\n'
                                     '|  6. Largest Array Element   12. ASCII to BCD            18. Bit '
                                     'Manipulation      |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'BCD Addition with DAA:\n'
                                     '`MOV AL, 59H`\n'
                                     '`ADD AL, 27H` -> Binary Result = 80H\n'
                                     '`DAA` -> Correct BCD Result = 86H (Auxiliary Carry AF=1 added 06H).',
                          'how_it_works': 'Executing Block Data Transfer Program:\n'
                                          '```assembly\n'
                                          'MOV AX, DATA_SEG\n'
                                          'MOV DS, AX\n'
                                          'MOV ES, AX\n'
                                          'LEA SI, SRC_ARRAY\n'
                                          'LEA DI, DST_ARRAY\n'
                                          'MOV CX, 000AH     ; 10 Bytes\n'
                                          'CLD               ; Auto-increment SI/DI\n'
                                          'REP MOVSB         ; Copy 10 bytes at full bus speed\n'
                                          '```',
                          'id': '8086_assembly_programming',
                          'important_points': [   'Program 1 (8-bit Addition): MOV AL, 25H | ADD AL, 15H | MOV '
                                                  '[2000H], AL.',
                                                  'Program 2 (16-bit Addition): MOV AX, 1234H | ADD AX, 5678H | MOV '
                                                  '[2000H], AX.',
                                                  'Program 3 (16-bit Subtraction): MOV AX, 5000H | SUB AX, 1200H | MOV '
                                                  '[2000H], AX.',
                                                  'Program 4 (Multiplication): MOV AX, 1000H | MOV BX, 0020H | MUL BX '
                                                  '-> Product in DX:AX.',
                                                  'Program 5 (Division): MOV AX, 0025H | MOV BL, 05H | DIV BL -> AL = '
                                                  'Quotient (07H), AH = Remainder (00H).',
                                                  'Program 6 (Largest Number): LEA SI, ARR | MOV CX, 5 | MOV AL, [SI] '
                                                  '| LOOP: CMP AL, [SI+1] | JAE NEXT | MOV AL, [SI+1] | NEXT: INC SI | '
                                                  'LOOP.',
                                                  'Program 7 (Smallest Number): Same as Largest using JBE condition.',
                                                  'Program 8 (Bubble Sort): Nested loops using CMP AL, [SI+1] and XCHG '
                                                  'AL, [SI+1].',
                                                  'Program 9 (Linear Search): LEA SI, ARR | MOV CX, N | MOV AL, KEY | '
                                                  'REPNE SCASB | JZ FOUND.',
                                                  'Program 10 (Block Transfer): LEA SI, SRC | LEA DI, DST | MOV CX, 10 '
                                                  '| CLD | REP MOVSB.',
                                                  'Program 11 (BCD Addition): MOV AL, 38H | ADD AL, 45H | DAA -> AL = '
                                                  '83H (BCD adjusted).',
                                                  "Program 12 (ASCII to BCD): MOV AL, '7' (37H) | AND AL, 0FH -> AL = "
                                                  '07H.',
                                                  'Program 13 (Count Pos/Neg): TEST AL, 80H | JS NEGATIVE | INC '
                                                  'POS_CNT.',
                                                  'Program 14 (Array Sum): ADD AX, [SI] | ADC DX, 0 | ADD SI, 2 | '
                                                  'LOOP.',
                                                  "Program 15 (String Length): LEA DI, STR | MOV AL, '$' | MOV CX, -1 "
                                                  '| CLD | REPNE SCASB.',
                                                  'Program 16 (Time Delay): MOV CX, 0FFFFH | DELAY: LOOP DELAY.',
                                                  'Program 17 (Even/Odd Check): TEST AL, 01H | JZ EVEN_NUM | JNZ '
                                                  'ODD_NUM.',
                                                  'Program 18 (Bit Manipulation): OR AL, 08H (Set Bit 3) | AND AL, F7H '
                                                  '(Clear Bit 3) | XOR AL, 08H (Toggle Bit 3).'],
                          'practical_application': 'Hardware DAA instruction is essential for financial algorithms '
                                                   'operating on BCD decimal numbers.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'DAA (Decimal Adjust Accumulator) adjusts binary addition result '
                                                     'in AL into valid BCD format.',
                                      'options': ['DAS', 'DAA (Decimal Adjust Accumulator)', 'AAA', 'AAM'],
                                      'question': 'Which 8086 instruction adjusts the result of adding two binary '
                                                  'coded decimal (BCD) numbers in AL?'},
                          'register_state': {   'after': 'AL = 86H (Correct BCD), AF = 1, CF = 0',
                                                'before': 'AL = 59H, BL = 27H',
                                                'operation': 'ADD AL, BL followed by DAA'},
                          'summary': '18 fully documented assembly programs: Addition, Subtraction, Multiplication, '
                                     'Division, Array Min/Max, Sorting, Searching, Block Transfer, BCD, ASCII, and '
                                     'String routines.',
                          'title': '16. 8086 Assembly Programming (18 Practical Programs)',
                          'try_it': 'Run Assembly code examples in the Virtual Trainer Kit.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        8086 STEP-BY-STEP EXECUTION TRACE '
                                     'WORKSTATION              |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  EXAMPLE 1: ADD AX, '
                                     'BX                                                            |\n'
                                     '|  Initial : AX = 2050H, BX = '
                                     '1030H                                                 |\n'
                                     '|  Exec    : ADD AX, BX  (2050H + 1030H = '
                                     '3080H)                                   |\n'
                                     '|  Final   : AX = 3080H, BX = '
                                     '1030H                                                 |\n'
                                     '|  Flags   : SF = 0, ZF = 0, PF = 1, CF = 0, OF = '
                                     '0                                  |\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Executing MUL CX with AX = 1000H, CX = 0010H:\n'
                                     'DX:AX = 1000H * 0010H = 00010000H -> DX = 0001H, AX = 0000H.',
                          'how_it_works': 'Detailed Flag Evaluation Trace for SUB AX, BX:\n'
                                          'AX = 1000H, BX = 2000H\n'
                                          'Operation: 1000H - 2000H = F000H.\n'
                                          '- MSB = 1 -> Sign Flag SF = 1.\n'
                                          '- Result != 0 -> Zero Flag ZF = 0.\n'
                                          '- Borrow required -> Carry Flag CF = 1.\n'
                                          '- Lower byte 00H has 0 ones (even) -> Parity Flag PF = 1.',
                          'id': '8086_examples',
                          'important_points': [   'Trace 1 (16-Bit Addition): MOV AX, 2050H | MOV BX, 1030H | ADD AX, '
                                                  'BX -> Final AX = 3080H, Flags: SF=0, ZF=0, PF=1, CF=0, OF=0.',
                                                  'Trace 2 (16-Bit Subtraction with Borrow): MOV AX, 1000H | MOV BX, '
                                                  "2000H | SUB AX, BX -> Final AX = F000H (-4096 in 2's comp), Flags: "
                                                  'SF=1, ZF=0, CF=1 (Borrow), OF=0.',
                                                  'Trace 3 (Unsigned Multiplication): MOV AX, 0100H | MOV CX, 0200H | '
                                                  'MUL CX -> Product = 00020000H -> DX = 0002H, AX = 0000H, Flags: '
                                                  'CF=1, OF=1 (Upper half active).',
                                                  'Trace 4 (Bitwise Masking AND): MOV AX, 1234H | AND AX, 00FFH -> '
                                                  'Final AX = 0034H (High byte masked out), Flags: SF=0, ZF=0, PF=1, '
                                                  'CF=0, OF=0.',
                                                  'Trace 5 (Rotate Left ROL): MOV AX, 8001H (1000 0000 0000 0001B) | '
                                                  'ROL AX, 1 -> Final AX = 0003H (0000 0000 0000 0011B), CF = 1 (MSB '
                                                  'rotated into CF and LSB).',
                                                  'Trace 6 (Load Effective Address LEA): LEA SI, [1000H] -> Final SI = '
                                                  '1000H (Offset loaded without memory read).',
                                                  'Trace 7 (Stack PUSH & POP): PUSH AX (SP=1FFEH) | POP BX -> Final BX '
                                                  '= AX value, SP restored to 2000H.'],
                          'practical_application': 'Tracing flags step-by-step is critical for debugging conditional '
                                                   'jumps (JE, JNE, JL, JG) in embedded code.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'INC increments the register and updates ZF, SF, OF, PF, AF, but '
                                                     'explicitly does NOT alter the Carry Flag (CF).',
                                      'options': [   'AX = 0000H, CF = 1',
                                                     'AX = 0000H, CF = 0 (INC does not affect CF)',
                                                     'AX = 10000H, CF = 1',
                                                     'AX = FFFFH, CF = 0'],
                                      'question': 'What will be the value of AX and the Carry Flag (CF) after '
                                                  'executing MOV AX, FFFFH followed by INC AX?'},
                          'register_state': {   'after': 'DX = 0001H, AX = 0000H, CF = 1, OF = 1',
                                                'before': 'AX = 1000H, CX = 0010H, DX = 0000H',
                                                'operation': 'MUL CX (16-bit Unsigned Multiply)'},
                          'summary': 'Detailed execution traces showing Initial Register values, Operation, Final '
                                     'Register states, and Affected Status Flags.',
                          'title': '17. Step-by-Step 8086 Execution Examples',
                          'try_it': 'Trace final register values for MOV AX, FFFFH | INC AX.'},
                      {   'diagram': '\n'
                                     '+-----------------------------------------------------------------------------------+\n'
                                     '|                        INTEL 8085 VS INTEL 8086 '
                                     'COMPARISON                        |\n'
                                     '|                                                                                   '
                                     '|\n'
                                     '|  FEATURE                  INTEL 8085                    INTEL '
                                     '8086                |\n'
                                     '|  '
                                     '+-----------------------+-----------------------------+-----------------------+  '
                                     '|\n'
                                     '|  | Data Bus Width        | 8 Bits (D7-D0)              | 16 Bits (D15-D0)      '
                                     '|  |\n'
                                     '|  | Address Bus Width     | 16 Bits (A15-A0)            | 20 Bits (A19-A0)      '
                                     '|  |\n'
                                     '|  | Physical Memory Space | 64 KB                       | 1 MB (1,048,576 '
                                     'bytes)|  |\n'
                                     '|  | Internal Architecture | Single Processing Unit      | Dual Units (BIU + EU) '
                                     '|  |\n'
                                     '|  | Instruction Queue     | No Queue (Non-pipelined)    | 6-Byte Prefetch Queue '
                                     '|  |\n'
                                     '|  | Memory Organization   | Single Contiguous Memory    | Segmented (64KB segs) '
                                     '|  |\n'
                                     '|  | Operating Modes       | Single Operating Mode       | Minimum & Maximum     '
                                     '|  |\n'
                                     '|  | Multiply/Divide       | Software Routines Only      | Hardware MUL/IMUL/DIV '
                                     '|  |\n'
                                     '|  | Interrupt Vectors     | 5 Hardware Interrupts       | 256 Vector Table IVT  '
                                     '|  |\n'
                                     '|  | Clock Frequency       | 3 MHz                       | 5 MHz, 8 MHz, 10 MHz  '
                                     '|  |\n'
                                     '|  '
                                     '+-----------------------+-----------------------------+-----------------------+  '
                                     '|\n'
                                     '+-----------------------------------------------------------------------------------+\n',
                          'example': 'Multiplying 16-bit numbers:\n'
                                     '8085 requires 50+ lines of software shift-and-add loop code (~200 T-states).\n'
                                     '8086 executes single hardware instruction `MUL BX` in 118 T-states.',
                          'how_it_works': 'Performance Jump Explanation:\n'
                                          'Combining a 16-bit data bus, 6-byte prefetch instruction queue, 10 MHz '
                                          'clock, and hardware 16-bit multiplication gave the 8086 over 10x higher '
                                          'processing throughput compared to the 8085.',
                          'id': '8085_vs_8086',
                          'important_points': [   'Data Bus: 8085 has 8-bit data bus; 8086 has 16-bit data bus (2x '
                                                  'data throughput).',
                                                  'Address Bus & Memory: 8085 has 16-bit address bus (64 KB); 8086 has '
                                                  '20-bit address bus (1 MB physical memory = 16x capacity).',
                                                  'Architecture & Pipelining: 8085 executes serially '
                                                  '(fetch-then-execute); 8086 uses BIU+EU dual units with 6-byte '
                                                  'instruction queue for pipelined execution.',
                                                  'Registers: 8085 has 8-bit registers (A, B, C, D, E, H, L); 8086 has '
                                                  '16-bit registers (AX, BX, CX, DX, CS, DS, SS, ES, SI, DI, SP, BP, '
                                                  'IP).',
                                                  'Hardware Math: 8085 lacks hardware multiplication/division; 8086 '
                                                  'includes built-in hardware 16-bit MUL, IMUL, DIV, IDIV '
                                                  'instructions.',
                                                  'Memory Layout: 8085 addresses flat 64 KB memory; 8086 divides 1 MB '
                                                  'memory into 64 KB Code, Data, Stack, and Extra segments.',
                                                  'Operating Modes: 8085 operates in single mode; 8086 supports '
                                                  'Minimum Mode (single CPU) and Maximum Mode (multiprocessor with '
                                                  '8087 math coprocessor).',
                                                  'Interrupt Vector Table: 8085 has 5 fixed hardware interrupts (TRAP, '
                                                  'RST7.5, RST6.5, RST5.5, INTR); 8086 supports 256 vectored '
                                                  'interrupts via IVT in RAM.'],
                          'practical_application': '8086 established the x86 instruction set architecture used in '
                                                   'modern Intel Core and AMD Ryzen processors today.',
                          'quiz': {   'correct': 1,
                                      'explanation': 'The 6-byte Instruction Queue in the 8086 Bus Interface Unit '
                                                     '(BIU) prefetches instructions while the EU executes, '
                                                     'implementing pipelining.',
                                      'options': [   'Accumulator Register',
                                                     '6-byte Instruction Queue in BIU',
                                                     '16-bit Address Latch',
                                                     '8-bit Stack Pointer'],
                                      'question': 'Which architectural feature introduced in the 8086 enables '
                                                  'instruction prefetching and pipelining compared to the 8085?'},
                          'register_state': {   'after': '8086 delivers 10x higher processing speed & x86 PC standard',
                                                'before': '8085: 8-Bit CPU, 64 KB RAM  |  8086: 16-Bit CPU, 1 MB RAM',
                                                'operation': 'Architectural Evolution Comparison'},
                          'summary': 'Comprehensive comparative analysis covering data bus, address bus, memory '
                                     'capacity, registers, architecture, pipelining, and performance.',
                          'title': '18. 8085 vs 8086 Microprocessor Comparison',
                          'try_it': 'Compare 8085 and 8086 features in the Learn workstation.'}]}]
