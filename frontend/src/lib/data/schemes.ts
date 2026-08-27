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
    name: { en: "Pradhan Mantri Fasal Bima Yojana (PMFBY)", te: "ప్రధాన మంత్రి ఫసల్ బీమా యోజన (PMFBY)" },
    benefit: { en: "Comprehensive crop insurance against natural calamities and pest attacks.", te: "ప్రకృతి వైపరీత్యాలు మరియు పీడల దాడుల నుండి సమగ్ర పంట బీమా." },
    overview: { en: "PMFBY provides insurance cover and financial support to farmers against failure of crops due to natural calamities, pests and diseases. Farmers pay a low premium while the central and state governments cover the rest.", te: "PMFBY ప్రకృతి వైపరీత్యాలు, పీడలు మరియు వ్యాధుల వల్ల పంట నష్టం జరిగినప్పుడు రైతులకు బీమా రక్షణ మరియు ఆర్థిక సహాయం అందిస్తుంది. రైతులు తక్కువ ప్రీమియం చెల్లిస్తారు, మిగిలిన మొత్తాన్ని కేంద్ర మరియు రాష్ట్ర ప్రభుత్వాలు భరిస్తాయి." },
    eligibility: { en: ["All farmers including sharecroppers and tenant farmers.", "Both loanee (credit-linked) and non-loanee farmers.", "Notification of the crop season of the implementing state."], te: ["భాగస్వామి మరియు కౌలు రైతులతో సహా అందరు రైతులు.", "అప్పు తీసుకున్న (క్రెడిట్-లింక్డ్) మరియు అప్పు తీసుకోని రైతులు — ఇద్దరూ.", "అమలు చేసే రాష్ట్రం యొక్క పంట సీజన్ ప్రకటన."] },
    benefits: { en: ["Low premium: up to 2% for Kharif and 1.5% for Rabi food crops.", "Full sum insured on crop loss due to listed risks.", "Post-harvest losses and localized calamity coverage."], te: ["తక్కువ ప్రీమియం: ఖరీఫ్కు 2% మరియు రబీ ఆహార పంటలకు 1.5% వరకు.", "జాబితా చేసిన ప్రమాదాల వల్ల పంట నష్టానికి పూర్తి బీమా మొత్తం.", "పంటకోత తర్వాత నష్టాలు మరియు స్థానిక వైపరీత్యాలకు రక్షణ."] },
    howToApply: { en: ["Register a consent letter on the PMFBY portal or through your bank.", "Approach your PACS / CSC / bank branch before the crop season deadline.", "Keep land records and sowing receipts ready for claim filing."], te: ["PMFBY పోర్టల్లో లేదా మీ బ్యాంకు ద్వారా సమ్మతి పత్రం (కన్సెంట్ లెటర్) నమోదు చేయండి.", "పంట సీజన్ గడువుకు ముందు మీ PACS / CSC / బ్యాంకు శాఖను సంప్రదించండి.", "దావా దాఖలు చేయడానికి భూ రికార్డులు మరియు విత్తన రసీదులను సిద్ధంగా ఉంచండి."] },
    documents: { en: ["Aadhaar card", "Land ownership / tenancy records", "Bank passbook", "Sowing certificate"], te: ["ఆధార్ కార్డు", "భూ యాజమాన్యం / కౌలు రికార్డులు", "బ్యాంకు పాస్‌బుక్", "విత్తన ధృవీకరణ పత్రం"] },
  },
  {
    slug: "pacs-membership",
    category: "pacs",
    name: { en: "PACS Membership & Services", te: "PACS సభ్యత్వం & సేవలు" },
    benefit: { en: "Access to credit, storage and agro-services through your local cooperative.", te: "మీ స్థానిక సహకార సంస్థ ద్వారా అప్పు, నిల్వ మరియు వ్యవసాయ సేవలకు ప్రాప్యత." },
    overview: { en: "The Primary Agricultural Credit Society (PACS) is the village-level cooperative that lends to members, provides farm inputs and supports storage. Joining gives you access to affordable credit and grievance recourse.", te: "ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీ (PACS) అనేది గ్రామ స్థాయి సహకార సంస్థ, ఇది సభ్యులకు అప్పులు ఇస్తుంది, వ్యవసాయ ఇన్‌పుట్‌లను అందిస్తుంది మరియు నిల్వకు మద్దతు ఇస్తుంది. చేరడం వల్ల మీకు సరసమైన అప్పు మరియు ఫిర్యాదు పరిష్కారానికి ప్రాప్యత లభిస్తుంది." },
    eligibility: { en: ["Residents of the PACS area of operation.", "Any person of the village who owns land or engages in agriculture."], te: ["PACS కార్యకలాపాల ప్రాంతంలో నివసించేవారు.", "గ్రామంలో భూమి కలిగి ఉన్న లేదా వ్యవసాయం చేసే ఏ వ్యక్తి అయినా."] },
    benefits: { en: ["Short-term crop loans at subsidized rates.", "Storage and godown facilities.", "Fertilizers, seeds and agro-equipment on demand."], te: ["సబ్సిడీ రేట్లలో స్వల్పకాలిక పంట రుణాలు.", "నిల్వ మరియు గోదాము సౌకర్యాలు.", "ఎరువులు, విత్తనాలు మరియు వ్యవసాయ పరికరాలు — అవసరమైనప్పుడు."] },
    howToApply: { en: ["Visit your local PACS office and fill the membership form.", "Submit identity and residence documents.", "Pay the small share/entrance fee as notified."], te: ["మీ స్థానిక PACS కార్యాలయాన్ని సందర్శించి సభ్యత్వ ఫారం పూరించండి.", "గుర్తింపు మరియు నివాస పత్రాలను సమర్పించండి.", "నోటిఫై చేసిన ప్రకారం చిన్న షేర్ / అడ్మిషన్ రుసుము చెల్లించండి."] },
    documents: { en: ["Aadhaar card", "Passport-size photo", "Income/residence proof"], te: ["ఆధార్ కార్డు", "పాస్‌పోర్ట్ పరిమాణ ఫోటో", "ఆదాయం / నివాస రుజువు"] },
  },
  {
    slug: "kisan-credit-card",
    category: "financial",
    name: { en: "Kisan Credit Card (KCC)", te: "కిసాన్ క్రెడిట్ కార్డు (KCC)" },
    benefit: { en: "Affordable, flexible crop credit with insurance and repayment support.", te: "బీమా మరియు తిరిగి చెల్లింపు మద్దతుతో సరసమైన, సౌకర్యవంతమైన పంట రుణం." },
    overview: { en: "KCC is a credit card for farmers for crop production needs, post-harvest expenses, and consumption. It bundles a personal accident insurance cover and provides flexible repayment aligned with harvest cycles.", te: "KCC అనేది పంట ఉత్పత్తి అవసరాలు, పంటకోత తర్వాత ఖర్చులు మరియు వినియోగం కోసం రైతులకు అందుబాటులో ఉండే క్రెడిట్ కార్డు. ఇది వ్యక్తిగత ప్రమాద బీమా రక్షణతో కూడి ఉంటుంది మరియు పంట చక్రాలకు అనుగుణంగా సౌకర్యవంతమైన తిరిగి చెల్లింపును అందిస్తుంది." },
    eligibility: { en: ["Owner-cultivators, tenant farmers and sharecroppers.", "Members of PACS / cooperative credit institutions."], te: ["యజమాని-సాగుదారులు, కౌలు రైతులు మరియు భాగస్వామి రైతులు.", "PACS / సహకార క్రెడిట్ సంస్థల సభ్యులు."] },
    benefits: { en: ["Short-term credit with competitive interest and interest subvention.", "Composite loan for cultivation and post-harvest needs.", "Personal accident insurance cover."], te: ["పోటీ వడ్డీ మరియు వడ్డీ సబ్సిడీతో స్వల్పకాలిక రుణం.", "సాగు మరియు పంటకోత తర్వాత అవసరాలకు మిశ్రమ రుణం.", "వ్యక్తిగత ప్రమాద బీమా రక్షణ."] },
    howToApply: { en: ["Apply at your bank or PACS with KCC application form.", "Provide land, identity and crop-cycle details.", "Receive the card after sanction and verification."], te: ["KCC దరఖాస్తు ఫారంతో మీ బ్యాంకు లేదా PACS వద్ద దరఖాస్తు చేయండి.", "భూమి, గుర్తింపు మరియు పంట చక్ర వివరాలను అందించండి.", "మంజూరు మరియు ధృవీకరణ తర్వాత కార్డు అందుకోండి."] },
    documents: { en: ["Aadhaar", "Land records", "Crop details", "Bank passbook"], te: ["ఆధార్", "భూ రికార్డులు", "పంట వివరాలు", "బ్యాంకు పాస్‌బుక్"] },
  },
  {
    slug: "coop-subsidy",
    category: "subsidy",
    name: { en: "Cooperative & Subsidy Schemes", te: "సహకార & సబ్సిడీ పథకాలు" },
    benefit: { en: "Capital, interest and infrastructure subsidies for cooperatives and farmers.", te: "సహకార సంస్థలు మరియు రైతులకు మూలధన, వడ్డీ మరియు మౌలిక సదుపాయ సబ్సిడీలు." },
    overview: { en: "The Ministry of Cooperation and allied bodies run several subsidy schemes for farmer cooperatives — capital support, interest subvention, godown and processing infrastructure, to strengthen local cooperatives.", te: "సహకార మంత్రిత్వ శాఖ మరియు అనుబంధ సంస్థలు రైతు సహకార సంస్థల కోసం అనేక సబ్సిడీ పథకాలను నిర్వహిస్తాయి — మూలధన మద్దతు, వడ్డీ సబ్సిడీ, గోదాము మరియు ప్రాసెసింగ్ మౌలిక సదుపాయాలు, స్థానిక సహకార సంస్థలను బలోపేతం చేయడానికి." },
    eligibility: { en: ["Registered cooperatives / PACS within the scheme scope.", "Individual farmers applying through eligible cooperative channels."], te: ["పథకం పరిధిలో నమోదైన సహకార సంస్థలు / PACS.", "అర్హత గల సహకార మార్గాల ద్వారా దరఖాస్తు చేసే వ్యక్తిగత రైతులు."] },
    benefits: { en: ["Capital support for cooperative infrastructure.", "Interest subvention on eligible loans.", "Support for godowns, processing and storage units."], te: ["సహకార మౌలిక సదుపాయాలకు మూలధన మద్దతు.", "అర్హత గల రుణాలపై వడ్డీ సబ్సిడీ.", "గోదాములు, ప్రాసెసింగ్ మరియు నిల్వ యూనిట్లకు మద్దతు."] },
    howToApply: { en: ["Check eligibility against the current scheme guidelines.", "Submit the application through the portal or the nodal cooperative office.", "Track approval and disbursal status on the portal."], te: ["ప్రస్తుత పథకం మార్గదర్శకాల ప్రకారం అర్హతను తనిఖీ చేయండి.", "పోర్టల్ ద్వారా లేదా నోడల్ సహకార కార్యాలయం ద్వారా దరఖాస్తును సమర్పించండి.", "పోర్టల్‌లో మంజూరు మరియు విడుదల స్థితిని ట్రాక్ చేయండి."] },
    documents: { en: ["Cooperative registration certificate", "Financial statements", "Project proposal"], te: ["సహకార సంస్థ నమోదు ధృవీకరణ పత్రం", "ఆర్థిక ప్రకటనలు", "ప్రాజెక్టు ప్రతిపాదన"] },
  },
  {
    slug: "pmay-gramin",
    category: "subsidy",
    name: { en: "Pradhan Mantri Awas Yojana – Gramin (PMAY-G)", te: "ప్రధాన మంత్రి ఆవాస్ యోజన – గ్రామీణ (PMAY-G)" },
    benefit: { en: "Financial assistance for housing to eligible rural families.", te: "అర్హత గల గ్రామీణ కుటుంబాలకు గృహ నిర్మాణానికి ఆర్థిక సహాయం." },
    overview: { en: "PMAY-G supports construction of pucca houses for eligible rural households with central and state assistance.", te: "PMAY-G అర్హత గల గ్రామీణ కుటుంబాలకు కేంద్ర మరియు రాష్ట్ర సహాయంతో పక్కా ఇళ్ల నిర్మాణానికి మద్దతు ఇస్తుంది." },
    eligibility: { en: ["Households without a pucca house.", "Beneficiary confirmed on SECC / Awas+ list."], te: ["పక్కా ఇల్లు లేని కుటుంబాలు.", "SECC / అవాస్+ జాబితాలో ధృవీకరించబడిన లబ్ధిదారు."] },
    benefits: { en: ["Direct cash transfer under the scheme.", "Financial support for toilet and electricity (targeted areas)."], te: ["పథకం కింద ప్రత్యక్ష నగదు బదిలీ.", "మరుగుదొడ్డి మరియు విద్యుత్ కోసం ఆర్థిక మద్దతు (లక్ష్య ప్రాంతాలు)."] },
    howToApply: { en: ["Apply through the Awas+ portal or your PACS / gram panchayat.", "Complete the geo-tagging and verification."], te: ["అవాస్+ పోర్టల్ ద్వారా లేదా మీ PACS / గ్రామ పంచాయతీ ద్వారా దరఖాస్తు చేయండి.", "జియో-ట్యాగింగ్ మరియు ధృవీకరణను పూర్తి చేయండి."] },
    documents: { en: ["Aadhaar", "Bank account", "SECC / beneficiary confirmation"], te: ["ఆధార్", "బ్యాంకు ఖాతా", "SECC / లబ్ధిదారు ధృవీకరణ"] },
  },
  {
    slug: "financial-literacy",
    category: "financial",
    name: { en: "Financial Literacy Programmes", te: "ఆర్థిక అక్షరాస్యత కార్యక్రమాలు" },
    benefit: { en: "Learn savings, borrowing, insurance and grievance basics.", te: "పొదుపు, అప్పు, బీమా మరియు ఫిర్యాదుల ప్రాథమిక అంశాలను నేర్చుకోండి." },
    overview: { en: "Financial literacy modules help cooperative members understand savings, affordable credit, insurance and safe digital banking practices.", te: "ఆర్థిక అక్షరాస్యత మాడ్యూళ్లు సహకార సభ్యులు పొదుపు, సరసమైన అప్పు, బీమా మరియు సురక్షిత డిజిటల్ బ్యాంకింగ్ పద్ధతులను అర్థం చేసుకోవడంలో సహాయపడతాయి." },
    eligibility: { en: ["All farmers, PACS members and rural stakeholders."], te: ["అందరు రైతులు, PACS సభ్యులు మరియు గ్రామీణ భాగస్వాములు."] },
    benefits: { en: ["Better savings and borrowing decisions.", "Awareness of insurance and entitlements.", "Safety against fraud and over-borrowing."], te: ["మెరుగైన పొదుపు మరియు అప్పు నిర్ణయాలు.", "బీమా మరియు హక్కులపై అవగాహన.", "మోసం మరియు అధిక అప్పు నుండి రక్షణ."] },
    howToApply: { en: ["Join village-level camps organized by PACS / banks.", "Use the chatbot for simple, plain-language guidance."], te: ["PACS / బ్యాంకులు నిర్వహించే గ్రామ స్థాయి శిబిరాల్లో చేరండి.", "సరళమైన, సులభ భాషలో మార్గదర్శనం కోసం చాట్‌బాట్‌ను ఉపయోగించండి."] },
    documents: { en: ["None — open participation"], te: ["ఏదీ లేదు — బహిరంగ భాగస్వామ్యం"] },
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
