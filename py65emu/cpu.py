#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math, functools

class Registers:
    """ An object to hold the CPU registers. """
    def __init__(self, pc=0):
        self.reset(pc)
        

    def reset(self, pc=0):
        self.a = 0          # Accumulator
        self.x = 0          # General Purpose X
        self.y = 0          # General Purpose Y
        self.s = 0xff       # Stack Pointer
        self.pc = pc        # Program Counter

        self.flagBit = {
            'N': 128,   # N - Negative
            'V': 64,    # V - Overflow
            'B': 16,    # B - Break Command
            'D': 8,     # D - Decimal Mode
            'I': 4,     # I - IRQ Disable
            'Z': 2,     # Z - Zero
            'C': 1      # C - Carry
        }
        self.p = 0          # Flag Pointer - N|V|0|B|D|I|Z|C

    def getFlag(self, flag):
        return bool(self.p & self.flagBit[flag])

    def setFlag(self, flag, v=True):
        if v:
            self.p = self.p | self.flagBit[flag]
        else:
            self.clearFlag(flag)            

    def clearFlag(self, flag):
        self.p = self.p & (255 - self.flagBit[flag])

    def clearFlags(self):
        self.p = 0

    def ZN(self, v):
        """
        The criteria for Z and N flags are standard.  Z gets set if the 
        value is zero and N gets set to the same value as bit 7 of the value.
        """
        self.setFlag('Z', v == 0)
        self.setFlag('N', v & 0x80)


