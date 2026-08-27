"use client";
import { useMemo, useState } from "react";
import { useI18n } from "@/lib/i18n/provider";
import { getFaqItems } from "@/lib/data";
import { Input } from "@/components/ui/Input";
import { Chips } from "@/components/ui/Chips";
import { EmptyState } from "@/components/ui/EmptyState";
import Link from "next/link";
import { IconChevronRight } from "@/components/ui/Icons";

const CATEGORY_ALL = "all";
const categories = ["all", "crop-insurance", "pacs", "financial", "grievance", "legal"] as const;
type Filter = (typeof categories)[number];

export default function FaqPage() {
  const { t, locale } = useI18n();
  const items = useMemo(() => getFaqItems(locale), [locale]);
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);
  const [open, setOpen] = useState<Set<string>>(new Set());

  const filtered = items.filter((f) => {
    const okCat = cat === CATEGORY_ALL || f.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery = !q || f.question.toLowerCase().includes(q) || f.answer.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  function toggle(id: string) {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="mx-auto max-w-3xl px-[var(--space-4)] py-[var(--space-8)]">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("faq.title")}</h1>
      <p className="mt-[var(--space-1)] text-[var(--text-secondary)]">{t("faq.subtitle")}</p>
      <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("faq.searchPlaceholder")} className="mt-4 max-w-sm" />
      <div className="mt-4">
        <Chips<Filter>
          options={categories}
          value={cat}
          onChange={setCat}
          render={(c) => (c === "all" ? t("common.all") : t(`faqCategory.${c}`))}
        />
      </div>
      {filtered.length === 0 ? (
        <div className="mt-6"><EmptyState title={t("faq.empty")} /></div>
      ) : (
        <ul className="mt-6 space-y-3">
          {filtered.map((f) => {
            const isOpen = open.has(f.id);
            return (
              <li key={f.id} className="rounded-[var(--radius-xl)] border border-[var(--border-default)] bg-[var(--surface-overlay)]">
                <button
                  type="button"
                  aria-expanded={isOpen}
                  onClick={() => toggle(f.id)}
                  className="flex w-full items-center justify-between gap-2 px-[var(--space-4)] py-[var(--space-4)] text-left focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]"
                >
                  <span className="font-[var(--font-semibold)] text-[var(--text-primary)]">{f.question}</span>
                  <IconChevronRight className={`w-5 h-5 shrink-0 text-[var(--text-tertiary)] transition ${isOpen ? "rotate-90" : ""}`} />
                </button>
                {isOpen && (
                  <div className="px-[var(--space-4)] pb-[var(--space-4)]">
                    <p className="text-sm text-[var(--text-secondary)]">{f.answer}</p>
                    <Link href={`/chat?q=${encodeURIComponent(f.question)}`} className="mt-3 inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-[var(--text-base)] font-[var(--font-medium)] transition focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] bg-[var(--color-pill)] text-[var(--text-primary)] hover:bg-[var(--surface-overlay)]">
                      {t("faq.askInChat")}
                    </Link>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
