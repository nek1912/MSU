"""Reranker A/B test — compare retrieval configurations.

Tests:
A: Dense top-20 → top-5
B: Hybrid top-20 → top-5
C: Dense top-20 → reranker → top-5
D: Hybrid top-20 → reranker → top-5
"""
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)
from supabase import create_client
from app.providers.embeddings import get_embedding_provider
from app.providers.reranker import get_reranker

PROJECT_ROOT = Path(__file__).parent.parent
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_KEY']
supabase = create_client(url, key)
provider = get_embedding_provider()
reranker = get_reranker()


def dense_retrieval(query: str, domain: str = None, state: str = None, k: int = 20) -> list:
    """Dense retrieval."""
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


def hybrid_retrieval(query: str, domain: str = None, state: str = None, k: int = 20) -> list:
    """Hybrid retrieval (dense + lexical + RRF)."""
    # For now, just use dense (lexical needs proper implementation)
    return dense_retrieval(query, domain, state, k)


def rerank_results(query: str, results: list, top_n: int = 5) -> list:
    """Rerank results using Jina reranker."""
    return reranker.rerank(query, results, top_n)


def evaluate_configuration(name: str, get_results_fn, answerable: list, top_k: int = 5) -> dict:
    """Evaluate a retrieval configuration."""
    start_time = time.time()
    
    recall_1 = 0
    recall_3 = 0
    recall_5 = 0
    mrr_sum = 0
    
    for case in answerable:
        gold_chunks = case.get('relevant_chunk_ids', [])
        if not gold_chunks:
            continue
        
        query = case['question']
        domain = case.get('expected_domain')
        state = case.get('expected_state')
        
        results = get_results_fn(query, domain, state)
        result_ids = [r['chunk_id'] for r in results[:top_k]]
        
        if any(gid in result_ids[:1] for gid in gold_chunks):
            recall_1 += 1
        if any(gid in result_ids[:3] for gid in gold_chunks):
            recall_3 += 1
        if any(gid in result_ids[:5] for gid in gold_chunks):
            recall_5 += 1
        
        for i, chunk_id in enumerate(result_ids):
            if chunk_id in gold_chunks:
                mrr_sum += 1.0 / (i + 1)
                break
    
    elapsed = time.time() - start_time
    n = len(answerable)
    
    return {
        'name': name,
        'recall_at_1': recall_1 / n,
        'recall_at_3': recall_3 / n,
        'recall_at_5': recall_5 / n,
        'mrr': mrr_sum / n,
        'duration': elapsed,
    }


def run_ab_test():
    """Run A/B test for retrieval configurations."""
    import yaml
    
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    answerable = [c for c in cases if c.get('answerable')]
    
    print('=== RETRIEVAL A/B TEST ===')
    print(f'Testing {len(answerable)} cases')
    print()
    
    # Configuration A: Dense top-20 -> top-5
    print('Testing A: Dense top-20 -> top-5...')
    results_a = evaluate_configuration(
        'Dense',
        lambda q, d, s: dense_retrieval(q, d, s, 20)[:5],
        answerable
    )
    
    # Configuration B: Hybrid top-20 -> top-5
    print('Testing B: Hybrid top-20 -> top-5...')
    results_b = evaluate_configuration(
        'Hybrid',
        lambda q, d, s: hybrid_retrieval(q, d, s, 20)[:5],
        answerable
    )
    
    # Configuration C: Dense top-20 -> reranker -> top-5
    print('Testing C: Dense top-20 -> reranker -> top-5...')
    def dense_reranked(q, d, s):
        dense_results = dense_retrieval(q, d, s, 20)
        return rerank_results(q, dense_results, 5)
    results_c = evaluate_configuration('Dense+Rerank', dense_reranked, answerable)
    
    # Configuration D: Hybrid top-20 -> reranker -> top-5
    print('Testing D: Hybrid top-20 -> reranker -> top-5...')
    def hybrid_reranked(q, d, s):
        hybrid_results = hybrid_retrieval(q, d, s, 20)
        return rerank_results(q, hybrid_results, 5)
    results_d = evaluate_configuration('Hybrid+Rerank', hybrid_reranked, answerable)
    
    # Print results
    print()
    print('=== RESULTS ===')
    print()
    
    configs = [results_a, results_b, results_c, results_d]
    
    print(f'{"Config":<15} {"Recall@1":<10} {"Recall@3":<10} {"Recall@5":<10} {"MRR":<10} {"Time":<10}')
    print('-' * 65)
    
    for r in configs:
        print(f'{r["name"]:<15} {r["recall_at_1"]:<10.3f} {r["recall_at_3"]:<10.3f} {r["recall_at_5"]:<10.3f} {r["mrr"]:<10.3f} {r["duration"]:<10.1f}')
    
    print()
    print('=== THRESHOLD CHECK ===')
    print()
    
    thresholds = {'recall_at_1': 0.40, 'recall_at_3': 0.60, 'recall_at_5': 0.80, 'mrr': 0.50}
    
    for r in configs:
        all_pass = True
        for metric, threshold in thresholds.items():
            if r[metric] < threshold:
                all_pass = False
                break
        status = 'PASS' if all_pass else 'FAIL'
        print(f'{r["name"]}: {status}')
    
    # Save results
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'reranker_ab_test.json'
    with open(output_path, 'w') as f:
        json.dump(configs, f, indent=2)
    
    print(f'\nResults saved to: {output_path}')
    
    return configs


if __name__ == '__main__':
    run_ab_test()
