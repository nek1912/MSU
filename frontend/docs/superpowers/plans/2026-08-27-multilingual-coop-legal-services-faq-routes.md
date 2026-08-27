# Legal, Services & FAQ Routes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three high-value routes — `/legal`, `/services`, `/faq` — plus their detail pages, navigation entries, i18n strings, and a `?q=` chat deep-link, mirroring the existing schemes/library UI.

**Architecture:** Follow the established idiom: static data module in `src/lib/data/` + list page (`src/app` route) + dynamic detail page (`/route/[slug]`), styled with existing Promptiq token components (`Card`, `Badge`, `Chips`, `Input`, `EmptyState`, `Button`) and `useI18n()` for strings. Content is English (in data), labels translated — exactly like existing schemes data. No new dependencies.

**Tech Stack:** Next.js 16 App Router (client components, Turbopack), React 19, TypeScript, Tailwind v4 tokens, Vitest for lib tests.

## Global Constraints

- **Tokens only in components:** UI code must use `var(--*)` design tokens (`--surface-overlay`, `--surface-elevated`, `--text-primary`, `--text-secondary`, `--border-default`, `--accent-primary`, `--color-pill`). No raw hex in TSX. (Hex allowed only in data/accent helper.)
- **Focus states:** every interactive element gets visible `focus-visible:ring-2 ring-[var(--border-focus)]`.
- **i18n:** page strings go through `useI18n()`; `en` + `hi` fully translated, `nav.*` for `mr/bn/ta` (match current coverage). Content strings stay English in data modules.
- **Testing:** data modules only (repo has no component/UI test runner). Verify UI via `npm run lint` + `npm run build`.
- **No new dependencies.**
- **Files: all under `A:\MSU\frontend`.**

---

### Task 1: Data modules + shared accent helper + tests

**Files:**
- Create: `src/lib/data/accent.ts`
- Create: `src/lib/data/legal.ts`
- Create: `src/lib/data/services.ts`
- Create: `src/lib/data/faq.ts`
- Modify: `src/lib/data/index.ts` (add exports)
- Test: `src/lib/data/legal.test.ts`
- Test: `src/lib/data/services.test.ts`
- Test: `src/lib/data/faq.test.ts`

**Interfaces:**
- Produces: `slugAccent(slug: string): string`; `LegalDoc`/`getLegalDocs()`/`getLegalDoc(slug)`; `Service`/`getServices()`/`getService(slug)`; `FaqItem`/`getFaqItems()`. Later tasks import these from `@/lib/data`.

- [ ] **Step 1: Write failing tests**

`src/lib/data/legal.test.ts`:
```ts
import { test, expect } from "vitest";
import { getLegalDocs, getLegalDoc } from "./legal";

test("legal accessors return well-formed data", () => {
  const all = getLegalDocs();
  expect(all.length).toBeGreaterThan(0);
  expect(all[0]).toHaveProperty("slug");
  expect(all[0]).toHaveProperty("category");
  const slugs = new Set(all.map((d) => d.slug));
  expect(slugs.size).toBe(all.length);
  expect(getLegalDoc("mscs-act-2002")).toBeDefined();
  expect(getLegalDoc("nope")).toBeUndefined();
});
```

`src/lib/data/services.test.ts`:
```ts
import { test, expect } from "vitest";
import { getServices, getService } from "./services";

test("services accessors return well-formed data", () => {
  const all = getServices();
  expect(all.length).toBeGreaterThan(0);
  expect(all[0]).toHaveProperty("slug");
  expect(all[0]).toHaveProperty("category");
  const slugs = new Set(all.map((s) => s.slug));
  expect(slugs.size).toBe(all.length);
  expect(getService("pacs-membership")).toBeDefined();
  expect(getService("nope")).toBeUndefined();
});
```

`src/lib/data/faq.test.ts`:
```ts
import { test, expect } from "vitest";
import { getFaqItems } from "./faq";

test("faq items are well-formed", () => {
  const all = getFaqItems();
  expect(all.length).toBeGreaterThan(0);
  expect(all[0]).toHaveProperty("id");
  expect(all[0]).toHaveProperty("category");
  expect(all[0]).toHaveProperty("question");
  expect(all[0]).toHaveProperty("answer");
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm run test -- --run`
Expected: FAIL — modules `./legal`, `./services`, `./faq` not found.

- [ ] **Step 3: Create `src/lib/data/accent.ts`**

```ts
const ACCENTS = ["#047857", "#b45309", "#1d4ed8", "#6d28d9", "#be123c"];
export function slugAccent(slug: string): string {
  let h = 0;
  for (let i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) >>> 0;
  return ACCENTS[h % ACCENTS.length];
}
```

- [ ] **Step 4: Create `src/lib/data/legal.ts`**

```ts
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
```

- [ ] **Step 5: Create `src/lib/data/services.ts`**

```ts
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
```

- [ ] **Step 6: Create `src/lib/data/faq.ts`**

