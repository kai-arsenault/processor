import os.path

from assembler import Assembler

def main():
    print('Enter file name for ARMv8 code: ')
    path = input()

    if (os.path.isfile(path)):
        ARMv8_assembler = Assembler(path)
        print(ARMv8_assembler.decimal_to_list())
        print(ARMv8_assembler.binary_to_list())
    else:
        print('Error: Invalid path')

if __name__ == '__main__':
    main()