import sys
sys.path.insert(0, "backend")
from dotenv import load_dotenv
load_dotenv("backend/.env", override=True)
from supabase import create_client
from app.config import get_settings
from app.providers.embeddings import get_embedding_provider

s = get_settings()
sb = create_client(s.supabase_url, s.supabase_service_key)
p = get_embedding_provider()

docs = sb.table("documents").select("source_id, domain, jurisdiction, state, title").execute().data
ch = sb.table("chunks").select("id", count="exact").execute()
print("DOCUMENTS:", len(docs), "| TOTAL CHUNKS:", ch.count)
for d in docs:
    print("  -", d["domain"], "|", d["jurisdiction"], "|", d["state"], "|", d["source_id"])

print()

def show(q, domain):
    v = p.embed_texts([q], task="retrieval.query")[0]
    rows = sb.rpc("match_chunks", {
        "query_embedding": v, "match_domain": domain,
        "match_state": None, "match_count": 3,
    }).execute().data or []
    print("Q[%s]: %s" % (domain, q))
    for r in rows:
        print("   sim=%.3f page=%s sec=%r | %r" % (
            r["similarity"], r["page"], r["section"][:40], r["content"][:90]))
    print()

show("What is the premium rate payable by farmer under PMFBY?", "pmfby")
show("PMFBY mein kisan ko kitna premium dena hota hai?", "pmfby")
show("How to open a Jan Dhan account?", "financial_inclusion")
show("What are the model byelaws for PACS membership?", "pacs_governance")
