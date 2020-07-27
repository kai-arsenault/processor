import os.path

from assembler import Assembler
from processor import Processor

def main():
    print('Enter file name for ARMv8 code: ')
    path = input()

    if (os.path.isfile(path)):
        ARMv8_assembler = Assembler(path)
        assembly = ARMv8_assembler.decimal_to_list()
    else:
        print('Error: Invalid path')
        exit(0)
    
    ARMv8_processor = Processor()
    
    while True:
        address = input('Enter address for DMEM or just press ENTER to skip: ')
        if (address == ''):
            break  
        value = input('Enter value for DMEM: ')
        ARMv8_processor.set_DMEM(int(address), int(value))
        print('Added DMEM[' + address + '] = ' + value + '\n')

    ARMv8_processor.process(assembly)

if __name__ == '__main__':
    main()