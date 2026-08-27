"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getService, slugAccent, services as rawServices } from "@/lib/data";
import { useTranslatedFields } from "@/lib/useTranslatedFields";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { IconChevronRight } from "@/components/ui/Icons";

export default function ServiceDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t, locale } = useI18n();
  const service = getService(locale, slug);
  const rawItem = service ? rawServices.find((s) => s.slug === slug) : undefined;
  const translated = useTranslatedFields({
    locale,
    items: service ? [service] : [],
    rawItems: (rawItem ? [rawItem] : []) as never,
    textFields: ["name", "summary", "description"],
    listFields: ["whoCanUse", "howToAccess"],
  });
  const sc = translated[0] ?? service;
  if (!sc) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState title={t("services.notFound")} action={<Link href="/services" className="text-sm text-[var(--accent-primary)] underline">{t("nav.services")}</Link>} />
      </div>
    );
  }
  const accent = slugAccent(sc.slug);
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl p-6 text-white" style={{ backgroundColor: accent }}>
        <Badge tone="neutral">{t(`serviceCategory.${sc.category}`)}</Badge>
        <h1 className="mt-2 font-[var(--font-display)] text-[var(--text-2xl)] font-[var(--font-medium)] tracking-tight">{sc.name}</h1>
        <p className="mt-1 text-sm opacity-90">{sc.summary}</p>
        <Link href={`/chat?q=${encodeURIComponent("How do I use the " + sc.name + " service?")}`}>
          <Button className="mt-4 bg-white/90 !text-slate-900 hover:bg-white">
            {t("services.askThisService")}
            <IconChevronRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
      <div className="mt-6 space-y-6">
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.overview")}</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">{sc.description}</p>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.whoCanUse")}</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
            {sc.whoCanUse.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.howToAccess")}</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
            {sc.howToAccess.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.source")}</h2>
          <a href={sc.source.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-sm text-[var(--accent-primary)] underline">
            {sc.source.label}
          </a>
        </section>
      </div>
    </div>
  );
}
