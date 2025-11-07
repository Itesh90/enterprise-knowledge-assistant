from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Iterator, Dict

from bs4 import BeautifulSoup
from readability import Document as ReadabilityDocument

def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_pdf(path: Path) -> str:
    # Fallback: try PyPDF2, fallback to pdfminer
    text = ""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(str(path))
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        pass
    try:
        from pdfminer.high_level import extract_text

        return extract_text(str(path)) or ""
    except Exception:
        return text


def load_html(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    doc = ReadabilityDocument(html)
    content_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(content_html, "lxml")
    return soup.get_text("\n")


def iter_documents(paths: Iterable[str]) -> Iterator[Dict[str, str]]:
    for root in paths:
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                p = Path(dirpath) / name
                lower = name.lower()
                if lower.endswith((".md", ".markdown")):
                    text = load_markdown(p)
                    yield {"source": str(p), "title": p.stem, "text": text}
                elif lower.endswith(".pdf"):
                    text = load_pdf(p)
                    yield {"source": str(p), "title": p.stem, "text": text}
                elif lower.endswith((".html", ".htm")):
                    text = load_html(p)
                    yield {"source": str(p), "title": p.stem, "text": text}


def load_file_from_path(path: Path) -> Dict[str, str] | None:
    """Load a single file and return document dict."""
    lower = path.name.lower()
    if lower.endswith((".md", ".markdown")):
        text = load_markdown(path)
        return {"source": str(path), "title": path.stem, "text": text}
    elif lower.endswith(".pdf"):
        text = load_pdf(path)
        return {"source": str(path), "title": path.stem, "text": text}
    elif lower.endswith((".html", ".htm")):
        text = load_html(path)
        return {"source": str(path), "title": path.stem, "text": text}
    return None


