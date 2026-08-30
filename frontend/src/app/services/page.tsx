"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getServices, services as rawServices } from "@/lib/data";
import { useTranslatedFields } from "@/lib/useTranslatedFields";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Chips } from "@/components/ui/Chips";
import { EmptyState } from "@/components/ui/EmptyState";
import { Reveal } from "@/components/motion/Reveal";
import { Stagger } from "@/components/motion/Stagger";
import { deco } from "@/lib/data/deco";

const CATEGORY_ALL = "all";
const categories = ["all", "credit", "storage", "insurance", "agro-inputs", "subsidy", "membership"] as const;
type Filter = (typeof categories)[number];

export default function ServicesPage() {
  const { t, locale } = useI18n();
  const all = useMemo(() => getServices(locale), [locale]);
  const translated = useTranslatedFields({
    locale,
    items: all,
    rawItems: rawServices as never,
    textFields: ["name", "summary"],
    listFields: [],
  });
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);

  const filtered = translated.filter((s) => {
    const okCat = cat === CATEGORY_ALL || s.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery = !q || s.name.toLowerCase().includes(q) || s.summary.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  return (
    <div className="rail-frame page-container">
      <Reveal trigger="load">
        <h1 className="display text-3xl tracking-tight text-[var(--ink)] md:text-4xl">{t("services.title")}</h1>
        <p className="mt-1 text-[var(--text-body)]">{t("services.subtitle")}</p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("services.searchPlaceholder")} className="max-w-sm" />
          <p className="text-sm text-[var(--text-body)]">{t("services.count", { n: filtered.length })}</p>
        </div>
        <div className="mt-4">
          <Chips<Filter>
            options={categories}
            value={cat}
            onChange={setCat}
            render={(c) => (c === "all" ? t("common.all") : t(`serviceCategory.${c}`))}
          />
        </div>
      </Reveal>
      {filtered.length === 0 ? (
        <div className="mt-6"><EmptyState title={t("services.empty")} /></div>
      ) : (
        <Stagger className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((s) => (
            <Link key={s.slug} href={`/services/${s.slug}`} className="block">
              <Card interactive>
                <Badge deco={deco(s.category)}>{t(`serviceCategory.${s.category}`)}</Badge>
                <h2 className="mt-[var(--space-2)] font-[var(--font-semibold)] text-[var(--text-primary)]">{s.name}</h2>
                <p className="mt-[var(--space-1)] text-[var(--text-sm)] text-[var(--text-secondary)]">{s.summary}</p>
              </Card>
            </Link>
          ))}
        </Stagger>
      )}
    </div>
  );
}
