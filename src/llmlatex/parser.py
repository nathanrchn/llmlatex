from __future__ import annotations

import re
import os
from typing import List, Set, Tuple, Optional

from .nodes import Node, TextNode, MacroNode, MultiNode

MACRO_PATTERN = (
    r"\\([a-zA-Z]+|[{}$%&_#^~\\|])(?:\s*\[[^\]]*\]|\s*\{(?:[^{}]|\{[^{}]*\})*\})*"
)
SUBSCRIPT_PATTERN = r"_\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
SUPERSCRIPT_PATTERN = r"\^\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
MATH_INLINE_PATTERN = r"\$([^$]+)\$"
MATH_DISPLAY_PATTERN = r"\\?\[([^\]]+)\\?\]"
MATH_DOUBLE_DOLLAR_PATTERN = r"\$\$([^$]+)\$\$"

SKIP_MACROS = {
    "left",
    "right", 
    "big",
    "Big",
    "bigg",
    "Bigg",
    "bigl",
    "bigr",
    "Bigl",
    "Bigr",
    "biggl", 
    "biggr",
    "Biggl",
    "Biggr",
    "tiny",
    "scriptsize",
    "footnotesize",
    "small",
    "large",
    "Large",
    "LARGE",
    "huge",
    "Huge"
}


