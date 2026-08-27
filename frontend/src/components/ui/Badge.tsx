import type { ReactNode } from "react";

type Tone = "neutral" | "success" | "warning" | "error";

const TONES: Record<Tone, string> = {
  neutral: "bg-[var(--surface-overlay)] text-[var(--text-tertiary)]",
  success: "bg-[var(--state-success)]/10 text-[var(--state-success)]",
  warning: "bg-[var(--state-warning)]/10 text-[var(--state-warning)]",
  error: "bg-[var(--state-error)]/10 text-[var(--state-error)]",
};

export function Badge({
  tone = "neutral",
  children,
  className = "",
}: {
  tone?: Tone;
  children: ReactNode;
  className?: string;
}) {
  return (
    <span className={`inline-flex items-center rounded-[var(--radius-full)] px-2 py-1 text-[var(--text-xs)] font-[var(--font-medium)] ${TONES[tone]} ${className}`}>
      {children}
    </span>
  );
}
