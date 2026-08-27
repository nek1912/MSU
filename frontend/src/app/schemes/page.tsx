"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getSchemes, schemes as rawSchemes } from "@/lib/data";
import { useTranslatedFields } from "@/lib/useTranslatedFields";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Chips } from "@/components/ui/Chips";
import { EmptyState } from "@/components/ui/EmptyState";

const CATEGORY_ALL = "all";
const categories = ["all", "crop-insurance", "pacs", "financial", "subsidy"] as const;
type Filter = (typeof categories)[number];

export default function SchemesPage() {
  const { t, locale } = useI18n();
  const all = useMemo(() => getSchemes(locale), [locale]);
  const translated = useTranslatedFields({
    locale,
    items: all,
    rawItems: rawSchemes as never,
    textFields: ["name", "benefit"],
    listFields: [],
  });
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);

  const filtered = translated.filter((s) => {
    const okCat = cat === CATEGORY_ALL || s.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery =
      !q ||
      s.name.toLowerCase().includes(q) ||
      s.benefit.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  return (
    <div className="mx-auto max-w-6xl px-[var(--space-4)] py-[var(--space-8)]">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("schemes.title")}</h1>
      <p className="mt-[var(--space-1)] text-[var(--text-secondary)]">{t("schemes.subtitle")}</p>
      <div className="mt-[var(--space-4)] flex flex-col gap-[var(--space-3)] sm:flex-row sm:items-center">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("schemes.searchPlaceholder")} className="max-w-sm" />
        <p className="text-[var(--text-sm)] text-[var(--text-secondary)]">{t("schemes.count", { n: filtered.length })}</p>
      </div>
      <div className="mt-[var(--space-4)]">
        <Chips<Filter>
          options={categories}
          value={cat}
          onChange={setCat}
          render={(c) => (c === "all" ? t("common.all") : t(`category.${c}`))}
        />
      </div>
      {filtered.length === 0 ? (
        <div className="mt-[var(--space-6)]">
          <EmptyState title={t("schemes.empty")} />
        </div>
      ) : (
        <div className="mt-[var(--space-6)] grid gap-[var(--space-4)] sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((s) => (
            <Link key={s.slug} href={`/schemes/${s.slug}`} className="block">
              <Card interactive>
                <Badge tone="neutral">{t(`category.${s.category}`)}</Badge>
                <h2 className="mt-[var(--space-2)] font-[var(--font-semibold)] text-[var(--text-primary)]">{s.name}</h2>
                <p className="mt-[var(--space-1)] text-[var(--text-sm)] text-[var(--text-secondary)]">{s.benefit}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
