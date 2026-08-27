import type { ReactNode } from "react";

type Tone = "info" | "warn" | "error";

const TONES: Record<Tone, string> = {
  info: "bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border-[var(--accent-primary)]/30",
  warn: "bg-[var(--state-warning)]/10 text-[var(--state-warning)] border-[var(--state-warning)]/30",
  error: "bg-[var(--state-error)]/10 text-[var(--state-error)] border-[var(--state-error)]/30",
};

export function Alert({ tone = "info", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <div role="alert" className={`rounded-[var(--radius-md)] border px-[var(--space-4)] py-[var(--space-3)] text-[var(--text-sm)] ${TONES[tone]}`}>
      {children}
    </div>
  );
}
