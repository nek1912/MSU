"""Gemini reranker — uses Gemini API to score candidate relevance.

Two-stage reranking:
1. Pre-ranking: Quick semantic scoring to filter candidates
2. Final reranking: Detailed relevance scoring for top candidates
"""

from __future__ import annotations

import json
import logging

import httpx

from app.config import REQUEST_TIMEOUT_S, get_settings

logger = logging.getLogger(__name__)

_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

PRE_RANK_MODEL = "gemini-2.5-flash-lite"
FINAL_RANK_MODEL = "gemini-2.5-flash-lite"


class GeminiReranker:

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.gemini_api_key
        if not self._api_key:
            logger.warning("Gemini API key not set, reranker will use passthrough scores")
            self._enabled = False
        else:
            self._enabled = True
            logger.info("Gemini reranker initialized")

    def _call_gemini(self, model: str, contents: list[dict]) -> dict | None:
        """Make a single Gemini API call."""
        if not self._enabled:
            return None

        url = _GEMINI_URL.format(model=model) + f"?key={self._api_key}"
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0,
                "maxTokens": 1024,
            },
        }

        try:
            r = httpx.post(url, json=payload, timeout=REQUEST_TIMEOUT_S)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning(f"Gemini reranking call failed: {e}")
            return None

    def _extract_score(self, response: dict) -> float | None:
        """Extract numeric score from Gemini response."""
        try:
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            # Try to parse as JSON first
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    return float(data.get("score", 0))
                elif isinstance(data, list) and data:
                    return float(data[0].get("score", 0))
            except json.JSONDecodeError:
                # Try to extract number from text
                import re
                match = re.search(r'"?score"?\s*[:=]\s*(\d+\.?\d*)', text, re.IGNORECASE)
                if match:
                    return float(match.group(1))
        except (KeyError, IndexError, TypeError):
            pass
        return None

    def pre_rank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 15,
        classification: dict | None = None,
    ) -> list[dict]:
        """Pre-rank candidates using Gemini to filter for relevance."""
        if not self._enabled or not candidates:
            return self._passthrough_pre_rank(query, candidates, top_k)

        # Build batch prompt for efficiency
        candidate_texts = []
        for i, c in enumerate(candidates[:top_k * 2]):  # Process more than needed
            content = c.get("content", "")[:500]  # Truncate for token efficiency
            candidate_texts.append(f"[{i}] {content}")

        prompt = f"""Rate each text chunk's relevance to the query on a scale of 0-10.
Query: {query}

Chunks:
{chr(10).join(candidate_texts)}

Return JSON array: [{{"index": 0, "score": 7, "relevant": true}}, ...]
Only include chunks with score >= 5 as relevant."""

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        response = self._call_gemini(PRE_RANK_MODEL, contents)

        if not response:
            return self._passthrough_pre_rank(query, candidates, top_k)

        # Parse scores
        scores = self._extract_scores_batch(response)

        # Apply scores to candidates
        scored = []
        for i, c in enumerate(candidates):
            result = dict(c)
            score_data = scores.get(i, {})
            result["gemini_score"] = score_data.get("score", 0.0)
            result["rerank_applicable"] = score_data.get("relevant", True)
            scored.append(result)

        scored.sort(key=lambda x: x["gemini_score"], reverse=True)
        return scored[:top_k]

    def _passthrough_pre_rank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        """Fallback passthrough scoring when Gemini is unavailable."""
        scored = []
        for i, c in enumerate(candidates):
            result = dict(c)
            result["gemini_score"] = float(c.get("bm25_score", 100.0 - i))
            result["rerank_applicable"] = True
            scored.append(result)
        scored.sort(key=lambda x: x["gemini_score"], reverse=True)
        return scored[:top_k]

    def _extract_scores_batch(self, response: dict) -> dict[int, dict]:
        """Extract batch scores from Gemini response."""
        scores = {}
        try:
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            # Find JSON array in response
            import re
            json_match = re.search(r'\[.*?\]', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                for item in data:
                    idx = item.get("index", -1)
                    if 0 <= idx:
                        scores[idx] = {
                            "score": float(item.get("score", 0)),
                            "relevant": item.get("relevant", True),
                        }
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.debug(f"Failed to parse Gemini batch scores: {e}")
        return scores

    def final_rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 8,
        classification: dict | None = None,
    ) -> list[dict]:
        """Final rerank using Gemini for detailed relevance scoring."""
        if not self._enabled or not candidates:
            return self._passthrough_final_rerank(query, candidates, top_k)

        # Build detailed prompt for final ranking
        candidate_texts = []
        for i, c in enumerate(candidates):
            content = c.get("content", "")[:600]
            source = c.get("source", c.get("url", "unknown"))
            candidate_texts.append(f"[{i}] Source: {source}\nContent: {content}")

        domain_hint = ""
        if classification:
            domain = classification.get("domain", "")
            if domain:
                domain_hint = f"\nDomain context: {domain}"

        prompt = f"""Score each evidence chunk for relevance to the query.
Rate 0-10 based on: direct answer support, source credibility, specificity.

Query: {query}{domain_hint}

Evidence chunks:
{chr(10).join(candidate_texts)}

Return JSON array: [{{"index": 0, "score": 8.5, "applicable": true, "reason": "directly answers"}}, ...]"""

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        response = self._call_gemini(FINAL_RANK_MODEL, contents)

        if not response:
            return self._passthrough_final_rerank(query, candidates, top_k)

        scores = self._extract_final_scores(response)

        scored = []
        for i, c in enumerate(candidates):
            result = dict(c)
            score_data = scores.get(i, {})
            result["rerank_score"] = score_data.get("score", 0.0)
            result["rerank_applicable"] = score_data.get("applicable", True)
            if "reason" in score_data:
                result["rerank_reason"] = score_data["reason"]
            scored.append(result)

        scored.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        return scored[:top_k]

    def _passthrough_final_rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        """Fallback passthrough scoring when Gemini is unavailable."""
        scored = []
        for i, c in enumerate(candidates):
            result = dict(c)
            result["rerank_score"] = float(c.get("rrf_score", 100.0 - i) * 100)
            result["rerank_applicable"] = True
            scored.append(result)
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored[:top_k]

    def _extract_final_scores(self, response: dict) -> dict[int, dict]:
        """Extract final scores from Gemini response."""
        scores = {}
        try:
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            import re
            json_match = re.search(r'\[.*?\]', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                for item in data:
                    idx = item.get("index", -1)
                    if 0 <= idx:
                        scores[idx] = {
                            "score": float(item.get("score", 0)),
                            "applicable": item.get("applicable", True),
                            "reason": item.get("reason", ""),
                        }
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.debug(f"Failed to parse Gemini final scores: {e}")
        return scores
