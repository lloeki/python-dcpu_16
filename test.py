import unittest
import random
import dcpu_16
from dcpu_16 import CPU

class TestInstructions(unittest.TestCase):
    """Instruction set"""

    def setUp(self):
        pass

    def test_SET(self):
        self.assertEqual(dcpu_16.SET.opcode, (0x01,))
        c = CPU()
        c.a = 0x0
        c.b = 0x42
        dcpu_16.SET(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x42)
        self.assertEqual(c.b, 0x42)

    def test_ADD(self):
        self.assertEqual(dcpu_16.ADD.opcode, (0x02,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.ADD(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17+0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_SUB(self):
        self.assertEqual(dcpu_16.SUB.opcode, (0x03,))
        c = CPU()
        c.a = 0x42
        c.b = 0x17
        dcpu_16.SUB(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x42-0x17)
        self.assertEqual(c.b, 0x17)
        self.assertEqual(c.ex, 0x0)

    def test_MUL(self):
        self.assertEqual(dcpu_16.MUL.opcode, (0x04,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.MUL(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17*0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_MLI(self):
        self.assertEqual(dcpu_16.MLI.opcode, (0x05,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.MLI(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17*0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_DIV(self):
        self.assertEqual(dcpu_16.DIV.opcode, (0x06,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.DIV(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17/0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, ((0x17<<16)/0x42)&0xFFFF)

    def test_DVI(self):
        self.assertEqual(dcpu_16.DVI.opcode, (0x07,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.DIV(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17/0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, ((0x17<<16)/0x42)&0xFFFF)

    def test_MOD(self):
        self.assertEqual(dcpu_16.MOD.opcode, (0x08,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.MOD(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17%0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_MDI(self):
        self.assertEqual(dcpu_16.MDI.opcode, (0x09,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.MOD(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17%0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_AND(self):
        self.assertEqual(dcpu_16.AND.opcode, (0x0A,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.AND(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17&0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_BOR(self):
        self.assertEqual(dcpu_16.BOR.opcode, (0x0B,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.BOR(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17|0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_XOR(self):
        self.assertEqual(dcpu_16.XOR.opcode, (0x0C,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.XOR(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17^0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_SHR(self):
        self.assertEqual(dcpu_16.SHR.opcode, (0x0D,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.SHR(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17>>0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_ASR(self):
        self.assertEqual(dcpu_16.ASR.opcode, (0x0E,))
        c = CPU()
        c.a = 0x17
        c.b = 0x42
        dcpu_16.ASR(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17>>0x42)
        self.assertEqual(c.b, 0x42)
        self.assertEqual(c.ex, 0x0)

    def test_SHL(self):
        self.assertEqual(dcpu_16.SHL.opcode, (0x0F,))
        c = CPU()
        c.a = 0x17
        c.b = 0x4
        dcpu_16.SHL(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.a, 0x17<<0x4 & dcpu_16.wmask)
        self.assertEqual(c.b, 0x4)
        self.assertEqual(c.ex, 0x0)

    def test_IFB(self):
        self.assertEqual(dcpu_16.IFB.opcode, (0x10,))
        c = CPU()

        c.a = 0xF0F0
        c.b = 0x0F0F
        dcpu_16.IFB(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, True)

        c.a = 0xF1F0
        c.b = 0x0F0F
        dcpu_16.IFB(c, c._pointer(0x0), c._pointer(0x1))
        self.assertEqual(c.skip, False)

    def test_IFE(self):
        self.assertEqual(dcpu_16.IFE.opcode, (0x12,))
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
        self.assertEqual(dcpu_16.IFN.opcode, (0x13,))
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
        self.assertEqual(dcpu_16.IFG.opcode, (0x14,))
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

    def test_JSR(self):
        self.assertEqual(dcpu_16.JSR.opcode, (0x00, 0x01))
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
        self.assertEqual(c.ex, 0)
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
        self.assertEqual(c.ex, 0)
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
        c.load_m(data=dcpu_16.spec_demo)

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
