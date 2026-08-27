import type { Locale } from "@/lib/i18n/i18n";
import { localize, type I18nText } from "./i18n";

export interface LibraryDoc {
  id: string;
  title: I18nText;
  source: I18nText;
  page: number;
  url: string;
  domain: string;
  publishedAt: string;
}

export const libraryDocs: LibraryDoc[] = [
  { id: "l1", title: { en: "Pradhan Mantri Fasal Bima Yojana — Operational Guidelines" }, source: { en: "Ministry of Cooperation" }, page: 12, url: "https://pmfby.gov.in", domain: "cropInsurance", publishedAt: "2025-04-02" },
  { id: "l2", title: { en: "Model Bye-laws of Primary Agricultural Credit Societies" }, source: { en: "Ministry of Cooperation" }, page: 6, url: "https://www.moc.gov.in", domain: "law", publishedAt: "2024-11-18" },
  { id: "l3", title: { en: "Multi-State Cooperative Societies Act, 2002 — Key Provisions" }, source: { en: "Ministry of Cooperation" }, page: 24, url: "https://www.moc.gov.in", domain: "law", publishedAt: "2024-08-30" },
  { id: "l4", title: { en: "Kisan Credit Card — Scheme Guidelines" }, source: { en: "NABARD" }, page: 8, url: "https://www.nabard.org", domain: "financial", publishedAt: "2025-01-21" },
  { id: "l5", title: { en: "Grievance Redressal Mechanism for Cooperative Societies" }, source: { en: "Ministry of Cooperation" }, page: 4, url: "https://www.moc.gov.in", domain: "grievance", publishedAt: "2025-02-11" },
];

export interface LocalizedLibraryDoc {
  id: string;
  title: string;
  source: string;
  page: number;
  url: string;
  domain: string;
  publishedAt: string;
}

export function getLibraryDocs(locale: Locale): LocalizedLibraryDoc[] {
  return libraryDocs.map((d) => ({
    id: d.id,
    title: localize(d.title, locale),
    source: localize(d.source, locale),
    page: d.page,
    url: d.url,
    domain: d.domain,
    publishedAt: d.publishedAt,
  }));
}
