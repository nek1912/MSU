"use client";
import { useState, useEffect, useRef, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { sendChat, ChatResponse } from "@/lib/api";
import { useI18n } from "@/lib/i18n/provider";
import type { Locale } from "@/lib/i18n/i18n";
import { useTranslate } from "@/lib/useTranslate";
import { createSpeechService } from "@/lib/speech";
import { MessageBubble } from "./chat/MessageBubble";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { Reveal } from "@/components/motion/Reveal";
import {
  IconMic,
  IconChevronRight,
  IconBot,
  IconTrash,
  IconSparkles,
  IconSend,
  IconPlus,
  IconSidebar,
  IconClock,
  IconDoc,
  IconGrid,
  IconScale,
  IconHelp,
} from "@/components/ui/Icons";

type Msg = { role: "user" | "assistant"; text?: string; resp?: ChatResponse };

const MODELS = ["Sahakarita-v2.5", "GPT-4o", "Claude 3.5 Sonnet"];

function fallback(lang: Locale): ChatResponse {
  return {
    answer:
      lang === "hi"
        ? "सेवा अभी उपलब्ध नहीं है।"
        : lang === "mr"
        ? "सेवा सध्या उपलब्ध नाही."
        : "Service unavailable right now.",
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
  const { translate } = useTranslate();
  const speech = useMemo(() => createSpeechService(), []);
  const sp = useSearchParams();
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [typing, setTyping] = useState(false);
  const [listening, setListening] = useState(false);
  const [model, setModel] = useState(MODELS[0]);
  const [showModelPicker, setShowModelPicker] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false); // Collapsed by default on small mobile, expanded on desktop via effect
  const [history, setHistory] = useState<string[]>([]);
  const [sessionId] = useState(() => crypto.randomUUID());
  const cancelListen = useRef<(() => void) | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const lang: Locale = locale;
  const sendLang: "en" | "hi" = locale === "hi" ? "hi" : "en";

  // Auto-expand sidebar on large screens (>=1024px); keep it a drawer on tablet/mobile
  useEffect(() => {
    if (typeof window !== "undefined" && window.innerWidth >= 1024) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSidebarOpen(true);
    }
  }, []);

  const initialHistory = useMemo(
    () => [t("chat.starter1"), t("chat.starter2"), t("chat.starter3"), t("chat.starter4")],
    [t]
  );

  useEffect(() => {
    if (history.length === 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHistory(initialHistory);
    }
  }, [initialHistory, history.length]);

  function factoryPrompt(scheme: string) {
    return scheme === "pmfby"
      ? t("chat.starter1")
      : `${t("nav.schemes")}: ${scheme.replace(/-/g, " ")}`;
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, typing]);

  // Auto-grow composer
  useEffect(() => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [input]);

  useEffect(() => {
    const q = sp?.get("q");
    const scheme = sp?.get("scheme");
    if (q) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInput(q);
      setMsgs([]);
    } else if (scheme) {
      setInput(factoryPrompt(scheme));
      setMsgs([]);
    }
  }, [sp]);

  // Re-translate chat history when UI language changes
  useEffect(() => {
    if (msgs.length === 0) return;
    let isCurrent = true;

    async function translateChatHistory() {
      const updatedMsgs = await Promise.all(
        msgs.map(async (m) => {
          if (m.role === "assistant" && m.resp && m.resp.language !== locale && !m.resp.abstained) {
            try {
              const translatedAnswer = await translate(m.resp.answer, locale);
              return {
                ...m,
                resp: {
                  ...m.resp,
                  answer: translatedAnswer,
                  language: locale,
                },
              };
            } catch {
              return m;
            }
          }
          return m;
        })
      );

      if (isCurrent) {
        setMsgs(updatedMsgs);
      }
    }

    translateChatHistory();

    return () => {
      isCurrent = false;
    };
  }, [locale]);

  async function ask(q?: string) {
    const question = (q ?? input).trim();
    if (!question || typing) return;
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: question }]);

    setHistory((prev) => (prev.includes(question) ? prev : [question, ...prev]));

    // Close sidebar on mobile/tablet when query starts
    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }

    setTyping(true);
    try {
      const backendQuestion = locale === sendLang ? question : await translate(question, sendLang);
      const resp = await sendChat({ question: backendQuestion, session_id: sessionId, language: sendLang, state: null });
      let answer = resp.answer;
      if (resp.language !== locale && !resp.abstained) {
        answer = await translate(answer, locale);
      }
      setMsgs((m) => [...m, { role: "assistant", resp: { ...resp, answer, language: locale } }]);
    } catch {
      setMsgs((m) => [...m, { role: "assistant", resp: fallback(lang) }]);
    } finally {
      setTyping(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      ask();
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

  function handleNewChat() {
    setMsgs([]);
    setInput("");
    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  }

  const suggestedActions = [
    { icon: "📈", label: t("nav.schemes") || "Crop Insurance", prompt: t("chat.starter1") },
    { icon: "⚡", label: t("nav.services") || "Services", prompt: t("chat.starter2") },
    { icon: "🌾", label: t("nav.library") || "PACS Services", prompt: t("chat.starter3") },
    { icon: "⚖️", label: t("nav.legal") || "Legal Framework", prompt: t("chat.starter4") },
  ];

  return (
    <div className="relative flex h-[calc(100dvh-8rem-env(safe-area-inset-bottom))] w-full overflow-hidden bg-[var(--canvas)] text-[var(--ink)] lg:h-[calc(100dvh-3.5rem)]">
      {/* Mobile Backdrop Overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-xs lg:hidden"
          aria-hidden="true"
        />
      )}

      {/* ==================== LEFT SIDEBAR (Mobile Responsive Drawer + Desktop Sidebar) ==================== */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex flex-col border-r border-[var(--border-soft)] bg-[var(--cream)] transition-all duration-300 lg:relative lg:z-0 ${
          sidebarOpen
            ? "w-72 min-w-[18rem] translate-x-0 shadow-2xl lg:shadow-none"
            : "w-0 min-w-0 -translate-x-full overflow-hidden lg:translate-x-0"
        }`}
      >
        {/* New Chat Button */}
        <div className="p-3">
          <button
            type="button"
            onClick={handleNewChat}
            className="flex w-full items-center justify-center gap-2 rounded-[var(--radius-cta)] bg-[var(--dark)] px-4 py-3 text-sm font-semibold text-[var(--on-dark-strong)] shadow-sm transition-all hover:bg-[var(--ink)] active:scale-[0.99]"
          >
            <IconPlus className="h-4 w-4" />
            <span>{t("common.newSession") || "New Chat"}</span>
          </button>
        </div>

        {/* History & Recent Chats Section */}
        <div className="flex-1 overflow-y-auto px-3 py-2">
          <div className="mb-2 flex items-center justify-between px-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-faint)]">
            <span className="flex items-center gap-1.5">
              <IconClock className="h-3.5 w-3.5 text-[var(--text-tertiary)]" />
              Recent History
            </span>
            {history.length > 0 && (
              <button
                type="button"
                onClick={() => setHistory([])}
                title="Clear History"
                className="text-[var(--text-faint)] hover:text-[var(--state-error)]"
              >
                <IconTrash className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          <div className="space-y-1">
            {history.map((item, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => ask(item)}
                className="group flex w-full items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-left text-xs font-medium text-[var(--ink)] transition-colors hover:bg-[var(--cream-2)]"
              >
                <IconClock className="h-3.5 w-3.5 shrink-0 text-[var(--text-faint)] group-hover:text-[var(--accent-primary)]" />
                <span className="truncate">{item}</span>
              </button>
            ))}
          </div>

          {/* Quick Links & Tools Section */}
          <div className="mt-6 border-t border-[var(--border-soft)] pt-4">
            <div className="mb-2 px-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-faint)]">
              Explore & Resources
            </div>
            <nav className="space-y-1">
              <Link
                href="/schemes"
                onClick={() => typeof window !== "undefined" && window.innerWidth < 1024 && setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-xs font-medium text-[var(--ink)] transition-colors hover:bg-[var(--cream-2)]"
              >
                <IconGrid className="h-4 w-4 text-[var(--accent-primary)]" />
                <span>{t("nav.schemes")}</span>
              </Link>
              <Link
                href="/services"
                onClick={() => typeof window !== "undefined" && window.innerWidth < 1024 && setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-xs font-medium text-[var(--ink)] transition-colors hover:bg-[var(--cream-2)]"
              >
                <IconDoc className="h-4 w-4 text-[var(--accent-primary)]" />
                <span>{t("nav.services")}</span>
              </Link>
              <Link
                href="/library"
                onClick={() => typeof window !== "undefined" && window.innerWidth < 1024 && setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-xs font-medium text-[var(--ink)] transition-colors hover:bg-[var(--cream-2)]"
              >
                <IconDoc className="h-4 w-4 text-[var(--accent-primary)]" />
                <span>{t("nav.library")}</span>
              </Link>
              <Link
                href="/legal"
                onClick={() => typeof window !== "undefined" && window.innerWidth < 1024 && setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-xs font-medium text-[var(--ink)] transition-colors hover:bg-[var(--cream-2)]"
              >
                <IconScale className="h-4 w-4 text-[var(--accent-primary)]" />
                <span>{t("nav.legal")}</span>
              </Link>
              <Link
                href="/faq"
                onClick={() => typeof window !== "undefined" && window.innerWidth < 1024 && setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-xs font-medium text-[var(--ink)] transition-colors hover:bg-[var(--cream-2)]"
              >
                <IconHelp className="h-4 w-4 text-[var(--accent-primary)]" />
                <span>{t("nav.faq")}</span>
              </Link>
            </nav>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="border-t border-[var(--border-soft)] p-3">
          <div className="flex items-center gap-3 rounded-[var(--radius-md)] bg-[var(--canvas)] p-2.5 shadow-2xs">
            <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-white">
              <IconBot className="h-4 w-4" />
              <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-[var(--canvas)] bg-[var(--state-success)]" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-[var(--ink)]">Sahakarita Copilot</p>
              <p className="truncate text-[11px] text-[var(--text-faint)]">Online · {locale.toUpperCase()}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* ==================== MAIN CHAT WORKSPACE (Full Responsive Size) ==================== */}
      <main className="flex flex-1 flex-col overflow-hidden bg-[var(--canvas)]">
        {/* Workspace Top Control Bar */}
        <div className="flex h-12 shrink-0 items-center justify-between border-b border-[var(--border-soft)] bg-[var(--canvas)] px-3 sm:px-4">
          <div className="flex items-center gap-2 sm:gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen((s) => !s)}
              title="Toggle Sidebar"
              className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] border border-[var(--border-soft)] text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
            >
              <IconSidebar className="h-4 w-4" />
            </button>
            <div className="flex items-center gap-2">
              <span className="text-xs sm:text-sm font-semibold tracking-tight text-[var(--ink)]">{t("nav.chat")}</span>
              <span className="rounded-full border border-[var(--border-soft)] bg-[var(--cream)] px-2 py-0.5 text-[10px] font-medium text-[var(--text-secondary)]">
                {locale.toUpperCase()}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleNewChat} className="gap-1 text-xs">
              <IconPlus className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">{t("common.newSession")}</span>
            </Button>
          </div>
        </div>

        {/* Messages Stream Container */}
        <div className="flex-1 space-y-6 overflow-y-auto p-3 sm:p-6 md:p-8">
          <div className="mx-auto max-w-4xl space-y-6">
            {msgs.length === 0 && (
              <Reveal trigger="load">
                <div className="flex items-start gap-3 sm:gap-4">
                  <div className="flex h-9 w-9 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-[var(--radius-md)] bg-[var(--dark)] text-[var(--on-dark-strong)] shadow-sm">
                    <IconBot className="h-5 w-5" />
                  </div>
                  <div className="w-full rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-4 sm:p-6 shadow-[0_4px_20px_rgba(0,0,0,0.03)]">
                    <h2 className="text-lg sm:text-xl font-semibold tracking-tight text-[var(--ink)]">
                      Sahakarita AI Copilot 🚀
                    </h2>
                    <p className="mt-2 text-xs sm:text-sm leading-relaxed text-[var(--text-body)]">
                      {t("chat.welcome")}
                    </p>

                    <div className="mt-4 sm:mt-5 flex items-center justify-between border-t border-[var(--border-soft)] pt-3 sm:pt-4">
                      <Link href="/schemes">
                        <button
                          type="button"
                          className="inline-flex items-center gap-2 rounded-[var(--radius-cta)] border border-[var(--accent-primary)]/40 bg-[var(--cream)] px-3.5 sm:px-4 py-1.5 sm:py-2 text-xs font-semibold text-[var(--ink)] transition-colors hover:border-[var(--accent-primary)] hover:bg-[var(--cream-2)]"
                        >
                          {t("landing.ctaSchemes")}
                          <IconChevronRight className="h-4 w-4 text-[var(--accent-primary)]" />
                        </button>
                      </Link>
                      <span className="text-[11px] text-[var(--text-faint)]">Just now</span>
                    </div>
                  </div>
                </div>
              </Reveal>
            )}

            {msgs.map((m, i) =>
              m.role === "user" ? (
                <div
                  key={i}
                  className="ml-auto w-fit max-w-[85%] sm:max-w-[78%] rounded-[var(--radius-lg)] border border-[var(--dark)] bg-[var(--dark)] px-3.5 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm text-[var(--on-dark-strong)] shadow-sm"
                >
                  {m.text}
                </div>
              ) : (
                <MessageBubble key={i} resp={m.resp!} />
              )
            )}

            {typing && (
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[var(--radius-md)] bg-[var(--dark)] text-[var(--on-dark-strong)]">
                  <IconBot className="h-5 w-5" />
                </span>
                <Skeleton className="h-16 w-2/3 max-w-[28rem]" />
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Suggested Actions Section (Horizontally scrollable on mobile) */}
        <div className="border-t border-[var(--border-soft)] bg-[var(--cream-2)]/30 px-3 py-2.5 sm:px-6 md:px-8">
          <div className="mx-auto max-w-4xl">
            <div className="mb-1.5 flex items-center gap-1.5 text-[11px] sm:text-xs font-semibold uppercase tracking-wider text-[var(--text-body)]">
              <IconSparkles className="h-3.5 w-3.5 text-[var(--accent-primary)]" />
              <span>Suggested Actions</span>
            </div>
            <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar sm:flex-wrap">
              {suggestedActions.map((action) => (
                <button
                  key={action.label}
                  type="button"
                  onClick={() => ask(action.prompt)}
                  className="inline-flex shrink-0 items-center gap-1.5 rounded-[var(--radius-cta)] border border-[var(--border-soft)] bg-[var(--canvas)] px-3 py-1.5 text-xs font-medium text-[var(--ink)] shadow-2xs transition-all hover:border-[var(--border-hover)] hover:bg-[var(--cream)] active:translate-y-0"
                >
                  <span>{action.icon}</span>
                  <span>{action.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Input Composer */}
        <div className="border-t border-[var(--border-soft)] bg-[var(--canvas)] p-3 sm:px-6 md:px-8 md:py-4">
          <div className="mx-auto max-w-4xl">
            <div className="ask-input-wrap flex items-center gap-2 sm:gap-3 rounded-[var(--radius-cta)] border border-[var(--border-default)] bg-[var(--cream)] px-3 sm:px-4 py-2 sm:py-2.5 shadow-[0_4px_20px_rgba(0,0,0,0.04)] transition-all focus-within:border-[var(--accent-primary)] focus-within:ring-1 focus-within:ring-[var(--accent-primary)]">
              {/* Mic Button */}
              {speech.supported && (
                <Button
                  variant="icon"
                  size="sm"
                  aria-label={listening ? t("common.stopMic") : t("common.mic")}
                  onClick={toggleMic}
                  className={`shrink-0 transition-transform ${
                    listening
                      ? "bg-[var(--accent-primary)] text-[var(--accent-contrast)] animate-pulse"
                      : "text-[var(--text-body)] hover:text-[var(--ink)]"
                  }`}
                >
                  <IconMic className="h-4 w-4" />
                </Button>
              )}

              {/* Textarea Input */}
              <textarea
                ref={taRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                rows={1}
                placeholder={t("chat.placeholder") || "Type your question..."}
                aria-label={t("chat.placeholder") || "Type your question..."}
                className="block w-full flex-1 min-w-0 resize-none bg-transparent py-1 font-answer text-xs sm:text-base leading-normal text-[var(--ink)] placeholder:text-[var(--text-faint)] focus:outline-none"
              />

              {/* Integrated Model Selection Dropdown */}
              <div className="relative shrink-0">
                <button
                  type="button"
                  onClick={() => setShowModelPicker((p) => !p)}
                  className="inline-flex items-center gap-1 rounded-[var(--radius-cta)] border border-[var(--border-soft)] bg-[var(--canvas)] px-2 sm:px-3 py-1 sm:py-1.5 text-[11px] sm:text-xs font-semibold text-[var(--ink)] transition-colors hover:border-[var(--border-hover)] hover:bg-[var(--cream-2)]"
                >
                  <span className="truncate max-w-[5rem] sm:max-w-none">{model}</span>
                  <span className="text-[9px] text-[var(--text-tertiary)]">▼</span>
                </button>

                {showModelPicker && (
                  <div className="absolute right-0 bottom-full z-30 mb-2 w-40 sm:w-44 rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-1 shadow-lg">
                    {MODELS.map((m) => (
                      <button
                        key={m}
                        type="button"
                        onClick={() => {
                          setModel(m);
                          setShowModelPicker(false);
                        }}
                        className={`flex w-full items-center justify-between rounded-[var(--radius-sm)] px-2.5 py-1.5 text-left text-xs ${
                          model === m
                            ? "bg-[var(--dark)] font-semibold text-[var(--on-dark-strong)]"
                            : "text-[var(--ink)] hover:bg-[var(--cream-2)]"
                        }`}
                      >
                        <span className="truncate">{m}</span>
                        {model === m && <span>✓</span>}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Circular Send Button */}
              <button
                type="button"
                aria-label={t("common.send")}
                disabled={!input.trim() || typing}
                onClick={() => ask()}
                className="flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-[var(--accent-contrast)] shadow-sm transition-all hover:bg-[var(--accent-hover)] hover:scale-105 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                <IconSend className="h-4 w-4" />
              </button>
            </div>

            {/* Footer Subtext */}
            <div className="mt-1.5 flex items-center justify-between px-1 text-[10px] sm:text-[11px] text-[var(--text-faint)]">
              <span>Press Enter to send</span>
              <span className="hidden sm:inline">Powered by Sahakarita Intelligence</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
