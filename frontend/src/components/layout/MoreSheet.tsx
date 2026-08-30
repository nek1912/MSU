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
      <div className="fixed inset-0 z-30 bg-[#201515]/45" aria-hidden="true" onClick={onClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="More"
        className="fixed inset-x-0 bottom-0 z-40 rounded-t-[var(--radius-md)] border-t border-[var(--border-soft)] bg-[var(--canvas)] pb-[env(safe-area-inset-bottom)]"
      >
        <div className="mx-auto w-full px-4 py-5 lg:hidden">
          <div className="mb-3 h-[3px] w-10 rounded-full bg-[var(--border-default)]" aria-hidden="true" />
          <div className="grid grid-cols-3 gap-2">
            {MORE_LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                onClick={onClose}
                className="flex flex-col items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--cream)] py-4 text-sm text-[var(--ink)] transition-colors hover:bg-[var(--cream-2)]"
              >
                {l.icon}
                <span>{t(l.key)}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
