# Full Multilingual Support — 12 Locales Design Spec

## Context and Goals

**Objective:** Make the app fully multilingual — every UI string AND every piece of data content renders in the active language — across 12 Indian languages.

**Problem being fixed:** Currently only `en` + `hi` are fully translated. `mr`/`bn`/`ta` contain only nav labels, so switching language leaves most of the page in English. All data content (schemes, legal, services, FAQ, library) is English-only. The chat API only accepts `en | hi`.

**Target State:** 12 fully-supported locales — `en, hi, mr, bn, ta, te, kn, pa, gu, or, ml, ur`. The `LanguageSwitcher` switches every screen's chrome and all content. Switching the locale re-renders the whole app (no reload).

**Approach:** Extend the locale set; make the data layer locale-aware (content stored per-locale, accessors take a locale, `en` fallback); fully translate all dictionary keys for all 12 locales; load in-script display fonts; widen chat-language handling.

**Constraint:** No new dependencies. Content authored as static strings in the codebase (no translation API). Delivered as one spec with 3 phases; each phase leaves a working, language-switchable app.

---

## Locale & Fonts

### Locale set
`src/lib/i18n/i18n.ts`:
```ts
export const LOCALES = ["en", "hi", "mr", "bn", "ta", "te", "kn", "pa", "gu", "or", "ml", "ur"] as const;
export type Locale = (typeof LOCALES)[number];
```
No UI change required to `LanguageSwitcher`/`useI18n` — they already iterate `LOCALES`.

