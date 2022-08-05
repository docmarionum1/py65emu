# Python 6502 Emulator


[![Tests](https://github.com/docmarionum1/py65emu/actions/workflows/run-tests.yml/badge.svg?branch=master)](https://github.com/docmarionum1/py65emu/actions/workflows/run-tests.yml)


A MOS 6502 Emulator intended to be used from within other programs.  All opcodes, included the undocumented illegal opcodes are implemented.

Example Usage

        from py65emu.cpu import CPU
        from py65emu.mmu import MMU

        f = open("program.rom", "rb")  # Open your rom

        # define your blocks of memory.  Each tuple is
        # (start_address, length, readOnly=True, value=None, valueOffset=0)
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
        print(c.r.a) 	# A register
        print(c.r.x) 	# X register
        print(c.r.y) 	# Y register
        print(c.r.s) 	# Stack Pointer
        print(c.r.pc) 	# Program Counter

        print(c.cc)     # Print the number of cycles that passed during the last step.
                        # This number resets for each call to `.step()`

        print(c.r.getFlag('C')) # Get the value of a flag from the flag register.

        print(mmu.read(0xff)) # Read a value from memory

        

The full set of parameters for CPU is

        mmu: An instance of MMU
        pc: The starting address of the pc (program counter)
        stack_page: The index of the page which contains the stack.  The default for
            a 6502 is page 1 (the stack from 0x0100-0x1ff) but in some varients the
            stack page may be elsewhere.
        magic: A value needed for the illegal opcodes, XAA.  This value differs
            between different versions, even of the same CPU.  The default is 0xee.

And for MMU, the tuple values are

        start : int
            The starting address of the block of memory
        length : int
            The length of the block in bytes
        readOnly: bool
            Whether the block should be read only (such as ROM) (default False)
        value : file pointer, binary or lint of unsigned integers
            The intial value for the block of memory. Used for loading program
            data. (Default None)
        valueOffset : integer
            Used when copying the above `value` into the block to offset the
            location it is copied into. For example, to copy byte 0 in `value`
            into location 1000 in the block, set valueOffest=1000. (Default 0)
