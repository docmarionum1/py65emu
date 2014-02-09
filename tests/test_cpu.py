#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cpu
----------------------------------

Tests for `py65emu` module.
"""

import unittest

from py65emu.cpu import CPU
from py65emu.mmu import MMU

class TestCPU(unittest.TestCase):

    def _cpu(self, ram=(0,0x100, False), rom=(0x1000, 0x100), romInit=None, pc=0x1000):
        return CPU(
            MMU([
                ram,
                rom + (True,romInit)
            ]),
            pc
        )

    def setUp(self):
        pass

    def test_nextByte(self):
        c = self._cpu(romInit=[1, 2, 3])
        self.assertEqual(c.nextByte(), 1)
        self.assertEqual(c.nextByte(), 2)
        self.assertEqual(c.nextByte(), 3)
        self.assertEqual(c.nextByte(), 0)

    def test_nextWord(self):
        c = self._cpu(romInit=[1, 2, 3, 4, 5, 9, 10])
        self.assertEqual(c.nextWord(), 0x0201)
        c.nextByte()
        self.assertEqual(c.nextWord(), 0x0504)
        self.assertEqual(c.nextWord(), 0x0a09)

    def test_zeropage_addressing(self):
        c = self._cpu(romInit=[1, 2, 3, 4, 5])
        self.assertEqual(c.z_a(), 1)
        c.r.x = 0
        self.assertEqual(c.zx_a(), 2)
        c.r.x = 1
        self.assertEqual(c.zx_a(), 4)
        c.r.y = 0
        self.assertEqual(c.zy_a(), 4)
        c.r.y = 1
        self.assertEqual(c.zy_a(), 6)

    def test_absolute_addressing(self):
        c = self._cpu(romInit=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(c.a_a(), 0x0201)

        c.r.x = 0
        c.cc = 0
        self.assertEqual(c.ax_a(), 0x0403)
        self.assertEqual(c.cc, 0)
        c.r.x = 0xff
        c.cc = 0
        self.assertEqual(c.ax_a(), 0x0605+0xff)
        self.assertEqual(c.cc, 1)

        c.r.y = 0
        c.cc = 0
        self.assertEqual(c.ay_a(), 0x0807)
        self.assertEqual(c.cc, 0)
        c.r.y = 0xff
        c.cc = 0
        self.assertEqual(c.ay_a(), 0x0a09+0xff)
        self.assertEqual(c.cc, 1)

    def test_indirect_addressing(self):
        c = self._cpu(romInit=[
            0x08, 0x10,
            0xff, 0x10,
            0x00, 0x10,
            0x0c, 0x10,

            0xf0, 0x00,
            0xe0, 0x00,
            0xd0, 0x00,
        ])

        self.assertEqual(c.i_a(), 0x00f0)
        self.assertEqual(c.i_a(), 0x0800)
        c.r.x = 0x0a
        self.assertEqual(c.ix_a(), 0x00e0)
        c.r.y = 0x0f
        self.assertEqual(c.iy_a(), 0x00df)

    def test_adc(self):
        c = self._cpu(romInit=[1, 2, 250, 3, 100, 100])

        #immediate
        c.ops[0x69]()
        self.assertEqual(c.r.a, 1)
        c.ops[0x69]()
        self.assertEqual(c.r.a, 3)
        c.ops[0x69]()
        self.assertEqual(c.r.a, 253)
        self.assertTrue(c.r.getFlag('N'))
        c.r.clearFlags()
        c.ops[0x69]()
        self.assertTrue(c.r.getFlag('C'))
        self.assertTrue(c.r.getFlag('Z'))
        c.r.clearFlags()
        c.ops[0x69]()
        c.ops[0x69]()
        self.assertTrue(c.r.getFlag('V'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()