```ts
export type FaqCategory = "crop-insurance" | "pacs" | "financial" | "grievance" | "legal";

export interface FaqItem {
  id: string;
  category: FaqCategory;
  question: string;
  answer: string;
}

export const faqItems: FaqItem[] = [
  {
    id: "f1",
    category: "crop-insurance",
    question: "What is PMFBY crop insurance?",
    answer:
      "PMFBY (Pradhan Mantri Fasal Bima Yojana) is a crop insurance scheme. Farmers pay a small premium and the rest is subsidised by the government, covering crop loss from natural calamities, pests and diseases.",
  },
  {
    id: "f2",
    category: "crop-insurance",
    question: "How do I claim under PMFBY?",
    answer:
      "File a claim before the deadline at your PACS, bank, or CSC with land records and sowing details. Compensation is disbursed after assessment of the insured crop loss.",
  },
  {
    id: "f3",
    category: "pacs",
    question: "How do I join a PACS as a member?",
    answer:
      "Visit your local PACS office, fill the membership form, submit identity and residence documents, and pay the small share/entrance fee as notified.",
  },
  {
    id: "f4",
    category: "pacs",
    question: "What services does a PACS provide?",
    answer:
      "PACS provide short-term crop loans, storage/godown facilities, agro-inputs (seed, fertiliser, equipment), insurance enrolment and a channel to raise grievances.",
  },
  {
    id: "f5",
    category: "financial",
    question: "What is a Kisan Credit Card (KCC)?",
    answer:
      "The KCC is a crop credit card for farmers offering short-term credit at competitive rates, flexible repayment after harvest, and a personal accident insurance cover.",
  },
  {
    id: "f6",
    category: "financial",
    question: "How can I improve my financial literacy?",
    answer:
      "Attend village-level camps organised by PACS and banks, and ask this chatbot plain-language questions on savings, borrowing, insurance and safe digital banking.",
  },
  {
    id: "f7",
    category: "grievance",
    question: "How do I complain about my cooperative?",
    answer:
      "Use the Grievance page to file a complaint with a category and description. You will get an ID to track the status on the grievance status page.",
  },
  {
    id: "f8",
    category: "grievance",
    question: "What categories of grievances can I raise?",
    answer:
      "Grievances can belong to crop insurance / PMFBY, PACS service, scheme or subsidy, or other cooperative matters.",
  },
  {
    id: "f9",
    category: "legal",
    question: "Which law governs multi-state cooperatives?",
    answer:
      "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies operating across more than one state.",
  },
  {
    id: "f10",
    category: "legal",
    question: "How are cooperative disputes resolved?",
    answer:
      "Disputes between a cooperative and its members are resolved through arbitration or a designated dispute authority, not regular civil courts.",
  },
  {
    id: "f11",
    category: "legal",
    question: "What are a cooperative society's by-laws?",
    answer:
      "By-laws are the society's internal rulebook covering membership, share capital, board powers, meetings and business activities, consistent with the governing Act.",
  },
];

export function getFaqItems(): FaqItem[] {
  return faqItems;
}
```

- [ ] **Step 7: Update `src/lib/data/index.ts`**

Add lines at the end:
```ts
export * from "./accent";
export * from "./legal";
export * from "./services";
export * from "./faq";
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `npm run test -- --run`
Expected: PASS (all suites).

- [ ] **Step 9: Lint + commit**

Run: `npm run lint`
Expected: no errors. Then:
```bash
git add src/lib/data/accent.ts src/lib/data/legal.ts src/lib/data/services.ts src/lib/data/faq.ts src/lib/data/index.ts src/lib/data/legal.test.ts src/lib/data/services.test.ts src/lib/data/faq.test.ts
git commit -m "feat: add legal, services and faq data modules"
```

---

### Task 2: i18n strings

**Files:**
- Modify: `src/lib/i18n/dictionaries.ts`

**Interfaces:**
- Consumes: existing `dict` / `translate` structure.
- Produces: keys `nav.legal`, `nav.services`, `nav.faq`; `legal.*`, `legalCategory.*`; `services.*`, `serviceCategory.*`; `faq.*`, `faqCategory.*` in `en` and `hi` (nav-only in `mr/bn/ta`).

- [ ] **Step 1: Add nav keys to all 5 locales**

In the `en` block, after `"nav.grievanceStatus": "Grievance status",` add:
```ts
  "nav.legal": "Legal",
  "nav.services": "Services",
  "nav.faq": "FAQ",
```
In the `hi` block after `"nav.grievanceStatus": "शिकायत स्थिति",` add:
```ts
  "nav.legal": "कानून",
  "nav.services": "सेवाएँ",
  "nav.faq": "FAQ",
```
In the `mr` block after `"nav.grievance": "तक्रार",` add:
```ts
  "nav.legal": "कायदा",
  "nav.services": "सेवा",
  "nav.faq": "FAQ",
```
In the `bn` block after `"nav.grievance": "অভিযোগ",` add:
```ts
  "nav.legal": "আইন",
  "nav.services": "সেবা",
  "nav.faq": "FAQ",
