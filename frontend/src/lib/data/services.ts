import type { Locale } from "@/lib/i18n/i18n";
import { localize, localizeList, type I18nList, type I18nText } from "./i18n";

export type ServiceCategory = "credit" | "storage" | "insurance" | "agro-inputs" | "subsidy" | "membership";

export interface Service {
  slug: string;
  name: I18nText;
  category: ServiceCategory;
  summary: I18nText;
  description: I18nText;
  whoCanUse: I18nList;
  howToAccess: I18nList;
  source: { label: I18nText; url: string };
}

export const services: Service[] = [
  {
    slug: "pacs-membership",
    name: { en: "PACS Membership" },
    category: "membership",
    summary: { en: "Become a member of your village cooperative to access credit and services." },
    description:
      { en: "Joining your Primary Agricultural Credit Society gives you access to affordable credit, storage, inputs and a channel to raise grievances." },
    whoCanUse: { en: ["Residents of the PACS area of operation.", "Landowners, tenant farmers and sharecroppers."] },
    howToAccess: { en: ["Visit your local PACS office.", "Submit identity and residence documents.", "Pay the share/entrance fee."] },
    source: { label: { en: "PACS / Cooperative Department" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "short-term-crop-credit",
    name: { en: "Short-term Crop Credit" },
    category: "credit",
    summary: { en: "Seasonal crop loans at subsidised interest to fund sowing to harvest." },
    description:
      { en: "Short-term crop loans cover cultivation costs and are repaid after harvest, often with interest subvention for timely repayment." },
    whoCanUse: { en: ["Member farmers of a PACS or cooperative credit institution."] },
    howToAccess: { en: ["Apply at your PACS or bank with KCC application.", "Provide land, identity and crop-cycle details."] },
    source: { label: { en: "PACS / Bank" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "godown-storage",
    name: { en: "Godown & Storage" },
    category: "storage",
    summary: { en: "Safe storage of produce to avoid distress sales and improve bargaining." },
    description:
      { en: "PACS and cooperative unions operate godowns where members can store grain and produce, and access pledge loans against stock." },
    whoCanUse: { en: ["Member farmers with stored produce.", "Producers holding warehouses/pledge receipts."] },
    howToAccess: { en: ["Register storage at your nearest PACS godown.", "Obtain a warehouse receipt to pledge for a loan."] },
    source: { label: { en: "PACS / Warehousing" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "agro-input-supply",
    name: { en: "Agro-input Supply" },
    category: "agro-inputs",
    summary: { en: "Seeds, fertilisers and farm equipment supplied through the cooperative." },
    description:
      { en: "PACS supply certified seeds, fertilisers, pesticides and farm equipment in bulk to members at fair prices." },
    whoCanUse: { en: ["PACS member farmers.", "Village residents in the society's area."] },
    howToAccess: { en: ["Place a request at the PACS sale counter or branches.", "Pay against the invoice and collect inputs."] },
    source: { label: { en: "PACS / Agro-supply" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "pmfby-enrolment",
    name: { en: "PMFBY Enrolment" },
    category: "insurance",
    summary: { en: "Enrol in crop insurance under PMFBY through your cooperative or CSC." },
    description:
      { en: "Pradhan Mantri Fasal Bima Yojana protects farmers against crop loss. PACS, banks and CSCs act as enrolment and claim-filing channels." },
    whoCanUse: { en: ["All farmers, loanee and non-loanee, within notified areas."] },
    howToAccess: { en: ["Sign a consent letter before the season deadline.", "Enrol at PACS / CSC / bank and keep land records."] },
    source: { label: { en: "PMFBY" }, url: "https://pmfby.gov.in" },
  },
  {
    slug: "cooperative-subsidy",
    name: { en: "Cooperative Subsidy" },
    category: "subsidy",
    summary: { en: "Capital, interest and infrastructure subsidies for farmer cooperatives." },
    description:
      { en: "The Ministry of Cooperation and allies run subsidy schemes for cooperative infrastructure — godowns, processing units and interest subvention." },
    whoCanUse: { en: ["Registered cooperatives / PACS within scheme scope.", "Farmers applying through eligible cooperative channels."] },
    howToAccess: { en: ["Check eligibility against current guidelines.", "Submit the application via the portal or nodal office."] },
    source: { label: { en: "Ministry of Cooperation" }, url: "https://www.moc.gov.in" },
  },
];

export interface LocalizedService {
  slug: string;
  category: ServiceCategory;
  name: string;
  summary: string;
  description: string;
  whoCanUse: string[];
  howToAccess: string[];
  source: { label: string; url: string };
}

function localizeService(s: Service, locale: Locale): LocalizedService {
  return {
    slug: s.slug,
    category: s.category,
    name: localize(s.name, locale),
    summary: localize(s.summary, locale),
    description: localize(s.description, locale),
    whoCanUse: localizeList(s.whoCanUse, locale),
    howToAccess: localizeList(s.howToAccess, locale),
    source: { label: localize(s.source.label, locale), url: s.source.url },
  };
}

export function getServices(locale: Locale): LocalizedService[] {
  return services.map((s) => localizeService(s, locale));
}
export function getService(locale: Locale, slug: string): LocalizedService | undefined {
  const found = services.find((s) => s.slug === slug);
  if (!found) return undefined;
  return localizeService(found, locale);
}
