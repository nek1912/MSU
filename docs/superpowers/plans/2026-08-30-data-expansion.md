# Data Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand hardcoded data from 3 schemes to 12 schemes, add real grievance categories, and improve Hindi/Gujarati translations.

**Architecture:** Add new entries to existing TypeScript data arrays. No new files, no interface changes. Follow existing I18nText/I18nList patterns.

**Tech Stack:** TypeScript, Next.js, existing I18n helpers

## Global Constraints

- No changes to TypeScript interfaces
- No new files needed
- All existing tests must pass
- Follow existing I18nText/I18nList patterns
- No comments in code
- Hindi + Gujarati only for new entries (en always present)

---

### Task 1: Add new schemes to schemes.ts

**Files:**
- Modify: `frontend/src/lib/data/schemes.ts`

**Interfaces:**
- Consumes: existing `Scheme` interface, `I18nText`, `I18nList`
- Produces: expanded `schemes` array with 9 new entries

- [ ] **Step 1: Read current schemes.ts to understand structure**

Read `frontend/src/lib/data/schemes.ts` lines 1-55 to understand the Scheme interface and existing entries.

- [ ] **Step 2: Add PM-KISAN scheme**

Add after the `kisan-credit-card` entry:

```typescript
{
  slug: "pm-kisan",
  category: "subsidy",
  name: { en: "PM-KISAN Samman Nidhi", hi: "पीएम-किसान सम्मान निधि", gu: "પીએમ-કિસાન સન્માન નિધિ" },
  benefit: { en: "Direct income support of ₹6,000 per year to farmer families.", hi: "किसान परिवारों को प्रति वर्ष ₹6,000 की प्रत्यक्ष आय सहायता।", gu: "ખેડૂત પરિવારોને દર વર્ષે ₹6,000 ની સીધી આવક સહાય." },
  overview: { en: "PM-KISAN provides ₹6,000 per year in three installments to all landholding farmer families. The scheme aims to supplement farmers' income and meet their agricultural needs.", hi: "पीएम-किसान सभी भूमिधारक किसान परिवारों को तीन किस्तों में प्रति वर्ष ₹6,000 प्रदान करता है। यह योजना किसानों की आय पूरक करने और उनकी कृषि आवश्यकताओं को पूरा करने का लक्ष्य रखती है।", gu: "પીએમ-કિસાન તમામ જમીન ધરાવતા ખેડૂત પરિવારોને ત્રણ હપ્તામાં દર વર્ષે ₹6,000 પ્રદાન કરે છે. આ યોજના ખેડૂતોની આવક પૂરક કરવા અને તેમની ખેતીની જરૂરિયાતો પૂરી કરવાનું લક્ષ્ય રાખે છે." },
  eligibility: { en: ["All landholding farmer families.", "Subject to certain exclusions for institutional landholders."], hi: ["सभी भूमिधारक किसान परिवार।", "संस्थागत भूमिधारकों के लिए कुछ बहिष्करण के अधीन।"], gu: ["તમામ જમીન ધરાવતા ખેડૂત પરિવારો.", "સંસ્થાગત જમીન ધરાવનારાઓ માટે અમુક બહિષ્કરણોને આધીન."] },
  benefits: { en: ["₹6,000 per year in three equal installments.", "Direct bank transfer to beneficiary accounts.", "Covers all landholding farmer families."], hi: ["तीन समान किस्तों में प्रति वर्ष ₹6,000.", "लाभार्थी खातों में सीधा बैंक हस्तांतरण।", "सभी भूमिधारक किसान परिवारों को कवर करता है।"], gu: ["ત્રણ સમાન હપ્તામાં દર વર્ષે ₹6,000.", "લાભાર્થી ખાતામાં સીધો બેંક ટ્રાન્સફર.", "તમામ જમીન ધરાવતા ખેડૂત પરિવારોને આવરી લે છે."] },
  howToApply: { en: ["Register at the PM-KISAN portal or through your PACS.", "Submit Aadhaar and bank account details.", "Installments are released automatically after verification."], hi: ["पीएम-किसान पोर्टल पर या अपने PACS के माध्यम से पंजीकरण करें।", "आधार और बैंक खाता विवरण जमा करें।", "सत्यापन के बाद किस्तें स्वचालित रूप से जारी की जाती हैं।"], gu: ["પીએમ-કિસાન પોર્ટલ પર અથવા તમારી PACS દ્વારા નોંધણી કરો.", "આધાર અને બેંક ખાતાની વિગતો જમા કરો.", "ચકાસણી પછી હપ્તાઓ આપમેળે બહાર પાડવામાં આવે છે."] },
  documents: { en: ["Aadhaar card", "Bank account details", "Land records"], hi: ["आधार कार्ड", "बैंक खाता विवरण", "जमीन के रिकॉर्ड"], gu: ["આધાર કાર્ડ", "બેંક ખાતાની વિગતો", "જમીનના રેકોર્ડ"] },
},
```

