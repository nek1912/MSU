import httpx, json

# Test English query
r = httpx.post("http://localhost:8000/chat", json={
    "question": "How does PMFBY crop insurance work?",
    "session_id": "test-session-001",
    "language": "en",
    "state": None
}, timeout=120)
print("=== ENGLISH QUERY ===")
print(f"Status: {r.status_code}")
data = r.json()
print(f"Answer: {data['answer'][:200]}")
print(f"Domain: {data['domain']}")
print(f"Intent: {data['intent']}")
print(f"Confidence: {data['confidence']} ({data['confidence_level']})")
print(f"Citations: {len(data['citations'])}")
print(f"Abstained: {data['abstained']}")
for c in data['citations']:
    print(f"  - {c['title'][:50]} p.{c['page']}")

# Test Hindi query
r2 = httpx.post("http://localhost:8000/chat", json={
    "question": "PACS क्या है?",
    "session_id": "test-session-002",
    "language": "hi",
    "state": None
}, timeout=120)
print("\n=== HINDI QUERY ===")
print(f"Status: {r2.status_code}")
data2 = r2.json()
print(f"Answer: {data2['answer'][:200]}")
print(f"Domain: {data2['domain']}")
print(f"Intent: {data2['intent']}")
print(f"Confidence: {data2['confidence']} ({data2['confidence_level']})")
print(f"Citations: {len(data2['citations'])}")
print(f"Abstained: {data2['abstained']}")
