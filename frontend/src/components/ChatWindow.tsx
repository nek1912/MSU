"use client";
import { useState, useEffect, useRef, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { sendChat, ChatResponse } from "@/lib/api";
import { useI18n } from "@/lib/i18n/provider";
import type { Locale } from "@/lib/i18n/i18n";
import { createSpeechService } from "@/lib/speech";
import { MessageBubble } from "./chat/MessageBubble";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Skeleton } from "@/components/ui/Skeleton";
import { IconMic, IconChat } from "@/components/ui/Icons";

type Msg = { role: "user" | "assistant"; text?: string; resp?: ChatResponse };

function fallback(lang: Locale): ChatResponse {
  return {
    answer: lang === "hi" ? "सेवा अभी उपलब्ध नहीं है।" : "Service unavailable right now.",
    language: lang,
    domain: "unknown",
    confidence: 0,
    citations: [],
    abstained: true,
    follow_up_question: null,
  };
}

export function ChatWindow() {
  const { t, locale } = useI18n();
  const speech = useMemo(() => createSpeechService(), []);
  const sp = useSearchParams();
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [typing, setTyping] = useState(false);
  const [listening, setListening] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const cancelListen = useRef<(() => void) | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const lang: Locale = locale;

  function factoryPrompt(scheme: string) {
    return scheme === "pmfby" ? "How does the PMFBY scheme work?" : "Tell me about the " + scheme.replace(/-/g, " ") + " scheme.";
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, typing]);

  useEffect(() => {
    const q = sp?.get("q");
    const scheme = sp?.get("scheme");
    if (q) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInput(q);
      setMsgs([]);
    } else if (scheme) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInput(factoryPrompt(scheme));
      setMsgs([]);
    }
  }, [sp]);

  async function ask(q?: string) {
    const question = (q ?? input).trim();
    if (!question || typing) return;
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: question }]);
    setTyping(true);
    try {
      const resp = await sendChat({ question, session_id: sessionId, language: lang, state: null });
      setMsgs((m) => [...m, { role: "assistant", resp }]);
    } catch {
      setMsgs((m) => [...m, { role: "assistant", resp: fallback(lang) }]);
    } finally {
      setTyping(false);
    }
  }

  function toggleMic() {
    if (listening) {
      cancelListen.current?.();
      setListening(false);
      return;
    }
    cancelListen.current = speech.listen(lang, (text) => {
      setInput((prev) => (prev ? prev + " " : "") + text);
      setListening(false);
    });
    setListening(true);
  }

  const starters = ["chat.starter1", "chat.starter2", "chat.starter3", "chat.starter4"];

  return (
    <div className="mx-auto flex h-[calc(100dvh-3.5rem)] max-w-3xl flex-col px-4 pt-4 md:h-dvh pb-16 md:pb-4">
      <div className="flex items-center justify-between py-2">
        <h1 className="text-lg font-bold text-[var(--text-primary)]">{t("nav.chat")}</h1>
        <div className="flex items-center gap-2">
          {speech.supported && (
            <Button variant={listening ? "primary" : "icon"} aria-label={listening ? t("common.stopMic") : t("common.mic")} onClick={toggleMic}>
              <IconMic className="w-5 h-5" />
            </Button>
          )}
          <Button variant="secondary" onClick={() => setMsgs([])}>{t("common.newSession")}</Button>
        </div>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto rounded-[var(--radius-xl)] border border-[var(--border-default)] bg-[var(--surface-elevated)] p-4">
        {msgs.length === 0 &&  (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <IconChat className="w-10 h-10 text-[var(--accent-primary)]" />
            <p className="text-sm text-[var(--text-secondary)]">
              {t("chat.welcome")}
            </p>
            <div className="grid w-full max-w-xs gap-2">
              {starters.map((k) => (
                <button key={k} onClick={() => ask(t(k))} className="rounded-[var(--radius-lg)] border border-[var(--border-default)] bg-[var(--surface-overlay)] px-3 py-2 text-left text-sm text-[var(--text-primary)] hover:border-[var(--border-hover)]">
                  {t(k)}
                </button>
              ))}
            </div>
          </div>
        )}
        {msgs.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="ml-auto w-fit max-w-[85%] rounded-[var(--radius-lg)] bg-[var(--text-primary)] px-4 py-2 text-white">{m.text}</div>
          ) : (
            <div key={i} className="max-w-[90%]">
              <MessageBubble resp={m.resp!} />
            </div>
          ),
        )}
        {typing && <Skeleton className="h-16 w-3/4" />}
        <div ref={bottomRef} />
      </div>

      <div className="mt-2 flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
          placeholder={t("chat.placeholder")}
          aria-label={t("chat.placeholder")}
        />
        <Button onClick={() => ask()} disabled={!input.trim() || typing}>{t("common.send")}</Button>
      </div>
      {speech.supported === false && <p className="mt-1 text-xs text-[var(--text-tertiary)]">{t("common.voiceUnsupported")}</p>}
    </div>
  );
}
