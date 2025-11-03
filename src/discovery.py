import os
from typing import List, Set
from pathlib import Path
import yaml
import httpx
import typer
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def gather_internal_links(start_urls, same_domain=True, limit_per_domain=5):
    urls = []
    seen = set()
    for start in start_urls:
        try:
            with httpx.Client(timeout=20, follow_redirects=True) as c:
                r = c.get(start)
                r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
            base = urlparse(start).netloc
            for a in soup.select("a[href]"):
                href = a["href"]
                if href.startswith("#"): 
                    continue
                if href.startswith("/"):
                    href = f"https://{base}{href}"
                if same_domain and urlparse(href).netloc != base:
                    continue
                if href in seen: 
                    continue
                seen.add(href)
                # Prefer likely articles / pdfs / press pages
                if re.search(r"(press|release|report|pdf|policy|cable|landing)", href, re.I):
                    urls.append(href)
                if len([u for u in urls if urlparse(u).netloc==base]) >= limit_per_domain:
                    break
        except Exception:
            pass
    return urls


def tavily_search(q: str, max_results: int = 8) -> List[str]:
    api = os.getenv("TAVILY_API_KEY")
    if not api:
        return []
    url = "https://api.tavily.com/search"
    payload = {"api_key": api, "query": q, "max_results": max_results}
    with httpx.Client(timeout=20) as c:
        r = c.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
    return [i.get("url") for i in data.get("results", []) if i.get("url")]

def discover(queries: List[str], provider: str = "none") -> List[str]:
    seen: Set[str] = set()
    urls: List[str] = []

    if provider == "tavily":
        if not os.getenv("TAVILY_API_KEY"):
            typer.echo("⚠️  TAVILY_API_KEY not set; falling back to seed_urls in config/topic.yml")
        else:
            for q in queries or []:
                for u in tavily_search(q) or []:
                    if u not in seen:
                        seen.add(u); urls.append(u)

    # Always merge seed_urls from config/topic.yml as a fallback
    try:
        cfg = yaml.safe_load(Path("config/topic.yml").read_text(encoding="utf-8"))
        for u in (cfg.get("discovery", {}).get("seed_urls") or []):
            if u not in seen:
                seen.add(u); urls.append(u)
    except Exception:
        pass

    expanded = gather_internal_links(urls, same_domain=True, limit_per_domain=5)
    # merge and dedupe
    for u in expanded:
        if u not in seen:
            seen.add(u); urls.append(u)
    return urls
