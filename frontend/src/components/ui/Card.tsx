import type { ReactNode } from "react";

export function Card({
  children,
  className = "",
  interactive = false,
}: {
  children: ReactNode;
  className?: string;
  interactive?: boolean;
}) {
  return (
    <div
      className={`rounded-[var(--radius-xl)] bg-[var(--surface-overlay)] p-[var(--space-6)] ${interactive ? "transition hover:bg-[var(--surface-tint)] focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]" : ""} ${className}`}
    >
      {children}
    </div>
  );
}
