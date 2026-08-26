"use client";
import { useState } from "react";
import { sendChat, ChatResponse } from "@/lib/api";
import { EvidenceBand } from "./EvidenceBand";

type Msg = { role: "user" | "assistant"; text?: string; resp?: ChatResponse };

export function ChatWindow() {
  const [lang, setLang] = useState<"en" | "hi">("en");
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [busy, setBusy] = useState(false);

  async function ask() {
    const q = input.trim();
    if (!q || busy) return;
    setInput(""); setBusy(true);
    setMsgs(m => [...m, { role: "user", text: q }]);
    try {
      const resp = await sendChat({ question: q, session_id: sessionId, language: lang, state: null });
      setMsgs(m => [...m, { role: "assistant", resp }]);
    } catch {
      setMsgs(m => [...m, { role: "assistant",
        resp: { answer: lang === "hi" ? "सेवा अभी उपलब्ध नहीं है।" : "Service unavailable right now.",
                language: lang, domain: "unknown", confidence: 0, citations: [],
                abstained: true, follow_up_question: null } }]);
    } finally { setBusy(false); }
  }

  return (
    <div className="mx-auto flex h-dvh max-w-2xl flex-col p-4">
      <div className="mb-2 flex gap-2">
        {(["en", "hi"] as const).map(l => (
          <button key={l} onClick={() => setLang(l)}
            className={`rounded border px-3 py-1 ${lang === l ? "bg-black text-white" : ""}`}>
            {l === "en" ? "English" : "हिंदी"}
          </button>
        ))}
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto">
        {msgs.map((m, i) => m.role === "user"
          ? <div key={i} className="ml-auto w-fit max-w-[85%] rounded-xl bg-blue-600 px-4 py-2 text-white">{m.text}</div>
          : <div key={i} className="max-w-[90%] space-y-2">
              <div className={`rounded-xl border px-4 py-2 ${m.resp!.abstained ? "border-gray-300 bg-gray-50" : ""}`}>
                {m.resp!.answer}
              </div>
              {!m.resp!.abstained && <>
                <EvidenceBand confidence={m.resp!.confidence} />
                {m.resp!.citations.map((c, j) => (
                  <a key={j} href={c.url} target="_blank" rel="noopener noreferrer"
                     className="block truncate text-xs text-blue-700 underline">
                    {c.title}{c.page ? ` — p.${c.page}` : ""}
                  </a>))}
              </>}
            </div>)}
      </div>
      <div className="mt-2 flex gap-2">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && ask()}
          placeholder={lang === "hi" ? "अपना प्रश्न लिखें…" : "Type your question…"}
          className="flex-1 rounded border px-3 py-2" />
        <button onClick={ask} disabled={busy} className="rounded bg-black px-4 py-2 text-white disabled:opacity-50">
          {busy ? "…" : "➤"}
        </button>
      </div>
    </div>
  );
}
