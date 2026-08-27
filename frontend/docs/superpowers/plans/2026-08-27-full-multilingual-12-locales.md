# Full Multilingual (12 Locales) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the app fully language-switchable across 12 locales — every UI string and the whole data-content engine render in the active language.

**Architecture:** Extend `LOCALES` to 12; add `src/lib/data/i18n.ts` with `localize`/`localizeList` (falling back to `en`); refactor all data modules so user-facing fields are stored per-locale and accessors take `(locale)`; update every page to pass `useI18n().locale`; widen chat `language` to `Locale`; load script fonts; fully translate the chrome dictionary for all 12 locales. Content translations fill in over Phases 2/3.

**Tech Stack:** Next.js 16 App Router (client components), React 19, TypeScript, Tailwind v4 tokens, Vitest.

## Global Constraints

- **Tokens only** (`var(--*)`, no raw hex in TSX).
- **Locale set (verbatim):** `["en","hi","mr","bn","ta","te","kn","pa","gu","or","ml","ur"]`.
- **Fallback:** missing locale resolves to `en` (via `localize`/`localizeList`/`translate`).
- **Data-layer accessor signature (verbatim):** `getSchemes(locale: Locale)`, `getScheme(locale, slug)`, `getLegalDocs(locale)`, `getLegalDoc(locale, slug)`, `getServices(locale)`, `getService(locale, slug)`, `getFaqItems(locale)`, `getLibraryDocs(locale)`.
- **Chat:** `sendChat`/`ChatResponse` `language` is `Locale`.
- **No new dependencies.** Vitest (`import { test, expect } from "vitest"`).
- **Out of scope:** translating backend chat responses (documented limitation); translation APIs.

---

# PHASE 1 — Foundation & Chrome

## Task 1: Extend locale set + language names

**Files:**
- Modify: `src/lib/i18n/i18n.ts`
- Modify: `src/components/layout/LanguageSwitcher.tsx`
- Modify: `src/lib/i18n/i18n.test.ts`

**Interfaces:**
- Produces: `LOCALES` of 12; `Locale` type includes all 12; `NAMES` in `LanguageSwitcher` covers all 12.

- [ ] **Step 1: Modify `src/lib/i18n/i18n.ts`**

Replace:
```ts
export const LOCALES = ["en", "hi", "mr", "bn", "ta"] as const;
export type Locale = (typeof LOCALES)[number];
```
with:
```ts
export const LOCALES = [
  "en", "hi", "mr", "bn", "ta", "te", "kn", "pa", "gu", "or", "ml", "ur",
] as const;
export type Locale = (typeof LOCALES)[number];
```

- [ ] **Step 2: Modify `src/components/layout/LanguageSwitcher.tsx`**

Replace the `NAMES` record:
```tsx
const NAMES: Record<Locale, string> = {
  en: "English", hi: "हिंदी", mr: "मराठी", bn: "বাংলা", ta: "தமிழ்",
};
```
with:
```tsx
const NAMES: Record<Locale, string> = {
  en: "English", hi: "हिंदी", mr: "मराठी", bn: "বাংলা", ta: "தமிழ்",
  te: "తెలుగు", kn: "ಕನ್ನಡ", pa: "ਪੰਜਾਬੀ", gu: "ગુજરાતી",
  or: "ଓଡ଼ିଆ", ml: "മലയാളം", ur: "اردو",
};
```

- [ ] **Step 3: Modify `src/lib/i18n/i18n.test.ts`**

Replace the first test (and the `fallback` test expectation for the new locales is unaffected):
```ts
test("exports 5 supported locales", () => {
  expect(LOCALES).toEqual(["en", "hi", "mr", "bn", "ta"]);
});
```
with:
```ts
test("exports 12 supported locales", () => {
  expect(LOCALES).toEqual(["en", "hi", "mr", "bn", "ta", "te", "kn", "pa", "gu", "or", "ml", "ur"]);
});
```

- [ ] **Step 4: Verify + commit**

Run: `npm run test` and `npm run lint` from `A:\MSU\frontend`. Expected: PASS / clean.
```bash
git -C A:\MSU add frontend/src/lib/i18n/i18n.ts frontend/src/components/layout/LanguageSwitcher.tsx frontend/src/lib/i18n/i18n.test.ts
git -C A:\MSU commit -m "feat: extend locales to 12 and update language switcher"
```

---

## Task 2: Locale-aware data helper

