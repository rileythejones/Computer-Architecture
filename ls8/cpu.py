"""CPU functionality."""
import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001

class CPU:

    def __init__(self):

        self.ram = [0b00000000] * 256
        self.reg = [0b00000000] * 8
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xf4
        self.halt = False 
         
    def read(self, address):
        return self.ram[address]

    def write(self, address, value):
        self.ram[address] = value

    def load(self, load_file=None):
        
        self.address = 0
        
        if load_file is not None: 
            print("loading file")
            with open(load_file) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if line == '':
                        continue
                    self.ram[self.address] = int(line,2)
                    self.address += 1
                    
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
                self.ram[self.address] = instruction
                self.address += 1

    def alu(self, op, reg_a, reg_b):

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        
        
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.read(self.pc),
            self.read(self.pc + 1),
            self.read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')


    def run(self):
        """Run the CPU."""

        while self.halt == False:
            op, a, b = self.read(self.pc), self.read(self.pc + 1), self.read(self.pc + 2)

            if op == LDI:
                """ Set the value of a register to an integer. """
                self.reg[a] = b
                self.pc += 3
                
            elif op == PRN:
                """ Print numeric value stored in the given register. """
                print(self.reg[a])
                self.pc += 2
                
            elif op == MUL:
                """ Multiply the values in two registers together and store the result in registerA. """
                self.alu('MUL', a, b)
                self.pc += 3
                
            elif op == ADD:
                self.alu('ADD', a, b)
                self.pc += 3
                
            elif op == PUSH:
                """ Push the value in the given register on the stack.
                    Decrement the SP.
                    Copy the value in the given register to the address pointed to by SP."""
                self.reg[self.sp] -= 1
                self.write(self.reg[self.sp], self.reg[a])
                self.pc += 2
                
            elif op == POP:
                """ Pop the value at the top of the stack into the given register.

                    Copy the value from the address pointed to by SP to the given register.
                    Increment SP.
                """
                self.reg[a] = self.read(self.reg[self.sp])
                self.reg[self.sp] += 1
                self.pc += 2
                
            elif op == CALL:
                """
                Calls a subroutine (function) at the address stored in the register.

                The address of the instruction directly after CALL is pushed onto the stack. 
                This allows us to return to where we left off when the subroutine finishes executing.
                The PC is set to the address stored in the given register. 
                We jump to that location in RAM and execute the first instruction in the subroutine. 
                The PC can move forward or backwards from its current location.
                """
                return_addr = self.pc + 2
                self.reg[self.sp] -= 1
                self.write(self.reg[self.sp], return_addr)
                self.pc = self.reg[a]
                
            elif op == RET:
                """
                Return from subroutine.

                Pop the value from the top of the stack and store it in the PC.
                """
                
                return_addr = self.read(self.reg[self.sp])
                self.reg[self.sp] += 1
                self.pc = return_addr
                
            elif op == HLT:
                """ Halt the CPU (and exit the emulator). """
                self.halt = True
            else:
                print(f'Unknown instruction {op} at address {self.pc}')
                sys.exit(1)
    