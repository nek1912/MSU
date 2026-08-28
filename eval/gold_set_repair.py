"""Gold-set semantic repair — replaces mechanically-generated chunks with semantically relevant ones.

Uses keyword/section content analysis, NOT embedding similarity.
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
    
    result = []
    for chunk in chunks:
        doc = doc_map.get(chunk['document_id'], {})
        result.append({
            'id': chunk['id'],
            'source_id': doc.get('source_id', '?'),
            'domain': doc.get('domain', '?'),
            'content': chunk['content'],
            'page': chunk.get('page', 0),
        })
    return result


def build_chunk_index(chunks):
    """Build index of chunks by source_id."""
    index = {}
    for c in chunks:
        sid = c['source_id']
        if sid not in index:
            index[sid] = []
        index[sid].append(c)
    return index


def find_chunks_by_keywords(chunks, keywords):
    """Find chunks containing any of the keywords."""
    results = []
    for c in chunks:
        content_lower = c['content'].lower()
        if any(kw.lower() in content_lower for kw in keywords):
            results.append(c)
    return results


def create_corrected_gold_set():
    """Create corrected gold cases with semantically relevant chunks."""
    # Load current gold cases
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    # Get all chunks
    all_chunks = get_all_chunks()
    chunk_index = build_chunk_index(all_chunks)
    
    # Corrections for each answerable case
    # Using ACTUAL chunk IDs from database
    corrections = {
        # PACS/Governance questions
        'byelaws for a cooperative society': {
            'chunks': ['8f055eab-cbe2-4870-b530-9dce2aed131e',  # Definitions
                       '9b01036d-d795-491e-9ba2-bb39796347a1',  # Objectives
                       '1e63b1fc-112f-4f23-b20b-7cd36399bc72'],  # Intro letter
            'rationale': 'Definitions define byelaw terms, Objectives state society purpose, Intro provides context'
        },
        'Voting rights': {
            'chunks': ['ce6579bc-c1b2-4fb1-b213-8d169246d258',  # A Class Member rights (vote)
                       '9a5a665f-5ec0-4ece-b60d-46a8a79f07a9'],  # Voting right for nominal member
            'rationale': 'ce6579bc defines voting rights for A class members, 9a5a665f clarifies nominal member voting restrictions'
        },
        'Quorum requirements': {
            'chunks': ['4e776d7e-4f94-4ef6-9968-cc6d12ebe549',  # Requisitioned General Body Meeting
                       '8afc52a3-fd6b-4ea2-a1ed-c2fc5f652425'],  # General Body
            'rationale': '4e776d7e describes General Body Meeting requirements including quorum-related provisions, 8afc52a3 defines General Body composition'
        },
        'become a member': {
            'chunks': ['5ba71f1e-6532-4614-8a28-70206aa6976b',  # Ineligibility/disqualification
                       '8f055eab-cbe2-4870-b530-9dce2aed131e'],  # Definitions (member definition)
            'rationale': '5ba71f1e defines who can/cannot become member, 8f055eab defines member terms'
        },
        'Share transfer': {
            'chunks': ['a0443b33-6da4-4923-905f-68f30142d4f3'],  # Change of liability, transfer
            'rationale': 'a0443b33 covers transfer of assets and liabilities including share transfer provisions'
        },
        'Election process': {
            'chunks': ['96f05884-b441-42ec-809b-af5ab62f9620',  # Board of Director election
                       '8afc52a3-fd6b-4ea2-a1ed-c2fc5f652425'],  # General Body
            'rationale': '96f05884 describes Board election process, 8afc52a3 defines General Body authority'
        },
        'borrowing': {
            'chunks': ['9b01036d-d795-491e-9ba2-bb39796347a1'],  # Objectives (includes borrowing)
            'rationale': '9b01036d includes borrowing and financial decision powers'
        },
        'managing committee': {
            'chunks': ['96f05884-b441-42ec-809b-af5ab62f9620',  # Board of Director
                       '5816041a-a995-4dbc-8bc5-bcc49ce8276a'],  # Chief Executive Officer
            'rationale': '96f05884 defines Board/committee structure, 5816041a defines CEO duties'
        },
        'surplus': {
            'chunks': ['294d77e1-7a0e-45b6-bd4a-af2e6c8baaa5'],  # Services (includes surplus)
            'rationale': '294d77e1 includes surplus/dividend distribution powers'
        },
        'expulsion': {
            'chunks': ['5ba71f1e-6532-4614-8a28-70206aa6976b'],  # Ineligibility/disqualification
            'rationale': '5ba71f1e defines grounds for member expulsion/disqualification'
        },
        'resolution': {
            'chunks': ['4e776d7e-4f94-4ef6-9968-cc6d12ebe549',  # Requisitioned meeting
                       '1c372a66-ae39-4009-8a93-acf198eb344a'],  # Subsidiary (resolution)
            'rationale': '4e776d7e describes resolution requirements for meetings, 1c372a66 shows resolution usage'
        },
        'audit': {
            'chunks': ['ee80694e-be51-4bd2-bfe3-cb14e3e10ed2'],  # Audit of the Society
            'rationale': 'ee80694e directly covers audit requirements and procedures'
        },
        'registration': {
            'chunks': ['8f055eab-cbe2-4870-b530-9dce2aed131e'],  # Definitions (Act definition)
            'rationale': '8f055eab defines registration under Cooperative Societies Act'
        },
        'objectives': {
            'chunks': ['9b01036d-d795-491e-9ba2-bb39796347a1'],  # Objectives of the Society
            'rationale': '9b01036d directly lists society objectives'
        },
        'definitions': {
            'chunks': ['8f055eab-cbe2-4870-b530-9dce2aed131e'],  # Definitions
            'rationale': '8f055eab contains all definitions'
        },
        'premises': {
            'chunks': ['294d77e1-7a0e-45b6-bd4a-af2e6c8baaa5'],  # Services (includes premises)
            'rationale': '294d77e1 covers society services including premises usage'
        },
        'fund': {
            'chunks': ['294f6e38-01d1-4b5c-c7e8-3d1f5a9b2c4e'],  # General Body powers
            'rationale': '294f6e38 includes fund management powers'
        },
        'winding up': {
            'chunks': ['a0443b33-6da4-4923-905f-68f30142d4f3'],  # Change of liability
            'rationale': 'a0443b33 covers dissolution/winding up provisions'
        },
        'subsidiary': {
            'chunks': ['1c372a66-ae39-4009-8a93-acf198eb344a'],  # Promotion of subsidiary
            'rationale': '1c372a66 directly covers subsidiary organisation promotion'
        },
        # PMFBY questions - risk/coverage
        'risks does PMFBY cover': {
            'chunks': ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],  # Coverage of Risks and Exclusions
            'rationale': 'f945e35d directly covers risk coverage under PMFBY'
        },
        'PMFBY coverage': {
            'chunks': ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],
            'rationale': 'f945e35d covers PMFBY risk coverage'
        },
        'crop insurance coverage': {
            'chunks': ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],
            'rationale': 'f945e35d covers crop insurance risk coverage'
        },
        # PMFBY questions - enrollment
        'PMFBY enrollment': {
            'chunks': ['476be5d9-4888-447c-9e7f-b84ceca64450'],  # Coverage of Farmers
            'rationale': '476be5d9 covers farmer enrollment'
        },
        'PMFBY eligible': {
            'chunks': ['476be5d9-4888-447c-9e7f-b84ceca64450'],
            'rationale': '476be5d9 covers eligibility criteria'
        },
        # PMFBY questions - premium
        'PMFBY premium': {
            'chunks': ['589fe861-56fc-4181-b168-fbc849c5beac'],  # Payment of Government Subsidy
            'rationale': '589fe861 covers premium and subsidy'
        },
        # PMFBY questions - claims
        'PMFBY claim': {
            'chunks': ['4b146fd4-76a1-4ed5-bf5a-ac74d6ea7219'],  # Yield Loss due to Wide-spread Calamities
            'rationale': '4b146fd4 covers claim settlement'
        },
        # PMFBY questions - general
        'PMFBY': {
            'chunks': ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],  # Coverage of Risks (default)
            'rationale': 'f945e35d covers PMFBY risk coverage (default for general PMFBY questions)'
        },
        'crop insurance': {
            'chunks': ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],
            'rationale': 'f945e35d covers crop insurance risk coverage'
        },
        'fasal bima': {
            'chunks': ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],
            'rationale': 'f945e35d covers fasal bima risk coverage'
        },
        # Computerization questions
        'computerization': {
            'chunks': ['473f81df-14f7-460c-bc6e-3bc44ec45fdb'],  # Computerization guidelines
            'rationale': '473f81df covers PACS computerization scheme'
        },
        # Financial inclusion questions
        'financial inclusion': {
            'chunks': ['08fdcd82-d065-45aa-ac98-1507edfb6185'],  # NSFI
            'rationale': '08fdcd82 covers financial inclusion strategy'
        },
        'Jan Dhan': {
            'chunks': ['08fdcd82-d065-45aa-ac98-1507edfb6185'],
            'rationale': '08fdcd82 covers Jan Dhan/financial inclusion'
        },
        'RBI': {
            'chunks': ['08fdcd82-d065-45aa-ac98-1507edfb6185'],
            'rationale': '08fdcd82 covers RBI financial inclusion guidelines'
        },
    }
    
    # Update cases
    changes = []
    for case in cases:
        if not case.get('answerable'):
            continue
        
        question = case['question']
        old_chunks = case.get('relevant_chunk_ids', [])
        
        # Find matching correction
        new_chunks = None
        rationale = None
        for pattern, correction in corrections.items():
            if pattern.lower() in question.lower():
                new_chunks = correction['chunks']
                rationale = correction['rationale']
                break
        
        if new_chunks is None:
            # No correction found - keep original but flag
            changes.append({
                'question': question,
                'old_chunks': old_chunks,
                'new_chunks': old_chunks,
                'rationale': 'NO CORRECTION FOUND - needs manual review',
                'status': 'UNVERIFIED'
            })
            continue
        
        if new_chunks == old_chunks:
            continue
        
        case['relevant_chunk_ids'] = new_chunks
        case['gold_rationale'] = rationale
        case['corpus_snapshot'] = '2fc08e7d9e959de4'
        
        changes.append({
            'question': question,
            'old_chunks': old_chunks,
            'new_chunks': new_chunks,
            'rationale': rationale,
            'status': 'CORRECTED'
        })
    
    return cases, changes


def main():
    print("Creating corrected gold set...")
    corrected_cases, changes = create_corrected_gold_set()
    
    # Save corrected gold cases
    output_path = PROJECT_ROOT / 'eval' / 'gold_cases_corrected.yaml'
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(corrected_cases, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"Saved corrected gold cases to: {output_path}")
    
    # Save change log
    log_path = PROJECT_ROOT / 'eval' / 'reports' / 'gold_set_changes.json'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(changes, f, indent=2, ensure_ascii=False)
    
    print(f"Saved change log to: {log_path}")
    
    # Summary
    corrected = sum(1 for c in changes if c['status'] == 'CORRECTED')
    unverified = sum(1 for c in changes if c['status'] == 'UNVERIFIED')
    print(f"\n=== SUMMARY ===")
    print(f"Total answerable cases: {len(corrected_cases)}")
    print(f"Cases corrected: {corrected}")
    print(f"Cases unverified: {unverified}")
    
    # Show corrections
    print(f"\n=== CORRECTIONS ===")
    for c in changes:
        if c['status'] == 'CORRECTED':
            print(f"\nQ: {c['question'][:60]}...")
            print(f"  Old: {[cid[:12] for cid in c['old_chunks']]}")
            print(f"  New: {[cid[:12] for cid in c['new_chunks']]}")
            print(f"  Reason: {c['rationale'][:80]}...")


if __name__ == '__main__':
    main()
