"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.is_running = False
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.reg[7] = 0b11110100
        self.sp = 7
        self.fl = 0b00000000

    def load(self, filename):
        """Load a program into memory."""
        print('\nloading file...')
        filename = sys.argv[1]
        try:
            address = 0
            with open(filename) as file:
                for line in file:
                    split_line = line.split('#')[0]
                    command = split_line.strip()
                    if command:
                        instruction = int(command, 2)
                        print(f'{instruction:8b} is {instruction}')
                        self.ram[address] = instruction
                        address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} file not found.')
            sys.exit()

    if len(sys.argv) < 2:
        print(f'please provide a second file to load with this program as such: python cpu.py [insert second file here]')
        sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    # should accept the address to read and return the value stored there.
    def ram_read(self, MAR):
        return self.ram[MAR]

    # should accept a value to write, and the address to write it to.
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001 #1
        LDI = 0b10000010 #130
        PRN = 0b01000111 #71
        ADD = 0b10100000
        MUL = 0b10100010 #162
        POP = 0b01000110
        PSH = 0b01000101
        CAL = 0b01010000
        RET = 0b00010001
        CMP = 0b10100111 # 167
        JEQ = 0b01010101 # 85
        JMP = 0b01010100 # 84
        JNE = 0b01010110 # 86

        self.is_running = True

        print(f'\n ({self.is_running}) Now running...\n')

        while self.is_running:

            IR = self.ram_read(self.pc)
            # print(f'IR: {IR}')
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR == HLT:
                print(f'\n Goodbye...')
                self.is_running = False

            elif IR == LDI:
                # self.ram_write(operand_a, operand_b)
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif IR == PRN:
                # print(self.ram_read(self.ram[self.pc+1]))
                print(self.reg[operand_a])
                self.pc += 2
            
            elif IR == ADD:
                print('ADD')
                total = self.reg[operand_a] + self.reg[operand_b]
                print(f'{self.reg[operand_a]} + {self.reg[operand_b]}')
                self.reg[operand_a] = total
                print('TOTAL: ')
                self.pc += 3

            elif IR == MUL:
                print('MULTIPLY')
                product = self.reg[operand_a] * self.reg[operand_b]
                print(f'{self.reg[operand_a]} * {self.reg[operand_b]}')
                self.reg[operand_a] = product
                self.pc += 3
                print('PRODUCT: ')

            elif IR == PSH:
                print('PUSH')
                self.reg[self.sp] -= 1
                reg_num = self.ram[self.pc + 1]
                value = self.reg[reg_num]
                top = self.reg[self.sp]
                self.ram[top] = value

                self.pc += 2


            elif IR == POP:
                print('POP')
                top = self.reg[self.sp]
                value = self.ram[top]
                reg_num = self.ram[self.pc + 1]
                self.reg[reg_num] = value

                self.reg[self.sp] += 1
                self.pc += 2

            
            elif IR == CAL:
                # print('CALL')
                #pushes return address to stack
                address = self.pc + 2
                self.sp -= 1
                self.ram[self.sp] = address

                # calls subroutine
                reg_num = self.ram[self.pc + 1]
                self.pc = self.reg[reg_num]

            elif IR == RET:
                # print('RET')
                # get our return address that was added to stack
                address = self.ram[self.sp]
                self.reg[self.sp] += 1

                # set pc to it
                self.pc = address
                # to space out each function after it's ready to return
                print('')
            
            # compares values in two registers
            elif IR == CMP:
                # print('CMP')
                value_1 = self.reg[operand_a]
                value_2 = self.reg[operand_b]

                # sets self.fl according to comparison, the structure is 0b00000LGE
                if value_1 < value_2:           # set L
                    self.fl = 0b00000100
                elif value_1 > value_2:         # set G
                    self.fl = 0b00000010
                elif value_1 == value_2:        # set E
                    self.fl = 0b00000001

                self.pc += 3

            # handles if the "E" in 0b00000LGE
            elif IR == JEQ:
                # print('JEQ')
                # if "E" in LGE is true (LG1), jump to given register
                if self.fl == 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif IR == JMP:
                # print('JMP')
                # jumps to given address (sets our self.pc to given register)
                self.pc = self.reg[operand_a]
                                                    
            # handles if the "E" in LGE is false (lG0)
            elif IR == JNE:
                # same check as JEQ but this time NOT equal to
                if self.fl != 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
                
            else:
                self.pc += 1 

                