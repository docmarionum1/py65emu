===============================
Python 6502 Emulator
===============================

.. image:: https://travis-ci.org/docmarionum1/py65emu.png?branch=master
        :target: https://travis-ci.org/docmarionum1/py65emu


A MOS 6502 Emulator intended to be used from within other programs.  All opcodes, included the undocumented illegal opcodes are implemented.

Example Usage:::

        from py65emu.cpu import CPU
        from py65emu.mmu import MMU

        f = open("program.rom", "rb")  # Open your rom

        # define your blocks of memory.  Each tuple is
        # (start_address, length, readonly=True, initial_value=None, value_offset=0)
        m = MMU([
                (0x00, 0x200), # Create RAM with 512 bytes
                (0x1000, 0x4000, True, f) # Create ROM starting at 0x1000 with your program.
        ])

        # Create the CPU with the MMU and the starting program counter address
        # You can also optionally pass in a value for stack_page, which defaults
        # to 1, meaning the stack will be from 0x100-0x1ff.  As far as I know this
        # is true for all 6502s, but for instance in the 6507 used by the Atari
        # 2600 it is in the zero page, stack_page=0.
        c = CPU(mmu, 0x1000)

        # Do this to execute one instruction
        c.step()

        # You can check the registers and memory values to determine what has changed
        print c.r.a 	# A register
        print c.r.x 	# X register
        print c.r.y 	# Y register
        print c.r.s 	# Stack Pointer
        print c.r.pc 	# Program Counter

        print c.r.getFlag('C') # Get the value of a flag from the flag register.

        print mmu.read(0xff) # Read a value from memory
