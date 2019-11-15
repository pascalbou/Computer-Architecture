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
        self.fl = 0b000 # flag

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
        elif op == 'POP':
            self.reg[reg_a] = self.ram[self.reg[7]]
            self.reg[7] += 1 # stack pointer
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b001
            # elif self.reg[reg_a] > self.reg[reg_b]:
            #     self.fl = 0b010
            # elif self.reg[reg_a] < self.reg[reg_b]:
            #     self.fl = 0b100
            else:
                self.fl = 0b000
        elif op == 'ADDI':
            self.reg[reg_a] += reg_b
        elif op == 'AND':
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == 'OR':
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == 'NOT':
            self.reg[reg_a] = ~(self.reg[reg_a])
        elif op == 'SHL':
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == 'SHR':
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == 'MOD':
            if self.reg[reg_b] == 0:
                raise Exception("Cannot divide by 0")
            else:
                self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
        elif op == 'ST':
            self.reg[reg_a] = self.reg[reg_b]
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
                '0b00010001': 'RET',
                '0b10100111': 'CMP',
                '0b01010100': 'JMP',
                '0b01010101': 'JEQ',
                '0b01010110': 'JNE',
                '0b10100001': 'ADDI', # coded invented, not in doc
                '0b10101000': 'AND',
                '0b10101010': 'OR',
                '0b01101001': 'NOT',
                '0b10101100': 'SHL',
                '0b10101101': 'SHR',
                '0b10100100': 'MOD',
                '0b10101011': 'XOR',
                '0b10000100': 'ST',
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
                'JMP': 2,
                'CMP': 3,
                'JEQ': 2,
                'JNE': 2,
                'ADDI': 2,
                'AND': 3,
                'OR': 3,
                'NOT': 2,
                'SHL': 3,
                'SHR': 3,
                'MOD': 3,
                'XOR': 3,
                'ST': 3,
            }

            instructions_that_set_pc = ['CALL', 'RET', 'JMP', 'JEQ', 'JNE', 'XOR']

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
                elif self.ir == 'JEQ':
                    if self.fl == 0b001:
                        self.ir = 'JMP'
                    else:
                        self.pc += instruction_size
                elif self.ir == 'JNE':
                    if self.fl == 0b000:
                        self.ir = 'JMP'
                    else:
                        self.pc += instruction_size
                elif self.ir == 'XOR':
                    # XOR = ((OR) AND (NAND))
                    operand_c = operand_a + 2
                    self.reg[operand_c] = self.reg[operand_a]
                    self.alu('OR', operand_a, operand_b)
                    self.alu('AND', operand_c, operand_b)
                    self.alu('NOT', operand_c,)
                    self.alu('AND', operand_a, operand_c)
                # extras ALU gates
                # elif self.ir == 'NAND':
                #     # NAND = NOT(AND)
                #     self.alu('AND', operand_a, operand_b)
                #     self.alu('NOT', operand_a)   
                # elif self.ir == 'NOR':
                #     # NOR = ((XOR) XOR (NAND))  
                #     operand_c = operand_a + 2
                #     self.reg[operand_c] = self.reg[operand_a]
                #     self.alu('XOR', operand_a, operand_b)
                #     self.alu('AND', operand_c, operand_b)
                #     self.alu('NOT', operand_c,)
                #     self.alu('XOR', operand_a, operand_c)                    
    
                if self.ir == 'JMP':
                    self.pc = self.reg[operand_a]
            else:
                # move to next operation
                self.pc += instruction_size
                # execute ALU method
                self.alu(self.ir, operand_a, operand_b)

            # == Debugging ==
            # time.sleep(1)
            # print(self.ir)
            # print(operand_a)
            # print(operand_b)
            # print(self.reg)
            # print(self.fl)