from __future__ import annotations

from typing import List, Dict

SYSTEM_PROMPT = (
    "You are a domain-scoped Knowledge Assistant. Answer concisely and precisely, "
    "include citations like [1], [2] (title + URL). If context is insufficient, say \"I’m not sure\" "
    "and suggest where to look. Avoid speculation."
)


def pack_contexts(contexts: List[Dict], max_items: int = 5) -> List[Dict]:
    # Dedup by source+section, keep order
    seen = set()
    packed: List[Dict] = []
    for r in contexts:
        key = (r.get('source', ''), r.get('section', ''))
        if key in seen:
            continue
        seen.add(key)
        packed.append(r)
        if len(packed) >= max_items:
            break
    return packed


def build_prompt(query: str, contexts: List[Dict]) -> str:
    header = f"System:\n{SYSTEM_PROMPT}\n\n"
    ctx_lines: List[str] = []
    for r in pack_contexts(contexts):
        rank = r.get('rank', 0)
        title = r.get("title", "")
        url = r.get("url", "")
        text = r.get("text", "")
        source = r.get("source", "")
        
        # Include actual text content, not just metadata
        if text:
            ctx_lines.append(f"[{rank}] Source: {title} ({source})")
            if url:
                ctx_lines.append(f"URL: {url}")
            ctx_lines.append(f"Content: {text}")
            ctx_lines.append("")  # Empty line between chunks
        else:
            # Fallback if text is not available
            ctx_lines.append(f"[{rank}] {title} {url}")
    
    context_block = "\n".join(ctx_lines).strip()
    return f"{header}Context from knowledge base:\n{context_block}\n\nUser question: {query}\n\nAnswer based on the context above, using citations like [1], [2] when referencing sources:"


