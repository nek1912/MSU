import type { ReactNode } from "react";
import { IconDoc } from "./Icons";

export function EmptyState({ title, action }: { title: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-[var(--space-3)] rounded-[var(--radius-xl)] border border-dashed border-[var(--border-default)] py-[var(--space-10)] text-center">
      <IconDoc className="w-8 h-8 text-[var(--text-tertiary)]" />
      <p className="text-[var(--text-sm)] text-[var(--text-secondary)]">{title}</p>
      {action}
    </div>
  );
}
