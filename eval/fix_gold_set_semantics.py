"""Fix gold set semantic errors — replace incorrectly assigned chunks.

The current gold set uses the same chunk (f945e35d - Coverage of Risks) for
many PMFBY queries, but this chunk is not the most relevant for most queries.
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


def fix_gold_set():
    """Fix gold set semantic errors."""
    # Load current gold cases
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    # Correct mappings based on semantic analysis
    # Format: question_substring -> correct_chunk_ids
    corrections = {
        # PMFBY queries - need topic-specific chunks
        'eligible for PMFBY': ['476be5d9-4888-447c-9e7f-b84ceca64450'],  # Coverage of Farmers
        'PMFBY enrollment deadline': ['298610f8-b096-4f5d-a04b-07bdf5512edc'],  # Seasonality Discipline
        'Gujarat PMFBY crop insurance portal': ['eaceebf6-7634-45f7-9b84-4c91e8781e68'],  # Digital Technology
        'PMFBY preventive sowing': ['c91e68a2-edb1-4e9b-8594-1187d8e8df4c'],  # Prevented sowing
        'PMFBY use of technology': ['eaceebf6-7634-45f7-9b84-4c91e8781e68'],  # Digital Technology
        'Gujarat PMFBY farmer enrollment': ['b41d4760-5c91-4e7a-b5c3-8d2f6a9e1b3c'],  # Universal Coverage
        'PMFBY coverage for perennial crops': ['b41d4760-5c91-4e7a-b5c3-8d2f6a9e1b3c'],  # Universal Coverage
        'PMFBY insurance company empanelment': ['c22d5cfe-b34e-4a8d-b5c3-8d2f6a9e1b3c'],  # Empanelment Criteria
        'PMFBY premium rates': ['589fe861-56fc-4181-b168-fbc849c5beac'],  # Payment of Government Subsidy
        'PMFBY claim amount': ['4b146fd4-76a1-4ed5-bf5a-ac74d6ea7219'],  # Yield Loss
        'PMFBY notification date': ['298610f8-b096-4f5d-a04b-07bdf5512edc'],  # Seasonality Discipline
        'PMFBY premium subsidy through PACS': ['589fe861-56fc-4181-b168-fbc849c5beac'],  # Payment of Government Subsidy
    }
    
    # Apply corrections
    fixed = 0
    for case in cases:
        if not case.get('answerable'):
            continue
        
        question = case['question']
        for pattern, chunk_ids in corrections.items():
            if pattern.lower() in question.lower():
                old_chunks = case.get('relevant_chunk_ids', [])
                if old_chunks != chunk_ids:
                    case['relevant_chunk_ids'] = chunk_ids
                    case['gold_rationale'] = f'Semantically corrected: {pattern}'
                    case['corpus_snapshot'] = '2fc08e7d9e959de4'
                    fixed += 1
                    print(f'Fixed: {question[:50]}...')
                    print(f'  Old: {old_chunks}')
                    print(f'  New: {chunk_ids}')
                break
    
    # Save
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(cases, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f'\nFixed {fixed} cases')
    return fixed


if __name__ == '__main__':
    fix_gold_set()
