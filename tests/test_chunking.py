import pytest

from app.rag.chunking import chunk_text


def test_chunk_text_splits_and_overlaps():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert chunks == ["abcdefghij", "ijklmnopqr", "qrstuvwxyz"]


def test_chunk_text_returns_empty_for_blank_text():
    assert chunk_text("   \n\t ", chunk_size=10, overlap=2) == []


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("abcdef", chunk_size=5, overlap=5)
