"use client";
import { useState, useMemo } from "react";
import type { ChatResponse } from "@/lib/api";
import { useI18n } from "@/lib/i18n/provider";
import { EvidenceBand } from "@/components/EvidenceBand";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { IconSpeaker, IconChevronRight, IconDoc } from "@/components/ui/Icons";
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
        <div className="flex items-center justify-between gap-2">
          <span>{t("abstained.title")}</span>
          {speech.supported && (
            <Button variant="icon" aria-label={t("common.readAloud")} onClick={handleSpeak}>
              <IconSpeaker className="w-5 h-5" />
            </Button>
          )}
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-2">
      <div className="rounded-[var(--radius-lg)] border border-[var(--border-default)] bg-[var(--surface-overlay)] px-4 py-2 text-[var(--text-primary)]">
        <div className="mb-1 flex items-center gap-2">
          <Badge tone="neutral">{domainLabel}</Badge>
          <EvidenceBand confidence={resp.confidence} label={t(`evidence.${evidenceTone(resp.confidence)}`)} />
          <span className="ml-auto text-xs text-[var(--text-tertiary)]">{(resp.confidence * 100).toFixed(0)}%</span>
        </div>
        <p className="text-sm leading-relaxed">{resp.answer}</p>
        {speech.supported && (
          <div className="mt-2 flex gap-2">
            <Button variant="ghost" className="!py-1 !px-2 text-xs" aria-label={speaking ? t("common.stopReadAloud") : t("common.readAloud")} onClick={handleSpeak}>
              <IconSpeaker className="w-4 h-4" />
              <span>{speaking ? t("common.stopReadAloud") : t("common.readAloud")}</span>
            </Button>
          </div>
        )}
      </div>
      {resp.citations.length > 0 && (
        <div className="text-sm">
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            className="inline-flex items-center gap-1 text-xs text-[var(--accent-primary)] underline"
          >
            <IconDoc className="w-4 h-4" />
            {resp.citations.length} {t("common.source")}
            <IconChevronRight className={`w-4 h-4 transition ${open ? "rotate-90" : ""}`} />
          </button>
          {open && (
            <ul className="mt-1 space-y-1 pl-1">
              {resp.citations.map((c, j) => (
                <li key={j}>
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block truncate text-xs text-[var(--accent-primary)] underline"
                  >
                    {c.title}
                    {c.page ? ` — p.${c.page}` : ""}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function evidenceTone(confidence: number): "strong" | "moderate" | "weak" {
  if (confidence >= 0.65) return "strong";
  if (confidence >= 0.45) return "moderate";
  return "weak";
}
