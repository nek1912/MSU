"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { IconHome, IconChat, IconGrid, IconDoc, IconShield } from "@/components/ui/Icons";

const LINKS = [
  { href: "/", key: "nav.home", icon: <IconHome className="w-6 h-6" /> },
  { href: "/chat", key: "nav.chat", icon: <IconChat className="w-6 h-6" /> },
  { href: "/schemes", key: "nav.schemes", icon: <IconGrid className="w-6 h-6" /> },
  { href: "/library", key: "nav.library", icon: <IconDoc className="w-6 h-6" /> },
  { href: "/grievance", key: "nav.grievance", icon: <IconShield className="w-6 h-6" /> },
] as const;

export function MobileNav() {
  const { t } = useI18n();
  const pathname = usePathname();
  const active = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);
  return (
    <nav
      aria-label="Primary mobile"
      className="fixed inset-x-0 bottom-0 z-20 border-t border-[var(--border-default)] bg-[var(--surface-base)] pb-[env(safe-area-inset-bottom)] md:hidden"
    >
      <div className="grid grid-cols-5">
        {LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            aria-current={active(l.href) ? "page" : undefined}
            className={`flex flex-col items-center gap-1 py-2 text-[11px] focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] ${
              active(l.href)
                ? "text-[var(--accent-primary)]"
                : "text-[var(--text-tertiary)]"
            }`}
          >
            {l.icon}
            <span className="truncate">{t(l.key)}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
}
