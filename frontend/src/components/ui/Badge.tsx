import type { ReactNode } from "react";

type Tone = "neutral" | "success" | "warning" | "error";

const TONES: Record<Tone, string> = {
  neutral: "bg-[var(--cream)] text-[var(--text-body)] border border-[var(--border-soft)]",
  success: "bg-[var(--state-success)]/12 text-[var(--state-success)] border border-transparent",
  warning: "bg-[var(--state-warning)]/14 text-[var(--state-warning)] border border-transparent",
  error: "bg-[var(--state-error)]/12 text-[var(--state-error)] border border-transparent",
};

export function Badge({
  tone = "neutral",
  deco,
  dot = true,
  children,
  className = "",
}: {
  tone?: Tone;
  deco?: string;
  dot?: boolean;
  children: ReactNode;
  className?: string;
}) {
  const style = deco
    ? { backgroundColor: `${deco}1f`, color: deco }
    : undefined;
  return (
    <span
      style={style}
      className={`inline-flex items-center gap-1.5 rounded-[var(--radius-sm)] px-2 py-1 text-xs font-medium leading-none ${style ? "" : TONES[tone]} ${className}`}
    >
      {dot ? <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-current" aria-hidden="true" /> : null}
      {children}
    </span>
  );
}
