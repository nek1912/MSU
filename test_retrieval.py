import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)

from supabase import create_client
from app.providers.embeddings import get_embedding_provider

supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
embed_provider = get_embedding_provider()

def test_retrieval(query, domain=None, state=None, k=5):
    print(f'\nQuery: "{query}"')
    print(f'Domain: {domain}, State: {state}')
    print('-' * 60)
    
    # Embed the query
    query_vec = embed_provider.embed_texts([query])[0]
    
    # Call match_chunks RPC
    result = supabase.rpc("match_chunks", {
        "query_embedding": query_vec,
        "match_domain": domain,
        "match_state": state,
        "match_count": k,
    }).execute()
    
    chunks = result.data or []
    print(f'Retrieved {len(chunks)} chunks:\n')
    
    for i, chunk in enumerate(chunks[:3], 1):
        print(f'{i}. [{chunk["domain"]}] {chunk["title"]}')
        print(f'   Similarity: {chunk["similarity"]:.3f}')
        print(f'   Content: {chunk["content"][:150]}...')
        print()

# Test queries
test_retrieval("What are PACS membership rules?", domain="pacs_governance")
test_retrieval("How to enroll crops under PMFBY?", domain="pmfby")
test_retrieval("Financial inclusion strategy", domain="financial_inclusion")
test_retrieval("PACS computerization scheme", domain="pacs_computerization")