- [ ] **Step 3: Add PM-KUSUM scheme**

Add after PM-KISAN:

```typescript
{
  slug: "pm-kusum",
  category: "subsidy",
  name: { en: "PM-KUSUM Solar Pump Scheme", hi: "पीएम-कुसुम सोलर पंप योजना", gu: "પીએમ-કુસુમ સોલાર પંપ યોજના" },
  benefit: { en: "Subsidized solar pumps and grid-connected solar power for farmers.", hi: "किसानों के लिए सब्सिडी वाले सोलर पंप और ग्रिड-कनेक्टेड सौर ऊर्जा।", gu: "ખેડૂતો માટે સબસિડીવાળા સોલાર પંપ અને ગ્રિડ-કનેક્ટેડ સોલાર પાવર." },
  overview: { en: "PM-KUSUM supports farmers to install standalone solar pumps and grid-connected solar power plants. It reduces dependence on diesel and grid electricity.", hi: "पीएम-कुसुम किसानों को स्वतंत्र सोलर पंप और ग्रिड-कनेक्टेड सौर ऊर्जा संयंत्र स्थापित करने में सहायता प्रदान करता है। यह डीजल और ग्रिड बिजली पर निर्भरता कम करता है।", gu: "પીએમ-કુસુમ ખેડૂતોને સ્વતંત્ર સોલાર પંપ અને ગ્રિડ-કનેક્ટેડ સોલાર પાવર પ્લાન્ટ સ્થાપિત કરવામાં સહાય કરે છે. તે ડીઝલ અને ગ્રિડ વીજળી પરની નિર્ભરતા ઘટાડે છે." },
  eligibility: { en: ["All farmers, including small and marginal farmers.", "Cooperative societies and farmer producer organizations."], hi: ["सभी किसान, छोटे और सीमांत किसान सहित।", "सहकारी समितियां और किसान उत्पादक संगठन।"], gu: ["તમામ ખેડૂતો, નાના અને સીમાંત ખેડૂતો સહિત.", "સહકારી સમિતિઓ અને ખેડૂત ઉત્પાદક સંગઠનો."] },
  benefits: { en: ["Up to 60% subsidy on solar pumps.", "Income from selling excess solar power to the grid.", "Reduced electricity costs for irrigation."], hi: ["सोलर पंप पर अधिकतम 60% सब्सिडी।", "अतिरिक्त सौर ऊर्जा बेचकर आय।", "सिंचाई के लिए बिजली लागत में कमी।"], gu: ["સોલાર પંપ પર 60% સુધી સબસિડી.", "વધારાની સોલાર પાવર વેચીને આવક.", "સિંચાઈ માટે વીજળી ખર્ચમાં ઘટાડો."] },
  howToApply: { en: ["Apply through the PM-KUSUM portal or your state DISCOM.", "Submit identity and land records.", "Get approval and install the solar system."], hi: ["पीएम-कुसुम पोर्टल या अपने राज्य DISCOM के माध्यम से आवेदन करें।", "ओळख और जमीन के रिकॉर्ड जमा करें।", "अनुमोदन प्राप्त करें और सोलर सिस्टम स्थापित करें।"], gu: ["પીએમ-કુસુમ પોર્ટલ અથવા તમારા રાજ્ય DISCOM દ્વારા અરજી કરો.", "ઓળખ અને જમીનના રેકોર્ડ જમા કરો.", "મંજૂરી મેળવો અને સોલાર સિસ્ટમ સ્થાપિત કરો."] },
  documents: { en: ["Aadhaar card", "Land records", "Bank account details"], hi: ["आधार कार्ड", "जमीन के रिकॉर्ड", "बैंक खाता विवरण"], gu: ["આધાર કાર્ડ", "જમીનના રેકોર્ડ", "બેંક ખાતાની વિગતો"] },
},
```

