# Research Agent (Shikhar edition)

Scout the web, extract **structured facts** with citations, and produce a **creator-ready dossier**.

## Quickstart
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -e .`
3) Copy `.env.example` → `.env` and set `OPENAI_API_KEY` (and `TAVILY_API_KEY` if using Tavily).
4) Edit `config/topic.yml`.
5) `python -m src.cli run --config config/topic.yml`

### Notes
- Uses OpenAI **Responses API** with **Structured Outputs** (JSON schema) to keep results clean.
- Respects gentle politeness; consider adding robots.txt checks for production.
- Outputs: `out/facts.csv`, `out/dossier.md`.

### Cursor & Copilot
Open this repo in **Cursor** and enable **GitHub Copilot** for “Codex-style” help in-editor. The old Codex API isn’t used anymore; Copilot routes to current coding models. See references in code comments.
