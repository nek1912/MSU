"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { LanguageSwitcher } from "./LanguageSwitcher";

const LINKS = [
  { href: "/", key: "nav.home" },
  { href: "/schemes", key: "nav.schemes" },
  { href: "/services", key: "nav.services" },
  { href: "/library", key: "nav.library" },
  { href: "/legal", key: "nav.legal" },
  { href: "/grievance", key: "nav.grievance" },
  { href: "/faq", key: "nav.faq" },
] as const;

export function TopNav() {
  const { t } = useI18n();
  const pathname = usePathname();
  const active = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--border-soft)] bg-[var(--canvas)]">
      <div className="mx-auto flex h-14 max-w-[1440px] items-center justify-between gap-4 px-4 md:px-6">
        <Link href="/" className="group flex shrink-0 flex-col leading-none">
          <span className="display text-xl text-[var(--ink)]">सहकारिता</span>
          <span className="mt-0.5 h-[2px] w-[22px] bg-[var(--accent-primary)] transition-all duration-[250ms] ease-[var(--ease-out-cubic)] group-hover:w-9" aria-hidden="true" />
        </Link>

        <nav className="hidden items-center gap-1 lg:flex" aria-label="Primary">
          {LINKS.map((l) => {
            const isActive = active(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                aria-current={isActive ? "page" : undefined}
                className={`flex h-14 items-center border-b-2 px-3 text-sm transition-colors duration-[200ms] ${
                  isActive
                    ? "border-[var(--ink)] font-medium text-[var(--ink)]"
                    : "border-transparent text-[var(--text-tertiary)] hover:text-[var(--ink)]"
                }`}
              >
                {t(l.key)}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <Link
            href="/chat"
            className="hidden items-center rounded-[var(--radius-pill)] border border-[var(--accent-primary)] bg-[var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[var(--accent-contrast)] transition-colors duration-[200ms] hover:bg-[var(--accent-hover)] hover:border-[var(--accent-hover)] md:inline-flex"
          >
            {t("nav.chat")}
          </Link>
        </div>
      </div>
    </header>
  );
}
