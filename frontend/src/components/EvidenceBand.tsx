import { evidenceBand, type Band } from "@/lib/band";

const TONE: Record<Band, string> = {
  strong: "bg-[var(--state-success)]/12 text-[var(--state-success)]",
  moderate: "bg-[var(--state-warning)]/14 text-[var(--state-warning)]",
  weak: "bg-[var(--state-error)]/12 text-[var(--state-error)]",
};

export function EvidenceBand({ confidence, label }: { confidence: number; label: string }) {
  const band = evidenceBand(confidence);
  return (
    <span className={`inline-flex items-center rounded-[var(--radius-sm)] px-2 py-1 text-xs font-medium leading-none ${TONE[band]}`}>
      {label}
    </span>
  );
}
