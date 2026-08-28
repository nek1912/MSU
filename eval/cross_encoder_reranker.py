"""Cross-encoder reranker using transformers.

Uses a small multilingual cross-encoder for reranking.
Falls back to heuristic if model unavailable.
"""
import os
import re
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# Small multilingual cross-encoder models suitable for CPU
CANDIDATE_MODELS = [
    "cross-encoder/ms-marco-MiniLM-L-6-v2",  # English, very small
    "BAAI/bge-reranker-v2-m3",  # Multilingual, small
]


class CrossEncoderReranker:
    """Cross-encoder reranker using transformers."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load the cross-encoder model."""
        try:
            print(f"Loading cross-encoder model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.eval()
            print(f"Model loaded successfully")
        except Exception as e:
            print(f"Failed to load model {self.model_name}: {e}")
            self.model = None
            self.tokenizer = None
    
    def rerank(self, query: str, documents: list, top_n: int = 5) -> list:
        """Rerank documents using cross-encoder."""
        if self.model is None or self.tokenizer is None:
            # Fallback to heuristic
            return self._heuristic_rerank(query, documents, top_n)
        
        if not documents:
            return []
        
        try:
            # Prepare pairs
            pairs = [(query, doc.get('content', '')[:512]) for doc in documents]
            
            # Tokenize
            inputs = self.tokenizer(
                [p[0] for p in pairs],
                [p[1] for p in pairs],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # Get scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = outputs.logits.squeeze().tolist()
            
            # Handle single document case
            if not isinstance(scores, list):
                scores = [scores]
            
            # Combine with original documents
            scored = []
            for i, (doc, score) in enumerate(zip(documents, scores)):
                scored.append({**doc, 'rerank_score': score})
            
            # Sort by score
            scored.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            return scored[:top_n]
            
        except Exception as e:
            print(f"Cross-encoder error: {e}, falling back to heuristic")
            return self._heuristic_rerank(query, documents, top_n)
    
    def _heuristic_rerank(self, query: str, documents: list, top_n: int) -> list:
        """Heuristic reranking fallback."""
        scored = []
        for doc in documents:
            content = doc.get('content', '')
            section = doc.get('section', '')
            dense_score = doc.get('similarity', 0)
            
            # Token overlap
            query_tokens = set(re.findall(r'\w+', query.lower()))
            doc_tokens = set(re.findall(r'\w+', content.lower()))
            token_overlap = len(query_tokens & doc_tokens) / len(query_tokens) if query_tokens else 0
            
            # Exact match
            exact_match = 1.0 if query.lower() in content.lower() else 0.0
            
            # Section match
            section_match = 0.0
            if section:
                section_terms = set(re.findall(r'\w+', section.lower()))
                section_match = len(query_tokens & section_terms) / len(query_tokens) if query_tokens else 0
            
            # Weighted score
            score = 0.6 * dense_score + 0.2 * token_overlap + 0.1 * exact_match + 0.1 * section_match
            
            scored.append({**doc, 'rerank_score': score})
        
        scored.sort(key=lambda x: x['rerank_score'], reverse=True)
        return scored[:top_n]


def get_reranker(model_name: str = None) -> CrossEncoderReranker:
    """Get or create reranker singleton."""
    if not hasattr(get_reranker, '_instance'):
        get_reranker._instance = CrossEncoderReranker(model_name)
    return get_reranker._instance
