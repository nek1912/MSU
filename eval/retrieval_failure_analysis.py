"""Retrieval failure analysis — case-by-case diagnosis.

For every failed gold case, produce:
- Top 10 retrieved chunks with full provenance
- Failure classification
- Root cause

Provenance chain: chunk_id → document_id → source_id → domain/jurisdiction/state
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


def resolve_provenance(chunk_id: str) -> dict:
    """Resolve chunk_id → document_id → source_id → domain/jurisdiction/state."""
    # Get chunk with document_id
    chunk_result = supabase.table('chunks').select('id, document_id').eq('id', chunk_id).execute()
    if not chunk_result.data:
        return {'exists': False}
    
    doc_id = chunk_result.data[0].get('document_id')
    
    # Get document with source_id, domain, jurisdiction, state
    doc_result = supabase.table('documents').select('id, source_id, domain, jurisdiction, state').eq('id', doc_id).execute()
    if not doc_result.data:
        return {'exists': True, 'document_id': doc_id, 'doc_found': False}
    
    doc = doc_result.data[0]
    return {
        'exists': True,
        'document_id': doc_id,
        'doc_found': True,
        'source_id': doc.get('source_id', '?'),
        'domain': doc.get('domain', '?'),
        'jurisdiction': doc.get('jurisdiction', '?'),
        'state': doc.get('state'),
    }


def classify_failure(gold_chunks: list, retrieved: list, expected_domain: str,
                     expected_sources: list, expected_state: str | None) -> dict:
    """Classify failure type and root cause with proper provenance."""
    gold_set = set(gold_chunks)
    retrieved_ids = [r['chunk_id'] for r in retrieved]
    retrieved_set = set(retrieved_ids)
    overlap = gold_set & retrieved_set
    
    # Determine failure type
    if not gold_chunks:
        failure_type = 'NO_GOLD_CHUNKS'
    elif not overlap:
        failure_type = 'NO_OVERLAP'
    elif len(overlap) < len(gold_chunks):
        failure_type = 'PARTIAL_OVERLAP'
    else:
        failure_type = 'FULL_OVERLAP'
    
    # Determine root cause with proper provenance
    if failure_type == 'NO_GOLD_CHUNKS':
        root_cause = 'Gold set has no chunks for this case'
        return {'failure_type': failure_type, 'root_cause': root_cause}
    
    if failure_type == 'FULL_OVERLAP':
        return {'failure_type': failure_type, 'root_cause': 'SUCCESS'}
    
    # Check if gold chunks exist in DB
    gold_missing = []
    for gid in gold_chunks:
        prov = resolve_provenance(gid)
        if not prov.get('exists'):
            gold_missing.append(gid)
    
    if gold_missing:
        return {
            'failure_type': failure_type,
            'root_cause': 'GOLD_NOT_FOUND',
            'detail': f'Gold chunks not in DB: {gold_missing}'
        }
    
    # For NO_OVERLAP and PARTIAL_OVERLAP, analyze retrieved chunks
    if not retrieved:
        return {
            'failure_type': failure_type,
            'root_cause': 'NO_RETRIEVED_CHUNKS',
            'detail': 'Retrieval returned no chunks'
        }
    
    # Check domain mismatch in retrieved chunks
    retrieved_domains = set()
    for r in retrieved:
        prov = resolve_provenance(r['chunk_id'])
        if prov.get('doc_found'):
            retrieved_domains.add(prov.get('domain'))
    
    if expected_domain not in retrieved_domains and retrieved_domains:
        return {
            'failure_type': failure_type,
            'root_cause': 'DOMAIN_MISMATCH',
            'detail': f'Expected domain {expected_domain}, got {retrieved_domains}'
        }
    
    # Check source mismatch
    retrieved_sources = set()
    for r in retrieved:
        prov = resolve_provenance(r['chunk_id'])
        if prov.get('doc_found'):
            retrieved_sources.add(prov.get('source_id'))
    
    source_overlap = set(expected_sources) & retrieved_sources
    if not source_overlap and expected_sources:
        return {
            'failure_type': failure_type,
            'root_cause': 'SOURCE_MISMATCH',
            'detail': f'Expected sources {expected_sources}, got {retrieved_sources}'
        }
    
    # Check jurisdiction mismatch
    if expected_state:
        for r in retrieved:
            prov = resolve_provenance(r['chunk_id'])
            if prov.get('doc_found'):
                chunk_state = prov.get('state')
                chunk_jurisdiction = prov.get('jurisdiction')
                if chunk_jurisdiction == 'state' and chunk_state != expected_state:
                    return {
                        'failure_type': failure_type,
                        'root_cause': 'JURISDICTION_MISMATCH',
                        'detail': f'Expected state {expected_state}, got {chunk_state}'
                    }
    
    # Gold chunks exist but not retrieved — ranking issue
    if overlap:
        return {
            'failure_type': failure_type,
            'root_cause': 'PARTIAL_RETRIEVAL',
            'detail': f'{len(overlap)}/{len(gold_chunks)} gold chunks retrieved'
        }
    
    # No overlap — embedding ranking issue
    return {
        'failure_type': failure_type,
        'root_cause': 'EMBEDDING_RANKING',
        'detail': 'Gold chunks exist but not in top-k results'
    }


def analyze_case(case):
    """Analyze a single case for retrieval failure."""
    question = case['question']
    domain = case.get('expected_domain')
    sources = case.get('relevant_source_ids', [])
    state = case.get('expected_state')
    gold_chunks = case.get('relevant_chunk_ids', [])
    
    # Embed query
    embedding = provider.embed_texts([question])[0]
    
    # Retrieve
    result = supabase.rpc(
        'match_chunks',
        {
            'query_embedding': embedding,
            'match_domain': domain,
            'match_state': state,
            'match_count': 10,
        }
    ).execute()
    
    retrieved = []
    for r in (result.data or []):
        # Get domain directly from RPC response (provenance is in the response)
        retrieved.append({
            'chunk_id': r.get('chunk_id'),
            'document_id': r.get('document_id'),
            'domain': r.get('domain', '?'),
            'jurisdiction': r.get('jurisdiction', '?'),
            'state': r.get('state'),
            'similarity': r.get('similarity', 0),
            'page': r.get('page', 0),
            'section': r.get('section', ''),
        })
    
    # Classify failure
    classification = classify_failure(
        gold_chunks, retrieved, domain, sources, state
    )
    
    return {
        'question': question,
        'expected_domain': domain,
        'expected_sources': sources,
        'expected_state': state,
        'gold_chunks': gold_chunks,
        'retrieved': retrieved[:10],
        'overlap_count': len(set(gold_chunks) & set(r['chunk_id'] for r in retrieved)),
        'gold_count': len(gold_chunks),
        'failure_type': classification['failure_type'],
        'root_cause': classification['root_cause'],
        'detail': classification.get('detail', ''),
    }


def main():
    # Load gold cases
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    answerable = [c for c in cases if c.get('answerable')]
    print(f"Analyzing {len(answerable)} answerable cases...")
    
    results = []
    for i, case in enumerate(answerable):
        result = analyze_case(case)
        results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  Analyzed {i + 1}/{len(answerable)}")
    
    # Summary
    from collections import Counter
    failure_counts = Counter(r['failure_type'] for r in results)
    root_cause_counts = Counter(r['root_cause'] for r in results)
    
    print("\n=== FAILURE TYPE DISTRIBUTION ===")
    for ft, count in failure_counts.most_common():
        print(f"  {ft}: {count}")
    
    print("\n=== ROOT CAUSE DISTRIBUTION ===")
    for rc, count in root_cause_counts.most_common():
        print(f"  {rc}: {count}")
    
    # Save results
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'retrieval_case_analysis.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_path}")
    
    # Show failed cases
    failed = [r for r in results if r['failure_type'] != 'FULL_OVERLAP']
    print(f"\n=== FAILED CASES: {len(failed)}/{len(results)} ===")
    for r in failed[:10]:
        print(f"\nQ: {r['question'][:60]}...")
        print(f"  Expected domain: {r['expected_domain']}")
        print(f"  Expected sources: {r['expected_sources']}")
        print(f"  Gold chunks: {r['gold_count']}")
        print(f"  Overlap: {r['overlap_count']}")
        print(f"  Failure: {r['failure_type']}")
        print(f"  Root cause: {r['root_cause']}")
        if r.get('detail'):
            print(f"  Detail: {r['detail'][:80]}")


if __name__ == '__main__':
    main()
