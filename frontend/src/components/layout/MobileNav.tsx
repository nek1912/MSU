"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { MoreSheet } from "./MoreSheet";
import { IconHome, IconChat, IconGrid, IconDoc, IconShield, IconMore } from "@/components/ui/Icons";

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
  const [moreOpen, setMoreOpen] = useState(false);
  const active = (href: string) => (href === "/" ? pathname === "/" : pathname.startsWith(href));
  return (
    <>
      <nav
        aria-label="Primary mobile"
        className="fixed inset-x-0 bottom-0 z-20 border-t border-[var(--border-soft)] bg-[var(--canvas)] pb-[env(safe-area-inset-bottom)] lg:hidden"
      >
        <div className="grid grid-cols-6">
          {LINKS.map((l) => {
            const isActive = active(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                aria-current={isActive ? "page" : undefined}
                className={`flex flex-col items-center gap-1 py-2 text-[11px] transition-colors duration-[200ms] ${isActive ? "text-[var(--ink)]" : "text-[var(--text-tertiary)]"}`}
              >
                <span className={`rounded-[var(--radius-cta)] px-2 py-0.5 ${isActive ? "bg-[var(--cream-2)]" : ""}`}>{l.icon}</span>
                <span className="truncate">{t(l.key)}</span>
              </Link>
            );
          })}
          <button
            type="button"
            aria-label={t("nav.more")}
            aria-expanded={moreOpen}
            onClick={() => setMoreOpen(true)}
            className="flex flex-col items-center gap-1 py-2 text-[11px] text-[var(--text-tertiary)]"
          >
            <IconMore className="w-6 h-6" />
            <span className="truncate">{t("nav.more")}</span>
          </button>
        </div>
      </nav>
      <MoreSheet open={moreOpen} onClose={() => setMoreOpen(false)} />
    </>
  );
}
