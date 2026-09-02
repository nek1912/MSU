"use client";
import { useState, useRef, useEffect } from "react";
import { LOCALES, type Locale } from "@/lib/i18n/i18n";
import { useI18n } from "@/lib/i18n/provider";
import { IconGlobe, IconCheck } from "@/components/ui/Icons";

const NAMES: Record<Locale, string> = {
  en: "English",
  hi: "हिंदी",
  gu: "ગુજરાતી",
  mr: "मराठी",
  bn: "বাংলা",
  ta: "தமிழ்",
};

export function LanguageSwitcher({ className = "" }: { className?: string }) {
  const { locale, setLocale, t } = useI18n();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close dropdown on Escape key
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div ref={containerRef} className={`relative inline-block ${className}`}>
      {/* shadcn UI Dropdown Trigger Button */}
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={t("common.globe")}
        onClick={() => setOpen((o) => !o)}
        className="inline-flex h-9 items-center justify-between gap-2 rounded-[var(--radius-cta)] border border-[var(--border-default)] bg-[var(--canvas)] px-3 text-sm font-medium text-[var(--ink)] shadow-2xs transition-all duration-200 hover:border-[var(--border-hover)] hover:bg-[var(--cream)] focus:border-[var(--accent-primary)] focus:outline-none"
      >
        <span className="flex items-center gap-1.5">
          <IconGlobe className="h-4 w-4 text-[var(--text-tertiary)]" />
          <span>{NAMES[locale]}</span>
        </span>
        <span className={`text-[10px] text-[var(--text-tertiary)] transition-transform duration-200 ${open ? "rotate-180" : ""}`}>
          ▼
        </span>
      </button>

      {/* shadcn UI Dropdown Menu Content Panel */}
      {open && (
        <div
          role="listbox"
          aria-label="Language selection"
          className="absolute right-0 top-full z-50 mt-1.5 max-h-72 w-44 overflow-y-auto rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-1.5 shadow-lg shadow-[rgba(0,0,0,0.08)] backdrop-blur-sm transition-all"
        >
          <div className="mb-1 border-b border-[var(--border-soft)] px-2 py-1 text-[11px] font-semibold uppercase tracking-wider text-[var(--text-faint)]">
            Select Language
          </div>
          <div className="space-y-0.5">
            {LOCALES.map((l) => {
              const isSelected = l === locale;
              return (
                <button
                  key={l}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => {
                    setLocale(l);
                    setOpen(false);
                  }}
                  className={`flex w-full items-center justify-between rounded-[var(--radius-sm)] px-2.5 py-1.5 text-left text-xs font-medium transition-colors ${
                    isSelected
                      ? "bg-[var(--cream-2)] font-semibold text-[var(--ink)]"
                      : "text-[var(--text-body)] hover:bg-[var(--cream)] hover:text-[var(--ink)]"
                  }`}
                >
                  <span>{NAMES[l]}</span>
                  {isSelected && <IconCheck className="h-3.5 w-3.5 text-[var(--accent-primary)]" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
