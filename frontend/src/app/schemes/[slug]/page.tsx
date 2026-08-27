"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getScheme, schemeColors } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { IconChevronRight } from "@/components/ui/Icons";

const SECTIONS = ["overview", "eligibility", "benefits", "howToApply", "documents"] as const;

export default function SchemeDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t, locale } = useI18n();
  const scheme = getScheme(locale, slug);
  if (!scheme) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState title={t("detail.notFound")} action={<Link href="/schemes" className="text-sm text-[var(--accent-primary)] underline">{t("nav.schemes")}</Link>} />
      </div>
    );
  }
  const accent = schemeColors(scheme.slug);
  const body: Record<(typeof SECTIONS)[number], string[] | string> = {
    overview: scheme.overview,
    eligibility: scheme.eligibility,
    benefits: scheme.benefits,
    howToApply: scheme.howToApply,
    documents: scheme.documents,
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl p-6 text-white" style={{ backgroundColor: accent }}>
        <Badge tone="neutral">{t(`category.${scheme.category}`)}</Badge>
        <h1 className="mt-2 font-[var(--font-display)] text-[var(--text-2xl)] font-[var(--font-medium)] tracking-tight">{scheme.name}</h1>
        <p className="mt-1 text-sm opacity-90">{scheme.benefit}</p>
        <Link href={`/chat?scheme=${scheme.slug}`}>
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
