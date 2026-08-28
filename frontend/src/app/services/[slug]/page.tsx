"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getService, services as rawServices } from "@/lib/data";
import { useTranslatedFields } from "@/lib/useTranslatedFields";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Reveal } from "@/components/motion/Reveal";
import { Stagger } from "@/components/motion/Stagger";
import { IconChevronRight } from "@/components/ui/Icons";
import { deco } from "@/lib/data/deco";

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
      <div className="mx-auto max-w-3xl px-4 py-[var(--space-8)] md:px-6">
        <EmptyState title={t("services.notFound")} action={<Link href="/services" className="text-sm text-[var(--accent-primary)] underline">{t("nav.services")}</Link>} />
      </div>
    );
  }
  return (
    <div className="mx-auto max-w-4xl px-4 py-[var(--space-8)] md:px-6">
      <Reveal trigger="load">
        <div className="rounded-[var(--radius-md)] border border-[var(--border-soft)] border-l-[3px] border-l-[var(--accent-primary)] bg-[var(--cream)] p-6 md:p-8">
          <Badge deco={deco(sc.category)}>{t(`serviceCategory.${sc.category}`)}</Badge>
          <h1 className="mt-3 display text-3xl tracking-tight text-[var(--ink)]">{sc.name}</h1>
          <p className="mt-1 text-[var(--text-body)]">{sc.summary}</p>
          <Link href={`/chat?q=${encodeURIComponent("How do I use the " + sc.name + " service?")}`}>
            <Button className="mt-4">
              {t("services.askThisService")}
              <IconChevronRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </Reveal>
      <Stagger className="mt-6 space-y-6">
        <section className="rounded-[var(--radius-xl)] border border-[var(--border-soft)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.overview")}</h2>
          <p className="mt-2 font-[var(--font-answer)] text-[var(--text-base)] leading-relaxed text-[var(--text-secondary)]">{sc.description}</p>
        </section>
        <section className="rounded-[var(--radius-xl)] border border-[var(--border-soft)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.whoCanUse")}</h2>
          <ul className="mt-2 font-[var(--font-answer)] list-disc space-y-1 pl-5 text-[var(--text-base)] leading-relaxed text-[var(--text-secondary)]">
            {sc.whoCanUse.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] border border-[var(--border-soft)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.howToAccess")}</h2>
          <ul className="mt-2 font-[var(--font-answer)] list-disc space-y-1 pl-5 text-[var(--text-base)] leading-relaxed text-[var(--text-secondary)]">
            {sc.howToAccess.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] border border-[var(--border-soft)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.source")}</h2>
          <a href={sc.source.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-sm text-[var(--accent-primary)] underline">
            {sc.source.label}
          </a>
        </section>
      </Stagger>
    </div>
  );
}
