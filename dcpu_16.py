# System width
w = 16
wmask = 2**16-1

# Literal values
literal = xrange(0x00, 0x20)

opcodes = [
    'nbi',
    'SET',
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'MOD',
    'SHL',
    'SHR',
    'AND',
    'BOR',
    'XOR',
    'IFE',
    'IFN',
    'IFG',
    'IFB',
]

class CPU(object):

    class Ops(object):
        def SET(c, a, b):
            return None
        def ADD(c, a, b):
            return None
        def SUB(c, a, b):
            return None
        def MUL(c, a, b):
            return None
        def DIV(c, a, b):
            return None
        def MOD(c, a, b):
            return None
        def SHL(c, a, b):
            return (a << b) & wmask
        def SHR(c, a, b):
            return (a >> b)
        def AND(c, a, b):
            return a & b
        def BOR(c, a, b):
            return a | b
        def XOR(c, a, b):
            return a ^ b
        def IFE(c, a, b):
            return a == b
        def IFN(c, a, b):
            return a != b
        def IFG(c, a, b):
            return a > b
        def IFB(c, a, b):
            return (a & b) != 0

    def __init__(c):
        c.reset()
        c.clear()

    def reset(c):
        """Reset CPU"""
        c.r = [0 for _ in xrange(0, w)]
        c.pc = 0
        c.sp = 0
        c.o  = False
        c.skip = False

    def clear(c):
        """Clear memory"""
        c.m = [0 for _ in xrange(0, 2**w)]

    def __getitem__(c, addr):
        """Read value at memory address"""
        return c.m[addr]

    def __setitem__(c, addr, value):
        """Write value at memory address"""
        c.m[addr] = value

    def next_word(c):
        val = c[c.pc]
        c.pc += 1
        return val

    def dispatch_op(c):

        def get_opcode(word):
            return word & 0xF
        def get_a(word):
            return (word >>  4) & 0x3F
        def get_b(word):
            return (word >> 10) & 0x3F

        def get_op(word):
            getattr(CPU.Ops, opcodes[get_opcode(word)])

        def is_nbi(opcode):
            return opcode == 0x0
        def is_set(opcode):
            return 0x0 < opcode <= 0xb
        def is_skip(opcode):
            return 0xb < opcode <= 0xf
        def set_a(value):
            pass

        word = c.next_word()
        if c.skip:
            c.skip = False
            return

        opcode = get_opcode(word)
        if is_nbi(opcode):
            pass
        elif is_set(opcode):
            set_a(get_op(opcode)())
        elif is_skip(opcode):
            if not get_op(opcode)():
                c.skip = True
        else:
            raise OpcodeError(c.pc, opcode)



class OpcodeError(Exception):
    def __init__(self, addr, data):
        self.addr = addr
        self.data = data

    def __str__(self):
        return "Invalid opcode at %s: '%s'" % (self.addr, self.data)

