# llmlatex

A simple Python library for parsing LLM-generated text containing LaTeX. Parse mixed text and LaTeX content into structured nodes, and apply custom formatting functions to LaTeX macros.

## Usage

```python
from src import parse_latex, format_latex_text, probabilistic_formatter

# Parse text with LaTeX
text = "Calculate $a \\times b$ where $\\alpha = 5$."
nodes = parse_latex(text)

# Apply custom formatters
formatters = {
    'times': probabilistic_formatter([(0.8, " * "), (0.2, " · ")]),
    'alpha': lambda args, opts: "α"
}
formatted = format_latex_text(text, formatters)
```
