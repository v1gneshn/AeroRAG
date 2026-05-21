"""End-to-end RAG pipeline.

This is a stub for Day 1. The real implementation lands progressively:
- Day 8: prompt + first end-to-end answer
- Day 9: citation enforcement
- Day 10: hybrid retrieval
- Day 11: cross-encoder re-rank
- Day 18: query router (regs vs. incidents vs. weather)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field

from aerorag.config import settings


@dataclass
class Answer:
    text: str
    citations: list[str] = field(default_factory=list)
    contexts: list[str] = field(default_factory=list)


def answer(question: str) -> Answer:
    """Placeholder: real retrieval+generation lands on Day 8."""
    return Answer(
        text=(
            "[stub] Retrieval index is not built yet. "
            "Follow ROADMAP.md Days 2–8 to wire up real Q&A. "
            f"You asked: {question!r}."
        ),
        citations=[],
        contexts=[],
    )


def _cli() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m aerorag.pipeline '<question>'", file=sys.stderr)
        return 2
    question = " ".join(sys.argv[1:])
    result = answer(question)
    print(result.text)
    if result.citations:
        print("\nCitations:")
        for c in result.citations:
            print(f"  - {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
