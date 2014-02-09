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


class CPU:
    
    def __init__(self, mmu=None, pc=None):
        self.mmu = mmu
        self.r = Registers()
        self.cc = 0
        self.reset()

        if pc:
            self.r.pc = pc
        else:
            # if pc is none get the address from $FFFD,$FFFC
            pass

        self._create_ops()

    # All the operations.  For each operation have a list of 2-tuples
    # containing the valid addressing modes for the operation, the 
    # base number of cycles it takes, and the opcode.
    _ops = [
        ("ADC", [
            ("im", 2, 0x69),
            ("z",  3, 0x65),
            ("zx", 4, 0x75),
            ("a",  4, 0x6d),
            ("ax", 4, 0x7d),
            ("ay", 4, 0x79),
            ("ix", 6, 0x61),
            ("iy", 5, 0x71)
        ])
    ]

    def _create_ops(self):

        def f(self, op_f, a_f):
            op_f(a_f())
            self.cc += cc

        self.ops = [None]*0xff
        for op,addrs in self._ops:
            op_f = getattr(self, op)
            for a,cc,opcode in addrs:
                a_f = getattr(self, a)
                self.ops[opcode] = functools.partial(f, self, op_f, a_f)


        
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

    def im(self):
        return self.nextByte()

    def z(self):
        return self.mmu.read(self.z_a())

    def zx(self):
        return self.mmu.read(self.zx_a())

    def zy(self):
        return self.mmu.read(self.zy_a())

    def a(self):
        return self.mmu.read(self.a_a())

    def ax(self):
        return self.mmu.read(self.ax_a())

    def ay(self):
        return self.mmu.read(self.ay_a())

    def i(self):
        return self.mmu.read(self.i_a())

    def ix(self):
        return self.mmu.read(self.ix_a())

    def iy(self):
        return self.mmu.read(self.iy_a())

    def ADC(self, v):
        if self.r.getFlag('D'): #decimal mode
            pass
        else:
            v1 = self.r.a
            v2 = v

            self.r.a = v1 + v2 + self.r.getFlag('C')

            self.r.setFlag('C', self.r.a > 0xff)
            self.r.a = self.r.a & 0xff

        self.r.setFlag('Z', self.r.a == 0)
        self.r.setFlag('N', self.r.a & 0x80)
        self.r.setFlag('V', (
                (v1 <= 127 and v2 <= 127 and self.r.a > 127) or
                (v1 >= 128 and v2 >= 128 and self.r.a < 128)
            )
        )
    