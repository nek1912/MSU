"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getLegalDocs, legalDocs as rawLegalDocs } from "@/lib/data";
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
const categories = ["all", "act", "bye-laws", "provisions"] as const;
type Filter = (typeof categories)[number];

export default function LegalPage() {
  const { t, locale } = useI18n();
  const all = useMemo(() => getLegalDocs(locale), [locale]);
  const translated = useTranslatedFields({
    locale,
    items: all,
    rawItems: rawLegalDocs as never,
    textFields: ["badge", "overview"],
    listFields: [],
  });
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);

  const filtered = translated.filter((d) => {
    const okCat = cat === CATEGORY_ALL || d.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery = !q || d.badge.toLowerCase().includes(q) || d.overview.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  return (
    <div className="rail-frame page-container">
      <Reveal trigger="load">
        <h1 className="display text-3xl tracking-tight text-[var(--ink)] md:text-4xl">{t("legal.title")}</h1>
        <p className="mt-1 text-[var(--text-body)]">{t("legal.subtitle")}</p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("legal.searchPlaceholder")} className="max-w-sm" />
          <p className="text-sm text-[var(--text-body)]">{t("legal.count", { n: filtered.length })}</p>
        </div>
        <div className="mt-4">
          <Chips<Filter>
            options={categories}
            value={cat}
            onChange={setCat}
            render={(c) => (c === "all" ? t("common.all") : t(`legalCategory.${c}`))}
          />
        </div>
      </Reveal>
      {filtered.length === 0 ? (
        <div className="mt-6"><EmptyState title={t("legal.empty")} /></div>
      ) : (
        <Stagger className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((d) => (
            <Link key={d.slug} href={`/legal/${d.slug}`} className="block">
              <Card interactive>
                <Badge deco={deco(d.category)}>{t(`legalCategory.${d.category}`)}</Badge>
                <h2 className="mt-[var(--space-2)] font-[var(--font-semibold)] text-[var(--text-primary)]">{d.badge}</h2>
                <p className="mt-[var(--space-1)] text-[var(--text-sm)] text-[var(--text-secondary)]">{d.overview}</p>
              </Card>
            </Link>
          ))}
        </Stagger>
      )}
    </div>
  );
}
