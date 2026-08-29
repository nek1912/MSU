import { NextResponse } from "next/server";
import type { Locale } from "@/lib/i18n/i18n";

/**
 * Server API route /api/chat
 * Proxy to the Python RAG backend (port 8000). The backend is the sole source
 * of truth: it performs retrieval, the evidence gate, and citation verification.
 * On any backend failure we return an explicit unavailable response — we must
 * NOT substitute a hardcoded local answer, which would bypass grounding.
 */

export async function POST(req: Request) {
  let body: { question?: string; session_id?: string; language?: string; state?: string | null };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const backendUrl = process.env.BACKEND_API_URL || "http://localhost:8000/chat";

  try {
    const backendRes = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (backendRes.ok) {
      return NextResponse.json(await backendRes.json());
    }

    return NextResponse.json(
      { error: "retrieval_backend_error", detail: `backend responded ${backendRes.status}` },
      { status: 502 },
    );
  } catch {
    return NextResponse.json(
      { error: "retrieval_backend_unavailable", detail: "backend unreachable" },
      { status: 503 },
    );
  }
}