class CPU:
    
    def __init__(self, mmu=None, pc=None, stack_page=0x1):
        self.mmu = mmu
        self.r = Registers()
        self.cc = 0
        # Which page the stack is in.  0x1 means that the stack is from 
        # 0x100-0x1ff.  In the 6502 this is always true but it's different
        # for other 65* varients. 
        self.stack_page = stack_page 
        self.reset()

        if pc:
            self.r.pc = pc
        else:
            # if pc is none get the address from $FFFD,$FFFC
            pass

        self._create_ops()




        
    def reset(self):
        self.r.reset()
        self.mmu.reset()

    def execute(self, instruction):
        """
        Execute a single instruction independent of the program in memory.
        instruction is an array of bytes.
        """
        pass

    def nextByte(self):
        v = self.mmu.read(self.r.pc)
        self.r.pc += 1
        return v

    def nextWord(self):
        low = self.nextByte()
        high = self.nextByte()
        return (high << 8) + low

    def stackPush(self, v):
        self.mmu.write(self.stack_page*0xff + self.r.s, v)
        self.r.s = (self.r.s - 1) & 0xff

    def stackPushWord(self, v):
        self.stackPush(v >> 8)
        self.stackPush(v)

    def stackPop(self):
        v = self.mmu.read(self.stack_page*0xff + ((self.r.s + 1) & 0xff))
        self.r.s = (self.r.s + 1) & 0xff
        return v

    def stackPopWord(self):
        return self.stackPop() + (self.stackPop() << 8)

    def fromBCD(self, v):
        return ((((v&0xf0)/0x10)*10) + (v&0xf))

    def toBCD(self, v):
        return (int(math.floor(v/10))*16 + (v%10))

    def fromTwosCom(self, v):
        return (v & 0x7f) - (v & 0x80)

    interrupts = {
        "ABORT":    0xfff8,
        "COP":      0xfff4,
        "IRQ":      0xfffe,
        "BRK":      0xfffe,
        "NMI":      0xfffa,
        "RESET":    0xfffc
    }

    def interruptAddress(self, i):
        return self.mmu.readWord(self.interrupts[i])


    # Addressing modes
    def z_a(self):
        return self.nextByte()

    def zx_a(self):
        return (self.nextByte() + self.r.x) & 0xff

    def zy_a(self):
        return (self.nextByte() + self.r.y) & 0xff

    def a_a(self):
        return self.nextWord()

    def ax_a(self):
        o = self.nextWord()
        a = o + self.r.x
        if math.floor(o/0xff) != math.floor(a/0xff):
            self.cc += 1

        return a

    def ay_a(self):
        o = self.nextWord()
        a = o + self.r.y
        if math.floor(o/0xff) != math.floor(a/0xff):
            self.cc += 1

        return a

    def i_a(self):
        """Only used by indirect JMP"""
        i = self.nextWord()
        #Doesn't carry, so if the low byte is in the XXFF position
        #Then the high byte will be XX00 rather than XY00
        if i&0xff == 0xff:
            j = i - 0xff
        else:
            j = i + 1

        return (self.mmu.read(j) << 8) + self.mmu.read(i)

    def ix_a(self):
        i = self.nextWord() + self.r.x
        return (self.mmu.read(i + 1) << 8) + self.mmu.read(i)

    def iy_a(self):
        i = self.nextWord()
        o = (self.mmu.read(i + 1) << 8) + self.mmu.read(i)
        a = o + self.r.y

        if math.floor(o/0xff) != math.floor(a/0xff):
            self.cc += 1

        return a


    # Return values based on the addressing mode
    def im(self): return self.nextByte()
    def z(self):  return self.mmu.read(self.z_a())
    def zx(self): return self.mmu.read(self.zx_a())
    def zy(self): return self.mmu.read(self.zy_a())
    def a(self):  return self.mmu.read(self.a_a())
    def ax(self): return self.mmu.read(self.ax_a())
    def ay(self): return self.mmu.read(self.ay_a())
    def i(self):  return self.mmu.read(self.i_a())
    def ix(self): return self.mmu.read(self.ix_a())
    def iy(self): return self.mmu.read(self.iy_a())


    # Operators
     # All the operations.  For each operation have the name of the operation,
    # whether it acts on values, "v" or on addresses, "a" and a list of 4-tuples
    # containing the valid addressing modes for the operation, the 
    # base number of cycles it takes, the opcode, and a target register, if valid.
    _ops = [
        ("ADC", "v", [
            ("im", 2, 0x69, None),
            ("z",  3, 0x65, None),
            ("zx", 4, 0x75, None),
            ("a",  4, 0x6d, None),
            ("ax", 4, 0x7d, None),
            ("ay", 4, 0x79, None),
            ("ix", 6, 0x61, None),
            ("iy", 5, 0x71, None)
        ]),
        ("AND", "v", [
            ("im", 2, 0x29, None),
            ("z",  3, 0x25, None),
            ("zx", 4, 0x35, None),
            ("a",  4, 0x2d, None),
            ("ax", 4, 0x3d, None),
            ("ay", 4, 0x39, None),
            ("ix", 6, 0x21, None),
            ("iy", 5, 0x31, None)
        ]),
        ("ASL", "a", [
            ("im", 2, 0x0a, "a"),
            ("z",  5, 0x06, None),
            ("zx", 6, 0x16, None),
            ("a",  6, 0x0e, None),
            ("ax", 7, 0x1e, None)
        ]),
        ("BIT", "v", [
            ("z",  3, 0x24, None),
            ("a",  4, 0x2c, None)
        ]),
        ("B", "v", [
            ("PL", 2, 0x10, ("N", False)),
            ("MI", 2, 0x30, ("N", True)),
            ("VC", 2, 0x50, ("V", False)),
            ("VC", 2, 0x70, ("V", True)),
            ("CC", 2, 0x90, ("C", False)),
            ("CS", 2, 0xB0, ("C", True)),
            ("NE", 2, 0xD0, ("Z", False)),
            ("EQ", 2, 0xF0, ("Z", True)),
        ]),
        ("BRK", "v", [
            ("im", 7, 0x00, 1)
        ]),
    ]

    def _create_ops(self):

        def f(self, op_f, a_f):
            op_f(a_f())
            self.cc += cc

        def f_target(target):
            return target

        self.ops = [None]*0xff
        for op,atype,addrs in self._ops:
            op_f = getattr(self, op)
            for a,cc,opcode,target in addrs:
                if target:
                    a_f = functools.partial(f_target, target)
                elif atype == 'v':
                    a_f = getattr(self, a)
                else:
                    a_f = getattr(self, "%s_a" % a)

                self.ops[opcode] = functools.partial(f, self, op_f, a_f)


    def ADC(self, v):
        v1 = self.r.a
        v2 = v

        if self.r.getFlag('D'): #decimal mode
            d1 = self.fromBCD(v1)
            d2 = self.fromBCD(v2)

            r = d1 + d2 + self.r.getFlag('C')
            self.r.a = self.toBCD(r%100)

            self.r.setFlag('C', r > 99)
        else:
            self.r.a = v1 + v2 + self.r.getFlag('C')

            self.r.setFlag('C', self.r.a > 0xff)
            self.r.a = self.r.a & 0xff

        self.r.ZN(self.r.a)
        self.r.setFlag('V', (
            (v1 <= 127 and v2 <= 127 and self.r.a > 127) or
            (v1 >= 128 and v2 >= 128 and self.r.a < 128)
        ))

    def AND(self, v):
        self.r.a = (self.r.a & v) & 0xff
        self.r.ZN(self.r.a)

    def ASL(self, a):
        if a == "a":
            v = self.r.a << 1
            self.r.a = v & 0xff
        else:
            v = self.mmu.read(a) << 1
            self.mmu.write(a, v)

        self.r.setFlag('C', v > 0xff)
        self.r.ZN(v&0xff)

    def BIT(self, v):
        self.r.setFlag('Z', self.r.a & v == 0)
        self.r.setFlag('N', v & 0x80)
        self.r.setFlag('V', v & 0x40)

    def B(self, v):
        """
        v is a tuple of (flag, boolean).  For instance, BCC (Branch Carry Clear)
        will call B(('C', False)).
        """
        d = self.im()
        if self.r.getFlag(v[0]) is v[1]:
            o = self.r.pc
            self.r.pc += self.fromTwosCom(d)
            if math.floor(o/0xff) == math.floor(self.r.pc/0xff):
                self.cc += 1
            else:
                self.cc += 2

    def BRK(self, _):
        self.r.setFlag('B')
        self.stackPushWord(self.r.pc+1)
        self.stackPush(self.r.p)
        self.r.clearFlag('I')
        self.r.pc = self.interruptAddress('BRK')