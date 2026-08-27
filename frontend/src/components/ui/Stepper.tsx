import { IconCheck } from "./Icons";

export function Stepper({
  steps,
  current,
}: {
  steps: string[];
  current: number;
}) {
  return (
    <ol className="flex items-center gap-[var(--space-2)]">
      {steps.map((label, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <li key={label} className="flex flex-1 flex-col items-center gap-[var(--space-1)]">
            <span
              className={`flex h-7 w-7 items-center justify-center rounded-[var(--radius-full)] text-[var(--text-xs)] font-[var(--font-semibold)] ${
                active
                  ? "bg-[var(--accent-primary)] text-[var(--text-inverse)]"
                  : done
                    ? "bg-[var(--accent-primary)]/15 text-[var(--accent-primary)]"
                    : "bg-[var(--surface-overlay)] text-[var(--text-secondary)]"
              }`}
              aria-current={active ? "step" : undefined}
            >
              {done ? <IconCheck className="w-4 h-4" /> : i + 1}
            </span>
            <span className={`text-center text-[var(--text-xs)] ${active ? "text-[var(--accent-primary)] font-[var(--font-medium)]" : "text-[var(--text-secondary)]"}`}>
              {label}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
