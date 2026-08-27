"use client";
import Link from "next/link";
import { useEffect } from "react";
import { useI18n } from "@/lib/i18n/provider";
import { IconScale, IconBuilding, IconHelp } from "@/components/ui/Icons";

const MORE_LINKS = [
  { href: "/legal", key: "nav.legal", icon: <IconScale className="w-5 h-5" /> },
  { href: "/services", key: "nav.services", icon: <IconBuilding className="w-5 h-5" /> },
  { href: "/faq", key: "nav.faq", icon: <IconHelp className="w-5 h-5" /> },
] as const;

export function MoreSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useI18n();
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <>
      <div className="fixed inset-0 z-30 bg-black/50" aria-hidden="true" onClick={onClose} />
      <div
        role="dialog"
        aria-label="More"
        className="fixed inset-x-0 bottom-0 z-40 rounded-t-[var(--radius-xl)] border-t border-[var(--border-default)] bg-[var(--surface-base)] pb-[env(safe-area-inset-bottom)]"
      >
        <div className="grid grid-cols-3 gap-2 px-[var(--space-4)] py-[var(--space-4)] md:hidden">
          {MORE_LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              onClick={onClose}
              className="flex flex-col items-center gap-1 rounded-[var(--radius-lg)] py-[var(--space-3)] text-[var(--text-sm)] text-[var(--text-primary)] focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]"
            >
              {l.icon}
              <span>{t(l.key)}</span>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
