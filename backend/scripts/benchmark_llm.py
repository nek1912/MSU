"""Benchmark: Sarvam-105B (direct) vs Groq+Translation (original architecture).

Tests both with the same prompt to measure latency and compare output quality.
"""

import json
import time
import httpx

# ── Configuration ──────────────────────────────────────────────────────────
SARVAM_API_KEY = "sk_iz54whep_gp6cI99hkcgjtrULNAl8oOvF"
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_MODEL = "sarvam-105b-conversations"

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"

TEST_PROMPT = """You are a helpful assistant for Indian citizens. Answer the following question in Gujarati.

Question: Tell me about પીએમ-કુસુમ સોલાર પંપ યોજના scheme

Answer in Gujarati. Provide accurate information about this government scheme."""


def benchmark_sarvam() -> dict:
    """Test Sarvam-105B direct generation (no translation)."""
    print("\n" + "=" * 60)
    print("SARVAM-105B (Direct Generation)")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": SARVAM_MODEL,
        "messages": [
            {"role": "user", "content": TEST_PROMPT}
        ],
        "max_tokens": 1000,
        "temperature": 0.3,
    }
    
    start = time.time()
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(SARVAM_URL, headers=headers, json=payload)
    
    elapsed = time.time() - start
    data = resp.json()
    
    usage = data.get("usage", {})
    content = data["choices"][0]["message"]["content"]
    
    result = {
        "provider": "Sarvam-105B",
        "latency_seconds": round(elapsed, 2),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "output_text": content,
        "chars_per_second": round(len(content) / elapsed, 1) if elapsed > 0 else 0,
    }
    
    print(f"Latency: {result['latency_seconds']}s")
    print(f"Prompt tokens: {result['prompt_tokens']}")
    print(f"Completion tokens: {result['completion_tokens']}")
    print(f"Chars/second: {result['chars_per_second']}")
    
    return result


def benchmark_groq_direct() -> dict:
    """Test Groq direct (no translation, English prompt, English output)."""
    print("\n" + "=" * 60)
    print("GROQ DIRECT (English in, English out)")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": "Tell me about PM-KUSUM Solar Pump Scheme in English. Provide accurate information about this government scheme."}
        ],
        "max_tokens": 1000,
        "temperature": 0.3,
    }
    
    start = time.time()
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(GROQ_URL, headers=headers, json=payload)
    
    elapsed = time.time() - start
    data = resp.json()
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return {
            "provider": "Groq Direct",
            "latency_seconds": round(elapsed, 2),
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "output_text": f"Error: {data['error']}",
            "chars_per_second": 0,
        }
    
    usage = data.get("usage", {})
    content = data["choices"][0]["message"]["content"]
    
    result = {
        "provider": "Groq Direct",
        "latency_seconds": round(elapsed, 2),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "output_text": content,
        "chars_per_second": round(len(content) / elapsed, 1) if elapsed > 0 else 0,
    }
    
    print(f"Latency: {result['latency_seconds']}s")
    print(f"Prompt tokens: {result['prompt_tokens']}")
    print(f"Completion tokens: {result['completion_tokens']}")
    print(f"Chars/second: {result['chars_per_second']}")
    
    return result


