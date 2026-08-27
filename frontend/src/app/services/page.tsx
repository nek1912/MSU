"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getServices } from "@/lib/data";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Chips } from "@/components/ui/Chips";
import { EmptyState } from "@/components/ui/EmptyState";

const CATEGORY_ALL = "all";
const categories = ["all", "credit", "storage", "insurance", "agro-inputs", "subsidy", "membership"] as const;
type Filter = (typeof categories)[number];

export default function ServicesPage() {
  const { t, locale } = useI18n();
  const all = useMemo(() => getServices(locale), [locale]);
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);

  const filtered = all.filter((s) => {
    const okCat = cat === CATEGORY_ALL || s.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery = !q || s.name.toLowerCase().includes(q) || s.summary.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  return (
    <div className="mx-auto max-w-6xl px-[var(--space-4)] py-[var(--space-8)]">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("services.title")}</h1>
      <p className="mt-[var(--space-1)] text-[var(--text-secondary)]">{t("services.subtitle")}</p>
      <div className="mt-[var(--space-4)] flex flex-col gap-[var(--space-3)] sm:flex-row sm:items-center">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("services.searchPlaceholder")} className="max-w-sm" />
        <p className="text-[var(--text-sm)] text-[var(--text-secondary)]">{t("services.count", { n: filtered.length })}</p>
      </div>
      <div className="mt-[var(--space-4)]">
        <Chips<Filter>
          options={categories}
          value={cat}
          onChange={setCat}
          render={(c) => (c === "all" ? t("common.all") : t(`serviceCategory.${c}`))}
        />
      </div>
      {filtered.length === 0 ? (
        <div className="mt-[var(--space-6)]"><EmptyState title={t("services.empty")} /></div>
      ) : (
        <div className="mt-[var(--space-6)] grid gap-[var(--space-4)] sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((s) => (
            <Link key={s.slug} href={`/services/${s.slug}`} className="block">
              <Card interactive>
                <Badge tone="neutral">{t(`serviceCategory.${s.category}`)}</Badge>
                <h2 className="mt-[var(--space-2)] font-[var(--font-semibold)] text-[var(--text-primary)]">{s.name}</h2>
                <p className="mt-[var(--space-1)] text-[var(--text-sm)] text-[var(--text-secondary)]">{s.summary}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
