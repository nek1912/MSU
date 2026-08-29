import httpx, uuid, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def chat(question, lang="en"):
    r = httpx.post("http://localhost:8000/chat", json={
        "question": question,
        "session_id": str(uuid.uuid4()),
        "language": lang,
        "state": None
    }, timeout=120)
    d = r.json()
    print(f"[{lang}] {question}")
    print(f"  domain={d['domain']} intent={d['intent']} confidence={d['confidence']} ({d['confidence_level']})")
    print(f"  abstained={d['abstained']}")
    if not d['abstained']:
        print(f"  answer: {d['answer'][:200]}")
        for c in d['citations']:
            print(f"  cite: {c.get('title','?')[:50]} p.{c.get('page','?')}")
    print()

# English
chat("How does PMFBY crop insurance work?")
chat("What is PACS?")
chat("Tell me about cooperative society bylaws")

# Hindi
chat("PMFBY फसल बीमा कैसे काम करता है?", "hi")
chat("PACS क्या है?", "hi")

# Gujarati
chat("PMFBY ફસल વીમો કેવી રીતે કામ કરે છે?", "gu")
