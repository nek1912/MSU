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
  const schemes = getSchemes();
  return (
    <div className="mx-auto max-w-6xl px-4">
      <section className="flex flex-col items-center py-16 text-center">
        <Badge tone="success">{t("landing.badge")}</Badge>
        <h1 className="mt-4 max-w-3xl text-4xl font-extrabold leading-tight text-slate-900 dark:text-slate-50 md:text-5xl">
          {t("landing.tagline")}
        </h1>
        <p className="mt-4 max-w-xl text-slate-600 dark:text-slate-300">
          {t("landing.f1text")}
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link href="/chat">
            <Button><IconChat className="w-5 h-5" />{t("landing.ctaChat")}</Button>
          </Link>
          <Link href="/schemes">
            <Button variant="secondary"><IconLeaf className="w-5 h-5" />{t("landing.ctaSchemes")}</Button>
          </Link>
        </div>
        <p className="mt-10 text-sm text-slate-500 dark:text-slate-400">{t("landing.trustText")}</p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {FEATURES.map((f) => (
          <Card key={f.title} interactive className="text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300">
              {f.icon}
            </div>
            <h2 className="mt-3 font-semibold text-slate-900 dark:text-slate-50">{t(f.title)}</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{t(f.text)}</p>
          </Card>
        ))}
      </section>

      <section className="py-16">
        <h2 className="text-center text-2xl font-bold text-slate-900 dark:text-slate-50">{t("landing.howTitle")}</h2>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {HOW.map((h) => (
            <div key={h.title} className="relative rounded-xl border border-slate-200 p-6 dark:border-slate-800">
              <IconCheck className="w-5 h-5 text-emerald-600" />
              <h3 className="mt-2 font-semibold text-slate-900 dark:text-slate-50">{t(h.title)}</h3>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{t(h.text)}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-2 gap-3 rounded-2xl bg-emerald-50 p-6 dark:bg-emerald-950 md:grid-cols-4">
        {schemes.slice(0, 4).map((s) => (
          <Link key={s.slug} href={`/schemes/${s.slug}`} className="text-center">
            <p className="font-semibold text-emerald-800 dark:text-emerald-200">{s.name}</p>
            <p className="mt-1 text-xs text-emerald-700/80 dark:text-emerald-300/70">{t(`category.${s.category}`)}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
