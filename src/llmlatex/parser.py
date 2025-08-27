from __future__ import annotations

import re
from typing import List, Set, Tuple, Optional

from .nodes import Node, TextNode, MacroNode, MultiNode

MACRO_PATTERN = r"\\([a-zA-Z]+)(?:\s*\[[^\]]*\]|\s*\{(?:[^{}]|\{[^{}]*\})*\})*"
SUBSCRIPT_PATTERN = r"_\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
SUPERSCRIPT_PATTERN = r"\^\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
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
                    text_node, new_pos = self._parse_text_with_scripts(
                        remaining_text, position, text
                    )
                    nodes.append(text_node)
                break

            match_start = position + next_match.start()
            if match_start > position:
                text_content = text[position:match_start]
                if text_content:
                    text_node = TextNode(text_content)
                    # Check for scripts immediately after this text content
                    updated_node, new_pos = self._parse_scripts(
                        text_node, text, match_start
                    )
                    nodes.append(updated_node)
                    if new_pos > match_start:
                        # Scripts were found and consumed, adjust the position
                        position = new_pos
                        continue

            if match_type == "macro":
                node = self._parse_macro(next_match)
                if node:
                    # Check for subscripts and superscripts after the macro
                    new_position = position + next_match.end()
                    updated_node, new_position = self._parse_scripts(
                        node, text, new_position
                    )
                    nodes.append(updated_node)
                    position = new_position
                    continue
            elif match_type == "subscript":
                # This is a standalone subscript, we need to attach it to the previous node
                if nodes:
                    prev_node = nodes.pop()  # Remove the last node
                    subscript_content = next_match.group(1)
                    subscript_nodes = self.parse(subscript_content)
                    if len(subscript_nodes) == 1:
                        subscript_node = subscript_nodes[0]
                    elif len(subscript_nodes) > 1:
                        subscript_node = MultiNode(content=subscript_nodes)
                    else:
                        subscript_node = TextNode("")

                    # Add subscript to previous node
                    if isinstance(prev_node, (MacroNode, TextNode)):
                        if isinstance(prev_node, MacroNode):
                            updated_node = MacroNode(
                                name=prev_node.name,
                                arguments=prev_node.arguments,
                                optional_arguments=prev_node.optional_arguments,
                                subscript=subscript_node,
                                superscript=prev_node.superscript,
                            )
                        else:  # TextNode
                            updated_node = TextNode(
                                content=prev_node.content,
                                subscript=subscript_node,
                                superscript=prev_node.superscript,
                            )
                        nodes.append(updated_node)
                    else:
                        # Can't attach to this node type, put it back and continue
                        nodes.append(prev_node)
            elif match_type == "superscript":
                # This is a standalone superscript, we need to attach it to the previous node
                if nodes:
                    prev_node = nodes.pop()  # Remove the last node
                    superscript_content = next_match.group(1)
                    superscript_nodes = self.parse(superscript_content)
                    if len(superscript_nodes) == 1:
                        superscript_node = superscript_nodes[0]
                    elif len(superscript_nodes) > 1:
                        superscript_node = MultiNode(content=superscript_nodes)
                    else:
                        superscript_node = TextNode("")

                    # Add superscript to previous node
                    if isinstance(prev_node, (MacroNode, TextNode)):
                        if isinstance(prev_node, MacroNode):
                            updated_node = MacroNode(
                                name=prev_node.name,
                                arguments=prev_node.arguments,
                                optional_arguments=prev_node.optional_arguments,
                                subscript=prev_node.subscript,
                                superscript=superscript_node,
                            )
                        else:  # TextNode
                            updated_node = TextNode(
                                content=prev_node.content,
                                subscript=prev_node.subscript,
                                superscript=superscript_node,
                            )
                        nodes.append(updated_node)
                    else:
                        # Can't attach to this node type, put it back and continue
                        nodes.append(prev_node)
            elif match_type in ["math_inline", "math_display", "math_double_dollar"]:
                node = self._parse_multi_node(next_match)
                if node:
                    # Check for subscripts and superscripts after math blocks too
                    new_position = position + next_match.end()
                    updated_node, new_position = self._parse_scripts(
                        node, text, new_position
                    )
                    nodes.append(updated_node)
                    position = new_position
                    continue

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

        # Look for subscripts and superscripts (these should have higher priority than individual macros)
        subscript_match = re.search(SUBSCRIPT_PATTERN, search_text)
        if subscript_match:
            matches.append(
                (start_pos + subscript_match.start(), subscript_match, "subscript")
            )

        superscript_match = re.search(SUPERSCRIPT_PATTERN, search_text)
        if superscript_match:
            matches.append(
                (
                    start_pos + superscript_match.start(),
                    superscript_match,
                    "superscript",
                )
            )

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

    def _parse_text_with_scripts(
        self, text_content: str, start_pos: int, full_text: str
    ) -> Tuple[TextNode, int]:
        """Parse text content and check for scripts that might follow."""
        # For the remaining text case, we need to check if any part of it has scripts
        # Look for the first occurrence of a script pattern
        script_pos = len(text_content)

        # Find the earliest script in the text content
        for pattern in [SUBSCRIPT_PATTERN, SUPERSCRIPT_PATTERN]:
            match = re.search(pattern, text_content)
            if match:
                script_pos = min(script_pos, match.start())

        if script_pos < len(text_content):
            # Found a script, split the text
            pure_text = text_content[:script_pos]
            text_node = TextNode(pure_text)

            # Parse scripts starting from the script position
            updated_node, new_pos = self._parse_scripts(
                text_node, full_text, start_pos + script_pos
            )
            return updated_node, new_pos
        else:
            # No scripts found, return simple text node
            return TextNode(text_content), start_pos + len(text_content)

    def _parse_scripts(self, node: Node, text: str, position: int) -> Tuple[Node, int]:
        """Parse subscripts and superscripts that may follow a node."""
        current_pos = position
        updated_node = node

        # Keep looking for scripts until we don't find any more
        while current_pos < len(text):
            remaining_text = text[current_pos:]

            # Check for subscript
            subscript_match = re.match(SUBSCRIPT_PATTERN, remaining_text)
            if subscript_match:
                subscript_content = subscript_match.group(1)
                if subscript_content:
                    # Parse the subscript content
                    subscript_nodes = self.parse(subscript_content)
                    if len(subscript_nodes) == 1:
                        subscript_node = subscript_nodes[0]
                    elif len(subscript_nodes) > 1:
                        subscript_node = MultiNode(content=subscript_nodes)
                    else:
                        subscript_node = TextNode("")

                    # Create new node with subscript based on type
                    if isinstance(updated_node, MacroNode):
                        updated_node = MacroNode(
                            name=updated_node.name,
                            arguments=updated_node.arguments,
                            optional_arguments=updated_node.optional_arguments,
                            subscript=subscript_node,
                            superscript=updated_node.superscript,
                        )
                    elif isinstance(updated_node, TextNode):
                        updated_node = TextNode(
                            content=updated_node.content,
                            subscript=subscript_node,
                            superscript=updated_node.superscript,
                        )
                    # For other node types, we can't add scripts directly
                    else:
                        break

                    current_pos += subscript_match.end()
                    continue

            # Check for superscript
            superscript_match = re.match(SUPERSCRIPT_PATTERN, remaining_text)
            if superscript_match:
                superscript_content = superscript_match.group(1)
                if superscript_content:
                    # Parse the superscript content
                    superscript_nodes = self.parse(superscript_content)
                    if len(superscript_nodes) == 1:
                        superscript_node = superscript_nodes[0]
                    elif len(superscript_nodes) > 1:
                        superscript_node = MultiNode(content=superscript_nodes)
                    else:
                        superscript_node = TextNode("")

                    # Create new node with superscript based on type
                    if isinstance(updated_node, MacroNode):
                        updated_node = MacroNode(
                            name=updated_node.name,
                            arguments=updated_node.arguments,
                            optional_arguments=updated_node.optional_arguments,
                            subscript=updated_node.subscript,
                            superscript=superscript_node,
                        )
                    elif isinstance(updated_node, TextNode):
                        updated_node = TextNode(
                            content=updated_node.content,
                            subscript=updated_node.subscript,
                            superscript=superscript_node,
                        )
                    # For other node types, we can't add scripts directly
                    else:
                        break

                    current_pos += superscript_match.end()
                    continue

            # No more scripts found
            break

        return updated_node, current_pos

    def _parse_multi_node(self, match: re.Match) -> Optional[MultiNode]:
        groups = match.groups()
        if not groups or not groups[0]:
            return None

        math_content = groups[0].strip()
        if not math_content:
            return None

        content_nodes = [TextNode(math_content)]

        return MultiNode(content=content_nodes)


def _collect_macro_names(node: Node) -> set[str]:
    macro_names = set()

    if isinstance(node, MacroNode):
        macro_names.add(node.name)

        if node.arguments:
            for arg_node in node.arguments:
                macro_names.update(_collect_macro_names(arg_node))

        if node.subscript:
            macro_names.update(_collect_macro_names(node.subscript))

        if node.superscript:
            macro_names.update(_collect_macro_names(node.superscript))

    elif isinstance(node, MultiNode):
        for content_node in node.content:
            macro_names.update(_collect_macro_names(content_node))

    elif isinstance(node, TextNode):
        if node.subscript:
            macro_names.update(_collect_macro_names(node.subscript))

        if node.superscript:
            macro_names.update(_collect_macro_names(node.superscript))

    return macro_names


def enumerate_macros(text: str) -> Set[str]:
    nodes = Parser().parse(text)

    all_macro_names = set()
    for node in nodes:
        all_macro_names.update(_collect_macro_names(node))

    return all_macro_names
