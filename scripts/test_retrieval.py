"""Quick end-to-end test of the backend."""
import sys
sys.path.insert(0, ".")

from supabase import create_client
from app.config import get_settings
from app.providers.embeddings import get_embedding_provider
from app.domains import get_anchor_store
from app.retrieval import retrieve, evidence_gate

s = get_settings()
sb = create_client(s.supabase_url, s.supabase_service_key)
provider = get_embedding_provider()

# Check data
docs = sb.table("documents").select("id, title, domain").execute().data
chunks_count = sb.table("chunks").select("id").execute().data
print(f"Documents: {len(docs)}, Chunks: {len(chunks_count)}")

# Test embedding + retrieval
query = "How does PMFBY crop insurance work?"
emb = provider.embed_texts([query])[0]
print(f"\nQuery: {query}")
print(f"Embedding dim: {len(emb)}")

# Domain classification
domain, score = get_anchor_store().classify(query, emb)
print(f"Domain: {domain} (score={score:.3f})")

# Retrieve
results = retrieve(sb, emb, domain, None)
print(f"Retrieved {len(results)} chunks")
for c in results:
    print(f"  sim={c.similarity:.3f} [{c.domain}] {c.title[:50]}")

# Evidence gate
gate = evidence_gate(results, expected_domain=domain)
print(f"\nEvidence gate: abstained={gate.abstained}, confidence={gate.confidence}, reason={gate.reason}")
