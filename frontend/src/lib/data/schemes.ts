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
    name: { en: "Pradhan Mantri Fasal Bima Yojana (PMFBY)", te: "ప్రధాన మంత్రి ఫసల్ బీమా యోజన (PMFBY)", kn: "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬೀಮಾ ಯೋಜನೆ (PMFBY)" },
    benefit: { en: "Comprehensive crop insurance against natural calamities and pest attacks.", te: "ప్రకృతి వైపరీత్యాలు మరియు పీడల దాడుల నుండి సమగ్ర పంట బీమా.", kn: "ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳು ಮತ್ತು ಪೀಡೆಗಳ ಆಕ್ರಮಣಗಳಿಂದ ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ." },
    overview: { en: "PMFBY provides insurance cover and financial support to farmers against failure of crops due to natural calamities, pests and diseases. Farmers pay a low premium while the central and state governments cover the rest.", te: "PMFBY ప్రకృతి వైపరీత్యాలు, పీడలు మరియు వ్యాధుల వల్ల పంట నష్టం జరిగినప్పుడు రైతులకు బీమా రక్షణ మరియు ఆర్థిక సహాయం అందిస్తుంది. రైతులు తక్కువ ప్రీమియం చెల్లిస్తారు, మిగిలిన మొత్తాన్ని కేంద్ర మరియు రాష్ట్ర ప్రభుత్వాలు భరిస్తాయి.", kn: "PMFBY ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳು, ಪೀಡೆಗಳು ಮತ್ತು ರೋಗಗಳಿಂದ ಬೆಳೆ ನಷ್ಟವಾದಾಗ ರೈತರಿಗೆ ವಿಮೆ ರಕ್ಷಣೆ ಮತ್ತು ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ಒದಗಿಸುತ್ತದೆ. ರೈತರು ಕಡಿಮೆ ಪ್ರೀಮಿಯಂ ಪಾವತಿಸುತ್ತಾರೆ, ಉಳಿದ ಮೊತ್ತವನ್ನು ಕೇಂದ್ರ ಮತ್ತು ರಾಜ್ಯ ಸರ್ಕಾರಗಳು ಭರಿಸುತ್ತವೆ." },
    eligibility: { en: ["All farmers including sharecroppers and tenant farmers.", "Both loanee (credit-linked) and non-loanee farmers.", "Notification of the crop season of the implementing state."], te: ["భాగస్వామి మరియు కౌలు రైతులతో సహా అందరు రైతులు.", "అప్పు తీసుకున్న (క్రెడిట్-లింక్డ్) మరియు అప్పు తీసుకోని రైతులు — ఇద్దరూ.", "అమలు చేసే రాష్ట్రం యొక్క పంట సీజన్ ప్రకటన."], kn: ["ಭಾಗಸ್ವಾಮಿ ಮತ್ತು ಗೇಣಿದಾರ ರೈತರನ್ನು ಒಳಗೊಂಡಂತೆ ಎಲ್ಲಾ ರೈತರು.", "ಸಾಲ ಪಡೆದ (ಕ್ರೆಡಿಟ್-ಲಿಂಕ್ಡ್) ಮತ್ತು ಸಾಲ ಪಡೆಯದ ರೈತರು — ಇಬ್ಬರೂ.", "ಜಾರಿಗೊಳಿಸುವ ರಾಜ್ಯದ ಬೆಳೆ ಋತುವಿನ ಪ್ರಕಟಣೆ."] },
    benefits: { en: ["Low premium: up to 2% for Kharif and 1.5% for Rabi food crops.", "Full sum insured on crop loss due to listed risks.", "Post-harvest losses and localized calamity coverage."], te: ["తక్కువ ప్రీమియం: ఖరీఫ్కు 2% మరియు రబీ ఆహార పంటలకు 1.5% వరకు.", "జాబితా చేసిన ప్రమాదాల వల్ల పంట నష్టానికి పూర్తి బీమా మొత్తం.", "పంటకోత తర్వాత నష్టాలు మరియు స్థానిక వైపరీత్యాలకు రక్షణ."], kn: ["ಕಡಿಮೆ ಪ್ರೀಮಿಯಂ: ಖರೀಫ್‌ಗೆ 2% ಮತ್ತು ರಬಿ ಆಹಾರ ಬೆಳೆಗಳಿಗೆ 1.5% ವರೆಗೆ.", "ಪಟ್ಟಿ ಮಾಡಲಾದ ಅಪಾಯಗಳಿಂದ ಬೆಳೆ ನಷ್ಟಕ್ಕೆ ಪೂರ್ಣ ವಿಮಾ ಮೊತ್ತ.", "ಸುಗ್ಗಿಯ ನಂತರದ ನಷ್ಟಗಳು ಮತ್ತು ಸ್ಥಳೀಯ ವಿಕೋಪಗಳ ರಕ್ಷಣೆ."] },
    howToApply: { en: ["Register a consent letter on the PMFBY portal or through your bank.", "Approach your PACS / CSC / bank branch before the crop season deadline.", "Keep land records and sowing receipts ready for claim filing."], te: ["PMFBY పోర్టల్లో లేదా మీ బ్యాంకు ద్వారా సమ్మతి పత్రం (కన్సెంట్ లెటర్) నమోదు చేయండి.", "పంట సీజన్ గడువుకు ముందు మీ PACS / CSC / బ్యాంకు శాఖను సంప్రదించండి.", "దావా దాఖలు చేయడానికి భూ రికార్డులు మరియు విత్తన రసీదులను సిద్ధంగా ఉంచండి."], kn: ["PMFBY ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅಥವಾ ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಮೂಲಕ ಸಮ್ಮತಿ ಪತ್ರವನ್ನು ನೋಂದಾಯಿಸಿ.", "ಬೆಳೆ ಋತುವಿನ ಗಡುವಿಗೆ ಮೊದಲು ನಿಮ್ಮ PACS / CSC / ಬ್ಯಾಂಕ್ ಶಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.", "ದಾವೆ ದಾಖಲಿಸಲು ಭೂ ದಾಖಲೆಗಳು ಮತ್ತು ಬಿತ್ತನೆ ರಸೀದಿಗಳನ್ನು ಸಿದ್ಧವಾಗಿಡಿ."] },
    documents: { en: ["Aadhaar card", "Land ownership / tenancy records", "Bank passbook", "Sowing certificate"], te: ["ఆధార్ కార్డు", "భూ యాజమాన్యం / కౌలు రికార్డులు", "బ్యాంకు పాస్‌బుక్", "విత్తన ధృవీకరణ పత్రం"], kn: ["ಆಧಾರ್ ಕಾರ್ಡ್", "ಭೂ ಮಾಲೀಕತ್ವ / ಗೇಣಿ ದಾಖಲೆಗಳು", "ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್", "ಬಿತ್ತನೆ ಪ್ರಮಾಣಪತ್ರ"] },
  },
  {
    slug: "pacs-membership",
    category: "pacs",
    name: { en: "PACS Membership & Services", te: "PACS సభ్యత్వం & సేవలు", kn: "PACS ಸದಸ್ಯತ್ವ ಮತ್ತು ಸೇವೆಗಳು" },
    benefit: { en: "Access to credit, storage and agro-services through your local cooperative.", te: "మీ స్థానిక సహకార సంస్థ ద్వారా అప్పు, నిల్వ మరియు వ్యవసాయ సేవలకు ప్రాప్యత.", kn: "ನಿಮ್ಮ ಸ್ಥಳೀಯ ಸಹಕಾರ ಸಂಸ್ಥೆಯ ಮೂಲಕ ಸಾಲ, ಶೇಖರಣೆ ಮತ್ತು ಕೃಷಿ ಸೇವೆಗಳಿಗೆ ಪ್ರವೇಶ." },
    overview: { en: "The Primary Agricultural Credit Society (PACS) is the village-level cooperative that lends to members, provides farm inputs and supports storage. Joining gives you access to affordable credit and grievance recourse.", te: "ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీ (PACS) అనేది గ్రామ స్థాయి సహకార సంస్థ, ఇది సభ్యులకు అప్పులు ఇస్తుంది, వ్యవసాయ ఇన్‌పుట్‌లను అందిస్తుంది మరియు నిల్వకు మద్దతు ఇస్తుంది. చేరడం వల్ల మీకు సరసమైన అప్పు మరియు ఫిర్యాదు పరిష్కారానికి ప్రాప్యత లభిస్తుంది.", kn: "ಪ್ರಾಥಮಿಕ ಕೃಷಿ ಕ್ರೆಡಿಟ್ ಸೊಸೈಟಿ (PACS) ಗ್ರಾಮ ಮಟ್ಟದ ಸಹಕಾರ ಸಂಸ್ಥೆಯಾಗಿದ್ದು, ಸದಸ್ಯರಿಗೆ ಸಾಲ ನೀಡುತ್ತದೆ, ಕೃಷಿ ಇನ್‌ಪುಟ್‌ಗಳನ್ನು ಒದಗಿಸುತ್ತದೆ ಮತ್ತು ಶೇಖರಣೆಗೆ ಬೆಂಬಲ ನೀಡುತ್ತದೆ. ಸೇರುವುದರಿಂದ ಕೈಗೆಟುಕುವ ಸಾಲ ಮತ್ತು ದೂರು ಪರಿಹಾರದ ಪ್ರವೇಶ ಲಭಿಸುತ್ತದೆ." },
    eligibility: { en: ["Residents of the PACS area of operation.", "Any person of the village who owns land or engages in agriculture."], te: ["PACS కార్యకలాపాల ప్రాంతంలో నివసించేవారు.", "గ్రామంలో భూమి కలిగి ఉన్న లేదా వ్యవసాయం చేసే ఏ వ్యక్తి అయినా."], kn: ["PACS ಕಾರ್ಯವ್ಯಾಪ್ತಿ ಪ್ರದೇಶದ ನಿವಾಸಿಗಳು.", "ಗ್ರಾಮದಲ್ಲಿ ಭೂಮಿ ಹೊಂದಿರುವ ಅಥವಾ ಕೃಷಿಯಲ್ಲಿ ತೊಡಗಿರುವ ಯಾವುದೇ ವ್ಯಕ್ತಿ."] },
    benefits: { en: ["Short-term crop loans at subsidized rates.", "Storage and godown facilities.", "Fertilizers, seeds and agro-equipment on demand."], te: ["సబ్సిడీ రేట్లలో స్వల్పకాలిక పంట రుణాలు.", "నిల్వ మరియు గోదాము సౌకర్యాలు.", "ఎరువులు, విత్తనాలు మరియు వ్యవసాయ పరికరాలు — అవసరమైనప్పుడు."], kn: ["ಸಬ್ಸಿಡಿ ದರಗಳಲ್ಲಿ ಅಲ್ಪಾವಧಿಯ ಬೆಳೆ ಸಾಲಗಳು.", "ಶೇಖರಣೆ ಮತ್ತು ಗೋದಾಮು ಸೌಲಭ್ಯಗಳು.", "ಗೊಬ್ಬರಗಳು, ಬೀಜಗಳು ಮತ್ತು ಕೃಷಿ ಉಪಕರಣಗಳು ಬೇಡಿಕೆಯ ಮೇರೆಗೆ."] },
    howToApply: { en: ["Visit your local PACS office and fill the membership form.", "Submit identity and residence documents.", "Pay the small share/entrance fee as notified."], te: ["మీ స్థానిక PACS కార్యాలయాన్ని సందర్శించి సభ్యత్వ ఫారం పూరించండి.", "గుర్తింపు మరియు నివాస పత్రాలను సమర్పించండి.", "నోటిఫై చేసిన ప్రకారం చిన్న షేర్ / అడ్మిషన్ రుసుము చెల్లించండి."], kn: ["ನಿಮ್ಮ ಸ್ಥಳೀಯ PACS ಕಚೇರಿಗೆ ಭೇಟಿ ನೀಡಿ ಸದಸ್ಯತ್ವ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಿ.", "ಗುರುತು ಮತ್ತು ನಿವಾಸ ದಾಖಲೆಗಳನ್ನು ಸಲ್ಲಿಸಿ.", "ಪ್ರಕಟಿಸಿದಂತೆ ಸಣ್ಣ ಪಾಲು / ಪ್ರವೇಶ ಶುಲ್ಕ ಪಾವತಿಸಿ."] },
    documents: { en: ["Aadhaar card", "Passport-size photo", "Income/residence proof"], te: ["ఆధార్ కార్డు", "పాస్‌పోర్ట్ పరిమాణ ఫోటో", "ఆదాయం / నివాస రుజువు"], kn: ["ಆಧಾರ್ ಕಾರ್ಡ್", "ಪಾಸ್‌ಪೋರ್ಟ್ ಗಾತ್ರದ ಫೋಟೊ", "ಆದಾಯ / ನಿವಾಸ ಪುರಾವೆ"] },
  },
  {
    slug: "kisan-credit-card",
    category: "financial",
    name: { en: "Kisan Credit Card (KCC)", te: "కిసాన్ క్రెడిట్ కార్డు (KCC)", kn: "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC)" },
    benefit: { en: "Affordable, flexible crop credit with insurance and repayment support.", te: "బీమా మరియు తిరిగి చెల్లింపు మద్దతుతో సరసమైన, సౌకర్యవంతమైన పంట రుణం.", kn: "ವಿಮೆ ಮತ್ತು ಮರುಪಾವತಿ ಬೆಂಬಲದೊಂದಿಗೆ ಕೈಗೆಟುಕುವ, ಸ್ಥಿತಿಸ್ಥಾಪಕ ಬೆಳೆ ಸಾಲ." },
    overview: { en: "KCC is a credit card for farmers for crop production needs, post-harvest expenses, and consumption. It bundles a personal accident insurance cover and provides flexible repayment aligned with harvest cycles.", te: "KCC అనేది పంట ఉత్పత్తి అవసరాలు, పంటకోత తర్వాత ఖర్చులు మరియు వినియోగం కోసం రైతులకు అందుబాటులో ఉండే క్రెడిట్ కార్డు. ఇది వ్యక్తిగత ప్రమాద బీమా రక్షణతో కూడి ఉంటుంది మరియు పంట చక్రాలకు అనుగుణంగా సౌకర్యవంతమైన తిరిగి చెల్లింపును అందిస్తుంది.", kn: "KCC ಬೆಳೆ ಉತ್ಪಾದನೆಯ ಅಗತ್ಯಗಳಿಗೆ, ಸುಗ್ಗಿಯ ನಂತರದ ವೆಚ್ಚಗಳಿಗೆ ಮತ್ತು ಬಳಕೆಗಾಗಿ ರೈತರಿಗೆ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ಆಗಿದೆ. ಇದು ವೈಯಕ್ತಿಕ ಅಪಘಾತ ವಿಮೆ ರಕ್ಷಣೆಯನ್ನು ಒಳಗೊಂಡಿರುತ್ತದೆ ಮತ್ತು ಸುಗ್ಗಿ ಚಕ್ರಗಳಿಗೆ ಹೊಂದುವ ಸ್ಥಿತಿಸ್ಥಾಪಕ ಮರುಪಾವತಿಯನ್ನು ಒದಗಿಸುತ್ತದೆ." },
    eligibility: { en: ["Owner-cultivators, tenant farmers and sharecroppers.", "Members of PACS / cooperative credit institutions."], te: ["యజమాని-సాగుదారులు, కౌలు రైతులు మరియు భాగస్వామి రైతులు.", "PACS / సహకార క్రెడిట్ సంస్థల సభ్యులు."], kn: ["ಮಾಲೀಕ-ಬೇಸಾಯಗಾರರು, ಗೇಣಿದಾರ ರೈತರು ಮತ್ತು ಭಾಗಸ್ವಾಮಿ ರೈತರು.", "PACS / ಸಹಕಾರ ಕ್ರೆಡಿಟ್ ಸಂಸ್ಥೆಗಳ ಸದಸ್ಯರು."] },
    benefits: { en: ["Short-term credit with competitive interest and interest subvention.", "Composite loan for cultivation and post-harvest needs.", "Personal accident insurance cover."], te: ["పోటీ వడ్డీ మరియు వడ్డీ సబ్సిడీతో స్వల్పకాలిక రుణం.", "సాగు మరియు పంటకోత తర్వాత అవసరాలకు మిశ్రమ రుణం.", "వ్యక్తిగత ప్రమాద బీమా రక్షణ."], kn: ["ಸ್ಪರ್ಧಾತ್ಮಕ ಬಡ್ಡಿ ಮತ್ತು ಬಡ್ಡಿ ಸಬ್ಸಿಡಿಯೊಂದಿಗೆ ಅಲ್ಪಾವಧಿಯ ಸಾಲ.", "ಬೇಸಾಯ ಮತ್ತು ಸುಗ್ಗಿಯ ನಂತರದ ಅಗತ್ಯಗಳಿಗೆ ಸಾಮೂಹಿಕ ಸಾಲ.", "ವೈಯಕ್ತಿಕ ಅಪಘಾತ ವಿಮೆ ರಕ್ಷಣೆ."] },
    howToApply: { en: ["Apply at your bank or PACS with KCC application form.", "Provide land, identity and crop-cycle details.", "Receive the card after sanction and verification."], te: ["KCC దరఖాస్తు ఫారంతో మీ బ్యాంకు లేదా PACS వద్ద దరఖాస్తు చేయండి.", "భూమి, గుర్తింపు మరియు పంట చక్ర వివరాలను అందించండి.", "మంజూరు మరియు ధృవీకరణ తర్వాత కార్డు అందుకోండి."], kn: ["KCC ಅರ್ಜಿ ಫಾರ್ಮ್‌ನೊಂದಿಗೆ ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಅಥವಾ PACS ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.", "ಭೂಮಿ, ಗುರುತು ಮತ್ತು ಬೆಳೆ ಚಕ್ರದ ವಿವರಗಳನ್ನು ಒದಗಿಸಿ.", "ಅನುಮೋದನೆ ಮತ್ತು ಪರಿಶೀಲನೆಯ ನಂತರ ಕಾರ್ಡ್ ಪಡೆಯಿರಿ."] },
    documents: { en: ["Aadhaar", "Land records", "Crop details", "Bank passbook"], te: ["ఆధార్", "భూ రికార్డులు", "పంట వివరాలు", "బ్యాంకు పాస్‌బుక్"], kn: ["ಆಧಾರ್", "ಭೂ ದಾಖಲೆಗಳು", "ಬೆಳೆ ವಿವರಗಳು", "ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್"] },
  },
  {
    slug: "coop-subsidy",
    category: "subsidy",
    name: { en: "Cooperative & Subsidy Schemes", te: "సహకార & సబ్సిడీ పథకాలు", kn: "ಸಹಕಾರ ಮತ್ತು ಸಬ್ಸಿಡಿ ಯೋಜನೆಗಳು" },
    benefit: { en: "Capital, interest and infrastructure subsidies for cooperatives and farmers.", te: "సహకార సంస్థలు మరియు రైతులకు మూలధన, వడ్డీ మరియు మౌలిక సదుపాయ సబ్సిడీలు.", kn: "ಸಹಕಾರ ಸಂಸ್ಥೆಗಳು ಮತ್ತು ರೈತರಿಗೆ ಬಂಡವಾಳ, ಬಡ್ಡಿ ಮತ್ತು ಮೂಲಸೌಕರ್ಯ ಸಬ್ಸಿಡಿಗಳು." },
    overview: { en: "The Ministry of Cooperation and allied bodies run several subsidy schemes for farmer cooperatives — capital support, interest subvention, godown and processing infrastructure, to strengthen local cooperatives.", te: "సహకార మంత్రిత్వ శాఖ మరియు అనుబంధ సంస్థలు రైతు సహకార సంస్థల కోసం అనేక సబ్సిడీ పథకాలను నిర్వహిస్తాయి — మూలధన మద్దతు, వడ్డీ సబ్సిడీ, గోదాము మరియు ప్రాసెసింగ్ మౌలిక సదుపాయాలు, స్థానిక సహకార సంస్థలను బలోపేతం చేయడానికి.", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ ಮತ್ತು ಸಂಬಂಧಿತ ಸಂಸ್ಥೆಗಳು ರೈತ ಸಹಕಾರ ಸಂಸ್ಥೆಗಳಿಗೆ ಹಲವಾರು ಸಬ್ಸಿಡಿ ಯೋಜನೆಗಳನ್ನು ನಡೆಸುತ್ತವೆ — ಬಂಡವಾಳ ಬೆಂಬಲ, ಬಡ್ಡಿ ಸಬ್ಸಿಡಿ, ಗೋದಾಮು ಮತ್ತು ಸಂಸ್ಕರಣೆ ಮೂಲಸೌಕರ್ಯ, ಸ್ಥಳೀಯ ಸಹಕಾರ ಸಂಸ್ಥೆಗಳನ್ನು ಬಲಪಡಿಸಲು." },
    eligibility: { en: ["Registered cooperatives / PACS within the scheme scope.", "Individual farmers applying through eligible cooperative channels."], te: ["పథకం పరిధిలో నమోదైన సహకార సంస్థలు / PACS.", "అర్హత గల సహకార మార్గాల ద్వారా దరఖాస్తు చేసే వ్యక్తిగత రైతులు."], kn: ["ಯೋಜನೆಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ನೋಂದಾಯಿತ ಸಹಕಾರ ಸಂಸ್ಥೆಗಳು / PACS.", "ಅರ್ಹ ಸಹಕಾರ ಮಾರ್ಗಗಳ ಮೂಲಕ ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ವೈಯಕ್ತಿಕ ರೈತರು."] },
    benefits: { en: ["Capital support for cooperative infrastructure.", "Interest subvention on eligible loans.", "Support for godowns, processing and storage units."], te: ["సహకార మౌలిక సదుపాయాలకు మూలధన మద్దతు.", "అర్హత గల రుణాలపై వడ్డీ సబ్సిడీ.", "గోదాములు, ప్రాసెసింగ్ మరియు నిల్వ యూనిట్లకు మద్దతు."], kn: ["ಸಹಕಾರ ಮೂಲಸೌಕರ್ಯಕ್ಕೆ ಬಂಡವಾಳ ಬೆಂಬಲ.", "ಅರ್ಹ ಸಾಲಗಳಿಗೆ ಬಡ್ಡಿ ಸಬ್ಸಿಡಿ.", "ಗೋದಾಮುಗಳು, ಸಂಸ್ಕರಣೆ ಮತ್ತು ಶೇಖರಣಾ ಘಟಕಗಳಿಗೆ ಬೆಂಬಲ."] },
    howToApply: { en: ["Check eligibility against the current scheme guidelines.", "Submit the application through the portal or the nodal cooperative office.", "Track approval and disbursal status on the portal."], te: ["ప్రస్తుత పథకం మార్గదర్శకాల ప్రకారం అర్హతను తనిఖీ చేయండి.", "పోర్టల్ ద్వారా లేదా నోడల్ సహకార కార్యాలయం ద్వారా దరఖాస్తును సమర్పించండి.", "పోర్టల్‌లో మంజూరు మరియు విడుదల స్థితిని ట్రాక్ చేయండి."], kn: ["ಪ್ರಸ್ತುತ ಯೋಜನೆಯ ಮಾರ್ಗಸೂಚಿಗಳಿಗೆ ಅನುಗುಣವಾಗಿ ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಿ.", "ಪೋರ್ಟಲ್ ಅಥವಾ ನೋಡಲ್ ಸಹಕಾರ ಕಚೇರಿ ಮೂಲಕ ಅರ್ಜಿಯನ್ನು ಸಲ್ಲಿಸಿ.", "ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅನುಮೋದನೆ ಮತ್ತು ವಿತರಣೆ ಸ್ಥಿತಿಯನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ."] },
    documents: { en: ["Cooperative registration certificate", "Financial statements", "Project proposal"], te: ["సహకార సంస్థ నమోదు ధృవీకరణ పత్రం", "ఆర్థిక ప్రకటనలు", "ప్రాజెక్టు ప్రతిపాదన"], kn: ["ಸಹಕಾರ ಸಂಸ್ಥೆ ನೋಂದಣಿ ಪ್ರಮಾಣಪತ್ರ", "ಆರ್ಥಿಕ ಹೇಳಿಕೆಗಳು", "ಯೋಜನಾ ಪ್ರಸ್ತಾವನೆ"] },
  },
  {
    slug: "pmay-gramin",
    category: "subsidy",
    name: { en: "Pradhan Mantri Awas Yojana – Gramin (PMAY-G)", te: "ప్రధాన మంత్రి ఆవాస్ యోజన – గ్రామీణ (PMAY-G)", kn: "ಪ್ರಧಾನ ಮಂತ್ರಿ ಆವಾಸ್ ಯೋಜನೆ – ಗ್ರಾಮೀಣ (PMAY-G)" },
    benefit: { en: "Financial assistance for housing to eligible rural families.", te: "అర్హత గల గ్రామీణ కుటుంబాలకు గృహ నిర్మాణానికి ఆర్థిక సహాయం.", kn: "ಅರ್ಹ ಗ್ರಾಮೀಣ ಕುಟುಂಬಗಳಿಗೆ ವಸತಿಗಾಗಿ ಆರ್ಥಿಕ ನೆರವು." },
    overview: { en: "PMAY-G supports construction of pucca houses for eligible rural households with central and state assistance.", te: "PMAY-G అర్హత గల గ్రామీణ కుటుంబాలకు కేంద్ర మరియు రాష్ట్ర సహాయంతో పక్కా ఇళ్ల నిర్మాణానికి మద్దతు ఇస్తుంది.", kn: "PMAY-G ಅರ್ಹ ಗ್ರಾಮೀಣ ಕುಟುಂಬಗಳಿಗೆ ಕೇಂದ್ರ ಮತ್ತು ರಾಜ್ಯ ನೆರವಿನೊಂದಿಗೆ ಪಕ್ಕಾ ಮನೆಗಳ ನಿರ್ಮಾಣಕ್ಕೆ ಬೆಂಬಲ ನೀಡುತ್ತದೆ." },
    eligibility: { en: ["Households without a pucca house.", "Beneficiary confirmed on SECC / Awas+ list."], te: ["పక్కా ఇల్లు లేని కుటుంబాలు.", "SECC / అవాస్+ జాబితాలో ధృవీకరించబడిన లబ్ధిదారు."], kn: ["ಪಕ್ಕಾ ಮನೆ ಇಲ್ಲದ ಕುಟುಂಬಗಳು.", "SECC / ಅವಾಸ್+ ಪಟ್ಟಿಯಲ್ಲಿ ದೃಢೀಕರಿಸಿದ ಫಲಾನುಭವಿ."] },
    benefits: { en: ["Direct cash transfer under the scheme.", "Financial support for toilet and electricity (targeted areas)."], te: ["పథకం కింద ప్రత్యక్ష నగదు బదిలీ.", "మరుగుదొడ్డి మరియు విద్యుత్ కోసం ఆర్థిక మద్దతు (లక్ష్య ప్రాంతాలు)."], kn: ["ಯೋಜನೆಯಡಿ ಪ್ರತ್ಯಕ್ಷ ನಗದು ವರ್ಗಾವಣೆ.", "ಶೌಚಾಲಯ ಮತ್ತು ವಿದ್ಯುತ್ತಿಗೆ ಆರ್ಥಿಕ ಬೆಂಬಲ (ಗುರಿ ಪ್ರದೇಶಗಳು)."] },
    howToApply: { en: ["Apply through the Awas+ portal or your PACS / gram panchayat.", "Complete the geo-tagging and verification."], te: ["అవాస్+ పోర్టల్ ద్వారా లేదా మీ PACS / గ్రామ పంచాయతీ ద్వారా దరఖాస్తు చేయండి.", "జియో-ట్యాగింగ్ మరియు ధృవీకరణను పూర్తి చేయండి."], kn: ["ಅವಾಸ್+ ಪೋರ್ಟಲ್ ಅಥವಾ ನಿಮ್ಮ PACS / ಗ್ರಾಮ ಪಂಚಾಯತ್ ಮೂಲಕ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.", "ಜಿಯೋ-ಟ್ಯಾಗಿಂಗ್ ಮತ್ತು ಪರಿಶೀಲನೆಯನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ."] },
    documents: { en: ["Aadhaar", "Bank account", "SECC / beneficiary confirmation"], te: ["ఆధార్", "బ్యాంకు ఖాతా", "SECC / లబ్ధిదారు ధృవీకరణ"], kn: ["ಆಧಾರ್", "ಬ್ಯಾಂಕ್ ಖಾತೆ", "SECC / ಫಲಾನುಭವಿ ದೃಢೀಕರಣ"] },
  },
  {
    slug: "financial-literacy",
    category: "financial",
    name: { en: "Financial Literacy Programmes", te: "ఆర్థిక అక్షరాస్యత కార్యక్రమాలు", kn: "ಆರ್ಥಿಕ ಸಾಕ್ಷರತಾ ಕಾರ್ಯಕ್ರಮಗಳು" },
    benefit: { en: "Learn savings, borrowing, insurance and grievance basics.", te: "పొదుపు, అప్పు, బీమా మరియు ఫిర్యాదుల ప్రాథమిక అంశాలను నేర్చుకోండి.", kn: "ಉಳಿತಾಯ, ಸಾಲ, ವಿಮೆ ಮತ್ತು ದೂರುಗಳ ಮೂಲಭೂತ ಅಂಶಗಳನ್ನು ಕಲಿಯಿರಿ." },
    overview: { en: "Financial literacy modules help cooperative members understand savings, affordable credit, insurance and safe digital banking practices.", te: "ఆర్థిక అక్షరాస్యత మాడ్యూళ్లు సహకార సభ్యులు పొదుపు, సరసమైన అప్పు, బీమా మరియు సురక్షిత డిజిటల్ బ్యాంకింగ్ పద్ధతులను అర్థం చేసుకోవడంలో సహాయపడతాయి.", kn: "ಆರ್ಥಿಕ ಸಾಕ್ಷರತಾ ಮಾಡ್ಯೂಲ್‌ಗಳು ಸಹಕಾರ ಸದಸ್ಯರು ಉಳಿತಾಯ, ಕೈಗೆಟುಕುವ ಸಾಲ, ವಿಮೆ ಮತ್ತು ಸುರಕ್ಷಿತ ಡಿಜಿಟಲ್ ಬ್ಯಾಂಕಿಂಗ್ ಪದ್ಧತಿಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುತ್ತವೆ." },
    eligibility: { en: ["All farmers, PACS members and rural stakeholders."], te: ["అందరు రైతులు, PACS సభ్యులు మరియు గ్రామీణ భాగస్వాములు."], kn: ["ಎಲ್ಲಾ ರೈತರು, PACS ಸದಸ್ಯರು ಮತ್ತು ಗ್ರಾಮೀಣ ಪಾಲುದಾರರು."] },
    benefits: { en: ["Better savings and borrowing decisions.", "Awareness of insurance and entitlements.", "Safety against fraud and over-borrowing."], te: ["మెరుగైన పొదుపు మరియు అప్పు నిర్ణయాలు.", "బీమా మరియు హక్కులపై అవగాహన.", "మోసం మరియు అధిక అప్పు నుండి రక్షణ."], kn: ["ಉತ್ತಮ ಉಳಿತಾಯ ಮತ್ತು ಸಾಲದ ನಿರ್ಧಾರಗಳು.", "ವಿಮೆ ಮತ್ತು ಹಕ್ಕುಗಳ ಬಗ್ಗೆ ಅರಿವು.", "ವಂಚನೆ ಮತ್ತು ಅತಿಯಾದ ಸಾಲದಿಂದ ರಕ್ಷಣೆ."] },
    howToApply: { en: ["Join village-level camps organized by PACS / banks.", "Use the chatbot for simple, plain-language guidance."], te: ["PACS / బ్యాంకులు నిర్వహించే గ్రామ స్థాయి శిబిరాల్లో చేరండి.", "సరళమైన, సులభ భాషలో మార్గదర్శనం కోసం చాట్‌బాట్‌ను ఉపయోగించండి."], kn: ["PACS / ಬ್ಯಾಂಕುಗಳು ಆಯೋಜಿಸುವ ಗ್ರಾಮ ಮಟ್ಟದ ಶಿಬಿರಗಳಿಗೆ ಸೇರಿಕೊಳ್ಳಿ.", "ಸರಳ, ಸುಲಭ ಭಾಷೆಯ ಮಾರ್ಗದರ್ಶನಕ್ಕಾಗಿ ಚಾಟ್‌ಬಾಟ್ ಬಳಸಿ."] },
    documents: { en: ["None — open participation"], te: ["ఏదీ లేదు — బహిరంగ భాగస్వామ్యం"], kn: ["ಯಾವುದೂ ಇಲ್ಲ — ಮುಕ್ತ ಭಾಗವಹಿಸುವಿಕೆ"] },
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
