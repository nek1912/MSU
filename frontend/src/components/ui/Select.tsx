import type { SelectHTMLAttributes } from "react";

export function Select({ className = "", children, ...rest }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...rest}
      className={`rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-elevated)] px-3 py-2 text-[var(--text-base)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--border-focus)] focus:border-[var(--border-focus)] disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {children}
    </select>
  );
}
