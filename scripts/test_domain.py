import sys
sys.path.insert(0, ".")

from app.domains import get_anchor_store
from app.providers.embeddings import get_embedding_provider

provider = get_embedding_provider()
store = get_anchor_store()

queries = [
    "How does PMFBY crop insurance work?",
    "What is PACS?",
    "Tell me about cooperative societies",
    "What is the premium for PMFBY?",
]

for q in queries:
    emb = provider.embed_texts([q])[0]
    domain, score = store.classify(q, emb)
    print(f"  domain={domain:15s} score={score:.3f}  query={q[:50]}")
