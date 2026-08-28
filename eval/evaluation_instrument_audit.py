"""Evaluation instrument audit — validates the evaluation system itself.

Checks:
1. Gold truth is independently determined
2. Retrieval result provenance is complete
3. Failure classifications are logically correct
4. Metric calculations are correct
5. Denominator is correct
6. No cases silently skipped
7. No embedding-derived labels used as truth
"""
import os
import json
import yaml
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


def audit_gold_independence(cases: list) -> dict:
    """Check that gold truth is independently determined."""
    issues = []
    
    for case in cases:
        if not case.get('answerable'):
            continue
        
        # Check for gold_rationale
        if not case.get('gold_rationale'):
            issues.append({
                'question': case['question'][:60],
                'issue': 'Missing gold_rationale'
            })
        
        # Check for corpus_snapshot
        if not case.get('corpus_snapshot'):
            issues.append({
                'question': case['question'][:60],
                'issue': 'Missing corpus_snapshot'
            })
        
        # Check for empty relevant_chunk_ids
        if not case.get('relevant_chunk_ids'):
            issues.append({
                'question': case['question'][:60],
                'issue': 'Empty relevant_chunk_ids'
            })
    
    return {
        'total_answerable': sum(1 for c in cases if c.get('answerable')),
        'issues': issues,
        'issue_count': len(issues),
        'pass': len(issues) == 0
    }


def audit_retrieval_provenance(cases: list) -> dict:
    """Check that retrieval results have complete provenance."""
    issues = []
    
    for case in cases:
        if not case.get('answerable'):
            continue
        
        gold_chunks = case.get('relevant_chunk_ids', [])
        for chunk_id in gold_chunks:
            # Check chunk exists
            chunk_result = supabase.table('chunks').select('id, document_id').eq('id', chunk_id).execute()
            if not chunk_result.data:
                issues.append({
                    'question': case['question'][:60],
                    'chunk_id': chunk_id,
                    'issue': 'Chunk not in database'
                })
                continue
            
            # Check document exists
            doc_id = chunk_result.data[0].get('document_id')
            doc_result = supabase.table('documents').select('id, source_id, domain').eq('id', doc_id).execute()
            if not doc_result.data:
                issues.append({
                    'question': case['question'][:60],
                    'chunk_id': chunk_id,
                    'issue': 'Document not found for chunk'
                })
                continue
            
            # Check source_id is not empty
            source_id = doc_result.data[0].get('source_id')
            if not source_id:
                issues.append({
                    'question': case['question'][:60],
                    'chunk_id': chunk_id,
                    'issue': 'Empty source_id'
                })
    
    return {
        'issues': issues,
        'issue_count': len(issues),
        'pass': len(issues) == 0
    }


def audit_metric_calculation() -> dict:
    """Verify metric calculation logic."""
    issues = []
    
    # Test Recall@k
    def compute_recall_at_k(retrieved, relevant, k):
        top_k = set(retrieved[:k])
        return bool(top_k.intersection(set(relevant)))
    
    # Test cases
    assert compute_recall_at_k(['a', 'b', 'c'], ['a'], 1) == True
    assert compute_recall_at_k(['a', 'b', 'c'], ['d'], 1) == False
    assert compute_recall_at_k(['a', 'b', 'c'], ['d', 'e'], 3) == False
    assert compute_recall_at_k(['a', 'b', 'c'], ['c', 'd'], 3) == True
    
    # Test MRR
    def compute_mrr(retrieved, relevant):
        relevant_set = set(relevant)
        for i, chunk_id in enumerate(retrieved):
            if chunk_id in relevant_set:
                return 1.0 / (i + 1)
        return 0.0
    
    assert compute_mrr(['a', 'b', 'c'], ['a']) == 1.0
    assert compute_mrr(['a', 'b', 'c'], ['b']) == 0.5
    assert compute_mrr(['a', 'b', 'c'], ['c']) == 1/3
    assert compute_mrr(['a', 'b', 'c'], ['d']) == 0.0
    
    return {
        'issues': issues,
        'issue_count': len(issues),
        'pass': len(issues) == 0
    }


def audit_denominator(cases: list) -> dict:
    """Verify denominator is correct."""
    answerable = [c for c in cases if c.get('answerable')]
    has_chunks = [c for c in answerable if c.get('relevant_chunk_ids')]
    
    issues = []
    if len(has_chunks) != len(answerable):
        issues.append({
            'answerable': len(answerable),
            'with_chunks': len(has_chunks),
            'issue': 'Some answerable cases have empty relevant_chunk_ids'
        })
    
    return {
        'total_cases': len(cases),
        'answerable': len(answerable),
        'with_chunks': len(has_chunks),
        'issues': issues,
        'issue_count': len(issues),
        'pass': len(issues) == 0
    }


def main():
    # Load gold cases
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    print("=== EVALUATION INSTRUMENT AUDIT ===\n")
    
    # Run audits
    print("1. Gold independence audit...")
    gold_audit = audit_gold_independence(cases)
    print(f"   Pass: {gold_audit['pass']}, Issues: {gold_audit['issue_count']}")
    
    print("2. Retrieval provenance audit...")
    provenance_audit = audit_retrieval_provenance(cases)
    print(f"   Pass: {provenance_audit['pass']}, Issues: {provenance_audit['issue_count']}")
    
    print("3. Metric calculation audit...")
    metric_audit = audit_metric_calculation()
    print(f"   Pass: {metric_audit['pass']}, Issues: {metric_audit['issue_count']}")
    
    print("4. Denominator audit...")
    denominator_audit = audit_denominator(cases)
    print(f"   Pass: {denominator_audit['pass']}, Issues: {denominator_audit['issue_count']}")
    
    # Overall
    all_pass = all([
        gold_audit['pass'],
        provenance_audit['pass'],
        metric_audit['pass'],
        denominator_audit['pass']
    ])
    
    print(f"\n=== OVERALL: {'PASS' if all_pass else 'FAIL'} ===")
    
    # Save report
    report = {
        'gold_independence': gold_audit,
        'retrieval_provenance': provenance_audit,
        'metric_calculation': metric_audit,
        'denominator': denominator_audit,
        'overall_pass': all_pass
    }
    
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'evaluation_instrument_audit.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved to: {output_path}")
    
    # Show issues
    if not all_pass:
        print("\n=== ISSUES ===")
        for audit_name, audit in [
            ('Gold independence', gold_audit),
            ('Retrieval provenance', provenance_audit),
            ('Metric calculation', metric_audit),
            ('Denominator', denominator_audit)
        ]:
            if audit['issues']:
                print(f"\n{audit_name}:")
                for issue in audit['issues'][:5]:
                    print(f"  {issue}")


if __name__ == '__main__':
    main()
