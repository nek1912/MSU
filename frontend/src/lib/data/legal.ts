export type LegalCategory = "act" | "bye-laws" | "provisions";

export interface LegalDoc {
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

export const legalDocs: LegalDoc[] = [
  {
    slug: "mscs-act-2002",
    title: "Multi-State Cooperative Societies Act, 2002",
    badge: "MSCS Act 2002",
    category: "act",
    overview:
      "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies that operate across more than one state in India. It sets out the legal framework for their registration, management, elections, and governance.",
    keyProvisions: [
      "Registration of multi-state cooperative societies with the Central Registrar.",
      "Membership rights and representation across member states.",
      "Election of the board of directors and tenure of the board.",
      "Reserve fund, audits, and annual returns under the Act.",
    ],
    applicability: ["Cooperative societies operating in two or more states."],
    byLaws: ["Each society adopts its own by-laws consistent with the Act and its rules."],
    source: { label: "Ministry of Cooperation", url: "https://www.moc.gov.in" },
  },
  {
    slug: "model-pacs-bye-laws",
    title: "Model Bye-laws of Primary Agricultural Credit Societies",
    badge: "Model PACS Bye-laws",
    category: "bye-laws",
    overview:
      "The model bye-laws prescribe the standard constitution and operational rules for Primary Agricultural Credit Societies (PACS) — the village-level cooperatives that provide credit and farm services.",
    keyProvisions: [
      "Eligibility and procedure for membership, share capital and entrance fees.",
      "Powers and duties of the board of directors.",
      "Conduct of general body meetings and voting rights.",
      "Appointment of the secretary and staff.",
    ],
    applicability: [
      "New and existing PACS that adopt the model bye-laws or a state-approved variant.",
    ],
    byLaws: [
      "Borrowing limits and lending rules for members.",
      "Formation of sub-committees for loans, audit and grievances.",
    ],
    source: { label: "Ministry of Cooperation", url: "https://www.moc.gov.in" },
  },
  {
    slug: "board-election-rules",
    title: "Election of Board of Directors — MSCS Rules, 2011",
    badge: "Board Elections",
    category: "provisions",
    overview:
      "The MSCS Rules, 2011 detail how the board of a multi-state cooperative society is elected, including the role of the election authority, the electoral college and the election timetable.",
    keyProvisions: [
      "Appointment of an election authority to conduct elections.",
      "Preparation and certification of the electoral college.",
      "Dates for the e-election/ballot and counting of votes.",
    ],
    applicability: ["Multi-state cooperative societies governed by MSCS Rules, 2011."],
    byLaws: ["Society bye-laws set the size and composition of the board."],
    source: { label: "Ministry of Cooperation", url: "https://www.moc.gov.in" },
  },
  {
    slug: "cooperative-disputes",
    title: "Cooperative Dispute Resolution",
    badge: "Disputes",
    category: "provisions",
    overview:
      "Disputes between a cooperative and its members — over loans, share capital, or by-law obligations — are resolved through arbitration or a cooperative dispute authority, not regular civil courts.",
    keyProvisions: [
      "Matters that are deemed disputes under the Act.",
      "Reference of disputes to arbitration or a designated authorit(y).",
      "Enforceability of arbitration awards.",
    ],
    applicability: ["Members, former members and cooperatives facing internal disputes."],
    byLaws: ["By-laws may prescribe an internal grievance-cum-dispute resolution committee."],
    source: { label: "Ministry of Cooperation", url: "https://www.moc.gov.in" },
  },
  {
    slug: "pac-model-bye-laws-moc",
    title: "Model Bye-laws for PACS — Ministry of Cooperation",
    badge: "PACS Bye-laws (MoC)",
    category: "bye-laws",
    overview:
      "The Ministry of Cooperation's revised model bye-laws modernise PACS — enabling them to provide banking, storage, and agro-services while keeping their village-level cooperative character.",
    keyProvisions: [
      "Minimum and maximum share capital for members.",
      "Wider business activities beyond lending (storage, insurance, IT services).",
      "Digital operational requirements and record-keeping.",
    ],
    applicability: ["PACS registered under the cooperative law of the state."],
    byLaws: ["Fees, dividends and reserve allocations set in the bye-laws."],
    source: { label: "Ministry of Cooperation", url: "https://www.moc.gov.in" },
  },
];

export function getLegalDocs(): LegalDoc[] {
  return legalDocs;
}
export function getLegalDoc(slug: string): LegalDoc | undefined {
  return legalDocs.find((d) => d.slug === slug);
}
