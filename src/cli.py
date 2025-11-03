from dotenv import load_dotenv
load_dotenv()

import yaml, typer, os, traceback
from typing import List
from .discovery import discover
from .fetcher import fetch
from .extractor import extract_from_text
from .summarizer import summarize
from .exporters import export_csv, export_md
from .models import ExtractedDoc

# If your app was single-command, keep it that way:
import typer
app = typer.Typer(no_args_is_help=True)

@app.command()
def main(config: str = typer.Option(..., "--config", "-c", help="Path to topic.yml")):
    cfg = yaml.safe_load(open(config, "r", encoding="utf-8"))
    provider = cfg["discovery"].get("provider", "none")
    queries: List[str] = cfg["discovery"].get("queries", [])

    typer.echo("🔎 Discovering sources...")
    urls = discover(queries, provider=provider)
    urls=urls[:20]
    typer.echo(f"• Found {len(urls)} URLs")

    include = set(cfg["discovery"].get("include_domains") or [])
    exclude = set(cfg["discovery"].get("exclude_domains") or [])

    docs: List[ExtractedDoc] = []
    for url in urls:
        dom = url.split("/")[2]
        if include and dom not in include:
            typer.echo(f"  ⏭ Skipping (not in include_domains): {url}")
            continue
        if dom in exclude:
            typer.echo(f"  ⏭ Skipping (in exclude_domains): {url}")
            continue

        try:
            typer.echo(f"→ Fetching: {url}")
            page = fetch(url)
            typer.echo(f"  ✓ Fetched {len(page['text'])} chars")
            raw = extract_from_text(url, page["text"])   # this returns a dict OR ExtractedDoc depending on your version
            # If your extract_from_text returns an ExtractedDoc already, adapt accordingly:
            if isinstance(raw, dict):
                doc = ExtractedDoc(**raw, raw_text_path=page["raw_path"])
            else:
                raw.raw_text_path = page["raw_path"]
                doc = raw
            docs.append(doc)
            typer.echo(f"  ✓ Extracted: {doc.title[:60]}")
        except Exception as e:
            typer.echo(f"  ❌ Error on {url}: {e}")
            traceback.print_exc()

    typer.echo(f"🧠 Total extracted documents: {len(docs)}")

    summary = summarize(docs) if docs else "No docs found."
    export_csv(docs, cfg["outputs"]["facts_csv"])
    export_md(docs, summary, cfg["outputs"]["dossier_md"])
    typer.echo("✓ Done. See out/ for results.")

if __name__ == "__main__":
    app()
