from __future__ import annotations

from typing import List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


class Node(ABC):
    @abstractmethod
    def to_text(self) -> str:
        pass


@dataclass
class TextNode(Node):
    content: str

    def to_text(self) -> str:
        return self.content


@dataclass
class MacroNode(Node):
    name: str
    arguments: Optional[List[Node]] = None
    optional_arguments: Optional[List[str]] = None

    def to_text(self) -> str:
        output = f"\\{self.name}"

        if self.optional_arguments:
            for arg in self.optional_arguments:
                output += f"[{arg}]"

        if self.arguments:
            for arg in self.arguments:
                output += f"{{{arg.to_text()}}}"

        return output


@dataclass
class MultiNode(Node):
    content: List[Node]

    def to_text(self) -> str:
        return "".join(node.to_text() for node in self.content)
