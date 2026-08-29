"""Demo: run the full pipeline with mocked providers."""
import json
import sys
import io
from unittest.mock import patch, MagicMock
from app.config import get_settings
import app.routes.chat as chat_route

# Fix Windows console encoding for Hindi/Gujarati output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class FakeStore:
    @staticmethod
    def classify(text, embedding):
        return "pmfby", 0.95


fake_chunks = [
    {
        "chunk_id": "aaaaaaaa-1111-2222-3333-444444444444",
        "stable_chunk_id": "pmfby-faq:p1:c0",
        "document_id": "dddd1111-2222-3333-4444-555555555555",
        "title": "PMFBY FAQ", "page": 1, "page_start": 1, "page_end": 1,
        "section": "Eligibility", "subsection": None, "clause": None,
        "content": "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas are eligible for coverage under PMFBY.",
        "similarity": 0.78,
        "source_url": "https://pmfby.gov.in/faq", "source_file": "pmfby.gov.in/faq",
        "domain": "pmfby", "jurisdiction": "central", "state": None,
    },
    {
        "chunk_id": "bbbbbbbb-5555-6666-7777-888888888888",
        "stable_chunk_id": "pmfby-guidelines:p4:c0",
        "document_id": "eeee1111-2222-3333-4444-555555555555",
        "title": "PMFBY Guidelines", "page": 4, "page_start": 4, "page_end": 4,
        "section": "Premium Rates", "subsection": None, "clause": None,
        "content": "Farmer pays 2% of sum insured for kharif, 1.5% for rabi, and 5% for commercial/horticultural crops.",
        "similarity": 0.65,
        "source_url": "https://pmfby.gov.in/guidelines",
        "source_file": "pmfby.gov.in/guidelines",
        "domain": "pmfby", "jurisdiction": "central", "state": None,
    },
]

with (
    patch.object(chat_route, "get_anchor_store", return_value=FakeStore()),
    patch.object(chat_route, "get_state", return_value=None),
    patch.object(chat_route, "touch_session", return_value=None),
    patch.object(chat_route, "get_supabase") as mock_supabase,
    patch("app.providers.embeddings.get_embedding_provider") as mock_emb,
    patch("app.llm_fallback.grounded_answer") as mock_llm,
):
    mock_prov = MagicMock()
    mock_prov.embed_texts.return_value = [[0.5] * 768]
    mock_emb.return_value = mock_prov
    # Mock supabase client — retrieve() calls supabase.rpc(...).execute().data
    mock_client = MagicMock()
    mock_client.rpc.return_value.execute.return_value.data = fake_chunks
    mock_supabase.return_value = mock_client
    mock_llm.return_value = (
        "PMFBY provides crop insurance to all farmers including sharecroppers "
        "and tenant farmers [chunk:aaaaaaaa]. Farmers pay 2% for kharif and "
        "1.5% for rabi crops [chunk:bbbbbbbb]."
    )

    get_settings.cache_clear()
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    questions = [
        ("en", "Who is eligible for PMFBY?"),
        ("hi", "पीएमएफबीवाई में कौन पात्र है?"),
        ("gu", "પીએમએફબીવાઈ માટે કોણ પાત્ર છે?"),
    ]

    for lang, q in questions:
        r = client.post("/chat", json={"question": q, "session_id": "demo", "language": lang})
        body = r.json()
        print(f"{'='*60}")
        print(f"  Language: {lang}  |  Domain: {body['domain']}")
        print(f"  Intent:   {body['intent']}  |  Entities: {body['entities']}")
        print(f"  Question: {q}")
        print(f"  Answer:   {body['answer']}")
        print(f"  Confidence: {body['confidence']} ({body['confidence_level']})")
        print(f"  Citations: {len(body['citations'])}  |  Abstained: {body['abstained']}")
        for c in body["citations"]:
            chunk_id = c.get("chunk_id", "?")
            title = c.get("title", "?")
            page = c.get("page", "?")
            url = c.get("url", "")
            print(f"    -> [{chunk_id}] {title}, p.{page}")
            if url:
                print(f"       {url}")
        print()
