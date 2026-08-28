"""Retrieval validation: failure analysis (step 3), page/citation accuracy
(step 4), metadata filters (step 5), domain taxonomy (step 6).

Mirrors production retrieval (query embeddings use retrieval.query).
"""
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "backend" / ".env", override=True)

from supabase import create_client
from app.config import get_settings
from app.providers.embeddings import get_embedding_provider
from app.domains import get_anchor_store

s = get_settings()
sb = create_client(s.supabase_url, s.supabase_service_key)
provider = get_embedding_provider()
store = get_anchor_store()

K = 10


def q_emb(q):
    return provider.embed_texts([q], task="retrieval.query")[0]


def retrieve(query, domain, state=None, k=K):
    rows = sb.rpc("match_chunks", {
        "query_embedding": q_emb(query),
        "match_domain": domain if domain != "out_of_scope" else None,
        "match_state": state,
        "match_count": k,
    }).execute().data or []
    return rows


def classify(q):
    return store.classify(q, q_emb(q))


# ---- Step 3: failure analysis ------------------------------------------------
def step3():
    cases = yaml_cases()
    misses = []
    for c in cases:
        if not c.get("answerable"):
            continue
        q = c["question"]
        domain, _ = classify(q)
        gold = set(c.get("relevant_chunk_ids", []))
        rows = retrieve(q, domain)
        ids = [r["chunk_id"] for r in rows]
        for k in (1, 3, 5):
            if not set(ids[:k]).intersection(gold):
                if k == 5:  # only record the top-5 miss
                    misses.append((c, domain, rows, gold))
                break
    print("\n=== STEP 3: FAILURE ANALYSIS (recall@5 misses) ===")
    print(f"answerable cases: {sum(1 for c in cases if c.get('answerable'))}, "
          f"misses@5: {len(misses)}")
    for c, domain, rows, gold in misses:
        print(f"\nQUERY: {c['question']}")
        print(f"  expected_domain={c.get('expected_domain')} predicted={domain}")
        # gold chunk detail
        g = sb.table("chunks").select("page, section, heading_path, content, token_count").eq("id", list(gold)[0]).execute().data
        if g:
            g0 = g[0]
            print(f"  GOLD chunk: page={g0.get('page')} section={g0.get('section')!r} "
                  f"tokens={g0.get('token_count')}")
            print(f"    text: {g0.get('content', '')[:120]!r}")
        print("  TOP-5 RETRIEVED:")
        for i, r in enumerate(rows[:5], 1):
            print(f"   {i}. sim={r['similarity']:.3f} page={r['page']} "
                  f"sec={r['section']!r} | {r['content'][:90]!r}")
        # classify failure type
        gold_page = g[0].get("page") if g else None
        top_pages = [r["page"] for r in rows[:5]]
        if gold_page and gold_page not in top_pages:
            print(f"  -> LIKELY CAUSE: semantic/rank mismatch (gold page {gold_page} "
                  f"not in top-5 pages {top_pages}); fine chunking buries the answer")
    return misses


# ---- Step 4: page / citation accuracy ---------------------------------------
def step4():
    print("\n=== STEP 4: PAGE / CITATION ACCURACY ===")
    docs = sb.table("documents").select("id, source_id, title").execute().data
    sample = []
    problems = 0
    for d in docs:
        chunks = sb.table("chunks").select("id, page_start, page_end, heading_path, section, content, metadata").eq("document_id", d["id"]).execute().data or []
        if not chunks:
            continue
        maxpage = max((c.get("page_end") or c.get("page_start") or 0) for c in chunks)
        for c in chunks[:5]:
            ps = c.get("page_start")
            pe = c.get("page_end")
            ok = (ps and 1 <= ps <= maxpage) and (pe is None or pe >= ps)
            if not ok:
                problems += 1
            sf = (c.get("metadata") or {}).get("source_file", "")
            sample.append((d["source_id"], ps, pe, maxpage, c.get("heading_path"),
                           (c.get("content") or "")[:50], sf))
    for s_id, ps, pe, mx, hp, txt, sf in sample[:25]:
        print(f"  {s_id[:30]:30} page {ps}-{pe} (max {mx}) hp={hp!r} sf={sf!r} | {txt!r}")
    print(f"  Sampled {len(sample)} chunks; structural page problems: {problems}")
    # Known anchor check: PMFBY premium -> section 13.1, page 47
    rows = retrieve("Actuarial Premium Rate payable by farmer PMFBY", "pmfby")
    if rows:
        print(f"  PMFBY premium query -> top chunk page={rows[0]['page']} "
              f"sec={rows[0]['section']!r} (expect ~page 47, 'Variation in Premium Rate')")


# ---- Step 5: metadata filters ------------------------------------------------
def step5():
    print("\n=== STEP 5: METADATA FILTERS (no cross-domain contamination) ===")
    tests = [
        ("PMFBY premium rate", "pmfby", None),
        ("PACS model byelaws membership", "pacs_governance", None),
        ("computerization of PACS project Gujarat", "pacs_computerization", "gujarat"),
        ("Jan Dhan account NSFI", "financial_inclusion", None),
    ]
    for q, exp_domain, state in tests:
        domain, _ = classify(q)
        rows = retrieve(q, domain, state, k=10)
        domains = Counter(r["domain"] for r in rows)
        contaminated = [r for r in rows if r["domain"] != domain]
        print(f"  Q={q!r} pred={domain} exp={exp_domain} -> domains={dict(domains)} "
              f"contamination={len(contaminated)}")
        if domain != exp_domain:
            print(f"    !! domain mismatch (predicted {domain}, expected {exp_domain})")


# ---- Step 6: domain taxonomy ------------------------------------------------
def step6():
    print("\n=== STEP 6: DOMAIN TAXONOMY (anchor classification) ===")
    probes = {
        "pacs_governance": "What are the model byelaws for a PACS society?",
        "pacs_computerization": "Computerization of PACS project guidelines",
        "financial_inclusion": "How to open a Jan Dhan account under NSFI",
        "pmfby": "PMFBY crop insurance premium and claim process",
        "agriculture": "Kisan Credit Card interest subvention",
        "grievance": "How do I file a grievance against the cooperative",
        "schemes": "Government scheme for dairy cooperative subsidy",
    }
    for exp, q in probes.items():
        domain, score = classify(q)
        flag = "" if domain == exp else "  <-- MISMATCH"
        print(f"  exp={exp:22} pred={domain:22} score={score:.2f}  Q={q!r}{flag}")


def yaml_cases():
    import yaml
    return yaml.safe_load((PROJECT_ROOT / "eval" / "gold_cases.yaml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    step3()
    step4()
    step5()
    step6()
