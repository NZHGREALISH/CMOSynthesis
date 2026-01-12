from ..graph.network import NetworkNode, Series, Parallel, Transistor, MosType, NodeType

def build_pun(pdn_node: NetworkNode) -> NetworkNode:
    """
    Builds the Pull-Up Network (PMOS) as the dual of the PDN.
    
    Rules:
    - SERIES <-> PARALLEL
    - NMOS -> PMOS
    - Gates are preserved
    """
    if pdn_node.type == NodeType.TRANSISTOR:
        if isinstance(pdn_node, Transistor):
            return Transistor(gate=pdn_node.gate, mos_type=MosType.PMOS)
        else:
             raise TypeError("Node type is TRANSISTOR but class is not Transistor")
             
    elif pdn_node.type == NodeType.SERIES:
        # Series in PDN becomes Parallel in PUN
        parallel = Parallel()
        for child in pdn_node.children:
            parallel.add_child(build_pun(child))
        return parallel
        
    elif pdn_node.type == NodeType.PARALLEL:
        # Parallel in PDN becomes Series in PUN
        series = Series()
        for child in pdn_node.children:
            series.add_child(build_pun(child))
        return series
        
    else:
        raise TypeError(f"Unknown node type: {pdn_node.type}")
