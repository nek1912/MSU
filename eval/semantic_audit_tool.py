"""Semantic gold-set repair — finds correct chunks for each answerable case.

Uses keyword/section search (NOT embedding similarity) to find candidate chunks.
"""
import os
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)
from supabase import create_client

PROJECT_ROOT = Path(__file__).parent.parent
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_KEY']
supabase = create_client(url, key)


def get_all_chunks():
    """Get all chunks with document info."""
    chunks = supabase.table('chunks').select('id, document_id, content, page, section').execute().data
    docs = supabase.table('documents').select('id, source_id, domain, title').execute().data
    doc_map = {d['id']: d for d in docs}
    
    for chunk in chunks:
        doc = doc_map.get(chunk['document_id'], {})
        chunk['source_id'] = doc.get('source_id', '?')
        chunk['domain'] = doc.get('domain', '?')
        chunk['doc_title'] = doc.get('title', '?')
    
    return chunks


def keyword_search(chunks, keywords, source_filter=None):
    """Find chunks containing keywords."""
    results = []
    for chunk in chunks:
        if source_filter and chunk['source_id'] != source_filter:
            continue
        content_lower = chunk['content'].lower()
        if any(kw.lower() in content_lower for kw in keywords):
            results.append(chunk)
    return results


def audit_case(case, all_chunks):
    """Audit a single case and find correct gold chunks."""
    question = case['question']
    domain = case.get('expected_domain', '?')
    sources = case.get('relevant_source_ids', [])
    
    # Generate search terms from question
    question_lower = question.lower()
    
    # Topic-specific keyword mapping
    topic_keywords = {
        'byelaw': ['byelaw', 'bye-law', 'byelaws', 'bye-laws'],
        'voting': ['voting', 'vote', 'ballot', 'voting right'],
        'quorum': ['quorum'],
        'membership': ['member', 'membership', 'admission', 'nomination'],
        'share transfer': ['share transfer', 'transfer of share', 'transfer share'],
        'election': ['election', 'elect', 'election process'],
        'borrowing': ['borrow', 'borrowing', 'loan', 'debt'],
        'managing committee': ['managing committee', 'board of director', 'committee'],
        'surplus': ['surplus', 'dividend', 'profit'],
        'expulsion': ['expel', 'expulsion', 'removal of member'],
        'resolution': ['resolution', 'resolution passed'],
        'audit': ['audit', 'auditor'],
        'registration': ['registration', 'register', 'registered'],
        'objectives': ['objectives', 'objective'],
        'definitions': ['definitions', 'definition'],
        'premises': ['premises', 'office', 'building'],
        'fund': ['fund', 'reserve fund'],
        'winding up': ['winding up', 'dissolution'],
        'subsidiary': ['subsidiary'],
        'pmfby': ['pmfby', 'crop insurance', 'fasal bima', 'claim', 'premium', 'enrolment', 'eligibility'],
        'computerization': ['computerization', 'digitization', 'digital', 'ncip'],
        'financial inclusion': ['financial inclusion', 'jan dhan', 'pmjdy', 'rupay', 'deposit insurance'],
        'cooperative society': ['cooperative society', 'co-operative society'],
        'primary agricultural': ['primary agricultural credit society', 'pacs'],
    }
    
    # Find matching topics
    matched_topics = []
    for topic, keywords in topic_keywords.items():
        if any(kw in question_lower for kw in keywords):
            matched_topics.append(topic)
    
    # If no specific topic matched, use general cooperative keywords
    if not matched_topics:
        matched_topics = ['cooperative society']
    
    # Search for candidate chunks
    candidates = []
    for topic in matched_topics:
        keywords = topic_keywords.get(topic, [topic])
        found = keyword_search(all_chunks, keywords, source_filter=sources[0] if sources else None)
        candidates.extend(found)
    
    # Deduplicate
    seen_ids = set()
    unique_candidates = []
    for c in candidates:
        if c['id'] not in seen_ids:
            seen_ids.add(c['id'])
            unique_candidates.append(c)
    
    return {
        'question': question,
        'domain': domain,
        'sources': sources,
        'matched_topics': matched_topics,
        'candidates': unique_candidates[:10],  # Top 10 candidates
    }


def main():
    print("Loading chunks...")
    all_chunks = get_all_chunks()
    print(f"  {len(all_chunks)} chunks loaded")
    
    # Load gold cases
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    answerable = [c for c in cases if c.get('answerable')]
    print(f"  {len(answerable)} answerable cases")
    
    # Audit each case
    audit_results = []
    for i, case in enumerate(answerable):
        result = audit_case(case, all_chunks)
        audit_results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  Audited {i + 1}/{len(answerable)} cases")
    
    # Save audit results
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'semantic_audit_results.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nAudit results saved to: {output_path}")
    
    # Print summary
    print("\n=== AUDIT SUMMARY ===")
    for r in audit_results[:5]:
        print(f"\nQ: {r['question'][:60]}...")
        print(f"  Topics: {r['matched_topics']}")
        print(f"  Candidates: {len(r['candidates'])}")
        for c in r['candidates'][:3]:
            content = c['content'][:80].replace('\n', ' ')
            print(f"    {c['id'][:12]} ({c['source_id']}): {content}...")


if __name__ == '__main__':
    main()
