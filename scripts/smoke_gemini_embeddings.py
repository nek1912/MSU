import os, sys, httpx

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"

def embed(key: str, text: str) -> list[float]:
    r = httpx.post(
        f"{URL}?key={key}",
        json={"content": {"parts": [{"text": text}]}, "output_dimensionality": 768},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["embedding"]["values"]

def main() -> int:
    key = os.environ["GEMINI_API_KEY"]
    texts = ["PMFBY crop insurance eligibility", "PACS byelaws membership",
             "RBI financial literacy booklet"]
    vecs = [embed(key, t) for t in texts]
    assert all(len(v) == 768 for v in vecs), "wrong dimensionality"
    assert len({tuple(v) for v in vecs}) == 3, "AGGREGATION GUARD FAILED: inputs collapsed"
    print("gemini-embedding-2 ok: 3 inputs -> 3 distinct 768-dim vectors")
    return 0

if __name__ == "__main__":
    sys.exit(main())
