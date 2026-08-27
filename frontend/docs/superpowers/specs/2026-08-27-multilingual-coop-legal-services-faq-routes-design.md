# Multilingual Cooperative — Legal, Services & FAQ Routes Design Spec

## Context and Goals

**Objective:** Add the three high-value routes that were missing relative to the Problem Statement (multilingual cooperative governance & legal assistance chatbot), using the existing UI conventions of the app.

**Problem Statement gaps addressed:**
- "Guidance on cooperative laws and by-laws" → `/legal` (previously only a chat domain + 2 library citations).
- "Information on Ministry of Cooperation schemes and services" → `/services` (PACS & Ministry services were only folded into scheme cards).
- Multilingual rural guidance, queries, and quick answers → `/faq`.

**Current State:**
- Next.js 16.3.3 + React 19 + Tailwind CSS v4, token-driven (Promptiq) design system.
- Existing idiom: list page + dynamic detail page driven by a static data module (`src/app/schemes/page.tsx` + `src/app/schemes/[slug]/page.tsx`, data in `src/lib/data/schemes.ts`, exports `getSchemes()`).
- Reusable components: `Card`, `Badge`, `Chips`, `Input`, `Button`, `EmptyState`, `Select`, `Alert`, `Stepper`, `Skeleton`, `Icons`.
- i18n via `useI18n()` (dictionary keys) with locales `en, hi, mr, bn, ta`.

**Target State:** Three new routes implemented to the same visual/functional bar as schemes/library; unblock all PS functional gaps except the ones deferred (auth/member, server-side voice, real grievance backend).

**Approach:** Mirror existing patterns exactly. No new dependencies.

---

## Routes & Pages

| Route | Type | Mirrors |
|---|---|---|
| `/legal` | List page | `src/app/schemes/page.tsx` |
| `/legal/[slug]` | Detail page | `src/app/schemes/[slug]/page.tsx` |
| `/services` | List page | `src/app/schemes/page.tsx` |
| `/services/[slug]` | Detail page | `src/app/schemes/[slug]/page.tsx` |
| `/faq` | Single page | `src/app/library/page.tsx` (search + chips) + accordion |

### `/legal` — Cooperative Laws & By-laws

**List page:** title, subtitle, search `Input`, category `Chips`, responsive card grid. Each card links to `/legal/[slug]`.

**Filters (Chips):** `all`, `act`, `bye-laws`, `provisions`.

**Detail page:** colored hero block (accent color resolved per slug, no hardcoded hex in components), `Badge` for category, title, summary, "Ask in chat" button linking to `/chat?q=<question>`. Sections in elevated cards: Overview, Key provisions, Applicability, By-law highlights, Official source (external link).

**Data module** `src/lib/data/legal.ts`:
```ts
export type LegalCategory = "act" | "bye-laws" | "provisions";
export interface LegalDoc {
  slug: string;
  title: string;        // full official name
  badge: string;        // short label e.g. "MSCS Act 2002"
  category: LegalCategory;
  overview: string;     // summary paragraph
  keyProvisions: string[];
  applicability: string[];
  byLaws: string[];
  source: { label: string; url: string };
}
export function getLegalDocs(): LegalDoc[];
export function getLegalDoc(slug: string): LegalDoc | undefined;
```

**Seed content:** MSCS Act 2002, Model PACS Bye-laws, Election of board of directors, Cooperative dispute resolution, Model bye-laws for PACS.

### `/services` — Ministry of Cooperation & PACS Services

**List page:** title, subtitle, search `Input`, category `Chips`, responsive card grid. Each card links to `/services/[slug]`.

**Filters (Chips):** `all`, `credit`, `storage`, `insurance`, `agro-inputs`, `subsidy`, `membership`.

**Detail page:** colored hero block, `Badge`, title, summary, "Ask in chat" button (`/chat?q=<question>`). Sections: Overview, Who can use, How to access, Official source.

