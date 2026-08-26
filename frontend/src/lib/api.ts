export interface ChatResponse {
  answer: string; language: "en" | "hi"; domain: string; confidence: number;
  citations: { title: string; page: number; url: string }[];
  abstained: boolean; follow_up_question: string | null;
}

export async function sendChat(payload: {
  question: string; session_id: string; language: "en" | "hi"; state: string | null;
}): Promise<ChatResponse> {
  const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"}/chat`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
