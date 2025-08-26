from typing import Dict, Callable

FORMATTER_TYPE = Callable[[str], str]

DEFAULT_FORMATTERS = {
    ("~", lambda _: "~" ),
    ("&", lambda _: "&" ),
    ("$", lambda _: "$" ),
    ("{", lambda _: "{" ),
    ("}", lambda _: "}" ),
    ("%", lambda _: "%" ),
    ("#", lambda _: "#" ),
    ("_", lambda _: "_" ),
}


class Mapping:
    def __init__(self, mapping: Dict[str, FORMATTER_TYPE]):
        self.mapping = {**DEFAULT_FORMATTERS, **mapping}
