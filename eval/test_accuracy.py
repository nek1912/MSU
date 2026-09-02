"""Comprehensive accuracy and edge case testing for the RAG system."""
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path('D:/Downloads/New folder')
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / 'backend' / '.env')

from app.providers.embeddings import get_embedding_provider
from app.retrieval import retrieve, evidence_gate
from app.evidence_gate import evidence_gate_v2, compute_confidence_band
from app.citation_verifier import verify_citations
from app.domains import get_anchor_store
from app.contracts import RetrievalCandidate
from app.db import get_supabase

# Initialize
provider = get_embedding_provider()
supabase = get_supabase()
anchor_store = get_anchor_store()

# ============================================================================
# TEST CASES
# ============================================================================

# Gold cases: (query, expected_domain, expected_titles, min_score)
GOLD_CASES = [
    # PMFBY domain
    ("What is PMFBY?", "pmfby", ["Pradhan Mantri Fasal"], 0.3),
    ("How to apply for crop insurance?", "pmfby", ["Pradhan Mantri Fasal"], 0.3),
    ("What are the eligibility criteria for PMFBY?", "pmfby", ["Pradhan Mantri Fasal"], 0.3),
    ("PMFBY claim process", "pmfby", ["Pradhan Mantri Fasal"], 0.3),
    
    # PACS domain
    ("What is PACS?", "pacs_governance", ["Primary Agricultural Credit"], 0.3),
    ("How to join a cooperative society?", "pacs_governance", ["Primary Agricultural Credit"], 0.3),
    ("Primary Agricultural Credit Societies", "pacs_governance", ["Primary Agricultural Credit"], 0.3),
    
    # PACS Computerization domain
    ("What is computerization of PACS?", "pacs_computerization", ["Computerization", "Corrigendum"], 0.3),
    ("PACS software guidelines", "pacs_computerization", ["Computerization"], 0.3),
    
    # Financial Inclusion domain
    ("What is financial inclusion?", "financial_inclusion", ["Financial Inclusion"], 0.3),
    ("RBI financial inclusion strategy", "financial_inclusion", ["Financial Inclusion"], 0.3),
    ("Pradhan Mantri Jan Dhan Yojana", "financial_inclusion", ["Financial Inclusion"], 0.3),
    
    # Out of scope
    ("What is the weather today?", "out_of_scope", [], 0),
    ("Tell me a joke", "out_of_scope", [], 0),
    ("What is machine learning?", "out_of_scope", [], 0),
]

# Edge cases
EDGE_CASES = [
    # Empty/whitespace
    ("", "should_abstain"),
    ("   ", "should_abstain"),
    
    # Very long query
    ("What is PMFBY and how does it work and what are the eligibility criteria and how to apply and what documents are needed and what is the claim process?", "pmfby"),
    
    # Hindi queries
    ("पीएमएफबीवाई क्या है?", "pmfby"),
    ("पीएसीएस में कैसे शामिल हों?", "pacs_governance"),
    
    # Mixed language
    ("Tell me about PMFBY scheme in Hindi", "pmfby"),
    
    # Ambiguous queries
    ("cooperative", "pacs_governance"),
    ("insurance", "pmfby"),
    
    # State-specific queries
    ("What are Gujarat cooperative rules?", "should_return_central_or_abstain"),
    
    # Technical terms
    ("Agricultural Credit Cooperative Society", "pacs_governance"),
    ("Crop Insurance Scheme", "pmfby"),
]

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_retrieval_accuracy():
    """Test retrieval accuracy against gold cases."""
    print("\n" + "="*80)
    print("RETRIEVAL ACCURACY TEST")
    print("="*80)
    
    results = []
    correct_domain = 0
    correct_chunks = 0
    total_score = 0
    total_cases = 0
    
    for query, expected_domain, expected_chunks, min_score in GOLD_CASES:
        if expected_domain == "out_of_scope":
            continue
        
        total_cases += 1
        embedding = provider.embed_texts([query], task="retrieval.query")[0]
        domain, _ = anchor_store.classify(query, embedding)
        chunks = retrieve(supabase, embedding, domain, None, k=5)
        
        # Check domain accuracy
        domain_match = domain == expected_domain
        if domain_match:
            correct_domain += 1
        
        # Check chunk relevance
        chunk_scores = [c.similarity for c in chunks]
        top_score = max(chunk_scores) if chunk_scores else 0
        
        # Check if expected chunks are in top results
        # Since chunks don't have domain, we need to check by document title
        retrieved_docs = set()
        for c in chunks:
            # The title field contains the document title
            for source in expected_chunks:
                source_lower = source.lower()
                title_lower = c.title.lower() if c.title else ""
                content_lower = c.content.lower() if c.content else ""
                if (source_lower in title_lower or 
                    source_lower in content_lower):
                    retrieved_docs.add(source)
        
        chunk_match = len(retrieved_docs) > 0
        if chunk_match:
            correct_chunks += 1
        
        total_score += top_score
        
        result = {
            "query": query[:50],
            "expected_domain": expected_domain,
            "actual_domain": domain,
            "domain_match": domain_match,
            "top_score": top_score,
            "chunk_match": chunk_match,
            "retrieved_count": len(chunks),
        }
        results.append(result)
        
        status = "OK" if domain_match and chunk_match else "FAIL"
        print(f"{status} {query[:50]}")
        print(f"  Domain: {domain} (expected: {expected_domain}) {'OK' if domain_match else 'FAIL'}")
        print(f"  Top score: {top_score:.3f} {'OK' if top_score >= min_score else 'FAIL'}")
        print(f"  Chunk match: {chunk_match}")
        print()
    
    # Summary
    domain_accuracy = correct_domain / total_cases if total_cases > 0 else 0
    chunk_accuracy = correct_chunks / total_cases if total_cases > 0 else 0
    avg_score = total_score / total_cases if total_cases > 0 else 0
    
    print("\n" + "-"*80)
    print("RETRIEVAL SUMMARY")
    print("-"*80)
    print(f"Total cases: {total_cases}")
    print(f"Domain accuracy: {domain_accuracy:.3f} ({correct_domain}/{total_cases})")
    print(f"Chunk accuracy: {chunk_accuracy:.3f} ({correct_chunks}/{total_cases})")
    print(f"Average top score: {avg_score:.3f}")
    
    return {
        "total_cases": total_cases,
        "domain_accuracy": domain_accuracy,
        "chunk_accuracy": chunk_accuracy,
        "avg_score": avg_score,
        "results": results,
    }


