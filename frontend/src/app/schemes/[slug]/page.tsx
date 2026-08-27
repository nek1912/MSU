"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getScheme, schemeColors, schemes as rawSchemes } from "@/lib/data";
import { useTranslatedFields } from "@/lib/useTranslatedFields";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { IconChevronRight } from "@/components/ui/Icons";

const SECTIONS = ["overview", "eligibility", "benefits", "howToApply", "documents"] as const;

export default function SchemeDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t, locale } = useI18n();
  const scheme = getScheme(locale, slug);
  const rawItem = scheme ? rawSchemes.find((s) => s.slug === slug) : undefined;
  const translated = useTranslatedFields({
    locale,
    items: scheme ? [scheme] : [],
    rawItems: (rawItem ? [rawItem] : []) as never,
    textFields: ["name", "benefit", "overview"],
    listFields: ["eligibility", "benefits", "howToApply", "documents"],
  });
  const sc = translated[0] ?? scheme;
  if (!sc) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState title={t("detail.notFound")} action={<Link href="/schemes" className="text-sm text-[var(--accent-primary)] underline">{t("nav.schemes")}</Link>} />
      </div>
    );
  }
  const accent = schemeColors(sc.slug);
  const body: Record<(typeof SECTIONS)[number], string[] | string> = {
    overview: sc.overview,
    eligibility: sc.eligibility,
    benefits: sc.benefits,
    howToApply: sc.howToApply,
    documents: sc.documents,
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl p-6 text-white" style={{ backgroundColor: accent }}>
        <Badge tone="neutral">{t(`category.${sc.category}`)}</Badge>
        <h1 className="mt-2 font-[var(--font-display)] text-[var(--text-2xl)] font-[var(--font-medium)] tracking-tight">{sc.name}</h1>
        <p className="mt-1 text-sm opacity-90">{sc.benefit}</p>
        <Link href={`/chat?scheme=${sc.slug}`}>
          <Button className="mt-4 bg-white/90 !text-slate-900 hover:bg-white">
            {t("common.askThisScheme")}
            <IconChevronRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
      <div className="mt-6 space-y-6">
        {SECTIONS.map((s) => (
          <section key={s} className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
            <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t(`detail.${s}`)}</h2>
            {Array.isArray(body[s]) ? (
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
                {(body[s] as string[]).map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-sm text-[var(--text-secondary)]">{body[s] as string}</p>
            )}
          </section>
        ))}
      </div>
    </div>
  );
}
