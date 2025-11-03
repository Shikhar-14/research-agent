from pathlib import Path
import csv
from typing import List
from .models import ExtractedDoc

def export_csv(docs: List[ExtractedDoc], path="out/facts.csv"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path,"w",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url","title","published_at","entities","summary"])
        for d in docs:
            w.writerow([d.url, d.title, d.published_at, "|".join(d.entities), d.summary[:300]])

def export_md(docs: List[ExtractedDoc], summary: str, path="out/dossier.md"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    md = "# Research Dossier\n\n" + summary + "\n\n---\n"
    for d in docs:
        md += f"## {d.title}\n\nSource: {d.url}\n\n{d.summary}\n\n---\n"
    Path(path).write_text(md, encoding="utf-8")
