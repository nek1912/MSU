import type { Locale } from "@/lib/i18n/i18n";

export interface ChatResponse {
  answer: string;
  language: Locale;
  domain: string;
  intent: string;
  entities: string[];
  confidence: number;
  confidence_level: "high" | "moderate" | "low" | "none";
  citations: {
    chunk_id: string | null;
    document_id: string | null;
    source_file: string;
    title: string;
    page: number;
    page_start: number | null;
    page_end: number | null;
    section: string;
    subsection: string;
    clause: string;
    url: string;
  }[];
  abstained: boolean;
  follow_up_question: string | null;
}

export async function sendChat(payload: {
  question: string;
  session_id: string;
  language: Locale;
  state: string | null;
}): Promise<ChatResponse> {
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
