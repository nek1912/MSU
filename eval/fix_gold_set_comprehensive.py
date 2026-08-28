"""Comprehensive gold set semantic repair.

Based on semantic analysis of all 40 answerable cases.
"""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)

PROJECT_ROOT = Path(__file__).parent.parent


def fix_gold_set():
    """Fix all gold set semantic errors."""
    
    # Load current gold cases
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', encoding='utf-8') as f:
        cases = yaml.safe_load(f)
    
    # Correct mappings based on semantic analysis
    # Format: question_substring -> (correct_chunk_ids, rationale)
    corrections = {
        # PMFBY cases - many use wrong gold chunk f945e35d (Coverage of Risks)
        'risks does PMFBY cover': (
            ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],  # Coverage of Risks
            'CORRECT: Question asks about risks covered'
        ),
        'PMFBY coverage for horticultural': (
            ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],  # Coverage of Risks
            'CORRECT: Question asks about coverage'
        ),
        'PMFBY add-on coverage': (
            ['f945e35d-67b6-40bf-a1f0-a99a0a70dad6'],  # Coverage of Risks
            'CORRECT: Question asks about coverage options'
        ),
        'PMFBY premium rates': (
            ['589fe861-56fc-4181-b168-fbc849c5beac'],  # Payment of Government Subsidy
            'FIXED: Question asks about premium rates, not coverage'
        ),
        'eligible for PMFBY': (
            ['476be5d9-4888-447c-9e7f-b84ceca64450'],  # Coverage of Farmers
            'FIXED: Question asks about eligibility, not coverage'
        ),
        'PMFBY enrollment deadline': (
            ['298610f8-b096-4f5d-a04b-07bdf5512edc'],  # Seasonality Discipline
            'FIXED: Question asks about deadlines, not coverage'
        ),
        'Gujarat PMFBY crop insurance portal': (
            ['eaceebf6-7634-45f7-9b84-4c91e8781e68'],  # Technology
            'FIXED: Question asks about portal/technology'
        ),
        'PMFBY use of technology': (
            ['eaceebf6-7634-45f7-9b84-4c91e8781e68'],  # Technology
            'FIXED: Question asks about technology'
        ),
        'Gujarat PMFBY farmer enrollment': (
            ['b41d4760-5c9a-4267-bb5a-1c13132f2b4b'],  # Universal Coverage
            'FIXED: Question asks about enrollment'
        ),
        'PMFBY coverage for perennial': (
            ['b41d4760-5c9a-4267-bb5a-1c13132f2b4b'],  # Universal Coverage
            'FIXED: Question asks about coverage for specific crops'
        ),
        'PMFBY insurance company empanelment': (
            ['c22d5cfe-b343-4cf3-9840-b89c12fdd239'],  # Empanelment Criteria
            'FIXED: Question asks about empanelment'
        ),
        'PMFBY coverage area definition': (
            ['b41d4760-5c9a-4267-bb5a-1c13132f2b4b'],  # Universal Coverage
            'FIXED: Question asks about coverage area'
        ),
        'PMFBY private crop insurance': (
            ['c22d5cfe-b343-4cf3-9840-b89c12fdd239'],  # Empanelment Criteria
            'FIXED: Question asks about private companies'
        ),
        'PMFBY restructured weather': (
            ['428e8d1e-bbdc-4b88-b153-cca086a9c6c1'],  # Weather-based scheme
            'FIXED: Question asks about weather-based scheme'
        ),
        'Gujarat PMFBY district-wise premium': (
            ['589fe861-56fc-4181-b168-fbc849c5beac'],  # Payment of Government Subsidy
            'FIXED: Question asks about premium rates'
        ),
        'PMFBY indemnity level': (
            ['2b187ae2-6280-43b6-b430-f265f95f8847'],  # State/UT notification
            'FIXED: Question asks about indemnity calculation'
        ),
        'PMFBY exclusion period': (
            ['6618395a-5379-48d1-a628-00107450ee81'],  # Prevented sowing
            'FIXED: Question asks about exclusion period'
        ),
        'PMFBY preventive sowing': (
            ['6618395a-5379-48d1-a628-00107450ee81'],  # Prevented sowing
            'FIXED: Question asks about preventive sowing'
        ),
        'PMFBY claim amount': (
            ['4b146fd4-76a1-4ed5-bf5a-ac74d6ea7219'],  # Yield Loss
            'CORRECT: Question asks about claim amount'
        ),
        'PMFBY notification date': (
            ['298610f8-b096-4f5d-a04b-07bdf5512edc'],  # Seasonality Discipline
            'FIXED: Question asks about notification dates'
        ),
        'PMFBY premium subsidy through PACS': (
            ['589fe861-56fc-4181-b168-fbc849c5beac'],  # Payment of Government Subsidy
            'CORRECT: Question asks about premium subsidy'
        ),
        'PMFBY premium subsidy by state': (
            ['589fe861-56fc-4181-b168-fbc849c5beac'],  # Payment of Government Subsidy
            'CORRECT: Question asks about premium subsidy'
        ),
    }
    
    # Apply corrections
    fixed = 0
    for case in cases:
        if not case.get('answerable'):
            continue
        
        question = case['question']
        for pattern, (chunk_ids, rationale) in corrections.items():
            if pattern.lower() in question.lower():
                old_chunks = case.get('relevant_chunk_ids', [])
                if old_chunks != chunk_ids:
                    case['relevant_chunk_ids'] = chunk_ids
                    case['gold_rationale'] = rationale
                    case['corpus_snapshot'] = '2fc08e7d9e959de4'
                    fixed += 1
                    print(f'Fixed: {question[:50]}...')
                    print(f'  Old: {old_chunks}')
                    print(f'  New: {chunk_ids}')
                    print(f'  Reason: {rationale}')
                break
    
    # Save
    with open(PROJECT_ROOT / 'eval' / 'gold_cases.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(cases, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f'\nFixed {fixed} cases')
    return fixed


if __name__ == '__main__':
    fix_gold_set()
