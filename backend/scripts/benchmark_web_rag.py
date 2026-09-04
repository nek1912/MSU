"""Benchmark: Tavily vs Firecrawl for web RAG search.

Tests both providers with the same queries to measure latency, result quality, and content richness.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Configuration ──────────────────────────────────────────────────────────
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY_1", "")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

TAVILY_URL = "https://api.tavily.com/search"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/search"

TEST_QUERIES = [
    {
        "query": "Rajkot APMC groundnut market price today",
        "original_gu": "રાજકોટ APMC માં મૂંગફળીનો આજનો બજાર ભાવ કેટલો છે?",
        "domain": "agriculture",
    },
    {
        "query": "cotton crop failure Gujarat what to do PMFBY claim",
        "original_gu": "ગઈકાલે ભારે વરસાદથી મારો કપાસનો પાક બગડ્યો છે. હવે હું શું કરું?",
        "domain": "pmfby",
    },
]


def benchmark_tavily(query: str) -> dict:
    """Test Tavily search."""
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "chunks_per_source": 3,
        "max_results": 10,
        "topic": "general",
        "include_answer": False,
        "include_raw_content": "markdown",
        "include_images": False,
    }

    start = time.time()
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(TAVILY_URL, headers=headers, json=payload)
    elapsed = time.time() - start

    data = resp.json()
    results = data.get("results", [])

    # Calculate content stats
    total_content_len = sum(len(r.get("content", "")) or len(r.get("raw_content", "")) for r in results)
    has_raw = sum(1 for r in results if r.get("raw_content"))

    return {
        "provider": "Tavily",
        "latency_seconds": round(elapsed, 2),
        "result_count": len(results),
        "total_content_chars": total_content_len,
        "results_with_raw_content": has_raw,
        "avg_content_per_result": round(total_content_len / len(results)) if results else 0,
        "top_results": [
            {
                "title": (r.get("title") or "")[:80],
                "url": (r.get("url") or "")[:100],
                "content_len": len(r.get("content") or ""),
                "raw_content_len": len(r.get("raw_content") or ""),
            }
            for r in results[:5]
        ],
    }


def benchmark_firecrawl(query: str) -> dict:
    """Test Firecrawl search."""
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "limit": 10,
        "lang": "en",
    }

    start = time.time()
    with httpx.Client(timeout=45.0) as client:
        resp = client.post(FIRECRAWL_URL, headers=headers, json=payload)
    elapsed = time.time() - start

    data = resp.json()
    results = data.get("data", [])

    # Calculate content stats
    total_content_len = sum(len(r.get("content", "")) or len(r.get("markdown", "")) for r in results)
    has_markdown = sum(1 for r in results if r.get("markdown"))

    return {
        "provider": "Firecrawl",
        "latency_seconds": round(elapsed, 2),
        "result_count": len(results),
        "total_content_chars": total_content_len,
        "results_with_markdown": has_markdown,
        "avg_content_per_result": round(total_content_len / len(results)) if results else 0,
        "top_results": [
            {
                "title": (r.get("title") or "")[:80],
                "url": (r.get("url") or "")[:100],
                "content_len": len(r.get("content") or ""),
                "markdown_len": len(r.get("markdown") or ""),
            }
            for r in results[:5]
        ],
    }


if __name__ == "__main__":
    print("BENCHMARK: Tavily vs Firecrawl for Web RAG")
    print("=" * 60)

    all_results = []

    for q in TEST_QUERIES:
        print(f"\nQuery: {q['query'][:60]}...")
        print("-" * 60)

        tavily_result = benchmark_tavily(q["query"])
        firecrawl_result = benchmark_firecrawl(q["query"])

        print(f"  Tavily:    {tavily_result['latency_seconds']}s, {tavily_result['result_count']} results, {tavily_result['total_content_chars']} chars")
        print(f"  Firecrawl: {firecrawl_result['latency_seconds']}s, {firecrawl_result['result_count']} results, {firecrawl_result['total_content_chars']} chars")

        all_results.append({
            "query": q["query"],
            "original_gu": q["original_gu"],
            "domain": q["domain"],
            "tavily": tavily_result,
            "firecrawl": firecrawl_result,
        })

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    tavily_avg_latency = sum(r["tavily"]["latency_seconds"] for r in all_results) / len(all_results)
    firecrawl_avg_latency = sum(r["firecrawl"]["latency_seconds"] for r in all_results) / len(all_results)

    tavily_avg_results = sum(r["tavily"]["result_count"] for r in all_results) / len(all_results)
    firecrawl_avg_results = sum(r["firecrawl"]["result_count"] for r in all_results) / len(all_results)

    tavily_avg_content = sum(r["tavily"]["total_content_chars"] for r in all_results) / len(all_results)
    firecrawl_avg_content = sum(r["firecrawl"]["total_content_chars"] for r in all_results) / len(all_results)

    print(f"{'Metric':<25} {'Tavily':<15} {'Firecrawl':<15}")
    print("-" * 55)
    print(f"{'Avg Latency (s)':<25} {tavily_avg_latency:<15.2f} {firecrawl_avg_latency:<15.2f}")
    print(f"{'Avg Results':<25} {tavily_avg_results:<15.1f} {firecrawl_avg_results:<15.1f}")
    print(f"{'Avg Content (chars)':<25} {tavily_avg_content:<15.0f} {firecrawl_avg_content:<15.0f}")

    # Determine winner
    faster = "Tavily" if tavily_avg_latency < firecrawl_avg_latency else "Firecrawl"
    richer = "Tavily" if tavily_avg_content > firecrawl_avg_content else "Firecrawl"

    print(f"\nFaster: {faster}")
    print(f"Richer content: {richer}")

    # Save results
    with open("web_rag_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nFull results saved to web_rag_benchmark.json")
