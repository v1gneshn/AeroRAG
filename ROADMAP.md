# AeroRAG — 30-Day Roadmap (June 2026)

One scoped, shippable deliverable per day. Each day ends with a git commit
and a `docs/daily_logs/YYYY-MM-DD.md` entry capturing what worked, what
didn't, and what's next.

**Time budget:** ~1.5–2 hrs/day on weekdays, ~3 hrs/day on weekends.
Anything that doesn't fit gets cut, not deferred — scope discipline is the
point.

**Definition of done for each day:**
1. Code/notes on `main` and pushed.
2. Daily log entry filed.
3. Tests still pass (after Day 8 once tests exist).

Legend: 🔧 build · 📚 research · ✅ eval · 🚢 ship

---

## Week 1 — Foundations & FAR/AIM ingestion (June 1–7)

### Day 01 · Mon Jun 01 · 🔧 Environment & first commit
- Create venv, install pinned `requirements.txt`.
- Verify `OPENAI_API_KEY` works with a 3-line "hello world" against
  `gpt-4o-mini`.
- Commit: `chore: bootstrap python env and verify openai access`.
- **DoD:** `python -c "from openai import OpenAI; print(OpenAI().models.list().data[0].id)"` prints.

### Day 02 · Tue Jun 02 · 📚 Source the corpus
- Download the **FAR (14 CFR Parts 61, 91, 119, 135)** from
  [ecfr.gov](https://www.ecfr.gov) as XML/HTML.
- Download the **AIM** PDF from
  [faa.gov](https://www.faa.gov/air_traffic/publications/).
- Download the **Pilot's Handbook of Aeronautical Knowledge (PHAK)**.
- Save everything to `data/raw/` (gitignored). Record SHA256 + source URLs
  in `data/raw/MANIFEST.md`.
- **DoD:** `du -sh data/raw/` shows ≥ ~50 MB of authoritative PDFs/XML.

### Day 03 · Wed Jun 03 · 🔧 PDF & XML parsing
- Implement `aerorag.data.loaders.load_pdf` using `pdfplumber` and
  `aerorag.data.loaders.load_ecfr_xml` using `lxml`.
- For ecFR XML, preserve §/(a)/(1) hierarchy as metadata.
- Write parsed text + structural metadata to `data/interim/*.jsonl`.
- **DoD:** one JSONL file per source doc; `wc -l` ≥ 500 lines per doc.

### Day 04 · Thu Jun 04 · 🔧 Chunking strategy
- Implement two chunkers in `aerorag.data.chunking`:
  - `recursive` (LangChain `RecursiveCharacterTextSplitter`, 800/120).
  - `regulatory` — split on §/(a)/(1) boundaries from Day 03 metadata.
- Compare avg/median chunk size + count on a notebook.
- **DoD:** `notebooks/04_chunking.ipynb` with comparison table.

### Day 05 · Fri Jun 05 · 🔧 Embeddings + Chroma index
- Embed every chunk with `text-embedding-3-small` (1536-d, cheap).
- Persist to `data/processed/chroma/` collection `aerorag_regs`.
- Log token usage + cost so far in the daily log.
- **DoD:** `chroma.PersistentClient(...).get_collection("aerorag_regs").count()` ≥ 2000.

### Day 06 · Sat Jun 06 · 🔧 First retrieval — eyeball mode
- CLI: `python -m aerorag.retrieval.search "VFR weather minimums class E"` returns top-5 chunks with source citations.
- Hand-craft **10 golden questions** in `tests/golden/regs.jsonl` (question + expected CFR cite). These become your eval set.
- **DoD:** golden file committed; CLI smoke test passes.

### Day 07 · Sun Jun 07 · ✅ Week 1 retro
- Run golden set through plain dense retrieval; log recall@5.
- Write `docs/weekly_retros/week1.md`: what surprised you, what's brittle,
  what to do differently in week 2.
- **DoD:** retro committed with concrete numbers.

---

## Week 2 — Core RAG pipeline & FAR/AIM Q&A (June 8–14)

### Day 08 · Mon Jun 08 · 🔧 Prompt + first end-to-end answer
- `aerorag.llm.prompts.REG_QA_PROMPT` — strict citation requirement
  ("Quote the exact §X.Y(a)(1) reference or say *insufficient context*").
- `aerorag.pipeline.answer(question)` returns `Answer(text, citations, contexts)`.
- **DoD:** CLI `python -m aerorag.pipeline "<q>"` produces cited answer.

### Day 09 · Tue Jun 09 · 🔧 Citation enforcement
- Post-process: reject any answer whose cited §s aren't present in the
  retrieved contexts. Force a regenerate (max 2 attempts) or return
  "insufficient context."
- **DoD:** unit test in `tests/test_citations.py` covers happy + reject paths.

### Day 10 · Wed Jun 10 · 🔧 Hybrid search (BM25 + dense)
- Add `rank_bm25` index over the same chunk corpus.
- `HybridRetriever` does RRF (reciprocal rank fusion) between BM25 and Chroma.
- **DoD:** golden set recall@5 ≥ +5pp vs Day 7 baseline.

### Day 11 · Thu Jun 11 · 🔧 Cross-encoder re-ranking
- Re-rank top-25 → top-5 with `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Measure latency hit; cache embeddings.
- **DoD:** golden set recall@5 ≥ +3pp vs Day 10.

### Day 12 · Fri Jun 12 · ✅ Faithfulness eval (manual + LLM-judge)
- Wire up `aerorag.eval.faithfulness` — LLM-judge prompt checks each
  sentence in the answer against retrieved contexts.
- Run on golden set; record faithfulness %.
- **DoD:** `docs/evals/week2_faithfulness.md` with score + 3 failure cases.

### Day 13 · Sat Jun 13 · 🔧 Streamlit UI v1
- `streamlit run src/aerorag/ui/app.py` — text box, answer, expandable
  citation panel with source PDF page link.
- **DoD:** screenshot committed to `docs/screenshots/v1.png`.

### Day 14 · Sun Jun 14 · ✅ Week 2 retro
- Re-run full eval suite, log scores.
- Decide: does the reg-only pipeline meet the "I'd trust this" bar? If
  not, week 3 starts with a fix, not a feature.
- **DoD:** `docs/weekly_retros/week2.md`.

---

## Week 3 — NTSB incident search (June 15–21)

### Day 15 · Mon Jun 15 · 📚 NTSB CAROL dataset
- Pull NTSB aviation accident dataset (CAROL JSON export).
- Subset to last 10 years for tractability.
- **DoD:** `data/raw/ntsb/` with ≥ 5k records; manifest updated.

### Day 16 · Tue Jun 16 · 🔧 Incident document model
- New schema: `Incident(narrative, probable_cause, aircraft, phase, date, location, severity)`.
- Embed the narrative; keep structured fields as metadata filters.
- **DoD:** Chroma collection `aerorag_incidents`.

### Day 17 · Wed Jun 17 · 🔧 Metadata-filtered retrieval
- Support filters: aircraft model, flight phase, severity, year range.
- CLI: `aerorag search-incidents --aircraft "C172" --phase landing "icing"`.
- **DoD:** filter combinations covered by `tests/test_filters.py`.

### Day 18 · Thu Jun 18 · 🔧 Query router
- Classifier prompt: regulation vs. incident vs. unknown.
- `aerorag.pipeline.answer` dispatches to the right sub-retriever.
- **DoD:** 20 hand-labeled queries route correctly ≥ 18/20.

### Day 19 · Fri Jun 19 · 🔧 Pattern-finding answers
- For incident queries, the answer summarizes *N similar incidents* with a
  ranked "common contributing factors" list.
- **DoD:** sample answer in `docs/screenshots/incident_demo.png`.

### Day 20 · Sat Jun 20 · 🔧 Conversational memory
- LangChain `ConversationBufferWindowMemory` (last 4 turns) in Streamlit.
- Follow-up questions resolve referents ("the second one you showed me").
- **DoD:** 3-turn demo recorded in daily log.

### Day 21 · Sun Jun 21 · ✅ Week 3 retro
- Eval router accuracy + incident faithfulness.
- **DoD:** `docs/weekly_retros/week3.md`.

---

## Week 4 — METAR/TAF, polish, ship (June 22–30)

### Day 22 · Mon Jun 22 · 🔧 Live weather tool
- Tool call against [aviationweather.gov](https://aviationweather.gov/data/api/)
  for METAR/TAF.
- Pure decoder (no LLM) in `aerorag.tools.metar.decode`.
- **DoD:** `decode("KJFK 211851Z 18012G22KT 10SM FEW050 28/19 A2998")` returns structured dict.

### Day 23 · Tue Jun 23 · 🔧 Wx briefing chain
- Given origin/destination + ETD, the model fetches METAR/TAF for both,
  decodes, and produces a plain-English go/no-go briefing **with
  explicit "this is not a flight dispatch" disclaimer**.
- **DoD:** end-to-end demo in notebook.

### Day 24 · Wed Jun 24 · ✅ RAGAS full sweep
- Wire `ragas` (faithfulness, answer_relevancy, context_precision,
  context_recall) into `aerorag.eval`.
- Run on combined golden set (regs + incidents).
- **DoD:** `docs/evals/week4_ragas.md` with the score table.

### Day 25 · Thu Jun 25 · 🔧 Latency & cost profiling
- Profile each stage; identify top-1 bottleneck. Add an LLM-response
  cache (`diskcache`).
- **DoD:** p50 latency reported pre/post; cost-per-query table.

### Day 26 · Fri Jun 26 · 🔧 Dockerize
- Multi-stage `Dockerfile` (slim runtime, no torch in prod image if
  re-ranker moved to a separate worker).
- `docker compose up` boots the Streamlit app.
- **DoD:** image < 1.5 GB; works on a clean machine.

### Day 27 · Sat Jun 27 · 🚢 Deploy
- Push to **Hugging Face Spaces** (free tier, no credit card) **or**
  **Fly.io** (closer to prod).
- Wire `OPENAI_API_KEY` as a secret.
- **DoD:** public URL in `README.md`.

### Day 28 · Sun Jun 28 · 🚢 Docs polish
- Architecture diagram (real, not ASCII), gif of the UI, "limitations &
  safety" section, contributor guide.
- **DoD:** README skimmable in 60 seconds.

### Day 29 · Mon Jun 29 · 🚢 Demo recording
- 3-minute screencast: reg query → incident query → wx briefing.
- Upload to YouTube unlisted; embed link in README.
- **DoD:** link in README.

### Day 30 · Tue Jun 30 · ✅ Final retro & v0.1.0 release
- Tag `v0.1.0`, GitHub Release with highlights + known limitations.
- Write the post-mortem: cost totals, hardest bug, top 3 things you'd do
  differently, what "v0.2" looks like.
- **DoD:** `docs/post_mortem.md` + GitHub Release published.

---

## Stretch goals (only if you're ahead, never instead)

- Multi-hop retrieval (sub-question decomposition).
- Re-rank ablation study (BGE vs. cross-encoder vs. ColBERT).
- Local embeddings (`bge-small-en-v1.5`) to drop OpenAI dependency.
- Voice input via Whisper for hands-free cockpit-style queries.
- Eval harness on Hugging Face Datasets for reproducibility.

## Anti-goals

- **No** fine-tuning. RAG only.
- **No** agent frameworks that hide what's happening (LangGraph beyond a
  single router is overkill for v0.1).
- **No** building a chat UI from scratch. Streamlit until it can't keep up.
- **No** scope expansion mid-week. Park ideas in `docs/parking_lot.md`.
