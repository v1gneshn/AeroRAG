"""Smoke tests so `pytest` is green from Day 1."""
from aerorag import __version__
from aerorag.pipeline import answer


def test_version_is_set():
    assert __version__


def test_answer_stub_returns_payload():
    result = answer("anything")
    assert result.text
    assert isinstance(result.citations, list)
    assert isinstance(result.contexts, list)
