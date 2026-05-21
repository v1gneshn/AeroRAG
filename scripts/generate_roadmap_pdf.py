"""Generate the AeroRAG weekly roadmap PDF (4-5 pages, weekly summary only).

Usage:
    python scripts/generate_roadmap_pdf.py
Produces:
    docs/AeroRAG_Roadmap_May22-Jun30.pdf
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "AeroRAG_Roadmap_May22-Jun30.pdf"

# --- Palette ---
NAVY = colors.HexColor("#0B3D91")
ORANGE = colors.HexColor("#FF6B35")
LIGHT = colors.HexColor("#F5F7FA")
LIGHT2 = colors.HexColor("#E9EEF5")
TEXT = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#6B7280")
LINE = colors.HexColor("#D1D5DB")

# ---------- Plan data (weekly, weekdays only) ----------

WEEKS: list[dict] = [
    {
        "n": 1,
        "range": "Fri May 22 + Mon–Fri May 25–29",
        "days": "6 weekdays",
        "theme": "Foundations & corpus",
        "tasks": [
            "Bootstrap venv; verify OpenAI access with gpt-4o-mini",
            "Source-map FAR (14 CFR) / AIM / PHAK; download into data/raw/ with SHA256 manifest",
            "PDF parsing (pdfplumber) + ecFR XML parser that preserves §/(a)/(1) hierarchy",
            "Spot-check 5 parsed sections vs. source PDFs to catch parser gotchas",
        ],
        "dod": "Authoritative corpus parsed into structured JSONL with verifiable provenance.",
    },
    {
        "n": 2,
        "range": "Mon–Fri Jun 01–05",
        "days": "5 weekdays",
        "theme": "Chunking, embeddings, first retrieval",
        "tasks": [
            "Two chunkers: recursive (800/120) + regulatory §/(a)/(1) boundary",
            "Embed with text-embedding-3-small → persist Chroma collection",
            "CLI: aerorag search '<q>' returns top-5 with citations",
            "Hand-craft a 10-question golden set; baseline recall@5 for both chunkers",
        ],
        "dod": "Working Chroma index + 10-question golden set with baseline numbers.",
    },
    {
        "n": 3,
        "range": "Mon–Fri Jun 08–12",
        "days": "5 weekdays",
        "theme": "RAG pipeline + hybrid retrieval",
        "tasks": [
            "Strict citation prompt; first end-to-end answer with §-level cites",
            "Citation enforcement: reject + regenerate (max 2 attempts) or refuse",
            "BM25 sparse index + RRF hybrid fusion with dense retrieval",
            "Cross-encoder re-rank top-25 → top-5",
            "LLM-judge faithfulness eval on golden set",
        ],
        "dod": "Cited reg Q&A beating dense baseline by ≥5pp recall@5; faithfulness measured.",
    },
    {
        "n": 4,
        "range": "Mon–Fri Jun 15–19",
        "days": "5 weekdays",
        "theme": "Streamlit UI + NTSB ingestion",
        "tasks": [
            "Streamlit UI v1: question box, answer, expandable citations panel",
            "Source PDF page links from each citation",
            "Pull NTSB CAROL dataset (last 10 yrs) + incident schema",
            "Embed narratives; structured fields as metadata filters",
            "Metadata-filtered retrieval (aircraft model, flight phase, severity)",
        ],
        "dod": "Clickable demo for regs + a filterable NTSB index seeded.",
    },
    {
        "n": 5,
        "range": "Mon–Fri Jun 22–26",
        "days": "5 weekdays",
        "theme": "Router + memory + METAR/TAF + full eval",
        "tasks": [
            "Query router: classify reg / incident / wx",
            "Pattern-finding answer for incident clusters",
            "Conversational memory (last 4 turns)",
            "METAR/TAF decoder tool (aviationweather.gov) + Wx briefing chain w/ non-dispatch disclaimer",
            "RAGAS full sweep across all three sub-domains",
        ],
        "dod": "Unified UX that routes across three data sources; system-wide eval table.",
    },
    {
        "n": 6,
        "range": "Mon–Tue Jun 29–30",
        "days": "2 weekdays",
        "theme": "Polish & ship",
        "tasks": [
            "Latency profiling + LLM-response disk cache; Dockerize",
            "Deploy to HF Spaces or Fly.io; 3-min demo screencast; tag v0.1.0 with post-mortem",
        ],
        "dod": "Public URL, demo video, GitHub Release with honest post-mortem.",
    },
]

PHASES = [
    ("Phase 1 — Reg-RAG",       "Weeks 1–3 (May 22 – Jun 12)", "Trustworthy FAR / AIM Q&A with strict citations."),
    ("Phase 2 — Incident-RAG",  "Week 4 (Jun 15 – Jun 19)",    "NTSB pattern search with metadata filters."),
    ("Phase 3 — Wx + Ship",     "Weeks 5–6 (Jun 22 – Jun 30)", "METAR/TAF briefings + deployed, eval'd, released."),
]

MILESTONES = [
    ("Fri May 29", "Corpus parsed & manifested"),
    ("Fri Jun 05", "First retrieval baseline measured"),
    ("Fri Jun 12", "Cited answers, hybrid retrieval, faithfulness eval"),
    ("Fri Jun 19", "Streamlit UI v1 + NTSB ingested"),
    ("Fri Jun 26", "Unified router, conversational, RAGAS sweep"),
    ("Tue Jun 30", "v0.1.0 deployed, demo video, post-mortem"),
]

STACK = [
    ("Language",         "Python 3.11"),
    ("Orchestration",    "LangChain (kept minimal)"),
    ("Vector store",     "ChromaDB (file-backed)"),
    ("Sparse retrieval", "rank_bm25 + RRF fusion"),
    ("Re-ranker",        "sentence-transformers cross-encoder"),
    ("Generator",        "OpenAI gpt-4o-mini"),
    ("Embeddings",       "text-embedding-3-small (1536-d)"),
    ("UI",               "Streamlit"),
    ("Eval",             "RAGAS + LLM-judge + golden set"),
    ("Deploy",           "Docker → HF Spaces / Fly.io"),
]

# ---------- Styles ----------

styles = getSampleStyleSheet()
H_TITLE = ParagraphStyle("HTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                         fontSize=40, leading=46, alignment=TA_LEFT, textColor=colors.white, spaceAfter=4)
H_SUB = ParagraphStyle("HSub", parent=styles["Normal"], fontName="Helvetica",
                       fontSize=15, leading=19, alignment=TA_LEFT, textColor=colors.white)
H_META = ParagraphStyle("HMeta", parent=styles["Normal"], fontName="Helvetica",
                        fontSize=10.5, leading=15, alignment=TA_LEFT, textColor=colors.white)
COVER_TAG = ParagraphStyle("CoverTag", parent=styles["Normal"], fontName="Helvetica-Oblique",
                           alignment=TA_CENTER, fontSize=13, leading=18, textColor=colors.white)
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
                    fontSize=20, leading=24, textColor=NAVY, spaceBefore=2, spaceAfter=10)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                    fontSize=13, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=6)
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica",
                      fontSize=10.5, leading=14.5, textColor=TEXT, spaceAfter=6)
BULLET = ParagraphStyle("Bullet", parent=BODY, leftIndent=14, bulletIndent=2, spaceAfter=2)
WEEK_NUM = ParagraphStyle("WeekNum", parent=styles["Normal"], fontName="Helvetica-Bold",
                          fontSize=11, leading=14, textColor=ORANGE)
WEEK_TITLE = ParagraphStyle("WeekTitle", parent=styles["Heading2"], fontName="Helvetica-Bold",
                            fontSize=14, leading=17, textColor=NAVY, spaceAfter=2)
WEEK_RANGE = ParagraphStyle("WeekRange", parent=styles["Normal"], fontName="Helvetica",
                            fontSize=9.5, leading=12, textColor=MUTED, spaceAfter=4)
WEEK_DOD = ParagraphStyle("WeekDoD", parent=styles["Normal"], fontName="Helvetica-Oblique",
                          fontSize=9.5, leading=13, textColor=MUTED, spaceAfter=2)

# ---------- Page templates ----------
PAGE_W, PAGE_H = LETTER
MARGIN = 0.6 * inch


def cover_bg(canvas, _doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(ORANGE)
    canvas.rect(0, PAGE_H - 0.25 * inch, PAGE_W, 0.25 * inch, stroke=0, fill=1)
    canvas.rect(0, 0, PAGE_W, 0.15 * inch, stroke=0, fill=1)
    canvas.restoreState()


def content_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 0.35 * inch, PAGE_W, 0.35 * inch, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(MARGIN, PAGE_H - 0.23 * inch, "AeroRAG  ·  Weekly Roadmap")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.23 * inch, "May 22 – Jun 30, 2026  ·  28 weekdays")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawCentredString(PAGE_W / 2, 0.35 * inch, f"Page {doc.page}")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 0.55 * inch, PAGE_W - MARGIN, 0.55 * inch)
    canvas.restoreState()


def build_doc(path: Path) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="AeroRAG Weekly Roadmap (May 22 – Jun 30, 2026)",
        author="v1gneshn",
        subject="6-week RAG prototype build plan (weekdays only)",
    )
    cover_frame = Frame(0.8 * inch, 0.8 * inch, PAGE_W - 1.6 * inch, PAGE_H - 1.6 * inch, id="cover")
    content_frame = Frame(MARGIN, 0.7 * inch, PAGE_W - 2 * MARGIN, PAGE_H - 1.1 * inch, id="content")
    doc.addPageTemplates([
        PageTemplate(id="cover",   frames=[cover_frame],   onPage=cover_bg),
        PageTemplate(id="content", frames=[content_frame], onPage=content_bg),
    ])
    return doc


# ---------- Story builders ----------

def cover_story() -> list:
    s: list = []
    s.append(Spacer(1, 1.7 * inch))
    s.append(Paragraph("AeroRAG", H_TITLE))
    s.append(Paragraph(
        "A retrieval-augmented co-pilot for FAA regulations,<br/>NTSB incidents, and live aviation weather.",
        H_SUB,
    ))
    s.append(Spacer(1, 0.45 * inch))
    meta = (
        "<b>Plan window:</b> Fri May 22 – Tue Jun 30, 2026 &nbsp;·&nbsp; 6 weeks &nbsp;·&nbsp; 28 weekdays<br/>"
        "<b>Cadence:</b> Mon–Fri only<br/>"
        "<b>Repository:</b> https://github.com/v1gneshn/AeroRAG<br/>"
        f"<b>Generated:</b> {date.today().isoformat()}"
    )
    s.append(Paragraph(meta, H_META))
    s.append(Spacer(1, 1.4 * inch))
    s.append(Paragraph(
        "One scoped weekly outcome. One commit per workday.<br/>Weekends off.",
        COVER_TAG,
    ))
    return s


def overview_story() -> list:
    s: list = [Paragraph("Project summary", H1)]
    s.append(Paragraph(
        "AeroRAG is a six-week prototype that builds a retrieval-augmented Q&amp;A system "
        "over three layers of aviation data — federal regulations, historical incident reports, "
        "and live weather — with strict citation enforcement and an honest, measured eval loop. "
        "The plan ships a deployable <b>v0.1.0</b> by June 30. Work happens Monday through Friday; "
        "weekends are explicitly off.",
        BODY,
    ))

    s.append(Paragraph("Phases", H2))
    phase_tbl = Table(
        [["Phase", "Window", "What good looks like"]] + [list(p) for p in PHASES],
        colWidths=[2.1 * inch, 2.0 * inch, 3.0 * inch],
    )
    phase_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT),
        ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
        ("LINEBELOW",  (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    s.append(phase_tbl)

    s.append(Paragraph("Stack", H2))
    stack_tbl = Table(STACK, colWidths=[1.7 * inch, 5.4 * inch])
    stack_tbl.setStyle(TableStyle([
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TEXTCOLOR",  (0, 0), (-1, -1), TEXT),
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",  (0, 0), (0, -1), NAVY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT, colors.white]),
        ("LINEBELOW",  (0, 0), (-1, -1), 0.3, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    s.append(stack_tbl)

    s.append(Paragraph("Weekly milestones", H2))
    ms = [["Date", "Milestone"]] + [list(m) for m in MILESTONES]
    ms_tbl = Table(ms, colWidths=[1.5 * inch, 5.6 * inch])
    ms_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT),
        ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
        ("LINEBELOW",  (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    s.append(ms_tbl)
    return s


def _week_card(w: dict) -> Table:
    """Render one week as a two-column 'card' (header + tasks)."""
    header = [
        [Paragraph(f"Week {w['n']}", WEEK_NUM)],
        [Paragraph(w["theme"], WEEK_TITLE)],
        [Paragraph(f"{w['range']}  ·  {w['days']}", WEEK_RANGE)],
    ]
    header_tbl = Table(header, colWidths=[2.2 * inch])
    header_tbl.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))

    bullets = [Paragraph(f"• {t}", BULLET) for t in w["tasks"]]
    bullets.append(Spacer(1, 4))
    bullets.append(Paragraph(f"<b>End-of-week:</b> {w['dod']}", WEEK_DOD))
    right = Table([[b] for b in bullets], colWidths=[4.7 * inch])
    right.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))

    card = Table([[header_tbl, right]], colWidths=[2.3 * inch, 4.8 * inch])
    card.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, 0), LIGHT),
        ("BACKGROUND",   (1, 0), (1, 0), colors.white),
        ("LINEABOVE",    (0, 0), (-1, 0), 0.6, NAVY),
        ("LINEBELOW",    (0, 0), (-1, 0), 0.4, LINE),
        ("LINEBEFORE",   (0, 0), (0, 0), 3, ORANGE),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    return card


def weeks_story() -> list:
    s: list = [Paragraph("Weekly plan", H1)]
    s.append(Paragraph(
        "Each week ends with a single, demoable outcome. Anything that doesn't fit the "
        "week gets cut, not pushed forward.",
        BODY,
    ))
    for w in WEEKS:
        s.append(_week_card(w))
        s.append(Spacer(1, 8))
    return s


def closing_story() -> list:
    s: list = [Paragraph("Working rhythm", H1)]
    s.append(Paragraph(
        "<b>Mon–Fri.</b> Weekends off. ~1.5 to 2 hrs per workday. "
        "One commit per day with a short message and a one-paragraph daily log. "
        "Even a \"nothing worked today, here's what I learned\" log counts — cadence beats heroics.",
        BODY,
    ))
    s.append(Paragraph("./scripts/daily.sh \"Wk 2 / Day 3 · embeddings + Chroma persist\"", ParagraphStyle(
        "Code", parent=BODY, fontName="Courier-Bold", textColor=NAVY, leftIndent=12, spaceAfter=8,
    )))
    s.append(Paragraph("→ stamps today's log from the template, opens it, stages, commits.", BODY))

    s.append(Paragraph("Anti-goals", H1))
    s.append(Paragraph(
        "Things this plan refuses to do, so the scope stays honest:",
        BODY,
    ))
    for line in [
        "<b>No fine-tuning.</b> Retrieval-only — that's where the leverage is for v0.1.",
        "<b>No agent frameworks that hide what's happening.</b> A single classifier-router is the limit.",
        "<b>No custom chat UI.</b> Streamlit until it can't keep up.",
        "<b>No mid-week scope expansion.</b> Ideas go to docs/parking_lot.md, not into this week.",
        "<b>No silent failures.</b> Every answer is either cited or refused.",
    ]:
        s.append(Paragraph(f"• {line}", BULLET))

    s.append(Paragraph("After v0.1.0 (stretch / v0.2 candidates)", H1))
    for line in [
        "Multi-hop retrieval (sub-question decomposition).",
        "Re-rank ablation: BGE vs. cross-encoder vs. ColBERT.",
        "Swap to local embeddings (bge-small-en-v1.5) to drop OpenAI dependency.",
        "Whisper voice input for hands-free cockpit-style queries.",
        "Publish eval harness as a Hugging Face dataset for reproducibility.",
    ]:
        s.append(Paragraph(f"• {line}", BULLET))
    return s


def build() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = build_doc(OUTPUT)

    story: list = []
    story += cover_story()
    story.append(NextPageTemplate("content"))
    story.append(PageBreak())
    story += overview_story()
    story.append(PageBreak())
    story += weeks_story()
    story.append(PageBreak())
    story += closing_story()

    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    out = build()
    print(f"Wrote {out} ({out.stat().st_size / 1024:.1f} KB)")
