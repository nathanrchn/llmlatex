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


# Additional mathematical functions and operators
def _format_hat(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}̂"
    else:
        return "̂"


def _format_tilde(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}̃"
    else:
        return "̃"


def _format_vec(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}⃗"
    else:
        return "⃗"


def _format_dot(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}̇"
    else:
        return "̇"


def _format_ddot(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}̈"
    else:
        return "̈"


def _format_underline(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"_{content}_"
    else:
        return ""


def _format_overbrace(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"⏞{content}"
    else:
        return "⏞"


def _format_underbrace(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"⏟{content}"
    else:
        return "⏟"


def _format_widetilde(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}̃"
    else:
        return "̃"


def _format_widehat(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}̂"
    else:
        return "̂"


def _format_mathbf(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"**{content}**"
    else:
        return ""


def _format_mathit(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"_{content}_"
    else:
        return ""


def _format_mathcal(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_mathbb(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_boldsymbol(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"**{content}**"
    else:
        return ""


def _format_cancel(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"~~{content}~~"
    else:
        return ""


# Additional complex formatters
def _format_cbrt(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        formatted_arg = formatter._format_node(node.arguments[0])
        if _needs_parentheses(formatted_arg):
            return f"∛({formatted_arg})"
        else:
            return f"∛{formatted_arg}"
    else:
        return "∛"


def _format_xrightarrow(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"--{content}-->"
    else:
        return "--->"


def _format_overrightarrow(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"{content}⃗"
    else:
        return "⃗"


def _format_overleftrightarrow(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"↔{content}"
    else:
        return "↔"


def _format_stackrel(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments and len(node.arguments) >= 2:
        top = formatter._format_node(node.arguments[0])
        bottom = formatter._format_node(node.arguments[1])
        return f"{bottom}^{top}"
    else:
        return ""


def _format_overset(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments and len(node.arguments) >= 2:
        top = formatter._format_node(node.arguments[0])
        bottom = formatter._format_node(node.arguments[1])
        return f"{bottom}^{top}"
    else:
        return ""


def _format_underset(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments and len(node.arguments) >= 2:
        bottom = formatter._format_node(node.arguments[0])
        top = formatter._format_node(node.arguments[1])
        return f"{top}_{bottom}"
    else:
        return ""


def _format_operatorname(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_phantom(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return " " * len(content)  # Replace with spaces
    else:
        return ""


def _format_hphantom(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return " " * len(content)  # Replace with spaces
    else:
        return ""


def _format_fbox(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"[{content}]"
    else:
        return "[]"


def _format_mbox(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_hbox(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        return formatter._format_node(node.arguments[0])
    else:
        return ""


def _format_emph(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"_{content}_"
    else:
        return ""


# Document structure formatters (simple versions)
def _format_section(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"# {content}"
    else:
        return ""


def _format_subsection(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"## {content}"
    else:
        return ""


def _format_title(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"Title: {content}"
    else:
        return ""


def _format_author(node: MacroNode, formatter: Formatter) -> str:
    if node.arguments:
        content = formatter._format_node(node.arguments[0])
        return f"Author: {content}"
    else:
        return ""


DEFAULT_FORMATTERS = {
    # Basic formatters
    "sqrt": _format_sqrt,
    "frac": _format_frac,
    "dfrac": _format_frac,
    "tfrac": _format_frac,
    "cfrac": _format_frac,
    
    # Greek letters (lowercase)
    "alpha": _simple_format("α"),
    "beta": _simple_format("β"),
    "gamma": _simple_format("γ"),
    "delta": _simple_format("δ"),
    "epsilon": _simple_format("ε"),
    "varepsilon": _simple_format("ε"),
    "zeta": _simple_format("ζ"),
    "eta": _simple_format("η"),
    "theta": _simple_format("θ"),
    "vartheta": _simple_format("ϑ"),
    "iota": _simple_format("ι"),
    "kappa": _simple_format("κ"),
    "lambda": _simple_format("λ"),
    "mu": _simple_format("μ"),
    "nu": _simple_format("ν"),
    "xi": _simple_format("ξ"),
    "pi": _simple_format("π"),
    "varpi": _simple_format("ϖ"),
    "rho": _simple_format("ρ"),
    "varrho": _simple_format("ϱ"),
    "sigma": _simple_format("σ"),
    "tau": _simple_format("τ"),
    "upsilon": _simple_format("υ"),
    "phi": _simple_format("φ"),
    "varphi": _simple_format("φ"),
    "chi": _simple_format("χ"),
    "psi": _simple_format("ψ"),
    "omega": _simple_format("ω"),
    
    # Greek letters (uppercase)
    "Gamma": _simple_format("Γ"),
    "Delta": _simple_format("Δ"),
    "Theta": _simple_format("Θ"),
    "Lambda": _simple_format("Λ"),
    "Xi": _simple_format("Ξ"),
    "Pi": _simple_format("Π"),
    "Sigma": _simple_format("Σ"),
    "Upsilon": _simple_format("Υ"),
    "Phi": _simple_format("Φ"),
    "Chi": _simple_format("Χ"),
    "Psi": _simple_format("Ψ"),
    "Omega": _simple_format("Ω"),
    
    # Comparison operators
    "lt": _simple_format("<"),
    "le": _simple_format("≤"),
    "leq": _simple_format("≤"),
    "leqq": _simple_format("≤"),
    "leqslant": _simple_format("≤"),
    "gt": _simple_format(">"),
    "ge": _simple_format("≥"),
    "geq": _simple_format("≥"),
    "geqq": _simple_format("≥"),
    "geqslant": _simple_format("≥"),
    "eq": _simple_format("="),
    "neq": _simple_format("≠"),
    "ne": _simple_format("≠"),
    "equiv": _simple_format("≡"),
    "approx": _simple_format("≈"),
    "sim": _simple_format("∼"),
    "simeq": _simple_format("≃"),
    "cong": _simple_format("≅"),
    "propto": _simple_format("∝"),
    
    # Set operations
    "in": _simple_format("∈"),
    "notin": _simple_format("∉"),
    "ni": _simple_format("∋"),
    "subset": _simple_format("⊂"),
    "supset": _simple_format("⊃"),
    "subseteq": _simple_format("⊆"),
    "supseteq": _simple_format("⊇"),
    "subsetneq": _simple_format("⊊"),
    "supsetneq": _simple_format("⊋"),
    "cap": _simple_format("∩"),
    "cup": _simple_format("∪"),
    "setminus": _simple_format("∖"),
    "emptyset": _simple_format("∅"),
    "varnothing": _simple_format("∅"),
    
    # Logic operators
    "forall": _simple_format("∀"),
    "exists": _simple_format("∃"),
    "nexists": _simple_format("∄"),
    "neg": _simple_format("¬"),
    "lnot": _simple_format("¬"),
    "land": _simple_format("∧"),
    "wedge": _simple_format("∧"),
    "lor": _simple_format("∨"),
    "vee": _simple_format("∨"),
    
    # Arrows
    "leftarrow": _simple_format("←"),
    "rightarrow": _simple_format("→"),
    "leftrightarrow": _simple_format("↔"),
    "Leftarrow": _simple_format("⇐"),
    "Rightarrow": _simple_format("⇒"),
    "Leftrightarrow": _simple_format("⇔"),
    "iff": _simple_format("⇔"),
    "uparrow": _simple_format("↑"),
    "downarrow": _simple_format("↓"),
    "nearrow": _simple_format("↗"),
    "searrow": _simple_format("↘"),
    "swarrow": _simple_format("↙"),
    "nwarrow": _simple_format("↖"),
    "mapsto": _simple_format("↦"),
    "to": _simple_format("→"),
    
    # Binary operations
    "pm": _simple_format("±"),
    "mp": _simple_format("∓"),
    "times": _simple_format("×"),
    "div": _simple_format("÷"),
    "cdot": _simple_format("·"),
    "bullet": _simple_format("•"),
    "circ": _simple_format("∘"),
    "ast": _simple_format("∗"),
    "star": _simple_format("⋆"),
    "oplus": _simple_format("⊕"),
    "ominus": _simple_format("⊖"),
    "otimes": _simple_format("⊗"),
    "oslash": _simple_format("⊘"),
    "odot": _simple_format("⊙"),
    
    # Integrals and sums
    "sum": _simple_format("∑"),
    "prod": _simple_format("∏"),
    "int": _simple_format("∫"),
    "oint": _simple_format("∮"),
    "iint": _simple_format("∬"),
    "iiint": _simple_format("∭"),
    
    # Delimiters
    "lfloor": _simple_format("⌊"),
    "rfloor": _simple_format("⌋"),
    "lceil": _format_lceil,
    "rceil": _format_rceil,
    "floor": _format_floor,
    "langle": _simple_format("⟨"),
    "rangle": _simple_format("⟩"),
    "lvert": _simple_format("|"),
    "rvert": _simple_format("|"),
    "lVert": _simple_format("‖"),
    "rVert": _simple_format("‖"),
    "vert": _simple_format("|"),
    "Vert": _simple_format("‖"),
    
    # Trigonometric functions
    "sin": _simple_format("sin"),
    "cos": _simple_format("cos"),
    "tan": _simple_format("tan"),
    "cot": _simple_format("cot"),
    "sec": _simple_format("sec"),
    "csc": _simple_format("csc"),
    "arcsin": _simple_format("arcsin"),
    "arccos": _simple_format("arccos"),
    "arctan": _simple_format("arctan"),
    "arccot": _simple_format("arccot"),
    "sinh": _simple_format("sinh"),
    "cosh": _simple_format("cosh"),
    "tanh": _simple_format("tanh"),
    "coth": _simple_format("coth"),
    
    # Logarithmic and exponential functions
    "log": _simple_format("log"),
    "ln": _simple_format("ln"),
    "lg": _simple_format("lg"),
    "exp": _simple_format("exp"),
    
    # Mathematical functions
    "min": _simple_format("min"),
    "max": _simple_format("max"),
    "sup": _simple_format("sup"),
    "inf": _simple_format("inf"),
    "lim": _simple_format("lim"),
    "limsup": _simple_format("lim sup"),
    "liminf": _simple_format("lim inf"),
    "gcd": _simple_format("gcd"),
    "lcm": _simple_format("lcm"),
    "det": _simple_format("det"),
    "dim": _simple_format("dim"),
    "ker": _simple_format("ker"),
    "deg": _simple_format("deg"),
    "Pr": _simple_format("Pr"),
    
    # Special symbols
    "infty": _simple_format("∞"),
    "partial": _simple_format("∂"),
    "nabla": _simple_format("∇"),
    "aleph": _simple_format("ℵ"),
    "Re": _simple_format("ℜ"),
    "Im": _simple_format("ℑ"),
    "wp": _simple_format("℘"),
    "ell": _simple_format("ℓ"),
    "hbar": _simple_format("ℏ"),
    "angle": _simple_format("∠"),
    "perp": _simple_format("⊥"),
    "parallel": _simple_format("∥"),
    "bot": _simple_format("⊥"),
    "top": _simple_format("⊤"),
    "mid": _simple_format("∣"),
    "nmid": _simple_format("∤"),
    
    # Shapes and symbols
    "diamond": _simple_format("♦"),
    "Diamond": _simple_format("◊"),
    "square": _simple_format("□"),
    "blacksquare": _simple_format("■"),
    "triangle": _simple_format("△"),
    "triangleleft": _simple_format("◁"),
    "triangleright": _simple_format("▷"),
    "bigstar": _simple_format("★"),
    "clubsuit": _simple_format("♣"),
    "diamondsuit": _simple_format("♦"),
    "heartsuit": _simple_format("♥"),
    "spadesuit": _simple_format("♠"),
    
    # Dots and spacing
    "cdots": _simple_format("⋯"),
    "ldots": _simple_format("..."),
    "vdots": _simple_format("⋮"),
    "ddots": _simple_format("⋱"),
    "dots": _simple_format("..."),
    "quad": _simple_format("    "),
    "qquad": _simple_format("        "),
    "therefore": _simple_format("∴"),
    "because": _simple_format("∵"),
    
    # Text formatting
    "textit": _format_textit,
    "textbf": _format_textbf,
    "texttt": _format_text,
    "textrm": _format_text,
    "textsf": _format_text,
    "textsl": _format_text,
    "textsc": _format_text,
    "textnormal": _format_text,
    "text": _format_text,
    "mathrm": _format_mathrm,
    "mathbf": _format_mathbf,
    "mathit": _format_mathit,
    "mathcal": _format_mathcal,
    "mathbb": _format_mathbb,
    "mathscr": _format_mathcal,
    "mathfrak": _format_mathcal,
    "boldsymbol": _format_boldsymbol,
    "bm": _format_boldsymbol,
    
    # Special formatters with arguments
    "bar": _format_bar,
    "overline": _format_overline,
    "underline": _format_underline,
    "hat": _format_hat,
    "tilde": _format_tilde,
    "widetilde": _format_widetilde,
    "widehat": _format_widehat,
    "vec": _format_vec,
    "dot": _format_dot,
    "ddot": _format_ddot,
    "overbrace": _format_overbrace,
    "underbrace": _format_underbrace,
    "cancel": _format_cancel,
    "boxed": _format_boxed,
    
    # Binomial coefficients
    "binom": _format_binom,
    "dbinom": _format_binom,
    "tbinom": _format_binom,
    "choose": _format_binom,
    
    # Modular arithmetic
    "mod": _format_mod,
    "pmod": _format_pmod,
    "bmod": _format_mod,
    
    # Delimiters
    "left": _format_left,
    "right": _format_right,
    
    # Simple letters and symbols
    "d": _simple_format("d"),
    
    # Environment formatters
    "begin": _format_begin,
    "end": _format_end,
    
    # Additional mathematical operators and symbols
    "implies": _simple_format("⇒"),
    "impliedby": _simple_format("⇐"),
    "iff": _simple_format("⇔"),
    "prec": _simple_format("≺"),
    "succ": _simple_format("≻"),
    "preceq": _simple_format("⪯"),
    "preccurlyeq": _simple_format("≼"),
    "bowtie": _simple_format("⋈"),
    "asymp": _simple_format("≍"),
    "doteq": _simple_format("≐"),
    "doteqdot": _simple_format("≑"),
    "risingdotseq": _simple_format("≓"),
    "eqslant": _simple_format("⩦"),
    "coloneqq": _simple_format(":="),
    "divides": _simple_format("∣"),
    "lesssim": _simple_format("⪅"),
    "gtrsim": _simple_format("⪆"),
    "lessdot": _simple_format("⋖"),
    "gtreqless": _simple_format("⋛"),
    "leadsto": _simple_format("⇝"),
    "hookrightarrow": _simple_format("↪"),
    "rightharpoonup": _simple_format("⇀"),
    "rightleftarrows": _simple_format("⇄"),
    "leftrightarrows": _simple_format("⇆"),
    "longrightarrow": _simple_format("⟶"),
    "Longrightarrow": _simple_format("⟹"),
    "Longleftrightarrow": _simple_format("⟺"),
    "rightsquigarrow": _simple_format("⇝"),
    
    # Additional set operations
    "sqsubseteq": _simple_format("⊑"),
    "sqcup": _simple_format("⊔"),
    "sqcap": _simple_format("⊓"),
    "smallsetminus": _simple_format("∖"),
    "subsetneqq": _simple_format("⊊"),
    "supsetneqq": _simple_format("⊋"),
    "varsubsetneqq": _simple_format("⊊"),
    
    # Additional logic and relations
    "complement": _simple_format("∁"),
    "vartriangle": _simple_format("△"),
    "triangleleft": _simple_format("◁"),
    "triangleright": _simple_format("▷"),
    "triangledown": _simple_format("▽"),
    "blacktriangle": _simple_format("▲"),
    "bigtriangleup": _simple_format("△"),
    "triangleq": _simple_format("≜"),
    "Box": _simple_format("□"),
    "boxplus": _simple_format("⊞"),
    "boxminus": _simple_format("⊟"),
    "boxtimes": _simple_format("⊠"),
    "boxempty": _simple_format("□"),
    
    # Additional arrows and relations
    "circledast": _simple_format("⊛"),
    "bigcirc": _simple_format("◯"),
    "bigodot": _simple_format("⊙"),
    "bigotimes": _simple_format("⊗"),
    "bigoplus": _simple_format("⊕"),
    "bigcap": _simple_format("⋂"),
    "bigcup": _simple_format("⋃"),
    "bigsqcup": _simple_format("⊔"),
    
    # Size modifiers (empty in text representation)
    "big": _simple_format(""),
    "Big": _simple_format(""),
    "bigg": _simple_format(""),
    "Bigg": _simple_format(""),
    "bigl": _simple_format(""),
    "Bigl": _simple_format(""),
    "biggl": _simple_format(""),
    "Biggl": _simple_format(""),
    "bigr": _simple_format(""),
    "Bigr": _simple_format(""),
    "biggr": _simple_format(""),
    "Biggr": _simple_format(""),
    
    # Text size commands (empty in text representation)
    "tiny": _simple_format(""),
    "scriptsize": _simple_format(""),
    "footnotesize": _simple_format(""),
    "small": _simple_format(""),
    "large": _simple_format(""),
    "Large": _simple_format(""),
    "LARGE": _simple_format(""),
    "huge": _simple_format(""),
    "Huge": _simple_format(""),
    
    # Additional mathematical functions
    "cbrt": _format_cbrt,
    "arg": _simple_format("arg"),
    "arctg": _simple_format("arctan"),  # arctg is sometimes used for arctan
    
    # Additional symbols
    "flat": _simple_format("♭"),
    "sharp": _simple_format("♯"),
    "natural": _simple_format("♮"),
    "checkmark": _simple_format("✓"),
    "dagger": _simple_format("†"),
    "dag": _simple_format("†"),
    "backslash": _simple_format("\\"),
    "lbrace": _simple_format("{"),
    "rbrace": _simple_format("}"),
    "llbracket": _simple_format("⟦"),
    "rrbracket": _simple_format("⟧"),
    "ulcorner": _simple_format("⌜"),
    "sphericalangle": _simple_format("∢"),
    "measuredangle": _simple_format("∡"),
    "varangle": _simple_format("∢"),
    "Varangle": _simple_format("∢"),
    "angle": _simple_format("∠"),
    "prime": _simple_format("′"),
    "jmath": _simple_format("j"),
    
    # Special formatting commands
    "mbox": _format_mbox,
    "hbox": _format_hbox,
    "fbox": _format_fbox,
    "phantom": _format_phantom,
    "hphantom": _format_hphantom,
    "vphantom": _simple_format(""),
    "stackrel": _format_stackrel,
    "overset": _format_overset,
    "underset": _format_underset,
    "operatorname": _format_operatorname,
    "emph": _format_emph,
    
    # Arrows with content
    "xrightarrow": _format_xrightarrow,
    "overrightarrow": _format_overrightarrow,
    "overleftrightarrow": _format_overleftrightarrow,
    
    # Style switches (empty in text representation)
    "bf": _simple_format(""),
    "rm": _simple_format(""),
    "it": _simple_format(""),
    "em": _simple_format(""),
    "cal": _simple_format(""),
    
    # Document structure
    "section": _format_section,
    "subsection": _format_subsection,
    "title": _format_title,
    "author": _format_author,
    
    # Spacing commands (simplified)
    "hfill": _simple_format("    "),
    "hspace": _simple_format("  "),
    "vspace": _simple_format(""),
    "medskip": _simple_format("  "),
    "smallskip": _simple_format(" "),
    "allowbreak": _simple_format(""),
    "linebreak": _simple_format("\n"),
    "newline": _simple_format("\n"),
    "noindent": _simple_format(""),
    "centering": _simple_format(""),
    
    # Additional dots
    "dotsb": _simple_format("..."),
    "dotsc": _simple_format("..."),
    "dotsm": _simple_format("..."),
    "hdots": _simple_format("..."),
    
    # Mathematical relations
    "smile": _simple_format("⌣"),
    "frown": _simple_format("⌢"),
    "backsim": _simple_format("∽"),
    "mho": _simple_format("℧"),
    
    # Additional brackets and delimiters
    "lhd": _simple_format("⊲"),
    "middle": _simple_format("|"),
    "vert": _simple_format("|"),
    "Vert": _simple_format("‖"),
    
    # Layout commands (empty or minimal)
    "notag": _simple_format(""),
    "nonumber": _simple_format(""),
    "nolimits": _simple_format(""),
    "limits": _simple_format(""),
    "displaystyle": _simple_format(""),
    "mathrel": _simple_format(""),
    "mathbin": _simple_format(""),
    "mathop": _simple_format(""),
    "noalign": _simple_format(""),
    "arraystretch": _simple_format(""),
    "cline": _simple_format(""),
    "hline": _simple_format("---"),
    "rule": _simple_format("---"),
    "intertext": _simple_format(""),
    "rlap": _simple_format(""),
    "kern": _simple_format(""),
    "over": _simple_format("/"),
    "atop": _simple_format(""),
    "choose": _format_binom,
    
    # Text formatting
    "verb": _format_text,
    "textasciitilde": _simple_format("~"),
    "textdollar": _simple_format("$"),
    "textcircled": _format_text,
    "textcolor": _format_text,
    "textup": _format_text,
    
    # Special commands
    "url": _format_text,
    "label": _format_text,
    "eqref": _format_text,
    "tag": _format_text,
    "footnote": _format_text,
    "footnotetext": _format_text,
    "item": _simple_format("• "),
    "quote": _format_text,
    "center": _simple_format(""),
    "fcolorbox": _format_fbox,
    "color": _simple_format(""),
    "usepackage": _simple_format(""),
    "renewcommand": _simple_format(""),
    "multirow": _format_text,
    "multicolumn": _format_text,
    "shortstack": _format_text,
    "substack": _format_text,
    
    # Cancellation
    "cancel": _format_cancel,
    "xcancel": _format_cancel,
    
    # Simple letter variables (for single-letter commands)
    "a": _simple_format("a"),
    "b": _simple_format("b"),
    "c": _simple_format("c"),
    "e": _simple_format("e"),
    "f": _simple_format("f"),
    "g": _simple_format("g"),
    "I": _simple_format("I"),
    "k": _simple_format("k"),
    "l": _simple_format("l"),
    "n": _simple_format("n"),
    "O": _simple_format("O"),
    "p": _simple_format("p"),
    "P": _simple_format("P"),
    "q": _simple_format("q"),
    "Q": _simple_format("Q"),
    "R": _simple_format("R"),
    "S": _simple_format("S"),
    "T": _simple_format("T"),
    "u": _simple_format("u"),
    "v": _simple_format("v"),
    "w": _simple_format("w"),
    "x": _simple_format("x"),
    "y": _simple_format("y"),
    "z": _simple_format("z"),
    "Y": _simple_format("Y"),
    
    # Additional text/word commands and domain-specific terms
    "improve": _simple_format("improve"),
    "Define": _simple_format("Define"),
    "LaTeX": _simple_format("LaTeX"),
    "taking": _simple_format("taking"),
    "solve": _simple_format("solve"),
    "python": _simple_format("python"),
    "escaped": _simple_format("escaped"),
    "correctly": _simple_format("correctly"),
    "hence": _simple_format("hence"),
    "equally": _simple_format("equally"),
    "using": _simple_format("using"),
    "various": _simple_format("various"),
    "experimentation": _simple_format("experimentation"),
    "coordinate": _simple_format("coordinate"),
    "perpendicular": _simple_format("perpendicular"),
    "hypotenuse": _simple_format("hypotenuse"),
    "concise": _simple_format("concise"),
    "equal": _simple_format("equal"),
    "get": _simple_format("get"),
    "markup": _simple_format("markup"),
    "Assume": _simple_format("Assume"),
    "ensure": _simple_format("ensure"),
    "under": _simple_format("under"),
    "allow": _simple_format("allow"),
    "product": _simple_format("product"),
    "breaks": _simple_format("breaks"),
    "calculate": _simple_format("calculate"),
    "number": _simple_format("number"),
    "bold": _simple_format("bold"),
    "the": _simple_format("the"),
    "deviation": _simple_format("deviation"),
    "integers": _simple_format("integers"),
    "confirms": _simple_format("confirms"),
    "space": _simple_format("space"),
    "break": _simple_format("break"),
    "flight": _simple_format("flight"),
    "leading": _simple_format("leading"),
    "units": _simple_format("units"),
    "Prove": _simple_format("Prove"),
    "draw": _simple_format("draw"),
    "fill": _simple_format("fill"),
    "option": _simple_format("option"),
    "permit": _simple_format("permit"),
    "say": _simple_format("say"),
    
    # Astronomical and planetary terms
    "neptune": _simple_format("neptune"),
    "earth": _simple_format("earth"),
    "astrosun": _simple_format("astrosun"),
    "uranus": _simple_format("uranus"),
    "leftmoon": _simple_format("leftmoon"),
    
    # Geometric notation - triangles
    "triangleNCO": _simple_format("△NCO"),
    "triangleAMQ": _simple_format("△AMQ"),
    "triangleDBG": _simple_format("△DBG"),
    "triangleBMN": _simple_format("△BMN"),
    "triangleABC": _simple_format("△ABC"),
    "triangleAMO": _simple_format("△AMO"),
    "triangleOBH": _simple_format("△OBH"),
    "triangleCPN": _simple_format("△CPN"),
    "triangleNKM": _simple_format("△NKM"),
    "triangleMNO": _simple_format("△MNO"),
    "triangleBC": _simple_format("△BC"),
    
    # Geometric notation - angles
    "angleD": _simple_format("∠D"),
    "angleDP": _simple_format("∠DP"),
    "angleCDO": _simple_format("∠CDO"),
    "angleB": _simple_format("∠B"),
    "angleFME": _simple_format("∠FME"),
    "anglePDC": _simple_format("∠PDC"),
    "angleFBO": _simple_format("∠FBO"),
    "angleDBO": _simple_format("∠DBO"),
    "angleKMA": _simple_format("∠KMA"),
    "angleBAC": _simple_format("∠BAC"),
    "angleMFK": _simple_format("∠MFK"),
    "angleABC": _simple_format("∠ABC"),
    "angleA": _simple_format("∠A"),
    
    # Geometric notation - perpendicular lines
    "perpKN": _simple_format("⊥KN"),
    "perpDE": _simple_format("⊥DE"),
    "perpDF": _simple_format("⊥DF"),
    "perpBC": _simple_format("⊥BC"),
    "perpKM": _simple_format("⊥KM"),
    "perpMN": _simple_format("⊥MN"),
    
    # Mathematical symbols and operators
    "surd": _simple_format("√"),
    "digamma": _simple_format("ψ"),
    "gg": _simple_format("≫"),
    "ll": _simple_format("≪"),
    "not": _simple_format("¬"),
    "colon": _simple_format(":"),
    "degree": _simple_format("°"),
    "plus": _simple_format("+"),
    "minus": _simple_format("-"),
    "modulo": _simple_format("mod"),
    "ord": _simple_format("ord"),
    "binomial": _format_binom,
    "sqrtforthbound": _simple_format("√"),
    "acos": _simple_format("arccos"),
    "atan": _simple_format("arctan"),
    "cosx": _simple_format("cos(x)"),
    "cotx": _simple_format("cot(x)"),
    "mathdollar": _simple_format("$"),
    "mathsf": _format_mathcal,
    
    # Special symbols and shapes
    "Box": _simple_format("□"),
    "hexagon": _simple_format("⬡"),
    "pentagon": _simple_format("⬟"),
    "blacklozenge": _simple_format("⬧"),
    "eighthnote": _simple_format("♪"),
    "twonotes": _simple_format("♫"),
    "arc": _simple_format("⌒"),
    "overarc": _format_overline,
    "overparen": _format_overbrace,
    "underrightarrow": _format_overrightarrow,
    
    # Advanced formatting
    "breve": _format_hat,  # Similar to hat but different symbol
    "acute": _format_hat,  # Acute accent
    "xlongequal": _simple_format("="),
    "qquqquad": _simple_format("        "),  # Extra quad spacing
    "vdotswithin": _simple_format("⋮"),
    "cdotR": _simple_format("·R"),
    "odotO": _simple_format("⊙O"),
    "overr": _simple_format("r"),
    
    # Conditional and logical terms
    "equates": _simple_format("equals"),
    "equivalence": _simple_format("equivalence"),
    "superset": _simple_format("superset"),
    "Meets": _simple_format("meets"),
    "Is": _simple_format("is"),
    "Note": _simple_format("Note"),
    
    # Domain-specific abbreviations and terms
    "ICMC": _simple_format("ICMC"),
    "DEF": _simple_format("DEF"),
    "BAQ": _simple_format("BAQ"),
    "BCQ": _simple_format("BCQ"),
    "ACP": _simple_format("ACP"),
    "CDA": _simple_format("CDA"),
    "AF": _simple_format("AF"),
    "kom": _simple_format("kom"),
    "nic": _simple_format("nic"),
    "od": _simple_format("od"),
    "rom": _simple_format("rom"),
    "os": _simple_format("os"),
    "ld": _simple_format("ld"),
    "lf": _simple_format("lf"),
    "rf": _simple_format("rf"),
    "rret": _simple_format("rret"),
    "cm": _simple_format("cm"),
    "cd": _simple_format("cd"),
    "xy": _simple_format("xy"),
    "wx": _simple_format("wx"),
    "cx": _simple_format("cx"),
    "ab": _simple_format("ab"),
    "ad": _simple_format("ad"),
    "ang": _simple_format("ang"),
    "her": _simple_format("her"),
    "ce": _simple_format("ce"),
    "vare": _simple_format("vare"),
    "wto": _simple_format("wto"),
    "balnf": _simple_format("balnf"),
    "spos": _simple_format("spos"),
    "deltaN": _simple_format("δN"),
    
    # Mathematical context terms (prefixed with 'n')
    "nExpression": _simple_format("expression"),
    "nProbability": _simple_format("probability"),
    "nPart": _simple_format("part"),
    "nArea": _simple_format("area"),
    "nAdditional": _simple_format("additional"),
    "nNature": _simple_format("nature"),
    "nTriangle": _simple_format("triangle"),
    "nInitial": _simple_format("initial"),
    "nExact": _simple_format("exact"),
    "nless": _simple_format("less"),
    "nsubseteq": _simple_format("⊆"),
    "nCondition": _simple_format("condition"),
    "nRotation": _simple_format("rotation"),
    "nmidc": _simple_format("midc"),
    "negtive": _simple_format("negative"),  # Note: probably a typo for "negative"
    "nRightarrow": _simple_format("⇒"),
    "nPattern": _simple_format("pattern"),
    "nConstraint": _simple_format("constraint"),
    "nCircle": _simple_format("circle"),
    "nPoints": _simple_format("points"),
    "nProblem": _simple_format("problem"),
    "nImplications": _simple_format("implications"),
    "nInequality": _simple_format("inequality"),
    "nFor": _simple_format("for"),
    "nSolutions": _simple_format("solutions"),
    "nNatural": _simple_format("natural"),
    "nWhen": _simple_format("when"),
    "nExpected": _simple_format("expected"),
    "nSorted": _simple_format("sorted"),
    "nMaximum": _simple_format("maximum"),
    "nLet": _simple_format("let"),
    "nThe": _simple_format("the"),
    "nmidd": _simple_format("midd"),
    "nGeneral": _simple_format("general"),
    "nVolume": _simple_format("volume"),
    "nPrime": _simple_format("prime"),
    "nDiscriminant": _simple_format("discriminant"),
    "nVdash": _simple_format("⊢"),
    "nAfter": _simple_format("after"),
    "nIs": _simple_format("is"),
    "nparallel": _simple_format("∥"),
    "nleq": _simple_format("≤"),
    
    # Special terms and commands
    "Blocked": _simple_format("Blocked"),
    "tags": _simple_format("tags"),
    "votes": _simple_format("votes"),
    "row": _simple_format("row"),
    "romannumeral": _simple_format("romannumeral"),
    "interspersing": _simple_format("interspersing"),
    "precincts": _simple_format("precincts"),
    "order": _simple_format("order"),
    "height": _simple_format("height"),
    "leqslantk": _simple_format("≤"),
    "geqslantd": _simple_format("≥"),
    "box": _simple_format("box"),
    "operator": _simple_format("operator"),
    "aligned": _simple_format("aligned"),
    "lefteqn": _simple_format("lefteqn"),
    "tWarning": _simple_format("Warning"),
    "qed": _simple_format("∎"),  # QED symbol
    "epsfbox": _simple_format("epsfbox"),
    "Bbb": _format_mathbb,
    "Area": _simple_format("Area"),
    "Leftrightarrow": _simple_format("⇔"),
    "math": _simple_format("math"),
    
    # Lowercase versions of additional macro names
    "s": _simple_format("S"),
    "re": _simple_format("ℜ"),
    "prove": _simple_format("Prove"),
    "pr": _simple_format("Pr"),
    "cdotr": _simple_format("·R"),
    "o": _simple_format("O"),
    "i": _simple_format("I"),
    "longleftrightarrow": _simple_format("⟺"),
    "t": _simple_format("T"),
    "im": _simple_format("ℑ"),
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
