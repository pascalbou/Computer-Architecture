"""CPU functionality."""

import sys, time

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.MAR = 0
        self.MDR = 0
        self.running = True


    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: 02-fileio02.py <filename>")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as program:
                address = 0
                for line in program:
                    # deal with comments
                    # split before and after any comment symbol '#'
                    comment_split = line.split("#")

                    # convert the pre-comment portion (to the left) from binary to a value
                    # extract the first part of the split to a number variable
                    # and trim whitespace
                    num = comment_split[0].strip()

                    # ignore blank lines / comment only lines
                    if len(num) == 0:
                        continue

                    # set the number to an integer of base 2
                    instruction = int(num, 2)

                    # loads instruction in ram
                    self.ram[address] = instruction
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)        


    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'LDI':
            self.reg[reg_a] = reg_b
        elif op == 'PRN':
            # print(f'self.reg[reg_a] {self.reg[reg_a]}')
            print(self.reg[reg_a])
        elif op == 'HLT':
            self.running = False
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
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

    def ram_read(self, address):
        self.MAR = address
        self.MDR = self.ram[self.MAR]
        return self.MDR

    def ram_write(self, address, data):
        self.MAR = address
        self.MDR = data
        self.ram[self.MAR] = self.MDR

    def run(self):
        """Run the CPU."""

        while self.running:
            command = self.ram[self.pc]
            # print(f'self.pc {self.pc}')
            command_string = format(command, '#010b')
            # print(f'command_string {command_string}')
            instruction_bits = command_string[2:4]
            # print(f'instruction_bits {instruction_bits}')

            if instruction_bits == '10':
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)   
            elif instruction_bits == '01':
                operand_a = self.ram_read(self.pc + 1)
                operand_b = None
            else:
                operand_a = None
                operand_b = None

            # print(f'operand_a {operand_a}')
            # print(f'operand_b {operand_b}')

            if command_string == '0b10000010':
                op = 'LDI'
                instruction_size = 3
            elif command_string == '0b01000111':
                op = 'PRN'
                instruction_size = 2
            elif command_string == '0b00000001':
                op = 'HLT'
            elif command_string == '0b10100010':
                op = 'MUL'


            # print(f'op {op}')
            self.alu(op, operand_a, operand_b)
            self.pc += instruction_size
            # time.sleep(1)

            
            