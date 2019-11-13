"""CPU functionality."""

import sys, time

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # random access memory
        self.reg = [0] * 8 # registers
        self.reg[7] = 0xF4 # Stack Pointer

        # internal registers
        self.pc = 0 # program counter
        self.ir = '' # Instruction Register
        self.mar = 0 # Memory Address Register
        self.mdr = 0 # Memory Data Register

        self.running = True # is the program running?
        

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
            print(self.reg[reg_a])
        elif op == 'HLT':
            self.running = False
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'PUSH':
            self.reg[7] -= 1 # stack pointer
            self.ram[self.reg[7]] = self.reg[reg_a]
            # print('test')
            # print(self.reg[reg_a])
        elif op == 'POP':
            self.reg[reg_a] = self.ram[self.reg[7]]
            self.reg[7] += 1 # stack pointer
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
        self.mar = address
        self.mdr = self.ram[self.mar]
        return self.mdr

    def ram_write(self, address, data):
        self.mar = address
        self.mdr = data
        self.ram[self.mar] = self.mdr

    def run(self):
        """Run the CPU."""

        while self.running:
            # get command saved in ram
            command = self.ram[self.pc]
            # string binary command
            command_string = format(command, '#010b')
            # get the first two bits, the instruction_bits
            instruction_bits = command_string[2:4]

            # saved one or two operands
            if instruction_bits == '10':
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)   
            elif instruction_bits == '01':
                operand_a = self.ram_read(self.pc + 1)  

            op_table = {
                '0b10100000': 'ADD',
                '0b10000010': 'LDI',
                '0b01000111': 'PRN',
                '0b00000001': 'HLT',
                '0b10100010': 'MUL',
                '0b01000101': 'PUSH',
                '0b01000110': 'POP',
                '0b01010000': 'CALL',
                '0b00010001': 'RET'
            }

            instrution_size_table = {
                'ADD': 3,
                'LDI': 3,
                'PRN': 2,
                'HLT': 0,
                'MUL': 3,
                'PUSH': 2,
                'POP': 2,
                'CALL': 2,
                'RET': 0,
                'JMP': 0,
            }

            instructions_that_set_pc = ['CALL', 'RET', 'JMP']

            # get name of operation
            self.ir = op_table[command_string]
            # get size of operation instrutions
            instruction_size = instrution_size_table[self.ir]

            # if it is an instruction that sets the pc
            if self.ir in instructions_that_set_pc:
                if self.ir == 'CALL':
                    self.reg[7] = self.pc + 2
                    self.alu('PUSH', 7)
                    self.pc = self.reg[operand_a]
                elif self.ir == 'RET':
                    self.alu('POP', 7)
                    self.pc = self.reg[7]
                elif self.ir == 'JMP':
                    # self.alu('JMP', operand_a)
                    self.pc = self.reg[operand_a]
            else:
                # move to next operation
                self.pc += instruction_size
                # execute ALU method
                self.alu(self.ir, operand_a, operand_b)

            