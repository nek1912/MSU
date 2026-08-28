import sys
sys.path.insert(0, "backend")
from dotenv import load_dotenv
load_dotenv("backend/.env", override=True)
from supabase import create_client
from app.config import get_settings
from app.providers.embeddings import get_embedding_provider
from app.domains import get_anchor_store
from app.hybrid_retrieval import retrieve_hybrid
from app.providers.reranker import JinaReranker

s = get_settings()
sb = create_client(s.supabase_url, s.supabase_service_key)
p = get_embedding_provider()
store = get_anchor_store()

for q in [
    "What is the Actuarial Premium Rate payable by farmer under PMFBY?",
    "Computerization of PACS project software and PMU roles",
    "How to open a Jan Dhan account under NSFI?",
]:
    emb = p.embed_texts([q], task="retrieval.query")[0]
    dom, _ = store.classify(q, emb)
    pool = retrieve_hybrid(sb, emb, q, dom, None, k=25)
    before = [c.chunk_id for c in pool[:6]]
    rr = JinaReranker()
    reranked = rr.rerank(q, [{"chunk_id": c.chunk_id, "content": c.content} for c in pool], top_n=6)
    after = [r["chunk_id"] for r in reranked]
    print(f"\nQ: {q}")
    print(f"  domain={dom} pool={len(pool)}")
    print(f"  reranker returned: {len(reranked)} chunks")
    print(f"  top before rerank: page={pool[0].page} sec={pool[0].section!r}")
    print(f"  top after rerank:  page={[c for c in pool if c.chunk_id==after[0]][0].page} "
          f"sec={[c for c in pool if c.chunk_id==after[0]][0].section!r}")
    print(f"  reorder changed top-1: {before[0] != after[0]}")
