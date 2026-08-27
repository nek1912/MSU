"use client";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconChat, IconMic, IconDoc, IconGlobe, IconLeaf, IconCheck } from "@/components/ui/Icons";
import { getSchemes } from "@/lib/data";

const FEATURES = [
  { icon: <IconGlobe />, title: "landing.f1title", text: "landing.f1text" },
  { icon: <IconMic />, title: "landing.f2title", text: "landing.f2text" },
  { icon: <IconDoc />, title: "landing.f3title", text: "landing.f3text" },
];
const HOW = [
  { title: "landing.how1title", text: "landing.how1text" },
  { title: "landing.how2title", text: "landing.how2text" },
  { title: "landing.how3title", text: "landing.how3text" },
];

export default function HomePage() {
  const { t } = useI18n();
  const schemes = getSchemes("en");
  return (
    <div className="mx-auto max-w-6xl">
      <section className="flex flex-col items-center px-[var(--space-4)] py-24 text-center">
        <Badge tone="neutral">{t("landing.badge")}</Badge>
        <h1 className="mt-6 max-w-4xl font-[var(--font-display)] text-5xl font-[var(--font-medium)] leading-[1.3] tracking-tight text-[var(--text-primary)] md:text-6xl">
          {t("landing.tagline")}
        </h1>
        <p className="mt-6 max-w-xl text-xl font-[var(--font-medium)] leading-[1.4] tracking-tight text-[var(--text-secondary)]">
          {t("landing.f1text")}
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-3">
          <Link href="/chat">
            <Button><IconChat className="w-5 h-5" />{t("landing.ctaChat")}</Button>
          </Link>
          <Link href="/schemes">
            <Button variant="secondary"><IconLeaf className="w-5 h-5" />{t("landing.ctaSchemes")}</Button>
          </Link>
        </div>
        <p className="mt-12 text-[var(--text-sm)] text-[var(--text-secondary)]">{t("landing.trustText")}</p>
      </section>

      <section className="grid gap-4 px-[var(--space-4)] py-6 md:grid-cols-3">
        {FEATURES.map((f) => (
          <Card key={f.title} interactive className="text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-accent-tint)] text-[var(--accent-primary)]">
              {f.icon}
            </div>
            <h2 className="mt-4 font-[var(--font-semibold)] text-[var(--text-primary)]">{t(f.title)}</h2>
            <p className="mt-1 text-[var(--text-sm)] text-[var(--text-secondary)]">{t(f.text)}</p>
          </Card>
        ))}
      </section>

      <section className="px-[var(--space-4)] py-16">
        <h2 className="text-center font-[var(--font-display)] text-4xl font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("landing.howTitle")}</h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {HOW.map((h) => (
            <div key={h.title} className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--color-accent-tint)] text-[var(--accent-primary)]">
                <IconCheck className="w-5 h-5" />
              </div>
              <h3 className="mt-4 font-[var(--font-semibold)] text-[var(--text-primary)]">{t(h.title)}</h3>
              <p className="mt-1 text-[var(--text-sm)] text-[var(--text-secondary)]">{t(h.text)}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="px-[var(--space-4)] pb-24">
        <div className="mx-auto grid max-w-5xl grid-cols-2 gap-x-4 gap-y-6 rounded-[var(--radius-xl)] bg-[var(--surface-overlay)] px-[var(--space-6)] py-[var(--space-8)] md:grid-cols-4">
          {schemes.slice(0, 4).map((s) => (
            <Link key={s.slug} href={`/schemes/${s.slug}`} className="text-center">
              <p className="font-[var(--font-semibold)] text-[var(--text-primary)]">{s.name}</p>
              <p className="mt-1 text-[var(--text-sm)] text-[var(--text-secondary)]">{t(`category.${s.category}`)}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
