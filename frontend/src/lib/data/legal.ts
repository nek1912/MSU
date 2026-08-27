import type { Locale } from "@/lib/i18n/i18n";
import { localize, localizeList, type I18nList, type I18nText } from "./i18n";

export type LegalCategory = "act" | "bye-laws" | "provisions";

export interface LegalDoc {
  slug: string;
  title: I18nText;
  badge: I18nText;
  category: LegalCategory;
  overview: I18nText;
  keyProvisions: I18nList;
  applicability: I18nList;
  byLaws: I18nList;
  source: { label: I18nText; url: string };
}

export const legalDocs: LegalDoc[] = [
  {
    slug: "mscs-act-2002",
    title: { en: "Multi-State Cooperative Societies Act, 2002" },
    badge: { en: "MSCS Act 2002" },
    category: "act",
    overview: {
      en: "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies that operate across more than one state in India. It sets out the legal framework for their registration, management, elections, and governance.",
    },
    keyProvisions: {
      en: [
        "Registration of multi-state cooperative societies with the Central Registrar.",
        "Membership rights and representation across member states.",
        "Election of the board of directors and tenure of the board.",
        "Reserve fund, audits, and annual returns under the Act.",
      ],
    },
    applicability: { en: ["Cooperative societies operating in two or more states."] },
    byLaws: { en: ["Each society adopts its own by-laws consistent with the Act and its rules."] },
    source: { label: { en: "Ministry of Cooperation" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "model-pacs-bye-laws",
    title: { en: "Model Bye-laws of Primary Agricultural Credit Societies" },
    badge: { en: "Model PACS Bye-laws" },
    category: "bye-laws",
    overview: {
      en: "The model bye-laws prescribe the standard constitution and operational rules for Primary Agricultural Credit Societies (PACS) — the village-level cooperatives that provide credit and farm services.",
    },
    keyProvisions: {
      en: [
        "Eligibility and procedure for membership, share capital and entrance fees.",
        "Powers and duties of the board of directors.",
        "Conduct of general body meetings and voting rights.",
        "Appointment of the secretary and staff.",
      ],
    },
    applicability: {
      en: [
        "New and existing PACS that adopt the model bye-laws or a state-approved variant.",
      ],
    },
    byLaws: {
      en: [
        "Borrowing limits and lending rules for members.",
        "Formation of sub-committees for loans, audit and grievances.",
      ],
    },
    source: { label: { en: "Ministry of Cooperation" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "board-election-rules",
    title: { en: "Election of Board of Directors — MSCS Rules, 2011" },
    badge: { en: "Board Elections" },
    category: "provisions",
    overview: {
      en: "The MSCS Rules, 2011 detail how the board of a multi-state cooperative society is elected, including the role of the election authority, the electoral college and the election timetable.",
    },
    keyProvisions: {
      en: [
        "Appointment of an election authority to conduct elections.",
        "Preparation and certification of the electoral college.",
        "Dates for the e-election/ballot and counting of votes.",
      ],
    },
    applicability: { en: ["Multi-state cooperative societies governed by MSCS Rules, 2011."] },
    byLaws: { en: ["Society bye-laws set the size and composition of the board."] },
    source: { label: { en: "Ministry of Cooperation" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "cooperative-disputes",
    title: { en: "Cooperative Dispute Resolution" },
    badge: { en: "Disputes" },
    category: "provisions",
    overview: {
      en: "Disputes between a cooperative and its members — over loans, share capital, or by-law obligations — are resolved through arbitration or a cooperative dispute authority, not regular civil courts.",
    },
    keyProvisions: {
      en: [
        "Matters that are deemed disputes under the Act.",
        "Reference of disputes to arbitration or a designated authority.",
        "Enforceability of arbitration awards.",
      ],
    },
    applicability: { en: ["Members, former members and cooperatives facing internal disputes."] },
    byLaws: { en: ["By-laws may prescribe an internal grievance-cum-dispute resolution committee."] },
    source: { label: { en: "Ministry of Cooperation" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "pac-model-bye-laws-moc",
    title: { en: "Model Bye-laws for PACS — Ministry of Cooperation" },
    badge: { en: "PACS Bye-laws (MoC)" },
    category: "bye-laws",
    overview: {
      en: "The Ministry of Cooperation's revised model bye-laws modernise PACS — enabling them to provide banking, storage, and agro-services while keeping their village-level cooperative character.",
    },
    keyProvisions: {
      en: [
        "Minimum and maximum share capital for members.",
        "Wider business activities beyond lending (storage, insurance, IT services).",
        "Digital operational requirements and record-keeping.",
      ],
    },
    applicability: { en: ["PACS registered under the cooperative law of the state."] },
    byLaws: { en: ["Fees, dividends and reserve allocations set in the bye-laws."] },
    source: { label: { en: "Ministry of Cooperation" }, url: "https://www.moc.gov.in" },
  },
];

export interface LocalizedLegalDoc {
  slug: string;
  title: string;
  badge: string;
  category: LegalCategory;
  overview: string;
  keyProvisions: string[];
  applicability: string[];
  byLaws: string[];
  source: { label: string; url: string };
}

export function getLegalDocs(locale: Locale): LocalizedLegalDoc[] {
  return legalDocs.map((d) => ({
    slug: d.slug,
    category: d.category,
    title: localize(d.title, locale),
    badge: localize(d.badge, locale),
    overview: localize(d.overview, locale),
    keyProvisions: localizeList(d.keyProvisions, locale),
    applicability: localizeList(d.applicability, locale),
    byLaws: localizeList(d.byLaws, locale),
    source: { label: localize(d.source.label, locale), url: d.source.url },
  }));
}
export function getLegalDoc(locale: Locale, slug: string): LocalizedLegalDoc | undefined {
  const found = legalDocs.find((d) => d.slug === slug);
  if (!found) return undefined;
  return {
    slug: found.slug,
    category: found.category,
    title: localize(found.title, locale),
    badge: localize(found.badge, locale),
    overview: localize(found.overview, locale),
    keyProvisions: localizeList(found.keyProvisions, locale),
    applicability: localizeList(found.applicability, locale),
    byLaws: localizeList(found.byLaws, locale),
    source: { label: localize(found.source.label, locale), url: found.source.url },
  };
}
