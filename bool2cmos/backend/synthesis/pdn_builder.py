from ..parser.ast import Node, Var, Not, And, Or
from ..graph.network import NetworkNode, Series, Parallel, Transistor, MosType

def build_pdn(expr: Node) -> NetworkNode:
    """
    Builds the Pull-Down Network (NMOS) from the inverted logic expression F'.
    
    Rules:
    - AND -> SERIES
    - OR -> PARALLEL
    - Var -> NMOS Transistor
    """
    if isinstance(expr, Var):
        return Transistor(gate=expr.name, mos_type=MosType.NMOS)
    elif isinstance(expr, Not):
        # Handle inverted literals, e.g. ~A
        if isinstance(expr.child, Var):
            return Transistor(gate=f"~{expr.child.name}", mos_type=MosType.NMOS)
        else:
            # Depending on how the AST is structured, this might need to handle complex negations
            # But usually we expect NNF (Negation Normal Form) or simplified inputs.
            # For now, treat as error or recurse if simple.
            raise ValueError("Complex NOT expressions should be simplified before synthesis.")
            
    elif isinstance(expr, And):
        series = Series()
        series.add_child(build_pdn(expr.left))
        series.add_child(build_pdn(expr.right))
        return series
        
    elif isinstance(expr, Or):
        parallel = Parallel()
        parallel.add_child(build_pdn(expr.left))
        parallel.add_child(build_pdn(expr.right))
        return parallel
        
    else:
        raise TypeError(f"Unknown expression type: {type(expr)}")