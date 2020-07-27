import os.path

class Assembler:
    # Key: OPCode | Value: [Decimal value, format]
    OP_CONVERSION = {
        'ADD' : ['1112', 'R'],
        'SUB' : ['1624','R'],
        'SUBS' : ['1880','R'],
        'AND' : ['1104','R'],
        'ORR' : ['1360','R'],
        'EOR' : ['1872','R'],
        'LSL' : ['1691','R'],
        'LSR' : ['1690','R'],
        'ADDI' : ['1160','I'],
        'SUBI' : ['1672','I'],
        'SUBIS' : ['1928','I'],
        'ANDI' : ['584','I'],
        'ORRI' : ['712','I'],
        'EORI' : ['840','I'],
        'LDUR' : ['1986','D'],
        'STUR' : ['1984','D'],
        'CBZ' : ['180','CB'],
        'CBNZ' : ['181','CB'],
        'B.EQ' : ['679','CB'],
        'B.NE' : ['679','CB'],
        'B.GE' : ['679','CB'],
        'B.LT' : ['679','CB'],
        'B.GT' : ['679','CB'],
        'B.LE' : ['679','CB'],
        'B' : ['5','B']
    }

    # Key: OPCode | Value: RT value for CB-format
    CB_RT_CONVERSION = {
        'B.EQ' : '0',
        'B.NE' : '1',
        'B.GE' : '10',
        'B.LT' : '11',
        'B.GT' : '12',
        'B.LE' : '13'
    }

    # Key: Label | Value: Line #
    labels = {}
    
    def __init__(self, path):
        self.path = path
        if (os.path.isfile('temp.txt')):
            os.remove('temp.txt')
        with open(path, 'r') as IFile, open('temp.txt', 'a+') as temp_file:
            # First pass: deal with labels (record location and remove), replace XZR with X31
            line_num = 0
            for line in IFile:
                if ('XZR' in line):
                    line = line.replace('XZR', 'X31')
                if ('//' in line):
                    line = line.split('//')[0].rstrip()
                    line = line + '\n'
                if (':' in line):
                    temp_file.write(line.split(':')[1].lstrip())
                    self.labels[line.split(':')[0]] = line_num
                else:
                    temp_file.write(line.lstrip())
                line_num = line_num + 1
# Private
    def __get_decimal(self, opcode, data, line_num, type):
        opc = self.OP_CONVERSION[opcode][0]
        if (type == 'R'):
            if (opcode == 'LSL' or opcode == 'LSR'):
                rm = '0'
                shamt = data.split()[2][1:]
            else:
                rm = data.split()[2][1:]
                shamt = '0'
            rn = data.split()[1][1:-1]
            rd = data.split()[0][1:-1]
            decimal_form = opc + ' ' + rm + ' ' + shamt + ' ' + rn + ' ' + rd
        elif (type == 'I'):
            immediate = data.split()[2][1:]
            rn = data.split()[1][1:-1]
            rd = data.split()[0][1:-1]
            decimal_form = opc + ' ' + immediate + ' ' + rn + ' ' + rd
        elif (type == 'D'):
            address = data.split()[2][1:-1]
            op2 = '0'
            rn = data.split()[1][2:-1]
            rt = data.split()[0][1:-1]
            decimal_form = opc + ' ' + address + ' ' + op2 + ' ' + rn + ' ' + rt 
        elif (type == 'CB'):
            if (opcode == 'CBZ' or opcode == 'CBNZ'):
                address = str(self.labels[data.split()[1]] - line_num)
                rt = data.split()[0].lstrip()[1:-1]
            else:
                address = str(self.labels[data] - line_num)
                rt = self.CB_RT_CONVERSION[opcode]
            decimal_form = opc + ' ' + address + ' ' + rt
        else:
            address = str(self.labels[data.lstrip()] - line_num)
            decimal_form = opc + ' ' + address
        return decimal_form

    def __convert_binary(self, decimal, size):
        decimal = int(decimal)
        binary = str(bin(decimal)).split('b')[1]
        binary = binary.zfill(size)
        if (decimal < 0):
            if ((int(binary, 2) & (1 << (size - 1))) != 1):
                binary = str(bin(int(binary, 2) - (1 << size)).split('b')[1])
        return binary

    def __getBinary(self, decimal, type):
        decimal = decimal.split()
        if (type == 'R'):
            opc = self.__convert_binary(decimal[0], 11)
            rm = self.__convert_binary(decimal[1], 5)
            shamt = self.__convert_binary(decimal[2], 6)
            rn = self.__convert_binary(decimal[3], 5)
            rd = self.__convert_binary(decimal[4], 5)
            binary_form = opc + ' ' + rm + ' ' + shamt + ' ' + rn + ' ' + rd
        elif (type == 'I'):
            opc = self.__convert_binary(decimal[0], 10)
            immediate = self.__convert_binary(decimal[1], 12)
            rn = self.__convert_binary(decimal[2], 5)
            rd = self.__convert_binary(decimal[3], 5)
            binary_form = opc + ' ' + immediate + ' ' + rn + ' ' + rd
        elif (type == 'D'):
            opc = self.__convert_binary(decimal[0], 11)
            address = self.__convert_binary(decimal[1], 9)
            op2 = self.__convert_binary(decimal[2], 2)
            rn = self.__convert_binary(decimal[3], 5)
            rt = self.__convert_binary(decimal[4], 5)
            binary_form = opc + ' ' + address + ' ' + op2 + ' ' + rn + ' ' + rt 
        elif (type == 'CB'):
            opc = self.__convert_binary(decimal[0], 8)
            address = self.__convert_binary(decimal[1], 19)
            rt = self.__convert_binary(decimal[2], 5)
            binary_form = opc + ' ' + address + ' ' + rt
        else:
            opc = self.__convert_binary(decimal[0], 6)
            address = self.__convert_binary(decimal[1], 26)
            binary_form = opc + ' ' + address
        return binary_form

