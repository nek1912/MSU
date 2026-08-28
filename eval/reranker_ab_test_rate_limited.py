"""Reranker A/B test with proper rate limiting."""
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


def dense_retrieval(query, domain, state, k=20):
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


def evaluate_config(name, get_results_fn, answerable, top_k=5):
    start_time = time.time()
    recall_1 = recall_3 = recall_5 = mrr_sum = 0
    
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
        
        time.sleep(0.5)  # Rate limiting
    
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
    import yaml
    
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    answerable = [c for c in cases if c.get('answerable')]
    
    print('=== RETRIEVAL A/B TEST ===')
    print('Testing', len(answerable), 'cases with rate limiting')
    print()
    
    # A: Dense top-20 -> top-5
    print('Testing A: Dense top-20 -> top-5...')
    results_a = evaluate_config(
        'Dense',
        lambda q, d, s: dense_retrieval(q, d, s, 20)[:5],
        answerable
    )
    
    # B: Dense top-20 -> reranker -> top-5
    print('Testing B: Dense top-20 -> reranker -> top-5...')
    def dense_reranked(q, d, s):
        dense_results = dense_retrieval(q, d, s, 20)
        time.sleep(1)  # Rate limit for reranker
        return reranker.rerank(q, dense_results, 5)
    results_b = evaluate_config('Dense+Rerank', dense_reranked, answerable)
    
    # Print results
    print()
    print('=== RESULTS ===')
    print()
    
    print('Config          Recall@1   Recall@3   Recall@5   MRR        Time')
    print('-' * 65)
    
    for r in [results_a, results_b]:
        print('{:<15} {:<10.3f} {:<10.3f} {:<10.3f} {:<10.3f} {:<10.1f}'.format(
            r['name'], r['recall_at_1'], r['recall_at_3'], r['recall_at_5'], r['mrr'], r['duration']))
    
    print()
    print('=== THRESHOLD CHECK ===')
    print()
    
    thresholds = {'recall_at_1': 0.40, 'recall_at_3': 0.60, 'recall_at_5': 0.80, 'mrr': 0.50}
    
    for r in [results_a, results_b]:
        all_pass = all(r[m] >= t for m, t in thresholds.items())
        status = 'PASS' if all_pass else 'FAIL'
        print(r['name'] + ': ' + status)
    
    # Save results
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'reranker_ab_test.json'
    with open(output_path, 'w') as f:
        json.dump([results_a, results_b], f, indent=2)
    
    print()
    print('Results saved to:', output_path)
    
    return results_a, results_b


if __name__ == '__main__':
    run_ab_test()
