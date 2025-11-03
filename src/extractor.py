# src/extractor.py
import os, json
from urllib.parse import urlparse
from dotenv import load_dotenv
from openai import OpenAI
from .models import ExtractedDoc

load_dotenv()

EXTRACTION_SYSTEM = """You are a strict information extractor.
Return **ONLY** valid JSON matching the schema.
Rules:
- Extract concrete data: entities (ORG, PERSON, LOCATION), dates, numbers (with units), and verbatim quotes with speakers if present.
- For EVERY claim, number, or quote, include a supporting URL (the page URL if no specific link is present).
- Do not summarize in prose inside fields. Keep values concise.
- Use null for unknowns. Never invent."""

def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ OPENAI_API_KEY missing. Put it in .env at repo root.")
    return OpenAI(api_key=api_key)

def _schema() -> dict:
    # dynamic import to avoid circulars
    from .models import ExtractedDoc
    return ExtractedDoc.model_json_schema()

def extract_from_text(url: str, text: str) -> ExtractedDoc:
    client = _get_client()
    schema = _schema()

    # 1) Try Responses API with JSON Schema (new SDKs)
    try:
        resp = client.responses.create(
            model="gpt-5",
            input=[
                {"role": "system", "content": EXTRACTION_SYSTEM},
                {"role": "user", "content": f"URL:\n{url}\n\nTEXT:\n{text[:120000]}"},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "ExtractedDoc", "schema": schema, "strict": True},
            },
        )
        raw = resp.output_parsed
    except TypeError:
        # 2) Fallback for older SDKs: Chat Completions with JSON object
        prompt = (
            "Extract the fields as JSON matching this JSON Schema exactly. "
            "No prose, only JSON.\n\nJSON Schema:\n"
            + json.dumps(schema, indent=2)
            + f"\n\nArticle URL: {url}\n\nText:\n{text[:120000]}"
        )
        cc = client.chat.completions.create(
            model="gpt-4o-mini",               # pick any chat-capable model you have
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},  # forces pure JSON
        )
        raw = json.loads(cc.choices[0].message.content)

    # finalize
    raw["url"] = url
    raw.setdefault("domain", urlparse(url).netloc)
    return ExtractedDoc(**raw)
