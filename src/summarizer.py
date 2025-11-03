import os
from typing import List
from openai import OpenAI
from .models import ExtractedDoc

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUMMARY_SYS = """You write neutral, factual briefs with citations like [1],[2].
Output sections: 
1) 10-bullet digest, 
2) 5-part brief (Context, Drivers, What's New, Risks, Open Questions),
3) 1-paragraph TL;DR.
Include bracketed indices mapping to the Sources list at the end."""

def summarize(docs: List[ExtractedDoc]) -> str:
    sources = [f"[{i+1}] {d.title} — {d.url}" for i,d in enumerate(docs)]
    joined = "\n\n---\n\n".join([f"{d.title}\n{d.summary}" for d in docs])
    res = client.responses.create(
        model="gpt-5",
        input=[
            {"role":"system","content":SUMMARY_SYS},
            {"role":"user","content":f"Sources:\n" + "\n".join(sources) + f"\n\nExtracted summaries:\n{joined[:100000]}"},
        ],
    )
    return res.output_text