**Files:**
- Create: `src/lib/data/i18n.ts`
- Modify: `src/lib/data/index.ts`
- Test: `src/lib/data/i18n.test.ts`

**Interfaces:**
- Produces: `I18nText`, `I18nList`, `localize(value, locale): string`, `localizeList(value, locale): string[]`. All later data tasks use these.

- [ ] **Step 1: Write failing test `src/lib/data/i18n.test.ts`**

```ts
import { test, expect } from "vitest";
import { localize, localizeList, type I18nText, type I18nList } from "./i18n";

test("localize returns the requested locale", () => {
  const v: I18nText = { en: "Apple", hi: "सेब" };
  expect(localize(v, "hi")).toBe("सेब");
});

test("localize falls back to en when locale missing", () => {
  const v: I18nText = { en: "Apple" };
  expect(localize(v, "te")).toBe("Apple");
});

test("localizeList returns requested locale array", () => {
  const v: I18nList = { en: ["a"], hi: ["ख"] };
  expect(localizeList(v, "hi")).toEqual(["ख"]);
});

test("localizeList falls back to en when locale missing", () => {
  const v: I18nList = { en: ["a"] };
  expect(localizeList(v, "kn")).toEqual(["a"]);
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm run test` → FAIL (`./i18n` not found).

- [ ] **Step 3: Create `src/lib/data/i18n.ts`**

```ts
import type { Locale } from "@/lib/i18n/i18n";

export type I18nText = Partial<Record<Locale, string>>;
export type I18nList = Partial<Record<Locale, string[]>>;

export function localize(value: I18nText, locale: Locale): string {
  return value[locale] ?? value.en ?? "";
}
export function localizeList(value: I18nList, locale: Locale): string[] {
  return value[locale] ?? value.en ?? [];
}
```

- [ ] **Step 4: Modify `src/lib/data/index.ts`**

Add at the end:
```ts
export * from "./i18n";
```

- [ ] **Step 5: Run to verify it passes**

Run: `npm run test` → PASS.

- [ ] **Step 6: Commit**

```bash
git -C A:\MSU add frontend/src/lib/data/i18n.ts frontend/src/lib/data/index.ts frontend/src/lib/data/i18n.test.ts
git -C A:\MSU commit -m "feat: add locale-aware data helper"
```

---

## Task 3: Refactor schemes to per-locale

**Files:**
- Modify: `src/lib/data/schemes.ts`
- Modify: `src/lib/data/data.test.ts`
- Test: `src/lib/data/schemes.test.ts` (new)

**Interfaces:**
- Consumes: `I18nText`, `I18nList`, `localize`, `localizeList` (Task 2); `Locale` (Task 1).
- Produces: `Scheme` with `I18nText`/`I18nList` fields; `getSchemes(locale)`, `getScheme(locale, slug)`.

- [ ] **Step 1: Replace `src/lib/data/schemes.ts`** with:

```ts
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
```

- [ ] **Step 2: Create `src/lib/data/schemes.test.ts`**

```ts
import { test, expect } from "vitest";
import { getSchemes, getScheme } from "./schemes";

test("getSchemes returns localized data for a locale", () => {
  const all = getSchemes("en");
  expect(all.length).toBeGreaterThan(0);
  expect(all[0]).toHaveProperty("slug");
  expect(all[0].name).toBeTypeOf("string");
  expect(getScheme("en", "pmfby")).toBeDefined();
  expect(getSchemes("te")[0].name).toBe(getSchemes("en")[0].name);
  expect(getScheme("en", "nope")).toBeUndefined();
});
```

- [ ] **Step 3: Update `src/lib/data/data.test.ts`**

Change the schemes section to the new signature:
```ts
import { getSchemes, getScheme } from "./schemes";
...
  const all = getSchemes("en");
  ...
  expect(getScheme("en", "pmfby")).toBeDefined();
  expect(getScheme("en", "does-not-exist")).toBeUndefined();
```
(Keep the library/grievance assertions unchanged for now; library is updated in Task 7 — the task-referencing of `getLibraryDocs()` must match that task.)

- [ ] **Step 4: Fix any callers in this repo that break**

