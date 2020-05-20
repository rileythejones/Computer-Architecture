"""CPU functionality."""

import sys


PUSH = 0b01000101 
POP = 0b01000110

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b00000000] * 256
        self.reg = [0b00000000] * 8
        self.pc = 0
        
        self.sp = 7 
        self.reg[self.sp] = 0xF4


    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self, load_file=None):
        """Load a program into memory."""
        
        address = 0 
        
        if load_file is not None: 
            print("loading file")
            with open(load_file) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if line == '':
                        continue
                    self.ram[address] = int(line,2)
                    address += 1
                    
        else:
            print("Run default")
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
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        if op == "MUL":
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

    def run(self):
        
        ir = self.pc
        halt = False 

        while halt == False:
            
            opcode = self.ram_read(ir)
            
            operand_A, operand_B = self.ram_read(ir + 1), self.ram_read(ir + 2)
            
            if opcode == HLT:
                halt = True 
                print("Halt")
                return  

            if opcode == LDI:
                self.reg[operand_A] = operand_B
                ir += 3 
            
            if opcode == PRN:
                print(self.reg[operand_A])
                ir += 2

            if opcode == MUL:
                self.alu('MUL', operand_A, operand_B)
                ir += 3
                
            if opcode == PUSH:
                self.reg[self.sp] -= 1   
                val = self.reg[self.ram[ir + 1]]  
                address = self.reg[self.sp]
                self.ram[address] = val   
                ir += 2

            if opcode == POP:
                val = self.ram[self.reg[self.sp]]
                reg = self.ram[ir + 1]
                self.reg[reg] = val
                self.reg[self.sp] += 1   
                ir += 2
