"use client";
import { useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getGrievanceStatus, type GrievanceRecord } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
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
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50">{t("grievance.statusTitle")}</h1>
      <p className="mt-1 text-slate-500 dark:text-slate-400">{t("grievance.statusSubtitle")}</p>
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
        <div className="mt-6 rounded-xl border border-slate-200 p-5 dark:border-slate-800">
          <p className="font-mono text-sm text-emerald-700 dark:text-emerald-300">{record.id}</p>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{record.details}</p>
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
                  <div className={`mt-1 h-4 w-4 rounded-full ${reached ? "bg-emerald-600" : "bg-slate-200 dark:bg-slate-700"}`} />
                  <div>
                    <p className={`text-sm font-medium ${reached ? "text-slate-900 dark:text-slate-100" : "text-slate-400"}`}>
                      {t(`status.${s}`)}
                    </p>
                    {reached && record.timeline.find((tl) => tl.status === s) && (
                      <p className="text-xs text-slate-400">{record.timeline.find((tl) => tl.status === s)!.at}</p>
                    )}
                  </div>
                </li>
              );
            })}
          </ol>
        </div>
      )}

      <div className="mt-6 text-center">
        <Link href="/grievance">
          <Button variant="secondary">{t("grievance.title")}</Button>
        </Link>
      </div>
    </div>
  );
}
