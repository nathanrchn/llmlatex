"""
llmlatex: A simple Python library for parsing LLM-generated text containing LaTeX.

Parse mixed text and LaTeX content into structured nodes, and apply custom 
formatting functions to LaTeX macros.
"""

from .parser import Parser, enumerate_macros
from .formatter import Formatter, DEFAULT_FORMATTERS
from .nodes import Node, TextNode, MacroNode, MultiNode

__version__ = "0.1.0"

__all__ = [
    "Parser",
    "enumerate_macros", 
    "Formatter",
    "DEFAULT_FORMATTERS",
    "Node",
    "TextNode", 
    "MacroNode",
    "MultiNode",
]
