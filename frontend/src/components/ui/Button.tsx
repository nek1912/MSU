import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "icon";
type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  children: ReactNode;
};

const STYLES: Record<Variant, string> = {
  primary:
    "bg-[var(--text-primary)] text-white hover:bg-[var(--text-secondary)] active:bg-[#0d0d0d] disabled:opacity-50 disabled:cursor-not-allowed",
  secondary:
    "bg-[var(--color-pill)] text-[var(--text-primary)] hover:bg-[var(--surface-overlay)] active:bg-[#e0e0e0] disabled:opacity-50 disabled:cursor-not-allowed",
  ghost:
    "text-[var(--text-primary)] hover:bg-[var(--color-pill)] active:bg-[var(--surface-overlay)] disabled:opacity-50 disabled:cursor-not-allowed",
  icon: "flex items-center justify-center rounded-full p-2 text-[var(--text-primary)] hover:bg-[var(--color-pill)] disabled:opacity-50 disabled:cursor-not-allowed",
};

export function Button({ variant = "primary", className = "", children, ...rest }: Props) {
  return (
    <button
      {...rest}
      className={`inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-[var(--text-base)] font-[var(--font-medium)] transition focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] focus-visible:ring-offset-2 disabled:cursor-not-allowed ${STYLES[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
