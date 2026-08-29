import sys
sys.path.insert(0, ".")

import httpx

# Test English query
r = httpx.post("http://localhost:8000/chat", json={
    "question": "How does PMFBY crop insurance work?",
    "session_id": "test-001",
    "language": "en",
    "state": None
}, timeout=120)
data = r.json()
print(f"Status: {r.status_code}")
print(f"Abstained: {data['abstained']}")
print(f"Domain: {data['domain']}")
print(f"Intent: {data.get('intent', 'N/A')}")
print(f"Confidence: {data['confidence']} ({data.get('confidence_level', 'N/A')})")
print(f"Citations: {len(data['citations'])}")
if data['abstained']:
    print(f"Answer (abstained): {data['answer'][:200]}")
else:
    print(f"Answer: {data['answer'][:300]}")
    for c in data['citations']:
        print(f"  cite: {c.get('title','?')[:50]} p.{c.get('page','?')}")
