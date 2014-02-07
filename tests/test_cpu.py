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

    def _cpu(self, ram=(0,0xff, False), rom=(0x1000, 0xff), romInit=None, pc=0x1000):
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
        c = self._cpu(romInit=[1, 2, 3, 4, 5])
        self.assertEqual(c.nextWord(), 0x0201)
        c.nextByte()
        self.assertEqual(c.nextWord(), 0x0504)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()