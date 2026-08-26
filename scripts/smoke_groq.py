import os, sys, httpx

def main() -> int:
    key = os.environ["GROQ_API_KEY"]
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": "llama-3.3-70b-versatile",
              "messages": [{"role": "user", "content": "Reply with OK"}],
              "max_tokens": 5},
        timeout=30,
    )
    r.raise_for_status()
    print("groq ok:", r.json()["choices"][0]["message"]["content"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
