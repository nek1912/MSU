import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)

from supabase import create_client
from app.providers.embeddings import get_embedding_provider

supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
embed_provider = get_embedding_provider()

def test_retrieval(query, expected_source, domain=None, k=6):
    query_vec = embed_provider.embed_texts([query])[0]
    result = supabase.rpc("match_chunks", {
        "query_embedding": query_vec,
        "match_domain": domain,
        "match_state": None,
        "match_count": k,
    }).execute()
    
    chunks = result.data or []
    retrieved_sources = [c.get("source_id", "") for c in chunks]
    retrieved_doc_ids = [c.get("document_id", "") for c in chunks]
    
    # Resolve document_id to source_id
    if retrieved_doc_ids:
        doc_resp = supabase.table("documents").select("id, source_id").in_("id", retrieved_doc_ids).execute()
        doc_map = {str(d["id"]): d.get("source_id", "") for d in (doc_resp.data or [])}
        retrieved_sources = [doc_map.get(did, "") for did in retrieved_doc_ids]
    
    hit = expected_source in retrieved_sources
    
    return {
        "query": query[:50],
        "expected": expected_source,
        "retrieved_sources": list(set(retrieved_sources)),
        "hit": hit,
    }

# Test cases
test_cases = [
    ("What are PACS membership rules?", "pacs_model_bylaws_2023", "pacs_governance"),
    ("How to enroll crops under PMFBY?", "pmfby_operational_guidelines", "pmfby"),
    ("Financial inclusion strategy", "nsfi_2025_30", "financial_inclusion"),
    ("PACS computerization scheme", "pacs_computerization_guidelines", "pacs_computerization"),
    ("Corrigendum to computerization guidelines", "pacs_computerization_corrigendum_2023_06_12", "pacs_computerization"),
]

print("SOURCE-LEVEL RETRIEVAL EVALUATION")
print("=" * 70)
hits = 0
for query, expected, domain in test_cases:
    result = test_retrieval(query, expected, domain)
    status = "HIT" if result["hit"] else "MISS"
    print(f"{status}: {result['query']}")
    print(f"  Expected: {result['expected']}")
    print(f"  Retrieved: {result['retrieved_sources']}")
    print()
    if result["hit"]:
        hits += 1

print(f"Recall@6 (source-level): {hits}/{len(test_cases)} = {hits/len(test_cases)*100:.1f}%")
