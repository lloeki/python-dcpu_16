"""DCPU-16 implementation. (c) 2012, Loic Nageleisen

Spec: http://dcpu.com/highnerd/dcpu16_1_5.txt

See LICENSE for licensing information.
"""

# TODO: cycle count management
#       branching opcodes take one cycle longer to perform if the test fails
#       when they skip an if instruction, they will skip an additional instruction
# TODO: signed functions
#       signed numbers are represented using two's complement
# TODO: interrupts
# TODO: hardware

from __future__ import print_function, division


# DCPU-16 spec version
spec = '1.5'


# log tool
def log(string):
    print(" << %s" % string)

# width constants
w = 16
wmask = 2**w - 1


_opcode_map = {}
class opcode(object):
    """Opcode decorator"""
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


_valcode_map = {}
_valcode_a_map = {}
class valcode(object):
    """Valcode decorator"""
    def __init__(self, valcode, a=False):
        self.valcode = valcode
        self.a = a

    def __call__(self, f):
        _valcode_f = f
        _valcode_f.valcode = self.valcode
        if self.a:
            valcode_map = _valcode_a_map
        else:
            valcode_map = _valcode_map
        try:
            for code in self.valcode:
                # currify with (bound) code
                valcode_map[code] = lambda c, code=code: _valcode_f(c, code)
                valcode_map[code].__name__ = '%s(code=0x%02X)' % (_valcode_f.__name__, code)
        except TypeError:
            valcode_map[self.valcode] = _valcode_f
        return _valcode_f


class Register(object):
    """Register descriptor"""
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


@opcode(0x00, 0x01)
def JSR(c, a):
    """pushes the address of the next instruction to the stack, then sets PC to a"""
    c.sp -= 1
    c.m[c.sp] = c.pc
    c.pc = a()

@opcode(0x00, 0x07)
def HCF(c, a):
    """use sparingly"""
    pass

@opcode(0x00, 0x08)
def INT(c, a):
    """triggers a software interrupt with message a"""
    pass

@opcode(0x00, 0x09)
def IAG(c, a):
    """sets a to IA"""
    pass

@opcode(0x00, 0x0A)
def IAS(c, a):
    """sets IA to a"""
    pass

@opcode(0x00, 0x0B)
def IAP(c, a):
    """if IA is 0, does nothing, otherwise pushes IA to the stack, then sets IA to a"""
    pass

@opcode(0x00, 0x0C)
def IAQ(c, a):
    """if a is nonzero, interrupts will be added to the queue instead of triggered. if a is zero, interrupts will be triggered as nomral again"""
    pass

@opcode(0x00, 0x10)
def HWN(c, a):
    """sets a to number of connected hardware devices"""
    pass

@opcode(0x00, 0x11)
def HWQ(c, a):
    """sets A, B, C,X, Y registers to information about hardware a
    
    A+(B<<16) is a 32 bit word identifying the hardware id
    C is the hardware version
    X+(Y<<16) is a 32 bit word identifying the manufacturer
    """
    pass

@opcode(0x00, 0x12)
def HWI(c, a):
    """sends an interrupt to hardware a"""
    pass

@opcode(0x01)
def SET(c, b, a):
    """sets b to a"""
    b.set(a())

@opcode(0x02)
def ADD(c, b, a):
    """sets b to b+a, sets EX to 0x0001 if there's an overflow, 0x0 otherwise"""
    res = (b() + a())
    if res > wmask:
        c.ex = 0x0001
    res = res & wmask
    b.set(res)

@opcode(0x03)
def SUB(c, b, a):
    """sets b to b-a, sets EX to 0xFFFF if there's an underflow, 0x0 otherwise"""
    res = (b() - a())
    if res & (wmask+1):
        c.ex = 0xFFFF
    res = res & wmask
    b.set(res)

@opcode(0x04)
def MUL(c, b, a):
    """sets b to b*a, sets EX to ((b*a)>>16)&0xFFFF (treats b, a as unsigned)"""
    res = (b() * a())
    c.ex = ((b() * a()) >> w) & wmask
    res = res & wmask
    b.set(res)

@opcode(0x05)
def MLI(c, b, a):
    """like MUL, but treats b, a as signed"""
    pass