def benchmark_groq_with_translation() -> dict:
    """Test Groq with translation (original architecture: translate Gujarati→English, Groq, output English)."""
    print("\n" + "=" * 60)
    print("GROQ + TRANSLATION (Original Architecture)")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Step 1: Translate Gujarati to English using Sarvam translation
    translate_payload = {
        "input": TEST_PROMPT,
        "source_language": "gu",
        "target_language": "en",
        "mode": "formal",
        "model": "mayura:v2",
    }
    
    t1_start = time.time()
    with httpx.Client(timeout=30.0) as client:
        translate_resp = client.post(
            "https://api.sarvam.ai/translate",
            headers=headers,
            json=translate_payload,
        )
    t1_elapsed = time.time() - t1_start
    translated_input = translate_resp.json().get("translated_text", "")
    print(f"Translation (gu->en): {t1_elapsed:.2f}s")
    
    # Step 2: Groq LLM
    groq_headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": translated_input}
        ],
        "max_tokens": 1000,
        "temperature": 0.3,
    }
    
    t2_start = time.time()
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(GROQ_URL, headers=groq_headers, json=payload)
    t2_elapsed = time.time() - t2_start
    
    groq_data = resp.json()
    if "error" in groq_data:
        print(f"Groq Error: {groq_data['error']}")
        return {
            "provider": "Groq + Translation",
            "latency_seconds": round(t1_elapsed + t2_elapsed, 2),
            "translation_gu_en": round(t1_elapsed, 2),
            "groq_llm": round(t2_elapsed, 2),
            "translation_en_gu": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "output_text": f"Error: {groq_data['error']}",
            "chars_per_second": 0,
        }
    
    groq_output = groq_data["choices"][0]["message"]["content"]
    
    # Step 3: Translate English output to Gujarati
    t3_start = time.time()
    translate_back_payload = {
        "input": groq_output,
        "source_language": "en",
        "target_language": "gu",
        "mode": "formal",
        "model": "mayura:v2",
    }
    with httpx.Client(timeout=30.0) as client:
        translate_back_resp = client.post(
            "https://api.sarvam.ai/translate",
            headers=headers,
            json=translate_back_payload,
        )
    t3_elapsed = time.time() - t3_start
    gujarati_output = translate_back_resp.json().get("translated_text", "")
    
    total_elapsed = t1_elapsed + t2_elapsed + t3_elapsed
    usage = resp.json().get("usage", {})
    
    result = {
        "provider": "Groq + Translation",
        "latency_seconds": round(total_elapsed, 2),
        "translation_gu_en": round(t1_elapsed, 2),
        "groq_llm": round(t2_elapsed, 2),
        "translation_en_gu": round(t3_elapsed, 2),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "output_text": gujarati_output,
        "chars_per_second": round(len(gujarati_output) / total_elapsed, 1) if total_elapsed > 0 else 0,
    }
    
    print(f"Translation (gu->en): {result['translation_gu_en']}s")
    print(f"Groq LLM: {result['groq_llm']}s")
    print(f"Translation (en->gu): {result['translation_en_gu']}s")
    print(f"Total latency: {result['latency_seconds']}s")
    print(f"Prompt tokens: {result['prompt_tokens']}")
    print(f"Completion tokens: {result['completion_tokens']}")
    print(f"Chars/second: {result['chars_per_second']}")
    
    return result


if __name__ == "__main__":
    print("BENCHMARK: Sarvam-105B vs Groq+Translation")
    
    sarvam_result = benchmark_sarvam()
    groq_direct_result = benchmark_groq_direct()
    groq_translation_result = benchmark_groq_with_translation()
    
    # Save full results to JSON
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "sarvam": sarvam_result,
            "groq_direct": groq_direct_result,
            "groq_translation": groq_translation_result,
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    
    results = [sarvam_result, groq_direct_result, groq_translation_result]
    
    print(f"{'Provider':<25} {'Latency':<10} {'Tokens':<8} {'Chars/s':<10}")
    print("-" * 55)
    for r in results:
        print(f"{r['provider']:<25} {r['latency_seconds']:<10} {r['total_tokens']:<8} {r['chars_per_second']:<10}")
    
    fastest = min(results, key=lambda x: x["latency_seconds"])
    print(f"\nFastest: {fastest['provider']} ({fastest['latency_seconds']}s)")
    
    # Groq breakdown
    gt = groq_translation_result
    print(f"\nGroq+Translation breakdown:")
    print(f"  Translate gu->en: {gt['translation_gu_en']}s")
    print(f"  Groq LLM:         {gt['groq_llm']}s")
    print(f"  Translate en->gu:  {gt['translation_en_gu']}s")
    print(f"  Total:            {gt['latency_seconds']}s")
    
    print(f"\nFull results saved to benchmark_results.json")
