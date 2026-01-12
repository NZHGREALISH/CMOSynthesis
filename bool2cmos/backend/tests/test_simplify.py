import unittest
from bool2cmos.backend.parser.ast import Var, Const, Not, And, Or
from bool2cmos.backend.logic.simplify import simplify

class TestSimplify(unittest.TestCase):
    
    def test_simplify_identity(self):
        a = Var("A")
        # A & 1 -> A
        self.assertEqual(simplify(And(a, Const(1))), a)
        # A | 0 -> A
        self.assertEqual(simplify(Or(a, Const(0))), a)

    def test_simplify_dominance(self):
        a = Var("A")
        # A & 0 -> 0
        self.assertEqual(simplify(And(a, Const(0))), Const(0))
        # A | 1 -> 1
        self.assertEqual(simplify(Or(a, Const(1))), Const(1))
    
    def test_simplify_idempotence(self):
        a = Var("A")
        # A & A -> A
        self.assertEqual(simplify(And(a, a)), a)
        # A | A -> A
        self.assertEqual(simplify(Or(a, a)), a)

    def test_simplify_complement(self):
        a = Var("A")
        # A & ~A -> 0
        self.assertEqual(simplify(And(a, Not(a))), Const(0))
        # A | ~A -> 1
        self.assertEqual(simplify(Or(a, Not(a))), Const(1))

if __name__ == '__main__':
    unittest.main()
