import re

WHITESPACE_RE = re.compile(r"[ \t\x0b\f\r]+")


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = WHITESPACE_RE.sub(" ", text)
    # Preserve code blocks and headings by not lowercasing
    lines = [ln.strip() for ln in text.split("\n")]
    # Drop duplicate empty lines
    out: list[str] = []
    last_empty = False
    for ln in lines:
        empty = len(ln) == 0
        if empty and last_empty:
            continue
        out.append(ln)
        last_empty = empty
    return "\n".join(out).strip()