# Public
    def to_files(self):
        with open('temp.txt', 'r') as temp_file, open('decimal.txt', 'a+') as D_OFile, open('binary.txt', 'a+') as B_OFile:
            D_OFile.write('See ' + self.path + ' for source code\n')
            B_OFile.write('See ' + self.path + ' for source code\n')
            # Second pass: convert
            line_num = 0
            for line in temp_file:
                opcode = line.split(' ', 1)[0]
                data = line.split(' ', 1)[1].rstrip()
                if (opcode in self.OP_CONVERSION):
                    opcodeFormat = self.OP_CONVERSION[opcode][1]
                    if (opcodeFormat == 'R'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    elif (opcodeFormat == 'I'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    elif (opcodeFormat == 'D'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    elif (opcodeFormat == 'CB'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    else:
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    D_OFile.write(d_line)
                    B_OFile.write(b_line)
                else:
                    D_OFile.write('Error: ' + opcode + ' not found')
                    B_OFile.write('Error: ' + opcode + ' not found')
                line_num = line_num + 1

    def decimal_to_list(self):
        decimal_list = []
        with open('temp.txt', 'r') as temp_file:
            # Second pass: convert
            line_num = 0
            for line in temp_file:
                opcode = line.split(' ', 1)[0]
                data = line.split(' ', 1)[1].rstrip()
                if (opcode in self.OP_CONVERSION):
                    opcodeFormat = self.OP_CONVERSION[opcode][1]
                    if (opcodeFormat == 'R'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                    elif (opcodeFormat == 'I'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                    elif (opcodeFormat == 'D'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                    elif (opcodeFormat == 'CB'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                    else:
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                    decimal_list.append(d_line)
                else:
                    decimal_list.append('Error: ' + opcode + ' not found')
                line_num = line_num + 1
        self.decimal_list = decimal_list
        return decimal_list

    def binary_to_list(self):
        binary_list = []
        with open('temp.txt', 'r') as temp_file:
            # Second pass: convert
            line_num = 0
            for line in temp_file:
                opcode = line.split(' ', 1)[0]
                data = line.split(' ', 1)[1].rstrip()
                if (opcode in self.OP_CONVERSION):
                    opcodeFormat = self.OP_CONVERSION[opcode][1]
                    if (opcodeFormat == 'R'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    elif (opcodeFormat == 'I'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    elif (opcodeFormat == 'D'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    elif (opcodeFormat == 'CB'):
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    else:
                        d_line = self.__get_decimal(opcode, data, line_num, opcodeFormat)
                        b_line = self.__getBinary(d_line, opcodeFormat)
                    binary_list.append(b_line)
                else:
                    binary_list.append('Error: ' + opcode + ' not found')
                line_num = line_num + 1
        self.binary_list = binary_list
        return binary_list
