# Data Expansion Design Spec

## Goal
Expand hardcoded data from 3 schemes to 8-15 schemes, add real grievance categories, and improve Hindi/Gujarati translations. All data is real Indian government cooperative/scheme information.

## Scope
- **Schemes**: Add 8-12 new schemes (PM-KISAN, PM-KUSUM, PM Dhan Dhanya, NABARD AIF, etc.)
- **Grievance**: Expand from 4 categories to 8-10 with Hindi/Gujarati labels
- **Services**: Add 2-3 new service entries
- **Legal**: Add 2-3 new legal docs (state coop acts, model bylaws)
- **Library**: Add 2-3 new library docs with real URLs
- **Translations**: Hindi + Gujarati only for new entries. Fix existing Hindi/Gujarati where machine-generated.

## Files to Modify
1. `frontend/src/lib/data/schemes.ts` — add new scheme entries
2. `frontend/src/lib/data/grievance.ts` — expand categories
3. `frontend/src/lib/data/services.ts` — add new service entries
4. `frontend/src/lib/data/legal.ts` — add new legal docs
5. `frontend/src/lib/data/library.ts` — add new library docs

## Schemes to Add

| Slug | Category | Name (en) |
|------|----------|-----------|
| `pm-kisan` | subsidy | PM-KISAN Samman Nidhi |
| `pm-kusum` | subsidy | PM-KUSUM Solar Pump Scheme |
| `pm-dhan-dhanya` | subsidy | PM Dhan Dhanya Yojana |
| `nabard-aif` | subsidy | NABARD Agri Infrastructure Fund |
| `nrcf` | subsidy | National Rural Credit Cooperative Fund |
| `e-nam` | agro-inputs | e-NAM Marketplace |
| `soil-health` | agro-inputs | Soil Health Card Scheme |
| `rganidhi` | financial | R-Gramin Nidhi |
| `pmjdj` | financial | Pradhan Mantri Jan Dhan Yojana |

## Grievance Categories to Add

| ID | Label (en) | Label (hi) | Label (gu) |
|----|------------|------------|------------|
| credit-denial | Credit Denial | कर्ज से इनकार | ધિરાણ નામંજૂર |
| insurance-delay | Insurance Claim Delay | बीमा दावा में देरी | વીમા દાવામાં વિલંબ |
| election-dispute | Election Dispute | चुनाव विवाद | ચૂંટણી વિવાદ |
| mismanagement | Mismanagement | दुर्व्यवस्थા | દુર્વ્યવસ્થા |
| member-rights | Member Rights Violation | सदस्य अधिकार उल्लंघन | સભ્ય અધિકાર ઉલ્લંઘન |
| fund-misuse | Fund Misuse | कोष का दुरुपयोग | ભંડારનો દુરુપયોગ |

## Constraints
- No changes to TypeScript interfaces
- No new files needed
- All existing tests must pass
- Follow existing I18nText/I18nList patterns
- No comments in code