- [ ] **Step 4: Add PM Dhan Dhanya scheme**

Add after PM-KUSUM:

```typescript
{
  slug: "pm-dhan-dhanya",
  category: "subsidy",
  name: { en: "PM Dhan Dhanya Yojana", hi: "पीएम धन धान्य योजना", gu: "પીએમ ધન ધાન્ય યોજના" },
  benefit: { en: "Comprehensive agricultural development in 100 districts focusing on foodgrain production.", hi: "100 जिलों में खाद्यान्न उत्पादन पर केंद्रित समग्र कृषि विकास।", gu: "100 જિલ્હામાં અનાજ ઉત્પાદન પર કેન્દ્રિત સમગ્ર કૃષિ વિકાસ." },
  overview: { en: "PM Dhan Dhanya targets 100 districts with low foodgrain production. It provides integrated support for irrigation, credit, insurance, and market access.", hi: "पीएम धन धान्य कम खाद्यान्न उत्पादन वाले 100 जिलों को लक्षित करता है। यह सिंचाई, क्रेडिट, बीमा और बाजार पहुंच के लिए एकीकृत सहायता प्रदान करता है।", gu: "પીએમ ધન ધાન્ય ઓછા અનાજ ઉત્પાદનવાળા 100 જિલ્હાને લક્ષ્ય બનાવે છે. તે સિંચાઈ, ક્રેડિટ, વીમા અને બજાર પહોંચ માટે એકીકૃત સહાય પ્રદાન કરે છે." },
  eligibility: { en: ["Farmers in 100 identified districts.", "Focus on small and marginal farmers."], hi: ["100 पहचाने गए जिलों में किसान।", "छोटे और सीमांत किसानों पर ध्यान केंद्रित।"], gu: ["100 ઓળખાયેલા જિલ્હામાં ખેડૂતો.", "નાના અને સીમાંત ખેડૂતો પર ધ્યાન કેન્દ્રિત."] },
  benefits: { en: ["Integrated support for irrigation and water management.", "Access to credit and insurance.", "Market linkage and value chain development."], hi: ["सिंचाई और जल प्रबंधन के लिए एकीकृत सहायता।", "क्रेडिट और बीमा तक पहुंच।", "बाजार लिंकेज और मूल्य श्रृंखला विकास।"], gu: ["સિંચાઈ અને જળ વ્યવસ્થાપન માટે એકીકૃત સહાય.", "ક્રેડિટ અને વીમા સુધી પહોંચ.", "બજાર લિંકેજ અને મૂલ્ય શ્રેણી વિકાસ."] },
  howToApply: { en: ["Contact your district agriculture office or PACS.", "Submit land and identity documents.", "Get enrolled in the scheme."], hi: ["अपने जिला कृषि कार्यालय या PACS से संपर्क करें।", "जमीन और ओळख दस्तावेज जमा करें।", "योजना में नामांकित हों।"], gu: ["તમારા જિલ્હા કૃષિ કાર્યાલય અથવા PACS નો સંપર્ક કરો.", "જમીન અને ઓળખ દસ્તાવેજો જમા કરો.", "યોજનામાં નોંધણી કરાવો."] },
  documents: { en: ["Aadhaar card", "Land records", "Bank account"], hi: ["आधार कार्ड", "जमीन के रिकॉर्ड", "बैंक खाता"], gu: ["આધાર કાર્ડ", "જમીનના રેકોર્ડ", "બેંક ખાતું"] },
},
```

- [ ] **Step 5: Add remaining schemes (NABARD AIF, NRCF, e-NAM, Soil Health, R-Gramin Nidhi, PMJDY)**

Add 6 more schemes following the same pattern. Each scheme must have `en`, `hi`, `gu` translations for all fields.

- [ ] **Step 6: Run TypeScript check**

Run: `npx tsc --noEmit` in `frontend/`
Expected: No errors

- [ ] **Step 7: Run existing tests**

Run: `npm test` in `frontend/`
Expected: All tests pass

- [ ] **Step 8: Commit**

```bash
git add frontend/src/lib/data/schemes.ts
git commit -m "feat: expand schemes from 3 to 12 with Hindi/Gujarati translations"
```

---

### Task 2: Expand grievance categories

**Files:**
- Modify: `frontend/src/lib/data/grievance.ts`

**Interfaces:**
- Consumes: existing `GrievanceCategory` interface
- Produces: expanded `CATEGORIES` array

