from typing import Dict, Callable

FORMATTER_TYPE = Callable[[str], str]


class Mapping:
    def __init__(self, mapping: Dict[str, FORMATTER_TYPE]):
        self.mapping = mapping