@opcode(0x06)
def DIV(c, b, a):
    """sets b to b/a, sets EX to ((b<<16)/a)&0xFFFF. if a==0, sets b and EX to 0 instead. (treats b, a as unsigned)"""
    res = b() // a()
    c.ex = ((b() << w) // a()) & wmask
    b.set(res)

@opcode(0x07)
def DVI(c, b, a):
    """like DIV, but treats b, a as signed. Rounds towards 0"""
    pass

@opcode(0x08)
def MOD(c, b, a):
    """sets b to b%a. if a==0 sets b to 0 instead"""
    if a()==0:
        res = 0
    else:
        res = b() % a()
    b.set(res)

@opcode(0x09)
def MDI(c, b, a):
    """like MOD, but treat b, a as signed. Rounds towards 0"""
    pass

@opcode(0x0A)
def AND(c, b, a):
    """sets b to b&a"""
    res = b() & a()
    b.set(res)

@opcode(0x0B)
def BOR(c, b, a):
    """sets b to b|a"""
    res = b() | a()
    b.set(res)

@opcode(0x0C)
def XOR(c, b, a):
    """sets b to b^a"""
    res = b() ^ a()
    b.set(res)

@opcode(0x0D)
def SHR(c, b, a):
    """sets b to b>>>a. sets EX to ((b<<16)>>a)&0xFFFF (logical shift)"""
    res = (b() >> a())
    c.ex = ((b() << w) >> a()) & wmask
    res = res & wmask
    b.set(res)

@opcode(0x0E)
def ASR(c, b, a):
    """sets b to b>>a. sets EX to ((b<<16)>>>a)&0xFFFF (arithmetic shift) (treats b as signed)"""
    pass

@opcode(0x0F)
def SHL(c, b, a):
    """sets b to b<<a. sets EX to ((b<<a)>>16)&0xFFFF"""
    res = (b() << a())
    c.ex = ((b() << a()) >> w) & wmask
    res = res & wmask
    b.set(res)

@opcode(0x10)
def IFB(c, b, a):
    """performs next instruction only if (b&a)!=0"""
    if (b() & a()) != 0:
        c.skip = False
    else:
        c.skip = True

@opcode(0x11)
def IFC(c, b, a):
    """performs next instruction only if (b&a)==0"""
    if (b() & a()) == 0:
        c.skip = False
    else:
        c.skip = True

@opcode(0x12)
def IFE(c, b, a):
    """performs next instruction only if b==a"""
    if b() == a():
        c.skip = False
    else:
        c.skip = True

@opcode(0x13)
def IFN(c, b, a):
    """performs next instruction only if b!=a"""
    if b() != a():
        c.skip = False
    else:
        c.skip = True

@opcode(0x14)
def IFG(c, b, a):
    """performs next instruction only if b>a"""
    if b() > a():
        c.skip = False
    else:
        c.skip = True

@opcode(0x15)
def IFA(c, b, a):
    """performs next instruction only if b>a (signed)"""
    pass

@opcode(0x16)
def IFL(c, b, a):
    """performs next instruction only if b<a"""
    if b() < a():
        c.skip = False
    else:
        c.skip = True

@opcode(0x17)
def IFU(c, b, a):
    """performs next instruction only if b<a (signed)"""
    pass

@opcode(0x1A)
def ADX(c, b, a):
    """sets b to b+a+EX, sets EX to 0x0001 if there is an overflow, 0x0 otherwise"""
    pass

@opcode(0x1B)
def SBX(c, b, a):
    """sets b to b-a+EX, sets EX to 0xFFFF if there is an underflow, 0x0 otherwise"""
    pass

@opcode(0x1E)
def STI(c, b, a):
    """sets b to a, then increases I and J by 1"""
    pass

@opcode(0x1F)
def STD(c, b, a):
    """sets b to a, then decreases I and J by 1"""
    pass


@valcode(range(0x00, 0x08))
@pointerize
def register(c, code):
    """register (A, B, C, X, Y, Z, I, J, in that order)"""
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
def push(c):
    """[--SP] / PUSH if in b"""
    c.sp -= 1
    v = "c.m[0x%04X]" % c.sp
    return v

@valcode(0x18, a=True)
@pointerize
def pop(c):
    """[SP++] / POP if in a"""
    v = "c.m[0x%04X]" % c.sp
    c.sp += 1
    return v

@valcode(0x19)
@pointerize
def peek(c):
    """[SP] / PEEK"""
    v = "c.m[0x%04X]" % c.sp
    return v

@valcode(0x1A)
@pointerize
def pick(c):
    """[SP + next word] / PICK n"""
    pass

@valcode(0x1B)
@pointerize
def stack_pointer(c):
    """SP"""
    v = "c.sp"
    return v

@valcode(0x1C)
@pointerize
def program_counter(c):
    """PC"""
    v = "c.pc"
    return v

@valcode(0x1D)
@pointerize
def excess(c):
    """EX"""
    v = "c.ex"
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

@valcode(range(0x20, 0x40), a=True)
@pointerize
def literal(c, code):
    """literal value 0xFFFF-0x1E (-1..30) (literal) (only for a)"""
    v = "0x%04X" % ((code - 0x20 - 1) & 0xFFFF)
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
    """DCPU-16"""
    def __init__(c, memory=Memory(), debug=False):
        """If you don't specify memory, CPUs will share the same, default memory object"""
        c.m = memory
        c.clear()
        c.reset()
        c.debug = debug

    def reset(c):
        """reset CPU"""
        c.r = [0 for _ in xrange(0, 8)]
        c.pc = 0x0000
        c.sp = 0x0000
        c.ex = 0x0000
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
    ex = Register()

    def _op(c, word):
        """dispatch word to op and args"""
        opcode = word       & 0x1F
        b_code = word >>  5 & 0x1F
        a_code = word >> 10 & 0x3F
        try:
            op = _opcode_map[opcode]
            try:
                op = op[b_code]
            except TypeError:
                args = (c._pointer(b_code),
                        c._pointer(a_code, a=True))
            else:
                args = (c._pointer(a_code, a=True),)
            finally:
                if c.debug:
                    log(' '.join([op.__name__] + [arg.codestr for arg in args]))
        except KeyError:
            raise Exception('Invalid opcode %s at PC=%04X' % (["%02X"%x for x in opcode], c.pc))
        return op, args

    def _pointer(c, code, a=False):
        """get pointer to valcode"""
        try:
            if a:
                try: # a-only valcodes
                    return _valcode_a_map[code](c)
                except KeyError: # fallback to other values
                    return _valcode_map[code](c)
            else:
                # no a-only values
                return _valcode_map[code](c)
        except KeyError:
            raise Exception("Invalid valcode: 0x%02x" % code)

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
        last_sp = 0xFFFF
        while c.pc != last_pc or c.sp != last_sp:
            last_pc = c.pc
            last_sp = c.sp
            c.step()
        log("Infinite loop")

    def dump_r(c):
        """human-readable register status"""
        return " ".join( "%s=%04X" %
                (["A", "B", "C",
                  "X", "Y", "Z",
                  "I", "J",
                  "PC", "SP", "EX",
                  ][i],
                  (c.r + [c.pc, c.sp, c.ex])[i])
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
    # TODO: hand-reassembled for 1.5, but still some bugs
    0x7c01, 0x0030,             #     SET A, 0x30
    0x7fc1, 0x1000, 0x0020,     #     SET [0x1000], 0x20
    0x7803, 0x1000,             #     SUB A, [0X1000]
    0xc413,                     #     IFN A, 0x10
    0x7f81, 0x001a,             #         SET PC, crash
    0xacc1,                     #     SET I, 10
    0x7c01, 0x2000,             #     SET A, 0x2000
                                # :loop
    0x22C1, 0x2000,             #     SET [I + 0x2000], [A]
    0x88C3,                     #     SUB I, 1
    0x84D3,                     #     IFN I, 0
    0x7f81, 0x000d,             #         SET PC, loop
    0x9461,                     #     SET X, 4
    0x7c20, 0x0018,             #     JSR testsub
    0x7f81, 0x001a,             #     SET PC, crash
                                # :testsub
    0x946f,                     #     SHL X, 4
    0x6381,                     #     SET PC, POP
                                # :crash
    0x7f81, 0x001a,             #     SET PC, crash
]
