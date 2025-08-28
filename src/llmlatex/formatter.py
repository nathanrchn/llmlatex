from __future__ import annotations

import re
from typing import Dict, Callable, Optional, List

from .nodes import Node, TextNode, MacroNode, MultiNode, EnvironmentNode


BINARY_OPERATORS = {"+", "-", "*", "/", "=", "<", ">"}


def _clean_parentheses_spacing(text: str) -> str:
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return text


def _simple_format(text: str) -> Callable[[MacroNode, Formatter, bool], str]:
    def _simple_format_wrapper(
        node: MacroNode, formatter: Formatter, add_spaces: bool = False
    ) -> str:
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

    for op in BINARY_OPERATORS:
        if op in formatted_string:
            return True

    if " " in formatted_string.strip():
        return True

    if ")/" in formatted_string or ")(" in formatted_string:
        return True

    return False


def _format_sqrt(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    # Handles \sqrt[n]{...}
    if node.optional_arguments:
        root_index = node.optional_arguments[0]
        if node.arguments and node.arguments[0] is not None:
            formatted_arg = formatter._format_node(node.arguments[0], add_spaces)
            if _needs_parentheses(formatted_arg):
                return f"({formatted_arg})^(1/{root_index})"
            else:
                return f"{formatted_arg}^(1/{root_index})"
        else:
            return f"x^(1/{root_index})"  # Placeholder
    else:  # Handles \sqrt{...}
        if node.arguments and node.arguments[0] is not None:
            formatted_arg = formatter._format_node(node.arguments[0], add_spaces)
            if _needs_parentheses(formatted_arg):
                return f"√({formatted_arg})"
            else:
                return f"√{formatted_arg}"
        else:
            return "√"


def _format_frac(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and len(node.arguments) >= 2:
        numerator = formatter._format_node(node.arguments[0], add_spaces)
        denominator = formatter._format_node(node.arguments[1], add_spaces)

        if _needs_parentheses(numerator):
            numerator = f"({numerator})"
        if _needs_parentheses(denominator):
            denominator = f"({denominator})"

        result = f"{numerator}/{denominator}"
        if add_spaces:
            result = formatter._add_spaces_to_content(result)
        return result
    else:
        return "frac"


def _format_genfrac(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    # genfrac{ldelim}{rdelim}{thick}{style}{num}{den} -> format as frac
    if node.arguments and len(node.arguments) >= 6:
        numerator = formatter._format_node(node.arguments[4], add_spaces)
        denominator = formatter._format_node(node.arguments[5], add_spaces)
        ldelim = formatter._format_node(node.arguments[0], add_spaces)
        rdelim = formatter._format_node(node.arguments[1], add_spaces)

        if _needs_parentheses(numerator):
            numerator = f"({numerator})"
        if _needs_parentheses(denominator):
            denominator = f"({denominator})"

        result = f"{numerator}/{denominator}"
        if ldelim or rdelim:
            result = f"{ldelim}{result}{rdelim}"

        if add_spaces:
            result = formatter._add_spaces_to_content(result)
        return result
    else:
        return "genfrac"


def _format_font_style(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        return formatter._format_node(node.arguments[0], add_spaces)
    else:
        return ""


def _format_bold(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f"**{content}**"
    else:
        return ""


def _format_italic(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f"_{content}_"
    else:
        return ""


def _format_ceil_floor(
    node: MacroNode,
    formatter: Formatter,
    ldelim: str,
    rdelim: str,
    add_spaces: bool = False,
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f"{ldelim}{content}{rdelim}"
    else:
        return f"{ldelim}{rdelim}"


def _format_boxed(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f"[{content}]"
    else:
        return "[]"


def _format_accent(
    node: MacroNode, formatter: Formatter, accent: str, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f"{content}{accent}"
    else:
        return accent


def _format_cancel(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f"~~{content}~~"  # Strikethrough for cancel
    else:
        return ""


def _format_mod(node: MacroNode, formatter: Formatter, add_spaces: bool = False) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f" mod {content}"
    else:
        return " mod"


def _format_pmod(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return f" (mod {content})"
    else:
        return " (mod)"


def _format_binom(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and len(node.arguments) >= 2:
        n = formatter._format_node(node.arguments[0], add_spaces)
        k = formatter._format_node(node.arguments[1], add_spaces)
        return f"C({n},{k})"
    else:
        return ""


def _format_stackrel(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and len(node.arguments) >= 2:
        top = formatter._format_node(node.arguments[0], add_spaces)
        bottom = formatter._format_node(node.arguments[1], add_spaces)
        return f"{bottom}^{top}"
    else:
        return ""


def _format_overset(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and len(node.arguments) >= 2:
        top = formatter._format_node(node.arguments[0], add_spaces)
        bottom = formatter._format_node(node.arguments[1], add_spaces)
        return f"{bottom}^{top}"
    else:
        return ""


def _format_underset(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and len(node.arguments) >= 2:
        bottom = formatter._format_node(node.arguments[0], add_spaces)
        top = formatter._format_node(node.arguments[1], add_spaces)
        return f"{top}_{bottom}"
    else:
        return ""


def _format_phantom(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        content = formatter._format_node(node.arguments[0], add_spaces)
        return " " * len(content)
    else:
        return ""


def _format_left_right(
    node: MacroNode, formatter: Formatter, add_spaces: bool = False
) -> str:
    if node.arguments and node.arguments[0] is not None:
        delimiter = formatter._format_node(node.arguments[0], add_spaces)
        return delimiter
    else:
        return ""


def _format_environment(env_name: str, content: str) -> str:
    cleaned_content = re.sub(r"\\\\\s*$", "", content.strip())
    cleaned_content = re.sub(
        r"\\\\\s*(?=\s*$)", "", cleaned_content, flags=re.MULTILINE
    )

    cleaned_content = cleaned_content.replace("\\\\", "\n")

    if env_name in {"matrix", "pmatrix", "bmatrix", "vmatrix", "Vmatrix", "array"}:
        cleaned_content = re.sub(r"\s*&\s*", " ", cleaned_content)
    elif env_name in {"align", "align*", "aligned"}:
        cleaned_content = re.sub(r"\s*&\s*", " ", cleaned_content)
    elif env_name in {"cases"}:
        cleaned_content = re.sub(r"\s*&\s*", " if ", cleaned_content)
    else:
        cleaned_content = re.sub(r"\s*&\s*", " ", cleaned_content)

    cleaned_content = re.sub(r" +", " ", cleaned_content).strip()

    if env_name == "pmatrix":
        return f"({cleaned_content})"
    elif env_name == "bmatrix":
        return f"[{cleaned_content}]"
    elif env_name == "vmatrix":
        return f"|{cleaned_content}|"
    elif env_name == "Vmatrix":
        return f"‖{cleaned_content}‖"
    elif env_name == "cases":
        return f"{{{cleaned_content}}}"
    else:
        return cleaned_content


DEFAULT_FORMATTERS = {
    # Basic formatters
    "sqrt": _format_sqrt,
    "frac": _format_frac,
    "dfrac": _format_frac,
    "tfrac": _format_frac,
    "cfrac": _format_frac,
    "genfrac": _format_genfrac,
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
    "varkappa": _simple_format("ϰ"),
    "lambda": _simple_format("λ"),
    "mu": _simple_format("μ"),
    "nu": _simple_format("ν"),
    "xi": _simple_format("ξ"),
    "pi": _simple_format("π"),
    "varpi": _simple_format("ϖ"),
    "rho": _simple_format("ρ"),
    "varrho": _simple_format("ϱ"),
    "sigma": _simple_format("σ"),
    "varsigma": _simple_format("ς"),
    "tau": _simple_format("τ"),
    "upsilon": _simple_format("υ"),
    "phi": _simple_format("φ"),
    "varphi": _simple_format("φ"),
    "chi": _simple_format("χ"),
    "psi": _simple_format("ψ"),
    "omega": _simple_format("ω"),
    # Greek letters (uppercase)
    "Gamma": _simple_format("Γ"),
    "varGamma": _simple_format("Γ"),
    "Delta": _simple_format("Δ"),
    "varDelta": _simple_format("Δ"),
    "Theta": _simple_format("Θ"),
    "Lambda": _simple_format("Λ"),
    "Xi": _simple_format("Ξ"),
    "Pi": _simple_format("Π"),
    "Sigma": _simple_format("Σ"),
    "Upsilon": _simple_format("Υ"),
    "Phi": _simple_format("Φ"),
    "Psi": _simple_format("Ψ"),
    "Omega": _simple_format("Ω"),
    "Beta": _simple_format("B"),  # No standard capital Beta symbol in math
    # Comparison operators
    "lt": _simple_format("<"),
    "gt": _simple_format(">"),
    "le": _simple_format("≤"),
    "leq": _simple_format("≤"),
    "leqq": _simple_format("≦"),
    "leqslant": _simple_format("⩽"),
    "nle": _simple_format("≰"),
    "nleq": _simple_format("≰"),
    "nleqslant": _simple_format("≰"),
    "ge": _simple_format("≥"),
    "geq": _simple_format("≥"),
    "geqq": _simple_format("≧"),
    "geqslant": _simple_format("⩾"),
    "nge": _simple_format("≱"),
    "ngeq": _simple_format("≱"),
    "ngeqslant": _simple_format("≱"),
    "eq": _simple_format("="),
    "neq": _simple_format("≠"),
    "ne": _simple_format("≠"),
    "equiv": _simple_format("≡"),
    "ncong": _simple_format("≇"),
    "approx": _simple_format("≈"),
    "approxeq": _simple_format("≈"),
    "sim": _simple_format("∼"),
    "nsim": _simple_format("≁"),
    "simeq": _simple_format("≃"),
    "cong": _simple_format("≅"),
    "propto": _simple_format("∝"),
    "ll": _simple_format("≪"),
    "gg": _simple_format("≫"),
    "lll": _simple_format("⋘"),
    "ggg": _simple_format("⋙"),
    "prec": _simple_format("≺"),
    "nprec": _simple_format("⊀"),
    "succ": _simple_format("≻"),
    "preceq": _simple_format("≼"),
    "succeq": _simple_format("≽"),
    "preccurlyeq": _simple_format("≼"),
    "succcurlyeq": _simple_format("≽"),
    "precsim": _simple_format("≾"),
    "gtrsim": _simple_format("≳"),
    "lessapprox": _simple_format("≲"),
    "gtrapprox": _simple_format("≳"),
    "lessdot": _simple_format("⋖"),
    "gtrdot": _simple_format("⋗"),
    "lessgtr": _simple_format("≶"),
    "gtrless": _simple_format("≷"),
    "lesseqgtr": _simple_format("⋚"),
    "gtreqless": _simple_format("⋛"),
    "risingdotseq": _simple_format("≓"),
    "fallingdotseq": _simple_format("≒"),
    "coloneqq": _simple_format(":="),
    "doteq": _simple_format("≐"),
    "doteqdot": _simple_format("≑"),
    "triangleq": _simple_format("≜"),
    "asymp": _simple_format("≍"),
    "bowtie": _simple_format("⋈"),
    # Set theory
    "in": _simple_format("∈"),
    "notin": _simple_format("∉"),
    "ni": _simple_format("∋"),
    "subset": _simple_format("⊂"),
    "supset": _simple_format("⊃"),
    "subseteq": _simple_format("⊆"),
    "supseteq": _simple_format("⊇"),
    "nsubset": _simple_format("⊄"),
    "nsubseteq": _simple_format("⊈"),
    "nsupseteq": _simple_format("⊉"),
    "subsetneq": _simple_format("⊊"),
    "supsetneq": _simple_format("⊋"),
    "subsetneqq": _simple_format("⫋"),
    "supsetneqq": _simple_format("⫌"),
    "varsubsetneqq": _simple_format("⫋"),
    "sqsubset": _simple_format("⊏"),
    "sqsupset": _simple_format("⊐"),
    "sqsubseteq": _simple_format("⊑"),
    "cap": _simple_format("∩"),
    "cup": _simple_format("∪"),
    "setminus": _simple_format("∖"),
    "smallsetminus": _simple_format("∖"),
    "emptyset": _simple_format("∅"),
    "varnothing": _simple_format("∅"),
    "complement": _simple_format("∁"),
    "uplus": _simple_format("⊎"),
    "sqcup": _simple_format("⊔"),
    "amalg": _simple_format("⨿"),
    "coprod": _simple_format("∐"),
    "bigcap": _simple_format("⋂"),
    "bigcup": _simple_format("⋃"),
    "bigsqcup": _simple_format("⨆"),
    # Logic
    "forall": _simple_format("∀"),
    "exists": _simple_format("∃"),
    "nexists": _simple_format("∄"),
    "neg": _simple_format("¬"),
    "lnot": _simple_format("¬"),
    "not": _simple_format("¬"),
    "land": _simple_format("∧"),
    "wedge": _simple_format("∧"),
    "curlywedge": _simple_format("⋏"),
    "lor": _simple_format("∨"),
    "vee": _simple_format("∨"),
    "curlyvee": _simple_format("⋎"),
    "bigvee": _simple_format("⋁"),
    "bigwedge": _simple_format("⋀"),
    "implies": _simple_format("⇒"),
    "impliedby": _simple_format("⇐"),
    "iff": _simple_format("⇔"),
    "therefore": _simple_format("∴"),
    "because": _simple_format("∵"),
    "top": _simple_format("⊤"),
    "bot": _simple_format("⊥"),
    "vdash": _simple_format("⊢"),
    "nvdash": _simple_format("⊬"),
    "nvDash": _simple_format("⊭"),
    "nVdash": _simple_format("⊮"),
    "models": _simple_format("⊨"),
    "vDash": _simple_format("⊨"),
    "Vdash": _simple_format("⊩"),
    # Arrows
    "to": _simple_format("→"),
    "gets": _simple_format("←"),
    "leftarrow": _simple_format("←"),
    "rightarrow": _simple_format("→"),
    "leftrightarrow": _simple_format("↔"),
    "nleftarrow": _simple_format("↚"),
    "nrightarrow": _simple_format("↛"),
    "Leftarrow": _simple_format("⇐"),
    "Rightarrow": _simple_format("⇒"),
    "nLeftarrow": _simple_format("⇍"),
    "nRightarrow": _simple_format("⇏"),
    "Leftrightarrow": _simple_format("⇔"),
    "updownarrow": _simple_format("↕"),
    "Uparrow": _simple_format("⇑"),
    "Downarrow": _simple_format("⇓"),
    "uparrow": _simple_format("↑"),
    "downarrow": _simple_format("↓"),
    "nearrow": _simple_format("↗"),
    "searrow": _simple_format("↘"),
    "swarrow": _simple_format("↙"),
    "nwarrow": _simple_format("↖"),
    "mapsto": _simple_format("↦"),
    "longmapsto": _simple_format("⟼"),
    "hookleftarrow": _simple_format("↩"),
    "hookrightarrow": _simple_format("↪"),
    "longleftarrow": _simple_format("⟵"),
    "longrightarrow": _simple_format("⟶"),
    "longleftrightarrow": _simple_format("⟷"),
    "Longleftarrow": _simple_format("⟸"),
    "Longrightarrow": _simple_format("⟹"),
    "Longleftrightarrow": _simple_format("⟺"),
    "rightharpoonup": _simple_format("⇀"),
    "upharpoonright": _simple_format("↾"),
    "downharpoonleft": _simple_format("⇃"),
    "rightleftarrows": _simple_format("⇄"),
    "leftrightharpoons": _simple_format("⇋"),
    "rightleftharpoons": _simple_format("⇌"),
    "leftrightarrows": _simple_format("⇆"),
    "twoheadrightarrow": _simple_format("↠"),
    "looparrowright": _simple_format("↬"),
    "circlearrowleft": _simple_format("↺"),
    "curvearrowright": _simple_format("↱"),
    "rightsquigarrow": _simple_format("⇝"),
    "multimap": _simple_format("⊸"),
    "leadsto": _simple_format("⤳"),
    "dashrightarrow": _simple_format("⇢"),
    "xleftarrow": lambda n, f, a=False: _format_accent(n, f, "←", a),
    "xrightarrow": lambda n, f, a=False: _format_accent(n, f, "→", a),
    "xlongequal": lambda n, f, a=False: _format_accent(n, f, "=", a),
    # Binary operators
    "pm": _simple_format("±"),
    "mp": _simple_format("∓"),
    "times": _simple_format("×"),
    "div": _simple_format("÷"),
    "cdot": _simple_format("·"),
    "cdotp": _simple_format("·"),
    "centerdot": _simple_format("·"),
    "bullet": _simple_format("•"),
    "circ": _simple_format("∘"),
    "ast": _simple_format("∗"),
    "star": _simple_format("⋆"),
    "oplus": _simple_format("⊕"),
    "ominus": _simple_format("⊖"),
    "otimes": _simple_format("⊗"),
    "oslash": _simple_format("⊘"),
    "odot": _simple_format("⊙"),
    "dagger": _simple_format("†"),
    "ddagger": _simple_format("‡"),
    "wr": _simple_format("≀"),
    "intercal": _simple_format("⊺"),
    "plus": _simple_format("+"),
    "minus": _simple_format("-"),
    "slash": _simple_format("/"),
    # Large operators
    "sum": _simple_format("∑"),
    "prod": _simple_format("∏"),
    "int": _simple_format("∫"),
    "intop": _simple_format("∫"),
    "oint": _simple_format("∮"),
    "oiint": _simple_format("∯"),
    "iint": _simple_format("∬"),
    "iiint": _simple_format("∭"),
    "iiiint": _simple_format("⨌"),
    "idotsint": _simple_format("∫⋯∫"),
    "fint": _simple_format("⨍"),
    "bigoplus": _simple_format("⨁"),
    "bigotimes": _simple_format("⨂"),
    "bigodot": _simple_format("⨀"),
    "biguplus": _simple_format("⨄"),
    # Delimiters & Brackets
    "lfloor": _simple_format("⌊"),
    "rfloor": _simple_format("⌋"),
    "lceil": lambda n, f, a=False: _format_ceil_floor(n, f, "⌈", "⌉", a),
    "rceil": lambda n, f, a=False: _format_ceil_floor(n, f, "⌈", "⌉", a),
    "langle": _simple_format("⟨"),
    "rangle": _simple_format("⟩"),
    "lvert": _simple_format("|"),
    "rvert": _simple_format("|"),
    "lVert": _simple_format("‖"),
    "rVert": _simple_format("‖"),
    "vert": _simple_format("|"),
    "Vert": _simple_format("‖"),
    "left": _format_left_right,
    "right": _format_left_right,
    "brace": _simple_format("{...}"),
    "brack": _simple_format("[...]"),
    "lbrace": _simple_format("{"),
    "rbrace": _simple_format("}"),
    "lbrack": _simple_format("["),
    "rbrack": _simple_format("]"),
    "llbracket": _simple_format("⟦"),
    "rrbracket": _simple_format("⟧"),
    "ulcorner": _simple_format("⌜"),
    "urcorner": _simple_format("⌝"),
    "llcorner": _simple_format("⌞"),
    "lrcorner": _simple_format("⌟"),
    "middle": _simple_format("|"),
    # Math functions
    "sin": _simple_format("sin"),
    "cos": _simple_format("cos"),
    "tan": _simple_format("tan"),
    "cot": _simple_format("cot"),
    "sec": _simple_format("sec"),
    "csc": _simple_format("csc"),
    "arcsin": _simple_format("arcsin"),
    "arccos": _simple_format("arccos"),
    "arctan": _simple_format("arctan"),
    "atan": _simple_format("arctan"),
    "sinh": _simple_format("sinh"),
    "cosh": _simple_format("cosh"),
    "tanh": _simple_format("tanh"),
    "coth": _simple_format("coth"),
    "log": _simple_format("log"),
    "ln": _simple_format("ln"),
    "lg": _simple_format("lg"),
    "exp": _simple_format("exp"),
    "min": _simple_format("min"),
    "max": _simple_format("max"),
    "sup": _simple_format("sup"),
    "inf": _simple_format("inf"),
    "lim": _simple_format("lim"),
    "limsup": _simple_format("limsup"),
    "varlimsup": _simple_format("limsup"),
    "liminf": _simple_format("liminf"),
    "varliminf": _simple_format("liminf"),
    "gcd": _simple_format("gcd"),
    "lcm": _simple_format("lcm"),
    "det": _simple_format("det"),
    "dim": _simple_format("dim"),
    "ker": _simple_format("ker"),
    "deg": _simple_format("deg"),
    "hom": _simple_format("hom"),
    "arg": _simple_format("arg"),
    "Pr": _simple_format("Pr"),
    "mod": _format_mod,
    "pmod": _format_pmod,
    "bmod": _format_mod,
    # Special symbols
    "infty": _simple_format("∞"),
    "partial": _simple_format("∂"),
    "nabla": _simple_format("∇"),
    "aleph": _simple_format("ℵ"),
    "beth": _simple_format("ℶ"),
    "Re": _simple_format("ℜ"),
    "Im": _simple_format("ℑ"),
    "im": _simple_format("im"),
    "wp": _simple_format("℘"),
    "ell": _simple_format("ℓ"),
    "hbar": _simple_format("ℏ"),
    "angle": _simple_format("∠"),
    "measuredangle": _simple_format("∡"),
    "sphericalangle": _simple_format("∢"),
    "varangle": _simple_format("∢"),
    "perp": _simple_format("⊥"),
    "Perp": _simple_format("⊥"),
    "parallel": _simple_format("∥"),
    "nparallel": _simple_format("∦"),
    "mid": _simple_format("|"),
    "nmid": _simple_format("∤"),
    "divides": _simple_format("|"),
    "Join": _simple_format("⋈"),
    "mho": _simple_format("℧"),
    "prime": _simple_format("'"),
    "backsim": _simple_format("∽"),
    "surd": _simple_format("√"),
    "Box": _simple_format("□"),
    "boxdot": _simple_format("⊡"),
    "boxplus": _simple_format("⊞"),
    "boxminus": _simple_format("⊟"),
    "boxtimes": _simple_format("⊠"),
    "boxbox": _simple_format("⧈"),
    # Shapes
    "diamond": _simple_format("⋄"),
    "Diamond": _simple_format("◊"),
    "square": _simple_format("□"),
    "blacksquare": _simple_format("■"),
    "triangle": _simple_format("△"),
    "bigtriangleup": _simple_format("△"),
    "bigtriangledown": _simple_format("▽"),
    "triangleleft": _simple_format("◁"),
    "triangleright": _simple_format("▷"),
    "vartriangle": _simple_format("△"),
    "vartriangleleft": _simple_format("⊲"),
    "trianglelefteq": _simple_format("⊴"),
    "trianglerighteq": _simple_format("⊵"),
    "ntriangleleft": _simple_format("⋪"),
    "ntrianglelefteq": _simple_format("⋬"),
    "unlhd": _simple_format("⊴"),
    "rhd": _simple_format("▷"),
    "lhd": _simple_format("◁"),
    "bigstar": _simple_format("★"),
    "clubsuit": _simple_format("♣"),
    "diamondsuit": _simple_format("♦"),
    "heartsuit": _simple_format("♡"),
    "spadesuit": _simple_format("♠"),
    "blacklozenge": _simple_format("⧫"),
    "astrosun": _simple_format("☉"),
    "smiley": _simple_format("☺"),
    "hexagon": _simple_format("⬡"),
    "pentagon": _simple_format("⬟"),
    "checkmark": _simple_format("✓"),
    "circledast": _simple_format("⊛"),
    "bigcirc": _simple_format("○"),
    "triangledown": _simple_format("▽"),
    "Square": _simple_format("□"),
    "flat": _simple_format("♭"),
    "natural": _simple_format("♮"),
    "sharp": _simple_format("♯"),
    "smile": _simple_format("⌣"),
    "frown": _simple_format("⌢"),
    # Dots and spacing
    "cdots": _simple_format("⋯"),
    "ldots": _simple_format("…"),
    "vdots": _simple_format("⋮"),
    "ddots": _simple_format("⋱"),
    "iddots": _simple_format("⋰"),
    "dots": _simple_format("…"),
    "hdots": _simple_format("…"),
    "dotsb": _simple_format("⋯"),
    "dotsc": _simple_format("…"),
    "dotsm": _simple_format("⋯"),
    "colon": _simple_format(":"),
    "quad": _simple_format("  "),
    "qquad": _simple_format("    "),
    "thinspace": _simple_format(" "),
    "enspace": _simple_format("  "),
    "enskip": _simple_format("  "),
    "hspace": _simple_format(" "),
    "hskip": _simple_format(" "),
    "kern": _simple_format(""),
    "indent": _simple_format("    "),
    "hfill": _simple_format(" "),
    "space": _simple_format(" "),
    "smallskip": _simple_format(" "),
    "smallskipamount": _simple_format(" "),
    "par": _simple_format("\n"),
    # Accents & Decorations
    "hat": lambda n, f, a=False: _format_accent(n, f, "̂", a),
    "widehat": lambda n, f, a=False: _format_accent(n, f, "̂", a),
    "tilde": lambda n, f, a=False: _format_accent(n, f, "̃", a),
    "widetilde": lambda n, f, a=False: _format_accent(n, f, "̃", a),
    "bar": lambda n, f, a=False: _format_accent(n, f, "̄", a),
    "overline": lambda n, f, a=False: _format_accent(n, f, "̄", a),
    "vec": lambda n, f, a=False: _format_accent(n, f, "⃗", a),
    "overrightarrow": lambda n, f, a=False: _format_accent(n, f, "⃗", a),
    "overleftarrow": lambda n, f, a=False: _format_accent(n, f, "⃖", a),
    "overleftrightarrow": lambda n, f, a=False: _format_accent(n, f, "↔", a),
    "dot": lambda n, f, a=False: _format_accent(n, f, "̇", a),
    "ddot": lambda n, f, a=False: _format_accent(n, f, "̈", a),
    "dddot": lambda n, f, a=False: _format_accent(n, f, "⃛", a),
    "ddddot": lambda n, f, a=False: _format_accent(n, f, "⃜", a),
    "check": lambda n, f, a=False: _format_accent(n, f, "̌", a),
    "grave": lambda n, f, a=False: _format_accent(n, f, "̀", a),
    "breve": lambda n, f, a=False: _format_accent(n, f, "̆", a),
    "mathring": lambda n, f, a=False: _format_accent(n, f, "̊", a),
    "underline": _format_italic,  # Simple fallback
    "underbracket": _format_italic,
    "overbrace": lambda n, f, a=False: _format_accent(n, f, "⏞", a),
    "underbrace": lambda n, f, a=False: _format_accent(n, f, "⏟", a),
    "overarc": lambda n, f, a=False: _format_accent(n, f, "⌒", a),
    "overparen": lambda n, f, a=False: _format_accent(n, f, "⏠", a),
    "cancel": _format_cancel,
    "boxed": _format_boxed,
    "fbox": _format_boxed,
    "framebox": _format_boxed,
    # Binomial coefficients
    "binom": _format_binom,
    "dbinom": _format_binom,
    "tbinom": _format_binom,
    "choose": _format_binom,
    # Text & Font styles
    "textit": _format_italic,
    "textbf": _format_bold,
    "textsl": _format_italic,
    "emph": _format_italic,
    "mathbf": _format_bold,
    "boldsymbol": _format_bold,
    "pmb": _format_bold,
    "boldmath": _simple_format(""),  # Style switch
    "texttt": _format_font_style,
    "textrm": _format_font_style,
    "textsf": _format_font_style,
    "textsc": _format_font_style,
    "textup": _format_font_style,
    "textnormal": _format_font_style,
    "text": _format_font_style,
    "mathrm": _format_font_style,
    "mathit": _format_italic,
    "mathcal": _format_font_style,
    "mathbb": _format_font_style,
    "mathbbm": _format_font_style,
    "Bbb": _format_font_style,
    "Bbbk": _format_font_style,
    "mathscr": _format_font_style,
    "mathfrak": _format_font_style,
    "mathsf": _format_font_style,
    "mathtt": _format_font_style,
    "bf": _simple_format(""),
    "rm": _simple_format(""),
    "tt": _simple_format(""),
    "em": _simple_format(""),
    "cal": _simple_format(""),
    "scr": _simple_format(""),
    "frak": _simple_format(""),
    "textsuperscript": lambda n, f, a=False: f"^{_format_font_style(n,f,a)}",
    "textsubscript": lambda n, f, a=False: f"_{_format_font_style(n,f,a)}",
    "textcircled": _format_font_style,
    "LaTeX": _simple_format("LaTeX"),
    "normalsize": _simple_format(""),
    # Structural & Layout
    "begingroup": _simple_format(""),
    "endgroup": _simple_format(""),
    "endarray": _simple_format(""),
    "item": _simple_format("• "),
    "title": lambda n, f, a=False: f"Title: {_format_font_style(n, f, a)}\n",
    "author": lambda n, f, a=False: f"Author: {_format_font_style(n, f, a)}\n",
    "caption": _format_font_style,
    "label": _simple_format(""),
    "ref": _format_font_style,
    "tag": _simple_format(""),
    "eqno": _simple_format(""),
    "footnotetext": _format_font_style,
    "parbox": _format_font_style,
    "makebox": _format_font_style,
    "mbox": _format_font_style,
    "hbox": _format_font_style,
    "rlap": _format_font_style,
    "llap": _format_font_style,
    "phantom": _format_phantom,
    "hphantom": _format_phantom,
    "vphantom": _simple_format(""),
    "mathstrut": _simple_format(""),
    "stackrel": _format_stackrel,
    "overset": _format_overset,
    "underset": _format_underset,
    "operatorname": _format_font_style,
    "atop": _simple_format("/"),
    "over": _simple_format("/"),
    "root": _format_sqrt,
    "uproot": _simple_format(""),
    "leftroot": _simple_format(""),
    "allowbreak": _simple_format(""),
    "break": _simple_format("\n"),
    "linebreak": _simple_format("\n"),
    "newline": _simple_format("\n"),
    "cr": _simple_format("\n"),
    "noindent": _simple_format(""),
    "notag": _simple_format(""),
    "nonumber": _simple_format(""),
    "nolimits": _simple_format(""),
    "limits": _simple_format(""),
    "displaystyle": _simple_format(""),
    "textstyle": _simple_format(""),
    "scriptstyle": _simple_format(""),
    "mathrel": _simple_format(""),
    "mathbin": _simple_format(""),
    "mathop": _simple_format(""),
    "noalign": _simple_format(""),
    "arraystretch": _simple_format(""),
    "tabcolsep": _simple_format(""),
    "cline": _simple_format("\n---\n"),
    "hline": _simple_format("\n---\n"),
    "hdashline": _simple_format("\n---\n"),
    "rule": _simple_format("---"),
    "multicolumn": lambda n, f, a=False: f"{_format_font_style(n, f, a)}",
    "substack": _format_font_style,
    "pmatrix": _format_font_style,
    "align": _format_font_style,
    "lefteqn": _format_font_style,
    "put": _simple_format(""),
    "multiput": _simple_format(""),
    # System/Meta commands
    "usepackage": _simple_format(""),
    "newcommand": _simple_format(""),
    "renewcommand": _simple_format(""),
    "setlength": _simple_format(""),
    "def": _simple_format(""),
    "let": _simple_format(""),
    "require": _simple_format(""),
    "ensuremath": _format_font_style,
    "color": lambda n, f, a=False: _format_font_style(
        node=MacroNode(name="", arguments=n.arguments[1:]), formatter=f, add_spaces=a
    ),
    "romannumeral": _format_font_style,
    "verb": _format_font_style,
    # Special Characters & Symbols
    "\\": _simple_format("\\"),
    "backslash": _simple_format("\\"),
    "$": _simple_format("$"),
    "textdollar": _simple_format("$"),
    "mathdollar": _simple_format("$"),
    "%": _simple_format("%"),
    "&": _simple_format("&"),
    "#": _simple_format("#"),
    "_": _simple_format("_"),
    "{": _simple_format("{"),
    "}": _simple_format("}"),
    "~": _simple_format("~"),
    "^": _simple_format("^"),
    "|": _simple_format("|"),
    "dag": _simple_format("†"),
    "ddag": _simple_format("‡"),
    "S": _simple_format("§"),
    "P": _simple_format("¶"),
    "copyright": _simple_format("©"),
    "textcopyright": _simple_format("©"),
    "circledR": _simple_format("®"),
    "pounds": _simple_format("£"),
    "cent": _simple_format("¢"),
    "textasciitilde": _simple_format("~"),
    "degree": _simple_format("°"),
    "digamma": _simple_format("ϝ"),
    "imath": _simple_format("ı"),
    "jmath": _simple_format("ȷ"),
    # Single letter commands (treated as variables)
    "a": _simple_format("a"),
    "A": _simple_format("A"),
    "b": _simple_format("b"),
    "B": _simple_format("B"),
    "c": _simple_format("c"),
    "C": _simple_format("C"),
    "d": _simple_format("d"),
    "D": _simple_format("D"),
    "e": _simple_format("e"),
    "E": _simple_format("E"),
    "f": _simple_format("f"),
    "G": _simple_format("G"),
    "h": _simple_format("h"),
    "H": _simple_format("H"),
    "i": _simple_format("i"),
    "I": _simple_format("I"),
    "J": _simple_format("J"),
    "k": _simple_format("k"),
    "l": _simple_format("l"),
    "L": _simple_format("L"),
    "m": _simple_format("m"),
    "M": _simple_format("M"),
    "O": _simple_format("O"),
    "r": _simple_format("r"),
    "t": _simple_format("t"),
    "T": _simple_format("T"),
    "u": _simple_format("u"),
    "U": _simple_format("U"),
    "v": _simple_format("v"),
    "x": _simple_format("x"),
    "z": _simple_format("z"),
    "Z": _simple_format("Z"),
    # Miscellaneous/Unsorted
    "sp": _simple_format(" "),
    "ac": _simple_format("∿"),
    "vari": _simple_format(""),
    "AA": _simple_format("Å"),
    "do": _simple_format(""),
    "of": _simple_format(" of "),
    "or": _simple_format(" or "),
    "fl": _simple_format("fl"),
    "Rrightarrow": _simple_format("↠"),
    "varprojlim": _simple_format("lim"),
    "varinjlim": _simple_format("lim"),
    "ds": _format_font_style,
    "od": _simple_format(""),
    "er": _simple_format(""),
    "In": _simple_format("in"),
    "SO": _simple_format("SO"),
    "parr": _simple_format("⅋"),
    "dashv": _simple_format("⊣"),
    "equal": _simple_format("="),
    "height": _simple_format(""),
    "long": _simple_format(""),
    "mark": _simple_format(""),
    "o": _simple_format("o"),
    "time": _simple_format("×"),
    "th": _simple_format("th"),
    # Additional requested commands
    "supseteqq": _simple_format("⫌"),
    "ngtr": _simple_format("≯"),
    "nless": _simple_format("≮"),
    "circle": _simple_format("○"),
    "math": _format_font_style,
    "bigm": _simple_format("|"),
    "line": _simple_format("—"),
    "ltimes": _simple_format("⋉"),
    "na": _simple_format(""),
    "box": _simple_format("□"),
    "boxempty": _simple_format("☐"),
    "textbackslash": _simple_format("\\"),
    "rightrightarrows": _simple_format("⇉"),
    "biggm": _simple_format("‖"),
    "lesssim": _simple_format("≲"),
    "vspace": _simple_format(" "),
    "restriction": _simple_format("↾"),
    "rtimes": _simple_format("⋊"),
    # Handle backslash-space command (\ )
    " ": _simple_format(" "),
}


SPECIAL_SUPERSCRIPT_FORMAT = {
    "∘": "°",
    "′": "′",
}


class Formatter:
    def __init__(
        self,
        formatters: Optional[Dict[str, Callable[[MacroNode, Formatter], str]]] = None,
    ):
        self.formatters = {**DEFAULT_FORMATTERS, **(formatters or {})}

    def _skip_empty_text_node(
        self, nodes: List[Node], node_type: str = ""
    ) -> List[Node]:
        return [
            node
            for node in nodes
            if node is not None
            and not (
                (isinstance(node, TextNode) and not node.content)
                or (
                    node_type == "math"
                    and isinstance(node, MacroNode)
                    and node.name == " "
                )
            )
        ]

    def _add_spaces_to_content(self, content: str) -> str:
        i = 0
        result = []

        no_space_before = {"(", "[", "{"}
        no_space_after = {")", "]", "}"}

        while i < len(content):
            char = content[i]

            if char in BINARY_OPERATORS:
                if result and result[-1] != " " and result[-1] not in no_space_before:
                    result.append(" ")

                result.append(char)

                if (
                    i + 1 < len(content)
                    and content[i + 1] != " "
                    and content[i + 1] not in no_space_after
                ):
                    result.append(" ")

            elif char in no_space_before:
                if result and result[-1] != " " and result[-1] not in BINARY_OPERATORS:
                    if result[-1].isalnum():
                        result.append(" ")
                result.append(char)

            elif char in no_space_after:
                result.append(char)
                if (
                    i + 1 < len(content)
                    and content[i + 1] not in BINARY_OPERATORS
                    and content[i + 1] != " "
                    and content[i + 1] not in no_space_after
                ):
                    if content[i + 1].isalnum():
                        result.append(" ")

            elif char == " ":
                if not result or result[-1] != " ":
                    result.append(char)

            else:
                result.append(char)

            i += 1

        return "".join(result)

    def _format_text_node(self, node: TextNode, add_spaces: bool = False) -> str:
        output = node.content
        if add_spaces:
            output = self._add_spaces_to_content(output)
        if node.subscript:
            subscript = self._format_node(node.subscript, add_spaces)
            output += f"_{subscript}"
        if node.superscript:
            superscript = self._format_node(node.superscript, add_spaces)
            if superscript in SPECIAL_SUPERSCRIPT_FORMAT:
                output += SPECIAL_SUPERSCRIPT_FORMAT[superscript]
            else:
                output += "^" + superscript
        return output

    def _format_macro_node(self, node: MacroNode, add_spaces: bool = False) -> str:
        if node.name in self.formatters:
            return self.formatters[node.name](node, self, add_spaces)
        else:
            raise ValueError(f"No formatter found for \\{node.name}")

    def _format_multi_node(self, node: MultiNode, add_spaces: bool = False) -> str:
        separator = " " if node.type == "math" and add_spaces else ""
        return separator.join(
            self._format_node(child, add_spaces)
            for child in self._skip_empty_text_node(node.content, node.type)
        )

    def _format_environment_node(
        self, node: EnvironmentNode, add_spaces: bool = False
    ) -> str:
        # Format the content within the environment
        content = "".join(
            self._format_node(child, add_spaces)
            for child in self._skip_empty_text_node(node.content)
        )

        # Apply environment-specific formatting
        formatted_content = _format_environment(node.name, content)

        # Handle subscripts and superscripts
        output = formatted_content
        if node.subscript:
            subscript = self._format_node(node.subscript, add_spaces)
            output += f"_{subscript}"
        if node.superscript:
            superscript = self._format_node(node.superscript, add_spaces)
            output += f"^{superscript}"

        return output

    def _format_node(self, node: Node, add_spaces: bool = False) -> str:
        if isinstance(node, TextNode):
            return self._format_text_node(node, add_spaces)
        elif isinstance(node, MacroNode):
            return self._format_macro_node(node, add_spaces)
        elif isinstance(node, MultiNode):
            return self._format_multi_node(node, add_spaces)
        elif isinstance(node, EnvironmentNode):
            return self._format_environment_node(node, add_spaces)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")

    def format_nodes(self, nodes: List[Node], add_spaces: bool = False) -> str:
        output = "".join(
            self._format_node(
                node, add_spaces and isinstance(node, MultiNode) and node.type == "math"
            )
            for node in self._skip_empty_text_node(nodes)
        )
        output = _clean_parentheses_spacing(output)
        return output