**Data module** `src/lib/data/services.ts`:
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
export function getServices(): Service[];
export function getService(slug: string): Service | undefined;
```

**Seed content:** PACS membership, Short-term crop credit / KCC, Godown & storage, Agro-input supply, PMFBY enrolment, Cooperative subsidy support.

### `/faq` — Multilingual FAQ

**Single page:** title, subtitle, search `Input`, category `Chips`, list of expandable accordion cards (question + answer). Each item has an "Ask in chat" link (`/chat?q=<question>`).

**Filters (Chips):** `all`, `crop-insurance`, `pacs`, `financial`, `grievance`, `legal`.

**Data module** `src/lib/data/faq.ts`:
```ts
export type FaqCategory = "crop-insurance" | "pacs" | "financial" | "grievance" | "legal";
export interface FaqItem {
  id: string;
  category: FaqCategory;
  question: string;
  answer: string;
}
export function getFaqItems(): FaqItem[];
```

**Seed content:** ~12 items distributed across all 5 categories.

**Accordion behavior:** click a question toggles the answer; `aria-expanded` on the button; keyboard accessible (button element). Uses `useState` per-item expansion (a Set of open ids in the page).

---

## Data & Reusable Helpers

Add `legal.ts`, `services.ts`, `faq.ts` under `src/lib/data/` and export them from `src/lib/data/index.ts`:
```ts
export * from "./legal";
export * from "./services";
export * from "./faq";
```

Reuse `schemeColors()` under a generalized name or add a parallel `legalColors()`/`serviceColors()` in each respective module — keep the page components free of raw hex. (Prefer reusing `schemeColors` semantics; introduce a shared `slugAccent(slug, palette)` helper in `src/lib/data/index.ts` if the three modules share it, otherwise duplicate the 15-line helper per module to avoid premature abstraction.)

---

## i18n

Add to `src/lib/i18n/dictionaries.ts`:
- `nav.legal`, `nav.services`, `nav.faq` — all 5 locales.
- Page keys — full `en` + `hi`, nav-only coverage for `mr/bn/ta` (matching existing per-locale coverage).

Keys (page strings): `legal.*` (title, subtitle, searchPlaceholder, empty, notFound, overview, keyProvisions, applicability, byLaws, source, askThisLaw), `services.*` (title, subtitle, searchPlaceholder, empty, notFound, overview, whoCanUse, howToAccess, source, askThisService), `faq.*` (title, subtitle, searchPlaceholder, empty, askInChat), and category label keys `legalCategory.*`, `serviceCategory.*`, reused `faqCategory.*`.

Content strings (English) live in the data modules — same behavior as existing schemes data (labels translated, content English). This keeps scope bounded; full 5-language content is out of scope for this pass and documented as a known limitation.

---

## Navigation

### TopNav (`src/components/layout/TopNav.tsx`)
Extend `LINKS` to 8 items, in order: Home, Chat, Schemes, Services, Library, Legal, Grievance, FAQ. Add icons to `src/components/ui/Icons.tsx`: `IconScale` (legal, `/legal`), `IconBuilding` (services, `/services`), `IconHelp` (faq, `/faq`).

### MobileNav (`src/components/layout/MobileNav.tsx`)
Keep 5 primary tiles (Home, Chat, Schemes, Library, Grievance) + a **More** tile (new `IconMore`) that opens a bottom sheet listing Legal, Services, FAQ. The sheet is a small client component with `aria`-labelled button, closes on item tap / backdrop tap / Escape. The bottom bar remains `grid-cols-5`.

---

## Chat Deep-link Enhancement

In `src/components/ChatWindow.tsx`, also read `sp.get("q")` (in addition to the existing `sp.get("scheme")`). When present, prefill `input` with the query and clear messages, so FAQ/legal/services "Ask in chat" links work with a full question. The `scheme` handling remains unchanged.

---

## Error & Empty States

- List pages: use `EmptyState` when a search/filter yields no results (mirror `schemes.empty` / `library.empty`).
- Detail pages: use `EmptyState` + back link when slug not found (mirror `detail.notFound`).
- FAQ: `EmptyState` when no items match search/filter.

---

## Testing

Add unit tests per data module, mirroring `src/lib/data/data.test.ts`:
- `getLegalDocs()` returns ≥1 doc and slugs are unique.
- `getLegalDoc(slug)` resolves known slug, `undefined` for unknown.
- Same invariants for `getServices()`/`getService()` and `getFaqItems()`.

Verification commands:
```bash
npm run test
npm run lint
npm run build
```

---

## Accessibility & Design Rules

Follow the existing Promptiq spec: token-based colors only (`var(--*)`), visible `focus-visible:ring-2 ring-[var(--border-focus)]` on all interactive elements, semantic HTML, `aria-expanded` on accordion/more-sheet triggers, `aria-current` on nav, minimum 44x44px touch targets, `prefers-reduced-motion` respected (no essential info via motion).

---

## Out of Scope (deferred)

- Auth / member profile route (`/member`, `/login`) — no auth backend exists.
- Server-side ASR/TTS, IVR/phone channel.
- Backend persistence for grievances.
- Full 5-language content translation (content stays English, labels translated).
- PWA install / push notifications.

---

## Known Limitation

The app's multilingual UI currently fully translates only `en` and `hi`; `mr`, `bn`, `ta` have nav labels only. This spec carries that same coverage. The chat API accepts only `"en" | "hi"`.

---

## Spec Self-Review

**Placeholder scan:** No TBD/TODO. All seeds enumerated.
**Internal consistency:** Data shapes match pages; nav order matches route set; `q` param handled alongside `scheme`.
**Scope check:** Focused single implementation cycle (5 pages, 3 data modules, i18n, nav, chat tweak). Large but cohesive; one plan with clear phases.
**Ambiguity check:** Category chip values and English-content behavior explicitly stated; accordion interaction defined.

## Approval

**Status:** Approved by user.
**Next Step:** Invoke writing-plans skill to produce the implementation plan.
