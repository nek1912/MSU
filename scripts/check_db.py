import sys; sys.path.insert(0, 'backend')
from supabase import create_client
from app.config import get_settings
from app.providers.embeddings import get_embedding_provider
s = get_settings()
sb = create_client(s.supabase_url, s.supabase_service_key)
docs = sb.table('documents').select('id, title, domain').execute().data
chunks = sb.table('chunks').select('id').execute().data
print(f"Documents: {len(docs)}, Chunks: {len(chunks)}")
for d in docs:
    print(f"  [{d['domain']}] {d['title']}")

# Test retrieval
provider = get_embedding_provider()
emb = provider.embed_texts(["How does PMFBY crop insurance work?"])[0]
result = sb.rpc('match_chunks', {
    'query_embedding': emb,
    'match_domain': 'pmfby',
    'match_state': None,
    'match_count': 3
}).execute()
print()
if result.data:
    print(f"match_chunks returned {len(result.data)} rows")
    print(f"  columns: {sorted(result.data[0].keys())}")
    for r in result.data:
        print(f"  sim={r.get('similarity',0):.3f} title={r.get('title','?')[:50]}")
else:
    print("match_chunks returned 0 rows")
