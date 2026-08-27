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
import { IconShield } from "@/components/ui/Icons";

type Step = 0 | 1 | 2;

export default function GrievancePage() {
  const { t } = useI18n();
  const categories = getGrievanceCategories();
  const [step, setStep] = useState<Step>(0);
  const [categoryId, setCategoryId] = useState(categories[0].id);
  const [details, setDetails] = useState("");
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [record, setRecord] = useState<GrievanceRecord | null>(null);

  const steps = [t("grievance.step1"), t("grievance.step2"), t("grievance.step3")];

  function submit() {
    const rec = submitGrievance({ categoryId, details: details.trim(), name: name.trim() || undefined, contact: contact.trim() || undefined });
    setRecord(rec);
  }

  if (record) {
    const track = getGrievanceStatus(record.id);
    return (
      <div className="mx-auto max-w-xl px-4 py-10 text-center">
        <IconShield className="mx-auto w-10 h-10 text-[var(--state-success)]" />
        <h1 className="mt-3 font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("grievance.successTitle")}</h1>
        <p className="mt-2 text-[var(--text-secondary)]">{t("grievance.complaintIdLabel")}</p>
        <p className="mt-1 font-mono text-lg text-[var(--accent-primary)]">{record.id}</p>
        <div className="mt-4">
          {track ? <Badge tone="neutral">{t(`status.${track.status}`)}</Badge> : null}
        </div>
        <Link href="/grievance/status" className="mt-6 inline-block">
          <Button variant="secondary">{t("common.trackStatus")}</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-8">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("grievance.title")}</h1>
      <p className="mt-1 text-[var(--text-secondary)]">{t("grievance.subtitle")}</p>
      <div className="mt-6">
        <Stepper steps={steps} current={step} />
      </div>

      <div className="mt-6">
        {step === 0 && (
          <div>
            <h2 className="font-semibold text-[var(--text-primary)]">{t("grievance.categoryTitle")}</h2>
            <div className="mt-3 grid grid-cols-2 gap-3">
              {categories.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setCategoryId(c.id)}
                  className={`rounded-[var(--radius-xl)] border p-[var(--space-4)] text-left text-sm font-medium ${
                    categoryId === c.id
                      ? "border-[var(--accent-primary)] bg-[var(--surface-elevated)] text-[var(--accent-primary)]"
                      : "border-[var(--border-default)] bg-[var(--surface-base)] text-[var(--text-primary)] hover:border-[var(--border-hover)]"
                  }`}
                >
                  {t(c.labelKey)}
                </button>
              ))}
            </div>
            <div className="mt-6 flex justify-end">
              <Button onClick={() => setStep(1)}>{t("common.next")}</Button>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)]">
                {t("grievance.detailsLabel")}
              </label>
              <textarea
                value={details}
                onChange={(e) => setDetails(e.target.value)}
                rows={5}
                placeholder={t("grievance.placeholder")}
                className="mt-1 w-full rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-base)] px-[var(--space-3)] py-[var(--space-2)] text-sm text-[var(--text-primary)]"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)]">
                {t("grievance.nameLabel")} <span className="font-normal text-[var(--text-secondary)]">{t("grievance.optional")}</span>
              </label>
              <Input value={name} onChange={(e) => setName(e.target.value)} className="mt-1" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)]">
                {t("grievance.contactLabel")} <span className="font-normal text-[var(--text-secondary)]">{t("grievance.optional")}</span>
              </label>
              <Input value={contact} onChange={(e) => setContact(e.target.value)} className="mt-1" />
            </div>
            <div className="flex justify-between">
              <Button variant="secondary" onClick={() => setStep(0)}>{t("common.back")}</Button>
              <Button onClick={() => setStep(2)}>{t("common.next")}</Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h2 className="font-semibold text-[var(--text-primary)]">{t("grievance.reviewTitle")}</h2>
            <Card>
              <Badge tone="neutral">{t(categories.find((c) => c.id === categoryId)!.labelKey)}</Badge>
              <p className="mt-2 text-[var(--text-primary)]">{details}</p>
              {(name || contact) && (
                <p className="mt-2 text-xs text-[var(--text-secondary)]">
                  {name} {contact ? `· ${contact}` : ""}
                </p>
              )}
            </Card>
            <div className="flex justify-between">
              <Button variant="secondary" onClick={() => setStep(1)}>{t("common.back")}</Button>
              <Button onClick={submit}>{t("grievance.submitLabel")}</Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
