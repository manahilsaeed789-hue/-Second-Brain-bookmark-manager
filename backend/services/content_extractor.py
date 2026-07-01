"""Content extraction from URLs, files, and raw text."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import pdfplumber
import requests
from bs4 import BeautifulSoup

from backend.config import get_settings

settings = get_settings()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def estimate_reading_time(text: str) -> int:
    """Estimate reading time in minutes (avg 200 wpm)."""
    words = len(text.split())
    return max(1, round(words / 200))


def count_words(text: str) -> int:
    return len(text.split())


def truncate_content(text: str, max_len: int | None = None) -> str:
    limit = max_len or settings.max_content_length
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[Content truncated...]"


def extract_from_url(url: str) -> dict:
    """Fetch and extract content from a web URL."""
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script/style elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    # Try article body selectors
    content = ""
    for selector in ["article", "main", '[role="main"]', ".post-content", ".article-body", ".entry-content"]:
        element = soup.select_one(selector)
        if element:
            content = element.get_text(separator="\n", strip=True)
            break

    if not content:
        content = soup.get_text(separator="\n", strip=True)

    content = re.sub(r"\n{3,}", "\n\n", content)
    content = truncate_content(content)

    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"]

    return {
        "title": title or urlparse(url).netloc,
        "content": content,
        "metadata": {
            "url": url,
            "description": description,
            "domain": urlparse(url).netloc,
        },
    }


def extract_from_pdf(file_path: str | Path) -> dict:
    """Extract text from a PDF file."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    content = "\n\n".join(text_parts)
    content = truncate_content(content)
    filename = Path(file_path).stem

    return {
        "title": filename.replace("_", " ").replace("-", " ").title(),
        "content": content,
        "metadata": {"filename": Path(file_path).name, "pages": len(text_parts)},
    }


def extract_from_text_file(file_path: str | Path) -> dict:
    """Extract content from TXT or Markdown files."""
    path = Path(file_path)
    content = path.read_text(encoding="utf-8", errors="ignore")
    content = truncate_content(content)

    title = path.stem.replace("_", " ").replace("-", " ").title()
    # Use first heading in markdown as title
    heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if heading_match:
        title = heading_match.group(1).strip()

    return {
        "title": title,
        "content": content,
        "metadata": {"filename": path.name, "extension": path.suffix},
    }


def extract_from_paste(content: str, title: Optional[str] = None) -> dict:
    """Process pasted article text."""
    content = truncate_content(content.strip())
    if not title:
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        title = lines[0][:200] if lines else "Pasted Content"
        if len(title) > 100:
            title = title[:97] + "..."

    return {
        "title": title,
        "content": content,
        "metadata": {"source": "paste"},
    }


def extract_from_note(title: str, content: str) -> dict:
    """Process a manual note."""
    content = truncate_content(content.strip())
    return {
        "title": title.strip() or "Untitled Note",
        "content": content,
        "metadata": {"source": "note"},
    }
