"use client";
import { useState, useMemo, useEffect } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";
import type { ChatResponse } from "@/lib/api";
import { useI18n } from "@/lib/i18n/provider";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import {
  IconSpeaker,
  IconDoc,
  IconChevronRight,
  IconCopy,
  IconCheck,
  IconThumbsUp,
  IconThumbsDown,
  IconBot,
} from "@/components/ui/Icons";
import { deco } from "@/lib/data/deco";
import { createSpeechService, speakSegments } from "@/lib/speech";
import { EvidenceBand } from "@/components/EvidenceBand";
import { evidenceBand } from "@/lib/band";

export function cleanMarkdownForDisplay(text: string): string {
  if (!text) return "";
  let cleaned = text;

  // Remove internal chunk citation tags (e.g. [chunk:123], (chunk:123))
  cleaned = cleaned.replace(/\[chunk:[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\(chunk:[^\)]*\)/gi, "");

  // Fix escaped asterisks (\*\* -> **)
  cleaned = cleaned.replace(/\\\*/g, "*");

  // Format bullet points: replace inline bullets (•) with newlines and markdown dash (- )
  cleaned = cleaned.replace(/([^\n])\s*•\s*/g, "$1\n- ");
  cleaned = cleaned.replace(/^\s*•\s*/gm, "- ");

  // Ensure numbered list items on inline text get proper linebreaks
  cleaned = cleaned.replace(/([^\n])\s*(\d+\.)\s+/g, "$1\n$2 ");

  // Preserve double newlines for paragraph breaks, remove excess newlines
  cleaned = cleaned.replace(/\n{3,}/g, "\n\n");

  return cleaned.trim();
}

export function cleanTextForSpeech(text: string): string {
  if (!text) return "";
  let cleaned = text;

  // Remove chunk citations
  cleaned = cleaned.replace(/\[chunk:[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\(chunk:[^\)]*\)/gi, "");

  // Remove markdown headers
  cleaned = cleaned.replace(/^#+\s+/gm, "");

  // Convert bullet points to sentence endings
  cleaned = cleaned.replace(/^[\s]*[-*+•]\s+/gm, ". ");
  cleaned = cleaned.replace(/([^\n])\s*•\s*/g, "$1. ");

  // Strip markdown formatting symbols
  cleaned = cleaned.replace(/\*\*([^*]+)\*\*/g, "$1");
  cleaned = cleaned.replace(/\*([^*]+)\*/g, "$1");
  cleaned = cleaned.replace(/`([^`]+)`/g, "$1");
  cleaned = cleaned.replace(/\\\*/g, "");

  // Replace newlines with sentence breaks
  cleaned = cleaned.replace(/\n+/g, ". ");

  // Normalize duplicate spaces and periods
  cleaned = cleaned.replace(/\.\s*\./g, ".");
  cleaned = cleaned.replace(/\s+/g, " ").trim();

  return cleaned;
}

export function MessageBubble({ resp, isStreaming = false }: { resp: ChatResponse; isStreaming?: boolean }) {
  const { t } = useI18n();
  const speech = useMemo(() => createSpeechService(), []);
  const [speaking, setSpeaking] = useState(false);
  const [openCitations, setOpenCitations] = useState(false);
  const [copied, setCopied] = useState(false);
  const [rating, setRating] = useState<"up" | "down" | null>(null);

  const segments = resp.speech_segments ?? [];
  const hasSegments = segments.length > 0;
  const domainKey = `domain.${resp.domain}`;
  const domainLabel = t(domainKey).startsWith("domain.") ? resp.domain : t(domainKey);

  async function handleSpeak() {
    if (speaking) {
      speech.stopSpeaking();
      setSpeaking(false);
      return;
    }
    setSpeaking(true);
    try {
      if (hasSegments) {
        await speakSegments(segments);
      } else {
        const cleanText = cleanTextForSpeech(resp.answer);
        await speech.speak(cleanText, resp.language);
      }
    } finally {
      setSpeaking(false);
    }
  }

  function handleCopy() {
    const cleanText = cleanMarkdownForDisplay(resp.answer);
    navigator.clipboard.writeText(cleanText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (resp.abstained) {
    return (
      <Alert tone="warn">
        <span>{t("abstained.title")}</span>
      </Alert>
    );
  }

  return (
    <div className="group flex gap-3 text-sm sm:text-base leading-relaxed text-[var(--ink)]">
      <div className="min-w-0 flex-1 space-y-2">
        <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge deco={deco(resp.domain)}>{domainLabel}</Badge>
            {resp.mode && (
              <span
                className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] sm:text-xs font-medium ${
                  resp.mode === "web"
                    ? "bg-blue-100 text-blue-800"
                    : resp.mode === "grievance"
                      ? "bg-orange-100 text-orange-800"
                      : "bg-gray-100 text-gray-600"
                }`}
              >
                {resp.mode === "web" ? t("chat.mode.webSearch") : resp.mode === "grievance" ? t("chat.mode.grievance") : t("chat.mode.staticRag")}
              </span>
            )}
            <EvidenceBand confidence={resp.confidence} label={t(`evidence.${evidenceBand(resp.confidence)}`)} />
          </div>
          <span className="text-[11px] sm:text-xs text-[var(--text-faint)]">{(resp.confidence * 100).toFixed(0)}% match</span>
        </div>

        {/* Answer Content */}
        <div className={`font-answer text-sm sm:text-base leading-relaxed text-[var(--ink)] prose prose-sm max-w-none prose-headings:font-semibold prose-headings:text-[var(--ink)] prose-p:my-2 prose-p:leading-relaxed prose-ul:my-2.5 prose-ul:list-disc prose-ul:pl-5 prose-ol:my-2.5 prose-ol:list-decimal prose-ol:pl-5 prose-li:my-1 prose-strong:font-semibold prose-strong:text-[var(--ink)] prose-table:text-xs prose-th:font-semibold prose-td:py-1 prose-th:py-1 prose-pre:bg-[var(--dark)] prose-pre:text-[var(--on-dark-strong)] prose-code:text-[var(--accent-primary)] ${isStreaming ? "streaming-text" : ""}`}>
          <Markdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p className="mb-2.5 leading-relaxed text-[var(--ink)]">{children}</p>,
              ul: ({ children }) => <ul className="my-2.5 list-disc pl-5 space-y-1 text-[var(--ink)]">{children}</ul>,
              ol: ({ children }) => <ol className="my-2.5 list-decimal pl-5 space-y-1 text-[var(--ink)]">{children}</ol>,
              li: ({ children }) => <li className="pl-1 leading-relaxed">{children}</li>,
              strong: ({ children }) => <strong className="font-semibold text-[var(--ink)]">{children}</strong>,
              h1: ({ children }) => <h1 className="text-lg font-bold my-2 text-[var(--ink)]">{children}</h1>,
              h2: ({ children }) => <h2 className="text-base font-bold my-2 text-[var(--ink)]">{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm font-semibold my-1.5 text-[var(--ink)]">{children}</h3>,
            }}
          >
            {cleanMarkdownForDisplay(resp.answer)}
          </Markdown>
        </div>
        {isStreaming && (
          <style jsx>{`
            .streaming-text :global(p:last-child)::after {
              content: "▊";
              animation: blink 0.8s step-end infinite;
              color: var(--accent-primary);
              font-weight: normal;
            }
            @keyframes blink {
              0%, 100% { opacity: 1; }
              50% { opacity: 0; }
            }
          `}</style>
        )}

        {resp.domain === "schemes" && (
          <div className="mt-3">
            <Link href="/schemes">
              <button
                type="button"
                className="inline-flex items-center gap-1.5 rounded-[var(--radius-cta)] border border-[var(--accent-primary)]/40 bg-[var(--cream)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)] transition-colors hover:border-[var(--accent-primary)] hover:bg-[var(--cream-2)]"
              >
                {t("chat.exploreSchemes")}
                <IconChevronRight className="h-3.5 w-3.5 text-[var(--accent-primary)]" />
              </button>
            </Link>
          </div>
        )}

        {/* Actions Footer */}
        <div className="pt-2 flex flex-wrap items-center gap-1.5 text-xs text-[var(--text-faint)]">
          {/* Copy Button */}
          <button
            type="button"
            onClick={handleCopy}
            title={copied ? t("chat.copied") : t("chat.copyResponse")}
            className="flex h-7 w-7 items-center justify-center rounded-[var(--radius-md)] text-[var(--text-tertiary)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)]"
          >
            {copied ? <IconCheck className="h-3.5 w-3.5 text-[var(--state-success)]" /> : <IconCopy className="h-3.5 w-3.5" />}
          </button>

          {/* Read Aloud Button */}
          <button
            type="button"
            onClick={handleSpeak}
            title={speaking ? t("common.stopReadAloud") : t("common.readAloud")}
            className={`flex h-7 w-7 items-center justify-center rounded-[var(--radius-md)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)] ${
              speaking ? "text-[var(--accent-primary)] bg-[var(--accent-tint-soft)]" : "text-[var(--text-tertiary)]"
            }`}
          >
            <IconSpeaker className={`h-3.5 w-3.5 ${speaking ? "animate-pulse" : ""}`} />
          </button>

          {/* Thumbs Up Button */}
          <button
            type="button"
            onClick={() => setRating((r) => (r === "up" ? null : "up"))}
            title={t("chat.goodResponse")}
            className={`flex h-7 w-7 items-center justify-center rounded-[var(--radius-md)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)] ${
              rating === "up" ? "text-[var(--state-success)] bg-[var(--cream-2)]" : "text-[var(--text-tertiary)]"
            }`}
          >
            <IconThumbsUp className="h-3.5 w-3.5" />
          </button>

          {/* Thumbs Down Button */}
          <button
            type="button"
            onClick={() => setRating((r) => (r === "down" ? null : "down"))}
            title={t("chat.badResponse")}
            className={`flex h-7 w-7 items-center justify-center rounded-[var(--radius-md)] transition-colors hover:bg-[var(--cream-2)] hover:text-[var(--ink)] ${
              rating === "down" ? "text-[var(--state-error)] bg-[var(--cream-2)]" : "text-[var(--text-tertiary)]"
            }`}
          >
            <IconThumbsDown className="h-3.5 w-3.5" />
          </button>

          {/* Citations Trigger Button */}
          {resp.citations.length > 0 && (
            <button
              type="button"
              onClick={() => setOpenCitations((o) => !o)}
              aria-expanded={openCitations}
              className="ml-auto inline-flex items-center gap-1 rounded-[var(--radius-md)] bg-[var(--cream-2)] px-2 py-1 text-xs text-[var(--text-body)] transition-colors hover:bg-[var(--border-soft)] hover:text-[var(--ink)]"
            >
              <IconDoc className="h-3.5 w-3.5 text-[var(--accent-primary)]" />
              <span>{resp.citations.length} {t("common.source")}</span>
              <IconChevronRight className={`h-3 w-3 transition-transform ${openCitations ? "rotate-90" : ""}`} />
            </button>
          )}
        </div>

        {/* Citations Expandable Content */}
        {openCitations && resp.citations.length > 0 && (
          <div className="mt-2 rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--cream)] p-3">
            <p className="mb-1.5 text-xs font-semibold text-[var(--text-tertiary)]">{t("chat.sourcesReferences")}</p>
            <ul className="space-y-1">
              {resp.citations.map((c, j) => (
                <li key={j} className="flex items-start gap-2">
                  <span
                    className={`mt-0.5 inline-flex shrink-0 items-center rounded-full px-1.5 py-0.5 text-[9px] font-semibold ${
                      c.source === "web"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-green-100 text-green-700"
                    }`}
                  >
                    {c.source_label || (c.source === "web" ? "Web" : "Doc")}
                  </span>
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="link block truncate text-xs font-medium"
                  >
                    {c.title} {c.page ? `(p. ${c.page})` : ""}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

