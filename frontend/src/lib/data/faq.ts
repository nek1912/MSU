import type { Locale } from "@/lib/i18n/i18n";
import { localize, type I18nText } from "./i18n";

export type FaqCategory = "crop-insurance" | "pacs" | "financial" | "grievance" | "legal";

export interface FaqItem {
  id: string;
  category: FaqCategory;
  question: I18nText;
  answer: I18nText;
}

export const faqItems: FaqItem[] = [
  {
    id: "f1",
    category: "crop-insurance",
    question: { en: "What is PMFBY crop insurance?", te: "PMFBY పంట బీమా అంటే ఏమిటి?" },
    answer:
      { en: "PMFBY (Pradhan Mantri Fasal Bima Yojana) is a crop insurance scheme. Farmers pay a small premium and the rest is subsidised by the government, covering crop loss from natural calamities, pests and diseases.", te: "PMFBY (ప్రధాన మంత్రి ఫసల్ బీమా యోజన) అనేది పంట బీమా పథకం. రైతులు చిన్న ప్రీమియం చెల్లిస్తారు, మిగిలిన మొత్తాన్ని ప్రభుత్వం సబ్సిడీ చేస్తుంది, ఇది ప్రకృతి వైపరీత్యాలు, పీడలు మరియు వ్యాధుల వల్ల పంట నష్టాన్ని కవర్ చేస్తుంది." },
  },
  {
    id: "f2",
    category: "crop-insurance",
    question: { en: "How do I claim under PMFBY?", te: "PMFBY కింద నేను ఎలా దావా వేయాలి?" },
    answer:
      { en: "File a claim before the deadline at your PACS, bank, or CSC with land records and sowing details. Compensation is disbursed after assessment of the insured crop loss.", te: "గడువుకు ముందు మీ PACS, బ్యాంకు లేదా CSC వద్ద భూ రికార్డులు మరియు విత్తన వివరాలతో దావా దాఖలు చేయండి. బీమా చేయబడిన పంట నష్టాన్ని అంచనా వేసిన తర్వాత పరిహారం విడుదల చేయబడుతుంది." },
  },
  {
    id: "f3",
    category: "pacs",
    question: { en: "How do I join a PACS as a member?", te: "సభ్యుడిగా నేను PACSలో ఎలా చేరాలి?" },
    answer:
      { en: "Visit your local PACS office, fill the membership form, submit identity and residence documents, and pay the small share/entrance fee as notified.", te: "మీ స్థానిక PACS కార్యాలయానికి వెళ్లి, సభ్యత్వ ఫారం పూరించండి, గుర్తింపు మరియు నివాస పత్రాలను సమర్పించండి, మరియు నోటిఫై చేసిన ప్రకారం చిన్న షేర్ / అడ్మిషన్ రుసుము చెల్లించండి." },
  },
  {
    id: "f4",
    category: "pacs",
    question: { en: "What services does a PACS provide?", te: "PACS ఏ సేవలను అందిస్తుంది?" },
    answer:
      { en: "PACS provide short-term crop loans, storage/godown facilities, agro-inputs (seed, fertiliser, equipment), insurance enrolment and a channel to raise grievances.", te: "PACS స్వల్పకాలిక పంట రుణాలు, నిల్వ / గోదాము సౌకర్యాలు, వ్యవసాయ ఇన్‌పుట్‌లు (విత్తనం, ఎరువు, పరికరాలు), బీమా నమోదు మరియు ఫిర్యాదులు తెలియజేయడానికి ఒక మార్గాన్ని అందిస్తుంది." },
  },
  {
    id: "f5",
    category: "financial",
    question: { en: "What is a Kisan Credit Card (KCC)?", te: "కిసాన్ క్రెడిట్ కార్డు (KCC) అంటే ఏమిటి?" },
    answer:
      { en: "The KCC is a crop credit card for farmers offering short-term credit at competitive rates, flexible repayment after harvest, and a personal accident insurance cover.", te: "KCC అనేది రైతుల కోసం పంట క్రెడిట్ కార్డు, ఇది పోటీ రేట్లలో స్వల్పకాలిక రుణం, పంటకోత తర్వాత సౌకర్యవంతమైన తిరిగి చెల్లింపు, మరియు వ్యక్తిగత ప్రమాద బీమా రక్షణను అందిస్తుంది." },
  },
  {
    id: "f6",
    category: "financial",
    question: { en: "How can I improve my financial literacy?", te: "నా ఆర్థిక అక్షరాస్యతను నేను ఎలా మెరుగుపరచుకోగలను?" },
    answer:
      { en: "Attend village-level camps organised by PACS and banks, and ask this chatbot plain-language questions on savings, borrowing, insurance and safe digital banking.", te: "PACS మరియు బ్యాంకులు నిర్వహించే గ్రామ స్థాయి శిబిరాలకు హాజరవ్వండి, మరియు పొదుపు, అప్పు, బీమా మరియు సురక్షిత డిజిటల్ బ్యాంకింగ్ గురించి ఈ చాట్‌బాట్‌ను సరళమైన భాషలో ప్రశ్నలు అడగండి." },
  },
  {
    id: "f7",
    category: "grievance",
    question: { en: "How do I complain about my cooperative?", te: "నా సహకార సంస్థ గురించి నేను ఎలా ఫిర్యాదు చేయాలి?" },
    answer:
      { en: "Use the Grievance page to file a complaint with a category and description. You will get an ID to track the status on the grievance status page.", te: "ఫిర్యాదు పేజీని ఉపయోగించి ఒక వర్గం మరియు వివరణతో ఫిర్యాదు దాఖలు చేయండి. ఫిర్యాదు స్థితి పేజీలో స్థితిని ట్రాక్ చేయడానికి మీకు ఒక ID లభిస్తుంది." },
  },
  {
    id: "f8",
    category: "grievance",
    question: { en: "What categories of grievances can I raise?", te: "నేను ఏ వర్గాల ఫిర్యాదులను తెలియజేయగలను?" },
    answer:
      { en: "Grievances can belong to crop insurance / PMFBY, PACS service, scheme or subsidy, or other cooperative matters.", te: "ఫిర్యాదులు పంట బీమా / PMFBY, PACS సేవ, పథకం లేదా సబ్సిడీ, లేదా ఇతర సహకార విషయాలకు సంబంధించినవి కావచ్చు." },
  },
  {
    id: "f9",
    category: "legal",
    question: { en: "Which law governs multi-state cooperatives?", te: "మల్టీ-స్టేట్ సహకార సంస్థలను ఏ చట్టం నియంత్రిస్తుంది?" },
    answer:
      { en: "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies operating across more than one state.", te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002 ఒకటి కంటే ఎక్కువ రాష్ట్రాల్లో పనిచేసే సహకార సొసైటీలను నియంత్రిస్తుంది." },
  },
  {
    id: "f10",
    category: "legal",
    question: { en: "How are cooperative disputes resolved?", te: "సహకార వివాదాలు ఎలా పరిష్కరించబడతాయి?" },
    answer:
      { en: "Disputes between a cooperative and its members are resolved through arbitration or a designated dispute authority, not regular civil courts.", te: "సహకార సంస్థ మరియు దాని సభ్యుల మధ్య వివాదాలు సాధారణ సివిల్ కోర్టులకు కాకుండా మధ్యవర్తిత్వం లేదా నియమిత వివాద అథారిటీ ద్వారా పరిష్కరించబడతాయి." },
  },
  {
    id: "f11",
    category: "legal",
    question: { en: "What are a cooperative society's by-laws?", te: "ఒక సహకార సొసైటీ యొక్క ఉప-నియమాలు ఏమిటి?" },
    answer:
      { en: "By-laws are the society's internal rulebook covering membership, share capital, board powers, meetings and business activities, consistent with the governing Act.", te: "ఉప-నియమాలు అనేవి సొసైటీ యొక్క అంతర్గత నియమావళి, ఇవి సభ్యత్వం, షేర్ మూలధనం, బోర్డు అధికారాలు, సమావేశాలు మరియు వ్యాపార కార్యకలాపాలను కవర్ చేస్తాయి, నియంత్రణ చట్టానికి అనుగుణంగా ఉంటాయి." },
  },
];

export interface LocalizedFaqItem {
  id: string;
  category: FaqCategory;
  question: string;
  answer: string;
}

function localizeFaq(f: FaqItem, locale: Locale): LocalizedFaqItem {
  return {
    id: f.id,
    category: f.category,
    question: localize(f.question, locale),
    answer: localize(f.answer, locale),
  };
}

export function getFaqItems(locale: Locale): LocalizedFaqItem[] {
  return faqItems.map((f) => localizeFaq(f, locale));
}
