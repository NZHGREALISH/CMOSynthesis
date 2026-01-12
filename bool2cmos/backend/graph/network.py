from enum import Enum
from typing import List, Optional

class NodeType(Enum):
    SERIES = "SERIES"
    PARALLEL = "PARALLEL"
    TRANSISTOR = "TRANSISTOR"

class MosType(Enum):
    NMOS = "NMOS"
    PMOS = "PMOS"

class NetworkNode:
    def __init__(self, node_type: NodeType):
        self.type = node_type
        self.children: List['NetworkNode'] = []
        
    def add_child(self, child: 'NetworkNode'):
        self.children.append(child)
        
    def to_dict(self):
        return {
            "type": self.type.value,
            "children": [child.to_dict() for child in self.children]
        }

class Transistor(NetworkNode):
    def __init__(self, gate: str, mos_type: MosType):
        super().__init__(NodeType.TRANSISTOR)
        self.gate = gate
        self.mos_type = mos_type
        
    def to_dict(self):
        return {
            "type": self.type.value,
            "gate": self.gate,
            "mos_type": self.mos_type.value
        }

class Series(NetworkNode):
    def __init__(self, children: Optional[List[NetworkNode]] = None):
        super().__init__(NodeType.SERIES)
        if children:
            self.children = children

class Parallel(NetworkNode):
    def __init__(self, children: Optional[List[NetworkNode]] = None):
        super().__init__(NodeType.PARALLEL)
        if children:
            self.children = children