```
In the `ta` block after `"nav.grievance": "புகார்",` add:
```ts
  "nav.legal": "சட்டம்",
  "nav.services": "சேவைகள்",
  "nav.faq": "FAQ",
```

- [ ] **Step 2: Add `en` page strings**

In the `en` block, before the closing `};` (after `"chat.welcome": ...`), add:
```ts
  "legal.title": "Cooperative Laws & By-laws",
  "legal.subtitle": "Understand the acts and bye-laws that govern cooperatives.",
  "legal.searchPlaceholder": "Search laws and bye-laws…",
  "legal.empty": "No laws match your search.",
  "legal.notFound": "Law not found.",
  "legal.overview": "Overview",
  "legal.keyProvisions": "Key provisions",
  "legal.applicability": "Applicability",
  "legal.byLaws": "By-law highlights",
  "legal.source": "Official source",
  "legal.askThisLaw": "Ask about this law",
  "legalCategory.act": "Act",
  "legalCategory.bye-laws": "Bye-laws",
  "legalCategory.provisions": "Provisions",

  "services.title": "Cooperative & PACS Services",
  "services.subtitle": "Find the cooperative and PACS service you need.",
  "services.searchPlaceholder": "Search services…",
  "services.empty": "No services match your search.",
  "services.notFound": "Service not found.",
  "services.overview": "Overview",
  "services.whoCanUse": "Who can use",
  "services.howToAccess": "How to access",
  "services.source": "Official source",
  "services.askThisService": "Ask about this service",
  "serviceCategory.credit": "Credit",
  "serviceCategory.storage": "Storage",
  "serviceCategory.insurance": "Insurance",
  "serviceCategory.agro-inputs": "Agro inputs",
  "serviceCategory.subsidy": "Subsidy",
  "serviceCategory.membership": "Membership",

  "faq.title": "Frequently asked questions",
  "faq.subtitle": "Quick answers to common cooperative questions.",
  "faq.searchPlaceholder": "Search questions…",
  "faq.empty": "No questions match your search.",
  "faq.askInChat": "Ask in chat",
  "faqCategory.crop-insurance": "Crop insurance",
  "faqCategory.pacs": "PACS",
  "faqCategory.financial": "Financial",
  "faqCategory.grievance": "Grievance",
  "faqCategory.legal": "Legal",
```

- [ ] **Step 3: Add `hi` page strings**

In the `hi` block, before its closing `};` (after `"chat.welcome": ...`), add:
```ts
  "legal.title": "सहकारी कानून और उपनियम",
  "legal.subtitle": "सहकारी समितियों को नियंत्रित करने वाले अधिनियम और उपनियम समझें।",
  "legal.searchPlaceholder": "कानून और उपनियम खोजें…",
  "legal.empty": "आपकी खोज से कोई कानून मेल नहीं खाता।",
  "legal.notFound": "कानून नहीं मिला।",
  "legal.overview": "विवरण",
  "legal.keyProvisions": "मुख्य प्रावधान",
  "legal.applicability": "लागू",
  "legal.byLaws": "उपनियम की मुख्य बातें",
  "legal.source": "आधिकारिक स्रोत",
  "legal.askThisLaw": "इस कानून के बारे में पूछें",
  "legalCategory.act": "अधिनियम",
  "legalCategory.bye-laws": "उपनियम",
  "legalCategory.provisions": "प्रावधान",

  "services.title": "सहकारी और PACS सेवाएँ",
  "services.subtitle": "अपनी ज़रूरत की सहकारी और PACS सेवा खोजें।",
  "services.searchPlaceholder": "सेवाएँ खोजें…",
  "services.empty": "आपकी खोज से कोई सेवा मेल नहीं खाती।",
  "services.notFound": "सेवा नहीं मिली।",
  "services.overview": "विवरण",
  "services.whoCanUse": "कौन उपयोग कर सकता है",
  "services.howToAccess": "कैसे पाएँ",
  "services.source": "आधिकारिक स्रोत",
  "services.askThisService": "इस सेवा के बारे में पूछें",
  "serviceCategory.credit": "ऋण",
  "serviceCategory.storage": "भंडारण",
  "serviceCategory.insurance": "बीमा",
  "serviceCategory.agro-inputs": "कृषि सामग्री",
  "serviceCategory.subsidy": "सब्सिडी",
  "serviceCategory.membership": "सदस्यता",

  "faq.title": "अक्सर पूछे जाने वाले प्रश्न",
  "faq.subtitle": "सामान्य सहकारी प्रश्नों के त्वरित उत्तर।",
  "faq.searchPlaceholder": "प्रश्न खोजें…",
  "faq.empty": "आपकी खोज से कोई प्रश्न मेल नहीं खाता।",
  "faq.askInChat": "चैट में पूछें",
  "faqCategory.crop-insurance": "फ़सल बीमा",
  "faqCategory.pacs": "PACS",
  "faqCategory.financial": "वित्तीय",
  "faqCategory.grievance": "शिकायत",
  "faqCategory.legal": "कानून",
