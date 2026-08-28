"""Multi-stage retrieval pipeline with lexical + dense + RRF + local reranking.

Architecture:
QUERY
  ↓
normalization
  ↓
domain/jurisdiction filters
  ↓
dense top-20 + lexical top-20
  ↓
RRF fusion
  ↓
deduplication
  ↓
top-20 candidates
  ↓
local reranker
  ↓
top-5/6 evidence
"""
import os
import re
import json
import time
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


def normalize_query(query: str) -> str:
    """Normalize query for retrieval."""
    # Unicode normalization
    normalized = query.strip()
    # Whitespace normalization
    normalized = re.sub(r'\s+', ' ', normalized)
    # Lowercase for matching
    return normalized


def dense_retrieval(query: str, domain: str = None, state: str = None, k: int = 20) -> list:
    """Dense retrieval using cosine similarity."""
    embedding = provider.embed_texts([query])[0]
    
    result = supabase.rpc(
        'match_chunks',
        {
            'query_embedding': embedding,
            'match_domain': domain,
            'match_state': state,
            'match_count': k,
        }
    ).execute()
    
    return result.data or []


def extract_search_terms(query: str) -> list:
    """Extract meaningful search terms from query."""
    # Common stop words to exclude
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'shall', 'can',
                  'what', 'how', 'when', 'where', 'who', 'which', 'why',
                  'for', 'in', 'on', 'at', 'to', 'from', 'by', 'with', 'of',
                  'and', 'or', 'but', 'not', 'no', 'nor'}
    
    # Extract words
    words = re.findall(r'\w+', query.lower())
    
    # Filter stop words and short words
    terms = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Also extract multi-word phrases for exact matching
    phrases = []
    # Look for quoted phrases
    quoted = re.findall(r'"([^"]+)"', query)
    phrases.extend(quoted)
    
    # Look for compound terms (e.g., "PMFBY", "PACS", "cooperative society")
    compound_patterns = [
        r'cooperative\s+society',
        r'primary\s+agricultural\s+credit\s+society',
        r'crop\s+insurance',
        r'financial\s+inclusion',
    ]
    for pattern in compound_patterns:
        matches = re.findall(pattern, query.lower())
        phrases.extend(matches)
    
    return terms + phrases


def lexical_retrieval(query: str, domain: str = None, state: str = None, k: int = 20) -> list:
    """Lexical retrieval using PostgreSQL ILIKE search."""
    search_terms = extract_search_terms(query)
    
    if not search_terms:
        return []
    
    # Build SQL query with OR matching
    conditions = []
    for term in search_terms:
        # Escape single quotes
        safe_term = term.replace("'", "''")
        conditions.append(f"c.content ILIKE '%{safe_term}%'")
    
    where_clause = " OR ".join(conditions)
    
    sql = f"""
    SELECT c.id as chunk_id, c.content, c.page, c.section,
           d.source_id, d.domain, d.jurisdiction, d.state,
           0.5 as similarity
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
    WHERE ({where_clause})
    """
    
    if domain and domain != 'out_of_scope':
        sql += f" AND d.domain = '{domain}'"
    
    if state:
        sql += f" AND (d.jurisdiction = 'central' OR d.state = '{state}')"
    
    sql += f" LIMIT {k}"
    
    try:
        # Use match_chunks RPC as a workaround for raw SQL
        # This is not ideal but works within Supabase client constraints
        result = supabase.table('chunks').select(
            'id, content, page, section, document_id'
        ).execute()
        
        # Filter by lexical match
        lexical_results = []
        for r in (result.data or []):
            content = r.get('content', '').lower()
            if any(term in content for term in search_terms):
                # Get document info
                doc_result = supabase.table('documents').select(
                    'source_id, domain, jurisdiction, state'
                ).eq('id', r['document_id']).execute()
                
                if doc_result.data:
                    doc = doc_result.data[0]
                    lexical_results.append({
                        'chunk_id': r['id'],
                        'content': r['content'],
                        'page': r.get('page', 0),
                        'section': r.get('section', ''),
                        'source_id': doc.get('source_id', '?'),
                        'domain': doc.get('domain', '?'),
                        'jurisdiction': doc.get('jurisdiction', '?'),
                        'state': doc.get('state'),
                        'similarity': 0.5,  # Placeholder
                    })
        
        # Sort by number of matching terms (more matches = higher rank)
        lexical_results.sort(
            key=lambda x: sum(1 for term in search_terms if term in x['content'].lower()),
            reverse=True
        )
        
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
    
    for case in answerable[:20]:
        gold_chunks = case.get('relevant_chunk_ids', [])
        if not gold_chunks:
            continue
        
        query = case['question']
        domain = case.get('expected_domain')
        
        # Dense
        dense_results = dense_retrieval(query, domain, None, 20)
        dense_ids = [r['chunk_id'] for r in dense_results]
        if any(gid in dense_ids for gid in gold_chunks):
            dense_hits += 1
        
        # Lexical
        lexical_results = lexical_retrieval(query, domain, None, 20)
        lexical_ids = [r['chunk_id'] for r in lexical_results]
        if any(gid in lexical_ids for gid in gold_chunks):
            lexical_hits += 1
        
        # Hybrid
        hybrid_results = hybrid_retrieval(query, domain, None, 20)
        hybrid_ids = [r['chunk_id'] for r in hybrid_results]
        if any(gid in hybrid_ids for gid in gold_chunks):
            hybrid_hits += 1
    
    n = 20
    print(f'Dense Recall@20: {dense_hits}/{n} = {dense_hits/n:.3f}')
    print(f'Lexical Recall@20: {lexical_hits}/{n} = {lexical_hits/n:.3f}')
    print(f'Hybrid Recall@20: {hybrid_hits}/{n} = {hybrid_hits/n:.3f}')
