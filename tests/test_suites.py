#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_suites
----------------------------------

Tests for `py65emu` module.
"""

import os, unittest, traceback

from py65emu.cpu import CPU
from py65emu.mmu import MMU


class TestPy65emu(unittest.TestCase):

    def setUp(self):
        pass

    def test_nestest(self):
        f = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 
            "files", "nestest_mod.nes"
        )

        mmu = MMU([
            (0x0000, 0x800), #RAM
            (0x2000, 0x8), #PPU
            (0x4000, 0x18),
            (0x8000, 0xc000, True, open(f), 0x3ff0) #ROM
            #(0xbff0, 0x6010, True, open(f)) #ROM
        ])

        c = CPU(mmu, 0xc000)

        c.r.s = 0xfd

        while c.r.pc != 0xc66e:
            try:
                c.step()
            except Exception, e:
                print c.r
                print traceback.format_exc()
                raise e
            self.assertEqual(c.mmu.read(0x2), 0x00, hex(c.mmu.read(0x2)))
            self.assertEqual(c.mmu.read(0x3), 0x00, hex(c.mmu.read(0x3)))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()