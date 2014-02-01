import array

class MemoryRangeError(ValueError):
    pass

class ReadOnlyError(TypeError):
    pass

class MMU:
    

    def __init__(self, blocks):
        """
        Initialize the MMU with the blocks specified in blocks.  blocks
        is a list of 3-tuples, (start, length, readonly, value).

        """

        # Different blocks of memory stored seperately so that they can
        # have different properties.  Stored as dict of "start", "length",
        # "readonly" and "memory"
        self.blocks = []
        
        for b in blocks:
            self.addBlock(*b)

    def addBlock(self, start, length, readonly=False, value=None):
        """
        Add a block of memory to the list of blocks with the given start address
        length. whether it is readonly or not and the starting value as either
        a file pointer, binary value or list of unsigned integers.  If the 
        block overlaps with an existing block an exception will be thrown.

        """
        
        #check if the block overlaps with another
        for b in self.blocks:
            if ((start+length > b['start'] and start+length < b['start']+b['length']) or 
                (b['start']+b['length'] > start and b['start']+b['length'] < start+length)):
                raise MemoryRangeError()


        self.blocks.append({
            'start': start, 'length': length, 'readonly': readonly,
            'memory': array.array('B', [0]*length)
        })

        #TODO: implement initialization value

    def getBlock(self, addr):
        for b in self.blocks:
            if addr >= b['start'] and addr < b['start']+b['length']:
                return b

        raise IndexError

    def getIndex(self, block, addr):
        return addr-block['start']

    def write(self, addr, value):
        b = self.getBlock(addr)
        if b['readonly']:
            raise ReadOnlyError()

        i = self.getIndex(b, addr)

        b['memory'][i] = value

    def read(self, addr):
        b = self.getBlock(addr)
        i = self.getIndex(b, addr)
        return b['memory'][i]
