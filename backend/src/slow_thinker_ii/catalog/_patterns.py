"""JSON Schema patterns use ECMA-262, whose `$` matches only at the very end of a string."""


def python_pattern(pattern: str) -> str:
    """The pattern for Python's `re`, where `$` would also match before a final newline.

    Every unescaped `$` outside a character class becomes `\\Z`; class boundaries follow
    Python's reading of the pattern, which compiles it.
    """
    parts: list[str] = []
    position = 0
    class_start = -1  # index of the `[` that opened the current character class
    while position < len(pattern):
        step = 2 if pattern[position] == "\\" else 1
        token = pattern[position : position + step]
        if class_start < 0:
            class_start = position if token == "[" else -1
            token = "\\Z" if token == "$" else token
        elif token == "]" and position > _first_member(pattern, class_start):
            class_start = -1
        parts.append(token)
        position += step
    return "".join(parts)


def _first_member(pattern: str, start: int) -> int:
    """Index of a class's first member; a `]` there is a member, not the class's end."""
    return start + 2 if pattern[start + 1 : start + 2] == "^" else start + 1
