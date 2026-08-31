import type { Locale } from "@/lib/i18n/i18n";

export interface SpeechSegment {
  text: string;
  language: string;
}

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
  mode?: string;
  conversation_id?: string;
  speech_text?: string;
  speech_segments?: SpeechSegment[];
  follow_up_question: string | null;
}

export async function sendChat(payload: {
  question: string;
  session_id: string;
  language: Locale;
  state: string | null;
  history?: Array<{ role: "user" | "assistant"; content: string }>;
  ui_language_explicit?: boolean;
}): Promise<ChatResponse> {
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}

export interface StreamEvent {
  event: "thinking" | "token" | "metadata" | "done" | "error";
  data: Record<string, unknown>;
}

export async function sendChatStream(
  payload: {
    question: string;
    session_id: string;
    language: Locale;
    state: string | null;
    history?: Array<{ role: "user" | "assistant"; content: string }>;
    ui_language_explicit?: boolean;
  },
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const r = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  const reader = r.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "";
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        const raw = line.slice(6);
        try {
          const data = JSON.parse(raw);
          onEvent({ event: currentEvent as StreamEvent["event"], data });
        } catch {
          onEvent({ event: currentEvent as StreamEvent["event"], data: { text: raw } });
        }
        currentEvent = "";
      }
    }
  }
}

export interface TranslateItem {
  original: string;
  translated: string;
}

export async function translateTexts(
  texts: string[],
  sourceLanguage: string,
  targetLanguage: string,
): Promise<TranslateItem[]> {
  const r = await fetch("/api/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      texts,
      source_language: sourceLanguage,
      target_language: targetLanguage,
    }),
  });
  if (!r.ok) throw new Error(`Translate API ${r.status}`);
  const data = await r.json();
  return data.translations;
}

export async function fetchVoiceSpeak(
  segments: SpeechSegment[],
): Promise<{ audio: string; language: string }> {
  const r = await fetch("/api/voice/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ segments }),
  });
  if (!r.ok) throw new Error(`Voice speak API ${r.status}`);
  return r.json();
}
