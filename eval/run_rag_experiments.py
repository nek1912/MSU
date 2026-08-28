"""RAG benchmark experiments — compare all configurations.

Experiments:
E0: Current dense
E1: Dense + lexical
E2: Dense + lexical + RRF
E3: Dense + local reranker
E4: Dense + lexical + RRF + local reranker
"""
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)
from supabase import create_client
from app.providers.embeddings import get_embedding_provider
from eval.multi_stage_retrieval import dense_retrieval, lexical_retrieval, hybrid_retrieval
from eval.local_reranker import local_rerank

PROJECT_ROOT = Path(__file__).parent.parent
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_KEY']
supabase = create_client(url, key)
provider = get_embedding_provider()


def evaluate_experiment(name, get_results_fn, answerable, top_k=5):
    """Evaluate a retrieval experiment."""
    start_time = time.time()
    
    recall_1 = recall_3 = recall_5 = recall_10 = mrr_sum = 0
    
    for case in answerable:
        gold_chunks = case.get('relevant_chunk_ids', [])
        if not gold_chunks:
            continue
        
        query = case['question']
        domain = case.get('expected_domain')
        state = case.get('expected_state')
        
        results = get_results_fn(query, domain, state)
        result_ids = [r['chunk_id'] for r in results]
        
        # Recall@k
        if any(gid in result_ids[:1] for gid in gold_chunks):
            recall_1 += 1
        if any(gid in result_ids[:3] for gid in gold_chunks):
            recall_3 += 1
        if any(gid in result_ids[:5] for gid in gold_chunks):
            recall_5 += 1
        if any(gid in result_ids[:10] for gid in gold_chunks):
            recall_10 += 1
        
        # MRR
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
        'recall_at_10': recall_10 / n,
        'mrr': mrr_sum / n,
        'duration': elapsed,
    }


def run_experiments():
    """Run all benchmark experiments."""
    import yaml
    
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    answerable = [c for c in cases if c.get('answerable')]
    
    print('=== RAG BENCHMARK EXPERIMENTS ===')
    print(f'Testing {len(answerable)} cases')
    print()
    
    # E0: Current dense
    print('E0: Dense top-20 -> top-5...')
    results_e0 = evaluate_experiment(
        'E0: Dense',
        lambda q, d, s: dense_retrieval(q, d, s, 20)[:5],
        answerable
    )
    
    # E1: Dense + lexical
    print('E1: Dense + lexical top-20 -> top-5...')
    def dense_lexical(q, d, s):
        dense = dense_retrieval(q, d, s, 20)
        lexical = lexical_retrieval(q, d, s, 20)
        # Simple union for now
        all_ids = list(dict.fromkeys([r['chunk_id'] for r in dense] + [r['chunk_id'] for r in lexical]))
        # Get full data for first 5 unique
        results = []
        seen = set()
        for r in dense + lexical:
            if r['chunk_id'] not in seen and len(results) < 5:
                results.append(r)
                seen.add(r['chunk_id'])
        return results
    results_e1 = evaluate_experiment('E1: Dense+Lexical', dense_lexical, answerable)
    
    # E2: Dense + lexical + RRF
    print('E2: Dense + lexical + RRF top-20 -> top-5...')
    def dense_lexical_rrf(q, d, s):
        return hybrid_retrieval(q, d, s, 20)[:5]
    results_e2 = evaluate_experiment('E2: Dense+Lexical+RRF', dense_lexical_rrf, answerable)
    
    # E3: Dense + local reranker
    print('E3: Dense top-20 -> local reranker -> top-5...')
    def dense_reranked(q, d, s):
        candidates = dense_retrieval(q, d, s, 20)
        return local_rerank(q, candidates, 5)
    results_e3 = evaluate_experiment('E3: Dense+Rerank', dense_reranked, answerable)
    
    # E4: Dense + lexical + RRF + local reranker
    print('E4: Dense + lexical + RRF -> local reranker -> top-5...')
    def full_pipeline(q, d, s):
        candidates = hybrid_retrieval(q, d, s, 20)
        return local_rerank(q, candidates, 5)
    results_e4 = evaluate_experiment('E4: Full Pipeline', full_pipeline, answerable)
    
    # Print results
    print()
    print('=== EXPERIMENT RESULTS ===')
    print()
    
    print('Experiment    Recall@1  Recall@3  Recall@5  Recall@10 MRR       Time')
    print('-' * 75)
    
    for r in [results_e0, results_e1, results_e2, results_e3, results_e4]:
        print('{:<13} {:<9.3f} {:<9.3f} {:<9.3f} {:<9.3f} {:<9.3f} {:<9.1f}'.format(
            r['name'], r['recall_at_1'], r['recall_at_3'], r['recall_at_5'], 
            r['recall_at_10'], r['mrr'], r['duration']))
    
    print()
    print('=== THRESHOLD CHECK ===')
    print()
    
    # Minimum thresholds
    min_thresholds = {'recall_at_1': 0.40, 'recall_at_3': 0.60, 'recall_at_5': 0.80, 'mrr': 0.50}
    
    # Near-production targets
    target_thresholds = {'recall_at_1': 0.80, 'recall_at_3': 0.90, 'recall_at_5': 0.95, 'mrr': 0.90}
    
    for r in [results_e0, results_e1, results_e2, results_e3, results_e4]:
        min_pass = all(r[m] >= t for m, t in min_thresholds.items())
        target_pass = all(r[m] >= t for m, t in target_thresholds.items())
        
        if target_pass:
            status = 'TARGET'
        elif min_pass:
            status = 'MIN'
        else:
            status = 'FAIL'
        
        print(r['name'] + ': ' + status)
    
    # Save results
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'rag_ablation_report.json'
    with open(output_path, 'w') as f:
        json.dump([results_e0, results_e1, results_e2, results_e3, results_e4], f, indent=2)
    
    print()
    print('Results saved to:', output_path)
    
    return [results_e0, results_e1, results_e2, results_e3, results_e4]


if __name__ == '__main__':
    run_experiments()
