from bool2cmos.backend.parser.ast import Node, And, Or

def factor(expr: Node) -> Node:
    """
    Factors the expression to reduce transistor count.
    Mainly targets: (A & B) | (A & C) -> A & (B | C)
    Also supports: (A | B) & (A | C) -> A | (B & C)
    """
    
    # Recursively factor children first
    if isinstance(expr, And):
        left = factor(expr.left)
        right = factor(expr.right)
        expr = And(left, right)
        
        # Check for (A | B) & (A | C) -> A | (B & C)
        if isinstance(left, Or) and isinstance(right, Or):
            l_args = [left.left, left.right]
            r_args = [right.left, right.right]
            
            for i in range(2):
                for j in range(2):
                    if l_args[i] == r_args[j]:
                        common = l_args[i]
                        rem_l = l_args[1-i]
                        rem_r = r_args[1-j]
                        return Or(common, And(rem_l, rem_r))
                        
    elif isinstance(expr, Or):
        left = factor(expr.left)
        right = factor(expr.right)
        expr = Or(left, right)
        
        # Check for (A & B) | (A & C) -> A & (B | C)
        if isinstance(left, And) and isinstance(right, And):
            l_args = [left.left, left.right]
            r_args = [right.left, right.right]
            
            for i in range(2):
                for j in range(2):
                    if l_args[i] == r_args[j]:
                        common = l_args[i]
                        rem_l = l_args[1-i]
                        rem_r = r_args[1-j]
                        return And(common, Or(rem_l, rem_r))
                        
    return expr