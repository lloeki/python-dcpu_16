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

class TestCPUWithPrograms(unittest.TestCase):
    def setUP(self):
        pass

    def test_spec_demo(self):
        c = CPU()
        data = [
            0x7c01, 0x0030, 0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d,
            0x7dc1, 0x001a, 0xa861, 0x7c01, 0x2000, 0x2161, 0x2000, 0x8463,
            0x806d, 0x7dc1, 0x000d, 0x9031, 0x7c10, 0x0018, 0x7dc1, 0x001a,
            0x9037, 0x61c1, 0x7dc1, 0x001a, 0x0000, 0x0000, 0x0000, 0x0000,
        ]
        c.load_m(data=data)

        self.assertEqual(c.pc, 0)
        c.step() # SET A, 0x30
        self.assertEqual(c.a, 0x30)

        self.assertEqual(c.pc, 2)
        c.step() # SET [0x1000], 0x20
        self.assertEqual(c.m[0x1000], 0x20)

        self.assertEqual(c.pc, 5) 
        c.step() # SUB A, [0x1000]
        self.assertEqual(c.a, 0x10)

        self.assertEqual(c.pc, 7)
        c.step() # IFN A, 0x10
        self.assertEqual(c.pc, 8)
        self.assertEqual(c.skip, True)

        c.step() # skip SET PC, crash
        self.assertEqual(c.skip, False)

        self.assertEqual(c.pc, 10)
        c.step() # SET I, 10
        self.assertEqual(c.i, 0x0A)

        self.assertEqual(c.pc, 11)
        c.step() # SET A, 0x2000
        self.assertEqual(c.a, 0x2000)

        for i in range(10, 0, -1):
            self.assertEqual(c.pc, 13)
            c.step() # SET [0x2000+I], [A]
            self.assertEqual(c.m[0x2000+i], 0x0)

            self.assertEqual(c.pc, 15)
            c.step() # SUB I, 1
            self.assertEqual(c.i, i-1)

            self.assertEqual(c.pc, 16)
            c.step() # IFN I, 0
            self.assertEqual(c.skip, i-1==0)

            self.assertEqual(c.pc, 17)
            c.step() # SET PC, loop (with skip if c.i==0)

        self.assertEqual(c.pc, 19)
        c.step() # SET X, 0x4
        self.assertEqual(c.x, 0x4)

        self.assertEqual(c.pc, 20)
        c.step() # JSR testsub
        self.assertEqual(c.sp, 0xFFFF)
        self.assertEqual(c.m[0xFFFF], 22)

        self.assertEqual(c.pc, 24)
        c.step() # SHL X, 4
        self.assertEqual(c.x, 0x40)

        self.assertEqual(c.pc, 25)
        c.step() # SET PC, POP

        self.assertEqual(c.pc, 22)
        c.step() # SET PC, crash

        self.assertEqual(c.pc, 26)
        c.step() # SET PC, crash

        self.assertEqual(c.pc, 26)
        # endless loop


if __name__ == '__main__':
    cases = [
            'test.TestInstructions',
            'test.TestCPU',
            'test.TestCPUWithPrograms'
            ]
    suite = unittest.TestLoader().loadTestsFromNames(cases)
    unittest.TextTestRunner(verbosity=2).run(suite)