The existing schemes pages call `getSchemes()`/`getScheme(slug)`. They are updated in **Task 8**. Until then, `npm run build`/`test` may fail on typecheck. To keep this task self-contained, also update the two scheme-page callers minimally (pass `"en"`):
- `src/app/page.tsx`: `getSchemes()` → `getSchemes("en")`.
- `src/app/schemes/page.tsx`: `getSchemes()` → `getSchemes("en")`.
- `src/app/schemes/[slug]/page.tsx`: `getScheme(slug)` → `getScheme("en", slug)`.
(Task 8 later makes them locale-aware; this keeps the tree compiling now.)

- [ ] **Step 5: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build` from `A:\MSU\frontend`. Expected: PASS / clean / success.
```bash
git -C A:\MSU add frontend/src/lib/data/schemes.ts frontend/src/lib/data/schemes.test.ts frontend/src/lib/data/data.test.ts frontend/src/app/page.tsx frontend/src/app/schemes/page.tsx frontend/src/app/schemes/[slug]/page.tsx
git -C A:\MSU commit -m "feat: localize schemes data module"
```

---

## Task 4: Refactor legal to per-locale

**Files:**
- Modify: `src/lib/data/legal.ts`
- Modify: `src/lib/data/legal.test.ts`

**Interfaces:**
- Consumes: `I18nText`/`I18nList`/`localize`/`localizeList`; `Locales`.
- Produces: `LegalDoc` localized; `getLegalDocs(locale)`, `getLegalDoc(locale, slug)`.

- [ ] **Step 1: Replace `src/lib/data/legal.ts`** — same transformation as schemes. Add `import type { Locale } ... ` and `import { localize, localizeList, type I18nList, type I18nText }`. Change `title`, `badge`, `overview`, `source.label` to `I18nText`; `keyProvisions`, `applicability`, `byLaws` to `I18nList`; wrap each existing English value as `{ en: ... }`. `LegalDoc.source` becomes `{ label: I18nText; url: string }`. Replace `getLegalDocs()`/`getLegalDoc(slug)` with `getLegalDocs(locale)`/`getLegalDoc(locale, slug)` using `localize`/`localizeList` (mirror Task 3's accessor pattern).

The `legalDocs` array keeps all 5 existing documents (mscs-act-2002, model-pacs-bye-laws, board-election-rules, cooperative-disputes, pac-model-bye-laws-moc). Every English string is moved verbatim into an `en` value. `source.url` values (`https://www.moc.gov.in`) and `slug`, `category` stay as-is. Apply the exact accessor shape:
```ts
export function getLegalDocs(locale: Locale): LegalDoc[] {
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
export function getLegalDoc(locale: Locale, slug: string): LegalDoc | undefined {
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
```

- [ ] **Step 2: Update `src/lib/data/legal.test.ts`**

Change every `getLegalDocs()` → `getLegalDocs("en")` and `getLegalDoc("nope")` → `getLegalDoc("en", "nope")` (and the `mscs-act-2002` call accordingly). Add `expect(getLegalDocs("en")[0].title).toBeTypeOf("string");`.

- [ ] **Step 3: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build`. Expected: PASS / clean / success.
```bash
git -C A:\MSU add frontend/src/lib/data/legal.ts frontend/src/lib/data/legal.test.ts
git -C A:\MSU commit -m "feat: localize legal data module"
```

---

## Task 5: Refactor services to per-locale

**Files:**
- Modify: `src/lib/data/services.ts`
- Modify: `src/lib/data/services.test.ts`

**Interfaces:**
- Consumes: Task 2 helpers; Locale.
- Produces: `Service` localized; `getServices(locale)`, `getService(locale, slug)`.

- [ ] **Step 1: Replace `src/lib/data/services.ts`** — same transformation: `name`, `summary`, `description`, `source.label` → `I18nText` (`source: { label: I18nText; url: string }`); `whoCanUse`, `howToAccess` → `I18nList`. Wrap every existing English value as `{ en: ... }`. Services list keeps all 6 (pacs-membership, short-term-crop-credit, godown-storage, agro-input-supply, pmfby-enrolment, cooperative-subsidy). Accessors:
```ts
export function getServices(locale: Locale): Service[] {
  return services.map((s) => ({ ...localizeService(s, locale) }));
}
export function getService(locale: Locale, slug: string): Service | undefined {
  const found = services.find((s) => s.slug === slug);
  if (!found) return undefined;
  return localizeService(found, locale);
}
```
where `localizeService` returns `{ slug, category, name, summary, description, whoCanUse[], howToAccess[], source:{label,url} }` using localize/localizeList.

- [ ] **Step 2: Update `src/lib/data/services.test.ts`** to new signatures (`getServices("en")`, `getService("en", "pacs-membership")`, `getService("en","nope")`), plus `expect(getServices("en")[0].name).toBeTypeOf("string");`.

- [ ] **Step 3: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build`. Expected: PASS / clean / success.
```bash
git -C A:\MSU add frontend/src/lib/data/services.ts frontend/src/lib/data/services.test.ts
git -C A:\MSU commit -m "feat: localize services data module"
```

