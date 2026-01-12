from bool2cmos.backend.parser.ast import Node, Var, Const, Not, And, Or

def to_nnf(expr: Node) -> Node:
    """
    Convert an expression to Negation Normal Form (NNF).
    In NNF, negation operator 'Not' is applied only to variables.
    
    Rules:
    - ~(A & B) -> ~A | ~B
    - ~(A | B) -> ~A & ~B
    - ~~A -> A
    """
    if isinstance(expr, Var) or isinstance(expr, Const):
        return expr
    
    if isinstance(expr, And):
        return And(to_nnf(expr.left), to_nnf(expr.right))
    
    if isinstance(expr, Or):
        return Or(to_nnf(expr.left), to_nnf(expr.right))
    
    if isinstance(expr, Not):
        child = expr.child
        
        # Double negation: ~~A -> A
        if isinstance(child, Not):
            return to_nnf(child.child)
        
        # De Morgan's Law 1: ~(A & B) -> ~A | ~B
        if isinstance(child, And):
            return Or(to_nnf(Not(child.left)), to_nnf(Not(child.right)))
        
        # De Morgan's Law 2: ~(A | B) -> ~A & ~B
        if isinstance(child, Or):
            return And(to_nnf(Not(child.left)), to_nnf(Not(child.right)))
        
        # Negation of constants
        if isinstance(child, Const):
            return Const(1 - child.value)
            
        # If it's Not(Var), it's already in NNF (at this level)
        if isinstance(child, Var):
            return expr
            
    return expr