from __future__ import annotations

from typing import Dict, Callable, Optional, List

from .nodes import Node, TextNode, MacroNode, MultiNode


def _simple_format(text: str) -> Callable[[MacroNode, Formatter], str]:
    def _simple_format_wrapper(node: MacroNode, formatter: Formatter) -> str:
        return text

    return _simple_format_wrapper


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


def _format_textit(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"_{content}_"
    else:
        return ""


def _format_text(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_rceil(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"⌈{content}⌉"
    else:
        return "⌈⌉"


def _format_lceil(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"⌈{content}⌉"
    else:
        return "⌈⌉"


def _format_floor(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"⌊{content}⌋"
    else:
        return "⌊⌋"


def _format_boxed(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"[{content}]"
    else:
        return "[]"


def _format_begin(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_end(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_bar(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return "̄"


def _format_overline(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return "̄"


def _format_textbf(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"**{content}**"
    else:
        return ""


def _format_mathrm(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_mod(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f" mod {content}"
    else:
        return ""


def _format_pmod(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f" (mod {content})"
    else:
        return ""


def _format_binom(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments and len(node.arguments) >= 2:
        n = formatter._format_node(node.arguments[0])
        k = formatter._format_node(node.arguments[1])
        return f"C({n},{k})"
    else:
        return ""


def _format_dfrac(node: MacroNode, formatter: Formatter) -> str:
    return _format_frac(node, formatter)


def _format_left(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        delimiter = formatter._format_node(node.arguments[0])
        return delimiter
    else:
        return ""


def _format_right(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        delimiter = formatter._format_node(node.arguments[0])
        return delimiter
    else:
        return ""


DEFAULT_FORMATTERS = {
    "sqrt": _format_sqrt,
    "frac": _format_frac,
    "dfrac": _format_dfrac,
    "theta": _simple_format("θ"),
    "mu": _simple_format("μ"),
    "rho": _simple_format("ρ"),
    "phi": _simple_format("φ"),
    "Delta": _simple_format("Δ"),
    "pi": _simple_format("π"),
    "approx": _simple_format("≈"),
    "cdot": _simple_format("·"),
    "ge": _simple_format("≥"),
    "geq": _simple_format("≥"),
    "leq": _simple_format("≤"),
    "equiv": _simple_format("≡"),
    "neq": _simple_format("≠"),
    "pm": _simple_format("±"),
    "Rightarrow": _simple_format("⇒"),
    "rightarrow": _simple_format("→"),
    "div": _simple_format("/"),
    "times": _simple_format("*"),
    "cap": _simple_format("∩"),
    "cup": _simple_format("∪"),
    "setminus": _simple_format("\\"),
    "circ": _simple_format("∘"),
    "therefore": _simple_format("∴"),
    "quad": _simple_format("    "),
    "cdots": _simple_format("⋯"),
    "ldots": _simple_format("..."),
    "lfloor": _simple_format("⌊"),
    "rfloor": _simple_format("⌋"),
    "lceil": _format_lceil,
    "rceil": _format_rceil,
    "floor": _format_floor,
    "log": _simple_format("log"),
    "ln": _simple_format("ln"),
    "min": _simple_format("min"),
    "max": _simple_format("max"),
    "gcd": _simple_format("gcd"),
    "sum": _simple_format("∑"),
    "textit": _format_textit,
    "textbf": _format_textbf,
    "text": _format_text,
    "mathrm": _format_mathrm,
    "bar": _format_bar,
    "overline": _format_overline,
    "boxed": _format_boxed,
    "mod": _format_mod,
    "pmod": _format_pmod,
    "binom": _format_binom,
    "left": _format_left,
    "right": _format_right,
    "d": _simple_format("d"),
    "begin": _format_begin,
    "end": _format_end,
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
