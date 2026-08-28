"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { IconChat, IconMic, IconDoc, IconGlobe, IconChevronRight } from "@/components/ui/Icons";
import { Reveal } from "@/components/motion/Reveal";
import { Stagger } from "@/components/motion/Stagger";
import { schemes as rawSchemes, services as rawServices, libraryDocs as rawLibraryDocs } from "@/lib/data";
import { deco } from "@/lib/data/deco";

const FEATURES = [
  { icon: <IconGlobe className="w-5 h-5" />, href: "/chat", title: "landing.f1title", text: "landing.f1text" },
  { icon: <IconMic className="w-5 h-5" />, href: "/chat", title: "landing.f2title", text: "landing.f2text" },
  { icon: <IconDoc className="w-5 h-5" />, href: "/library", title: "landing.f3title", text: "landing.f3text" },
];
const HOW = [
  { title: "landing.how1title", text: "landing.how1text" },
  { title: "landing.how2title", text: "landing.how2text" },
  { title: "landing.how3title", text: "landing.how3text" },
];
const COVERAGE = [
  { cat: "credit", href: "/services", key: "serviceCategory.credit" },
  { cat: "crop-insurance", href: "/schemes", key: "category.crop-insurance" },
  { cat: "storage", href: "/services", key: "serviceCategory.storage" },
  { cat: "pacs", href: "/schemes", key: "category.pacs" },
  { cat: "financial", href: "/schemes", key: "category.financial" },
  { cat: "subsidy", href: "/services", key: "serviceCategory.subsidy" },
];
const STARTERS = ["chat.starter1", "chat.starter2", "chat.starter3", "chat.starter4"];