```

- [ ] **Step 4: Verify + commit**

Run: `npm run test -- --run` then `npm run lint`
Expected: PASS / no errors.
```bash
git add src/lib/i18n/dictionaries.ts
git commit -m "feat: add i18n strings for legal, services and faq routes"
```

---

### Task 3: New icons

**Files:**
- Modify: `src/components/ui/Icons.tsx`

**Interfaces:**
- Produces: `IconScale`, `IconBuilding`, `IconHelp`, `IconMore` (each accepts `className` prop, default `"w-5 h-5"`). Used by TopNav, MobileNav, and the More sheet.

- [ ] **Step 1: Add four icons**

Append before the closing of the file (after `IconGlobe`):
```tsx
export function IconScale({ className = "w-5 h-5" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M12 3v18M8 21h8M3 7l4 7-4 4 4-4m10-7-4 7 4 4-4-4m-6-11h4" />
    </svg>
  );
}
export function IconBuilding({ className = "w-5 h-5" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-3h6v3M9 8h.01M15 8h.01M9 12h.01M15 12h.01" />
    </svg>
  );
}
export function IconHelp({ className = "w-5 h-5" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M9 9a3 3 0 1 1 4.1 2.8 2 2 0 0 0-1.1 1.9v.6M12 17.5h.01" />
    </svg>
  );
}
export function IconMore({ className = "w-5 h-5" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M5 12h.01M12 12h.01M19 12h.01" />
    </svg>
  );
}
```

- [ ] **Step 2: Lint + commit**

Run: `npm run lint`
Expected: no errors.
```bash
git add src/components/ui/Icons.tsx
git commit -m "feat: add legal, services, faq and more icons"
```

---

### Task 4: `/legal` list page

**Files:**
- Create: `src/app/legal/page.tsx`

**Interfaces:**
- Consumes: `getLegalDocs()` from `@/lib/data`; `Card`, `Badge`, `Input`, `Chips`, `EmptyState`; `useI18n()`.

- [ ] **Step 1: Create the page**

```tsx
"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getLegalDocs } from "@/lib/data";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Chips } from "@/components/ui/Chips";
import { EmptyState } from "@/components/ui/EmptyState";

const CATEGORY_ALL = "all";
const categories = ["all", "act", "bye-laws", "provisions"] as const;
type Filter = (typeof categories)[number];

