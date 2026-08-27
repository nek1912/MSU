import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "icon";
type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  children: ReactNode;
};

const STYLES: Record<Variant, string> = {
  primary:
    "bg-[var(--accent-primary)] text-white hover:bg-[var(--accent-hover)] active:bg-[var(--accent-active)] disabled:opacity-50 disabled:cursor-not-allowed",
  secondary:
    "border border-[var(--border-default)] bg-transparent text-[var(--text-tertiary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)] disabled:opacity-50 disabled:cursor-not-allowed",
  ghost:
    "text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-overlay)] disabled:opacity-50 disabled:cursor-not-allowed",
  icon: "flex items-center justify-center rounded-[var(--radius-md)] p-2 text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-overlay)] disabled:opacity-50 disabled:cursor-not-allowed",
};

export function Button({ variant = "primary", className = "", children, ...rest }: Props) {
  return (
    <button
      {...rest}
      className={`inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] px-4 py-2 text-[var(--text-sm)] font-[var(--font-medium)] transition focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] focus-visible:ring-offset-2 disabled:cursor-not-allowed ${STYLES[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
