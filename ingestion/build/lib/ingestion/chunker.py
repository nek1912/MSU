import re

_HEADING = re.compile(r"^#{1,6}\s", re.M)


def _split_long(text: str, target: int, max_tokens: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= max_tokens:
        return [text] if text.strip() else []
    out, step = [], max(target - overlap, 1)
    for start in range(0, len(words), step):
        piece = words[start:start + target]
        if len(piece) < overlap and out:
            break
        out.append(" ".join(piece))
    return out


def chunk_markdown(body: str, target_tokens: int = 600, min_tokens: int = 400,
                   max_tokens: int = 800, overlap_tokens: int = 80) -> list[str]:
    sections, current = [], []
    for line in body.splitlines():
        if _HEADING.match(line) and current:
            sections.append("\n".join(current)); current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))

    chunks: list[str] = []
    for section in sections:
        words = section.split()
        if len(words) < min_tokens and chunks and len(chunks[-1].split()) + len(words) <= max_tokens:
            chunks[-1] = chunks[-1] + "\n" + section  # merge undersized tail
        else:
            chunks.extend(_split_long(section, target_tokens, max_tokens, overlap_tokens))
    return [c.strip() for c in chunks if c.strip()]
