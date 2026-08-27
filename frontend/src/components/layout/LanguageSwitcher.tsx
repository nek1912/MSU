"use client";
import { LOCALES, type Locale } from "@/lib/i18n/i18n";
import { useI18n } from "@/lib/i18n/provider";
import { IconGlobe } from "@/components/ui/Icons";

const NAMES: Record<Locale, string> = {
  en: "English", hi: "हिंदी", mr: "मराठी", bn: "বাংলা", ta: "தமிழ்",
};

export function LanguageSwitcher({ className = "" }: { className?: string }) {
  const { locale, setLocale, t } = useI18n();
  return (
    <label className={`flex items-center gap-[var(--space-1)] text-[var(--text-sm)] ${className}`}>
      <IconGlobe className="w-4 h-4" />
      <span className="sr-only">{t("common.globe")}</span>
      <select
        aria-label="Language"
        value={locale}
        onChange={(e) => setLocale(e.target.value as Locale)}
        className="rounded-[var(--radius-md)] border border-[var(--border-default)] bg-transparent px-[var(--space-1)] py-[var(--space-1)] text-[var(--text-secondary)]"
      >
        {LOCALES.map((l) => (
          <option key={l} value={l}>{NAMES[l]}</option>
        ))}
      </select>
    </label>
  );
}
