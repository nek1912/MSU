import type { Locale } from "@/lib/i18n/i18n";
import { localize, type I18nText } from "./i18n";

export interface LibraryDoc {
  id: string;
  title: I18nText;
  source: I18nText;
  page: number;
  url: string;
  domain: string;
  publishedAt: string;
}

export const libraryDocs: LibraryDoc[] = [
  { id: "l1", title: { en: "Pradhan Mantri Fasal Bima Yojana — Operational Guidelines", gu: "પ્રધાન મંત્રી ફસલ બીમા યોજના — કાર્યાચરણ માર્ગદર્શિકાઓ", pa: "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫਸਲ ਬੀਮਾ ਯੋਜਨਾ — ਕਾਰਜਸ਼ੀਲ ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼", te: "ప్రధాన మంత్రి ఫసల్ బీమా యోజన — కార్యాచరణ మార్గదర్శకాలు", kn: "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬೀಮಾ ಯೋಜನೆ — ಕಾರ್ಯಾಚರಣೆ ಮಾರ್ಗಸೂಚಿಗಳು", or: "ପ୍ରଧାନ ମନ୍ତ୍ରୀ ଫସଲ ବୀମା ଯୋଜନା — କାର୍ଯ୍ୟାଚରଣ ମାର୍ଗଦର୍ଶିକା" }, source: { en: "Ministry of Cooperation", gu: "સહકાર મંત્રાલય", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ", or: "ସହକାର ମନ୍ତ୍ରାଳୟ", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ" }, page: 12, url: "https://pmfby.gov.in", domain: "cropInsurance", publishedAt: "2025-04-02" },
  { id: "l2", title: { en: "Model Bye-laws of Primary Agricultural Credit Societies", gu: "પ્રાથમિક કૃષિ ક્રેડિટ સોસાયટીઓના મોડેલ ઉપ-નિયમો", pa: "ਪ੍ਰਾਇਮਰੀ ਐਗਰੀਕਲਚਰਲ ਕ੍ਰੈਡਿਟ ਸੋਸਾਇਟੀਆਂ ਦੇ ਨਮੂਨਾ ਉਪ-ਨਿਯਮ", te: "ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీల నమూనా ఉప-నియమాలు", kn: "ಪ್ರಾಥಮಿಕ ಕೃಷಿ ಕ್ರೆಡಿಟ್ ಸೊಸೈಟಿಗಳ ಮಾದರಿ ಉಪ-ನಿಯಮಗಳು", or: "ପ୍ରାଥମିକ କୃଷି କ୍ରେଡିଟ୍ ସୋସାଇଟିଗୁଡ଼ିକର ଆଦର୍ଶ ଉପ-ନିୟମ" }, source: { en: "Ministry of Cooperation", gu: "સહકાર મંત્રાલય", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ", or: "ସହକାର ମନ୍ତ୍ରାଳୟ", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ" }, page: 6, url: "https://www.moc.gov.in", domain: "law", publishedAt: "2024-11-18" },
  { id: "l3", title: { en: "Multi-State Cooperative Societies Act, 2002 — Key Provisions", gu: "મલ્ટી-રાજ્ય સહકારી સોસાયટી અધિનિયમ, 2002 — મુખ્ય જોગવાઈઓ", pa: "ਮਲਟੀ-ਸਟੇਟ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ ਐਕਟ, 2002 — ਮੁੱਖ ਪ੍ਰਬੰਧ", te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002 — ప్రధాన నిబంధనలు", kn: "ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಗಳ ಕಾಯಿದೆ, 2002 — ಮುಖ್ಯ ನಿಬಂಧನೆಗಳು", or: "ମଲ୍ଟି-ରାଜ୍ୟ ସହକାରୀ ସୋସାଇଟି ଅଧିନିୟମ, 2002 — ମୁଖ୍ୟ ନିବନ୍ଧନ" }, source: { en: "Ministry of Cooperation", gu: "સહકાર મંત્રાલય", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ", or: "ସହକାର ମନ୍ତ୍ରାଳୟ", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ" }, page: 24, url: "https://www.moc.gov.in", domain: "law", publishedAt: "2024-08-30" },
  { id: "l4", title: { en: "Kisan Credit Card — Scheme Guidelines", gu: "કિસાન ક્રેડિટ કાર્ડ — યોજના માર્ગદર્શિકાઓ", pa: "ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ — ਯੋਜਨਾ ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼", te: "కిసాన్ క్రెడిట్ కార్డు — పథకం మార్గదర్శకాలు", kn: "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ — ಯೋಜನಾ ಮಾರ್ಗಸೂಚಿಗಳು", or: "କିସାନ କ୍ରେଡିଟ୍ କାର୍ଡ — ଯୋଜନା ମାର୍ଗଦର୍ଶିକା" }, source: { en: "NABARD", gu: "NABARD", pa: "NABARD", te: "NABARD", kn: "NABARD", or: "NABARD" }, page: 8, url: "https://www.nabard.org", domain: "financial", publishedAt: "2025-01-21" },
  { id: "l5", title: { en: "Grievance Redressal Mechanism for Cooperative Societies", gu: "સહકારી સોસાયટીઓ માટે ફરિયાદ નિવારણ વ્યવસ્થા", pa: "ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ ਲਈ ਸ਼ਿਕਾਇਤ ਨਿਵਾਰਣ ਵਿਧੀ", te: "సహకార సొసైటీల కోసం ఫిర్యాదుల పరిష్కార విధానం", kn: "ಸಹಕಾರ ಸೊಸೈಟಿಗಳಿಗೆ ದೂರು ಪರಿಹಾರ ವ್ಯವಸ್ಥೆ", or: "ସହକାରୀ ସୋସାଇଟିଗୁଡ଼ିକ ପାଇଁ ଅଭିଯୋଗ ନିବାରଣ ବ୍ୟବସ୍ଥା" }, source: { en: "Ministry of Cooperation", gu: "સહકાર મંત્રાલય", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ", or: "ସହକାର ମନ୍ତ୍ରାଳୟ", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ" }, page: 4, url: "https://www.moc.gov.in", domain: "grievance", publishedAt: "2025-02-11" },
];

export interface LocalizedLibraryDoc {
  id: string;
  title: string;
  source: string;
  page: number;
  url: string;
  domain: string;
  publishedAt: string;
}

export function getLibraryDocs(locale: Locale): LocalizedLibraryDoc[] {
  return libraryDocs.map((d) => ({
    id: d.id,
    title: localize(d.title, locale),
    source: localize(d.source, locale),
    page: d.page,
    url: d.url,
    domain: d.domain,
    publishedAt: d.publishedAt,
  }));
}
