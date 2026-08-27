"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { IconHome, IconChat, IconGrid, IconDoc, IconShield } from "@/components/ui/Icons";

const LINKS = [
  { href: "/", key: "nav.home", icon: <IconHome className="w-5 h-5" /> },
  { href: "/chat", key: "nav.chat", icon: <IconChat className="w-5 h-5" /> },
  { href: "/schemes", key: "nav.schemes", icon: <IconGrid className="w-5 h-5" /> },
  { href: "/library", key: "nav.library", icon: <IconDoc className="w-5 h-5" /> },
  { href: "/grievance", key: "nav.grievance", icon: <IconShield className="w-5 h-5" /> },
] as const;

export function TopNav() {
  const { t } = useI18n();
  const pathname = usePathname();
  const active = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--border-default)] bg-[var(--surface-base)]/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-[var(--space-4)]">
        <Link href="/" className="flex items-center gap-2 font-[var(--font-semibold)] text-[var(--accent-primary)]">
          <IconShield className="w-6 h-6" />
          <span>सहकारिता</span>
        </Link>
        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              aria-current={active(l.href) ? "page" : undefined}
              className={`flex items-center gap-2 rounded-[var(--radius-md)] px-3 py-2 text-[var(--text-sm)] font-[var(--font-medium)] focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] ${
                active(l.href)
                  ? "text-[var(--accent-primary)]"
                  : "text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
              }`}
            >
              {l.icon}
              <span>{t(l.key)}</span>
            </Link>
          ))}
        </nav>
        <LanguageSwitcher />
      </div>
    </header>
  );
}
