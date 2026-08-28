"use client";
import { useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getGrievanceCategories, submitGrievance, getGrievanceStatus, type GrievanceRecord } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Stepper } from "@/components/ui/Stepper";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/motion/Reveal";
import { IconShield, IconChevronRight } from "@/components/ui/Icons";

type Step = 0 | 1 | 2;

export default function GrievancePage() {
  const { t } = useI18n();
  const categories = getGrievanceCategories();
  const [step, setStep] = useState<Step>(0);
  const [categoryId, setCategoryId] = useState(categories[0].id);
  const [details, setDetails] = useState("");
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [detailsError, setDetailsError] = useState(false);
  const [record, setRecord] = useState<GrievanceRecord | null>(null);

  function goNext() {
    if (!details.trim()) {
      setDetailsError(true);
      return;
    }
    setDetailsError(false);
    setStep(2);
  }

  const steps = [t("grievance.step1"), t("grievance.step2"), t("grievance.step3")];

  function submit() {
    const rec = submitGrievance({
      categoryId,
      details: details.trim(),
      name: name.trim() || undefined,
      contact: contact.trim() || undefined,
    });
    setRecord(rec);
  }

  if (record) {
    const track = getGrievanceStatus(record.id);
    return (
      <div className="px-4 py-[var(--space-8)] md:px-6">
        <Reveal trigger="load">
          <h1 className="display text-3xl tracking-tight text-[var(--ink)] md:text-4xl">{t("grievance.title")}</h1>
          <p className="mt-1 text-[var(--text-body)]">{t("grievance.subtitle")}</p>
        </Reveal>
        <div className="mx-auto mt-8 max-w-xl">
          <div className="rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-8 text-center shadow-[0_8px_32px_rgba(0,0,0,0.04)]">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[var(--cream)] text-[var(--state-success)]">
              <IconShield className="h-8 w-8" />
            </div>
            <h2 className="display mt-4 text-2xl tracking-tight text-[var(--ink)] md:text-3xl">{t("grievance.successTitle")}</h2>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">{t("grievance.complaintIdLabel")}</p>
            <p className="mt-1 font-mono text-xl font-semibold text-[var(--accent-primary)]">{record.id}</p>
            <div className="mt-4">
              {track ? <Badge tone="neutral">{t(`status.${track.status}`)}</Badge> : null}
            </div>
            <div className="mt-6 flex items-center justify-center gap-3">
              <Link href="/grievance/status">
                <Button variant="secondary">
                  {t("common.trackStatus")}
                  <IconChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-[var(--space-8)] md:px-6">
      <Reveal trigger="load">
        <h1 className="display text-3xl tracking-tight text-[var(--ink)] md:text-4xl">{t("grievance.title")}</h1>
        <p className="mt-1 text-[var(--text-body)]">{t("grievance.subtitle")}</p>
      </Reveal>

      <div className="mx-auto mt-8 max-w-2xl">
        <div className="rounded-[var(--radius-md)] border border-[var(--border-soft)] bg-[var(--canvas)] p-6 shadow-[0_8px_32px_rgba(0,0,0,0.04)] md:p-8">
          <Stepper steps={steps} current={step} />

          <div className="mt-8">
            {step === 0 && (
              <div>
                <h2 className="font-semibold text-[var(--text-primary)]">{t("grievance.categoryTitle")}</h2>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {categories.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setCategoryId(c.id)}
                      aria-pressed={categoryId === c.id}
                      className={`group rounded-[var(--radius-md)] border p-4 text-left font-medium transition-all duration-[200ms] ease-[var(--ease-out-cubic)] ${
                        categoryId === c.id
                          ? "border-[var(--ink)] bg-[var(--cream-2)] text-[var(--ink)] shadow-sm"
                          : "border-[var(--border-soft)] bg-[var(--canvas)] text-[var(--text-body)] hover:border-[var(--border-hover)] hover:bg-[var(--cream)]"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold">{t(c.labelKey)}</span>
                        <div
                          className={`h-4 w-4 rounded-full border flex items-center justify-center ${
                            categoryId === c.id ? "border-[var(--ink)] bg-[var(--ink)]" : "border-[var(--border-default)]"
                          }`}
                        >
                          {categoryId === c.id && <div className="h-1.5 w-1.5 rounded-full bg-[var(--canvas)]" />}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
                <div className="mt-8 flex justify-end border-t border-[var(--border-soft)] pt-5">
                  <Button onClick={() => setStep(1)}>{t("common.next")}</Button>
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="space-y-5">
                <div>
                  <label htmlFor="details" className="block text-sm font-medium text-[var(--ink)]">
                    {t("grievance.detailsLabel")} <span className="text-[var(--state-error)]">*</span>
                  </label>
                  <textarea
                    id="details"
                    value={details}
                    onChange={(e) => {
                      setDetails(e.target.value);
                      if (detailsError && e.target.value.trim()) setDetailsError(false);
                    }}
                    rows={5}
                    placeholder={t("grievance.placeholder")}
                    aria-invalid={detailsError || undefined}
                    aria-describedby={detailsError ? "details-error" : undefined}
                    className="mt-1.5 w-full rounded-[var(--radius-cta)] border border-[var(--border-default)] bg-[var(--canvas)] px-3.5 py-2.5 font-answer text-[var(--text-base)] text-[var(--ink)] placeholder:text-[var(--text-faint)] transition-colors focus:border-[var(--accent-primary)] focus:outline-none"
                  />
                  {detailsError ? (
                    <p id="details-error" className="mt-1.5 text-xs font-medium text-[var(--state-error)]">
                      {t("grievance.detailsRequired")}
                    </p>
                  ) : null}
                </div>

                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-[var(--ink)]">
                    {t("grievance.nameLabel")}
                  </label>
                  <Input id="name" value={name} onChange={(e) => setName(e.target.value)} className="mt-1.5" />
                </div>

                <div>
                  <label htmlFor="contact" className="block text-sm font-medium text-[var(--ink)]">
                    {t("grievance.contactLabel")}
                  </label>
                  <Input id="contact" value={contact} onChange={(e) => setContact(e.target.value)} className="mt-1.5" />
                </div>

                <div className="flex items-center justify-between border-t border-[var(--border-soft)] pt-5">
                  <Button variant="secondary" onClick={() => setStep(0)}>
                    {t("common.back")}
                  </Button>
                  <Button onClick={goNext}>{t("common.next")}</Button>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-5">
                <h2 className="font-semibold text-[var(--text-primary)]">{t("grievance.reviewTitle")}</h2>
                <Card className="space-y-3 p-5">
                  <Badge tone="neutral">{t(categories.find((c) => c.id === categoryId)!.labelKey)}</Badge>
                  <p className="font-answer text-sm leading-relaxed text-[var(--ink)]">{details}</p>
                  {(name || contact) && (
                    <div className="border-t border-[var(--border-soft)] pt-2 text-xs text-[var(--text-secondary)]">
                      {name && <span>{name}</span>}
                      {name && contact && <span> · </span>}
                      {contact && <span>{contact}</span>}
                    </div>
                  )}
                </Card>
                <div className="flex items-center justify-between border-t border-[var(--border-soft)] pt-5">
                  <Button variant="secondary" onClick={() => setStep(1)}>
                    {t("common.back")}
                  </Button>
                  <Button onClick={submit}>{t("grievance.submitLabel")}</Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
