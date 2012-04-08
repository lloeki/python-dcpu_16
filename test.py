import unittest
import random
import dcpu_16
from dcpu_16 import CPU

class TestInstructions(unittest.TestCase):
    """Instruction set"""

    def setUp(self):
        pass

    def test_SET(self):
        dcpu_16.SET.opcode = (0x1,)
        c = CPU()
        c.a = 0x0
        c.b = 0x42
        dcpu_16.SET(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x42)
        self.assertEqual(c.b, 0x42)

    def test_ADD(self):
        dcpu_16.SET.opcode = (0x2,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.ADD(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17+0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, 0x0)

    def test_SUB(self):
        dcpu_16.SET.opcode = (0x3,)
        c = CPU()
        c.a = 0x42
        c.b = 0x17
        dcpu_16.SUB(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x42-0x17)
        self.assertEqual(c.b, 0x17)
        self.assertEqual(c.o, 0x0)

    def test_MUL(self):
        dcpu_16.SET.opcode = (0x4,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.MUL(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17*0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, 0x0)

    def test_DIV(self):
        dcpu_16.SET.opcode = (0x5,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.DIV(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17/0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, ((0x17<<16)/0x42)&0xFFFF)

    def test_MOD(self):
        dcpu_16.SET.opcode = (0x6,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.MOD(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17%0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, 0x0)

    def test_SHL(self):
        dcpu_16.SET.opcode = (0x7,)
        c = CPU()
        c.a = 0x17
        c.b = 0x4
        dcpu_16.SHL(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17<<0x4 & dcpu_16.wmask)
        self.assertEqual(c.b, 0x4)
        self.assertEqual(c.o, 0x0)

    def test_SHR(self):
        dcpu_16.SET.opcode = (0x8,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.SHR(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17>>0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, 0x0)

    def test_AND(self):
        dcpu_16.SET.opcode = (0x9,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.AND(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17&0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, 0x0)

    def test_BOR(self):
        dcpu_16.SET.opcode = (0xA,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.BOR(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17|0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, 0x0)

    def test_XOR(self):
        dcpu_16.SET.opcode = (0xB,)
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.XOR(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17^0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.o, 0x0)

    def test_IFE(self):
        dcpu_16.SET.opcode = (0xC,)
        c = CPU()

        c.a = 0x17
        c.b = 0x42
        dcpu_16.IFE(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, True)

        c.a = 0x42
        c.b = 0x42
        dcpu_16.IFE(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, False)

    def test_IFN(self):
        dcpu_16.SET.opcode = (0xD,)
        c = CPU()

        c.a = 0x17
        c.b = 0x42
        dcpu_16.IFN(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, False)

        c.a = 0x42
        c.b = 0x42
        dcpu_16.IFN(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, True)

    def test_IFG(self):
        dcpu_16.SET.opcode = (0xE,)
        c = CPU()

        c.a = 0x41
        c.b = 0x42
        dcpu_16.IFG(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, True)

        c.a = 0x42
        c.b = 0x42
        dcpu_16.IFG(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, True)

        c.a = 0x42
        c.b = 0x41
        dcpu_16.IFG(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, False)

    def test_IFB(self):
        dcpu_16.SET.opcode = (0xF,)
        c = CPU()

        c.a = 0xF0F0
        c.b = 0x0F0F
        dcpu_16.IFB(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, True)

        c.a = 0xF1F0
        c.b = 0x0F0F
        dcpu_16.IFB(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, False)

    def test_JSR(self):
        dcpu_16.JSR.opcode = (0x0, 0x1)
        c = CPU()

        c.a = 0xDEAD
        c.pc = 0xBEEF
        dcpu_16.JSR(c, c._pointer(0x0))
        self.assertEqual(c.pc, 0xDEAD)
        self.assertEqual(c.sp, 0xFFFF)
        self.assertEqual(c.m[0xFFFF], 0xBEEF)

class TestCPU(unittest.TestCase):
    """CPU behavior"""

    def setUp(self):
        pass

    def test_initial_state(self):
        """Initial state shall be all zero"""
        c = CPU()
        for r in c.r:
            self.assertEqual(r, 0)
        self.assertEqual(c.pc, 0)
        self.assertEqual(c.o, 0)
        self.assertEqual(c.sp, 0)
        self.assertEqual(c.skip, False)
        self.assertEqual(c.pc, 0)
        for r in c.m:
            self.assertEqual(r, 0)

    def test_reset(self):
        """Reset shall bring CPU register state to initial"""
        c = CPU()
        for i in xrange(0x8):
            c.r[i] = random.randrange(0x10000)
        c.reset()
        for r in c.r:
            self.assertEqual(r, 0)
        self.assertEqual(c.pc, 0)
        self.assertEqual(c.o, 0)
        self.assertEqual(c.sp, 0)
        self.assertEqual(c.skip, False)
        self.assertEqual(c.pc, 0)

    def test_clear(self):
        """Clear shall zero memory"""
        c = CPU()
        for i in xrange(0x10000):
            c.m[i] = random.randrange(0x10000)
        c.clear()
        for r in c.m:
            self.assertEqual(r, 0)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromNames(['test.TestInstructions', 'test.TestCPU'])
    unittest.TextTestRunner(verbosity=2).run(suite)
