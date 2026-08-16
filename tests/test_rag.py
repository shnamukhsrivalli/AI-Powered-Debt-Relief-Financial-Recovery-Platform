import pytest
from pathlib import Path
from rag.chunker import chunk_document
from rag.document_loader import load_knowledge_documents
from rag.vector_store import VectorStore
from unittest.mock import MagicMock

def test_document_chunking():
    doc = {
        "title": "Test Title",
        "content": "This is a sentence. " * 30,  # ~600 characters
        "source": "test.md"
    }
    
    chunks = chunk_document(doc, chunk_size=200, chunk_overlap=40)
    
    assert len(chunks) > 1
    assert chunks[0]["title"] == "Test Title"
    assert chunks[0]["chunk_index"] == 0
    # Overlap assertions
    assert len(chunks[0]["content"]) > 0


def test_document_loader(tmp_path):
    # Setup dummy directory
    d = tmp_path / "knowledge"
    d.mkdir()
    p = d / "test_basics.md"
    p.write_text("# Test Article\nThis is basic personal finance.", encoding="utf-8")
    
    docs = load_knowledge_documents(d)
    assert len(docs) == 1
    assert docs[0]["title"] == "Test Basics"
    assert "personal finance" in docs[0]["content"]


def test_vector_store_offline(tmp_path):
    # Setup offline VectorStore index
    vs = VectorStore(tmp_path / "vector_index")
    
    # Mock GeminiService's embedding generation
    dummy_vector = [0.1] * 768
    vs.ai_service.get_embeddings = MagicMock(return_value=dummy_vector)
    
    mock_chunks = [
        {"title": "Debt A", "content": "How to clear debt snowball", "source": "snowball.md", "chunk_index": 0},
        {"title": "Debt B", "content": "How to pay avalanche rates", "source": "avalanche.md", "chunk_index": 0}
    ]
    
    vs.build_index(mock_chunks)
    
    assert vs.is_built() is True
    
    # Reload from disk
    vs.load_index()
    
    # Query similarity search (will return both since they share the same mock dummy vector)
    results = vs.similarity_search("How to pay avalanche", k=2)
    assert len(results) == 2
    assert results[0][0]["title"] in ["Debt A", "Debt B"]
