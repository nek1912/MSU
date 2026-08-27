import { evidenceBand, type Band } from "@/lib/band";

const TONE: Record<Band, string> = {
  strong: "bg-[var(--state-success)]/15 text-[var(--state-success)]",
  moderate: "bg-[var(--state-warning)]/15 text-[var(--state-warning)]",
  weak: "bg-[var(--state-error)]/15 text-[var(--state-error)]",
};

export function EvidenceBand({ confidence, label }: { confidence: number; label: string }) {
  const band = evidenceBand(confidence);
  return (
    <span className={`rounded-[var(--radius-sm)] px-[var(--space-2)] py-[var(--space-1)] text-[var(--text-xs)] font-[var(--font-medium)] ${TONE[band]}`}>
      {label}
    </span>
  );
}
