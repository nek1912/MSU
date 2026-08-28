import type { ReactNode } from "react";
import { IconDoc } from "./Icons";

export function EmptyState({
  title,
  description,
  icon = <IconDoc className="h-6 w-6" />,
  action,
}: {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div role="status" className="flex flex-col items-center gap-2 rounded-[var(--radius-md)] border border-dashed border-[var(--border-default)] bg-[var(--cream)] px-4 py-12 text-center">
      <div className="mb-1 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--cream-2)] text-[var(--text-tertiary)]">
        {icon}
      </div>
      <p className="text-[var(--text-base)] font-medium text-[var(--ink)]">{title}</p>
      {description ? <p className="max-w-sm text-sm text-[var(--text-tertiary)]">{description}</p> : null}
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}
