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

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            # print(self.ram[address])
            address += 1


    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'LDI':
            self.reg[reg_a] = reg_b
        elif op == 'PRN':
            self.reg[reg_a] = reg_a
            print('printing')
            print(self.reg[reg_a])
        elif op == 'HLT':
            self.running = False
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
            # print(self.pc)

            instruction_bits = str(bin(command))[2:4]
            # print(str(bin(command)))
            print(instruction_bits)
            # print(type(instruction_bits))
            if instruction_bits == '10':
                # print('works')
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)   
            elif instruction_bits == '01':
                operand_a = self.ram_read(self.pc + 1)
                operand_b = None
            else:
                operand_a = None
                operand_b = None

            # print(operand_a)
            # print(operand_b)

            if str(bin(command)) == '0b10000010':
                # print('works')
                op = 'LDI'
                self.pc += 3
            elif str(bin(command)) == '0b1000111':
                op = 'PRN'
                self.pc += 2
            elif str(bin(command)) == '0b1':
                op = 'HLT'
                self.pc = 0


            # print(op)
            self.alu(op, operand_a, operand_b)
            time.sleep(1)
            
            