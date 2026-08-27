"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getService, slugAccent } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { IconChevronRight } from "@/components/ui/Icons";

export default function ServiceDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t } = useI18n();
  const service = getService("en", slug);
  if (!service) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState title={t("services.notFound")} action={<Link href="/services" className="text-sm text-[var(--accent-primary)] underline">{t("nav.services")}</Link>} />
      </div>
    );
  }
  const accent = slugAccent(service.slug);
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl p-6 text-white" style={{ backgroundColor: accent }}>
        <Badge tone="neutral">{t(`serviceCategory.${service.category}`)}</Badge>
        <h1 className="mt-2 font-[var(--font-display)] text-[var(--text-2xl)] font-[var(--font-medium)] tracking-tight">{service.name}</h1>
        <p className="mt-1 text-sm opacity-90">{service.summary}</p>
        <Link href={`/chat?q=${encodeURIComponent("How do I use the " + service.name + " service?")}`}>
          <Button className="mt-4 bg-white/90 !text-slate-900 hover:bg-white">
            {t("services.askThisService")}
            <IconChevronRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
      <div className="mt-6 space-y-6">
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.overview")}</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">{service.description}</p>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.whoCanUse")}</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
            {service.whoCanUse.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.howToAccess")}</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
            {service.howToAccess.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.source")}</h2>
          <a href={service.source.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-sm text-[var(--accent-primary)] underline">
            {service.source.label}
          </a>
        </section>
      </div>
    </div>
  );
}
