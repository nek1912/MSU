"use client";
import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { sendChat, ChatResponse } from "@/lib/api";
import { useI18n } from "@/lib/i18n/provider";
import type { Locale } from "@/lib/i18n/i18n";
import { createSpeechService } from "@/lib/speech";
import { MessageBubble } from "./chat/MessageBubble";
import { LanguageSwitcher } from "@/components/layout/LanguageSwitcher";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { Reveal } from "@/components/motion/Reveal";
import {
  IconMic,
  IconTrash,
  IconSparkles,
  IconSend,
  IconPlus,
  IconSidebar,
  IconClock,
  IconBot,
  IconArrowLeft,
  IconPin,
  IconSearch,
  IconEdit,
  IconShare,
  IconUser,
  IconCompass,
  IconX,
} from "@/components/ui/Icons";

type Msg = { role: "user" | "assistant"; text?: string; resp?: ChatResponse };

interface Conversation {
  id: string;
  title: string;
  messages: Msg[];
  createdAt: number;
  updatedAt?: number;
  pinned?: boolean;
}

const STORAGE_KEY = "sahakarita_conversations";
const MODELS = ["Sahakarita-v2.5"];

function loadConversations(): Conversation[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveConversations(convs: Conversation[]) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(convs));
  } catch {
    // localStorage full or unavailable
  }
}

function fallback(lang: Locale): ChatResponse {
  return {
    answer:
      lang === "hi"
        ? "सेवा अभी उपलब्ध नहीं है।"
        : lang === "gu"
        ? "સેવા હમણાં ઉપલબ્ધ નથી."
        : "Service unavailable right now.",
    language: lang,
    domain: "unknown",
    intent: "unknown",
    entities: [],
    confidence: 0,
    confidence_level: "none",
    citations: [],
    abstained: true,
    follow_up_question: null,
  };
}

