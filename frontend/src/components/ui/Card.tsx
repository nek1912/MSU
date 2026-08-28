import type { ReactNode } from "react";

export function Card({
  children,
  className = "",
  interactive = false,
  fill = "canvas",
}: {
  children: ReactNode;
  className?: string;
  interactive?: boolean;
  fill?: "canvas" | "cream";
}) {
  const base = fill === "cream" ? "bg-[var(--cream-2)] border border-[var(--cream-2)]" : "bg-[var(--canvas)] border border-[var(--border-soft)]";
  return (
    <div
      className={`rounded-[var(--radius-md)] p-6 ${base} ${
        interactive
          ? "transition-all duration-[250ms] ease-[var(--ease-out-cubic)] hover:border-[var(--border-hover)] hover:bg-[var(--cream)] hover:-translate-y-0.5"
          : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