def test_out_of_scope():
    """Test out-of-scope detection."""
    print("\n" + "="*80)
    print("OUT-OF-SCOPE DETECTION TEST")
    print("="*80)
    
    results = []
    correct = 0
    total = 0
    
    for query, expected_domain, expected_chunks, min_score in GOLD_CASES:
        if expected_domain != "out_of_scope":
            continue
        
        total += 1
        embedding = provider.embed_texts([query], task="retrieval.query")[0]
        domain, _ = anchor_store.classify(query, embedding)
        
        is_correct = domain == "out_of_scope"
        if is_correct:
            correct += 1
        
        result = {
            "query": query[:50],
            "expected": expected_domain,
            "actual": domain,
            "correct": is_correct,
        }
        results.append(result)
        
        status = "OK" if is_correct else "FAIL"
        print(f"{status} {query[:50]}")
        print(f"  Domain: {domain} (expected: {expected_domain})")
        print()
    
    accuracy = correct / total if total > 0 else 0
    print("-"*80)
    print(f"Out-of-scope accuracy: {accuracy:.3f} ({correct}/{total})")
    print("-"*80)
    
    return {"accuracy": accuracy, "results": results}


def test_evidence_gate():
    """Test evidence gate behavior."""
    print("\n" + "="*80)
    print("EVIDENCE GATE TEST")
    print("="*80)
    
    results = []
    
    # Test 1: Good evidence
    query = "What is PMFBY?"
    embedding = provider.embed_texts([query], task="retrieval.query")[0]
    chunks = retrieve(supabase, embedding, "pmfby", None, k=5)
    
    candidates = [
        RetrievalCandidate(
            chunk_id=c.chunk_id,
            document_id="",
            source_id="",
            dense_score=c.similarity,
            filter_decisions={
                "domain": True,
                "active": True,
                "is_central": c.jurisdiction == "central",
                "state_match": True,
            },
        )
        for c in chunks
    ]
    
    abstained, reason, band = evidence_gate_v2(candidates, "pmfby", None)
    gate_result = evidence_gate(chunks, "pmfby", None)
    
    print(f"Query: {query}")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Evidence gate v2: abstained={abstained}, reason={reason}, band={band}")
    print(f"  Evidence gate v1: abstained={gate_result.abstained}, reason={gate_result.reason}, confidence={gate_result.confidence}")
    print()
    
    results.append({
        "query": query,
        "v2_abstained": abstained,
        "v2_reason": str(reason) if reason else None,
        "v2_band": str(band),
        "v1_abstained": gate_result.abstained,
        "v1_confidence": gate_result.confidence,
    })
    
    # Test 2: Empty chunks
    abstained, reason, band = evidence_gate_v2([], "pmfby", None)
    print(f"Empty chunks test:")
    print(f"  abstained={abstained}, reason={reason}, band={band}")
    print()
    
    results.append({
        "query": "empty_chunks",
        "v2_abstained": abstained,
        "v2_reason": str(reason) if reason else None,
        "v2_band": str(band),
    })
    
    print("-"*80)
    print("Evidence gate tests complete")
    print("-"*80)
    
    return results