export default function LegalPage() {
  const { t } = useI18n();
  const all = useMemo(() => getLegalDocs(), []);
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);

  const filtered = all.filter((d) => {
    const okCat = cat === CATEGORY_ALL || d.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery =
      !q ||
      d.badge.toLowerCase().includes(q) ||
      d.overview.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  return (
    <div className="mx-auto max-w-6xl px-[var(--space-4)] py-[var(--space-8)]">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("legal.title")}</h1>
      <p className="mt-[var(--space-1)] text-[var(--text-secondary)]">{t("legal.subtitle")}</p>
      <div className="mt-[var(--space-4)] flex flex-col gap-[var(--space-3)] sm:flex-row sm:items-center">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("legal.searchPlaceholder")} className="max-w-sm" />
        <p className="text-[var(--text-sm)] text-[var(--text-secondary)]">{t("schemes.count", { n: filtered.length })}</p>
      </div>
      <div className="mt-[var(--space-4)]">
        <Chips<Filter>
          options={categories}
          value={cat}
          onChange={setCat}
          render={(c) => (c === "all" ? t("common.all") : t(`legalCategory.${c}`))}
        />
      </div>
      {filtered.length === 0 ? (
        <div className="mt-[var(--space-6)]"><EmptyState title={t("legal.empty")} /></div>
      ) : (
        <div className="mt-[var(--space-6)] grid gap-[var(--space-4)] sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((d) => (
            <Link key={d.slug} href={`/legal/${d.slug}`} className="block">
              <Card interactive>
                <Badge tone="neutral">{t(`legalCategory.${d.category}`)}</Badge>
                <h2 className="mt-[var(--space-2)] font-[var(--font-semibold)] text-[var(--text-primary)]">{d.badge}</h2>
                <p className="mt-[var(--space-1)] text-[var(--text-sm)] text-[var(--text-secondary)]">{d.overview}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify + commit**

Run: `npm run lint` (Expected: no errors), then create the missing detail route stub temporarily? Not required — build will pass with list page alone. Run `npm run build` (Expected: success).
```bash
git add src/app/legal/page.tsx
git commit -m "feat: add legal list page"
```

---

### Task 5: `/legal/[slug]` detail page

**Files:**
- Create: `src/app/legal/[slug]/page.tsx`

**Interfaces:**
- Consumes: `getLegalDoc` and `slugAccent` from `@/lib/data`; `Button`, `Badge`, `EmptyState`, `IconChevronRight`.

- [ ] **Step 1: Create the page**

```tsx
"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getLegalDoc, slugAccent } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { IconChevronRight } from "@/components/ui/Icons";

const SECTIONS = ["keyProvisions", "applicability", "byLaws"] as const;

export default function LegalDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t } = useI18n();
  const doc = getLegalDoc(slug);
  if (!doc) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState title={t("legal.notFound")} action={<Link href="/legal" className="text-sm text-[var(--accent-primary)] underline">{t("nav.legal")}</Link>} />
      </div>
    );
  }
  const accent = slugAccent(slug);
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl p-6 text-white" style={{ backgroundColor: accent }}>
        <Badge tone="neutral">{t(`legalCategory.${doc.category}`)}</Badge>
        <h1 className="mt-2 font-[var(--font-display)] text-[var(--text-2xl)] font-[var(--font-medium)] tracking-tight">{doc.title}</h1>
        <p className="mt-1 text-sm opacity-90">{doc.overview}</p>
        <Link href={`/chat?q=${encodeURIComponent("Tell me about " + doc.title)}`}>
          <Button className="mt-4 bg-white/90 !text-slate-900 hover:bg-white">
            {t("legal.askThisLaw")}
            <IconChevronRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
      <div className="mt-6 space-y-6">
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("legal.overview")}</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">{doc.overview}</p>
        </section>
        {SECTIONS.map((s) => (
          <section key={s} className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
            <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t(`legal.${s}`)}</h2>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
              {doc[s].map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>
        ))}
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("legal.source")}</h2>
          <a href={doc.source.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-sm text-[var(--accent-primary)] underline">
            {doc.source.label}
          </a>
        </section>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify + commit**

Run: `npm run lint` and `npm run build`. Expected: success.
```bash
git add src/app/legal/[slug]/page.tsx
git commit -m "feat: add legal detail page"
```

---

### Task 6: `/services` list page

**Files:**
- Create: `src/app/services/page.tsx`

**Interfaces:**
- Consumes: `getServices()` from `@/lib/data`; same components as `/legal` list.

- [ ] **Step 1: Create the page**

```tsx
"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/provider";
import { getServices } from "@/lib/data";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Chips } from "@/components/ui/Chips";
import { EmptyState } from "@/components/ui/EmptyState";

const CATEGORY_ALL = "all";
const categories = ["all", "credit", "storage", "insurance", "agro-inputs", "subsidy", "membership"] as const;
type Filter = (typeof categories)[number];

export default function ServicesPage() {
  const { t } = useI18n();
  const all = useMemo(() => getServices(), []);
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);

  const filtered = all.filter((s) => {
    const okCat = cat === CATEGORY_ALL || s.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery = !q || s.name.toLowerCase().includes(q) || s.summary.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  return (
    <div className="mx-auto max-w-6xl px-[var(--space-4)] py-[var(--space-8)]">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("services.title")}</h1>
      <p className="mt-[var(--space-1)] text-[var(--text-secondary)]">{t("services.subtitle")}</p>
      <div className="mt-[var(--space-4)] flex flex-col gap-[var(--space-3)] sm:flex-row sm:items-center">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("services.searchPlaceholder")} className="max-w-sm" />
        <p className="text-[var(--text-sm)] text-[var(--text-secondary)]">{t("schemes.count", { n: filtered.length })}</p>
      </div>
      <div className="mt-[var(--space-4)]">
        <Chips<Filter>
          options={categories}
          value={cat}
          onChange={setCat}
          render={(c) => (c === "all" ? t("common.all") : t(`serviceCategory.${c}`))}
        />
      </div>
      {filtered.length === 0 ? (
        <div className="mt-[var(--space-6)]"><EmptyState title={t("services.empty")} /></div>
      ) : (
        <div className="mt-[var(--space-6)] grid gap-[var(--space-4)] sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((s) => (
            <Link key={s.slug} href={`/services/${s.slug}`} className="block">
              <Card interactive>
                <Badge tone="neutral">{t(`serviceCategory.${s.category}`)}</Badge>
                <h2 className="mt-[var(--space-2)] font-[var(--font-semibold)] text-[var(--text-primary)]">{s.name}</h2>
                <p className="mt-[var(--space-1)] text-[var(--text-sm)] text-[var(--text-secondary)]">{s.summary}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify + commit**

Run: `npm run lint` and `npm run build`. Expected: success.
```bash
git add src/app/services/page.tsx
git commit -m "feat: add services list page"
```

---

### Task 7: `/services/[slug]` detail page

**Files:**
- Create: `src/app/services/[slug]/page.tsx`

**Interfaces:**
- Consumes: `getService` and `slugAccent` from `@/lib/data`; `Button`, `Badge`, `EmptyState`, `IconChevronRight`.

- [ ] **Step 1: Create the page**

```tsx
"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { getService, slugAccent } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { IconChevronRight } from "@/components/ui/Icons";

export default function ServiceDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t } = useI18n();
  const service = getService(slug);
  if (!service) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState title={t("services.notFound")} action={<Link href="/services" className="text-sm text-[var(--accent-primary)] underline">{t("nav.services")}</Link>} />
      </div>
    );
  }
  const accent = slugAccent(service.slug);
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl p-6 text-white" style={{ backgroundColor: accent }}>
        <Badge tone="neutral">{t(`serviceCategory.${service.category}`)}</Badge>
        <h1 className="mt-2 font-[var(--font-display)] text-[var(--text-2xl)] font-[var(--font-medium)] tracking-tight">{service.name}</h1>
        <p className="mt-1 text-sm opacity-90">{service.summary}</p>
        <Link href={`/chat?q=${encodeURIComponent("How do I use the " + service.name + " service?")}`}>
          <Button className="mt-4 bg-white/90 !text-slate-900 hover:bg-white">
            {t("services.askThisService")}
            <IconChevronRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
      <div className="mt-6 space-y-6">
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.overview")}</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">{service.description}</p>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.whoCanUse")}</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
            {service.whoCanUse.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.howToAccess")}</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
            {service.howToAccess.map((item, i) => (<li key={i}>{item}</li>))}
          </ul>
        </section>
        <section className="rounded-[var(--radius-xl)] bg-[var(--surface-elevated)] p-[var(--space-6)]">
          <h2 className="font-[var(--font-semibold)] text-[var(--text-primary)]">{t("services.source")}</h2>
          <a href={service.source.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-sm text-[var(--accent-primary)] underline">
            {service.source.label}
          </a>
        </section>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify + commit**

Run: `npm run lint` and `npm run build`. Expected: success.
```bash
git add src/app/services/[slug]/page.tsx
git commit -m "feat: add services detail page"
```

---

### Task 8: `/faq` page

**Files:**
- Create: `src/app/faq/page.tsx`

**Interfaces:**
- Consumes: `getFaqItems()` from `@/lib/data`; `Input`, `Chips`, `EmptyState`, `Button`, `IconChevronRight`.

- [ ] **Step 1: Create the page**

```tsx
"use client";
import { useMemo, useState } from "react";
import { useI18n } from "@/lib/i18n/provider";
import { getFaqItems } from "@/lib/data";
import { Input } from "@/components/ui/Input";
import { Chips } from "@/components/ui/Chips";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { IconChevronRight } from "@/components/ui/Icons";

const CATEGORY_ALL = "all";
const categories = ["all", "crop-insurance", "pacs", "financial", "grievance", "legal"] as const;
type Filter = (typeof categories)[number];

export default function FaqPage() {
  const { t } = useI18n();
  const items = useMemo(() => getFaqItems(), []);
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<Filter>(CATEGORY_ALL);
  const [open, setOpen] = useState<Set<string>>(new Set());

  const filtered = items.filter((f) => {
    const okCat = cat === CATEGORY_ALL || f.category === cat;
    const q = query.trim().toLowerCase();
    const okQuery = !q || f.question.toLowerCase().includes(q) || f.answer.toLowerCase().includes(q);
    return okCat && okQuery;
  });

  function toggle(id: string) {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="mx-auto max-w-3xl px-[var(--space-4)] py-[var(--space-8)]">
      <h1 className="font-[var(--font-display)] text-[var(--text-3xl)] font-[var(--font-medium)] tracking-tight text-[var(--text-primary)]">{t("faq.title")}</h1>
      <p className="mt-[var(--space-1)] text-[var(--text-secondary)]">{t("faq.subtitle")}</p>
      <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("faq.searchPlaceholder")} className="mt-4 max-w-sm" />
      <div className="mt-4">
        <Chips<Filter>
          options={categories}
          value={cat}
          onChange={setCat}
          render={(c) => (c === "all" ? t("common.all") : t(`faqCategory.${c}`))}
        />
      </div>
      {filtered.length === 0 ? (
        <div className="mt-6"><EmptyState title={t("faq.empty")} /></div>
      ) : (
        <ul className="mt-6 space-y-3">
          {filtered.map((f) => {
            const isOpen = open.has(f.id);
            return (
              <li key={f.id} className="rounded-[var(--radius-xl)] border border-[var(--border-default)] bg-[var(--surface-overlay)]">
                <button
                  type="button"
                  aria-expanded={isOpen}
                  onClick={() => toggle(f.id)}
                  className="flex w-full items-center justify-between gap-2 px-[var(--space-4)] py-[var(--space-4)] text-left focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]"
                >
                  <span className="font-[var(--font-semibold)] text-[var(--text-primary)]">{f.question}</span>
                  <IconChevronRight className={`w-5 h-5 shrink-0 text-[var(--text-tertiary)] transition ${isOpen ? "rotate-90" : ""}`} />
                </button>
                {isOpen && (
                  <div className="px-[var(--space-4)] pb-[var(--space-4)]">
                    <p className="text-sm text-[var(--text-secondary)]">{f.answer}</p>
                    <a href={`/chat?q=${encodeURIComponent(f.question)}`} className="mt-3 inline-block">
                      <Button variant="secondary" className="!py-1 !px-3 text-xs">{t("faq.askInChat")}</Button>
                    </a>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify + commit**

Run: `npm run lint` and `npm run build`. Expected: success.
```bash
git add src/app/faq/page.tsx
git commit -m "feat: add faq page"
```

---

### Task 9: TopNav — add Legal, Services, FAQ

**Files:**
- Modify: `src/components/layout/TopNav.tsx`

**Interfaces:**
- Consumes: new icons `IconScale`, `IconBuilding`, `IconHelp`; nav keys added in Task 2.

- [ ] **Step 1: Update imports and LINKS**

Replace the import line to include the new icons:
```tsx
import { IconHome, IconChat, IconGrid, IconDoc, IconShield, IconScale, IconBuilding, IconHelp } from "@/components/ui/Icons";
```
Replace the `LINKS` array with the 8-item order read left-to-right as Home, Chat, Schemes, Services, Library, Legal, Grievance, FAQ:
```tsx
const LINKS = [
  { href: "/", key: "nav.home", icon: <IconHome className="w-5 h-5" /> },
  { href: "/chat", key: "nav.chat", icon: <IconChat className="w-5 h-5" /> },
  { href: "/schemes", key: "nav.schemes", icon: <IconGrid className="w-5 h-5" /> },
  { href: "/services", key: "nav.services", icon: <IconBuilding className="w-5 h-5" /> },
  { href: "/library", key: "nav.library", icon: <IconDoc className="w-5 h-5" /> },
  { href: "/legal", key: "nav.legal", icon: <IconScale className="w-5 h-5" /> },
  { href: "/grievance", key: "nav.grievance", icon: <IconShield className="w-5 h-5" /> },
  { href: "/faq", key: "nav.faq", icon: <IconHelp className="w-5 h-5" /> },
] as const;
```

- [ ] **Step 2: Lint + commit**

Run: `npm run lint`. Expected: no errors.
```bash
git add src/components/layout/TopNav.tsx
git commit -m "feat: add legal, services and faq to desktop nav"
```

---

### Task 10: MobileNav — 5 primary tiles + More sheet

**Files:**
- Create: `src/components/layout/MoreSheet.tsx`
- Modify: `src/components/layout/MobileNav.tsx`

**Interfaces:**
- Consumes: `IconMore`, `IconScale`, `IconBuilding`, `IconHelp`; nav keys from Task 2.

- [ ] **Step 1: Create `src/components/layout/MoreSheet.tsx`**

```tsx
"use client";
import Link from "next/link";
import { useEffect } from "react";
import { useI18n } from "@/lib/i18n/provider";
import { IconScale, IconBuilding, IconHelp } from "@/components/ui/Icons";

const MORE_LINKS = [
  { href: "/legal", key: "nav.legal", icon: <IconScale className="w-5 h-5" /> },
  { href: "/services", key: "nav.services", icon: <IconBuilding className="w-5 h-5" /> },
  { href: "/faq", key: "nav.faq", icon: <IconHelp className="w-5 h-5" /> },
] as const;

export function MoreSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useI18n();
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <>
      <div className="fixed inset-0 z-30 bg-black/50" aria-hidden="true" onClick={onClose} />
      <div
        role="dialog"
        aria-label="More"
        className="fixed inset-x-0 bottom-0 z-40 rounded-t-[var(--radius-xl)] border-t border-[var(--border-default)] bg-[var(--surface-base)] pb-[env(safe-area-inset-bottom)]"
      >
        <div className="grid grid-cols-3 gap-2 px-[var(--space-4)] py-[var(--space-4)] md:hidden">
          {MORE_LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              onClick={onClose}
              className="flex flex-col items-center gap-1 rounded-[var(--radius-lg)] py-[var(--space-3)] text-[var(--text-sm)] text-[var(--text-primary)] focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]"
            >
              {l.icon}
              <span>{t(l.key)}</span>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 2: Modify `src/components/layout/MobileNav.tsx`**

Replace the whole file with:
```tsx
"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n/provider";
import { MoreSheet } from "./MoreSheet";
import { IconHome, IconChat, IconGrid, IconDoc, IconShield, IconMore } from "@/components/ui/Icons";

const LINKS = [
  { href: "/", key: "nav.home", icon: <IconHome className="w-6 h-6" /> },
  { href: "/chat", key: "nav.chat", icon: <IconChat className="w-6 h-6" /> },
  { href: "/schemes", key: "nav.schemes", icon: <IconGrid className="w-6 h-6" /> },
  { href: "/library", key: "nav.library", icon: <IconDoc className="w-6 h-6" /> },
  { href: "/grievance", key: "nav.grievance", icon: <IconShield className="w-6 h-6" /> },
] as const;

export function MobileNav() {
  const { t } = useI18n();
  const pathname = usePathname();
  const [moreOpen, setMoreOpen] = useState(false);
  const active = (href: string) => (href === "/" ? pathname === "/" : pathname.startsWith(href));
  return (
    <>
      <nav
        aria-label="Primary mobile"
        className="fixed inset-x-0 bottom-0 z-20 border-t border-[var(--border-default)] bg-[var(--surface-base)] pb-[env(safe-area-inset-bottom)] md:hidden"
      >
        <div className="grid grid-cols-6">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              aria-current={active(l.href) ? "page" : undefined}
              className={`flex flex-col items-center gap-1 py-2 text-[11px] focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] ${
                active(l.href) ? "text-[var(--accent-primary)]" : "text-[var(--text-secondary)]"
              }`}
            >
              {l.icon}
              <span className="truncate">{t(l.key)}</span>
            </Link>
          ))}
          <button
            type="button"
            aria-label={t("nav.more")}
            aria-expanded={moreOpen}
            onClick={() => setMoreOpen(true)}
            className="flex flex-col items-center gap-1 py-2 text-[11px] text-[var(--text-secondary)] focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]"
          >
            <IconMore className="w-6 h-6" />
            <span className="truncate">{t("nav.more")}</span>
          </button>
        </div>
      </nav>
      <MoreSheet open={moreOpen} onClose={() => setMoreOpen(false)} />
    </>
  );
}
```

Note: the bottom `grid` is `grid-cols-6` (5 primary tiles + More).

- [ ] **Step 3: Add `nav.more` i18n key**

In `en`: `"nav.more": "More",`. In `hi`: `"nav.more": "और",`. (Optional mr/bn/ta label fallback to English is acceptable since `translate` falls back to `en`.)

- [ ] **Step 4: Verify + commit**

Run: `npm run lint` and `npm run build`. Expected: success.
```bash
git add src/components/layout/MoreSheet.tsx src/components/layout/MobileNav.tsx src/lib/i18n/dictionaries.ts
git commit -m "feat: add mobile more sheet with legal, services and faq"
```

---

### Task 11: Chat deep-link `?q=`

**Files:**
- Modify: `src/components/ChatWindow.tsx:48-55`

**Interfaces:**
- Consumes: `useSearchParams` already imported.
- Produces: prefill of `input` from `?q=` so FAQ/legal/services links work.

- [ ] **Step 1: Extend the existing effect**

Replace:
```tsx
  useEffect(() => {
    const scheme = sp?.get("scheme");
    if (scheme) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInput(factoryPrompt(scheme));
      setMsgs([]);
    }
  }, [sp]);
```
with:
```tsx
  useEffect(() => {
    const q = sp?.get("q");
    const scheme = sp?.get("scheme");
    if (q) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInput(q);
      setMsgs([]);
    } else if (scheme) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInput(factoryPrompt(scheme));
      setMsgs([]);
    }
  }, [sp]);
```

- [ ] **Step 2: Verify + commit**

Run: `npm run lint` and `npm run build`. Expected: success.
```bash
git add src/components/ChatWindow.tsx
git commit -m "feat: support ?q= chat deep-link"
```

---

### Task 12: Final verification

**Files:** none (verification only).

- [ ] **Step 1: Run the full suite**

Run: `npm run test -- --run`
Expected: PASS.

- [ ] **Step 2: Lint**

Run: `npm run lint`
Expected: no errors.

- [ ] **Step 3: Production build**

Run: `npm run build`
Expected: success — all 7 route groups compiled (existing 5 + `/legal`, `/services`, `/faq`, plus detail pages).

- [ ] **Step 4: Confirm route files**

Verify these exist:
- `src/app/legal/page.tsx`, `src/app/legal/[slug]/page.tsx`
- `src/app/services/page.tsx`, `src/app/services/[slug]/page.tsx`
- `src/app/faq/page.tsx`

---

## Self-Review

**Spec coverage:**
- `/legal` + detail → Tasks 4, 5. `/services` + detail → Tasks 6, 7. `/faq` → Task 8.
- Data modules + accent helper → Task 1. i18n → Tasks 2, 10. Icons → Task 3.
- TopNav → Task 9. Mobile More sheet → Task 10. Chat `?q=` → Task 11.
- All spec "Out of scope" items untouched.

**Placeholder scan:** No TBD/TODO. Full code blocks provided for every code step. Content seeded inline.

**Type consistency:**
- `slugAccent(slug)` used in Tasks 5, 7 (defined Task 1). `getLegalDocs/getLegalDoc`, `getServices/getService`, `getFaqItems` used consistently.
- `legal.*`, `legalCategory.*`, `services.*`, `serviceCategory.*`, `faq.*`, `faqCategory.*`, `nav.*` keys match Task 2 definitions.
- `IconScale/IconBuilding/IconHelp/IconMore` defined Task 3, used Tasks 9, 10.
- `MoreSheet` component named consistently (Task 10 Step 1/2).
- Mobile bottom grid uses `grid-cols-6` (5 primary tiles + More), consistent across Steps 1/2.
