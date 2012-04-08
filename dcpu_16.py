from __future__ import print_function, division

def log(string):
    print(" << %s" % string)

#http://0x10c.com/doc/dcpu-16.txt
spec = '1.1'

w = 16
wmask = 2**w-1

literals = [l for l in xrange(0, 0x20)]

opcode_map = {}
valcode_map = {}


class opcode(object):
    def __init__(self, *opcode):
        self.opcode = opcode

    def __call__(self, f):
        _opcode_f = f
        _opcode_f.opcode = self.opcode
        opcode_map[self.opcode] = _opcode_f
        return _opcode_f


class valcode(object):
    def __init__(self, valcode):
        self.valcode = valcode

    def __call__(self, f):
        _valcode_f = f
        _valcode_f.valcode = self.valcode
        try:
            for code in self.valcode:
                # currify with (bound) code
                valcode_map[code] = lambda c, code=code: _valcode_f(c, code)
                valcode_map[code].__name__ = '%s(code=0x%02X)' % (_valcode_f.__name__, code)
        except TypeError:
            valcode_map[self.valcode] = _valcode_f
        return _valcode_f


@opcode(0x0, 0x01)
def JSR(c, a):
    """pushes the address of the next instruction to the stack, then sets PC to a"""
    #pushnext
    c.pc = c[a]

@opcode(0x1)
def SET(c, a, b):
    """sets a to b"""
    a.set(b())

@opcode(0x2)
def ADD(c, a, b):
    """sets a to a+b, sets O to 0x0001 if there's an overflow"""
    res = (a() + b())
    if res > wmask:
        c.o = 0x0001
    res = res & wmask
    a.set(res)

@opcode(0x3)
def SUB(c, a, b):
    """sets a to a-b, sets O to 0xFFFF if there's an underflow"""
    res = (a() - b())
    if res & (wmask+1):
        c.o = 0xFFFF
    res = res & wmask
    a.set(res)

@opcode(0x4)
def MUL(c, a, b):
    """sets a to a*b, sets O to ((a*b)>>16)&0xFFFF"""
    res = (a() * b())
    c.o = ((a() * b()) >> w) & wmask
    res = res & wmask
    a.set(res)

@opcode(0x5)
def DIV(c, a, b):
    """sets a to a/b, sets O to ((a<<16)/b)&0xFFFF"""
    res = a() / b()
    c.o = ((a() << w) / b()) & wmask
    a.set(res)

@opcode(0x6)
def MOD(c, a, b):
    """sets a to a%b. if b==0, sets a to 0 instead"""
    if b()==0:
        res = 0
    else:
        res = a() % b()
    a.set(res)

@opcode(0x7)
def SHL(c, a, b):
    """sets a to a<<b. sets O to ((a<<b)>>16)&0xFFFF"""
    res = (a() << b())
    c.o = ((a() << b()) >> w) & wmask
    res = res & wmask
    a.set(res)

@opcode(0x8)
def SHR(c, a, b):
    """sets a to a>>b. sets O to ((a>>16)>>b)&0xFFFF"""
    res = (a() >> b())
    c.o = ((a() >> w) >> b()) & wmask
    res = res & wmask
    a.set(res)

@opcode(0x9)
def AND(c, a, b):
    """sets a to a&b"""
    res = a() & b()
    a.set(res)

@opcode(0xA)
def BOR(c, a, b):
    """sets a to a|b"""
    res = a() | b()
    a.set(res)

@opcode(0xB)
def XOR(c, a, b):
    """sets a to a^b"""
    res = a() ^ b()
    a.set(res)

@opcode(0xC)
def IFE(c, a, b):
    """performs next instruction only if a==b"""
    if a() == b():
        c.skip = True

@opcode(0xD)
def IFN(c, a, b):
    """performs next instruction only if a!=b"""
    if a() != b():
        c.skip = True

@opcode(0xE)
def IFG(c, a, b):
    """performs next instruction only if a>b"""
    if a() > b():
        c.skip = True

@opcode(0xF)
def IFB(c, a, b):
    """performs next instruction only if (a&b)!=0"""
    if (a() & b()) != 0:
        c.skip = True


def make_pointer(c, codestr):
    """creates a pointer func that evaluates codestr"""
    def getter(c=c):
        return eval("%s" % codestr)
    def setter(data, c=c):
        exec("%s = %r" % (codestr, data)) in {}, {'c': c, 'data': data}
    pointer     = getter
    pointer.codestr = codestr
    pointer.set = setter
    return pointer

def pointerize(f):
    """wraps a function that generates a codestr to create a pointer"""
    if f.func_code.co_argcount == 1:
        ptrz = lambda c: make_pointer(c, f(c))
    elif f.func_code.co_argcount == 2:
        ptrz = lambda c, code: make_pointer(c, f(c, code))
    else:
        raise Exception('%s has too many arguments' % f.__name__)
    ptrz.__name__ = 'ptr_to_%s' % f.__name__
    ptrz.__doc__ = f.__doc__
    return ptrz

@valcode(range(0x00, 0x08))
@pointerize
def register(c, code):
    """register"""
    v = "c.r[0x%01X]" % code
    log(v)
    return v

