import type { Locale } from "@/lib/i18n/i18n";
import { localize, localizeList, type I18nList, type I18nText } from "./i18n";

export type SchemeCategory = "crop-insurance" | "pacs" | "financial" | "subsidy";

export interface Scheme {
  slug: string;
  category: SchemeCategory;
  name: I18nText;
  benefit: I18nText;
  overview: I18nText;
  eligibility: I18nList;
  benefits: I18nList;
  howToApply: I18nList;
  documents: I18nList;
}

const ACCENTS = ["#047857", "#b45309", "#1d4ed8", "#6d28d9", "#be123c"];
export function schemeColors(slug: string): string {
  let h = 0;
  for (let i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) >>> 0;
  return ACCENTS[h % ACCENTS.length];
}

export const schemes: Scheme[] = [
  {
    slug: "pmfby",
    category: "crop-insurance",
    name: { en: "Pradhan Mantri Fasal Bima Yojana (PMFBY)" },
    benefit: { en: "Comprehensive crop insurance against natural calamities and pest attacks." },
    overview: { en: "PMFBY provides insurance cover and financial support to farmers against failure of crops due to natural calamities, pests and diseases. Farmers pay a low premium while the central and state governments cover the rest." },
    eligibility: { en: ["All farmers including sharecroppers and tenant farmers.", "Both loanee (credit-linked) and non-loanee farmers.", "Notification of the crop season of the implementing state."] },
    benefits: { en: ["Low premium: up to 2% for Kharif and 1.5% for Rabi food crops.", "Full sum insured on crop loss due to listed risks.", "Post-harvest losses and localized calamity coverage."] },
    howToApply: { en: ["Register a consent letter on the PMFBY portal or through your bank.", "Approach your PACS / CSC / bank branch before the crop season deadline.", "Keep land records and sowing receipts ready for claim filing."] },
    documents: { en: ["Aadhaar card", "Land ownership / tenancy records", "Bank passbook", "Sowing certificate"] },
  },
  {
    slug: "pacs-membership",
    category: "pacs",
    name: { en: "PACS Membership & Services" },
    benefit: { en: "Access to credit, storage and agro-services through your local cooperative." },
    overview: { en: "The Primary Agricultural Credit Society (PACS) is the village-level cooperative that lends to members, provides farm inputs and supports storage. Joining gives you access to affordable credit and grievance recourse." },
    eligibility: { en: ["Residents of the PACS area of operation.", "Any person of the village who owns land or engages in agriculture."] },
    benefits: { en: ["Short-term crop loans at subsidized rates.", "Storage and godown facilities.", "Fertilizers, seeds and agro-equipment on demand."] },
    howToApply: { en: ["Visit your local PACS office and fill the membership form.", "Submit identity and residence documents.", "Pay the small share/entrance fee as notified."] },
    documents: { en: ["Aadhaar card", "Passport-size photo", "Income/residence proof"] },
  },
  {
    slug: "kisan-credit-card",
    category: "financial",
    name: { en: "Kisan Credit Card (KCC)" },
    benefit: { en: "Affordable, flexible crop credit with insurance and repayment support." },
    overview: { en: "KCC is a credit card for farmers for crop production needs, post-harvest expenses, and consumption. It bundles a personal accident insurance cover and provides flexible repayment aligned with harvest cycles." },
    eligibility: { en: ["Owner-cultivators, tenant farmers and sharecroppers.", "Members of PACS / cooperative credit institutions."] },
    benefits: { en: ["Short-term credit with competitive interest and interest subvention.", "Composite loan for cultivation and post-harvest needs.", "Personal accident insurance cover."] },
    howToApply: { en: ["Apply at your bank or PACS with KCC application form.", "Provide land, identity and crop-cycle details.", "Receive the card after sanction and verification."] },
    documents: { en: ["Aadhaar", "Land records", "Crop details", "Bank passbook"] },
  },
  {
    slug: "coop-subsidy",
    category: "subsidy",
    name: { en: "Cooperative & Subsidy Schemes" },
    benefit: { en: "Capital, interest and infrastructure subsidies for cooperatives and farmers." },
    overview: { en: "The Ministry of Cooperation and allied bodies run several subsidy schemes for farmer cooperatives — capital support, interest subvention, godown and processing infrastructure, to strengthen local cooperatives." },
    eligibility: { en: ["Registered cooperatives / PACS within the scheme scope.", "Individual farmers applying through eligible cooperative channels."] },
    benefits: { en: ["Capital support for cooperative infrastructure.", "Interest subvention on eligible loans.", "Support for godowns, processing and storage units."] },
    howToApply: { en: ["Check eligibility against the current scheme guidelines.", "Submit the application through the portal or the nodal cooperative office.", "Track approval and disbursal status on the portal."] },
    documents: { en: ["Cooperative registration certificate", "Financial statements", "Project proposal"] },
  },
  {
    slug: "pmay-gramin",
    category: "subsidy",
    name: { en: "Pradhan Mantri Awas Yojana – Gramin (PMAY-G)" },
    benefit: { en: "Financial assistance for housing to eligible rural families." },
    overview: { en: "PMAY-G supports construction of pucca houses for eligible rural households with central and state assistance." },
    eligibility: { en: ["Households without a pucca house.", "Beneficiary confirmed on SECC / Awas+ list."] },
    benefits: { en: ["Direct cash transfer under the scheme.", "Financial support for toilet and electricity (targeted areas)."] },
    howToApply: { en: ["Apply through the Awas+ portal or your PACS / gram panchayat.", "Complete the geo-tagging and verification."] },
    documents: { en: ["Aadhaar", "Bank account", "SECC / beneficiary confirmation"] },
  },
  {
    slug: "financial-literacy",
    category: "financial",
    name: { en: "Financial Literacy Programmes" },
    benefit: { en: "Learn savings, borrowing, insurance and grievance basics." },
    overview: { en: "Financial literacy modules help cooperative members understand savings, affordable credit, insurance and safe digital banking practices." },
    eligibility: { en: ["All farmers, PACS members and rural stakeholders."] },
    benefits: { en: ["Better savings and borrowing decisions.", "Awareness of insurance and entitlements.", "Safety against fraud and over-borrowing."] },
    howToApply: { en: ["Join village-level camps organized by PACS / banks.", "Use the chatbot for simple, plain-language guidance."] },
    documents: { en: ["None — open participation"] },
  },
];

export interface LocalizedScheme {
  slug: string;
  category: SchemeCategory;
  name: string;
  benefit: string;
  overview: string;
  eligibility: string[];
  benefits: string[];
  howToApply: string[];
  documents: string[];
}

export function getSchemes(locale: Locale): LocalizedScheme[] {
  return schemes.map((s) => ({
    slug: s.slug,
    category: s.category,
    name: localize(s.name, locale),
    benefit: localize(s.benefit, locale),
    overview: localize(s.overview, locale),
    eligibility: localizeList(s.eligibility, locale),
    benefits: localizeList(s.benefits, locale),
    howToApply: localizeList(s.howToApply, locale),
    documents: localizeList(s.documents, locale),
  }));
}
export function getScheme(locale: Locale, slug: string): LocalizedScheme | undefined {
  const found = schemes.find((s) => s.slug === slug);
  if (!found) return undefined;
  return {
    slug: found.slug,
    category: found.category,
    name: localize(found.name, locale),
    benefit: localize(found.benefit, locale),
    overview: localize(found.overview, locale),
    eligibility: localizeList(found.eligibility, locale),
    benefits: localizeList(found.benefits, locale),
    howToApply: localizeList(found.howToApply, locale),
    documents: localizeList(found.documents, locale),
  };
}
