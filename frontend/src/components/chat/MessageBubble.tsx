"use client";
import { useState, useMemo } from "react";
import Link from "next/link";
import type { ChatResponse } from "@/lib/api";
import { useI18n } from "@/lib/i18n/provider";
import { EvidenceBand } from "@/components/EvidenceBand";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { IconSpeaker, IconChevronRight, IconDoc, IconBot } from "@/components/ui/Icons";
import { deco } from "@/lib/data/deco";
import { createSpeechService } from "@/lib/speech";

export function MessageBubble({ resp }: { resp: ChatResponse }) {
  const { t } = useI18n();
  const speech = useMemo(() => createSpeechService(), []);
  const [speaking, setSpeaking] = useState(false);
  const [open, setOpen] = useState(false);
  const domainKey = `domain.${resp.domain}`;
  const domainLabel = t(domainKey).startsWith("domain.") ? resp.domain : t(domainKey);

  function handleSpeak() {
    if (speaking) {
      speech.stopSpeaking();
      setSpeaking(false);
    } else {
      speech.speak(resp.answer, resp.language);
      setSpeaking(true);
    }
  }

  if (resp.abstained) {
    return (
      <Alert tone="warn">
        <div className="flex items-center justify-between gap-2 text-xs sm:text-sm">
          <span>{t("abstained.title")}</span>
          {speech.supported && (
            <Button variant="icon" aria-label={t("common.readAloud")} onClick={handleSpeak}>
              <IconSpeaker className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
          )}
        </div>
      </Alert>
    );
  }

  return (
    <div className="flex items-start gap-2.5 sm:gap-3">
      <div className="flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-[var(--radius-md)] bg-[var(--dark)] text-[var(--on-dark-strong)] shadow-sm">
        <IconBot className="h-4 w-4 sm:h-5 sm:w-5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-3.5 sm:p-5 shadow-[0_4px_20px_rgba(0,0,0,0.03)] transition-all hover:border-[var(--border-hover)]">
          <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <Badge deco={deco(resp.domain)}>{domainLabel}</Badge>
              <EvidenceBand confidence={resp.confidence} label={t(`evidence.${evidenceTone(resp.confidence)}`)} />
            </div>
            <span className="text-[11px] sm:text-xs text-[var(--text-faint)]">{(resp.confidence * 100).toFixed(0)}% match</span>
          </div>

          <p className="font-answer text-sm sm:text-base leading-relaxed text-[var(--ink)]">{resp.answer}</p>

          {/* Action CTA inside message if relevant */}
          {resp.domain === "schemes" && (
            <div className="mt-3.5 sm:mt-4">
              <Link href="/schemes">
                <button
                  type="button"
                  className="inline-flex items-center gap-1.5 sm:gap-2 rounded-[var(--radius-cta)] border border-[var(--accent-primary)]/40 bg-[var(--cream)] px-3 sm:px-3.5 py-1.5 sm:py-2 text-xs font-semibold text-[var(--ink)] transition-colors hover:border-[var(--accent-primary)] hover:bg-[var(--cream-2)]"
                >
                  Explore Schemes
                  <IconChevronRight className="h-3.5 w-3.5 text-[var(--accent-primary)]" />
                </button>
              </Link>
            </div>
          )}

          {resp.domain === "services" && (
            <div className="mt-3.5 sm:mt-4">
              <Link href="/services">
                <button
                  type="button"
                  className="inline-flex items-center gap-1.5 sm:gap-2 rounded-[var(--radius-cta)] border border-[var(--accent-primary)]/40 bg-[var(--cream)] px-3 sm:px-3.5 py-1.5 sm:py-2 text-xs font-semibold text-[var(--ink)] transition-colors hover:border-[var(--accent-primary)] hover:bg-[var(--cream-2)]"
                >
                  View Services
                  <IconChevronRight className="h-3.5 w-3.5 text-[var(--accent-primary)]" />
                </button>
              </Link>
            </div>
          )}

          <div className="mt-3.5 sm:mt-4 flex flex-wrap items-center justify-between border-t border-[var(--border-soft)] pt-2.5 sm:pt-3 text-xs text-[var(--text-tertiary)]">
            <div className="flex flex-wrap items-center gap-3 sm:gap-4">
              {speech.supported && (
                <button
                  type="button"
                  onClick={handleSpeak}
                  className="inline-flex items-center gap-1.5 font-medium transition-colors hover:text-[var(--ink)]"
                >
                  <IconSpeaker className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  <span>{speaking ? t("common.stopReadAloud") : t("common.readAloud")}</span>
                </button>
              )}
              {resp.citations.length > 0 && (
                <button
                  type="button"
                  onClick={() => setOpen((o) => !o)}
                  aria-expanded={open}
                  className="inline-flex items-center gap-1.5 font-medium transition-colors hover:text-[var(--ink)]"
                >
                  <IconDoc className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  <span>{resp.citations.length} {t("common.source")}</span>
                  <IconChevronRight className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-90" : ""}`} />
                </button>
              )}
            </div>
            <span className="text-[10px] sm:text-[11px] text-[var(--text-faint)]">Just now</span>
          </div>

          {open && resp.citations.length > 0 && (
            <ul className="mt-3 space-y-1.5 border-t border-[var(--border-soft)] pt-3">
              {resp.citations.map((c, j) => (
                <li key={j}>
                  <a href={c.url} target="_blank" rel="noopener noreferrer" className="link block truncate text-xs">
                    {c.title}
                    {c.page ? ` — p.${c.page}` : ""}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function evidenceTone(confidence: number): "strong" | "moderate" | "weak" {
  if (confidence >= 0.65) return "strong";
  if (confidence >= 0.45) return "moderate";
  return "weak";
}
