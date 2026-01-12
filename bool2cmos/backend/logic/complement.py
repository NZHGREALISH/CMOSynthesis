from bool2cmos.backend.parser.ast import Node, Not
from bool2cmos.backend.logic.nnf import to_nnf

def get_complement(expr: Node) -> Node:
    """
    Returns the logical complement (F') of the given expression F.
    The result is returned in Negation Normal Form (NNF).
    """
    return to_nnf(Not(expr))