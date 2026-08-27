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
  { id: "l1", title: { en: "Pradhan Mantri Fasal Bima Yojana — Operational Guidelines", te: "ప్రధాన మంత్రి ఫసల్ బీమా యోజన — కార్యాచరణ మార్గదర్శకాలు", kn: "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬೀಮಾ ಯೋಜನೆ — ಕಾರ್ಯಾಚರಣೆ ಮಾರ್ಗಸೂಚಿಗಳು" }, source: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, page: 12, url: "https://pmfby.gov.in", domain: "cropInsurance", publishedAt: "2025-04-02" },
  { id: "l2", title: { en: "Model Bye-laws of Primary Agricultural Credit Societies", te: "ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీల నమూనా ఉప-నియమాలు", kn: "ಪ್ರಾಥಮಿಕ ಕೃಷಿ ಕ್ರೆಡಿಟ್ ಸೊಸೈಟಿಗಳ ಮಾದರಿ ಉಪ-ನಿಯಮಗಳು" }, source: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, page: 6, url: "https://www.moc.gov.in", domain: "law", publishedAt: "2024-11-18" },
  { id: "l3", title: { en: "Multi-State Cooperative Societies Act, 2002 — Key Provisions", te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002 — ప్రధాన నిబంధనలు", kn: "ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಗಳ ಕಾಯಿದೆ, 2002 — ಮುಖ್ಯ ನಿಬಂಧನೆಗಳು" }, source: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, page: 24, url: "https://www.moc.gov.in", domain: "law", publishedAt: "2024-08-30" },
  { id: "l4", title: { en: "Kisan Credit Card — Scheme Guidelines", te: "కిసాన్ క్రెడిట్ కార్డు — పథకం మార్గదర్శకాలు", kn: "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ — ಯೋಜನಾ ಮಾರ್ಗಸೂಚಿಗಳು" }, source: { en: "NABARD", te: "NABARD", kn: "NABARD" }, page: 8, url: "https://www.nabard.org", domain: "financial", publishedAt: "2025-01-21" },
  { id: "l5", title: { en: "Grievance Redressal Mechanism for Cooperative Societies", te: "సహకార సొసైటీల కోసం ఫిర్యాదుల పరిష్కార విధానం", kn: "ಸಹಕಾರ ಸೊಸೈಟಿಗಳಿಗೆ ದೂರು ಪರಿಹಾರ ವ್ಯವಸ್ಥೆ" }, source: { en: "Ministry of Cooperation", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸచಿವಾಲಯ" }, page: 4, url: "https://www.moc.gov.in", domain: "grievance", publishedAt: "2025-02-11" },
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
