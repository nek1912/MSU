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
    question: { en: "What is PMFBY crop insurance?", te: "PMFBY పంట బీమా అంటే ఏమిటి?", kn: "PMFBY ಬೆಳೆ ವಿಮೆ ಎಂದರೇನು?" },
    answer:
      { en: "PMFBY (Pradhan Mantri Fasal Bima Yojana) is a crop insurance scheme. Farmers pay a small premium and the rest is subsidised by the government, covering crop loss from natural calamities, pests and diseases.", te: "PMFBY (ప్రధాన మంత్రి ఫసల్ బీమా యోజన) అనేది పంట బీమా పథకం. రైతులు చిన్న ప్రీమియం చెల్లిస్తారు, మిగిలిన మొత్తాన్ని ప్రభుత్వం సబ్సిడీ చేస్తుంది, ఇది ప్రకృతి వైపరీత్యాలు, పీడలు మరియు వ్యాధుల వల్ల పంట నష్టాన్ని కవర్ చేస్తుంది.", kn: "PMFBY (ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬೀಮಾ ಯೋಜನೆ) ಒಂದು ಬೆಳೆ ವಿಮಾ ಯೋಜನೆಯಾಗಿದೆ. ರೈತರು ಸಣ್ಣ ಪ್ರೀಮಿಯಂ ಪಾವತಿಸುತ್ತಾರೆ, ಉಳಿದ ಮೊತ್ತವನ್ನು ಸರ್ಕಾರ ಸಬ್ಸಿಡಿ ಮಾಡುತ್ತದೆ, ಇದು ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳು, ಪೀಡೆಗಳು ಮತ್ತು ರೋಗಗಳಿಂದ ಆಗುವ ಬೆಳೆ ನಷ್ಟವನ್ನು ರಕ್ಷಿಸುತ್ತದೆ." },
  },
  {
    id: "f2",
    category: "crop-insurance",
    question: { en: "How do I claim under PMFBY?", te: "PMFBY కింద నేను ఎలా దావా వేయాలి?", kn: "PMFBY ಅಡಿ ನಾನು ಹೇಗೆ ದಾವೆ ಸಲ್ಲಿಸುವುದು?" },
    answer:
      { en: "File a claim before the deadline at your PACS, bank, or CSC with land records and sowing details. Compensation is disbursed after assessment of the insured crop loss.", te: "గడువుకు ముందు మీ PACS, బ్యాంకు లేదా CSC వద్ద భూ రికార్డులు మరియు విత్తన వివరాలతో దావా దాఖలు చేయండి. బీమా చేయబడిన పంట నష్టాన్ని అంచనా వేసిన తర్వాత పరిహారం విడుదల చేయబడుతుంది.", kn: "ಗಡುವಿಗೆ ಮೊದಲು ನಿಮ್ಮ PACS, ಬ್ಯಾಂಕ್, ಅಥವಾ CSC ನಲ್ಲಿ ಭೂ ದಾಖಲೆಗಳು ಮತ್ತು ಬಿತ್ತನೆ ವಿವರಗಳೊಂದಿಗೆ ದಾವೆ ದಾಖಲಿಸಿ. ವಿಮೆ ಮಾಡಿದ ಬೆಳೆ ನಷ್ಟವನ್ನು ಮೌಲ್ಯಮಾಪನ ಮಾಡಿದ ನಂತರ ಪರಿಹಾರವನ್ನು ವಿತರಿಸಲಾಗುತ್ತದೆ." },
  },
  {
    id: "f3",
    category: "pacs",
    question: { en: "How do I join a PACS as a member?", te: "సభ్యుడిగా నేను PACSలో ఎలా చేరాలి?", kn: "ಸದಸ್ಯರಾಗಿ ನಾನು PACS ಸೇರುವುದು ಹೇಗೆ?" },
    answer:
      { en: "Visit your local PACS office, fill the membership form, submit identity and residence documents, and pay the small share/entrance fee as notified.", te: "మీ స్థానిక PACS కార్యాలయానికి వెళ్లి, సభ్యత్వ ఫారం పూరించండి, గుర్తింపు మరియు నివాస పత్రాలను సమర్పించండి, మరియు నోటిఫై చేసిన ప్రకారం చిన్న షేర్ / అడ్మిషన్ రుసుము చెల్లించండి.", kn: "ನಿಮ್ಮ ಸ್ಥಳೀಯ PACS ಕಚೇರಿಗೆ ಭೇಟಿ ನೀಡಿ, ಸದಸ್ಯತ್ವ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಿ, ಗುರುತು ಮತ್ತು ನಿವಾಸ ದಾಖಲೆಗಳನ್ನು ಸಲ್ಲಿಸಿ, ಮತ್ತು ಪ್ರಕಟಿಸಿದಂತೆ ಸಣ್ಣ ಪಾಲು / ಪ್ರವೇಶ ಶುಲ್ಕ ಪಾವತಿಸಿ." },
  },
  {
    id: "f4",
    category: "pacs",
    question: { en: "What services does a PACS provide?", te: "PACS ఏ సేవలను అందిస్తుంది?", kn: "PACS ಯಾವ ಸೇವೆಗಳನ್ನು ಒದಗಿಸುತ್ತದೆ?" },
    answer:
      { en: "PACS provide short-term crop loans, storage/godown facilities, agro-inputs (seed, fertiliser, equipment), insurance enrolment and a channel to raise grievances.", te: "PACS స్వల్పకాలిక పంట రుణాలు, నిల్వ / గోదాము సౌకర్యాలు, వ్యవసాయ ఇన్‌పుట్‌లు (విత్తనం, ఎరువు, పరికరాలు), బీమా నమోదు మరియు ఫిర్యాదులు తెలియజేయడానికి ఒక మార్గాన్ని అందిస్తుంది.", kn: "PACS ಅಲ್ಪಾವಧಿಯ ಬೆಳೆ ಸಾಲಗಳು, ಶೇಖರಣೆ / ಗೋದಾಮು ಸೌಲಭ್ಯಗಳು, ಕೃಷಿ ಇನ್‌ಪುಟ್‌ಗಳು (ಬೀಜ, ಗೊಬ್ಬರ, ಉಪಕರಣ), ವಿಮೆ ನೋಂದಣಿ ಮತ್ತು ದೂರುಗಳನ್ನು ತಿಳಿಸಲು ಒಂದು ಮಾರ್ಗವನ್ನು ಒದಗಿಸುತ್ತದೆ." },
  },
  {
    id: "f5",
    category: "financial",
    question: { en: "What is a Kisan Credit Card (KCC)?", te: "కిసాన్ క్రెడిట్ కార్డు (KCC) అంటే ఏమిటి?", kn: "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಎಂದರೇನು?" },
    answer:
      { en: "The KCC is a crop credit card for farmers offering short-term credit at competitive rates, flexible repayment after harvest, and a personal accident insurance cover.", te: "KCC అనేది రైతుల కోసం పంట క్రెడిట్ కార్డు, ఇది పోటీ రేట్లలో స్వల్పకాలిక రుణం, పంటకోత తర్వాత సౌకర్యవంతమైన తిరిగి చెల్లింపు, మరియు వ్యక్తిగత ప్రమాద బీమా రక్షణను అందిస్తుంది.", kn: "KCC ರೈತರಿಗೆ ಬೆಳೆ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ಆಗಿದೆ, ಇದು ಸ್ಪರ್ಧಾತ್ಮಕ ದರಗಳಲ್ಲಿ ಅಲ್ಪಾವಧಿಯ ಸಾಲ, ಸುಗ್ಗಿಯ ನಂತರ ಸ್ಥಿತಿಸ್ಥಾಪಕ ಮರುಪಾವತಿ, ಮತ್ತು ವೈಯಕ್ತಿಕ ಅಪಘಾತ ವಿಮೆ ರಕ್ಷಣೆಯನ್ನು ಒದಗಿಸುತ್ತದೆ." },
  },
  {
    id: "f6",
    category: "financial",
    question: { en: "How can I improve my financial literacy?", te: "నా ఆర్థిక అక్షరాస్యతను నేను ఎలా మెరుగుపరచుకోగలను?", kn: "ನನ್ನ ಆರ್ಥಿಕ ಸಾಕ್ಷರತೆಯನ್ನು ನಾನು ಹೇಗೆ ಸುಧಾರಿಸಬಹುದು?" },
    answer:
      { en: "Attend village-level camps organised by PACS and banks, and ask this chatbot plain-language questions on savings, borrowing, insurance and safe digital banking.", te: "PACS మరియు బ్యాంకులు నిర్వహించే గ్రామ స్థాయి శిబిరాలకు హాజరవ్వండి, మరియు పొదుపు, అప్పు, బీమా మరియు సురక్షిత డిజిటల్ బ్యాంకింగ్ గురించి ఈ చాట్‌బాట్‌ను సరళమైన భాషలో ప్రశ్నలు అడగండి.", kn: "PACS ಮತ್ತು ಬ್ಯಾಂಕುಗಳು ಆಯೋಜಿಸುವ ಗ್ರಾಮ ಮಟ್ಟದ ಶಿಬಿರಗಳಿಗೆ ಹಾಜರಾಗಿ, ಮತ್ತು ಉಳಿತಾಯ, ಸಾಲ, ವಿಮೆ ಮತ್ತು ಸುರಕ್ಷಿತ ಡಿಜಿಟಲ್ ಬ್ಯಾಂಕಿಂಗ್ ಬಗ್ಗೆ ಈ ಚಾಟ್‌ಬಾಟ್‌ನನ್ನು ಸರಳ ಭಾಷೆಯಲ್ಲಿ ಪ್ರಶ್ನೆ ಕೇಳಿ." },
  },
  {
    id: "f7",
    category: "grievance",
    question: { en: "How do I complain about my cooperative?", te: "నా సహకార సంస్థ గురించి నేను ఎలా ఫిర్యాదు చేయాలి?", kn: "ನನ್ನ ಸಹಕಾರ ಸಂಸ್ಥೆಯ ಬಗ್ಗೆ ನಾನು ಹೇಗೆ ದೂರು ನೀಡುವುದು?" },
    answer:
      { en: "Use the Grievance page to file a complaint with a category and description. You will get an ID to track the status on the grievance status page.", te: "ఫిర్యాదు పేజీని ఉపయోగించి ఒక వర్గం మరియు వివరణతో ఫిర్యాదు దాఖలు చేయండి. ఫిర్యాదు స్థితి పేజీలో స్థితిని ట్రాక్ చేయడానికి మీకు ఒక ID లభిస్తుంది.", kn: "ವರ್ಗ ಮತ್ತು ವಿವರಣೆಯೊಂದಿಗೆ ದೂರು ದಾಖಲಿಸಲು ದೂರು ಪುಟವನ್ನು ಬಳಸಿ. ದೂರು ಸ್ಥಿತಿ ಪುಟದಲ್ಲಿ ಸ್ಥಿತಿಯನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಲು ನಿಮಗೆ ಒಂದು ID ಸಿಗುತ್ತದೆ." },
  },
  {
    id: "f8",
    category: "grievance",
    question: { en: "What categories of grievances can I raise?", te: "నేను ఏ వర్గాల ఫిర్యాదులను తెలియజేయగలను?", kn: "ನಾನು ಯಾವ ವರ್ಗದ ದೂರುಗಳನ್ನು ತಿಳಿಸಬಹುದು?" },
    answer:
      { en: "Grievances can belong to crop insurance / PMFBY, PACS service, scheme or subsidy, or other cooperative matters.", te: "ఫిర్యాదులు పంట బీమా / PMFBY, PACS సేవ, పథకం లేదా సబ్సిడీ, లేదా ఇతర సహకార విషయాలకు సంబంధించినవి కావచ్చు.", kn: "ದೂರುಗಳು ಬೆಳೆ ವಿಮೆ / PMFBY, PACS ಸೇವೆ, ಯೋಜನೆ ಅಥವಾ ಸಬ್ಸಿಡಿ, ಅಥವಾ ಇತರ ಸಹಕಾರ ವಿಷಯಗಳಿಗೆ ಸೇರಿರಬಹುದು." },
  },
  {
    id: "f9",
    category: "legal",
    question: { en: "Which law governs multi-state cooperatives?", te: "మల్టీ-స్టేట్ సహకార సంస్థలను ఏ చట్టం నియంత్రిస్తుంది?", kn: "ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸಂಸ್ಥೆಗಳನ್ನು ಯಾವ ಕಾನೂನು ನಿಯಂತ್ರಿಸುತ್ತದೆ?" },
    answer:
      { en: "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies operating across more than one state.", te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002 ఒకటి కంటే ఎక్కువ రాష్ట్రాల్లో పనిచేసే సహకార సొసైటీలను నియంత్రిస్తుంది.", kn: "ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಗಳ ಕಾಯಿದೆ, 2002 ಒಂದಕ್ಕಿಂತ ಹೆಚ್ಚು ರాజ್ಯಗಳಲ್ಲಿ ಕಾರ್ಯನಿರ್ವಹಿಸುವ ಸಹಕಾರ ಸೊಸೈಟಿಗಳನ್ನು ನಿಯಂತ್ರಿಸುತ್ತದೆ." },
  },
  {
    id: "f10",
    category: "legal",
    question: { en: "How are cooperative disputes resolved?", te: "సహకార వివాదాలు ఎలా పరిష్కరించబడతాయి?", kn: "ಸಹಕಾರ ವಿವಾದಗಳನ್ನು ಹೇಗೆ ಪರಿಹರಿಸಲಾಗುತ್ತದೆ?" },
    answer:
      { en: "Disputes between a cooperative and its members are resolved through arbitration or a designated dispute authority, not regular civil courts.", te: "సహకార సంస్థ మరియు దాని సభ్యుల మధ్య వివాదాలు సాధారణ సివిల్ కోర్టులకు కాకుండా మధ్యవర్తిత్వం లేదా నియమిత వివాద అథారిటీ ద్వారా పరిష్కరించబడతాయి.", kn: "ಸಹಕಾರ ಸಂಸ್ಥೆ ಮತ್ತು ಅದರ ಸದಸ್ಯರ ನಡುವಿನ ವಿವಾದಗಳನ್ನು ಸಾಮಾನ್ಯ ನಾಗರಿಕ ನ್ಯಾಯಾಲಯಗಳಿಗಿಂತ ಮಧ್ಯಸ್ಥಿಕೆ ಅಥವಾ ನಿಯೋಜಿತ ವಿವಾದ ಪ್ರಾಧಿಕಾರದ ಮೂಲಕ ಪರಿಹರಿಸಲಾಗುತ್ತದೆ." },
  },
  {
    id: "f11",
    category: "legal",
    question: { en: "What are a cooperative society's by-laws?", te: "ఒక సహకార సొసైటీ యొక్క ఉప-నియమాలు ఏమిటి?", kn: "ಸಹಕಾರ ಸೊಸೈಟಿಯ ಉಪ-ನಿಯಮಗಳು ಎಂದರೇನು?" },
    answer:
      { en: "By-laws are the society's internal rulebook covering membership, share capital, board powers, meetings and business activities, consistent with the governing Act.", te: "ఉప-నియమాలు అనేవి సొసైటీ యొక్క అంతర్గత నియమావళి, ఇవి సభ్యత్వం, షేర్ మూలధనం, బోర్డు అధికారాలు, సమావేశాలు మరియు వ్యాపార కార్యకలాపాలను కవర్ చేస్తాయి, నియంత్రణ చట్టానికి అనుగుణంగా ఉంటాయి.", kn: "ಉಪ-ನಿಯಮಗಳು ಸೊಸೈಟಿಯ ಆಂತರಿಕ ನಿಯಮಗಳ ಪುಸ್ತಕವಾಗಿದ್ದು, ಸದಸ್ಯತ್ವ, ಪಾಲು ಬಂಡವಾಳ, ಮಂಡಳಿ ಅಧಿಕಾರಗಳು, ಸಭೆಗಳು ಮತ್ತು ವ್ಯಾಪಾರ ಚಟುವಟಿಕೆಗಳನ್ನು ಒಳಗೊಳ್ಳುತ್ತದೆ, ಆಡಳಿತಾತ್ಮಕ ಕಾಯಿದೆಗೆ ಅನುಗುಣವಾಗಿ." },
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
