import os.path

class Assembler:
    # Key: OPCode | Value: [Decimal value, format]
    OP_CONVERSION = {
        'ADD' : ['1112', 'R'],
        'SUB' : ['1624','R'],
        'SUBS' : ['1880','R'],
        'AND' : ['1112','R'],
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
        'B.EQ' : ['679','CB','0'],
        'B.NE' : ['679','CB','1'],
        'B.GE' : ['679','CB','10'],
        'B.LT' : ['679','CB','11'],
        'B.GT' : ['679','CB','12'],
        'B.LE' : ['679','CB','13'],
        'B' : ['5','B']
    }

    # Key: Label | Value: Line #
    labels = {}
    
    def __init__(self, path):
        if (os.path.isfile('temp.txt')):
            os.remove('temp.txt')
        with open(path, 'r') as IFile, open('temp.txt', 'a+') as tempFile, open('decimal.txt', 'w+') as D_OFile, open('binary.txt', 'w+') as B_OFile:
            D_OFile.write('See ' + path + ' for source code\n')
            B_OFile.write('See ' + path + ' for source code\n')
            # First pass: deal with labels (record location and remove), replace XZR with X31
            lineNum = 0
            for line in IFile:
                if ('XZR' in line):
                    line = line.replace('XZR', 'X31')
                if (':' in line):
                    tempFile.write(line.split(':')[1].lstrip())
                    self.labels[line.split(':')[0]] = lineNum
                else:
                    tempFile.write(line.lstrip())
                lineNum = lineNum + 1

    def convertR(self, opcode, data):
        opc = self.OP_CONVERSION[opcode][0]
        if (opcode == 'LSL' or opcode == 'LSR'):
            rm = '0'
            shamt = data.split()[2][1:]
        else:
            rm = data.split()[2][1:]
            shamt = '0'
        rn = data.split()[1][1:-1]
        rd = data.split()[0][1:-1]
        decimalForm = opc + ' ' + rm + ' ' + shamt + ' ' + rn + ' ' + rd
        return decimalForm

    def convertI(self, opcode, data):
        opc = self.OP_CONVERSION[opcode][0]
        immediate = data.split()[2][1:]
        rn = data.split()[1][1:-1]
        rd = data.split()[0][1:-1]
        decimalForm = opc + ' ' + immediate + ' ' + rn + ' ' + rd
        return decimalForm

    def convertD(self, opcode, data):
        opc = self.OP_CONVERSION[opcode][0]
        address = data.split()[2][1:-1]
        op2 = '0'
        rn = data.split()[1][2:-1]
        rt = data.split()[0][1:-1]
        decimalForm = opc + ' ' + address + ' ' + op2 + ' ' + rn + ' ' + rt 
        return decimalForm

    def convertCB(self, opcode, data, lineNum):
        opc = self.OP_CONVERSION[opcode][0]
        address = str(self.labels[data] - lineNum)
        rt = self.OP_CONVERSION[opcode][2]
        decimalForm = opc + ' ' + address + ' ' + rt
        return decimalForm

    def convertB(self, opcode, data, lineNum):
        opc = self.OP_CONVERSION[opcode][0]
        address = str(self.labels[data] - lineNum)
        decimalForm = opc + ' ' + address
        return decimalForm

    def convertBinary(self, decimal, size):
        decimal = int(decimal)
        binary = str(bin(decimal)).split('b')[1]
        binary = binary.zfill(size)
        if (decimal < 0):
            if ((int(binary, 2) & (1 << (size - 1))) != 1):
                binary = str(bin(int(binary, 2) - (1 << size)).split('b')[1])
        return binary

    def getBinary(self, decimal, type):
        decimal = decimal.split()
        print(decimal)
        if (type == 'R'):
            opc = self.convertBinary(decimal[0], 11)
            rm = self.convertBinary(decimal[1], 5)
            shamt = self.convertBinary(decimal[2], 6)
            rn = self.convertBinary(decimal[3], 5)
            rd = self.convertBinary(decimal[4], 5)
            binaryForm = opc + ' ' + rm + ' ' + shamt + ' ' + rn + ' ' + rd
        elif (type == 'I'):
            opc = self.convertBinary(decimal[0], 10)
            immediate = self.convertBinary(decimal[1], 12)
            rn = self.convertBinary(decimal[2], 5)
            rd = self.convertBinary(decimal[3], 5)
            binaryForm = opc + ' ' + immediate + ' ' + rn + ' ' + rd
        elif (type == 'D'):
            opc = self.convertBinary(decimal[0], 11)
            address = self.convertBinary(decimal[1], 9)
            op2 = self.convertBinary(decimal[2], 2)
            rn = self.convertBinary(decimal[3], 5)
            rt = self.convertBinary(decimal[4], 5)
            binaryForm = opc + ' ' + address + ' ' + op2 + ' ' + rn + ' ' + rt 
        elif (type == 'CB'):
            opc = self.convertBinary(decimal[0], 8)
            address = self.convertBinary(decimal[1], 19)
            rt = self.convertBinary(decimal[2], 5)
            binaryForm = opc + ' ' + address + ' ' + rt
        else:
            opc = self.convertBinary(decimal[0], 6)
            address = self.convertBinary(decimal[1], 26)
            binaryForm = opc + ' ' + address
        return binaryForm

    def convert(self):
        with open('temp.txt', 'r') as tempFile, open('decimal.txt', 'a+') as D_OFile, open('binary.txt', 'a+') as B_OFile:
            # Second pass: convert
            lineNum = 0
            for line in tempFile:
                opcode = line.split(' ', 1)[0]
                data = line.split(' ', 1)[1].rstrip()
                if (opcode in self.OP_CONVERSION):
                    opcodeFormat = self.OP_CONVERSION[opcode][1]
                    if (opcodeFormat == 'R'):
                        d_line = self.convertR(opcode, data)
                        b_line = self.getBinary(d_line, 'R')
                    elif (opcodeFormat == 'I'):
                        d_line = self.convertI(opcode, data)
                        b_line = self.getBinary(d_line, 'I')
                    elif (opcodeFormat == 'D'):
                        d_line = self.convertD(opcode, data)
                        b_line = self.getBinary(d_line, 'D')
                    elif (opcodeFormat == 'CB'):
                        d_line = self.convertCB(opcode, data, lineNum)
                        b_line = self.getBinary(d_line, 'CB')
                    else:
                        d_line = self.convertB(opcode, data, lineNum)
                        b_line = self.getBinary(d_line, 'B')
                    D_OFile.write(d_line + '\n')
                    B_OFile.write(b_line + '\n')
                else:
                    D_OFile.write('Error: ' + opcode + ' not found')
                    B_OFile.write('Error: ' + opcode + ' not found')
                lineNum = lineNum + 1

def main():
    print('Enter file name for LEGv8 code: ')
    path = input()

    if (os.path.isfile(path)):
        LEGv8_Assembler = Assembler(path)
        LEGv8_Assembler.convert()
    else:
        print('Error: Invalid path')


if __name__ == '__main__':
    main()