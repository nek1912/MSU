"""Jina reranker integration for second-stage retrieval.

Architecture:
QUERY
  ↓
dense retrieval top-20
  ↓
Jina reranker
  ↓
top-5/6 evidence
"""
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv('backend/.env', override=True)

# Configuration
RERANKER_PROVIDER = os.environ.get('RERANKER_PROVIDER', 'jina')
RERANKER_MODEL = os.environ.get('RERANKER_MODEL', 'jina-reranker-v2-base-multilingual')
RERANKER_TOP_N = int(os.environ.get('RERANKER_TOP_N', '5'))
RERANKER_TIMEOUT = int(os.environ.get('RERANKER_TIMEOUT', '30'))


class JinaReranker:
    """Jina reranker for query-document reranking."""
    
    def __init__(self):
        self.api_key = os.environ.get('JINA_API_KEY')
        self.model = RERANKER_MODEL
        self.top_n = RERANKER_TOP_N
        self.timeout = RERANKER_TIMEOUT
        self.endpoint = "https://api.jina.ai/v1/rerank"
    
    def rerank(self, query: str, documents: list[dict], top_n: int = None) -> list[dict]:
        """Rerank documents using Jina reranker.
        
        Args:
            query: The search query
            documents: List of documents with 'chunk_id' and 'content' keys
            top_n: Number of results to return (default: self.top_n)
            
        Returns:
            List of reranked documents with 'rerank_score' added
        """
        if not self.api_key:
            # Fallback: return original order
            return documents[:top_n or self.top_n]
        
        if not documents:
            return []
        
        top_n = top_n or self.top_n
        
        # Prepare documents for reranking
        docs_for_rerank = []
        for i, doc in enumerate(documents):
            docs_for_rerank.append({
                "text": doc.get("content", ""),
                "index": i,
            })
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "query": query,
                        "documents": [d["text"] for d in docs_for_rerank],
                        "top_n": min(top_n, len(docs_for_rerank)),
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            # Process results
            results = []
            for item in data.get("results", []):
                original_idx = item.get("index", 0)
                score = item.get("relevance_score", 0)
                
                # Preserve original document data
                doc = documents[original_idx].copy()
                doc["rerank_score"] = score
                results.append(doc)
            
            return results
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limited - fallback to original order
                print(f"Reranker rate limited, falling back to original order")
                return documents[:top_n]
            raise
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            # Timeout/connection error - fallback
            print(f"Reranker error: {e}, falling back to original order")
            return documents[:top_n]
        except Exception as e:
            # Any other error - fallback
            print(f"Reranker unexpected error: {e}, falling back to original order")
            return documents[:top_n]


# Global reranker instance
_reranker = None


def get_reranker() -> JinaReranker:
    """Get or create reranker singleton."""
    global _reranker
    if _reranker is None:
        _reranker = JinaReranker()
    return _reranker
