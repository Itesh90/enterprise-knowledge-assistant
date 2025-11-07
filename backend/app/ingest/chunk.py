from __future__ import annotations

from typing import Dict, Iterator, List


def split_into_chunks(
    text: str, 
    max_tokens: int = 512, 
    overlap: int = 64,
) -> List[str]:
    # Approximate tokens by words; simple strategy for baseline
    words = text.split()
    if max_tokens <= 0:
        return [text]
    chunks: List[str] = []
    i = 0
    step = max(1, max_tokens - overlap)
    while i < len(words):
        chunk_words = words[i : i + max_tokens]
        chunks.append(" ".join(chunk_words))
        i += step
    return chunks


def iter_chunk_records(
    doc: Dict[str, str], max_tokens: int, overlap: int
) -> Iterator[Dict]:
    sections = doc["text"].split("\n# ")  # naive heading split
    position = 0
    for s in sections:
        section_title = "" if position == 0 else s.splitlines()[0][:120]
        section_text = s if position == 0 else "\n".join(s.splitlines()[1:])
        for ch in split_into_chunks(section_text, max_tokens, overlap):
            rec = {
                "text": ch,
                "tokens": len(ch.split()),
                "section": section_title,
                "position": position,
                "meta": {
                    "source": doc.get("source"),
                    "title": doc.get("title"),
                    "url": doc.get("url", ""),
                    "section": section_title,
                    "position": position,
                },
            }
            yield rec
            position += 1