@valcode(range(0x08, 0x10))
@pointerize
def register_value(c, code):
    """[register]"""
    v = "c.m[c.r[0x%01X]]" % (code-0x07)
    log(v)
    return v

@valcode(range(0x10, 0x18))
@pointerize
def next_word_plus_register_value(c, code):
    """[next word + register]"""
    v = "c.m[0x%04X + 0x%01X]" % (c.m[c.pc], code-0x0F)
    log(v)
    c.pc += 1
    return v

@valcode(0x18)
@pointerize
def pop(c):
    """POP / [SP++]"""
    v = "c.m[0x%04X]" % c.sp
    log(v)
    c.sp += 1
    return v

@valcode(0x19)
@pointerize
def peek(c):
    """PEEK / [SP]"""
    v = "c.m[0x%04X]" % c.sp
    log(v)
    return v

@valcode(0x1A)
@pointerize
def push(c):
    """PUSH / [--SP]"""
    c.sp -= 1
    v = "c.m[0x%04X]" % c.sp
    log(v)
    return v

@valcode(0x1B)
@pointerize
def stack_pointer(c):
    """stack pointer"""
    v = "c.sp"
    log(v)
    return v

@valcode(0x1C)
@pointerize
def program_counter(c):
    """program counter"""
    v = "c.pc"
    log(v)
    return v

@valcode(0x1D)
@pointerize
def overflow(c):
    """overflow"""
    v = "c.o"
    log(v)
    return v

@valcode(0x1E)
@pointerize
def next_word_value(c):
    """[next_word]"""
    v = "c.m[0x%04X]" % c.m[c.pc]
    c.pc += 1
    log(v)
    return v

@valcode(0x1F)
@pointerize
def next_word(c):
    """next_word (literal)"""
    v = "c.m[0x%04X]" % c.pc
    c.pc += 1
    log(v)
    return v

@valcode(range(0x20, 0x40))
@pointerize
def literal(c, code):
    """literal value 0x00-0x1F (literal)"""
    v = "0x%04X" % (code - 0x20)
    log(v)
    return v



class CPU(object):
    def __init__(c, debug=False):
        c.clear()
        c.reset()
        c.debug = debug

    def reset(c):
        """reset CPU"""
        c.r = [0 for _ in xrange(0, 8)]
        c.pc = 0x0000
        c.sp = 0x0000
        c.o  = 0x0000
        c.skip = False

    def clear(c):
        """clear memory"""
        c.m = [0 for _ in xrange(0, 2**w)]

    @property
    def a(c):
        return c.r[0]
    @a.setter
    def a(c, val):
        c.r[0] = val

    @property
    def b(c):
        return c.r[1]
    @b.setter
    def b(c, val):
        c.r[1] = val

    @property
    def c(c):
        return c.r[2]
    @c.setter
    def c(c, val):
        c.r[2] = val

    @property
    def x(c):
        return c.r[3]
    @x.setter
    def x(c, val):
        c.r[3] = val

    @property
    def y(c):
        return c.r[4]
    @y.setter
    def y(c, val):
        c.r[4] = val

    @property
    def z(c):
        return c.r[5]
    @z.setter
    def z(c, val):
        c.r[5] = val

    @property
    def i(c):
        return c.r[6]
    @i.setter
    def i(c, val):
        c.r[6] = val

    @property
    def j(c):
        return c.r[7]
    @j.setter
    def j(c, val):
        c.r[7] = val



    def _pointer(c, code):
        """get pointer to value code"""
        try:
            return valcode_map[code](c)
        except KeyError:
            raise Exception("Invalid value code")

    def __getitem__(c, code):
        """get pointer to value"""
        return c._pointer(code)()

    def __setitem__(c, code, value):
        """set value at pointer"""
        c._pointer(code).set(value)

    def step(c):
        """start handling [PC]"""
        word = c.m[c.pc]
        c.pc += 1
        opcode = word & 0xF
        try:
            op = opcode_map[(opcode,)]
            log(op.__name__)
        except KeyError:
            raise Exception('Invalid opcode %01X at PC=%04X' % (opcode, c.pc))
        a = c._pointer(word >>  4 & 0x3F)
        b = c._pointer(word >> 10 & 0x3F)
        if c.skip:
            c.skip = False
        else:
            op(c, a, b)
        if c.debug:
            log(c.dump_r())

    def dump_r(c):
        """human-readable register status"""
        return " ".join( "%s=%04X" %
                (["A", "B", "C",
                  "X", "Y", "Z",
                  "I", "J",
                  "PC", "SP", "O",
                  ][i],
                  (c.r + [c.pc, c.sp, c.o])[i])
                for i in range(11))

    def load_m(c, io=None):
        """load data in memory"""
        # TODO: load from io object
        data = [
            0x7c01, 0x0030, 0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d,
            0x7dc1, 0x001a, 0xa861, 0x7c01, 0x2000, 0x2161, 0x2000, 0x8463,
            0x806d, 0x7dc1, 0x000d, 0x9031, 0x7c10, 0x0018, 0x7dc1, 0x001a,
            0x9037, 0x61c1, 0x7dc1, 0x001a, 0x0000, 0x0000, 0x0000, 0x0000,
        ]
        for i in xrange(len(data)):
            c.m[i] = data[i]

    def dump_m(c, io):
        """dump memory data"""
        # TODO: save to io object
        pass


