from __future__ import print_function, division

def log(string):
    print(" << %s" % string)

#http://0x10c.com/doc/dcpu-16.txt
spec = '1.1'

w = 16
wmask = 2**w - 1

literals = [l for l in xrange(0, 0x20)]

_opcode_map = {}
_valcode_map = {}


class opcode(object):
    def __init__(self, *opcode):
        self.opcode = opcode

    def __call__(self, f):
        _opcode_f = f
        _opcode_f.opcode = self.opcode
        if len(self.opcode) == 1:
            _opcode_map[self.opcode[0]] = _opcode_f
        else:
            if not self.opcode[0] in _opcode_map.keys():
                _opcode_map[self.opcode[0]] = {}
            _opcode_map[self.opcode[0]][self.opcode[1]] = _opcode_f
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
                _valcode_map[code] = lambda c, code=code: _valcode_f(c, code)
                _valcode_map[code].__name__ = '%s(code=0x%02X)' % (_valcode_f.__name__, code)
        except TypeError:
            _valcode_map[self.valcode] = _valcode_f
        return _valcode_f


class Register(object):
    def __init__(self, regcode=None):
        self.regcode = regcode
    def __get__(self, c, type=None):
        if self.regcode is not None:
            return c.r[self.regcode]
        else:
            return self.value
    def __set__(self, c, value):
        if self.regcode is not None:
            c.r[self.regcode] = value & wmask
        else:
            self.value = value & wmask


@opcode(0x0, 0x01)
def JSR(c, a):
    """pushes the address of the next instruction to the stack, then sets PC to a"""
    c.sp -= 1
    c.m[c.sp] = c.pc
    c.pc = a()

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
    res = a() // b()
    c.o = ((a() << w) // b()) & wmask
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
        c.skip = False
    else:
        c.skip = True

@opcode(0xD)
def IFN(c, a, b):
    """performs next instruction only if a!=b"""
    if a() != b():
        c.skip = False
    else:
        c.skip = True

@opcode(0xE)
def IFG(c, a, b):
    """performs next instruction only if a>b"""
    if a() > b():
        c.skip = False
    else:
        c.skip = True

@opcode(0xF)
def IFB(c, a, b):
    """performs next instruction only if (a&b)!=0"""
    if (a() & b()) != 0:
        c.skip = False
    else:
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
    return v

@valcode(range(0x08, 0x10))
@pointerize
def register_value(c, code):
    """[register]"""
    v = "c.m[c.r[0x%01X]]" % (code-0x07)
    return v

@valcode(range(0x10, 0x18))
@pointerize
def next_word_plus_register_value(c, code):
    """[next word + register]"""
    v = "c.m[0x%04X + c.r[0x%01X]]" % (c.m[c.pc], code-0x0F)
    c.pc += 1
    return v

@valcode(0x18)
@pointerize
def pop(c):
    """POP / [SP++]"""
    v = "c.m[0x%04X]" % c.sp
    c.sp += 1
    return v

@valcode(0x19)
@pointerize
def peek(c):
    """PEEK / [SP]"""
    v = "c.m[0x%04X]" % c.sp
    return v

@valcode(0x1A)
@pointerize
def push(c):
    """PUSH / [--SP]"""
    c.sp -= 1
    v = "c.m[0x%04X]" % c.sp
    return v

@valcode(0x1B)
@pointerize
def stack_pointer(c):
    """stack pointer"""
    v = "c.sp"
    return v

@valcode(0x1C)
@pointerize
def program_counter(c):
    """program counter"""
    v = "c.pc"
    return v

@valcode(0x1D)
@pointerize
def overflow(c):
    """overflow"""
    v = "c.o"
    return v

@valcode(0x1E)
@pointerize
def next_word_value(c):
    """[next_word]"""
    v = "c.m[0x%04X]" % c.m[c.pc]
    c.pc += 1
    return v

@valcode(0x1F)
@pointerize
def next_word(c):
    """next_word (literal)"""
    v = "c.m[0x%04X]" % c.pc
    c.pc += 1
    return v

@valcode(range(0x20, 0x40))
@pointerize
def literal(c, code):
    """literal value 0x00-0x1F (literal)"""
    v = "0x%04X" % (code - 0x20)
    return v


class Memory(object):
    """array of 16-bit words"""
    def __init__(m, debug=False):
        m.clear()

    def clear(m):
        """clear memory"""
        # TODO: (addr, len) memory range to clear
        m.w = [0 for _ in xrange(0, 2**w)]

    def __getitem__(m, addr):
        """get word at addr"""
        return m.w[addr]

    def __setitem__(m, addr, value):
        """assignment truncates values to 16-bit words"""
        # TODO: multi-word assignment starting at addr when value is list
        m.w[addr] = value & wmask


class CPU(object):
    def __init__(c, memory=Memory(), debug=False):
        c.m = memory
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
        c.m.clear()

    a = Register(0x0)
    b = Register(0x1)
    c = Register(0x2)
    x = Register(0x3)
    y = Register(0x4)
    z = Register(0x5)
    i = Register(0x6)
    j = Register(0x7)
    pc = Register()
    sp = Register()
    o = Register()

    def _op(c, word):
        """dispatch word to op and args"""
        opcode = word & 0xF
        a_code = word >>  4 & 0x3F
        b_code = word >> 10 & 0x3F
        try:
            op = _opcode_map[opcode]
            try:
                op = op[a_code]
            except TypeError:
                args = (c._pointer(a_code),
                        c._pointer(b_code))
            else:
                args = (c._pointer(b_code),)
            finally:
                if c.debug:
                    log(' '.join([op.__name__] + [arg.codestr for arg in args]))
        except KeyError:
            raise Exception('Invalid opcode %s at PC=%04X' % (["%02X"%x for x in opcode], c.pc))
        return op, args

    def _pointer(c, code):
        """get pointer to valcode"""
        try:
            return _valcode_map[code](c)
        except KeyError:
            raise Exception("Invalid valcode")

    def __getitem__(c, code):
        """get value of valcode"""
        return c._pointer(code)()

    def __setitem__(c, code, value):
        """set value at valcode"""
        c._pointer(code).set(value)

    def step(c):
        """start handling [PC]"""
        word = c.m[c.pc]
        c.pc += 1
        op, args = c._op(word)
        if c.skip:
            c.skip = False
            if c.debug: log("Skipped")
        else:
            op(c, *args)
        if c.debug: log(c.dump_r())

    def run(c):
        """step until PC is constant"""
        last_pc = 0xFFFF
        while c.pc != last_pc:
            last_pc = c.pc
            c.step()
        log("Infinite loop")

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

    def load_m(c, data=None, io=None):
        """load data in memory"""
        # TODO: load from io object
        for i in xrange(len(data)):
            c.m[i] = data[i]

    def dump_m(c, io):
        """dump memory data"""
        # TODO: save to io object
        pass


spec_demo = [
    0x7c01, 0x0030, 0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d,
    0x7dc1, 0x001a, 0xa861, 0x7c01, 0x2000, 0x2161, 0x2000, 0x8463,
    0x806d, 0x7dc1, 0x000d, 0x9031, 0x7c10, 0x0018, 0x7dc1, 0x001a,
    0x9037, 0x61c1, 0x7dc1, 0x001a, 0x0000, 0x0000, 0x0000, 0x0000,
]
