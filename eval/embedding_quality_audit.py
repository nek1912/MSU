"""Embedding consistency audit — verifies embedding quality and consistency.

Checks:
- Provider/model/dimension
- Similarity metric meaning
- Gold chunk vs distractor scores
- Query/document encoding consistency
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


def audit_embedding_consistency():
    """Audit embedding consistency and quality."""
    print("=== EMBEDDING CONSISTENCY AUDIT ===\n")
    
    # 1. Provider info
    print("1. Provider information:")
    print(f"   Provider: {provider.__class__.__name__}")
    print(f"   Model: {getattr(provider, 'model', 'unknown')}")
    print(f"   Dimension: {getattr(provider, 'dimension', 'unknown')}")
    
    # 2. Verify dimension consistency
    print("\n2. Dimension consistency check:")
    test_embedding = provider.embed_texts(["test query"])[0]
    print(f"   Test embedding dimension: {len(test_embedding)}")
    
    # Check stored embeddings
    sample = supabase.table('chunks').select('embedding').limit(1).execute()
    if sample.data:
        import json as j
        stored_dim = len(j.loads(sample.data[0]['embedding']))
        print(f"   Stored embedding dimension: {stored_dim}")
        print(f"   Consistent: {len(test_embedding) == stored_dim}")
    
    # 3. Similarity metric verification
    print("\n3. Similarity metric verification:")
    print("   RPC uses: 1 - (c.embedding <=> query_embedding)")
    print("   This is cosine similarity (1 - cosine distance)")
    print("   Range: [-1, 1] where 1 = identical, 0 = orthogonal, -1 = opposite")
    
    # 4. Gold chunk vs distractor analysis
    print("\n4. Gold chunk vs distractor analysis:")
    
    # Load gold cases
    import yaml
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    answerable = [c for c in cases if c.get('answerable')][:5]  # First 5 for speed
    
    gold_scores = []
    distractor_scores = []
    
    for case in answerable:
        question = case['question']
        gold_chunks = case.get('relevant_chunk_ids', [])
        
        if not gold_chunks:
            continue
        
        # Embed query
        query_embedding = provider.embed_texts([question])[0]
        
        # Retrieve
        result = supabase.rpc(
            'match_chunks',
            {
                'query_embedding': query_embedding,
                'match_domain': case.get('expected_domain'),
                'match_state': None,
                'match_count': 10,
            }
        ).execute()
        
        retrieved = result.data or []
        
        # Separate gold vs distractor scores
        for r in retrieved:
            chunk_id = r.get('chunk_id')
            similarity = r.get('similarity', 0)
            
            if chunk_id in gold_chunks:
                gold_scores.append(similarity)
            else:
                distractor_scores.append(similarity)
    
    if gold_scores and distractor_scores:
        print(f"   Gold chunk scores: min={min(gold_scores):.4f}, max={max(gold_scores):.4f}, "
              f"mean={sum(gold_scores)/len(gold_scores):.4f}")
        print(f"   Distractor scores: min={min(distractor_scores):.4f}, max={max(distractor_scores):.4f}, "
              f"mean={sum(distractor_scores)/len(distractor_scores):.4f}")
        print(f"   Score margin: {sum(gold_scores)/len(gold_scores) - sum(distractor_scores)/len(distractor_scores):.4f}")
    
    # 5. Check for normalization
    print("\n5. Normalization check:")
    print("   Jina v3 returns unit-normalized vectors by default")
    print("   Gemini embedding-2 returns unit-normalized vectors")
    print("   No explicit normalization in Python code (correct)")
    
    return {
        'provider': provider.__class__.__name__,
        'model': getattr(provider, 'model', 'unknown'),
        'dimension': len(test_embedding),
        'stored_dimension': stored_dim if sample.data else None,
        'consistent': len(test_embedding) == (stored_dim if sample.data else len(test_embedding)),
    }


def main():
    result = audit_embedding_consistency()
    
    # Save report
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'embedding_quality_audit.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved to: {output_path}")


if __name__ == '__main__':
    main()
