#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def setFlag(self, flag):
        self.p = self.p | self.flagBit[flag]

    def clearFlag(self, flag):
        self.p = self.p & (255 - self.flagBit[flag])


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

    def ax_x(self):
        o = self.nextWord()
        a = o + self.r.x
        if math.floor(o/0xff) != math.floor(a/0xff):
            cpu.cc += 1

        return a

    def ax_y(self):
        o = self.nextWord()
        a = o + self.r.y
        if math.floor(o/0xff) != math.floor(a/0xff):
            cpu.cc += 1

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
            cpu.cc += 1

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

    def ADC(self, v): pass

    def ADC_im(self, mem): pass
    def ADC_z(self): pass
    def ADC_zx(self): pass
    def ADC_a(self): pass
    def ADC_ax(self): pass
    def ADC_ay(self): pass
    def ADC_ix(self): pass
    def ADC_iy(self): pass

    opmap = [
        # /*0*/
        # self.BRK_im,
        # self.ORA_ix,
        # self.XX,
        # self.XX,
        # self.NOP_z,
        # self.ORA_z,
        # self.ASL_z,
        # self.XX,
        # self.PHP_im,
        # self.ORA_im,
        # self.ASL_im,
        # self.XX,
        # self.XX,
        # self.ORA_a,
        # self.ASL_a,
        # self.XX,

        # /*1*/
        # self.BPL_rel,
        # self.ORA_iy,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.ORA_zx,
        # self.ASL_zx,
        # self.XX,
        # self.CLC_im,
        # self.ORA_ay,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.ORA_ax,
        # self.ASL_ax,
        # self.XX,

        # /*2*/
        # self.JSR_a,
        # self.AND_ix,
        # self.XX,
        # self.XX,
        # self.BIT_z,
        # self.AND_z,
        # self.ROL_z,
        # self.XX,
        # self.PLP_im,
        # self.AND_im,
        # self.ROL_im,
        # self.XX,
        # self.BIT_a,
        # self.AND_a,
        # self.ROL_a,
        # self.XX,

        # /*3*/
        # self.BMI_rel,
        # self.AND_iy,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.AND_zx,
        # self.ROL_zx,
        # self.XX,
        # self.SEC_im,
        # self.AND_ay,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.AND_ax,
        # self.ROL_ax,
        # self.XX,

        # /*4*/
        # self.RTI_im,
        # self.EOR_ix,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.EOR_z,
        # self.LSR_z,
        # self.XX,
        # self.PHA_im,
        # self.EOR_im,
        # self.LSR_im,
        # self.XX,
        # self.JMP_a,
        # self.EOR_a,
        # self.LSR_a,
        # self.XX,

        # /*5*/
        # self.BVC_rel,
        # self.EOR_iy,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.EOR_zx,
        # self.LSR_zx,
        # self.XX,
        # self.CLI_im,
        # self.EOR_ay,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.EOR_ax,
        # self.LSR_ax,
        # self.XX,

        # /*6*/
        # self.RTS_im,
        # self.ADC_iy,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.ADC_z,
        # self.ROR_z,
        # self.XX,
        # self.PLA_im,
        # self.ADC_im,
        # self.ROR_im,
        # self.XX,
        # self.JMP_i,
        # self.ADC_a,
        # self.ROR_a,
        # self.XX,

        # /*7*/
        # self.BVS_rel,
        # self.ADC_iy,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.ADC_zx,
        # self.ROR_zx,
        # self.XX,
        # self.SEI_im,
        # self.ADC_ay,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.ADC_ax,
        # self.ROR_ax,
        # self.XX,

        # /*8*/
        # self.XX,
        # self.STA_ix,
        # self.XX,
        # self.XX,
        # self.STY_z,
        # self.STA_z,
        # self.STX_z,
        # self.XX,
        # self.DEY_im,
        # self.XX,
        # self.TXA_im,
        # self.XX,
        # self.STY_a,
        # self.STA_a,
        # self.STX_a,
        # self.XX,

        # /*9*/
        # self.BCC_rel,
        # self.STA_iy,
        # self.XX,
        # self.XX,
        # self.STY_zx,
        # self.STA_zx,
        # self.STX_zy,
        # self.XX,
        # self.TYA_im,
        # self.STA_ay,
        # self.TXS_im,
        # self.XX,
        # self.XX,
        # self.STA_ax,
        # self.XX,
        # self.XX,

        # /*A*/
        # self.LDY_im,
        # self.LDA_ix,
        # self.LDX_im,
        # self.LAX_ix,
        # self.LDY_z,
        # self.LDA_z,
        # self.LDX_z,
        # self.LAX_z,
        # self.TAY_im,
        # self.LDA_im,
        # self.TAX_im,
        # self.XX,
        # self.LDY_a,
        # self.LDA_a,
        # self.LDX_a,
        # self.LAX_a,

        # /*B*/
        # self.BCS_rel,
        # self.LDA_iy,
        # self.XX,
        # self.LAX_iy,
        # self.LDY_zx,
        # self.LDA_zx,
        # self.LDX_zy,
        # self.LAX_zy,
        # self.CLV_im,
        # self.LDA_ay,
        # self.TSX_im,
        # self.XX,
        # self.LDY_ax,
        # self.LDA_ax,
        # self.LDX_ay,
        # self.XX,

        # /*C*/
        # self.CPY_im,
        # self.CMP_ix,
        # self.XX,
        # self.XX,
        # self.CPY_z,
        # self.CMP_z,
        # self.DEC_z,
        # self.XX,
        # self.INY_im,
        # self.CMP_im,
        # self.DEX_im,
        # self.XX,
        # self.CPY_a,
        # self.CMP_a,
        # self.DEC_a,
        # self.XX,

        # /*D*/
        # self.BNE_rel,
        # self.CMP_iy,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.CMP_zx,
        # self.DEC_zx,
        # self.XX,
        # self.CLD_im,
        # self.CMP_ay,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.CMP_ax,
        # self.DEC_ax,
        # self.XX,

        # /*E*/
        # self.CPX_im,
        # self.SBC_ix,
        # self.XX,
        # self.XX,
        # self.CPX_z,
        # self.SBC_z,
        # self.INC_z,
        # self.XX,
        # self.INX_im,
        # self.SBC_im,
        # self.NOP_im,
        # self.XX,
        # self.CPX_a,
        # self.SBC_a,
        # self.INC_a,
        # self.XX,

        # /*F*/
        # self.BEQ_rel,
        # self.SBC_iy,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.SBC_zx,
        # self.INC_zx,
        # self.XX,
        # self.SED_im,
        # self.SBC_ay,
        # self.XX,
        # self.XX,
        # self.XX,
        # self.SBC_ax,
        # self.INC_ax,
        # self.XX
    ]
