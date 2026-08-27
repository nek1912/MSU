import type { Locale } from "@/lib/i18n/i18n";
import { localize, localizeList, type I18nList, type I18nText } from "./i18n";

export type LegalCategory = "act" | "bye-laws" | "provisions";

export interface LegalDoc {
  slug: string;
  title: I18nText;
  badge: I18nText;
  category: LegalCategory;
  overview: I18nText;
  keyProvisions: I18nList;
  applicability: I18nList;
  byLaws: I18nList;
  source: { label: I18nText; url: string };
}

export const legalDocs: LegalDoc[] = [
  {
    slug: "mscs-act-2002",
    title: { en: "Multi-State Cooperative Societies Act, 2002", te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002" },
    badge: { en: "MSCS Act 2002", te: "MSCS చట్టం 2002" },
    category: "act",
    overview: {
      en: "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies that operate across more than one state in India. It sets out the legal framework for their registration, management, elections, and governance.",
      te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002 భారతదేశంలో ఒకటి కంటే ఎక్కువ రాష్ట్రాల్లో పనిచేసే సహకార సొసైటీలను నియంత్రిస్తుంది. ఇది వాటి నమోదు, నిర్వహణ, ఎన్నికలు మరియు పాలన కోసం చట్టపరమైన ఫ్రేమ్‌వర్క్‌ను నిర్దేశిస్తుంది.",
    },
    keyProvisions: {
      en: [
        "Registration of multi-state cooperative societies with the Central Registrar.",
        "Membership rights and representation across member states.",
        "Election of the board of directors and tenure of the board.",
        "Reserve fund, audits, and annual returns under the Act.",
      ],
      te: [
        "కేంద్ర రిజిస్ట్రార్‌తో మల్టీ-స్టేట్ సహకార సొసైటీల నమోదు.",
        "సభ్య రాష్ట్రాల్లో సభ్యత్వ హక్కులు మరియు ప్రాతినిధ్యం.",
        "డైరెక్టర్ల బోర్డు ఎన్నిక మరియు బోర్డు పదవీకాలం.",
        "చట్టం కింద రిజర్వ్ ఫండ్, ఆడిట్‌లు మరియు వార్షిక రిటర్న్‌లు.",
      ],
    },
    applicability: { en: ["Cooperative societies operating in two or more states."], te: ["రెండు లేదా అంతకంటే ఎక్కువ రాష్ట్రాల్లో పనిచేసే సహకార సొసైటీలు."] },
    byLaws: { en: ["Each society adopts its own by-laws consistent with the Act and its rules."], te: ["ప్రతి సొసైటీ చట్టం మరియు దాని నిబంధనలకు అనుగుణంగా తన స్వంత ఉప-నియమాలను అవలంబిస్తుంది."] },
    source: { label: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "model-pacs-bye-laws",
    title: { en: "Model Bye-laws of Primary Agricultural Credit Societies", te: "ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీల నమూనా ఉప-నియమాలు" },
    badge: { en: "Model PACS Bye-laws", te: "నమూనా PACS ఉప-నియమాలు" },
    category: "bye-laws",
    overview: {
      en: "The model bye-laws prescribe the standard constitution and operational rules for Primary Agricultural Credit Societies (PACS) — the village-level cooperatives that provide credit and farm services.",
      te: "నమూనా ఉప-నియమాలు ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీల (PACS) ప్రామాణిక రాజ్యాంగం మరియు కార్యాచరణ నిబంధనలను నిర్దేశిస్తాయి — ఇవి అప్పు మరియు వ్యవసాయ సేవలు అందించే గ్రామ స్థాయి సహకార సంస్థలు.",
    },
    keyProvisions: {
      en: [
        "Eligibility and procedure for membership, share capital and entrance fees.",
        "Powers and duties of the board of directors.",
        "Conduct of general body meetings and voting rights.",
        "Appointment of the secretary and staff.",
      ],
      te: [
        "సభ్యత్వం, షేర్ మూలధనం మరియు అడ్మిషన్ రుసుములకు అర్హత మరియు విధానం.",
        "డైరెక్టర్ల బోర్డు అధికారాలు మరియు విధులు.",
        "సాధారణ సభా సమావేశాల నిర్వహణ మరియు ఓటింగ్ హక్కులు.",
        "సెక్రటరీ మరియు సిబ్బంది నియామకం.",
      ],
    },
    applicability: {
      en: [
        "New and existing PACS that adopt the model bye-laws or a state-approved variant.",
      ],
      te: [
        "నమూనా ఉప-నియమాలను లేదా రాష్ట్ర-ఆమోదించిన వైవిధ్యాన్ని అవలంబించే కొత్త మరియు ఇప్పటికే ఉన్న PACS.",
      ],
    },
    byLaws: {
      en: [
        "Borrowing limits and lending rules for members.",
        "Formation of sub-committees for loans, audit and grievances.",
      ],
      te: [
        "సభ్యులకు అప్పు తీసుకునే పరిమితులు మరియు రుణ నిబంధనలు.",
        "రుణాలు, ఆడిట్ మరియు ఫిర్యాదుల కోసం ఉప-కమిటీల ఏర్పాటు.",
      ],
    },
    source: { label: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "board-election-rules",
    title: { en: "Election of Board of Directors — MSCS Rules, 2011", te: "డైరెక్టర్ల బోర్డు ఎన్నిక — MSCS నిబంధనలు, 2011" },
    badge: { en: "Board Elections", te: "బోర్డు ఎన్నికలు" },
    category: "provisions",
    overview: {
      en: "The MSCS Rules, 2011 detail how the board of a multi-state cooperative society is elected, including the role of the election authority, the electoral college and the election timetable.",
      te: "MSCS నిబంధనలు, 2011 మల్టీ-స్టేట్ సహకార సొసైటీ బోర్డు ఎలా ఎన్నుకోబడుతుందో వివరంగా నిర్దేశిస్తాయి, ఇందులో ఎన్నికల అథారిటీ పాత్ర, ఎలక్టోరల్ కాలేజ్ మరియు ఎన్నికల సమయపట్టిక ఉన్నాయి.",
    },
    keyProvisions: {
      en: [
        "Appointment of an election authority to conduct elections.",
        "Preparation and certification of the electoral college.",
        "Dates for the e-election/ballot and counting of votes.",
      ],
      te: [
        "ఎన్నికలు నిర్వహించడానికి ఎన్నికల అథారిటీ నియామకం.",
        "ఎలక్టోరల్ కాలేజీ తయారీ మరియు ధృవీకరణ.",
        "ఇ-ఎన్నిక / బ్యాలెట్ మరియు ఓట్ల లెక్కింపు తేదీలు.",
      ],
    },
    applicability: { en: ["Multi-state cooperative societies governed by MSCS Rules, 2011."], te: ["MSCS నిబంధనలు, 2011 ద్వారా నియంత్రించబడే మల్టీ-స్టేట్ సహకార సొసైటీలు."] },
    byLaws: { en: ["Society bye-laws set the size and composition of the board."], te: ["సొసైటీ ఉప-నియమాలు బోర్డు పరిమాణం మరియు కూర్పును నిర్దేశిస్తాయి."] },
    source: { label: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "cooperative-disputes",
    title: { en: "Cooperative Dispute Resolution", te: "సహకార వివాద పరిష్కారం" },
    badge: { en: "Disputes", te: "వివాదాలు" },
    category: "provisions",
    overview: {
      en: "Disputes between a cooperative and its members — over loans, share capital, or by-law obligations — are resolved through arbitration or a cooperative dispute authority, not regular civil courts.",
      te: "సహకార సంస్థ మరియు దాని సభ్యుల మధ్య వివాదాలు — రుణాలు, షేర్ మూలధనం, లేదా ఉప-నియమ బాధ్యతలపై — సాధారణ సివిల్ కోర్టులకు కాకుండా మధ్యవర్తిత్వం లేదా సహకార వివాద అథారిటీ ద్వారా పరిష్కరించబడతాయి.",
    },
    keyProvisions: {
      en: [
        "Matters that are deemed disputes under the Act.",
        "Reference of disputes to arbitration or a designated authority.",
        "Enforceability of arbitration awards.",
      ],
      te: [
        "చట్టం కింద వివాదాలుగా పరిగణించబడే విషయాలు.",
        "మధ్యవర్తిత్వం లేదా నియమిత అథారిటీకి వివాదాలను సూచించడం.",
        "మధ్యవర్తిత్వ తీర్పుల అమలు సాధ్యత.",
      ],
    },
    applicability: { en: ["Members, former members and cooperatives facing internal disputes."], te: ["అంతర్గత వివాదాలను ఎదుర్కొంటున్న సభ్యులు, మాజీ సభ్యులు మరియు సహకార సంస్థలు."] },
    byLaws: { en: ["By-laws may prescribe an internal grievance-cum-dispute resolution committee."], te: ["ఉప-నియమాలు అంతర్గత ఫిర్యాదు-సహిత-వివాద పరిష్కార కమిటీని నిర్దేశించవచ్చు."] },
    source: { label: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "pac-model-bye-laws-moc",
    title: { en: "Model Bye-laws for PACS — Ministry of Cooperation", te: "PACS కోసం నమూనా ఉప-నియమాలు — సహకార మంత్రిత్వ శాఖ" },
    badge: { en: "PACS Bye-laws (MoC)", te: "PACS ఉప-నియమాలు (MoC)" },
    category: "bye-laws",
    overview: {
      en: "The Ministry of Cooperation's revised model bye-laws modernise PACS — enabling them to provide banking, storage, and agro-services while keeping their village-level cooperative character.",
      te: "సహకార మంత్రిత్వ శాఖ సవరించిన నమూనా ఉప-నియమాలు PACSలను ఆధునికీకరిస్తాయి — వాటి గ్రామ స్థాయి సహకార లక్షణాన్ని కొనసాగిస్తూనే బ్యాంకింగ్, నిల్వ మరియు వ్యవసాయ సేవలను అందించేలా చేస్తాయి.",
    },
    keyProvisions: {
      en: [
        "Minimum and maximum share capital for members.",
        "Wider business activities beyond lending (storage, insurance, IT services).",
        "Digital operational requirements and record-keeping.",
      ],
      te: [
        "సభ్యులకు కనిష్ట మరియు గరిష్ట షేర్ మూలధనం.",
        "రుణం ఇవ్వడం కంటే విస్తృతమైన వ్యాపార కార్యకలాపాలు (నిల్వ, బీమా, IT సేవలు).",
        "డిజిటల్ కార్యాచరణ అవసరాలు మరియు రికార్డు నిర్వహణ.",
      ],
    },
    applicability: { en: ["PACS registered under the cooperative law of the state."], te: ["రాష్ట్ర సహకార చట్టం కింద నమోదైన PACS."] },
    byLaws: { en: ["Fees, dividends and reserve allocations set in the bye-laws."], te: ["ఉప-నియమాలలో నిర్దేశించిన రుసుములు, డివిడెండ్‌లు మరియు రిజర్వు కేటాయింపులు."] },
    source: { label: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ" }, url: "https://www.moc.gov.in" },
  },
];

export interface LocalizedLegalDoc {
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

export function getLegalDocs(locale: Locale): LocalizedLegalDoc[] {
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
export function getLegalDoc(locale: Locale, slug: string): LocalizedLegalDoc | undefined {
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
