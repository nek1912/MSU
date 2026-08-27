export type GrievanceStatus = "submitted" | "in-review" | "resolved";

export interface GrievanceCategory {
  id: string;
  labelKey: string;
}

export interface GrievanceSubmission {
  categoryId: string;
  details: string;
  name?: string;
  contact?: string;
}

export interface GrievanceRecord {
  id: string;
  categoryId: string;
  details: string;
  status: GrievanceStatus;
  submittedAt: string;
  timeline: { status: GrievanceStatus; at: string }[];
}

const store = new Map<string, GrievanceRecord>();

export function getGrievanceCategories(): GrievanceCategory[] {
  return [
    { id: "insurance", labelKey: "grievance.category.insurance" },
    { id: "pacs", labelKey: "grievance.category.pacs" },
    { id: "service", labelKey: "grievance.category.service" },
    { id: "other", labelKey: "grievance.category.other" },
  ];
}

export function submitGrievance(sub: GrievanceSubmission): GrievanceRecord {
  const id = `GRV-${Date.now().toString(36).toUpperCase()}${Math.random().toString(36).slice(2, 5).toUpperCase()}`;
  const now = new Date().toISOString();
  const record: GrievanceRecord = {
    id,
    categoryId: sub.categoryId,
    details: sub.details,
    status: "submitted",
    submittedAt: now,
    timeline: [{ status: "submitted", at: now }],
  };
  store.set(id, record);
  return record;
}

export function getGrievanceStatus(id: string): GrievanceRecord | undefined {
  return store.get(id);
}
