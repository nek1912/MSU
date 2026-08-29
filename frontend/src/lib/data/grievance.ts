export type GrievanceStatus = "submitted" | "in-review" | "resolved";

export interface GrievanceCategory {
  id: string;
  labelKey: string;
}

export interface GrievanceTimelineEntry {
  status: string;
  timestamp: string;
}

export interface GrievanceRecord {
  id: string;
  categoryId: string;
  details: string;
  name?: string;
  contact?: string;
  status: string;
  timeline: GrievanceTimelineEntry[];
}

const CATEGORIES: GrievanceCategory[] = [
  { id: "insurance", labelKey: "grievance.category.insurance" },
  { id: "pacs", labelKey: "grievance.category.pacs" },
  { id: "service", labelKey: "grievance.category.service" },
  { id: "other", labelKey: "grievance.category.other" },
];

const store = new Map<string, GrievanceRecord>();
let counter = 0;

export function getGrievanceCategories(): GrievanceCategory[] {
  return CATEGORIES;
}

export function submitGrievance(input: {
  categoryId: string;
  details: string;
  name?: string;
  contact?: string;
}): GrievanceRecord {
  counter++;
  const id = `GRV-${String(counter).padStart(5, "0")}`;
  const now = new Date().toISOString();
  const record: GrievanceRecord = {
    id,
    categoryId: input.categoryId,
    details: input.details,
    name: input.name,
    contact: input.contact,
    status: "submitted",
    timeline: [{ status: "submitted", timestamp: now }],
  };
  store.set(id, record);
  return record;
}

export function getGrievanceStatus(id: string): GrievanceRecord | undefined {
  return store.get(id);
}