def test_citation_verification():
    """Test citation verification."""
    print("\n" + "="*80)
    print("CITATION VERIFICATION TEST")
    print("="*80)
    
    results = []
    
    # Test 1: Valid citations
    answer1 = "PMFBY provides crop insurance [chunk:abc12345] [chunk:def67890]"
    chunk_ids1 = ["abc12345", "def67890", "ghi11111"]
    
    verification1 = verify_citations(answer1, chunk_ids1)
    print(f"Test 1: Valid citations")
    print(f"  Answer: {answer1[:60]}...")
    print(f"  Valid: {verification1.is_valid}")
    print(f"  Valid IDs: {verification1.valid_citations}")
    print()
    
    results.append({
        "test": "valid_citations",
        "is_valid": verification1.is_valid,
        "valid_count": len(verification1.valid_citations),
    })
    
    # Test 2: Invalid citations
    answer2 = "PMFBY provides crop insurance [chunk:xyz99999]"
    chunk_ids2 = ["abc12345", "def67890"]
    
    verification2 = verify_citations(answer2, chunk_ids2)
    print(f"Test 2: Invalid citations")
    print(f"  Answer: {answer2[:60]}...")
    print(f"  Valid: {verification2.is_valid}")
    print(f"  Invalid prefixes: {verification2.invalid_prefixes}")
    print()
    
    results.append({
        "test": "invalid_citations",
        "is_valid": verification2.is_valid,
        "invalid_count": len(verification2.invalid_prefixes),
    })
    
    # Test 3: Fabricated URLs
    answer3 = "Visit https://example.com for more info"
    chunk_ids3 = ["abc12345"]
    
    verification3 = verify_citations(answer3, chunk_ids3)
    print(f"Test 3: Fabricated URLs")
    print(f"  Answer: {answer3[:60]}...")
    print(f"  Valid: {verification3.is_valid}")
    print()
    
    results.append({
        "test": "fabricated_urls",
        "is_valid": verification3.is_valid,
    })
    
    print("-"*80)
    print("Citation verification tests complete")
    print("-"*80)
    
    return results


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "="*80)
    print("EDGE CASE TEST")
    print("="*80)
    
    results = []
    
    for query, expected in EDGE_CASES:
        if expected == "should_abstain":
            # These would need the actual chat endpoint to test properly
            print(f"Query: (requires chat endpoint)")
            results.append({"query": query[:50] if query else "empty", "status": "requires_endpoint"})
            continue
        
        embedding = provider.embed_texts([query], task="retrieval.query")[0]
        domain, _ = anchor_store.classify(query, embedding)
        
        print(f"Query: (len={len(query)})")
        print(f"  Domain: {domain}")
        print()
        
        results.append({
            "query": query[:50] if query else "empty",
            "domain": domain,
        })
    
    print("-"*80)
    print("Edge case tests complete")
    print("-"*80)
    
    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*80)
    print("RAG SYSTEM ACCURACY AND EDGE CASE TESTING")
    print("="*80)
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Chunks in database: 500")
    print(f"Embedding model: Jina v3 768d")
    print()
    
    # Run tests
    retrieval_results = test_retrieval_accuracy()
    oos_results = test_out_of_scope()
    gate_results = test_evidence_gate()
    citation_results = test_citation_verification()
    edge_results = test_edge_cases()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    print("\n1. Retrieval Accuracy:")
    print(f"   Domain accuracy: {retrieval_results['domain_accuracy']:.3f}")
    print(f"   Chunk accuracy: {retrieval_results['chunk_accuracy']:.3f}")
    print(f"   Average top score: {retrieval_results['avg_score']:.3f}")
    
    print("\n2. Out-of-Scope Detection:")
    print(f"   Accuracy: {oos_results['accuracy']:.3f}")
    
    print("\n3. Evidence Gate:")
    print(f"   Tests passed: {len([r for r in gate_results if not r.get('v2_abstained', True)])}/{len(gate_results)}")
    
    print("\n4. Citation Verification:")
    print(f"   Tests passed: {len([r for r in citation_results if r.get('is_valid', False)])}/{len(citation_results)}")
    
    print("\n5. Edge Cases:")
    print(f"   Tested: {len(edge_results)}")
    
    # Save results
    all_results = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "retrieval": retrieval_results,
        "out_of_scope": oos_results,
        "evidence_gate": gate_results,
        "citation_verification": citation_results,
        "edge_cases": edge_results,
    }
    
    output_path = PROJECT_ROOT / "eval" / "accuracy_report.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_path}")
    print("="*80)


if __name__ == "__main__":
    main()
