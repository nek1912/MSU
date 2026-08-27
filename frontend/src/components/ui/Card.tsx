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
      className={`rounded-[var(--radius-xl)] border border-[var(--border-default)] bg-[var(--surface-elevated)] p-[var(--space-4)] shadow-sm ${interactive ? "transition hover:border-[var(--border-hover)] hover:shadow-md focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]" : ""} ${className}`}
    >
      {children}
    </div>
  );
}
