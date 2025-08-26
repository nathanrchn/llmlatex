from __future__ import annotations

import re
from typing import List, Tuple, Optional

from nodes import Node, TextNode, MacroNode, MultiNode

MACRO_PATTERN = r"\\([a-zA-Z]+)(?:\s*\[[^\]]*\]|\s*\{(?:[^{}]|\{[^{}]*\})*\})*"
MATH_INLINE_PATTERN = r"\$([^$]+)\$"
MATH_DISPLAY_PATTERN = r"\\?\[([^\]]+)\\?\]"
MATH_DOUBLE_DOLLAR_PATTERN = r"\$\$([^$]+)\$\$"


class Parser:
    def __init__(self):
        pass

    def parse(self, text: str) -> List[Node]:
        if not text:
            return []

        nodes = []
        position = 0

        while position < len(text):
            next_match, match_type = self._find_next_match(text, position)

            if next_match is None:
                remaining_text = text[position:]
                if remaining_text:
                    nodes.append(TextNode(remaining_text))
                break

            match_start = position + next_match.start()
            if match_start > position:
                text_content = text[position:match_start]
                if text_content:
                    nodes.append(TextNode(text_content))

            if match_type == "macro":
                node = self._parse_macro(next_match)
                if node:
                    nodes.append(node)
            elif match_type in ["math_inline", "math_display", "math_double_dollar"]:
                node = self._parse_multi_node(next_match)
                if node:
                    nodes.append(node)

            position = position + next_match.end()

        return nodes

    def _find_next_match(
        self, text: str, start_pos: int
    ) -> Tuple[Optional[re.Match], Optional[str]]:
        matches = []
        search_text = text[start_pos:]

        macro_match = re.search(MACRO_PATTERN, search_text)
        if macro_match:
            matches.append((start_pos + macro_match.start(), macro_match, "macro"))

        math_inline_match = re.search(MATH_INLINE_PATTERN, search_text)
        if math_inline_match:
            matches.append(
                (
                    start_pos + math_inline_match.start(),
                    math_inline_match,
                    "math_inline",
                )
            )

        math_display_match = re.search(MATH_DISPLAY_PATTERN, search_text)
        if math_display_match:
            matches.append(
                (
                    start_pos + math_display_match.start(),
                    math_display_match,
                    "math_display",
                )
            )

        math_double_match = re.search(MATH_DOUBLE_DOLLAR_PATTERN, search_text)
        if math_double_match:
            matches.append(
                (
                    start_pos + math_double_match.start(),
                    math_double_match,
                    "math_double_dollar",
                )
            )

        if not matches:
            return None, None

        earliest = min(matches, key=lambda x: x[0])
        return earliest[1], earliest[2]

    def _parse_macro(self, match: re.Match) -> Optional[MacroNode]:
        groups = match.groups()
        if not groups or not groups[0]:
            return None

        command_name = groups[0]
        full_match = match.group(0)

        optional_args = []
        optional_matches = re.findall(r"\[([^\]]*)\]", full_match)
        if optional_matches:
            optional_args = optional_matches

        required_args = []
        brace_args = self._extract_brace_arguments(full_match)
        for arg_text in brace_args:
            if arg_text:
                arg_nodes = self.parse(arg_text)
                if len(arg_nodes) == 1:
                    required_args.append(arg_nodes[0])
                elif len(arg_nodes) > 1:
                    required_args.append(MultiNode(content=arg_nodes))
                else:
                    required_args.append(TextNode(""))

        return MacroNode(
            name=command_name,
            optional_arguments=optional_args if optional_args else None,
            arguments=required_args if required_args else None,
        )

    def _extract_brace_arguments(self, text: str) -> List[str]:
        arguments = []
        i = 0
        while i < len(text):
            if text[i] == "{":
                brace_count = 1
                start = i + 1
                i += 1
                while i < len(text) and brace_count > 0:
                    if text[i] == "{":
                        brace_count += 1
                    elif text[i] == "}":
                        brace_count -= 1
                    i += 1

                if brace_count == 0:
                    argument = text[start : i - 1]
                    arguments.append(argument)
                else:
                    break
            else:
                i += 1

        return arguments

    def _parse_multi_node(self, match: re.Match) -> Optional[MultiNode]:
        groups = match.groups()
        if not groups or not groups[0]:
            return None

        math_content = groups[0].strip()
        if not math_content:
            return None

        content_nodes = [TextNode(math_content)]

        return MultiNode(content=content_nodes)


if __name__ == "__main__":
    parser = Parser()
    print(parser.parse(r"\textbf{Bold} \textit{Italic}"))
