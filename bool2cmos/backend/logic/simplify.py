from bool2cmos.backend.parser.ast import Node, Var, Const, Not, And, Or

def simplify(expr: Node) -> Node:
    """
    Simplifies the boolean expression using basic rules:
    - Identity: X & 1 = X, X | 0 = X
    - Dominance: X & 0 = 0, X | 1 = 1
    - Idempotence: X & X = X, X | X = X
    - Complement: X & ~X = 0, X | ~X = 1
    - Double Negation: ~~X = X
    - Constant folding for Not
    """
    
    if isinstance(expr, Not):
        child = simplify(expr.child)
        if isinstance(child, Const):
            return Const(1 - child.value)
        if isinstance(child, Not):
            return child.child
        return Not(child)

    if isinstance(expr, And):
        left = simplify(expr.left)
        right = simplify(expr.right)
        
        # Dominance: X & 0 = 0
        if isinstance(left, Const) and left.value == 0: return Const(0)
        if isinstance(right, Const) and right.value == 0: return Const(0)
        
        # Identity: X & 1 = X
        if isinstance(left, Const) and left.value == 1: return right
        if isinstance(right, Const) and right.value == 1: return left
        
        # Idempotence: X & X = X
        if left == right:
            return left
            
        # Complement: X & ~X = 0
        if is_complement(left, right):
            return Const(0)
            
        return And(left, right)

    if isinstance(expr, Or):
        left = simplify(expr.left)
        right = simplify(expr.right)
        
        # Dominance: X | 1 = 1
        if isinstance(left, Const) and left.value == 1: return Const(1)
        if isinstance(right, Const) and right.value == 1: return Const(1)
        
        # Identity: X | 0 = X
        if isinstance(left, Const) and left.value == 0: return right
        if isinstance(right, Const) and right.value == 0: return left
        
        # Idempotence: X | X = X
        if left == right:
            return left
            
        # Complement: X | ~X = 1
        if is_complement(left, right):
            return Const(1)
            
        return Or(left, right)

    return expr

def is_complement(expr1: Node, expr2: Node) -> bool:
    """Checks if expr1 is the negation of expr2 or vice versa."""
    if isinstance(expr1, Not) and expr1.child == expr2:
        return True
    if isinstance(expr2, Not) and expr2.child == expr1:
        return True
    return False