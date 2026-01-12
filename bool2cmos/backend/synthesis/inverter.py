from typing import List, Set
from ..graph.network import NetworkNode, NodeType, Transistor

def get_required_inverters(node: NetworkNode) -> List[str]:
    """
    Traverses the network (PDN usually sufficient as PUN has same gates) 
    and returns a list of inverted signals (e.g. '~A') that appear.
    """
    inverters: Set[str] = set()
    
    def traverse(n: NetworkNode):
        if n.type == NodeType.TRANSISTOR:
            if isinstance(n, Transistor):
                # Check if gate indicates inversion
                # We assume convention that inverted signals start with '~'
                if n.gate.startswith("~"):
                    inverters.add(n.gate)
        elif n.children:
            for child in n.children:
                traverse(child)
                
    traverse(node)
    return sorted(list(inverters))

def count_inverter_transistors(inverters: List[str]) -> int:
    """
    Returns the total transistor count for the inverters.
    Each inverter requires 2 transistors (1 NMOS, 1 PMOS).
    """
    return len(inverters) * 2
