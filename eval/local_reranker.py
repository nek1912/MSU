"""Local reranking using cross-encoder similarity.

Uses a lightweight approach: compute token overlap and section similarity
as proxy for cross-encoder scoring.
"""
import os
import re
from collections import Counter


def compute_token_overlap(query: str, document: str) -> float:
    """Compute token overlap score between query and document."""
    query_tokens = set(re.findall(r'\w+', query.lower()))
    doc_tokens = set(re.findall(r'\w+', document.lower()))
    
    if not query_tokens:
        return 0.0
    
    # Jaccard similarity
    intersection = query_tokens & doc_tokens
    union = query_tokens | doc_tokens
    
    return len(intersection) / len(union) if union else 0.0


def compute_exact_match_score(query: str, document: str) -> float:
    """Compute exact phrase match score."""
    query_lower = query.lower()
    doc_lower = document.lower()
    
    # Check for exact query in document
    if query_lower in doc_lower:
        return 1.0
    
    # Check for significant phrases
    query_phrases = re.findall(r'\b\w+\s+\w+\b', query_lower)
    if not query_phrases:
        return 0.0
    
    matches = sum(1 for phrase in query_phrases if phrase in doc_lower)
    return matches / len(query_phrases)


def compute_section_match_score(query: str, section: str) -> float:
    """Compute section/title match score."""
    if not section:
        return 0.0
    
    query_lower = query.lower()
    section_lower = section.lower()
    
    # Check if query terms appear in section
    query_terms = set(re.findall(r'\w+', query_lower))
    section_terms = set(re.findall(r'\w+', section_lower))
    
    if not query_terms:
        return 0.0
    
    overlap = query_terms & section_terms
    return len(overlap) / len(query_terms)


def local_rerank(query: str, candidates: list, top_n: int = 5) -> list:
    """Local reranking using multiple signals.
    
    Combines:
    - Dense similarity (from retrieval)
    - Token overlap
    - Exact match
    - Section match
    
    No external API calls.
    """
    scored = []
    
    for candidate in candidates:
        content = candidate.get('content', '')
        section = candidate.get('section', '')
        
        # Compute scores
        dense_score = candidate.get('similarity', 0)
        token_score = compute_token_overlap(query, content)
        exact_score = compute_exact_match_score(query, content)
        section_score = compute_section_match_score(query, section)
        
        # Weighted combination
        # Dense is primary, others are boosters
        final_score = (
            0.6 * dense_score +
            0.2 * token_score +
            0.1 * exact_score +
            0.1 * section_score
        )
        
        scored.append({
            **candidate,
            'local_score': final_score,
            'token_score': token_score,
            'exact_score': exact_score,
            'section_score': section_score,
        })
    
    # Sort by local score
    scored.sort(key=lambda x: x['local_score'], reverse=True)
    
    return scored[:top_n]


def analyze_ranking_improvement(query: str, candidates: list, gold_chunks: list, top_n: int = 5) -> dict:
    """Analyze whether local reranking improves ranking of gold chunks."""
    # Get original ranking
    original_ids = [c['chunk_id'] for c in candidates[:top_n]]
    original_rank = None
    for i, chunk_id in enumerate(original_ids):
        if chunk_id in gold_chunks:
            original_rank = i + 1
            break
    
    # Get reranked results
    reranked = local_rerank(query, candidates, top_n)
    reranked_ids = [c['chunk_id'] for c in reranked]
    reranked_rank = None
    for i, chunk_id in enumerate(reranked_ids):
        if chunk_id in gold_chunks:
            reranked_rank = i + 1
            break
    
    return {
        'original_rank': original_rank,
        'reranked_rank': reranked_rank,
        'improved': reranked_rank is not None and (original_rank is None or reranked_rank < original_rank),
    }
