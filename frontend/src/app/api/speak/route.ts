import { NextResponse } from "next/server";

/**
 * Server API route /api/speak
 * Proxies TTS requests to the Python backend (Sarvam Bulbul v3 → Azure fallback).
 */

export async function POST(req: Request) {
  const formData = await req.formData();
  const text = formData.get("text") as string;
  const language = (formData.get("language") as string) || "hi";

  if (!text) {
    return new Response("Missing text", { status: 400 });
  }

  const backendUrl = process.env.BACKEND_API_URL || "http://localhost:8000";

  // Try backend first
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);

    const backendForm = new FormData();
    backendForm.append("text", text);
    backendForm.append("language", language);

    const res = await fetch(`${backendUrl}/voice/speak`, {
      method: "POST",
      body: backendForm,
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (res.ok) {
      const audioBuffer = await res.arrayBuffer();
      if (audioBuffer.byteLength > 100) {
        return new Response(audioBuffer, {
          headers: { "Content-Type": "audio/wav" },
        });
      }
    }
  } catch {
    // Backend offline
  }

  // Fallback: return empty (client falls back to browser TTS)
  return new Response("", { status: 503, headers: { "Content-Type": "audio/wav" } });
}
