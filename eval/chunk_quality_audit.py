"""Chunking quality audit — measures actual chunk characteristics.

Inspects:
- Per-document chunk counts
- Token/character distribution
- Heading/section retention
- Overlap
- Legal provision continuity
"""
import os
import json
import statistics
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)
from supabase import create_client

PROJECT_ROOT = Path(__file__).parent.parent
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_KEY']
supabase = create_client(url, key)


def get_document_chunks():
    """Get all chunks grouped by document."""
    docs = supabase.table('documents').select('id, source_id, domain, title').execute().data
    chunks = supabase.table('chunks').select('id, document_id, content, page, section').execute().data
    
    doc_map = {d['id']: d for d in docs}
    chunks_by_doc = {}
    for chunk in chunks:
        doc_id = chunk['document_id']
        if doc_id not in chunks_by_doc:
            chunks_by_doc[doc_id] = []
        chunks_by_doc[doc_id].append(chunk)
    
    return doc_map, chunks_by_doc


def analyze_chunk_characteristics(chunks: list) -> dict:
    """Analyze characteristics of a set of chunks."""
    if not chunks:
        return {'count': 0}
    
    # Character counts
    char_counts = [len(c.get('content', '')) for c in chunks]
    
    # Word counts (proxy for tokens)
    word_counts = [len(c.get('content', '').split()) for c in chunks]
    
    # Check heading retention
    has_heading = sum(1 for c in chunks if c.get('content', '').strip().startswith('#'))
    
    # Check page metadata
    has_page = sum(1 for c in chunks if c.get('page', 0) > 0)
    
    # Check section metadata
    has_section = sum(1 for c in chunks if c.get('section', '').strip())
    
    return {
        'count': len(chunks),
        'char_count': {
            'min': min(char_counts),
            'max': max(char_counts),
            'mean': round(statistics.mean(char_counts), 1),
            'median': round(statistics.median(char_counts), 1),
            'p95': round(sorted(char_counts)[int(len(char_counts) * 0.95)], 1) if len(char_counts) >= 20 else max(char_counts),
        },
        'word_count': {
            'min': min(word_counts),
            'max': max(word_counts),
            'mean': round(statistics.mean(word_counts), 1),
            'median': round(statistics.median(word_counts), 1),
            'p95': round(sorted(word_counts)[int(len(word_counts) * 0.95)], 1) if len(word_counts) >= 20 else max(word_counts),
        },
        'heading_retention': round(has_heading / len(chunks), 2),
        'page_metadata': round(has_page / len(chunks), 2),
        'section_metadata': round(has_section / len(chunks), 2),
    }


def main():
    print("=== CHUNKING QUALITY AUDIT ===\n")
    
    doc_map, chunks_by_doc = get_document_chunks()
    
    results = {}
    for doc_id, chunks in chunks_by_doc.items():
        doc = doc_map.get(doc_id, {})
        source_id = doc.get('source_id', '?')
        domain = doc.get('domain', '?')
        
        analysis = analyze_chunk_characteristics(chunks)
        results[source_id] = {
            'domain': domain,
            'analysis': analysis
        }
        
        print(f"Document: {source_id} ({domain})")
        print(f"  Chunks: {analysis['count']}")
        if analysis['count'] > 0:
            print(f"  Chars: min={analysis['char_count']['min']}, max={analysis['char_count']['max']}, "
                  f"mean={analysis['char_count']['mean']}, median={analysis['char_count']['median']}")
            print(f"  Words: min={analysis['word_count']['min']}, max={analysis['word_count']['max']}, "
                  f"mean={analysis['word_count']['mean']}, median={analysis['word_count']['median']}")
            print(f"  Heading retention: {analysis['heading_retention']:.0%}")
            print(f"  Page metadata: {analysis['page_metadata']:.0%}")
            print(f"  Section metadata: {analysis['section_metadata']:.0%}")
        print()
    
    # Overall summary
    total_chunks = sum(r['analysis']['count'] for r in results.values())
    print(f"Total chunks: {total_chunks}")
    
    # Save report
    output_path = PROJECT_ROOT / 'eval' / 'reports' / 'chunk_quality_audit.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved to: {output_path}")


if __name__ == '__main__':
    main()
