import type { ReactNode } from "react";

export function Chips<T extends string>({
  options,
  value,
  onChange,
  render = (x) => x,
}: {
  options: readonly T[];
  value: T;
  onChange: (v: T) => void;
  render?: (v: T) => ReactNode;
}) {
  return (
    <div className="flex flex-wrap gap-2" role="listbox" aria-label="Filters">
      {options.map((o) => (
        <button
          key={o}
          type="button"
          role="option"
          aria-selected={o === value}
          onClick={() => onChange(o)}
          className={`rounded-[var(--radius-full)] px-[var(--space-3)] py-[var(--space-1)] text-[var(--text-sm)] font-[var(--font-medium)] transition ${
            o === value
              ? "bg-[var(--accent-primary)] text-[var(--text-inverse)]"
              : "bg-[var(--surface-overlay)] text-[var(--text-secondary)] hover:bg-[var(--border-hover)]"
          }`}
        >
          {render(o)}
        </button>
      ))}
    </div>
  );
}
