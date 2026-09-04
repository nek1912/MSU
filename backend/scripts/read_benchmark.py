import json

with open("web_rag_benchmark.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for q in data:
    print(f"=== Query: {q['query'][:60]} ===")
    t = q["tavily"]
    print(f"Tavily: {t['result_count']} results, {t['total_content_chars']} chars, {t['latency_seconds']}s")
    for r in t["top_results"]:
        print(f"  - {r['title'][:60]} ({r['content_len']} chars, raw: {r['raw_content_len']})")
    print()