---

## Task 6: Refactor faq to per-locale

**Files:**
- Modify: `src/lib/data/faq.ts`
- Modify: `src/lib/data/faq.test.ts`

**Interfaces:**
- Consumes: Task 2 helpers; Locale.
- Produces: `FaqItem` localized; `getFaqItems(locale)`.

- [ ] **Step 1: Replace `src/lib/data/faq.ts`** — `question` and `answer` → `I18nText`; wrap all existing English values as `{ en: ... }` for items f1..f11. `id`, `category` stay. Accessor:
```ts
export function getFaqItems(locale: Locale): FaqItem[] {
  return faqItems.map((f) => ({
    id: f.id,
    category: f.category,
    question: localize(f.question, locale),
    answer: localize(f.answer, locale),
  }));
}
```

- [ ] **Step 2: Update `src/lib/data/faq.test.ts`** — `getFaqItems()` → `getFaqItems("en")`, plus `expect(all[0].question).toBeTypeOf("string");`.

- [ ] **Step 3: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build`. Expected: PASS / clean / success.
```bash
git -C A:\MSU add frontend/src/lib/data/faq.ts frontend/src/lib/data/faq.test.ts
git -C A:\MSU commit -m "feat: localize faq data module"
```

---

## Task 7: Refactor library to per-locale

**Files:**
- Modify: `src/lib/data/library.ts`
- Modify: `src/lib/data/data.test.ts`

**Interfaces:**
- Consumes: Task 2 helpers; Locale.
- Produces: `LibraryDoc` localized (`title`/`source` → `I18nText`); `getLibraryDocs(locale)`.

- [ ] **Step 1: Replace `src/lib/data/library.ts`** — `title`, `source` → `I18nText`; wrap existing values (`source` e.g. "Ministry of Cooperation", `title` etc.) as `{ en: ... }`. `id`, `page`, `url`, `domain`, `publishedAt` stay. Accessor:
```ts
export function getLibraryDocs(locale: Locale): LibraryDoc[] {
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
```

- [ ] **Step 2: Update `src/lib/data/data.test.ts`** — its library section: `getLibraryDocs()` → `getLibraryDocs("en")`.

- [ ] **Step 3: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build`. Expected: PASS / clean / success.
```bash
git -C A:\MSU add frontend/src/lib/data/library.ts frontend/src/lib/data/data.test.ts
git -C A:\MSU commit -m "feat: localize library data module"
```

---

## Task 8: Make all callers locale-aware

**Files:**
- Modify: `src/app/page.tsx`, `src/app/schemes/page.tsx`, `src/app/schemes/[slug]/page.tsx`, `src/app/library/page.tsx`, `src/app/legal/page.tsx`, `src/app/legal/[slug]/page.tsx`, `src/app/services/page.tsx`, `src/app/services/[slug]/page.tsx`, `src/app/faq/page.tsx`

**Interfaces:**
- Consumes: `useI18n()` (has `.locale`); the locale-aware accessors from Tasks 3-7.

- [ ] **Step 1: Each page — pass the active locale**

For each page, get `const { t, locale } = useI18n();` (add `locale`), then:
- home `page.tsx`: `getSchemes()` → `getSchemes(locale)`
- schemes `page.tsx`: `getSchemes()` → `getSchemes(locale)`
- schemes `[slug]`: `getScheme(slug)` → `getScheme(locale, slug)`
- library `page.tsx`: `getLibraryDocs()` → `getLibraryDocs(locale)`
- legal `page.tsx`: `getLegalDocs()` → `getLegalDocs(locale)`
- legal `[slug]`: `getLegalDoc(slug)` → `getLegalDoc(locale, slug)`
- services `page.tsx`: `getServices()` → `getServices(locale)`
- services `[slug]`: `getService(slug)` → `getService(locale, slug)`
- faq `page.tsx`: `getFaqItems()` → `getFaqItems(locale)`

(For pages already destructuring `const { t } = useI18n();`, change to `const { t, locale } = useI18n();`.)

- [ ] **Step 2: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build`. Expected: PASS / clean / success.
```bash
git -C A:\MSU add frontend/src/app/page.tsx frontend/src/app/schemes/page.tsx frontend/src/app/schemes/[slug]/page.tsx frontend/src/app/library/page.tsx frontend/src/app/legal/page.tsx frontend/src/app/legal/[slug]/page.tsx frontend/src/app/services/page.tsx frontend/src/app/services/[slug]/page.tsx frontend/src/app/faq/page.tsx
git -C A:\MSU commit -m "feat: pass active locale to data accessors"
```

---

## Task 9: Widen chat language to Locale

**Files:**
- Modify: `src/lib/api.ts`
- Modify: `src/components/ChatWindow.tsx`
- Verify: `src/lib/speech.ts` (no edit expected)

**Interfaces:**
- Consumes: `Locale` (Task 1); `NEXT_PUBLIC_API_BASE` unchanged.

- [ ] **Step 1: `src/lib/api.ts`**

Replace `language: "en" | "hi"` with `language: Locale` (import `Locale` from `@/lib/i18n/i18n`): both in `ChatResponse` and the `sendChat` payload type.

- [ ] **Step 2: `src/components/ChatWindow.tsx`**

Replace `const lang: "en" | "hi" = locale === "hi" ? "hi" : "en";` with `const lang: Locale = locale;` (import `Locale` type). `fallback(lang)` and `speak`/`listen` calls then pass the locale (speech already maps `*-IN`).

- [ ] **Step 3: `src/lib/speech.ts`** — verify (no code change expected) the `listen` mapping: currently `locale === "hi" || locale === "mr" || ... ? locale + "-IN" : "en-IN"`. Change it to accept all `*-IN`: replace the ternary body so any non-`en` locale becomes `locale + "-IN"` and `en` → `"en-IN"`. (If it already lists the old locales, extend the condition to the full set, or simplify to: `rec.lang = locale === "en" ? "en-IN" : locale + "-IN"`.)

- [ ] **Step 4: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build`. Expected: PASS / clean / success.
```bash
git -C A:\MSU add frontend/src/lib/api.ts frontend/src/components/ChatWindow.tsx frontend/src/lib/speech.ts
git -C A:\MSU commit -m "feat: widen chat speech language to full locale set"
```

---

## Task 10: Script-aware fonts

**Files:**
- Modify: `src/app/layout.tsx`

**Interfaces:**
- Consumes: `useI18n()` `.locale` is NOT available in the server `layout.tsx`; the font must be applied via a client wrapper or a script class derived from the locale. Simplest: apply the `--font-script` CSS var on `:root` per locale in `globals.css` and let fallback handle it; load the Noto fonts in `layout.tsx`.

- [ ] **Step 1: `src/app/layout.tsx` — load Noto fonts**

Add imports:
```ts
import { Noto_Serif_Bengali, Noto_Serif_Tamil, Noto_Serif_Telugu, Noto_Serif_Kannada, Noto_Serif_Gurmukhi, Noto_Serif_Gujarati, Noto_Serif_Odia, Noto_Serif_Malayalam } from "next/font/google";
```
Instantiate each with `{ variable: "--font-<script>", subsets: [...], weight: ["400","500","600","700"] }` (subsets per font: latin + the script's subset; e.g., Bengali: `["bengali","latin"]`), and add each `.variable` class to the `<html>` className alongside the existing ones.

- [ ] **Step 2: `src/app/globals.css` — map locale to script font**

Add rules so the display font follows the script, e.g.:
```css
:root, [lang="hi"], [lang="mr"] { --font-script: var(--font-devanagari); }
html[data-locale="bn"] { --font-script: var(--font-bengali); }
html[data-locale="ta"] { --font-script: var(--font-tamil); }
html[data-locale="te"] { --font-script: var(--font-telugu); }
html[data-locale="kn"] { --font-script: var(--font-kannada); }
html[data-locale="pa"] { --font-script: var(--font-gurmukhi); }
html[data-locale="gu"] { --font-script: var(--font-gujarati); }
html[data-locale="or"] { --font-script: var(--font-odia); }
html[data-locale="ml"] { --font-script: var(--font-malayalam); }
```
Add `else { --font-script: var(--font-geist-sans); }` default. Set `data-locale` on `<html>` via a tiny client effect in the language provider (set `document.documentElement.setAttribute("data-locale", locale)` on locale change). Replace `font-[var(--font-display)]` usages with `font-[var(--font-script)]` (or alias `--font-display` to `var(--font-script)` at the `:root` to avoid touching every page).

- [ ] **Step 3: Verify + commit**

Run: `npm run build` (Expected: success), `npm run lint`. Commit:
```bash
git -C A:\MSU add frontend/src/app/layout.tsx frontend/src/app/globals.css frontend/src/lib/i18n/provider.tsx
git -C A:\MSU commit -m "feat: load script fonts and apply per-locale display font"
```

---

## Task 11: Chrome dictionary — upgrade mr/bn/ta to full

**Files:**
- Modify: `src/lib/i18n/dictionaries.ts`

**Interfaces:**
- Consumes: the `en` key set (the source). Produces: `mr`, `bn`, `ta` dictionaries with EVERY key `en` has.

- [ ] **Step 1: Translate the full `en` key set into `mr`, `bn`, `ta`**

For each of the three locales, add every key that currently exists in `en` (nav.*, common.*, evidence.*, abstained.title, domain.*, landing.*, category.*, schemes.*, detail.*, library.*, grievance.*, status.*, chat.*, legal.*, legalCategory.*, services.*, serviceCategory.*, faq.*, faqCategory.*, legal.count, services.count, nav.more) with an appropriate translation. These locales currently have only `nav.*` + `all`/`globe`; fill the remainder. The `translate` fallback stays but is no longer hit for these locales.

- [ ] **Step 2: Verify + commit**

Run: `npm run test`, `npm run lint`. Commit:
```bash
git -C A:\MSU add frontend/src/lib/i18n/dictionaries.ts
git -C A:\MSU commit -m "feat: fully translate mr, bn and ta dictionaries"
```

---

## Task 12: Chrome dictionary — author te/kn/pa/gu/or/ml/ur

**Files:**
- Modify: `src/lib/i18n/dictionaries.ts`

**Interfaces:**
- Consumes: `en` key set. Produces: `te`, `kn`, `pa`, `gu`, `or`, `ml`, `ur` dictionaries with every `en` key fully translated.

- [ ] **Step 1: Add 7 new locale dictionaries**

Add `const te: Record<string,string> = { ... };` (and `kn`, `pa`, `gu`, `or`, `ml`, `ur`) each containing the full translated `en` key set. Add them all to the export:
```ts
export const dict: Record<Locale, Record<string, string>> = { en, hi, mr, bn, ta, te, kn, pa, gu, or, ml, ur };
```

- [ ] **Step 2: Verify + commit**

Run: `npm run test`, `npm run lint`. Commit:
```bash
git -C A:\MSU add frontend/src/lib/i18n/dictionaries.ts
git -C A:\MSU commit -m "feat: add telugu, kannada, punjabi, gujarati, odia, malayalam and urdu dictionaries"
```

---

## Task 13: Dictionary parity test

**Files:**
- Create: `src/lib/i18n/dictionaries.test.ts`

**Interfaces:**
- Consumes: `dict`, `LOCALES`.

- [ ] **Step 1: Create `src/lib/i18n/dictionaries.test.ts`**

```ts
import { test, expect } from "vitest";
import { dict, translate } from "./dictionaries";
import { LOCALES } from "./i18n";

test("every locale defines every key that en defines", () => {
  const enKeys = Object.keys(dict.en);
  for (const loc of LOCALES) {
    for (const k of enKeys) {
      expect(dict[loc][k], `${loc}.${k}`).toBeDefined();
    }
  }
});

test("new locales translate nav.home and a page key", () => {
  // spot-check non-empty translations for all new locales
  for (const loc of ["mr", "bn", "ta", "te", "kn", "pa", "gu", "or", "ml", "ur"]) {
    expect(translate(loc, "nav.home").length).toBeGreaterThan(0);
  }
});
```

- [ ] **Step 2: Verify + commit**

Run: `npm run test` (Expected: PASS), `npm run lint`. Commit:
```bash
git -C A:\MSU add frontend/src/lib/i18n/dictionaries.test.ts
git -C A:\MSU commit -m "test: enforce dictionary parity across all locales"
```

---

# PHASE 2 — Content batch 1 (schemes, services, library)

## Task 14: Translate schemes content into 12 locales

**Files:**
- Modify: `src/lib/data/schemes.ts`

**Interfaces:**
- Consumes: `I18nText`/`I18nList` structure (en populated). Produces: `Scheme` per-locale content fully populated for all 12 locales (no `en` fallback).

- [ ] **Step 1: Fill every locale for all 6 schemes**

For each of the 6 schemes, populate `name`, `benefit`, `overview`, `eligibility`, `benefits`, `howToApply`, `documents` with translations in `hi, mr, bn, ta, te, kn, pa, gu, or, ml, ur` (in addition to `en`). Read the existing English text in this file as the source reference; translate faithfully. Keep `slug`/`category`/`schemeColors` unchanged.

- [ ] **Step 2: Verify + commit**

Run: `npm run test`, `npm run lint`, `npm run build`. Commit:
```bash
git -C A:\MSU add frontend/src/lib/data/schemes.ts
git -C A:\MSU commit -m "feat: translate schemes content into 12 languages"
```

## Task 15: Translate services content into 12 locales

**Files:**
- Modify: `src/lib/data/services.ts`

- [ ] **Step 1:** populate all 6 services' `name`, `summary`, `description`, `whoCanUse`, `howToAccess`, `source.label` for all 12 locales. [`slug`/`category`/`source.url` unchanged.]
- [ ] **Step 2:** `npm run test`, `npm run lint`, `npm run build`; commit `feat: translate services content into 12 languages`.

## Task 16: Translate library content into 12 locales

**Files:**
- Modify: `src/lib/data/library.ts` (and any dictionary `domain` labels as needed)

- [ ] **Step 1:** populate `title` and `source` for all 5 docs across all 12 locales. [`id`/`page`/`url`/`domain`/`publishedAt` unchanged.]
- [ ] **Step 2:** `npm run test`, `npm run lint`, `npm run build`; commit `feat: translate library content into 12 languages`.

---

# PHASE 3 — Content batch 2 (legal, faq)

## Task 17: Translate legal content into 12 locales

**Files:**
- Modify: `src/lib/data/legal.ts`

- [ ] **Step 1:** populate all 5 legal docs' `title`, `badge`, `overview`, `keyProvisions`, `applicability`, `byLaws`, `source.label` for all 12 locales. (Longest translation volume; the existing English text is the source.) [`slug`/`category`/`source.url` unchanged.]
- [ ] **Step 2:** `npm run test`, `npm run lint`, `npm run build`; commit `feat: translate legal content into 12 languages`.

## Task 18: Translate faq content into 12 locales

**Files:**
- Modify: `src/lib/data/faq.ts`

- [ ] **Step 1:** populate all 11 FAQ items' `question` and `answer` for all 12 locales. [`id`/`category` unchanged.]
- [ ] **Step 2:** `npm run test`, `npm run lint`, `npm run build`; commit `feat: translate faq content into 12 languages`.

---

# Final verification (all phases)

- [ ] Run `npm run test` (Expected: PASS, includes parity + localized-accessor tests), `npm run lint` (Expected: 0 errors; only the known ChatWindow unused-disable warning), `npm run build` (Expected: success).
- [ ] Confirm routes still all present: `/`, `/chat`, `/faq`, `/grievance`, `/grievance/status`, `/legal`, `/legal/[slug]`, `/library`, `/schemes`, `/schemes/[slug]`, `/services`, `/services/[slug]`.

---

## Self-Review

**Spec coverage:** Phase 1 → Tasks 1-13 (locales, helper, all 5 data modules, callers, chat, fonts, chrome translation, parity). Phase 2 → Tasks 14-16. Phase 3 → Tasks 17-18. Chat limitation documented (Task 9).

**Placeholder scan:** Structural tasks carry full code. Translation-authoring tasks (11, 12, 14-18) specify the exact source (`en`/existing English text in the repo), target locales/structure, and verification — no TBD/TODO. Their literal translated strings are content authored during execution from the concrete `en` source in the repo.

**Type consistency:** `I18nText`/`I18nList`/`localize`/`localizeList` defined once (Task 2) and reused (Tasks 3-7). `getSchemes(locale)`/`getScheme(locale, slug)`/`getLegalDocs(locale)`/`getLegalDoc(locale, slug)`/`getServices(locale)`/`getService(locale, slug)`/`getFaqItems(locale)`/`getLibraryDocs(locale)` signatures consistent across Tasks 3-8. `Locale` 12-wide consistent (Task 1). `LanguageSwitcher.NAMES` covers 12. API `language: Locale` consistent.
