import os, time, re, hashlib
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict
import httpx, trafilatura
from bs4 import BeautifulSoup
import markdownify

UA = os.getenv("USER_AGENT", "ShikharResearchAgent/1.0")

def persist_raw(url: str, html: str, base="storage") -> str:
    h = hashlib.sha1(url.encode()).hexdigest()
    p = Path(base) / f"{h}.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return str(p)

def clean_text_from_html(html: str) -> str:
    extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
    if extracted:
        return extracted
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(" ", strip=True)

def fetch(url: str) -> Dict[str, str]:
    with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": UA}) as c:
        r = c.get(url)
        if r.status_code == 403:
            raise RuntimeError("403 Forbidden")
        r.raise_for_status()
        html = r.text
    text = clean_text_from_html(html)
    md = markdownify.markdownify(html, heading_style="ATX")
    raw_path = persist_raw(url, html)
    time.sleep(0.5)  # politeness
    return {"html": html, "text": text, "md": md, "raw_path": raw_path, "domain": urlparse(url).netloc}
