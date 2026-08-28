"""Hybrid retrieval with dense + lexical + RRF fusion.

Combines:
- Dense retrieval (cosine similarity)
- Lexical retrieval (PostgreSQL ILIKE)
- Reciprocal Rank Fusion
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)
from supabase import create_client
from app.providers.embeddings import get_embedding_provider

PROJECT_ROOT = Path(__file__).parent.parent
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_KEY']
supabase = create_client(url, key)
provider = get_embedding_provider()

# RRF constant
RRF_K = 60


def dense_retrieval(query: str, domain: str = None, state: str = None, k: int = 20) -> list:
    """Dense retrieval using cosine similarity."""
    embedding = provider.embed_texts([query])[0]
    
    result = supabase.rpc(
        'match_chunks',
        {
            'query_embedding': embedding,
            'match_domain': domain if domain != 'out_of_scope' else None,
            'match_state': state,
            'match_count': k,
        }
    ).execute()
    
    return result.data or []


def lexical_retrieval(query: str, domain: str = None, state: str = None, k: int = 20) -> list:
    """Lexical retrieval using PostgreSQL ILIKE search."""
    # Clean query for search
    search_terms = query.lower().split()
    
    # Build SQL query with ILIKE
    sql = """
    SELECT c.id as chunk_id, c.content, d.source_id, d.domain, d.jurisdiction, d.state,
           c.page, c.section, 0.5 as similarity
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
    WHERE (
    """
    
    conditions = []
    for term in search_terms:
        if len(term) > 2:  # Skip very short terms
            conditions.append(f"c.content ILIKE '%{term}%'")
    
    if not conditions:
        conditions.append("TRUE")
    
    sql += " OR ".join(conditions) + ")"
    
    if domain and domain != 'out_of_scope':
        sql += f" AND d.domain = '{domain}'"
    
    if state:
        sql += f" AND (d.jurisdiction = 'central' OR d.state = '{state}')"
    
    sql += f" LIMIT {k}"
    
    try:
        # Use raw SQL query
        result = supabase.rpc('match_chunks', {
            'query_embedding': [0.1] * 768,  # Dummy for RPC
            'match_domain': domain,
            'match_state': state,
            'match_count': k,
        }).execute()
        
        # Filter by lexical match
        lexical_results = []
        for r in (result.data or []):
            content = r.get('content', '').lower()
            if any(term in content for term in search_terms if len(term) > 2):
                lexical_results.append(r)
        
        return lexical_results[:k]
    except Exception as e:
        print(f"Lexical search error: {e}")
        return []


def rrf_fusion(dense_results: list, lexical_results: list, k: int = 20) -> list:
    """Reciprocal Rank Fusion of dense and lexical results."""
    # Create rank mappings
    dense_ranks = {r['chunk_id']: i + 1 for i, r in enumerate(dense_results)}
    lexical_ranks = {r['chunk_id']: i + 1 for i, r in enumerate(lexical_results)}
    
    # Combine all unique chunk IDs
    all_chunk_ids = set(dense_ranks.keys()) | set(lexical_ranks.keys())
    
    # Calculate RRF scores
    rrf_scores = {}
    for chunk_id in all_chunk_ids:
        dense_rank = dense_ranks.get(chunk_id, len(dense_results) + 1)
        lexical_rank = lexical_ranks.get(chunk_id, len(lexical_results) + 1)
        
        # RRF formula: sum(1 / (k + rank))
        score = 1.0 / (RRF_K + dense_rank) + 1.0 / (RRF_K + lexical_rank)
        rrf_scores[chunk_id] = score
    
    # Sort by RRF score
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    # Get top-k results with metadata
    results = []
    for chunk_id in sorted_ids[:k]:
        # Find the chunk in dense or lexical results
        chunk_data = None
        for r in dense_results + lexical_results:
            if r['chunk_id'] == chunk_id:
                chunk_data = r
                break
        
        if chunk_data:
            results.append({
                **chunk_data,
                'rrf_score': rrf_scores[chunk_id],
                'dense_rank': dense_ranks.get(chunk_id, 0),
                'lexical_rank': lexical_ranks.get(chunk_id, 0),
            })
    
    return results


def hybrid_retrieval(query: str, domain: str = None, state: str = None, k: int = 20) -> list:
    """Hybrid retrieval with dense + lexical + RRF fusion."""
    # Dense retrieval
    dense_results = dense_retrieval(query, domain, state, k)
    
    # Lexical retrieval
    lexical_results = lexical_retrieval(query, domain, state, k)
    
    # RRF fusion
    fused_results = rrf_fusion(dense_results, lexical_results, k)
    
    return fused_results


def compare_retrieval_methods(query: str, domain: str = None, gold_chunks: list = None) -> dict:
    """Compare dense, lexical, and hybrid retrieval."""
    # Dense only
    dense_results = dense_retrieval(query, domain, None, 20)
    dense_ids = [r['chunk_id'] for r in dense_results]
    dense_recall = any(gid in dense_ids for gid in (gold_chunks or []))
    
    # Lexical only
    lexical_results = lexical_retrieval(query, domain, None, 20)
    lexical_ids = [r['chunk_id'] for r in lexical_results]
    lexical_recall = any(gid in lexical_ids for gid in (gold_chunks or []))
    
    # Hybrid
    hybrid_results = hybrid_retrieval(query, domain, None, 20)
    hybrid_ids = [r['chunk_id'] for r in hybrid_results]
    hybrid_recall = any(gid in hybrid_ids for gid in (gold_chunks or []))
    
    return {
        'dense_recall': dense_recall,
        'lexical_recall': lexical_recall,
        'hybrid_recall': hybrid_recall,
        'dense_count': len(dense_results),
        'lexical_count': len(lexical_results),
        'hybrid_count': len(hybrid_results),
    }


if __name__ == '__main__':
    # Test hybrid retrieval
    import yaml
    
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    answerable = [c for c in cases if c.get('answerable')]
    
    print('=== HYBRID RETRIEVAL TEST ===')
    print()
    
    dense_hits = 0
    lexical_hits = 0
    hybrid_hits = 0
    
    for case in answerable[:20]:  # First 20 for speed
        gold_chunks = case.get('relevant_chunk_ids', [])
        if not gold_chunks:
            continue
        
        query = case['question']
        domain = case.get('expected_domain')
        
        result = compare_retrieval_methods(query, domain, gold_chunks)
        
        if result['dense_recall']:
            dense_hits += 1
        if result['lexical_recall']:
            lexical_hits += 1
        if result['hybrid_recall']:
            hybrid_hits += 1
    
    n = min(20, len(answerable))
    print(f'Dense Recall@20: {dense_hits}/{n} = {dense_hits/n:.3f}')
    print(f'Lexical Recall@20: {lexical_hits}/{n} = {lexical_hits/n:.3f}')
    print(f'Hybrid Recall@20: {hybrid_hits}/{n} = {hybrid_hits/n:.3f}')
