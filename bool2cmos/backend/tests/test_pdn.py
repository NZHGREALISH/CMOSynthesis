import unittest
from bool2cmos.backend.parser.ast import Var, And, Or, Not
from bool2cmos.backend.synthesis.pdn_builder import build_pdn
from bool2cmos.backend.synthesis.pun_builder import build_pun
from bool2cmos.backend.synthesis.inverter import get_required_inverters, count_inverter_transistors
from bool2cmos.backend.graph.network import NodeType, MosType

class TestSynthesis(unittest.TestCase):
    def setUp(self):
        # F' = A + (B * ~C)
        # Using binary AST: Or(Var('A'), And(Var('B'), Not(Var('C'))))
        self.expr = Or(
            Var('A'),
            And(
                Var('B'),
                Not(Var('C'))
            )
        )

    def test_pdn_structure(self):
        pdn = build_pdn(self.expr)
        self.assertEqual(pdn.type, NodeType.PARALLEL)
        self.assertEqual(len(pdn.children), 2)
        
        # Check first child: Transistor A
        # Note: Since build_pdn processes expr.left then expr.right, 
        # and we constructed Or(A, And(...)), A should be first.
        child1 = pdn.children[0]
        self.assertEqual(child1.type, NodeType.TRANSISTOR)
        self.assertEqual(child1.gate, 'A')
        self.assertEqual(child1.mos_type, MosType.NMOS)
        
        # Check second child: Series(B, ~C)
        child2 = pdn.children[1]
        self.assertEqual(child2.type, NodeType.SERIES)
        self.assertEqual(len(child2.children), 2)
        
        t1 = child2.children[0]
        self.assertEqual(t1.type, NodeType.TRANSISTOR)
        self.assertEqual(t1.gate, 'B')
        
        t2 = child2.children[1]
        self.assertEqual(t2.type, NodeType.TRANSISTOR)
        self.assertEqual(t2.gate, '~C')

    def test_pun_structure(self):
        pdn = build_pdn(self.expr)
        pun = build_pun(pdn)
        
        # Dual of Parallel is Series
        self.assertEqual(pun.type, NodeType.SERIES)
        self.assertEqual(len(pun.children), 2)
        
        # Dual of A is PMOS A
        child1 = pun.children[0]
        self.assertEqual(child1.type, NodeType.TRANSISTOR)
        self.assertEqual(child1.gate, 'A')
        self.assertEqual(child1.mos_type, MosType.PMOS)
        
        # Dual of Series is Parallel
        child2 = pun.children[1]
        self.assertEqual(child2.type, NodeType.PARALLEL)
        
        t1 = child2.children[0]
        self.assertEqual(t1.gate, 'B')
        self.assertEqual(t1.mos_type, MosType.PMOS)
        
        t2 = child2.children[1]
        self.assertEqual(t2.gate, '~C')
        self.assertEqual(t2.mos_type, MosType.PMOS)

    def test_inverter_tracking(self):
        pdn = build_pdn(self.expr)
        invs = get_required_inverters(pdn)
        self.assertEqual(invs, ['~C'])
        self.assertEqual(count_inverter_transistors(invs), 2)

if __name__ == '__main__':
    unittest.main()