export default function HomePage() {
  const router = useRouter();
  const { t } = useI18n();
  const [ask, setAsk] = useState("");

  const [wordmark] = t("landing.tagline").split("—").map((s) => s.trim());

  const stats = [
    { n: rawSchemes.length, label: t("nav.schemes") },
    { n: rawServices.length, label: t("nav.services") },
    { n: rawLibraryDocs.length, label: t("nav.library") },
  ];

  function submitAsk() {
    const q = ask.trim();
    if (!q) return;
    router.push(`/chat?q=${encodeURIComponent(q)}`);
  }

  return (
    <div>
      {/* Hero — left headline, right product chat card */}
      <section className="flex flex-col gap-10 px-4 pt-10 pb-12 md:px-6 md:pt-16 lg:flex-row lg:items-center lg:gap-12 lg:pb-16">
        <Reveal trigger="load" className="flex max-w-2xl flex-col items-start">
          <p className="eyebrow">{t("landing.badge")}</p>
          <h1 className="display mt-6 text-5xl leading-[1.02] tracking-tight text-[var(--ink)] md:text-[60px]">
            {wordmark}
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-[var(--text-body)]">
            {t("landing.f1text")}
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link href="/chat">
              <Button size="lg">
                {t("landing.ctaChat")}
                <IconChevronRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link href="/schemes">
              <Button size="lg" variant="secondary">
                {t("landing.ctaSchemes")}
              </Button>
            </Link>
          </div>
          <p className="mt-5 text-sm text-[var(--text-faint)]">{t("landing.trustText")}</p>
        </Reveal>

        <Reveal trigger="load" delay={0.1} className="lg:flex-1">
          <div className="rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-6 shadow-[0_8px_32px_rgba(0,0,0,0.05)]">
            <div className="ask-input-wrap flex items-center gap-3 rounded-[var(--radius-cta)] border border-[var(--border-default)] bg-[var(--cream)] px-4 py-3">
              <IconChat className="h-5 w-5 shrink-0 text-[var(--accent-primary)]" />
              <input
                value={ask}
                onChange={(e) => setAsk(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submitAsk()}
                placeholder={t("chat.placeholder")}
                aria-label={t("chat.placeholder")}
                className="w-full flex-1 bg-transparent text-[var(--ink)] placeholder:text-[var(--text-faint)] focus:outline-none"
              />
              <Button onClick={submitAsk} disabled={!ask.trim()} className="shrink-0">
                {t("common.send")}
              </Button>
            </div>
            <div className="mt-5 grid gap-2 sm:grid-cols-2">
              {STARTERS.map((k) => (
                <button
                  key={k}
                  type="button"
                  onClick={() => router.push(`/chat?q=${encodeURIComponent(t(k))}`)}
                  className="rounded-[var(--radius-cta)] border border-[var(--border-soft)] bg-[var(--cream)] px-3 py-2.5 text-left text-sm text-[var(--ink)] transition-colors hover:border-[var(--border-hover)] hover:bg-[var(--cream-2)]"
                >
                  {t(k)}
                </button>
              ))}
            </div>
          </div>
        </Reveal>
      </section>

      {/* Stats — inverted band */}
      <Reveal className="bg-[var(--dark)] px-4 py-10 text-[var(--on-dark-strong)] md:px-6 md:py-12">
        <div className="grid grid-cols-3 gap-6">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <p className="display text-3xl sm:text-4xl md:text-5xl">{s.n}</p>
              <p className="mt-1 text-sm text-[var(--on-dark-muted)]">{s.label}</p>
            </div>
          ))}
        </div>
      </Reveal>

      {/* Coverage — cream band */}
      <section className="bg-[var(--cream)] px-4 py-12 md:px-6 md:py-14">
        <Reveal>
          <p className="eyebrow">{t("landing.trustTitle")}</p>
          <h2 className="display mt-3 text-3xl tracking-tight text-[var(--ink)] md:text-4xl">{t("landing.trustText")}</h2>
        </Reveal>
        <Stagger className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {COVERAGE.map((c) => (
            <Link
              key={c.cat}
              href={c.href}
              className="group flex items-center justify-between gap-3 rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-5 transition-all duration-[250ms] ease-[var(--ease-out-cubic)] hover:-translate-y-0.5 hover:border-[var(--border-hover)] hover:shadow-[0_8px_32px_rgba(0,0,0,0.05)]"
            >
              <Badge deco={deco(c.cat)}>{t(c.key)}</Badge>
              <IconChevronRight className="h-4 w-4 shrink-0 text-[var(--text-faint)] transition-transform duration-[250ms] group-hover:translate-x-0.5 group-hover:text-[var(--accent-primary)]" />
            </Link>
          ))}
        </Stagger>
      </section>

      {/* How it works */}
      <section className="px-4 py-12 md:px-6 md:py-14">
        <Reveal>
          <h2 className="display text-3xl tracking-tight text-[var(--ink)] md:text-4xl">{t("landing.howTitle")}</h2>
        </Reveal>
        <Stagger className="mt-10 grid gap-8 md:grid-cols-3 md:gap-12">
          {HOW.map((h, i) => (
            <div key={h.title} className="relative">
              <span className="display text-5xl text-[var(--border-hover)]/60" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
              <h3 className="mt-3 font-medium text-[var(--ink)]">{t(h.title)}</h3>
              <p className="mt-2 max-w-sm text-sm leading-relaxed text-[var(--text-body)]">{t(h.text)}</p>
            </div>
          ))}
        </Stagger>
      </section>

      {/* Features trio — cream band */}
      <section className="bg-[var(--cream)] px-4 py-12 md:px-6 md:py-14">
        <Stagger className="grid gap-3 sm:grid-cols-3">
          {FEATURES.map((f) => (
            <Link
              key={f.title}
              href={f.href}
              className="group rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-6 text-left transition-all duration-[250ms] ease-[var(--ease-out-cubic)] hover:-translate-y-0.5 hover:border-[var(--border-hover)] hover:shadow-[0_8px_32px_rgba(0,0,0,0.06)]"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--cream-2)] text-[var(--ink)]">
                {f.icon}
              </div>
              <h2 className="mt-4 flex items-center gap-1 font-semibold text-[var(--ink)]">
                {t(f.title)}
                <IconChevronRight className="h-4 w-4 text-[var(--text-faint)] transition-transform duration-[250ms] group-hover:translate-x-0.5 group-hover:text-[var(--accent-primary)]" />
              </h2>
              <p className="mt-1 text-sm text-[var(--text-body)]">{t(f.text)}</p>
            </Link>
          ))}
        </Stagger>
      </section>

      {/* Final CTA — inverted band */}
      <Reveal className="bg-[var(--dark)] px-4 py-16 text-center text-[var(--on-dark-strong)] md:px-6 md:py-20">
        <p className="text-xs font-medium uppercase tracking-[0.09em] text-[var(--on-dark-muted)]">{t("landing.badge")}</p>
        <h2 className="display mx-auto mt-4 max-w-2xl text-3xl leading-tight tracking-tight md:text-4xl">{t("landing.ctaChat")}</h2>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link href="/chat">
            <Button size="lg">{t("landing.ctaChat")}</Button>
          </Link>
          <Link href="/grievance">
            <Button size="lg" variant="dark">{t("nav.grievance")}</Button>
          </Link>
        </div>
      </Reveal>
    </div>
  );
}