class Parser:
    def __init__(self):
        self.valid_commands = self._load_valid_commands()
    
    def _load_valid_commands(self) -> Set[str]:
        valid_commands = set()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        commands_file = os.path.join(current_dir, "commands.txt")
        
        try:
            with open(commands_file, "r", encoding="utf-8") as f:
                valid_commands = set([line[1:] for line in f.read().splitlines()])
        except FileNotFoundError:
            pass
            
        return valid_commands

    def _find_valid_command_name(self, command_name: str) -> Optional[str]:
        if command_name in self.valid_commands:
            return command_name
        
        for i in range(len(command_name) - 1, 0, -1):
            shortened_name = command_name[:i]
            if shortened_name in self.valid_commands:
                return shortened_name
        
        return None

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
                node, consumed_length = self._parse_macro(next_match)
                if node:
                    # Check for subscripts and superscripts after the macro
                    # Use the actual consumed length instead of the full match end
                    new_position = position + consumed_length
                    updated_node, new_position = self._parse_scripts(
                        node, text, new_position
                    )
                    nodes.append(updated_node)
                    position = new_position
                    continue
                else:
                    # Even if no node was created, we need to advance by the consumed length
                    position = position + consumed_length
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
                        subscript_node = MultiNode(content=subscript_nodes, type="any")
                    else:
                        subscript_node = None

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
                        superscript_node = MultiNode(
                            content=superscript_nodes, type="any"
                        )
                    else:
                        superscript_node = None

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

    def _parse_macro(self, match: re.Match) -> Tuple[Optional[MacroNode], int]:
        """
        Parse a macro and return the node and the actual consumed length.
        
        Returns:
            Tuple of (MacroNode or None, consumed_length)
            where consumed_length is how many characters from the match were actually used.
        """
        groups = match.groups()
        if not groups or not groups[0]:
            return None, match.end()

        original_command_name = groups[0]
        
        # Find the longest valid command name by progressively shortening
        command_name = self._find_valid_command_name(original_command_name)
        
        if not command_name or command_name in SKIP_MACROS:
            return None, match.end()
        
        # Calculate how much of the original match we actually consumed
        if len(command_name) < len(original_command_name):
            # We shortened the command, so we need to adjust the consumed length
            # The match starts with \commandname, so we need to account for the backslash
            consumed_length = len(command_name) + 1  # +1 for the backslash
        else:
            consumed_length = match.end()
            
        # For shortened commands, we only parse arguments from the valid command part
        if len(command_name) < len(original_command_name):
            # Reconstruct the match string for just the valid command
            valid_command_str = "\\" + command_name
            full_match = valid_command_str
        else:
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
                    required_args.append(MultiNode(content=arg_nodes, type="any"))
                else:
                    required_args.append(None)

        node = MacroNode(
            name=command_name,
            optional_arguments=optional_args if optional_args else None,
            arguments=required_args if required_args else None,
        )
        
        return node, consumed_length

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
                        subscript_node = MultiNode(content=subscript_nodes, type="any")
                    else:
                        subscript_node = None

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
                        superscript_node = MultiNode(
                            content=superscript_nodes, type="any"
                        )
                    else:
                        superscript_node = None

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

    def _remove_spaces_from_math_nodes(self, nodes: List[Node]) -> List[Node]:
        """Recursively remove spaces from text nodes within math content."""
        processed_nodes = []

        for node in nodes:
            if isinstance(node, TextNode):
                # Remove spaces from text content
                cleaned_content = node.content.replace(" ", "")

                # Process subscript and superscript if they exist
                cleaned_subscript = None
                cleaned_superscript = None

                if node.subscript:
                    cleaned_subscript = self._remove_spaces_from_single_node(
                        node.subscript
                    )

                if node.superscript:
                    cleaned_superscript = self._remove_spaces_from_single_node(
                        node.superscript
                    )

                processed_nodes.append(
                    TextNode(
                        content=cleaned_content,
                        subscript=cleaned_subscript,
                        superscript=cleaned_superscript,
                    )
                )

            elif isinstance(node, MacroNode):
                # Process macro arguments recursively
                cleaned_arguments = None
                if node.arguments:
                    cleaned_arguments = self._remove_spaces_from_math_nodes(
                        node.arguments
                    )

                # Process subscript and superscript if they exist
                cleaned_subscript = None
                cleaned_superscript = None

                if node.subscript:
                    cleaned_subscript = self._remove_spaces_from_single_node(
                        node.subscript
                    )

                if node.superscript:
                    cleaned_superscript = self._remove_spaces_from_single_node(
                        node.superscript
                    )

                processed_nodes.append(
                    MacroNode(
                        name=node.name,
                        arguments=cleaned_arguments,
                        optional_arguments=node.optional_arguments,
                        subscript=cleaned_subscript,
                        superscript=cleaned_superscript,
                    )
                )

            elif isinstance(node, MultiNode):
                # Recursively process multi-node content
                cleaned_content = self._remove_spaces_from_math_nodes(node.content)
                processed_nodes.append(
                    MultiNode(content=cleaned_content, type=node.type)
                )
            else:
                # For other node types, keep as is
                processed_nodes.append(node)

        return processed_nodes

    def _remove_spaces_from_single_node(self, node: Node) -> Node:
        """Helper to remove spaces from a single node."""
        if isinstance(node, TextNode):
            cleaned_content = node.content.replace(" ", "")

            cleaned_subscript = None
            cleaned_superscript = None

            if node.subscript:
                cleaned_subscript = self._remove_spaces_from_single_node(node.subscript)

            if node.superscript:
                cleaned_superscript = self._remove_spaces_from_single_node(
                    node.superscript
                )

            return TextNode(
                content=cleaned_content,
                subscript=cleaned_subscript,
                superscript=cleaned_superscript,
            )

        elif isinstance(node, MacroNode):
            cleaned_arguments = None
            if node.arguments:
                cleaned_arguments = self._remove_spaces_from_math_nodes(node.arguments)

            cleaned_subscript = None
            cleaned_superscript = None

            if node.subscript:
                cleaned_subscript = self._remove_spaces_from_single_node(node.subscript)

            if node.superscript:
                cleaned_superscript = self._remove_spaces_from_single_node(
                    node.superscript
                )

            return MacroNode(
                name=node.name,
                arguments=cleaned_arguments,
                optional_arguments=node.optional_arguments,
                subscript=cleaned_subscript,
                superscript=cleaned_superscript,
            )

        elif isinstance(node, MultiNode):
            cleaned_content = self._remove_spaces_from_math_nodes(node.content)
            return MultiNode(content=cleaned_content, type=node.type)
        else:
            return node

    def _parse_multi_node(self, match: re.Match) -> Optional[MultiNode]:
        groups = match.groups()
        if not groups or not groups[0]:
            return None

        math_content = groups[0].strip()
        if not math_content:
            return None

        content_nodes = self.parse(math_content)
        processed_nodes = self._remove_spaces_from_math_nodes(content_nodes)

        return MultiNode(content=processed_nodes, type="math")


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