- [ ] **Step 1: Read current grievance.ts**

Read `frontend/src/lib/data/grievance.ts` to understand the CATEGORIES structure.

- [ ] **Step 2: Add new grievance categories**

Replace the CATEGORIES array with expanded version:

```typescript
const CATEGORIES: GrievanceCategory[] = [
  { id: "insurance", labelKey: "grievance.category.insurance" },
  { id: "pacs", labelKey: "grievance.category.pacs" },
  { id: "service", labelKey: "grievance.category.service" },
  { id: "credit-denial", labelKey: "grievance.category.credit-denial" },
  { id: "insurance-delay", labelKey: "grievance.category.insurance-delay" },
  { id: "election-dispute", labelKey: "grievance.category.election-dispute" },
  { id: "mismanagement", labelKey: "grievance.category.mismanagement" },
  { id: "member-rights", labelKey: "grievance.category.member-rights" },
  { id: "fund-misuse", labelKey: "grievance.category.fund-misuse" },
  { id: "other", labelKey: "grievance.category.other" },
];
```

- [ ] **Step 3: Add translation keys for new categories**

Check if there's an i18n file for grievance labels. If not, the labels are handled by the chatbot's natural language understanding. The `labelKey` values are used for display.

- [ ] **Step 4: Run TypeScript check**

Run: `npx tsc --noEmit` in `frontend/`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/data/grievance.ts
git commit -m "feat: expand grievance categories from 4 to 10"
```

---

### Task 3: Add new services

**Files:**
- Modify: `frontend/src/lib/data/services.ts`

**Interfaces:**
- Consumes: existing `Service` interface
- Produces: expanded `services` array

- [ ] **Step 1: Read current services.ts**

Read `frontend/src/lib/data/services.ts` to understand the Service interface and existing entries.

- [ ] **Step 2: Add new service entries**

Add 2-3 new services following the existing pattern. Each service must have `en`, `hi`, `gu` translations.

- [ ] **Step 3: Run TypeScript check**

Run: `npx tsc --noEmit` in `frontend/`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/data/services.ts
git commit -m "feat: add new cooperative services with Hindi/Gujarati translations"
```

---

### Task 4: Add new legal docs

**Files:**
- Modify: `frontend/src/lib/data/legal.ts`

**Interfaces:**
- Consumes: existing `LegalDoc` interface
- Produces: expanded `legalDocs` array

- [ ] **Step 1: Read current legal.ts**

Read `frontend/src/lib/data/legal.ts` to understand the LegalDoc interface and existing entries.

- [ ] **Step 2: Add new legal doc entries**

Add 2-3 new legal docs following the existing pattern. Each doc must have `en`, `hi`, `gu` translations.

- [ ] **Step 3: Run TypeScript check**

Run: `npx tsc --noEmit` in `frontend/`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/data/legal.ts
git commit -m "feat: add new legal docs with Hindi/Gujarati translations"
```

---

### Task 5: Add new library docs

**Files:**
- Modify: `frontend/src/lib/data/library.ts`

**Interfaces:**
- Consumes: existing `LibraryDoc` interface
- Produces: expanded `libraryDocs` array

- [ ] **Step 1: Read current library.ts**

Read `frontend/src/lib/data/library.ts` to understand the LibraryDoc interface and existing entries.

- [ ] **Step 2: Add new library doc entries**

Add 2-3 new library docs following the existing pattern. Each doc must have `en`, `hi`, `gu` translations and real URLs.

- [ ] **Step 3: Run TypeScript check**

Run: `npx tsc --noEmit` in `frontend/`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/data/library.ts
git commit -m "feat: add new library docs with Hindi/Gujarati translations"
```

---

### Task 6: Final verification

**Files:**
- None (verification only)

- [ ] **Step 1: Run full TypeScript check**

Run: `npx tsc --noEmit` in `frontend/`
Expected: No errors

- [ ] **Step 2: Run all tests**

Run: `npm test` in `frontend/`
Expected: All tests pass

- [ ] **Step 3: Verify scheme count**

Check that `schemes.ts` now has 12 entries (3 original + 9 new).

- [ ] **Step 4: Verify grievance count**

Check that `grievance.ts` now has 10 categories (4 original + 6 new).

- [ ] **Step 5: Final commit if needed**

```bash
git add -A
git commit -m "feat: complete data expansion with real Indian cooperative schemes"
```
