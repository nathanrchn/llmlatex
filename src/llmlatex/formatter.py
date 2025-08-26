from __future__ import annotations

from typing import Dict, Callable, Optional, List

from .nodes import Node, TextNode, MacroNode, MultiNode


def _needs_parentheses(formatted_string: str) -> bool:
    if not formatted_string:
        return False
    
    if formatted_string.startswith("(") and formatted_string.endswith(")"):
        paren_count = 0
        for i, char in enumerate(formatted_string):
            if char == "(":
                paren_count += 1
            elif char == ")":
                paren_count -= 1
                if paren_count == 0 and i < len(formatted_string) - 1:
                    break
        else:
            if paren_count == 0:
                return False
    
    operators = {"+", "-", "*", "/", "^", "=", "<", ">", "≤", "≥", "±"}
    for op in operators:
        if op in formatted_string:
            return True
    
    if " " in formatted_string.strip():
        return True
    
    if ")/" in formatted_string or ")(" in formatted_string:
        return True
    
    return False


def _format_sqrt(node: MacroNode, formatter: Formatter) -> str:
    if not node.optional_arguments or (
        node.optional_arguments and node.optional_arguments[0] == "2"
    ):
        if node.arguments:
            formatted_arg = formatter._format_node(node.arguments[0])
            if _needs_parentheses(formatted_arg):
                return f"√({formatted_arg})"
            else:
                return f"√{formatted_arg}"
        else:
            return "√"
    else:
        root_index = node.optional_arguments[0]
        if node.arguments:
            formatted_arg = formatter._format_node(node.arguments[0])
            if _needs_parentheses(formatted_arg):
                return f"({formatted_arg})^(1/{root_index})"
            else:
                return f"{formatted_arg}^(1/{root_index})"
        else:
            return f"x^(1/{root_index})"


def _format_frac(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments and len(node.arguments) >= 2:
        numerator = formatter._format_node(node.arguments[0])
        denominator = formatter._format_node(node.arguments[1])
        
        if _needs_parentheses(numerator):
            numerator = f"({numerator})"
        if _needs_parentheses(denominator):
            denominator = f"({denominator})"
            
        return f"{numerator}/{denominator}"
    else:
        return "frac"


DEFAULT_FORMATTERS = {
    "sqrt": _format_sqrt,
    "frac": _format_frac,
}


class Formatter:
    def __init__(
        self,
        formatters: Optional[Dict[str, Callable[[MacroNode, Formatter], str]]] = None,
    ):
        self.formatters = {**DEFAULT_FORMATTERS, **(formatters or {})}

    def _format_text_node(self, node: TextNode) -> str:
        return node.content

    def _format_macro_node(self, node: MacroNode) -> str:
        if node.name in self.formatters:
            return self.formatters[node.name](node, self)
        else:
            raise ValueError(f"No formatter found for {node.name}")

    def _format_multi_node(self, node: MultiNode) -> str:
        return "".join(self._format_node(child) for child in node.content)

    def _format_node(self, node: Node) -> str:
        if isinstance(node, TextNode):
            return self._format_text_node(node)
        elif isinstance(node, MacroNode):
            return self._format_macro_node(node)
        elif isinstance(node, MultiNode):
            return self._format_multi_node(node)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")

    def format_nodes(self, nodes: List[Node]) -> str:
        return "".join(self._format_node(node) for node in nodes)
