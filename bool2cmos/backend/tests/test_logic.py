import unittest
from bool2cmos.backend.parser.ast import Var, Const, Not, And, Or
from bool2cmos.backend.logic.nnf import to_nnf
from bool2cmos.backend.logic.complement import get_complement
from bool2cmos.backend.logic.simplify import simplify
from bool2cmos.backend.logic.factor import factor

class TestLogic(unittest.TestCase):
    
    def test_nnf_de_morgan(self):
        # ~(A & B) -> ~A | ~B
        a = Var("A")
        b = Var("B")
        expr = Not(And(a, b))
        expected = Or(Not(a), Not(b))
        self.assertEqual(to_nnf(expr), expected)
        
        # ~(A | B) -> ~A & ~B
        expr = Not(Or(a, b))
        expected = And(Not(a), Not(b))
        self.assertEqual(to_nnf(expr), expected)

    def test_nnf_double_negation(self):
        # ~~A -> A
        a = Var("A")
        expr = Not(Not(a))
        self.assertEqual(to_nnf(expr), a)

    def test_complement(self):
        # Complement of A | B -> ~A & ~B
        a = Var("A")
        b = Var("B")
        expr = Or(a, b)
        expected = And(Not(a), Not(b))
        self.assertEqual(get_complement(expr), expected)

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
        
    def test_factor_basic(self):
        a = Var("A")
        b = Var("B")
        c = Var("C")
        # (A & B) | (A & C) -> A & (B | C)
        expr = Or(And(a, b), And(a, c))
        expected = And(a, Or(b, c))
        self.assertEqual(factor(expr), expected)

    def test_factor_reordered(self):
        a = Var("A")
        b = Var("B")
        c = Var("C")
        # (B & A) | (A & C) -> A & (B | C)  (checks different positions)
        expr = Or(And(b, a), And(a, c))
        # Note: My implementation keeps order of remaining terms: Or(b, c)
        expected = And(a, Or(b, c))
        self.assertEqual(factor(expr), expected)

if __name__ == '__main__':
    unittest.main()
