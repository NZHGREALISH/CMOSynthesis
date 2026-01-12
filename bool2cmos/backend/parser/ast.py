from __future__ import annotations

from dataclasses import dataclass


class Node:
    pass

Expr = Node

@dataclass(frozen=True, slots=True)
class Const(Node):
    value: int # 0 or 1

    def __repr__(self) -> str:
        return str(self.value)

@dataclass(frozen=True, slots=True)
class Var(Node):
    name: str

    def __post_init__(self) -> None:
        if len(self.name) != 1 or not ("A" <= self.name <= "Z"):
            raise ValueError(f"Var name must be a single A–Z letter, got: {self.name!r}")

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class Not(Node):
    child: Node

    def __repr__(self) -> str:
        return f"Not({self.child!r})"


@dataclass(frozen=True, slots=True)
class And(Node):
    left: Node
    right: Node

    def __repr__(self) -> str:
        return f"And({self.left!r},{self.right!r})"


@dataclass(frozen=True, slots=True)
class Or(Node):
    left: Node
    right: Node

    def __repr__(self) -> str:
        return f"Or({self.left!r},{self.right!r})"