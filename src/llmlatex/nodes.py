from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


@dataclass
class Node:
    pass


@dataclass
class TextNode(Node):
    content: str
    subscript: Optional[Node] = None
    superscript: Optional[Node] = None


@dataclass
class MacroNode(Node):
    name: str
    arguments: Optional[List[Node]] = None
    optional_arguments: Optional[List[str]] = None
    subscript: Optional[Node] = None
    superscript: Optional[Node] = None


@dataclass
class MultiNode(Node):
    content: List[Node]
    type: Literal["math", "any"] = "any"
