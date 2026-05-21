# AeroRAG — Weekly Roadmap (May 22 – Jun 30, 2026)

**6 weeks · 28 weekdays · Mon–Fri only · weekends off.**

A polished PDF version lives at
[`docs/AeroRAG_Roadmap_May22-Jun30.pdf`](./docs/AeroRAG_Roadmap_May22-Jun30.pdf).

One scoped, demoable outcome per week. Anything that doesn't fit the week gets
cut, not pushed forward. One commit per workday with a short daily log.

**Definition of done for each week:**
1. Code/notes on `main` and pushed.
2. Weekly retro filed in `docs/weekly_retros/` with at least one quantitative datapoint.
3. Tests still pass.

---

## Week 1 · Fri May 22 + Mon–Fri May 25–29 · Foundations & corpus

- [ ] Bootstrap venv; verify OpenAI access with `gpt-4o-mini`
- [ ] Source-map FAR (14 CFR Parts 61, 91, 119, 135) / AIM / PHAK; download into `data/raw/` with SHA256 manifest
- [ ] PDF parsing (`pdfplumber`) + ecFR XML parser preserving §/(a)/(1) hierarchy → `data/interim/*.jsonl`
- [ ] Spot-check 5 parsed sections against the source PDFs to catch parser gotchas

**End-of-week:** Authoritative corpus parsed into structured JSONL with verifiable provenance.

## Week 2 · Mon–Fri Jun 01–05 · Chunking, embeddings, first retrieval

- [ ] Two chunkers: recursive (800/120) + regulatory §/(a)/(1) boundary
- [ ] Embed all chunks with `text-embedding-3-small` → persist Chroma collection `aerorag_regs`
- [ ] CLI: `aerorag search '<q>'` returns top-5 with citations
- [ ] Hand-craft 10-question golden set in `tests/golden/regs.jsonl`
- [ ] Compare chunkers on golden set (recall@5)

**End-of-week:** Working Chroma index + 10-question golden set with baseline numbers.

## Week 3 · Mon–Fri Jun 08–12 · RAG pipeline + hybrid retrieval

- [ ] Strict citation prompt; first end-to-end answer with §-level cites
- [ ] Citation enforcement: reject + regenerate (max 2 attempts) or refuse
- [ ] BM25 sparse index + RRF hybrid fusion with dense retrieval
- [ ] Cross-encoder re-rank top-25 → top-5
- [ ] LLM-judge faithfulness eval on golden set

**End-of-week:** Cited reg Q&A beating dense baseline by ≥5pp recall@5; faithfulness measured.

## Week 4 · Mon–Fri Jun 15–19 · Streamlit UI + NTSB ingestion

- [ ] Streamlit UI v1: question box, answer, expandable citations panel
- [ ] Source PDF page links from each citation
- [ ] Pull NTSB CAROL dataset (last 10 yrs) + incident schema
- [ ] Embed narratives; structured fields as metadata filters
- [ ] Metadata-filtered retrieval (aircraft model, flight phase, severity)

**End-of-week:** Clickable demo for regs + a filterable NTSB index seeded.

## Week 5 · Mon–Fri Jun 22–26 · Router + memory + METAR/TAF + full eval

- [ ] Query router: classify reg / incident / wx
- [ ] Pattern-finding answer for incident clusters
- [ ] Conversational memory (last 4 turns)
- [ ] METAR/TAF decoder tool ([aviationweather.gov](https://aviationweather.gov/data/api/)) + Wx briefing chain with **explicit non-dispatch disclaimer**
- [ ] RAGAS full sweep across all three sub-domains

**End-of-week:** Unified UX that routes across three data sources; system-wide eval table.

## Week 6 · Mon–Tue Jun 29–30 · Polish & ship

- [ ] Latency profiling + LLM-response disk cache; Dockerize
- [ ] Deploy to HF Spaces or Fly.io; 3-min demo screencast; tag `v0.1.0` with post-mortem

**End-of-week:** Public URL, demo video, GitHub Release with honest post-mortem.

---

## Working rhythm

Mon–Fri, ~1.5–2 hrs per workday. One commit per workday using:

```bash
./scripts/daily.sh "Wk 2 / Day 3 · embeddings + Chroma persist"
```

Even a "nothing worked today, here's what I learned" log counts — cadence beats heroics.

## Anti-goals

- **No fine-tuning.** Retrieval-only — that's where the leverage is for v0.1.
- **No agent frameworks that hide what's happening.** A single classifier-router is the limit.
- **No custom chat UI.** Streamlit until it can't keep up.
- **No mid-week scope expansion.** Ideas go in `docs/parking_lot.md`, not into this week.
- **No silent failures.** Every answer is either cited or refused.

## After v0.1.0 (stretch / v0.2 candidates)

- Multi-hop retrieval (sub-question decomposition).
- Re-rank ablation: BGE vs. cross-encoder vs. ColBERT.
- Swap to local embeddings (`bge-small-en-v1.5`) to drop the OpenAI dependency.
- Whisper voice input for hands-free cockpit-style queries.
- Publish the eval harness as a Hugging Face dataset for reproducibility.

## Regenerating the PDF

```bash
.venv/bin/pip install reportlab
.venv/bin/python scripts/generate_roadmap_pdf.py
```