export function ChatWindow() {
  const router = useRouter();
  const { t, locale } = useI18n();
  const speech = useMemo(() => createSpeechService(), []);
  const [speechReady, setSpeechReady] = useState(false);
  const sp = useSearchParams();
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [typing, setTyping] = useState(false);
  const [listening, setListening] = useState(false);
  const [model, setModel] = useState(MODELS[0]);
  const [showModelPicker, setShowModelPicker] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearchInput, setShowSearchInput] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const cancelListen = useRef<(() => void) | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const lang: Locale = locale;

  // Load conversations from localStorage on mount
  useEffect(() => {
    setConversations(loadConversations());
  }, []);

  // Client-only speech readiness
  useEffect(() => {
    setSpeechReady(true);
  }, []);

  // Auto-expand sidebar on large screens
  useEffect(() => {
    if (typeof window !== "undefined" && window.innerWidth >= 1024) {
      setSidebarOpen(true);
    }
  }, []);

  // Auto-save current conversation when msgs change
  useEffect(() => {
    if (msgs.length === 0 || !activeConvId) return;
    setConversations((prev) => {
      const next = prev.map((c) =>
        c.id === activeConvId
          ? { ...c, messages: msgs, updatedAt: Date.now() }
          : c
      );
      saveConversations(next);
      return next;
    });
  }, [msgs, activeConvId]);

  // Create a new conversation
  const createConversation = useCallback((firstMsg: Msg) => {
    const conv: Conversation = {
      id: crypto.randomUUID(),
      title: firstMsg.text?.slice(0, 50) || "New Chat",
      messages: [firstMsg],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      pinned: false,
    };
    setConversations((prev) => {
      const next = [conv, ...prev];
      saveConversations(next);
      return next;
    });
    setActiveConvId(conv.id);
    setMsgs([firstMsg]);
    return conv.id;
  }, []);

  // Load a conversation from sidebar
  const loadConversation = useCallback((conv: Conversation) => {
    setMsgs(conv.messages);
    setActiveConvId(conv.id);
    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  }, []);

  // Pin/Unpin a conversation
  const togglePinConversation = useCallback((convId: string, e?: React.MouseEvent) => {
    e?.stopPropagation();
    setConversations((prev) => {
      const next = prev.map((c) =>
        c.id === convId ? { ...c, pinned: !c.pinned } : c
      );
      saveConversations(next);
      return next;
    });
  }, []);

  // Delete a conversation
  const deleteConversation = useCallback(
    (convId: string, e: React.MouseEvent) => {
      e.stopPropagation();
      setConversations((prev) => {
        const next = prev.filter((c) => c.id !== convId);
        saveConversations(next);
        return next;
      });
      if (activeConvId === convId) {
        setMsgs([]);
        setActiveConvId(null);
      }
    },
    [activeConvId]
  );

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, typing]);

  // Auto-grow composer
  useEffect(() => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 180) + "px";
  }, [input]);

  useEffect(() => {
    const q = sp?.get("q") || (typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("q") : null);
    const scheme = sp?.get("scheme") || (typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("scheme") : null);
    const schemeName = sp?.get("name") || (typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("name") : null);
    if (q) {
      setInput(q);
      setMsgs([]);
      setActiveConvId(null);
    } else if (scheme) {
      if (scheme === "pmfby") {
        setInput(t("chat.starter1"));
      } else if (schemeName) {
        setInput(`Tell me about ${schemeName} scheme`);
      } else {
        setInput(`Tell me about ${scheme.replace(/-/g, " ")} scheme`);
      }
      setMsgs([]);
      setActiveConvId(null);
    }
  }, [sp, t]);

  async function ask(q?: string) {
    const question = (q ?? input).trim();
    if (!question || typing) return;
    setInput("");

    const userMsg: Msg = { role: "user", text: question };

    if (!activeConvId) {
      createConversation(userMsg);
    } else {
      setMsgs((m) => [...m, userMsg]);
    }

    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }

    setTyping(true);
    try {
      const history = msgs
        .filter((m): m is Msg & { text: string } => !!m.text)
        .slice(-5)
        .map(m => ({ role: m.role, content: m.text }));

      const resp = await sendChat({ question, session_id: sessionId, language: lang, state: null, history });
      const assistantMsg: Msg = { role: "assistant", resp };
      setMsgs((m) => [...m, assistantMsg]);
    } catch {
      const assistantMsg: Msg = { role: "assistant", resp: fallback(lang) };
      setMsgs((m) => [...m, assistantMsg]);
    } finally {
      setTyping(false);
    }
  }

  function handleNewChat() {
    setMsgs([]);
    setInput("");
    setActiveConvId(null);
    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  }

  function handleBack() {
    if (window.history.length > 1) {
      router.back();
    } else {
      router.push("/");
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

  const suggestedActions = [
    { icon: "🌾", label: t("nav.schemes") || "Crop Insurance", prompt: t("chat.starter1") },
    { icon: "⚡", label: t("nav.services") || "Services", prompt: t("chat.starter2") },
    { icon: "🏛️", label: t("nav.library") || "PACS Services", prompt: t("chat.starter3") },
    { icon: "⚖️", label: t("nav.legal") || "Legal Framework", prompt: t("chat.starter4") },
  ];

  function formatTime(ts: number) {
    const d = new Date(ts);
    const now = new Date();
    if (d.toDateString() === now.toDateString()) {
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
    return d.toLocaleDateString([], { month: "short", day: "numeric" });
  }

  // Filter conversations
  const filteredConversations = useMemo(() => {
    if (!searchQuery.trim()) return conversations;
    return conversations.filter((c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [conversations, searchQuery]);

  const pinnedConversations = useMemo(() => {
    return filteredConversations.filter((c) => c.pinned);
  }, [filteredConversations]);

  const recentConversations = useMemo(() => {
    return filteredConversations.filter((c) => !c.pinned);
  }, [filteredConversations]);

  return (
    <div className="relative flex h-dvh w-full overflow-hidden bg-[var(--canvas)] text-[var(--ink)] font-sans">
      {/* Mobile Backdrop Overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-xs lg:hidden"
          aria-hidden="true"
        />
      )}

      {/* ==================== LEFT SIDEBAR ==================== */}
      {/* Collapsed Rail (desktop icon sidebar like ChatGPT) */}
      {!sidebarOpen && (
        <aside className="hidden lg:flex inset-y-0 left-0 z-40 w-16 flex-col items-center border-r border-[var(--border-soft)] bg-[var(--cream)] py-3">
          {/* Toggle Sidebar */}
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            title="Open Sidebar"
            className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
          >
            <IconSidebar className="h-5 w-5" />
          </button>

          {/* New Chat Icon */}
          <button
            type="button"
            onClick={handleNewChat}
            title="New Chat"
            className="mt-2 flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
          >
            <IconEdit className="h-5 w-5" />
          </button>

          <div className="my-2 h-[1px] w-8 bg-[var(--border-soft)]" />

          {/* Icon List of Conversations */}
          <div className="flex-1 w-full overflow-y-auto space-y-1.5 px-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                type="button"
                onClick={() => loadConversation(conv)}
                title={conv.title}
                className={`group flex h-9 w-full items-center justify-center rounded-[var(--radius-md)] transition-colors hover:bg-[var(--cream-2)] ${
                  activeConvId === conv.id ? "bg-[var(--cream-2)] text-[var(--accent-primary)]" : "text-[var(--text-faint)]"
                }`}
              >
                {conv.pinned ? (
                  <IconPin className="h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
                ) : (
                  <IconClock className="h-4 w-4 shrink-0 group-hover:text-[var(--ink)]" />
                )}
              </button>
            ))}
          </div>

          {/* Footer User Profile */}
          <div className="mt-auto pt-2">
            <Link
              href="/"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--dark)] text-[var(--on-dark-strong)] shadow-xs transition-transform hover:scale-105"
              title="Sahakarita Home"
            >
              <IconBot className="h-5 w-5" />
            </Link>
          </div>
        </aside>
      )}

      {/* Expanded Sidebar (ChatGPT Style) */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex flex-col border-r border-[var(--border-soft)] bg-[var(--cream)] transition-all duration-300 lg:relative lg:z-0 ${
          sidebarOpen
            ? "w-72 min-w-[18rem] translate-x-0 shadow-2xl lg:shadow-none"
            : "w-0 min-w-0 -translate-x-full overflow-hidden lg:hidden"
        }`}
      >
        {/* Sidebar Header with ChatGPT-like Icons */}
        <div className="flex items-center justify-between p-3 border-b border-[var(--border-soft)]/60">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setSidebarOpen(false)}
              title="Close Sidebar"
              className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
            >
              <IconSidebar className="h-4.5 w-4.5" />
            </button>
          </div>

          <div className="flex items-center gap-1">
            {/* Search Toggle */}
            <button
              type="button"
              onClick={() => setShowSearchInput((s) => !s)}
              title="Search History"
              className={`flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] transition-colors hover:bg-[var(--cream-2)] ${
                showSearchInput ? "bg-[var(--cream-2)] text-[var(--accent-primary)]" : "text-[var(--text-body)]"
              }`}
            >
              <IconSearch className="h-4 w-4" />
            </button>

            {/* New Chat Button */}
            <button
              type="button"
              onClick={handleNewChat}
              title="New Chat"
              className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
            >
              <IconEdit className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Search Input Bar (if open) */}
        {showSearchInput && (
          <div className="px-3 pt-2.5 pb-1">
            <div className="relative flex items-center rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] px-2.5 py-1.5 shadow-2xs">
              <IconSearch className="h-3.5 w-3.5 shrink-0 text-[var(--text-faint)]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search history..."
                className="w-full bg-transparent px-2 text-xs text-[var(--ink)] placeholder:text-[var(--text-faint)] focus:outline-none"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="text-[var(--text-faint)] hover:text-[var(--ink)]"
                >
                  <IconX className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          </div>
        )}

        {/* Main Sidebar Navigation & History List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-4">
          {/* ChatGPT Style Top Links */}
          <div className="space-y-0.5">
            <button
              type="button"
              onClick={handleNewChat}
              className="flex w-full items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-left text-xs font-semibold transition-colors hover:bg-[var(--cream-2)] text-[var(--ink)]"
            >
              <IconPlus className="h-4 w-4 text-[var(--accent-primary)] shrink-0" />
              <span>{t("common.newSession") || "New chat"}</span>
            </button>
          </div>

          {/* PINNED SECTION */}
          {pinnedConversations.length > 0 && (
            <div>
              <div className="mb-1.5 flex items-center justify-between px-2 text-[11px] font-bold uppercase tracking-wider text-[var(--text-tertiary)]">
                <span className="flex items-center gap-1.5">
                  <IconPin className="h-3.5 w-3.5 text-[var(--accent-primary)]" />
                  Pinned
                </span>
                <span className="text-[10px] text-[var(--text-faint)] font-mono">{pinnedConversations.length}</span>
              </div>
              <div className="space-y-0.5">
                {pinnedConversations.map((conv) => (
                  <button
                    key={conv.id}
                    type="button"
                    onClick={() => loadConversation(conv)}
                    className={`group flex w-full items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-left text-xs font-medium transition-colors hover:bg-[var(--cream-2)] ${
                      activeConvId === conv.id
                        ? "bg-[var(--cream-2)] font-semibold text-[var(--ink)] border-l-2 border-[var(--accent-primary)]"
                        : "text-[var(--ink)]"
                    }`}
                  >
                    <IconPin className="h-3.5 w-3.5 shrink-0 text-[var(--accent-primary)]" />
                    <div className="min-w-0 flex-1">
                      <span className="block truncate">{conv.title}</span>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => togglePinConversation(conv.id, e)}
                      title="Unpin"
                      className="shrink-0 p-1 text-[var(--accent-primary)] hover:opacity-75"
                    >
                      <IconPin className="h-3 w-3" />
                    </button>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* RECENT HISTORY SECTION */}
          <div>
            <div className="mb-1.5 flex items-center justify-between px-2 text-[11px] font-bold uppercase tracking-wider text-[var(--text-tertiary)]">
              <span className="flex items-center gap-1.5">
                <IconClock className="h-3.5 w-3.5 text-[var(--text-tertiary)]" />
                Recent history
              </span>
              {conversations.length > 0 && (
                <button
                  type="button"
                  onClick={() => {
                    setConversations([]);
                    saveConversations([]);
                    setMsgs([]);
                    setActiveConvId(null);
                  }}
                  title="Clear History"
                  className="text-[var(--text-faint)] hover:text-[var(--state-error)] transition-colors"
                >
                  <IconTrash className="h-3.5 w-3.5" />
                </button>
              )}
            </div>

            <div className="space-y-0.5">
              {recentConversations.length === 0 && pinnedConversations.length === 0 && (
                <p className="px-2 py-6 text-center text-xs text-[var(--text-faint)] italic">
                  No chat history yet
                </p>
              )}

              {recentConversations.map((conv) => (
                <button
                  key={conv.id}
                  type="button"
                  onClick={() => loadConversation(conv)}
                  className={`group flex w-full items-center gap-2.5 rounded-[var(--radius-md)] px-2.5 py-2 text-left text-xs font-medium transition-colors hover:bg-[var(--cream-2)] ${
                    activeConvId === conv.id
                      ? "bg-[var(--cream-2)] font-semibold text-[var(--ink)] border-l-2 border-[var(--accent-primary)]"
                      : "text-[var(--ink)]"
                  }`}
                >
                  <IconClock className="h-3.5 w-3.5 shrink-0 text-[var(--text-faint)] group-hover:text-[var(--accent-primary)]" />
                  <div className="min-w-0 flex-1">
                    <span className="block truncate">{conv.title}</span>
                    <span className="text-[10px] text-[var(--text-faint)] block truncate">
                      {formatTime(conv.updatedAt || conv.createdAt)}
                    </span>
                  </div>
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      type="button"
                      onClick={(e) => togglePinConversation(conv.id, e)}
                      title="Pin chat"
                      className="p-1 text-[var(--text-faint)] hover:text-[var(--accent-primary)]"
                    >
                      <IconPin className="h-3 w-3" />
                    </button>
                    <button
                      type="button"
                      onClick={(e) => deleteConversation(conv.id, e)}
                      title="Delete"
                      className="p-1 text-[var(--text-faint)] hover:text-[var(--state-error)]"
                    >
                      <IconTrash className="h-3 w-3" />
                    </button>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar Footer with User Account */}
        <div className="border-t border-[var(--border-soft)] p-3">
          <div className="flex items-center gap-3 rounded-[var(--radius-md)] bg-[var(--canvas)] p-2 shadow-2xs">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--dark)] text-[var(--on-dark-strong)]">
              <IconUser className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-[var(--ink)]">Sahakarita User</p>
              <p className="truncate text-[10px] text-[var(--text-faint)] font-mono">Free Plan</p>
            </div>
          </div>
        </div>
      </aside>

      {/* ==================== MAIN CENTERED CHAT AREA ==================== */}
      <main className="flex flex-1 flex-col overflow-hidden bg-[var(--canvas)] min-w-0">
        {/* Top Header Bar */}
        <header className="flex h-13 shrink-0 items-center justify-between border-b border-[var(--border-soft)] bg-[var(--canvas)] px-3 sm:px-4">
          <div className="flex items-center gap-2">
            {/* BACK BUTTON TO LEAVE CHAT ROUTE */}
            <button
              type="button"
              onClick={handleBack}
              title="Back"
              className="flex items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--border-soft)] px-2.5 py-1.5 text-xs font-semibold text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
            >
              <IconArrowLeft className="h-4 w-4" />
              <span className="hidden sm:inline">Back</span>
            </button>

            {/* Sidebar toggle */}
            <button
              type="button"
              onClick={() => setSidebarOpen((s) => !s)}
              title="Toggle Sidebar"
              className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] border border-[var(--border-soft)] text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
            >
              <IconSidebar className="h-4 w-4" />
            </button>

            {/* Model Badge */}
            <div className="relative ml-1">
              <span className="flex items-center gap-1.5 rounded-[var(--radius-md)] px-2.5 py-1 text-sm font-semibold text-[var(--ink)]">
                <span>{model}</span>
                <span className="text-[10px] text-[var(--text-faint)]">▼</span>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <button
              type="button"
              onClick={handleNewChat}
              title="New Chat"
              className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] border border-[var(--border-soft)] text-[var(--text-body)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
            >
              <IconPlus className="h-4 w-4" />
            </button>
          </div>
        </header>

        {/* Center Aligned Message Stream Area */}
        <div className="flex-1 overflow-y-auto w-full">
          <div className="mx-auto w-full max-w-3xl px-4 sm:px-6 py-6 space-y-6">
            {/* ChatGPT Style Empty State Hero */}
            {msgs.length === 0 && (
              <Reveal trigger="load">
                <div className="py-12 sm:py-20 text-center space-y-4">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[var(--dark)] text-[var(--on-dark-strong)] shadow-md">
                    <IconBot className="h-7 w-7" />
                  </div>
                  <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[var(--ink)]">
                    What can I help with today?
                  </h1>
                  <p className="text-sm text-[var(--text-body)] max-w-md mx-auto">
                    Ask any question about PACS cooperative schemes, crop insurance (PMFBY), services, or legal frameworks.
                  </p>

                  {/* 2x2 Suggested Actions Grid Centered */}
                  <div className="pt-6 grid grid-cols-1 sm:grid-cols-2 gap-3 text-left max-w-2xl mx-auto">
                    {suggestedActions.map((action) => (
                      <button
                        key={action.label}
                        type="button"
                        onClick={() => {
                          setInput(action.prompt);
                          taRef.current?.focus();
                        }}
                        className="group flex flex-col justify-between rounded-xl border border-[var(--border-soft)] bg-[var(--cream)] p-3.5 transition-all hover:border-[var(--accent-primary)]/40 hover:bg-[var(--cream-2)] hover:shadow-sm"
                      >
                        <div className="flex items-center gap-2 font-medium text-xs text-[var(--ink)]">
                          <span className="text-base">{action.icon}</span>
                          <span>{action.label}</span>
                        </div>
                        <p className="mt-1.5 text-xs text-[var(--text-tertiary)] line-clamp-2">
                          {action.prompt}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              </Reveal>
            )}

            {/* Conversation Messages */}
            {msgs.map((m, i) =>
              m.role === "user" ? (
                <div key={i} className="flex justify-end">
                  <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl bg-[var(--dark)] px-4 py-3 text-xs sm:text-sm leading-relaxed text-[var(--on-dark-strong)] shadow-2xs">
                    {m.text}
                  </div>
                </div>
              ) : (
                <MessageBubble key={i} resp={m.resp!} />
              )
            )}

            {typing && (
              <div className="flex gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--dark)] text-[var(--on-dark-strong)]">
                  <IconBot className="h-4 w-4 animate-pulse" />
                </div>
                <Skeleton className="h-16 w-3/4 max-w-[28rem] rounded-xl" />
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Center Aligned Floating Input Composer (ChatGPT Style) */}
        <div className="w-full bg-[var(--canvas)] pb-3 pt-2">
          <div className="mx-auto w-full max-w-3xl px-4 sm:px-6">
            <div className="ask-input-wrap relative flex flex-col rounded-3xl border border-[var(--border-default)] bg-[var(--cream)] p-2.5 sm:p-3 shadow-md transition-all focus-within:border-[var(--accent-primary)] focus-within:ring-1 focus-within:ring-[var(--accent-primary)]">
              {/* Text Area */}
              <textarea
                ref={taRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                rows={1}
                placeholder={t("chat.placeholder") || "Ask anything..."}
                aria-label={t("chat.placeholder") || "Ask anything..."}
                className="w-full resize-none bg-transparent px-2 py-1 font-answer text-xs sm:text-base leading-relaxed text-[var(--ink)] placeholder:text-[var(--text-faint)] focus:outline-none min-h-[40px]"
              />

              {/* Input Toolbar */}
              <div className="mt-2 flex items-center justify-end pt-1 gap-2">
                {/* Speech Mic */}
                {speechReady && speech.supported && (
                  <button
                    type="button"
                    aria-label={listening ? t("common.stopMic") : t("common.mic")}
                    onClick={toggleMic}
                    className={`flex h-8 w-8 items-center justify-center rounded-full transition-colors ${
                      listening
                        ? "bg-[var(--accent-primary)] text-[var(--accent-contrast)] animate-pulse"
                        : "text-[var(--text-body)] hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
                    }`}
                  >
                    <IconMic className="h-4 w-4" />
                  </button>
                )}

                {/* ChatGPT Circular Send Button */}
                <button
                  type="button"
                  aria-label={t("common.send")}
                  disabled={!input.trim() || typing}
                  onClick={() => ask()}
                  className="flex h-8 w-8 sm:h-9 sm:w-9 items-center justify-center rounded-full bg-[var(--accent-primary)] text-[var(--accent-contrast)] shadow-sm transition-all hover:bg-[var(--accent-hover)] hover:scale-105 active:scale-95 disabled:opacity-35 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  <IconSend className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Sub-caption Disclaimer Centered */}
            <p className="mt-2 text-center text-[10px] sm:text-xs text-[var(--text-faint)]">
              Sahakarita AI can make mistakes. Verify important info.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
