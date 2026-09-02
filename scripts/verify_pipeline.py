import sys
sys.path.insert(0, "backend")
from dotenv import load_dotenv
load_dotenv("backend/.env", override=True)
from supabase import create_client
from app.config import get_settings
from app.providers.embeddings import get_embedding_provider
from app.domains import get_anchor_store
from app.hybrid_retrieval import retrieve_hybrid
from app.evidence_gate import evidence_gate_v2
from app.contracts import RetrievalCandidate

s = get_settings()
sb = create_client(s.supabase_url, s.supabase_service_key)
p = get_embedding_provider()
store = get_anchor_store()

def run(q):
    v = p.embed_texts([q], task="retrieval.query")[0]
    domain, score = store.classify(q, v)
    print("Q: %s" % q)
    print("  domain=%s score=%.3f" % (domain, score))
    if domain == "out_of_scope":
        print("  -> out_of_scope (general answer)\n"); return
    chunks = retrieve_hybrid(sb, v, q, domain, None)
    cands = [RetrievalCandidate(chunk_id=c.chunk_id, document_id="", source_id="",
                                dense_score=c.similarity,
                                filter_decisions={"domain": True, "active": True,
                                                   "is_central": c.jurisdiction == "central",
                                                   "state_match": c.jurisdiction == "central" or c.state == None})
              for c in chunks]
    abstained, reason, band = evidence_gate_v2(cands, expected_domain=domain, expected_state=None)
    print("  retrieved=%d abstained=%s reason=%s band=%s" % (len(chunks), abstained, reason, band))
    if not abstained and chunks:
        print("  top: page=%s sec=%r | %r" % (chunks[0].page, chunks[0].section[:40], chunks[0].content[:90]))
    print()

run("What is the premium rate payable by farmer under PMFBY?")
run("PMFBY mein kisan ko kitna premium dena hota hai?")
run("What are the model byelaws for PACS membership eligibility?")
run("How to open a Jan Dhan account under NSFI?")
run("What is the capital of France?")
