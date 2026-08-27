import type { Locale } from "@/lib/i18n/i18n";
import { localize, localizeList, type I18nList, type I18nText } from "./i18n";

export type ServiceCategory = "credit" | "storage" | "insurance" | "agro-inputs" | "subsidy" | "membership";

export interface Service {
  slug: string;
  name: I18nText;
  category: ServiceCategory;
  summary: I18nText;
  description: I18nText;
  whoCanUse: I18nList;
  howToAccess: I18nList;
  source: { label: I18nText; url: string };
}

export const services: Service[] = [
  {
    slug: "pacs-membership",
    name: { en: "PACS Membership", te: "PACS సభ్యత్వం" },
    category: "membership",
    summary: { en: "Become a member of your village cooperative to access credit and services.", te: "అప్పు మరియు సేవలకు ప్రాప్యత పొందడానికి మీ గ్రామ సహకార సంస్థలో సభ్యుడిగా చేరండి." },
    description:
      { en: "Joining your Primary Agricultural Credit Society gives you access to affordable credit, storage, inputs and a channel to raise grievances.", te: "మీ ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీలో చేరడం వల్ల సరసమైన అప్పు, నిల్వ, ఇన్‌పుట్‌లు మరియు ఫిర్యాదులు తెలియజేయడానికి ఒక మార్గం లభిస్తుంది." },
    whoCanUse: { en: ["Residents of the PACS area of operation.", "Landowners, tenant farmers and sharecroppers."], te: ["PACS కార్యకలాపాల ప్రాంతంలో నివసించేవారు.", "భూయజమానులు, కౌలు రైతులు మరియు భాగస్వామి రైతులు."] },
    howToAccess: { en: ["Visit your local PACS office.", "Submit identity and residence documents.", "Pay the share/entrance fee."], te: ["మీ స్థానిక PACS కార్యాలయాన్ని సందర్శించండి.", "గుర్తింపు మరియు నివాస పత్రాలను సమర్పించండి.", "షేర్ / అడ్మిషన్ రుసుము చెల్లించండి."] },
    source: { label: { en: "PACS / Cooperative Department", te: "PACS / సహకార శాఖ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "short-term-crop-credit",
    name: { en: "Short-term Crop Credit", te: "స్వల్పకాలిక పంట రుణం" },
    category: "credit",
    summary: { en: "Seasonal crop loans at subsidised interest to fund sowing to harvest.", te: "విత్తనం నుండి పంటకోత వరకు నిధుల కోసం సబ్సిడీ వడ్డీతో సీజనల్ పంట రుణాలు." },
    description:
      { en: "Short-term crop loans cover cultivation costs and are repaid after harvest, often with interest subvention for timely repayment.", te: "స్వల్పకాలిక పంట రుణాలు సాగు ఖర్చులను భరిస్తాయి మరియు పంటకోత తర్వాత తిరిగి చెల్లించబడతాయి, తరచుగా సకాలంలో తిరిగి చెల్లింపుకు వడ్డీ సబ్సిడీ ఉంటుంది." },
    whoCanUse: { en: ["Member farmers of a PACS or cooperative credit institution."], te: ["PACS లేదా సహకార క్రెడిట్ సంస్థల సభ్యులు."] },
    howToAccess: { en: ["Apply at your PACS or bank with KCC application.", "Provide land, identity and crop-cycle details."], te: ["KCC దరఖాస్తుతో మీ PACS లేదా బ్యాంకు వద్ద దరఖాస్తు చేయండి.", "భూమి, గుర్తింపు మరియు పంట చక్ర వివరాలను అందించండి."] },
    source: { label: { en: "PACS / Bank", te: "PACS / బ్యాంకు" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "godown-storage",
    name: { en: "Godown & Storage", te: "గోదాము & నిల్వ" },
    category: "storage",
    summary: { en: "Safe storage of produce to avoid distress sales and improve bargaining.", te: "నిర్బంధ విక్రయాలను నివారించడానికి మరియు బేరసారాలు మెరుగుపరచడానికి ఉత్పత్తిని సురక్షితంగా నిల్వ చేయడం." },
    description:
      { en: "PACS and cooperative unions operate godowns where members can store grain and produce, and access pledge loans against stock.", te: "PACS మరియు సహకార సంఘాలు గోదాములను నిర్వహిస్తాయి, ఇక్కడ సభ్యులు ధాన్యం మరియు ఉత్పత్తిని నిల్వ చేయవచ్చు, మరియు స్టాక్‌కు వ్యతిరేకంగా తాకట్టు రుణాలు పొందవచ్చు." },
    whoCanUse: { en: ["Member farmers with stored produce.", "Producers holding warehouses/pledge receipts."], te: ["నిల్వ చేసిన ఉత్పత్తితో ఉన్న సభ్య రైతులు.", "గోదాము / తాకట్టు రసీదులు కలిగిన ఉత్పత్తిదారులు."] },
    howToAccess: { en: ["Register storage at your nearest PACS godown.", "Obtain a warehouse receipt to pledge for a loan."], te: ["మీ సమీప PACS గోదాములో నిల్వను నమోదు చేయండి.", "రుణం కోసం తాకట్టు పెట్టడానికి గోదాము రసీదు పొందండి."] },
    source: { label: { en: "PACS / Warehousing", te: "PACS / గోదాము" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "agro-input-supply",
    name: { en: "Agro-input Supply", te: "వ్యవసాయ ఇన్‌పుట్ సరఫరా" },
    category: "agro-inputs",
    summary: { en: "Seeds, fertilisers and farm equipment supplied through the cooperative.", te: "సహకార సంస్థ ద్వారా విత్తనాలు, ఎరువులు మరియు వ్యవసాయ పరికరాల సరఫరా." },
    description:
      { en: "PACS supply certified seeds, fertilisers, pesticides and farm equipment in bulk to members at fair prices.", te: "PACS ధృవీకరించిన విత్తనాలు, ఎరువులు, పురుగుమందులు మరియు వ్యవసాయ పరికరాలను సభ్యులకు సరసమైన ధరలకు టోకుగా సరఫరా చేస్తాయి." },
    whoCanUse: { en: ["PACS member farmers.", "Village residents in the society's area."], te: ["PACS సభ్య రైతులు.", "సొసైటీ ప్రాంతంలోని గ్రామ నివాసులు."] },
    howToAccess: { en: ["Place a request at the PACS sale counter or branches.", "Pay against the invoice and collect inputs."], te: ["PACS అమ్మకపు కౌంటర్ లేదా శాఖల్లో అభ్యర్థన ఉంచండి.", "ఇన్వాయిస్‌కు వ్యతిరేకంగా చెల్లించి ఇన్‌పుట్‌లను సేకరించండి."] },
    source: { label: { en: "PACS / Agro-supply", te: "PACS / వ్యవసాయ సరఫరా" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "pmfby-enrolment",
    name: { en: "PMFBY Enrolment", te: "PMFBY నమోదు" },
    category: "insurance",
    summary: { en: "Enrol in crop insurance under PMFBY through your cooperative or CSC.", te: "మీ సహకార సంస్థ లేదా CSC ద్వారా PMFBY కింద పంట బీమాలో నమోదు చేయండి." },
    description:
      { en: "Pradhan Mantri Fasal Bima Yojana protects farmers against crop loss. PACS, banks and CSCs act as enrolment and claim-filing channels.", te: "ప్రధాన మంత్రి ఫసల్ బీమా యోజన రైతులను పంట నష్టం నుండి రక్షిస్తుంది. PACS, బ్యాంకులు మరియు CSCలు నమోదు మరియు దావా దాఖలు మార్గాలుగా పనిచేస్తాయి." },
    whoCanUse: { en: ["All farmers, loanee and non-loanee, within notified areas."], te: ["నోటిఫై చేసిన ప్రాంతాల్లో అందరు రైతులు — అప్పు తీసుకున్నవారు మరియు తీసుకోనివారు."] },
    howToAccess: { en: ["Sign a consent letter before the season deadline.", "Enrol at PACS / CSC / bank and keep land records."], te: ["సీజన్ గడువుకు ముందు సమ్మతి పత్రంపై సంతకం చేయండి.", "PACS / CSC / బ్యాంకులో నమోదు చేయండి మరియు భూ రికార్డులను ఉంచండి."] },
    source: { label: { en: "PMFBY", te: "PMFBY" }, url: "https://pmfby.gov.in" },
  },
  {
    slug: "cooperative-subsidy",
    name: { en: "Cooperative Subsidy", te: "సహకార సబ్సిడీ" },
    category: "subsidy",
    summary: { en: "Capital, interest and infrastructure subsidies for farmer cooperatives.", te: "రైతు సహకార సంస్థలకు మూలధన, వడ్డీ మరియు మౌలిక సదుపాయ సబ్సిడీలు." },
    description:
      { en: "The Ministry of Cooperation and allies run subsidy schemes for cooperative infrastructure — godowns, processing units and interest subvention.", te: "సహకార మంత్రిత్వ శాఖ మరియు అనుబంధ సంస్థలు సహకార మౌలిక సదుపాయాల కోసం సబ్సిడీ పథకాలను నిర్వహిస్తాయి — గోదాములు, ప్రాసెసింగ్ యూనిట్లు మరియు వడ్డీ సబ్సిడీ." },
    whoCanUse: { en: ["Registered cooperatives / PACS within scheme scope.", "Farmers applying through eligible cooperative channels."], te: ["పథకం పరిధిలో నమోదైన సహకార సంస్థలు / PACS.", "అర్హత గల సహకార మార్గాల ద్వారా దరఖాస్తు చేసే రైతులు."] },
    howToAccess: { en: ["Check eligibility against current guidelines.", "Submit the application via the portal or nodal office."], te: ["ప్రస్తుత మార్గదర్శకాల ప్రకారం అర్హతను తనిఖీ చేయండి.", "పోర్టల్ ద్వారా లేదా నోడల్ కార్యాలయం ద్వారా దరఖాస్తును సమర్పించండి."] },
    source: { label: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ" }, url: "https://www.moc.gov.in" },
  },
];

export interface LocalizedService {
  slug: string;
  category: ServiceCategory;
  name: string;
  summary: string;
  description: string;
  whoCanUse: string[];
  howToAccess: string[];
  source: { label: string; url: string };
}

function localizeService(s: Service, locale: Locale): LocalizedService {
  return {
    slug: s.slug,
    category: s.category,
    name: localize(s.name, locale),
    summary: localize(s.summary, locale),
    description: localize(s.description, locale),
    whoCanUse: localizeList(s.whoCanUse, locale),
    howToAccess: localizeList(s.howToAccess, locale),
    source: { label: localize(s.source.label, locale), url: s.source.url },
  };
}

export function getServices(locale: Locale): LocalizedService[] {
  return services.map((s) => localizeService(s, locale));
}
export function getService(locale: Locale, slug: string): LocalizedService | undefined {
  const found = services.find((s) => s.slug === slug);
  if (!found) return undefined;
  return localizeService(found, locale);
}