### Fonts (`src/app/layout.tsx`)
Load Google Noto Serif fonts (variable `--font-*`, weight 400/500/600/700) for the non-Latin scripts and apply as the display font when the locale uses that script:
- `Noto_Serif_Devanagari` (existing, hi/mr)
- `Noto_Serif_Bengali` (bn)
- `Noto_Serif_Tamil` (ta)
- `Noto_Serif_Telugu` (te)
- `Noto_Serif_Kannada` (kn)
- `Noto_Serif_Gurmukhi` (pa)
- `Noto_Serif_Gujarati` (gu)
- `Noto_Serif_Odia` (or)
- `Noto_Serif_Malayalam` (ml)
- `Noto_Serif_*` (ur → Arabic script): use `Noto_Naskh_Arabic` (or fall back to the platform's Arabic font).

Apply the matching `--font-display` (or an equivalent token) contextually. Simplest robust approach: define a `--font-script` variable on the `<html>` (or a wrapper) based on the active locale, and reference it in the existing `font-[var(--font-display)]` usages via a locale-aware class. Bundle-weight note: loading all fonts adds weight; acceptable for full script support. (Fallback decision: if bundle weight is a concern, defer Odia/Malayalam/Urdu to system fonts — but default is to load all.)

---

## i18n Dictionary (Chrome)

`src/lib/i18n/dictionaries.ts` must define **every** key for **all 12 locales**. Current state: `en`+`hi` complete, `mr/bn/ta` partial (nav + `all`/`globe`), other 5 absent.

**Required key set (per locale)** — the full set already present in `en`, plus nothing new beyond it (all current keys must be translated):
- `nav.*` (home, chat, schemes, library, grievance, grievanceStatus, legal, services, faq, more)
- `common.*` (send, submit, loading, retry, openNew, search, newSession, back, next, previous, mic, stopMic, readAloud, stopReadAloud, voiceUnsupported, askThisScheme, trackStatus, enterComplaintId, findStatus, all, source, error, globe)
- `evidence.*` (strong, moderate, weak)
- `abstained.title`
- `domain.*` (cropInsurance, financial, grievance, literacy, law, unknown)
- `landing.*` (badge, tagline, ctaChat, ctaSchemes, f1title, f1text, f2title, f2text, f3title, f3text, howTitle, how1title, how1text, how2title, how2text, how3title, how3text, trustTitle, trustText)
- `category.*` (crop-insurance, pacs, financial, subsidy)
- `schemes.*` (title, subtitle, searchPlaceholder, empty, count)
- `detail.*` (notFound, overview, eligibility, benefits, howToApply, documents)
- `library.*` (title, subtitle, searchPlaceholder, empty, page)
- `grievance.*` (title, subtitle, step1..3, categoryTitle, detailsLabel, placeholder, nameLabel, contactLabel, optional, submitLabel, reviewTitle, successTitle, complaintIdLabel, statusTitle, statusSubtitle, notFound, category.insurance/pacs/service/other)
- `status.*` (submitted, inReview, resolved)
- `chat.*` (starter1..4, placeholder, welcome)
- `legal.*`, `legalCategory.*`
- `services.*`, `serviceCategory.*`
- `faq.*`, `faqCategory.*`
- `legal.count`, `services.count`

**Fallback:** `translate()` already falls back `locale → en`. This stays as a safety net but is no longer the normal path.

---

## Locale-Aware Data Layer

Currently modules (`src/lib/data/schemes.ts`, `legal.ts`, `services.ts`, `faq.ts`, `library.ts`) export non-localized objects. Refactor to store text per-locale and expose locale-aware accessors.

### Shared helper (`src/lib/data/i18n.ts`)
```ts
import type { Locale } from "@/lib/i18n/i18n";
export type I18nText = Record<Locale, string>;
export type I18nList = Record<Locale, string[]>;

export function localize(value: I18nText, locale: Locale): string {
  return value[locale] ?? value.en;
}
export function localizeList(value: I18nList, locale: Locale): string[] {
  return value[locale] ?? value.en;
}
```
(Exported from `src/lib/data/index.ts`.)

### Modelled entities
Only user-facing text fields are localized; identifiers/keys stay as-is (`slug`, `category`, `id`, `domain`, `url`, `page`, `publishedAt`).

**schemes** (`Scheme`): `name`, `benefit`, `overview` → `I18nText`; `eligibility`, `benefits`, `howToApply`, `documents` → `I18nList`. `slug`, `category` unchanged.
**legal** (`LegalDoc`): `title`, `badge`, `overview`, `source.label` → `I18nText`; `keyProvisions`, `applicability`, `byLaws` → `I18nList`. `slug`, `category`, `source.url` unchanged.
**services** (`Service`): `name`, `summary`, `description`, `source.label` → `I18nText`; `whoCanUse`, `howToAccess` → `I18nList`. `slug`, `category`, `source.url` unchanged.
**faq** (`FaqItem`): `question`, `answer` → `I18nText`. `id`, `category` unchanged.
**library** (`LibraryDoc`): `title`, `source` → `I18nText`. `id`, `domain`, `page`, `url`, `publishedAt` unchanged.

### Accessors (signature change — ALL callers updated)
```ts
getSchemes(locale: Locale): Scheme[]
getScheme(locale: Locale, slug: string): Scheme | undefined
getLegalDocs(locale: Locale): LegalDoc[]
getLegalDoc(locale: Locale, slug: string): LegalDoc | undefined
getServices(locale: Locale): Service[]
getService(locale: Locale, slug: string): Service | undefined
getFaqItems(locale: Locale): FaqItem[]
getLibraryDocs(locale: Locale): LibraryDoc[]
```
Each returns localized plain objects (converting `I18nText` → `string`, `I18nList` → `string[]`) via `localize`/`localizeList`. A shared `pick(locale)` resolves any missing locale to `en`.

### Callers to update (pass `useI18n().locale`)
- `src/app/page.tsx` (home schemes preview)
- `src/app/schemes/page.tsx`
- `src/app/schemes/[slug]/page.tsx`
- `src/app/library/page.tsx`
- `src/app/legal/page.tsx`
- `src/app/legal/[slug]/page.tsx`
- `src/app/services/page.tsx`
- `src/app/services/[slug]/page.tsx`
- `src/app/faq/page.tsx`

### Data-module content
Each module's content is stored as per-locale maps for every entity/field. `en` (existing English content) stays the reference; `hi` already exists for scheme content where present; the remaining locales are authored during implementation. Every locale must be populated for every text field (no gaps) to satisfy "full."

---

## Chat & Speech Language

### Chat (`src/lib/api.ts`, `src/components/ChatWindow.tsx`)
- `sendChat` `payload.language: "en" | "hi"` → `Locale` (send the active locale).
- `ChatResponse.language: "en" | "hi"` → `Locale`.
- `ChatWindow`: `const lang = locale === "hi" ? "hi" : "en"` becomes `const lang: Locale = locale`; `fallback(lang)` and `toggleMic` speech locale mapping updated to pass the locale (speech already maps `*-IN`).

**Documented limitation:** the backend currently only answers `en`/`hi`. Sending another locale is safe on the frontend; responses fall back per the backend. This is the only part of "every content" the frontend cannot translate itself (chat responses are backend-generated).

### Speech (`src/lib/speech.ts`)
No structural change needed — `listen(locale)`/`speak(text, locale)` already accept an arbitrary locale and derive `lang = locale + "-IN"`. Verify `hi/mr/bn/ta/te/kn/pa/gu/or/ml/ur` all map to `*-IN` (Urdu uses ur-PK/ur-IN; accept `ur-IN` fallback).

---

## Testing

- `src/lib/data/i18n.test.ts` (new): `localize`/`localizeList` fall back to `en` when a locale is missing.
- Update `schemes.test`/`legal.test`/`services.test`/`faq.test` and any data tests to the new locale-accessor signatures (pass `"en"`).
- `src/lib/i18n/i18n.test.ts`: assert all 12 locales in `LOCALES`.
- `src/lib/i18n/dictionaries.test.ts` (new): assert every locale has every key that `en` has (parity), and `mr/bn/ta/te/kn/pa/gu/or/ml/ur` are fully populated (no empty-string values).
- Manual: language switch relabels every screen; `npm run build`, `npm run lint`, `npm run test` all pass.

---

## Phases

### Phase 1 — Foundation & chrome
1. Extend `LOCALES` to 12.
2. `src/lib/data/i18n.ts` helper + `localize`/`localizeList` + `pick`.
3. Refactor all 5 data modules to per-locale structures + locale-aware accessors; migrate all callers to pass locale.
4. Refactor data tests to new signatures.
5. Widen chat `language` to `Locale` (api + ChatWindow + speech verify).
6. Fonts in `layout.tsx` + locale-aware script font.
7. Fully translate ALL `en` keys into `mr`,`bn`,`ta`,`te`,`kn`,`pa`,`gu`,`or`,`ml`,`ur` (dictionaries).

Result: entire app chrome + content engine switches language for all 12 locales. Data text is `en` for the new languages until Phase 2/3 fills it (fallback makes this safe), except the UI chrome which is fully translated.

### Phase 2 — Content batch 1
Author per-locale content for `schemes`, `services` (and `library` source/title) in all 12 locales, populating every `I18nText`/`I18nList` so no fallback to `en` remains for these entities.

### Phase 3 — Content batch 2
Author per-locale content for `legal` (long provisions) and `faq` in all 12 locales.

---

## Out of Scope

- Translating backend chat responses (backend-driven; documented limitation).
- Machine-translation integration / translation API.
- `mr/bn/ta` automatic improvement beyond full parity (they are done in Phase 1).
- Audio (TTS) quality per language — speech uses the browser's installed voices; no custom voices.

---

## Spec Self-Review

**Placeholder scan:** No TBD/TODO. Keys, fields, accessors, locales, and callers enumerated precisely. Literal per-locale translation text is authored during implementation as the content (the spec defines the contract: which keys/fields, which locales, `en` fallback).
**Internal consistency:** Data-accessor signature change is reflected in the "Callers to update" list and tests; chrome keys enumerated match the existing `en` set; chat/speech language mapping consistent.
**Scope check:** Large but a single coherent system; broken into 3 phases each independently shippable and testable.
**Ambiguity check:** Locale list, fallback rule (`en`), per-locale field coverage, and chat limitation all explicit.

## Approval

**Status:** Approved by user (combined single spec).
**Next Step:** Invoke writing-plans skill to produce a phased implementation plan.
