#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_mmu
----------------------------------
"""

import unittest

from py65emu.cpu import Registers


class TestRegisters(unittest.TestCase):

    def setUp(self):
        pass

    def test_flags(self):
        r = Registers()
        r.setFlag('N')
        self.assertEqual(r.p, 128)
        r.setFlag('Z')
        self.assertEqual(r.p, 130)
        r.clearFlag('N')
        self.assertEqual(r.p, 2)
        self.assertTrue(r.getFlag('Z'))


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
