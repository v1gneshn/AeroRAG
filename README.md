# AeroRAG

A 6-week RAG (Retrieval-Augmented Generation) prototype built on aviation data.
The goal: ship a working **Flight Safety Co-pilot** that can answer pilot
questions grounded in primary-source FAA documents, with cited evidence and
zero hallucination tolerance.

> Status: **Scaffolding complete.** Building runs **May 22 – Jun 30, 2026**.
> Cadence: **Mon–Fri only**, weekends off, ~28 weekdays total.
> One commit per workday.

See the full plan in [`ROADMAP.md`](./ROADMAP.md) or the polished
[PDF summary](./docs/AeroRAG_Roadmap_May22-Jun30.pdf) (5 pages).

---

## Why this project?

Aviation is one of the few domains where:

1. The reference corpus is **public, large, and authoritative** (FAR/AIM, PHAK,
   NTSB, ASRS, METAR/TAF feeds).
2. **Citations matter** — a pilot needs to know *exactly* which regulation says
   they can or can't do something.
3. **Hallucinations have real-world consequences**, which makes evaluation
   non-optional.

That makes it a near-perfect testbed for serious RAG engineering rather than
toy demos.

## Phased scope

| Phase | Window | Data | Question shape |
| --- | --- | --- | --- |
| **1. Reg-RAG** | May 22 – Jun 12 (Wk 1–3) | FAR (14 CFR), AIM, PHAK PDFs | *"Can I fly VFR-on-top without an IFR clearance?"* |
| **2. Incident-RAG** | Jun 15 – Jun 19 (Wk 4) | NTSB / ASRS reports | *"Show me prior incidents involving icing on Cessna 172."* |
| **3. Wx-RAG & ship** | Jun 22 – Jun 30 (Wk 5–6) | Live METAR / TAF / PIREP | *"Decode KJFK 211851Z 18012G22KT…"* + deploy v0.1.0 |

## Architecture (target end-state)

```
                    ┌──────────────────────────┐
                    │       Streamlit UI        │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │      Query Router         │  (reg | incident | wx)
                    └────────────┬─────────────┘
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
       │  Reg Index   │   │ NTSB / ASRS  │   │  Live Wx API │
       │ (Chroma+BM25)│   │   (Chroma)   │   │   (METAR)    │
       └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │  Re-ranker (cross-enc.)  │
                    └────────────┬─────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │  OpenAI gpt-4o-mini w/   │
                    │  citation-enforced prompt│
                    └──────────────────────────┘
```

## Stack

- **Python 3.11**
- **LangChain** for orchestration (swappable)
- **ChromaDB** for the vector store (file-backed, zero-ops)
- **rank_bm25** for sparse retrieval (hybrid search)
- **sentence-transformers** for re-ranking
- **OpenAI** `gpt-4o-mini` for generation, `text-embedding-3-small` for embeddings
- **Streamlit** for the UI
- **RAGAS** + custom evals
- **pytest** for unit tests

## Quick start

```bash
git clone https://github.com/v1gneshn/AeroRAG.git
cd AeroRAG

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set OPENAI_API_KEY

# (after Day 2 lands) ingest the FAR/AIM corpus
python -m aerorag.data.ingest

# (after Day 9 lands) ask a question
python -m aerorag.pipeline "What are the VFR weather minimums in Class E airspace below 10,000 ft MSL?"
```

## Repo layout

```
AeroRAG/
├── README.md              ← this file
├── ROADMAP.md             ← full 30-day plan
├── docs/
│   └── daily_logs/        ← one markdown file per day
├── src/aerorag/
│   ├── config.py          ← env / settings
│   ├── data/              ← loaders, chunkers, ingest pipelines
│   ├── retrieval/         ← dense + sparse + hybrid + re-rank
│   ├── llm/               ← prompt templates, OpenAI client
│   ├── eval/              ← RAGAS + custom metrics
│   └── pipeline.py        ← end-to-end RAG chain
├── data/
│   ├── raw/               ← downloaded PDFs / JSON (gitignored)
│   ├── interim/           ← parsed text
│   └── processed/         ← chunked + embedded artifacts
├── notebooks/             ← exploration notebooks
├── tests/                 ← pytest
└── scripts/               ← helpers (incl. daily commit helper)
```

## Weekly discipline

Every Mon–Fri carries a small commit toward a single weekly outcome.
Weekends are explicitly off. See [`ROADMAP.md`](./ROADMAP.md) for the
weekly plan and [`docs/daily_logs/`](./docs/daily_logs/) for the logbook
of what actually shipped each day.

A helper is provided to streamline the daily commit ritual:

```bash
./scripts/daily.sh "Day 03: PDF parsing pipeline with pdfplumber"
```

This stamps today's log file, opens it for editing, stages, and commits.

## License

MIT — see [`LICENSE`](./LICENSE).
