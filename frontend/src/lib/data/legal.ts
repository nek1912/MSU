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
    title: { en: "Multi-State Cooperative Societies Act, 2002", pa: "ਮਲਟੀ-ਸਟੇਟ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ ਐਕਟ, 2002", te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002", kn: "ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಗಳ ಕಾಯಿದೆ, 2002" },
    badge: { en: "MSCS Act 2002", pa: "MSCS ਐਕਟ 2002", te: "MSCS చట్టం 2002", kn: "MSCS ಕಾಯಿದೆ 2002" },
    category: "act",
    overview: {
      en: "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies that operate across more than one state in India. It sets out the legal framework for their registration, management, elections, and governance.",
      pa: "ਮਲਟੀ-ਸਟੇਟ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ ਐਕਟ, 2002 ਭਾਰਤ ਵਿੱਚ ਇੱਕ ਤੋਂ ਵੱਧ ਰਾਜਾਂ ਵਿੱਚ ਕੰਮ ਕਰਨ ਵਾਲੀਆਂ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ ਨੂੰ ਨਿਯੰਤ੍ਰਿਤ ਕਰਦਾ ਹੈ। ਇਹ ਉਨ੍ਹਾਂ ਦੀ ਰਜਿਸਟ੍ਰੇਸ਼ਨ, ਪ੍ਰਬੰਧਨ, ਚੋਣਾਂ ਅਤੇ ਪ੍ਰਸ਼ਾਸਨ ਲਈ ਕਾਨੂੰਨੀ ਢਾਂਚਾ ਨਿਰਧਾਰਤ ਕਰਦਾ ਹੈ।",
      te: "మల్టీ-స్టేట్ సహకార సొసైటీల చట్టం, 2002 భారతదేశంలో ఒకటి కంటే ఎక్కువ రాష్ట్రాల్లో పనిచేసే సహకార సొసైటీలను నియంత్రిస్తుంది. ఇది వాటి నమోదు, నిర్వహణ, ఎన్నికలు మరియు పాలన కోసం చట్టపరమైన ఫ్రేమ్‌వర్క్‌ను నిర్దేశిస్తుంది.",
      kn: "ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಗಳ ಕಾಯಿದೆ, 2002 ಭಾರತದಲ್ಲಿ ಒಂದಕ್ಕಿಂತ ಹೆಚ್ಚು ರಾಜ್ಯಗಳಲ್ಲಿ ಕಾರ್ಯನಿರ್ವಹಿಸುವ ಸಹಕಾರ ಸೊಸೈಟಿಗಳನ್ನು ನಿಯಂತ್ರಿಸುತ್ತದೆ. ಇದು ಅವುಗಳ ನೋಂದಣಿ, ನಿರ್ವಹಣೆ, ಚುನಾವಣೆಗಳು ಮತ್ತು ಆಡಳಿತಕ್ಕಾಗಿ ಕಾನೂನು ಚೌಕಟ್ಟನ್ನು ನಿಗದಿಪಡಿಸುತ್ತದೆ.",
    },
    keyProvisions: {
      en: [
        "Registration of multi-state cooperative societies with the Central Registrar.",
        "Membership rights and representation across member states.",
        "Election of the board of directors and tenure of the board.",
        "Reserve fund, audits, and annual returns under the Act.",
      ],
      pa: [
        "ਕੇਂਦਰੀ ਰਜਿਸਟਰਾਰ ਨਾਲ ਮਲਟੀ-ਸਟੇਟ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ ਦੀ ਰਜਿਸਟ੍ਰੇਸ਼ਨ।",
        "ਮੈਂਬਰ ਰਾਜਾਂ ਵਿੱਚ ਮੈਂਬਰਸ਼ਿਪ ਅਧਿਕਾਰ ਅਤੇ ਨੁਮਾਇੰਦਗੀ।",
        "ਨਿਰਦੇਸ਼ਕ ਬੋਰਡ ਦੀ ਚੋਣ ਅਤੇ ਬੋਰਡ ਦੀ ਮਿਆਦ।",
        "ਐਕਟ ਤਹਿਤ ਰਿਜ਼ਰਵ ਫੰਡ, ਆਡਿਟ ਅਤੇ ਸਾਲਾਨਾ ਵਾਪਸੀਆਂ।",
      ],
      te: [
        "కేంద్ర రిజిస్ట్రార్‌తో మల్టీ-స్టేట్ సహకార సొసైటీల నమోదు.",
        "సభ్య రాష్ట్రాల్లో సభ్యత్వ హక్కులు మరియు ప్రాతినిధ్యం.",
        "డైరెక్టర్ల బోర్డు ఎన్నిక మరియు బోర్డు పదవీకాలం.",
        "చట్టం కింద రిజర్వ్ ఫండ్, ఆడిట్‌లు మరియు వార్షిక రిటర్న్‌లు.",
      ],
      kn: [
        "ಕೇಂದ್ರ ನೋಂದಣಿದಾರರೊಂದಿಗೆ ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಗಳ ನೋಂದಣಿ.",
        "ಸದಸ್ಯ ರಾಜ್ಯಗಳಾದ್ಯಂತ ಸದಸ್ಯತ್ವ ಹಕ್ಕುಗಳು ಮತ್ತು ಪ್ರಾತಿನಿಧ್ಯ.",
        "ನಿರ್ದೇಶಕರ ಮಂಡಳಿಯ ಚುನಾವಣೆ ಮತ್ತು ಮಂಡಳಿಯ ಅವಧಿ.",
        "ಕಾಯಿದೆಯ ಅಡಿ ಮೀಸಲು ನಿಧಿ, ಲೆಕ್ಕಪರಿಶೋಧನೆಗಳು ಮತ್ತು ವಾರ್ಷಿಕ ವರದಿಗಳು.",
      ],
    },
    applicability: { en: ["Cooperative societies operating in two or more states."], pa: ["ਦੋ ਜਾਂ ਵੱਧ ਰਾਜਾਂ ਵਿੱਚ ਕੰਮ ਕਰਨ ਵਾਲੀਆਂ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ।"], te: ["రెండు లేదా అంతకంటే ఎక్కువ రాష్ట్రాల్లో పనిచేసే సహకార సొసైటీలు."], kn: ["ಎರಡು ಅಥವಾ ಹೆಚ್ಚು ರಾಜ್ಯಗಳಲ್ಲಿ ಕಾರ್ಯನಿರ್ವಹಿಸುವ ಸಹಕಾರ ಸೊಸೈಟಿಗಳು."] },
    byLaws: { en: ["Each society adopts its own by-laws consistent with the Act and its rules."], pa: ["ਹਰ ਸੋਸਾਇਟੀ ਐਕਟ ਅਤੇ ਉਸਦੇ ਨਿਯਮਾਂ ਦੇ ਅਨੁਸਾਰ ਆਪਣੇ ਉਪ-ਨਿਯਮ ਅਪਣਾਉਂਦੀ ਹੈ।"], te: ["ప్రతి సొసైటీ చట్టం మరియు దాని నిబంధనలకు అనుగుణంగా తన స్వంత ఉప-నియమాలను అవలంబిస్తుంది."], kn: ["ಪ್ರತಿ ಸೊಸೈಟಿ ಕಾಯಿದೆ ಮತ್ತು ಅದರ ನಿಯಮಗಳಿಗೆ ಅನುಗುಣವಾಗಿ ತನ್ನದೇ ಆದ ಉಪ-ನಿಯಮಗಳನ್ನು ಅಳವಡಿಸುತ್ತದೆ."] },
    source: { label: { en: "Ministry of Cooperation", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "model-pacs-bye-laws",
    title: { en: "Model Bye-laws of Primary Agricultural Credit Societies", pa: "ਪ੍ਰਾਇਮਰੀ ਐਗਰੀਕਲਚਰਲ ਕ੍ਰੈਡਿਟ ਸੋਸਾਇਟੀਆਂ ਦੇ ਨਮੂਨਾ ਉਪ-ਨਿਯਮ", te: "ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీల నమూనా ఉప-నియమాలు", kn: "ಪ್ರಾಥಮಿಕ ಕೃಷಿ ಕ್ರೆಡಿಟ್ ಸೊಸೈಟಿಗಳ ಮಾದರಿ ಉಪ-ನಿಯಮಗಳು" },
    badge: { en: "Model PACS Bye-laws", pa: "ਨਮੂਨਾ PACS ਉਪ-ਨਿਯਮ", te: "నమూనా PACS ఉప-నియమాలు", kn: "ಮಾದರಿ PACS ಉಪ-ನಿಯಮಗಳು" },
    category: "bye-laws",
    overview: {
      en: "The model bye-laws prescribe the standard constitution and operational rules for Primary Agricultural Credit Societies (PACS) — the village-level cooperatives that provide credit and farm services.",
      pa: "ਨਮੂਨਾ ਉਪ-ਨਿਯਮ ਪ੍ਰਾਇਮਰੀ ਐਗਰੀਕਲਚਰਲ ਕ੍ਰੈਡਿਟ ਸੋਸਾਇਟੀਆਂ (PACS) — ਜੋ ਕਿਰਜ਼ਾ ਅਤੇ ਖੇਤੀ ਸੇਵਾਵਾਂ ਪ੍ਰਦਾਨ ਕਰਨ ਵਾਲੀਆਂ ਪਿੰਡ-ਪੱਧਰੀ ਸਹਿਕਾਰੀਆਂ ਹਨ — ਲਈ ਮਿਆਰੀ ਸੰਰਚਨਾ ਅਤੇ ਕਾਰਜਸ਼ੀਲ ਨਿਯਮ ਨਿਰਧਾਰਤ ਕਰਦੇ ਹਨ।",
      te: "నమూనా ఉప-నియమాలు ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీల (PACS) ప్రామాణిక రాజ్యాంగం మరియు కార్యాచరణ నిబంధనలను నిర్దేశిస్తాయి — ఇవి అప్పు మరియు వ్యవసాయ సేవలు అందించే గ్రామ స్థాయి సహకార సంస్థలు.",
      kn: "ಮಾದರಿ ಉಪ-ನಿಯಮಗಳು ಪ್ರಾಥಮಿಕ ಕೃಷಿ ಕ್ರೆಡಿಟ್ ಸೊಸೈಟಿಗಳ (PACS) ಪ್ರಮಾಣಿತ ಸಂವಿಧಾನ ಮತ್ತು ಕಾರ್ಯಾಚರಣೆ ನಿಯಮಗಳನ್ನು ನಿಗದಿಪಡಿಸುತ್ತವೆ — ಇವು ಸಾಲ ಮತ್ತು ಕೃಷಿ ಸೇವೆಗಳನ್ನು ಒದಗಿಸುವ ಗ್ರಾಮ ಮಟ್ಟದ ಸಹಕಾರ ಸಂಸ್ಥೆಗಳು.",
    },
    keyProvisions: {
      en: [
        "Eligibility and procedure for membership, share capital and entrance fees.",
        "Powers and duties of the board of directors.",
        "Conduct of general body meetings and voting rights.",
        "Appointment of the secretary and staff.",
      ],
      pa: [
        "ਮੈਂਬਰਸ਼ਿਪ, ਸ਼ੇਅਰ ਪੂੰਜੀ ਅਤੇ ਦਾਖਲਾ ਫੀਸਾਂ ਲਈ ਯੋਗਤਾ ਅਤੇ ਵਿਧੀ।",
        "ਨਿਰਦੇਸ਼ਕ ਬੋਰਡ ਦੇ ਅਧਿਕਾਰ ਅਤੇ ਕਰਤੱਵ।",
        "ਜਨਰਲ ਬਾਡੀ ਦੀਆਂ ਮੀਟਿੰਗਾਂ ਦਾ ਆਯੋਜਨ ਅਤੇ ਵੋਟਿੰਗ ਅਧਿਕਾਰ।",
        "ਸਕੱਤਰ ਅਤੇ ਸਟਾਫ ਦੀ ਨਿਯੁਕਤੀ।",
      ],
      te: [
        "సభ్యత్వం, షేర్ మూలధనం మరియు అడ్మిషన్ రుసుములకు అర్హత మరియు విధానం.",
        "డైరెక్టర్ల బోర్డు అధికారాలు మరియు విధులు.",
        "సాధారణ సభా సమావేశాల నిర్వహణ మరియు ఓటింగ్ హక్కులు.",
        "సెక్రటరీ మరియు సిబ్బంది నియామకం.",
      ],
      kn: [
        "ಸದಸ್ಯತ್ವ, ಪಾಲು ಬಂಡವಾಳ ಮತ್ತು ಪ್ರವೇಶ ಶುಲ್ಕಗಳಿಗೆ ಅರ್ಹತೆ ಮತ್ತು ವಿಧಾನ.",
        "ನಿರ್ದೇಶಕರ ಮಂಡಳಿಯ ಅಧಿಕಾರಗಳು ಮತ್ತು ಕರ್ತವ್ಯಗಳು.",
        "ಸಾಮಾನ್ಯ ಸಭೆಗಳ ನಡವಳಿಕೆ ಮತ್ತು ಮತದಾನದ ಹಕ್ಕುಗಳು.",
        "ಕಾರ್ಯದರ್ಶಿ ಮತ್ತು ಸಿಬ್ಬಂದಿಯ ನೇಮಕಾತಿ.",
      ],
    },
    applicability: {
      en: [
        "New and existing PACS that adopt the model bye-laws or a state-approved variant.",
      ],
      pa: [
        "ਨਮੂਨਾ ਉਪ-ਨਿਯਮ ਜਾਂ ਰਾਜ-ਪ੍ਰਵਾਨਿਤ ਰੂਪ ਅਪਣਾਉਣ ਵਾਲੀਆਂ ਨਵੀਆਂ ਅਤੇ ਮੌਜੂਦਾ PACS।",
      ],
      te: [
        "నమూనా ఉప-నియమాలను లేదా రాష్ట్ర-ఆమోదించిన వైవిధ్యాన్ని అవలంబించే కొత్త మరియు ఇప్పటికే ఉన్న PACS.",
      ],
      kn: [
        "ಮಾದರಿ ಉಪ-ನಿಯಮಗಳನ್ನು ಅಥವಾ ರಾಜ್ಯ-ಅನುಮೋದಿತ ರೂಪಾಂತರವನ್ನು ಅಳವಡಿಸುವ ಹೊಸ ಮತ್ತು ಅಸ್ತಿತ್ವದಲ್ಲಿರುವ PACS.",
      ],
    },
    byLaws: {
      en: [
        "Borrowing limits and lending rules for members.",
        "Formation of sub-committees for loans, audit and grievances.",
      ],
      pa: [
        "ਮੈਂਬਰਾਂ ਲਈ ਕਰਜ਼ਾ ਲੈਣ ਦੀਆਂ ਸੀਮਾਵਾਂ ਅਤੇ ਕਰਜ਼ਾ ਦੇਣ ਦੇ ਨਿਯਮ।",
        "ਕਰਜ਼ੇ, ਆਡਿਟ ਅਤੇ ਸ਼ਿਕਾਇਤਾਂ ਲਈ ਉਪ-ਕਮੇਟੀਆਂ ਦਾ ਗਠਨ।",
      ],
      te: [
        "సభ్యులకు అప్పు తీసుకునే పరిమితులు మరియు రుణ నిబంధనలు.",
        "రుణాలు, ఆడిట్ మరియు ఫిర్యాదుల కోసం ఉప-కమిటీల ఏర్పాటు.",
      ],
      kn: [
        "ಸದಸ್ಯರಿಗೆ ಸಾಲ ಪಡೆಯುವ ಮಿತಿಗಳು ಮತ್ತು ಸಾಲ ನೀಡುವ ನಿಯಮಗಳು.",
        "ಸಾಲಗಳು, ಲೆಕ್ಕಪರಿಶೋಧನೆ ಮತ್ತು ದೂರುಗಳಿಗಾಗಿ ಉಪ-ಸಮಿತಿಗಳ ರಚನೆ.",
      ],
    },
    source: { label: { en: "Ministry of Cooperation", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "board-election-rules",
    title: { en: "Election of Board of Directors — MSCS Rules, 2011", pa: "ਨਿਰਦੇਸ਼ਕ ਬੋਰਡ ਦੀ ਚੋਣ — MSCS ਨਿਯਮ, 2011", te: "డైరెక్టర్ల బోర్డు ఎన్నిక — MSCS నిబంధనలు, 2011", kn: "ನಿರ್ದೇಶಕರ ಮಂಡಳಿಯ ಚುನಾವಣೆ — MSCS ನಿಯಮಗಳು, 2011" },
    badge: { en: "Board Elections", pa: "ਬੋਰਡ ਚੋਣਾਂ", te: "బోర్డు ఎన్నికలు", kn: "ಮಂಡಳಿ ಚುನಾವಣೆಗಳು" },
    category: "provisions",
    overview: {
      en: "The MSCS Rules, 2011 detail how the board of a multi-state cooperative society is elected, including the role of the election authority, the electoral college and the election timetable.",
      pa: "MSCS ਨਿਯਮ, 2011 ਵਿੱਚ ਵਿਸਥਾਰ ਵਿੱਚ ਦੱਸਿਆ ਗਿਆ ਹੈ ਕਿ ਮਲਟੀ-ਸਟੇਟ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀ ਦਾ ਬੋਰਡ ਕਿਵੇਂ ਚੁਣਿਆ ਜਾਂਦਾ ਹੈ, ਜਿਸ ਵਿੱਚ ਚੋਣ ਪ੍ਰਾਧਿਕਰਣ ਦੀ ਭੂਮਿਕਾ, ਚੋਣਕਾਰ ਮੰਡਲ ਅਤੇ ਚੋਣ ਸਮਾਂ-ਸਾਰਣੀ ਸ਼ਾਮਲ ਹੈ।",
      te: "MSCS నిబంధనలు, 2011 మల్టీ-స్టేట్ సహకార సొసైటీ బోర్డు ఎలా ఎన్నుకోబడుతుందో వివరంగా నిర్దేశిస్తాయి, ఇందులో ఎన్నికల అథారిటీ పాత్ర, ఎలక్టోరల్ కాలేజ్ మరియు ఎన్నికల సమయపట్టిక ఉన్నాయి.",
      kn: "MSCS ನಿಯಮಗಳು, 2011 ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಯ ಮಂಡಳಿಯನ್ನು ಹೇಗೆ ಆಯ್ಕೆ ಮಾಡಲಾಗುತ್ತದೆ ಎಂಬುದನ್ನು ವಿವರವಾಗಿ ನಿಗದಿಪಡಿಸುತ್ತವೆ, ಇದರಲ್ಲಿ ಚುನಾವಣಾ ಪ್ರಾಧಿಕಾರದ ಪಾತ್ರ, ಚುನಾವಣಾ ಸಮಿತಿ ಮತ್ತು ಚುನಾವಣಾ ಸಮಯಪಟ್ಟಿ ಸೇರಿವೆ.",
    },
    keyProvisions: {
      en: [
        "Appointment of an election authority to conduct elections.",
        "Preparation and certification of the electoral college.",
        "Dates for the e-election/ballot and counting of votes.",
      ],
      pa: [
        "ਚੋਣਾਂ ਕਰਨ ਲਈ ਚੋਣ ਪ੍ਰਾਧਿਕਰਣ ਦੀ ਨਿਯੁਕਤੀ।",
        "ਚੋਣਕਾਰ ਮੰਡਲ ਦੀ ਤਿਆਰੀ ਅਤੇ ਪ੍ਰਮਾਣੀਕਰਣ।",
        "ਈ-ਚੋਣ / ਬੈਲਟ ਅਤੇ ਵੋਟਾਂ ਦੀ ਗਿਣਤੀ ਦੀਆਂ ਮਿਤੀਆਂ।",
      ],
      te: [
        "ఎన్నికలు నిర్వహించడానికి ఎన్నికల అథారిటీ నియామకం.",
        "ఎలక్టోరల్ కాలేజీ తయారీ మరియు ధృవీకరణ.",
        "ఇ-ఎన్నిక / బ్యాలెట్ మరియు ఓట్ల లెక్కింపు తేదీలు.",
      ],
      kn: [
        "ಚುನಾವಣೆಗಳನ್ನು ನಡೆಸಲು ಚುನಾವಣಾ ಪ್ರಾಧಿಕಾರದ ನೇಮಕಾತಿ.",
        "ಚುನಾವಣಾ ಸಮಿತಿಯ ತಯಾರಿ ಮತ್ತು ಪ್ರಮಾಣೀಕರಣ.",
        "ಇ-ಚುನಾವಣೆ / ಮತಪತ್ರ ಮತ್ತು ಮತ ಎಣಿಕೆಯ ದಿನಾಂಕಗಳು.",
      ],
    },
    applicability: { en: ["Multi-state cooperative societies governed by MSCS Rules, 2011."], pa: ["MSCS ਨਿਯਮ, 2011 ਦੁਆਰਾ ਨਿਯੰਤ੍ਰਿਤ ਮਲਟੀ-ਸਟੇਟ ਸਹਿਕਾਰੀ ਸੋਸਾਇਟੀਆਂ।"], te: ["MSCS నిబంధనలు, 2011 ద్వారా నియంత్రించబడే మల్టీ-స్టేట్ సహకార సొసైటీలు."], kn: ["MSCS ನಿಯಮಗಳು, 2011 ರಿಂದ ನಿಯಂತ್ರಿಸಲ್ಪಡುವ ಮಲ್ಟಿ-ರಾಜ್ಯ ಸಹಕಾರ ಸೊಸೈಟಿಗಳು."] },
    byLaws: { en: ["Society bye-laws set the size and composition of the board."], pa: ["ਸੋਸਾਇਟੀ ਦੇ ਉਪ-ਨਿਯਮ ਬੋਰਡ ਦਾ ਆਕਾਰ ਅਤੇ ਗਠਨ ਨਿਰਧਾਰਤ ਕਰਦੇ ਹਨ।"], te: ["సొసైటీ ఉప-నియమాలు బోర్డు పరిమాణం మరియు కూర్పును నిర్దేశిస్తాయి."], kn: ["ಸೊಸೈಟಿ ಉಪ-ನಿಯಮಗಳು ಮಂಡಳಿಯ ಗಾತ್ರ ಮತ್ತು ಸಂಯೋಜನೆಯನ್ನು ನಿಗದಿಪಡಿಸುತ್ತವೆ."] },
    source: { label: { en: "Ministry of Cooperation", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "cooperative-disputes",
    title: { en: "Cooperative Dispute Resolution", pa: "ਸਹਿਕਾਰੀ ਵਿਵਾਦ ਨਿਵਾਰਣ", te: "సహకార వివాద పరిష్కారం", kn: "ಸಹಕಾರ ವಿವಾದ ಪರಿಹಾರ" },
    badge: { en: "Disputes", pa: "ਵਿਵਾਦ", te: "వివాదాలు", kn: "ವಿವಾದಗಳು" },
    category: "provisions",
    overview: {
      en: "Disputes between a cooperative and its members — over loans, share capital, or by-law obligations — are resolved through arbitration or a cooperative dispute authority, not regular civil courts.",
      pa: "ਸਹਿਕਾਰੀ ਅਤੇ ਉਸਦੇ ਮੈਂਬਰਾਂ ਵਿਚਕਾਰ ਵਿਵਾਦ — ਕਰਜ਼ੇ, ਸ਼ੇਅਰ ਪੂੰਜੀ, ਜਾਂ ਉਪ-ਨਿਯਮ ਦੀਆਂ ਜ਼ਿੰਮੇਵਾਰੀਆਂ ਨੂੰ ਲੈ ਕੇ — ਨਿਯਮਤ ਸਿਵਲ ਅਦਾਲਤਾਂ ਦੀ ਬਜਾਏ ਸਾਲਸੀ (ਆਰਬਿਟ੍ਰੇਸ਼ਨ) ਜਾਂ ਸਹਿਕਾਰੀ ਵਿਵਾਦ ਪ੍ਰਾਧਿਕਰਣ ਰਾਹੀਂ ਸੁਲਝਾਏ ਜਾਂਦੇ ਹਨ।",
      te: "సహకార సంస్థ మరియు దాని సభ్యుల మధ్య వివాదాలు — రుణాలు, షేర్ మూలధనం, లేదా ఉప-నియమ బాధ్యతలపై — సాధారణ సివిల్ కోర్టులకు కాకుండా మధ్యవర్తిత్వం లేదా సహకార వివాద అథారిటీ ద్వారా పరిష్కరించబడతాయి.",
      kn: "ಸಹಕಾರ ಸಂಸ್ಥೆ ಮತ್ತು ಅದರ ಸದಸ್ಯರ ನಡುವಿನ ವಿವಾದಗಳು — ಸಾಲಗಳು, ಪಾಲು ಬಂಡವಾಳ, ಅಥವಾ ಉಪ-ನಿಯಮ ಬಾಧ್ಯತೆಗಳ ಮೇಲೆ — ಸಾಮಾನ್ಯ ನಾಗರಿಕ ನ್ಯಾಯಾಲಯಗಳಿಗಿಂತ ಮಧ್ಯಸ್ಥಿಕೆ ಅಥವಾ ಸಹಕಾರ ವಿವಾದ ಪ್ರಾಧಿಕಾರದ ಮೂಲಕ ಪರಿಹರಿಸಲ್ಪಡುತ್ತವೆ.",
    },
    keyProvisions: {
      en: [
        "Matters that are deemed disputes under the Act.",
        "Reference of disputes to arbitration or a designated authority.",
        "Enforceability of arbitration awards.",
      ],
      pa: [
        "ਐਕਟ ਤਹਿਤ ਵਿਵਾਦ ਮੰਨੇ ਜਾਣ ਵਾਲੇ ਮਾਮਲੇ।",
        "ਵਿਵਾਦਾਂ ਨੂੰ ਸਾਲਸੀ ਜਾਂ ਨਿਸ਼ਚਿਤ ਪ੍ਰਾਧਿਕਰਣ ਕੋਲ ਭੇਜਣਾ।",
        "ਸਾਲਸੀ ਦੇ ਫੈਸਲਿਆਂ ਦੀ ਲਾਗੂ ਹੋਣ ਦੀ ਸਮਰੱਥਾ।",
      ],
      te: [
        "చట్టం కింద వివాదాలుగా పరిగణించబడే విషయాలు.",
        "మధ్యవర్తిత్వం లేదా నియమిత అథారిటీకి వివాదాలను సూచించడం.",
        "మధ్యవర్తిత్వ తీర్పుల అమలు సాధ్యత.",
      ],
      kn: [
        "ಕಾಯಿದೆಯ ಅಡಿ ವಿವಾದಗಳೆಂದು ಪರಿಗಣಿಸಲಾಗುವ ವಿಷಯಗಳು.",
        "ಮಧ್ಯಸ್ಥಿಕೆ ಅಥವಾ ನಿಯೋಜಿತ ಪ್ರಾಧಿಕಾರಕ್ಕೆ ವಿವಾದಗಳ ಉಲ್ಲೇಖ.",
        "ಮಧ್ಯಸ್ಥಿಕೆ ತೀರ್ಪುಗಳ ಜಾರಿಯ ಸಾಧ್ಯತೆ.",
      ],
    },
    applicability: { en: ["Members, former members and cooperatives facing internal disputes."], pa: ["ਅੰਦਰੂਨੀ ਵਿਵਾਦਾਂ ਦਾ ਸਾਹਮਣਾ ਕਰ ਰਹੇ ਮੈਂਬਰ, ਸਾਬਕਾ ਮੈਂਬਰ ਅਤੇ ਸਹਿਕਾਰੀਆਂ।"], te: ["అంతర్గత వివాదాలను ఎదుర్కొంటున్న సభ్యులు, మాజీ సభ్యులు మరియు సహకార సంస్థలు."], kn: ["ಆಂತರಿಕ ವಿವಾದಗಳನ್ನು ಎದುರಿಸುತ್ತಿರುವ ಸದಸ್ಯರು, ಮಾಜಿ ಸದಸ್ಯರು ಮತ್ತು ಸಹಕಾರ ಸಂಸ್ಥೆಗಳು."] },
    byLaws: { en: ["By-laws may prescribe an internal grievance-cum-dispute resolution committee."], pa: ["ਉਪ-ਨਿਯਮ ਅੰਦਰੂਨੀ ਸ਼ਿਕਾਇਤ-ਸਹਿਤ-ਵਿਵਾਦ ਨਿਵਾਰਣ ਕਮੇਟੀ ਨਿਰਧਾਰਤ ਕਰ ਸਕਦੇ ਹਨ।"], te: ["ఉప-నియమాలు అంతర్గత ఫిర్యాదు-సహిత-వివాద పరిష్కార కమిటీని నిర్దేశించవచ్చు."], kn: ["ಉಪ-ನಿಯಮಗಳು ಆಂತರಿಕ ದೂರು-ಮತ್ತು-ವಿವಾದ ಪರಿಹಾರ ಸಮಿತಿಯನ್ನು ನಿಗದಿಪಡಿಸಬಹುದು."] },
    source: { label: { en: "Ministry of Cooperation", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "pac-model-bye-laws-moc",
    title: { en: "Model Bye-laws for PACS — Ministry of Cooperation", pa: "PACS ਲਈ ਨਮੂਨਾ ਉਪ-ਨਿਯਮ — ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ", te: "PACS కోసం నమూనా ఉప-నియమాలు — సహకార మంత్రిత్వ శాఖ", kn: "PACS ಗಾಗಿ ಮಾದರಿ ಉಪ-ನಿಯಮಗಳು — ಸಹಕಾರ ಸಚಿವಾಲಯ" },
    badge: { en: "PACS Bye-laws (MoC)", pa: "PACS ਉਪ-ਨਿਯਮ (MoC)", te: "PACS ఉప-నియమాలు (MoC)", kn: "PACS ಉಪ-ನಿಯಮಗಳು (MoC)" },
    category: "bye-laws",
    overview: {
      en: "The Ministry of Cooperation's revised model bye-laws modernise PACS — enabling them to provide banking, storage, and agro-services while keeping their village-level cooperative character.",
      pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ ਦੇ ਸੋਧੇ ਹੋਏ ਨਮੂਨਾ ਉਪ-ਨਿਯਮ PACS ਨੂੰ ਆਧੁਨਿਕ ਬਣਾਉਂਦੇ ਹਨ — ਉਨ੍ਹਾਂ ਦੇ ਪਿੰਡ-ਪੱਧਰੀ ਸਹਿਕਾਰੀ ਸੁਭਾਅ ਨੂੰ ਬਰਕਰਾਰ ਰੱਖਦਿਆਂ ਬੈਂਕਿੰਗ, ਸਟੋਰੇਜ ਅਤੇ ਖੇਤੀ ਸੇਵਾਵਾਂ ਪ੍ਰਦਾਨ ਕਰਨ ਵਿੱਚ ਸਮਰੱਥ ਬਣਾਉਂਦੇ ਹਨ।",
      te: "సహకార మంత్రిత్వ శాఖ సవరించిన నమూనా ఉప-నియమాలు PACSలను ఆధునికీకరిస్తాయి — వాటి గ్రామ స్థాయి సహకార లక్షణాన్ని కొనసాగిస్తూనే బ్యాంకింగ్, నిల్వ మరియు వ్యవసాయ సేవలను అందించేలా చేస్తాయి.",
      kn: "ಸಹಕಾರ ಸಚಿವಾಲಯದ ಪರಿಷ್ಕೃತ ಮಾದರಿ ಉಪ-ನಿಯಮಗಳು PACS ಗಳನ್ನು ಆಧುನೀಕರಿಸುತ್ತವೆ — ಅವುಗಳ ಗ್ರಾಮ ಮಟ್ಟದ ಸಹಕಾರ ಸ್ವಭಾವವನ್ನು ಉಳಿಸಿಕೊಂಡು ಬ್ಯಾಂಕಿಂಗ್, ಶೇಖರಣೆ ಮತ್ತು ಕೃಷಿ ಸೇವೆಗಳನ್ನು ಒದಗಿಸಲು ಅನುವು ಮಾಡಿಕೊಡುತ್ತವೆ.",
    },
    keyProvisions: {
      en: [
        "Minimum and maximum share capital for members.",
        "Wider business activities beyond lending (storage, insurance, IT services).",
        "Digital operational requirements and record-keeping.",
      ],
      pa: [
        "ਮੈਂਬਰਾਂ ਲਈ ਘੱਟੋ-ਘੱਟ ਅਤੇ ਵੱਧ ਤੋਂ ਵੱਧ ਸ਼ੇਅਰ ਪੂੰਜੀ।",
        "ਕਰਜ਼ਾ ਦੇਣ ਤੋਂ ਪਰੇ ਵਿਆਪਕ ਕਾਰੋਬਾਰੀ ਗਤੀਵਿਧੀਆਂ (ਸਟੋਰੇਜ, ਬੀਮਾ, IT ਸੇਵਾਵਾਂ)।",
        "ਡਿਜੀਟਲ ਕਾਰਜਸ਼ੀਲ ਲੋੜਾਂ ਅਤੇ ਰਿਕਾਰਡ ਰੱਖਣਾ।",
      ],
      te: [
        "సభ్యులకు కనిష్ట మరియు గరిష్ట షేర్ మూలధనం.",
        "రుణం ఇవ్వడం కంటే విస్తృతమైన వ్యాపార కార్యకలాపాలు (నిల్వ, బీమా, IT సేవలు).",
        "డిజిటల్ కార్యాచరణ అవసరాలు మరియు రికార్డు నిర్వహణ.",
      ],
      kn: [
        "ಸದಸ್ಯರಿಗೆ ಕನಿಷ್ಠ ಮತ್ತು ಗರಿಷ್ಠ ಪಾಲು ಬಂಡವಾಳ.",
        "ಸಾಲ ನೀಡುವುದಕ್ಕಿಂತ ವಿಶಾಲವಾದ ವ್ಯಾಪಾರ ಚಟುವಟಿಕೆಗಳು (ಶೇಖರಣೆ, ವಿಮೆ, IT ಸೇವೆಗಳು).",
        "ಡಿಜಿಟಲ್ ಕಾರ್ಯಾಚರಣೆ ಅವಶ್ಯಕತೆಗಳು ಮತ್ತು ದಾಖಲೆ ನಿರ್ವಹಣೆ.",
      ],
    },
    applicability: { en: ["PACS registered under the cooperative law of the state."], pa: ["ਰਾਜ ਦੇ ਸਹਿਕਾਰੀ ਕਾਨੂੰਨ ਤਹਿਤ ਰਜਿਸਟਰਡ PACS।"], te: ["రాష్ట్ర సహకార చట్టం కింద నమోదైన PACS."], kn: ["ರಾಜ್ಯದ ಸಹಕಾರ ಕಾಯಿದೆಯ ಅಡಿ ನೋಂದಾಯಿತ PACS."] },
    byLaws: { en: ["Fees, dividends and reserve allocations set in the bye-laws."], pa: ["ਉਪ-ਨਿਯਮਾਂ ਵਿੱਚ ਸੈੱਟ ਕੀਤੇ ਫੀਸ, ਲਾਭਅੰਸ਼ ਅਤੇ ਰਿਜ਼ਰਵ ਵੰਡ।"], te: ["ఉప-నియమాలలో నిర్దేశించిన రుసుములు, డివిడెండ్‌లు మరియు రిజర్వు కేటాయింపులు."], kn: ["ಉಪ-ನಿಯಮಗಳಲ್ಲಿ ನಿಗದಿಪಡಿಸಿದ ಶುಲ್ಕಗಳು, ಲಾಭಾಂಶಗಳು ಮತ್ತು ಮೀಸಲು ಹಂಚಿಕೆಗಳು."] },
    source: { label: { en: "Ministry of Cooperation", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, url: "https://www.moc.gov.in" },
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
