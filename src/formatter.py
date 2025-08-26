from __future__ import annotations

from typing import Dict, Callable, Optional, List

from .nodes import MacroNode, Node


def _format_sqrt(node: MacroNode) -> str:
    if not node.optional_arguments or (
        node.optional_arguments and node.optional_arguments[0] == "2"
    ):
        if node.arguments:
            return f"√({node.arguments[0]})"
        else:
            return "√"
    else:
        root_index = node.optional_arguments[0]
        if node.arguments:
            return f"({node.arguments[0]})^(1/{root_index})"
        else:
            return f"x^(1/{root_index})"

def _format_frac(node: MacroNode) -> str:
    return "frac"


DEFAULT_FORMATTERS = {
    "sqrt": _format_sqrt,
    "frac": _format_frac,
}


class Formatter:
    def __init__(
        self, formatters: Optional[Dict[str, Callable[[MacroNode], str]]] = None
    ):
        self.formatters = {**DEFAULT_FORMATTERS, **(formatters or {})}

    def format_node(self, node: MacroNode) -> str:
        if node.name in self.formatters:
            return self.formatters[node.name](node)
        else:
            raise ValueError(f"No formatter found for {node.name}")

    def format_nodes(self, nodes: List[Node]) -> str:
        return "".join(self.format_node(node) for node in nodes)
