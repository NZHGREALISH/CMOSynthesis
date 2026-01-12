from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TransistorCount:
    pdn_leaves: int
    pun_leaves: int
    inverters: int

    @property
    def inverter_transistors(self) -> int:
        return self.inverters * 2

    @property
    def total(self) -> int:
        return self.pdn_leaves + self.pun_leaves + self.inverter_transistors

    def to_dict(self) -> dict[str, int]:
        return {
            "pdn_leaves": self.pdn_leaves,
            "pun_leaves": self.pun_leaves,
            "inverters": self.inverters,
            "inverter_transistors": self.inverter_transistors,
            "total": self.total,
        }


def _iter_children(obj: Any) -> Iterable[Any]:
    if isinstance(obj, Mapping):
        for key in ("children", "nodes", "items", "args", "operands"):
            value = obj.get(key)
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
                return value
    return ()


def _is_leaf_node(obj: Any) -> bool:
    if isinstance(obj, Mapping):
        node_type = obj.get("type") or obj.get("kind")
        if node_type in {"leaf", "transistor", "device"}:
            return True
        if any(k in obj for k in ("literal", "var", "symbol", "gate")) and not _iter_children(obj):
            return True
    return False


def count_leaves(network: Any) -> int:
    """
    Counts "leaf" devices in a PDN/PUN network structure.

    The project currently doesn't enforce a single canonical schema, so this
    function supports common JSON-like encodings:
      - dict nodes with `type: leaf/transistor/device`
      - dict nodes with children under `children`/`nodes`/`items`/`args`/`operands`
      - lists/tuples of nodes
    """

    if network is None:
        return 0

    if _is_leaf_node(network):
        return 1

    if isinstance(network, (list, tuple)):
        return sum(count_leaves(item) for item in network)

    children = _iter_children(network)
    if children:
        return sum(count_leaves(child) for child in children)

    return 0


def transistor_count(pdn: Any, pun: Any, inverter_count: int = 0) -> TransistorCount:
    """
    Computes transistor counts:
      - PDN leaf count
      - PUN leaf count
      - inverter count (each inverter is 2 transistors)
    """

    if inverter_count < 0:
        raise ValueError("inverter_count must be >= 0")

    return TransistorCount(
        pdn_leaves=count_leaves(pdn),
        pun_leaves=count_leaves(pun),
        inverters=inverter_count,
    )
