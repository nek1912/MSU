export type ServiceCategory = "credit" | "storage" | "insurance" | "agro-inputs" | "subsidy" | "membership";

export interface Service {
  slug: string;
  name: string;
  category: ServiceCategory;
  summary: string;
  description: string;
  whoCanUse: string[];
  howToAccess: string[];
  source: { label: string; url: string };
}

export const services: Service[] = [
  {
    slug: "pacs-membership",
    name: "PACS Membership",
    category: "membership",
    summary: "Become a member of your village cooperative to access credit and services.",
    description:
      "Joining your Primary Agricultural Credit Society gives you access to affordable credit, storage, inputs and a channel to raise grievances.",
    whoCanUse: ["Residents of the PACS area of operation.", "Landowners, tenant farmers and sharecroppers."],
    howToAccess: ["Visit your local PACS office.", "Submit identity and residence documents.", "Pay the share/entrance fee."],
    source: { label: "PACS / Cooperative Department", url: "https://www.moc.gov.in" },
  },
  {
    slug: "short-term-crop-credit",
    name: "Short-term Crop Credit",
    category: "credit",
    summary: "Seasonal crop loans at subsidised interest to fund sowing to harvest.",
    description:
      "Short-term crop loans cover cultivation costs and are repaid after harvest, often with interest subvention for timely repayment.",
    whoCanUse: ["Member farmers of a PACS or cooperative credit institution."],
    howToAccess: ["Apply at your PACS or bank with KCC application.", "Provide land, identity and crop-cycle details."],
    source: { label: "PACS / Bank", url: "https://www.moc.gov.in" },
  },
  {
    slug: "godown-storage",
    name: "Godown & Storage",
    category: "storage",
    summary: "Safe storage of produce to avoid distress sales and improve bargaining.",
    description:
      "PACS and cooperative unions operate godowns where members can store grain and produce, and access pledge loans against stock.",
    whoCanUse: ["Member farmers with stored produce.", "Producers holding warehouses/pledge receipts."],
    howToAccess: ["Register storage at your nearest PACS godown.", "Obtain a warehouse receipt to pledge for a loan."],
    source: { label: "PACS / Warehousing", url: "https://www.moc.gov.in" },
  },
  {
    slug: "agro-input-supply",
    name: "Agro-input Supply",
    category: "agro-inputs",
    summary: "Seeds, fertilisers and farm equipment supplied through the cooperative.",
    description:
      "PACS supply certified seeds, fertilisers, pesticides and farm equipment in bulk to members at fair prices.",
    whoCanUse: ["PACS member farmers.", "Village residents in the society's area."],
    howToAccess: ["Place a request at the PACS sale counter or branches.", "Pay against the invoice and collect inputs."],
    source: { label: "PACS / Agro-supply", url: "https://www.moc.gov.in" },
  },
  {
    slug: "pmfby-enrolment",
    name: "PMFBY Enrolment",
    category: "insurance",
    summary: "Enrol in crop insurance under PMFBY through your cooperative or CSC.",
    description:
      "Pradhan Mantri Fasal Bima Yojana protects farmers against crop loss. PACS, banks and CSCs act as enrolment and claim-filing channels.",
    whoCanUse: ["All farmers, loanee and non-loanee, within notified areas."],
    howToAccess: ["Sign a consent letter before the season deadline.", "Enrol at PACS / CSC / bank and keep land records."],
    source: { label: "PMFBY", url: "https://pmfby.gov.in" },
  },
  {
    slug: "cooperative-subsidy",
    name: "Cooperative Subsidy",
    category: "subsidy",
    summary: "Capital, interest and infrastructure subsidies for farmer cooperatives.",
    description:
      "The Ministry of Cooperation and allies run subsidy schemes for cooperative infrastructure — godowns, processing units and interest subvention.",
    whoCanUse: ["Registered cooperatives / PACS within scheme scope.", "Farmers applying through eligible cooperative channels."],
    howToAccess: ["Check eligibility against current guidelines.", "Submit the application via the portal or nodal office."],
    source: { label: "Ministry of Cooperation", url: "https://www.moc.gov.in" },
  },
];

export function getServices(): Service[] {
  return services;
}
export function getService(slug: string): Service | undefined {
  return services.find((s) => s.slug === slug);
}
