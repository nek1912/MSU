import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "dark" | "ghost" | "icon";
type Size = "sm" | "md" | "lg";
type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  full?: boolean;
  children: ReactNode;
};

const STYLES: Record<Variant, string> = {
  primary:
    "bg-[var(--accent-primary)] text-[var(--accent-contrast)] border border-[var(--accent-primary)] hover:bg-[var(--accent-hover)] hover:border-[var(--accent-hover)] active:bg-[var(--accent-active)]",
  secondary:
    "bg-[var(--canvas)] text-[var(--ink)] border border-[var(--ink)] hover:bg-[var(--cream)] hover:border-[var(--text-body)] active:bg-[var(--cream-2)]",
  dark:
    "bg-[var(--dark)] text-[var(--on-dark-strong)] border border-[var(--dark)] hover:bg-[#3a2c2c] active:bg-[#2c2020]",
  ghost:
    "bg-transparent text-[var(--ink)] border border-transparent hover:bg-[var(--cream)] hover:text-[var(--dark)] active:bg-[var(--cream-2)]",
  icon: "bg-transparent text-[var(--ink)] border border-transparent hover:bg-[var(--cream)] hover:text-[var(--dark)] active:bg-[var(--cream-2)]",
};

const SIZE: Record<Size, string> = {
  sm: "h-9 px-3.5 text-[var(--text-sm)]",
  md: "h-11 px-5 text-[var(--text-base)]",
  lg: "h-12 px-6 text-[var(--text-lg)]",
};

const ICON_SIZE: Record<Size, string> = {
  sm: "h-9 w-9",
  md: "h-11 w-11",
  lg: "h-12 w-12",
};

function Spinner() {
  return (
    <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden="true" />
  );
}

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  full = false,
  className = "",
  children,
  disabled,
  ...rest
}: Props) {
  const square = variant === "icon";
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={`inline-flex items-center justify-center gap-2 font-semibold transition-all duration-[250ms] ease-[var(--ease-out-cubic)] active:scale-[0.99] disabled:opacity-45 disabled:cursor-not-allowed ${
        square ? `${ICON_SIZE[size]} rounded-[var(--radius-cta)] p-0` : `${SIZE[size]} rounded-[var(--radius-cta)]`
      } ${STYLES[variant]} ${full ? "w-full" : ""} ${className}`}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
}
