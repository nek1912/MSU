"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getLegalDoc, slugAccent } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { IconChevronRight } from "@/components/ui/Icons";

const SECTIONS = ["keyProvisions", "applicability", "byLaws"] as const;

export default function LegalDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t } = useI18n();
  const doc = getLegalDoc(slug);
  if (!doc) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState title={t("legal.notFound")} action={<Link href="/legal" className="text-sm text-[var(--accent-primary)] underline">{t("nav.legal")}</Link>} />
      </div>
    );
  }
  const accent = slugAccent(slug);
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl p-6 text-white" style={{ backgroundColor: accent }}>
        <Badge tone="neutral">{t(`legalCategory.${doc.category}`)}</Badge>
        <h1 className="mt-2 font-[var(--font-display)] text-[var(--text-2xl)] font-[var(--font-medium)] tracking-tight">{doc.title}</h1>
        <p className="mt-1 text-sm opacity-90">{doc.overview}</p>
        <Link href={`/chat?q=${encodeURIComponent("Tell me about " + doc.title)}`}>
          <Button className="mt-4 bg-white/90 !text-slate-900 hover:bg-white">
            {t("legal.askThisLaw")}
            <IconChevronRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
      <div className="mt-6 space-y-6">
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("legal.overview")}</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">{doc.overview}</p>
        </section>
        {SECTIONS.map((s) => (
          <section key={s} className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
            <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t(`legal.${s}`)}</h2>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
              {doc[s].map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>
        ))}
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("legal.source")}</h2>
          <a href={doc.source.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-sm text-[var(--accent-primary)] underline">
            {doc.source.label}
          </a>
        </section>
      </div>
    </div>
  );
}
