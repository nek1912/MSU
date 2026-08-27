"use client";
import { useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getGrievanceStatus, type GrievanceRecord } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";

const ORDER = ["submitted", "in-review", "resolved"] as const;

export default function GrievanceStatusPage() {
  const { t } = useI18n();
  const [id, setId] = useState("");
  const [record, setRecord] = useState<GrievanceRecord | null>(null);
  const [searched, setSearched] = useState(false);

  function search() {
    setRecord(getGrievanceStatus(id.trim()) ?? null);
    setSearched(true);
  }

  const currentIdx = record ? ORDER.indexOf(record.status as (typeof ORDER)[number]) : -1;

  return (
    <div className="mx-auto max-w-xl px-4 py-8">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("grievance.statusTitle")}</h1>
      <p className="mt-1 text-[var(--text-secondary)]">{t("grievance.statusSubtitle")}</p>
      <div className="mt-4 flex gap-2">
        <Input value={id} onChange={(e) => setId(e.target.value)} placeholder={t("common.enterComplaintId")} />
        <Button onClick={search}>{t("common.findStatus")}</Button>
      </div>

      {searched && !record && (
        <div className="mt-6">
          <EmptyState title={t("grievance.notFound")} />
        </div>
      )}

      {record && (
        <Card className="mt-6">
          <p className="font-mono text-sm text-[var(--accent-primary)]">{record.id}</p>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">{record.details}</p>
          <div className="mt-4 flex items-center gap-2">
            <Badge tone={currentIdx >= ORDER.length - 1 ? "success" : currentIdx >= 1 ? "warning" : "neutral"}>
              {t(`status.${record.status}`)}
            </Badge>
          </div>
          <ol className="mt-4 space-y-0">
            {ORDER.map((s, i) => {
              const reached = i <= currentIdx;
              return (
                <li key={s} className="flex items-start gap-3">
                  <div className={`mt-1 h-4 w-4 rounded-full ${reached ? "bg-[var(--state-success)]" : "bg-[var(--border-default)]"}`} />
                  <div>
                    <p className={`text-sm font-medium ${reached ? "text-[var(--text-primary)]" : "text-[var(--text-secondary)]"}`}>
                      {t(`status.${s}`)}
                    </p>
                    {reached && record.timeline.find((tl) => tl.status === s) && (
                      <p className="text-xs text-[var(--text-secondary)]">{record.timeline.find((tl) => tl.status === s)!.at}</p>
                    )}
                  </div>
                </li>
              );
            })}
          </ol>
        </Card>
      )}

      <div className="mt-6 text-center">
        <Link href="/grievance">
          <Button variant="secondary">{t("grievance.title")}</Button>
        </Link>
      </div>
    </div>
  );
}
