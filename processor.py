# Instruction Fetch (IF)
# Instruction Decode (ID)
# Execute (EXE)
# Memory Access (MEM)
# Write Back (WB)

class Processor:

    OP_CONVERSION = {
        '1112' : 'R',
        '1624' : 'R',
        '1880' : 'R',
        '1104' : 'R',
        '1360' : 'R',
        '1872' : 'R',
        '1691' : 'R',
        '1690' : 'R',
        '1160' : 'I',
        '1672' : 'I',
        '1928' : 'I',
        '584' : 'I',
        '712' : 'I',
        '840' : 'I',
        '1986' : 'D',
        '1984' : 'D',
        '180' : 'CB',
        '181' : 'CB',
        '679' : 'CB',
        '5' : 'B'
    }
    # Instruction Memory Contents
    IMEM = []
    IMEM_MAX = 10
    # Data Memory Contents
    DMEM = []
    DMEM_MAX = 10
    # Register Contents
    REG = []
    REG_MAX = 32

    def __init__(self):
        for i in range(self.IMEM_MAX):
            self.IMEM.append('')
        for i in range(self.DMEM_MAX):
            self.DMEM.append(0)
        for i in range(self.REG_MAX):
            self.REG.append(0)
        self.PC = 0

# Private
    # Set IMEM
    def __set_IMEM(self, assembly):
        # Store assembly instructions in IMEM
        for i in range(len(assembly)):
            if (i < self.IMEM_MAX):
                self.IMEM[i] = assembly[i]

    # Reset the processor
    def __reset(self):
        # Empty all instructions memory locations
        for i in range(self.IMEM_MAX):
            self.IMEM[i] = ''
        # Set all data memory locations to 0
        for i in range(self.DMEM_MAX):
            self.DMEM[i] = 0
        # Set all registers to 0
        for i in range(self.REG_MAX):
            self.REG[i] = 0
        # Set program counter to 0
        self.PC = 0

    # Print all IMEM, DMEM, and REG values
    def __print_begin(self):
        msg = ''
        print('\nInstruction Memory Contents')
        for i in range(self.IMEM_MAX):
            if (i % 3 == 0):
                print(msg)
                msg = ''
            msg += 'IMEM[' + str(i) + '] = ' + str(self.IMEM[i]) + '   '
        if (msg != ''):
            print(msg)
            msg = ''
        print('\nData Memory Contents')
        for i in range(self.DMEM_MAX):
            if (i % 3 == 0):
                print(msg)
                msg = ''
            msg += 'DMEM[' + str(i) + '] = ' + str(self.DMEM[i]) + '   '
        if (msg != ''):
            print(msg)
            msg = ''
        print('\nRegister Contents')
        for i in range(self.REG_MAX):
            if (i % 3 == 0):
                print(msg)
                msg = ''
            msg += 'REG[' + str(i) + '] = ' + str(self.REG[i]) + '   '
        if (msg != ''):
            print(msg)
            msg = ''
        print()
    
    # Print all DMEM and REG values
    def __print_end(self):
        msg = ''
        print('\nData Memory Contents')
        for i in range(self.DMEM_MAX):
            if (i % 3 == 0):
                print(msg)
                msg = ''
            msg += 'DMEM[' + str(i) + '] = ' + str(self.DMEM[i]) + '   '
        if (msg != ''):
            print(msg)
            msg = ''
        print('\nRegister Contents')
        for i in range(self.REG_MAX):
            if (i % 3 == 0):
                print(msg)
                msg = ''
            msg += 'REG[' + str(i) + '] = ' + str(self.REG[i]) + '   '
        if (msg != ''):
            print(msg)
            msg = ''
        print()

    # Add all values in DMEM to REGs
    def __add_DMEM(self):
        for i in range(len(self.DMEM)):
            self.REG[i] = self.DMEM[i]

    # Get condition codes based on ALU_output
    def __get_condition_codes(self):
        if (self.ALU_output < 0):
            self.N = True
        else:
            self.N = False
        if (self.ALU_output == 0):
            self.Z = True
        else:
            self.Z = False

    # Receive the instruction from IMEM at the PC location and increase PC
    def __instruction_fetch(self):
        self.current_instruction = self.IMEM[self.PC]
        print('Executing ' + self.current_instruction)
        self.PC += 1

    # Decode the instructions and read from the registers
    def __instruction_decode(self):
        instruction_split = self.current_instruction.split()
        self.current_opcode = instruction_split[0]
        if (self.OP_CONVERSION[self.current_opcode] == 'R'):
            self.A = self.REG[int(instruction_split[3])]
            if (self.current_opcode == '1690' or self.current_opcode == '1691'): ## If LSL or LSR
                self.B = int(instruction_split[2])
            else:
                self.B = self.REG[int(instruction_split[1])]
            self.WB = int(instruction_split[4])
        elif (self.OP_CONVERSION[self.current_opcode] == 'I'):
            self.A = self.REG[int(instruction_split[2])]
            self.Imm = int(instruction_split[1])
            self.WB = int(instruction_split[3])
        elif (self.OP_CONVERSION[self.current_opcode] == 'D'):
            self.A = self.REG[int(instruction_split[3])]
            self.Imm = int(instruction_split[1])
            self.WB = int(instruction_split[4])
        elif (self.OP_CONVERSION[self.current_opcode] == 'CB'):
            if (self.current_opcode == '679'):  # if B.__
                self.B = int(instruction_split[2])
            else:                               # if CBZ/CBNZ
                self.B = self.REG[int(instruction_split[2])]
            self.Imm = int(instruction_split[1])
        elif (self.OP_CONVERSION[self.current_opcode] == 'B'):
            self.Imm = int(instruction_split[1])

    # Execute the instruction
    def __execute(self):
        if (self.OP_CONVERSION[self.current_opcode] == 'R'):
            if (self.current_opcode == '1112'):     # ADD
                self.ALU_output = self.A + self.B
            elif (self.current_opcode == '1624'):   # SUB
                self.ALU_output = self.A - self.B
            elif (self.current_opcode == '1880'):   # SUBS
                self.ALU_output = self.A - self.B
                self.__get_condition_codes()
            elif (self.current_opcode == '1104'):   # AND
                self.ALU_output = self.A & self.B
            elif (self.current_opcode == '1360'):   # ORR
                self.ALU_output = self.A | self.B
            elif (self.current_opcode == '1872'):   # EOR
                self.ALU_output = self.A ^ self.B
            elif (self.current_opcode == '1691'):   # LSL
                self.ALU_output = self.A << self.B
            elif (self.current_opcode == '1690'):   # LSR
                self.ALU_output = self.A >> self.B
        elif (self.OP_CONVERSION[self.current_opcode] == 'I'):
            if (self.current_opcode == '1160'):     # ADDI
                self.ALU_output = self.A + self.Imm
            elif (self.current_opcode == '1672'):   # SUBI
                self.ALU_output = self.A - self.Imm
            elif (self.current_opcode == '1928'):   # SUBSIS
                self.ALU_output = self.A - self.Imm
                self.__get_condition_codes()
            elif (self.current_opcode == '584'):    # ANDI
                self.ALU_output = self.A & self.Imm
            elif (self.current_opcode == '712'):    # ORRI
                self.ALU_output = self.A | self.Imm
            elif (self.current_opcode == '840'):    # EORI
                self.ALU_output = self.A ^ self.Imm
        elif (self.OP_CONVERSION[self.current_opcode] == 'D'):
            if (self.current_opcode == '1986'):     # LDUR
                self.ALU_output = self.A + self.Imm
            elif (self.current_opcode == '1984'):   # STUR
                self.ALU_output = self.A + self.Imm
        elif (self.OP_CONVERSION[self.current_opcode] == 'CB'):
            if (self.current_opcode == '679'):
                if (self.B == 0 and self.Z):                        # B.EQ
                    self.PC = (self.PC - 1) + self.Imm
                elif (self.B == 1 and not self.Z):                  # B.NE
                    self.PC = (self.PC - 1) + self.Imm
                elif (self.B == 10 and not self.N):                 # B.GE
                    self.PC = (self.PC - 1) + self.Imm
                elif (self.B == 11 and self.N):                     # B.LT
                    self.PC = (self.PC - 1) + self.Imm
                elif (self.B == 12 and not self.Z and not self.N):  # B.GT
                    self.PC = (self.PC - 1) + self.Imm
                elif (self.B == 13 and self.Z and self.N):          # B.LE
                    self.PC = (self.PC - 1) + self.Imm
            elif (self.current_opcode == '180'):    # CBZ
                if (self.B == 0):
                    self.PC = (self.PC - 1) + self.Imm
            elif (self.current_opcode == '181'):    # CBNZ
                if (self.B != 0):
                    self.PC = (self.PC - 1) + self.Imm
        elif (self.OP_CONVERSION[self.current_opcode] == 'B'):
            self.PC = (self.PC - 1) + self.Imm

    # Access data memory (only for loads and stores)
    def __memory_access(self):
        if (self.OP_CONVERSION[self.current_opcode] == 'D'):
            if (self.current_opcode == '1986'):     # LDUR
                self.LMD = self.DMEM[self.ALU_output]   # Get value from DMEM as load it into LMD
            elif (self.current_opcode == '1984'):   # STUR
                self.DMEM[self.ALU_output] = self.REG[self.WB]  # Get value from Rt registers and store into DMEM 

    # Write values to registers
    def __write_back(self):
        if (self.WB == 31): # Register 31 (XZR) should always be 0
            self.REG[self.WB] = 0
        elif (self.OP_CONVERSION[self.current_opcode] == 'R' or self.OP_CONVERSION[self.current_opcode] == 'I'):  # Any R or I type
            self.REG[self.WB] = self.ALU_output
        elif (self.OP_CONVERSION[self.current_opcode] == 'D' and self.current_opcode == '1986'):                # LDUR
            self.REG[self.WB] = self.LMD

# Public
    # Set DMEM pre processing
    def set_DMEM(self, address, value):
        if (address < self.DMEM_MAX):
            self.DMEM[address] = value
        else:
            print('Error: Address is out of data memory scope. Address must be between 0 and ' + str(self.DMEM_MAX))

    # Run the processor
    def process(self, assembly):
        self.__set_IMEM(assembly)
        self.__print_begin()
        #self.__add_DMEM()
        #for i in range(15):
        while self.IMEM[self.PC] != '':
            self.__instruction_fetch()
            self.__instruction_decode()
            self.__execute()
            self.__memory_access()
            self.__write_back()
        self.__print_end()
        self.__reset()