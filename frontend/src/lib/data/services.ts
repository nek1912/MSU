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
    name: { en: "PACS Membership", gu: "PACS સભ્યપદ", pa: "PACS ਮੈਂਬਰਸ਼ਿਪ", te: "PACS సభ్యత్వం", kn: "PACS ಸದಸ್ಯತ್ವ" },
    category: "membership",
    summary: { en: "Become a member of your village cooperative to access credit and services.", gu: "તમારી ગામ સહકારીના સભ્ય બનો જેથી ધિરાણ અને સેવાઓની પહોંચ મળે.", pa: "ਕਰਜ਼ੇ ਅਤੇ ਸੇਵਾਵਾਂ ਤੱਕ ਪਹੁੰਚ ਲਈ ਆਪਣੀ ਪਿੰਡ ਸਹਿਕਾਰੀ ਦੇ ਮੈਂਬਰ ਬਣੋ।", te: "అప్పు మరియు సేవలకు ప్రాప్యత పొందడానికి మీ గ్రామ సహకార సంస్థలో సభ్యుడిగా చేరండి.", kn: "ಸಾಲ ಮತ್ತು ಸೇವೆಗಳಿಗೆ ಪ್ರವೇಶ ಪಡೆಯಲು ನಿಮ್ಮ ಗ್ರಾಮ ಸಹಕಾರ ಸಂಸ್ಥೆಯ ಸದಸ್ಯರಾಗಿ." },
    description:
      { en: "Joining your Primary Agricultural Credit Society gives you access to affordable credit, storage, inputs and a channel to raise grievances.", gu: "તમારી પ્રાથમિક કૃષિ ક્રેડિટ સોસાયટીમાં જોડાવાથી તમને ઓછા ખર્ચાળ ધિરાણ, સંગ્રહ, સામગ્રી અને ફરિયાદ ઉઠાવવાનો માર્ગ મળે છે.", pa: "ਆਪਣੀ ਪ੍ਰਾਇਮਰੀ ਐਗਰੀਕਲਚਰਲ ਕ੍ਰੈਡਿਟ ਸੋਸਾਇਟੀ ਵਿੱਚ ਸ਼ਾਮਲ ਹੋਣ ਨਾਲ ਤੁਹਾਨੂੰ ਕਿਫਾਇਤੀ ਕਰਜ਼ਾ, ਸਟੋਰੇਜ, ਸਮੱਗਰੀ ਅਤੇ ਸ਼ਿਕਾਇਤਾਂ ਦੱਸਣ ਦਾ ਚੈਨਲ ਮਿਲਦਾ ਹੈ।", te: "మీ ప్రాథమిక వ్యవసాయ క్రెడిట్ సొసైటీలో చేరడం వల్ల సరసమైన అప్పు, నిల్వ, ఇన్‌పుట్‌లు మరియు ఫిర్యాదులు తెలియజేయడానికి ఒక మార్గం లభిస్తుంది.", kn: "ನಿಮ್ಮ ಪ್ರಾಥಮಿಕ ಕೃಷಿ ಕ್ರೆಡಿಟ್ ಸೊಸೈಟಿಗೆ ಸೇರುವುದರಿಂದ ಕೈಗೆಟುಕುವ ಸಾಲ, ಶೇಖರಣೆ, ಇನ್‌ಪುಟ್‌ಗಳು ಮತ್ತು ದೂರುಗಳನ್ನು ತಿಳಿಸಲು ಒಂದು ಮಾರ್ಗ ಲಭಿಸುತ್ತದೆ." },
    whoCanUse: { en: ["Residents of the PACS area of operation.", "Landowners, tenant farmers and sharecroppers."], gu: ["PACS ના કાર્યક્ષેત્રના રહેવાસીઓ.", "જમીનદાર, ભાડાના ખેડૂતો અને સહભાગી ખેડૂતો."], pa: ["PACS ਦੇ ਕਾਰਜ ਖੇਤਰ ਦੇ ਨਿਵਾਸੀ।", "ਜ਼ਮੀਨ ਮਾਲਕ, ਕਿਰਾਏਦਾਰ ਕਿਸਾਨ ਅਤੇ ਸੀਰਦਾਰ।"], te: ["PACS కార్యకలాపాల ప్రాంతంలో నివసించేవారు.", "భూయజమానులు, కౌలు రైతులు మరియు భాగస్వామి రైతులు."], kn: ["PACS ಕಾರ್ಯವ್ಯಾಪ್ತಿ ಪ್ರದೇಶದ ನಿವಾಸಿಗಳು.", "ಭೂಮಾಲೀಕರು, ಗೇಣಿದಾರ ರೈತರು ಮತ್ತು ಭಾಗಸ್ವಾಮಿ ರೈತರು."] },
    howToAccess: { en: ["Visit your local PACS office.", "Submit identity and residence documents.", "Pay the share/entrance fee."], gu: ["તમારી સ્થાનિક PACS ઓફિસની મુલાકાત લો.", "ઓળખ અને રહેઠાણના દસ્તાવેજો જમા કરો.", "શેર / પ્રવેશ ફી ભરો."], pa: ["ਆਪਣੀ ਸਥਾਨਕ PACS ਦਫ਼ਤਰ ਜਾਓ।", "ਪਛਾਣ ਅਤੇ ਨਿਵਾਸ ਦਸਤਾਵੇਜ਼ ਜਮ੍ਹਾਂ ਕਰੋ।", "ਸ਼ੇਅਰ / ਦਾਖਲਾ ਫੀਸ ਦਿਓ।"], te: ["మీ స్థానిక PACS కార్యాలయాన్ని సందర్శించండి.", "గుర్తింపు మరియు నివాస పత్రాలను సమర్పించండి.", "షేర్ / అడ్మిషన్ రుసుము చెల్లించండి."], kn: ["ನಿಮ್ಮ ಸ್ಥಳೀಯ PACS ಕಚೇರಿಗೆ ಭೇಟಿ ನೀಡಿ.", "ಗುರುತು ಮತ್ತು ನಿವಾಸ ದಾಖಲೆಗಳನ್ನು ಸಲ್ಲಿಸಿ.", "ಪಾಲು / ಪ್ರವೇಶ ಶುಲ್ಕ ಪಾವತಿಸಿ."] },
    source: { label: { en: "PACS / Cooperative Department", gu: "PACS / સહકાર વિભાગ", pa: "PACS / ਸਹਿਕਾਰੀ ਵਿਭਾਗ", te: "PACS / సహకార శాఖ", kn: "PACS / ಸಹಕಾರ ಇಲಾಖೆ" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "short-term-crop-credit",
    name: { en: "Short-term Crop Credit", gu: "ટૂંકા ગાળાનો પાક ધિરાણ", pa: "ਥੋੜ੍ਹੇ ਸਮੇਂ ਦਾ ਫਸਲ ਕਰਜ਼ਾ", te: "స్వల్పకాలిక పంట రుణం", kn: "ಅಲ್ಪಾವಧಿ ಬೆಳೆ ಸಾಲ" },
    category: "credit",
    summary: { en: "Seasonal crop loans at subsidised interest to fund sowing to harvest.", gu: "વાવણીથી લણણી સુધી ભંડોળ માટે સબસિડી વ્યાજ પર મોસમી પાક ધિરાણ.", pa: "ਬਿਜਾਈ ਤੋਂ ਵਾਢੀ ਤੱਕ ਫੰਡ ਕਰਨ ਲਈ ਸਬਸਿਡੀਜ਼ਡ ਵਿਆਜ 'ਤੇ ਮੌਸਮੀ ਫਸਲ ਕਰਜ਼ੇ।", te: "విత్తనం నుండి పంటకోత వరకు నిధుల కోసం సబ్సిడీ వడ్డీతో సీజనల్ పంట రుణాలు.", kn: "ಬಿತ್ತನೆಯಿಂದ ಸುಗ್ಗಿಯವರೆಗೆ ಹಣಕಾಸಿಗೆ ಸಬ್ಸಿಡಿ ಬಡ್ಡಿಯಲ್ಲಿ ಋತುಮಾನದ ಬೆಳೆ ಸಾಲಗಳು." },
    description:
      { en: "Short-term crop loans cover cultivation costs and are repaid after harvest, often with interest subvention for timely repayment.", gu: "ટૂંકા ગાળાના પાક ધિરાણ ખેતીના ખર્ચ આવરે છે અને લણણી પછી ચૂકવવામાં આવે છે, ઘણીવાર સમયસર ચુકવણી માટે વ્યાજ સબસિડી સાથે.", pa: "ਥੋੜ੍ਹੇ ਸਮੇਂ ਦੇ ਫਸਲ ਕਰਜ਼ੇ ਕਾਸ਼ਤ ਦੇ ਖਰਚੇ ਪੂਰੇ ਕਰਦੇ ਹਨ ਅਤੇ ਵਾਢੀ ਤੋਂ ਬਾਅਦ ਮੁੜ-ਭੁਗਤਾਨ ਕੀਤੇ ਜਾਂਦੇ ਹਨ, ਸਮੇਂ ਸਿਰ ਮੁੜ-ਭੁਗਤਾਨ ਲਈ ਅਕਸਰ ਵਿਆਜ ਸਬਸਿਡੀ ਹੁੰਦੀ ਹੈ।", te: "స్వల్పకాలిక పంట రుణాలు సాగు ఖర్చులను భరిస్తాయి మరియు పంటకోత తర్వాత తిరిగి చెల్లించబడతాయి, తరచుగా సకాలంలో తిరిగి చెల్లింపుకు వడ్డీ సబ్సిడీ ఉంటుంది.", kn: "ಅಲ್ಪಾವಧಿಯ ಬೆಳೆ ಸಾಲಗಳು ಬೇಸಾಯ ವೆಚ್ಚಗಳನ್ನು ಒಳಗೊಳ್ಳುತ್ತವೆ ಮತ್ತು ಸುಗ್ಗಿಯ ನಂತರ ಮರುಪಾವತಿಯಾಗುತ್ತವೆ, ಸಮಯೋಚಿತ ಮರುಪಾವತಿಗೆ ಸಾಮಾನ್ಯವಾಗಿ ಬಡ್ಡಿ ಸಬ್ಸಿಡಿ ಇರುತ್ತದೆ." },
    whoCanUse: { en: ["Member farmers of a PACS or cooperative credit institution."], gu: ["PACS અથવા સહકારી ધિરાણ સંસ્થાના સભ્ય ખેડૂતો."], pa: ["PACS ਜਾਂ ਸਹਿਕਾਰੀ ਕ੍ਰੈਡਿਟ ਸੰਸਥਾ ਦੇ ਮੈਂਬਰ ਕਿਸਾਨ।"], te: ["PACS లేదా సహకార క్రెడిట్ సంస్థల సభ్యులు."], kn: ["PACS ಅಥವಾ ಸಹಕಾರ ಕ್ರೆಡಿಟ್ ಸಂಸ್ಥೆಯ ಸದಸ್ಯ ರೈತರು."] },
    howToAccess: { en: ["Apply at your PACS or bank with KCC application.", "Provide land, identity and crop-cycle details."], gu: ["KCC અરજી સાથે તમારી PACS અથવા બેંક પર અરજી કરો.", "જમીન, ઓળખ અને પાક ચક્રની વિગતો પૂરી પાડો."], pa: ["KCC ਅਰਜ਼ੀ ਨਾਲ ਆਪਣੀ PACS ਜਾਂ ਬੈਂਕ ਵਿੱਚ ਅਰਜ਼ੀ ਦਿਓ।", "ਜ਼ਮੀਨ, ਪਛਾਣ ਅਤੇ ਫਸਲ-ਚੱਕਰ ਦੇ ਵੇਰਵੇ ਦਿਓ।"], te: ["KCC దరఖాస్తుతో మీ PACS లేదా బ్యాంకు వద్ద దరఖాస్తు చేయండి.", "భూమి, గుర్తింపు మరియు పంట చక్ర వివరాలను అందించండి."], kn: ["KCC ಅರ್ಜಿಯೊಂದಿಗೆ ನಿಮ್ಮ PACS ಅಥವಾ ಬ್ಯಾಂಕ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.", "ಭೂಮಿ, ಗುರುತು ಮತ್ತು ಬೆಳೆ ಚಕ್ರದ ವಿವರಗಳನ್ನು ಒದಗಿಸಿ."] },
    source: { label: { en: "PACS / Bank", gu: "PACS / બેંક", pa: "PACS / ਬੈਂਕ", te: "PACS / బ్యాంకు", kn: "PACS / ಬ್ಯಾಂಕ್" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "godown-storage",
    name: { en: "Godown & Storage", gu: "ગોદામ અને સંગ્રહ", pa: "ਗੋਦਾਮ ਅਤੇ ਸਟੋਰੇਜ", te: "గోదాము & నిల్వ", kn: "ಗೋದಾಮು ಮತ್ತು ಶೇಖರಣೆ" },
    category: "storage",
    summary: { en: "Safe storage of produce to avoid distress sales and improve bargaining.", gu: "મજબૂરીની વેચાણ ટાળવા અને ભાવ સુધારવા માટે ઉત્પાદનનો સલામત સંગ્રહ.", pa: "ਮਜਬੂਰੀ ਦੀਆਂ ਵਿਕਰੀਆਂ ਤੋਂ ਬਚਣ ਅਤੇ ਮੋਲ-ਭਾਅ ਸੁਧਾਰਨ ਲਈ ਉਪਜ ਦੀ ਸੁਰੱਖਿਅਤ ਸਟੋਰੇਜ।", te: "నిర్బంధ విక్రయాలను నివారించడానికి మరియు బేరసారాలు మెరుగుపరచడానికి ఉత్పత్తిని సురక్షితంగా నిల్వ చేయడం.", kn: "ನಿರ್ಬಂಧ ಮಾರಾಟವನ್ನು ತಪ್ಪಿಸಲು ಮತ್ತು ಚೌಕಾಶಿ ಸುಧಾರಿಸಲು ಉತ್ಪನ್ನದ ಸುರಕ್ಷಿತ ಶೇಖರಣೆ." },
    description:
      { en: "PACS and cooperative unions operate godowns where members can store grain and produce, and access pledge loans against stock.", gu: "PACS અને સહકારી સંઘો ગોદામો ચલાવે છે જ્યાં સભ્યો અનાજ અને ઉત્પાદન સંગ્રહિત કરી શકે છે, અને સ્ટોક સામે ગીરવે ધિરાણ મેળવી શકે છે.", pa: "PACS ਅਤੇ ਸਹਿਕਾਰੀ ਯੂਨੀਅਨਾਂ ਗੋਦਾਮ ਚਲਾਉਂਦੀਆਂ ਹਨ ਜਿੱਥੇ ਮੈਂਬਰ ਅਨਾਜ ਅਤੇ ਉਪਜ ਸਟੋਰ ਕਰ ਸਕਦੇ ਹਨ, ਸਟਾਕ ਦੇ ਆਧਾਰ 'ਤੇ ਗਿਰਵੀ ਕਰਜ਼ੇ ਲੈ ਸਕਦੇ ਹਨ।", te: "PACS మరియు సహకార సంఘాలు గోదాములను నిర్వహిస్తాయి, ఇక్కడ సభ్యులు ధాన్యం మరియు ఉత్పత్తిని నిల్వ చేయవచ్చు, మరియు స్టాక్‌కు వ్యతిరేకంగా తాకట్టు రుణాలు పొందవచ్చు.", kn: "PACS ಮತ್ತು ಸಹಕಾರ ಸಂಘಗಳು ಗೋದಾಮುಗಳನ್ನು ನಡೆಸುತ್ತವೆ, ಅಲ್ಲಿ ಸದಸ್ಯರು ಧಾನ್ಯ ಮತ್ತು ಉತ್ಪನ್ನಗಳನ್ನು ಶೇಖರಿಸಬಹುದು, ಮತ್ತು ಸ್ಟಾಕ್‌ನ ವಿರುದ್ಧ ಜಮೀನುದಾರಿ ಸಾಲಗಳನ್ನು ಪಡೆಯಬಹುದು." },
    whoCanUse: { en: ["Member farmers with stored produce.", "Producers holding warehouses/pledge receipts."], gu: ["સંગ્રહિત ઉત્પાદન ધરાવતા સભ્ય ખેડૂતો.", "ગોદામ / ગીરવે રસીદ ધરાવતા ઉત્પાદકો."], pa: ["ਸਟੋਰ ਕੀਤੀ ਉਪਜ ਵਾਲੇ ਮੈਂਬਰ ਕਿਸਾਨ।", "ਗੋਦਾਮ / ਗਿਰਵੀ ਰਸੀਦਾਂ ਰੱਖਣ ਵਾਲੇ ਉਤਪਾਦਕ।"], te: ["నిల్వ చేసిన ఉత్పత్తితో ఉన్న సభ్య రైతులు.", "గోదాము / తాకట్టు రసీదులు కలిగిన ఉత్పత్తిదారులు."], kn: ["ಶೇಖರಿಸಿದ ಉತ್ಪನ್ನವಿರುವ ಸದಸ್ಯ ರೈತರು.", "ಗೋದಾಮು / ಜಮೀನುದಾರಿ ರಸೀದಿಗಳನ್ನು ಹೊಂದಿರುವ ಉತ್ಪಾದಕರು."] },
    howToAccess: { en: ["Register storage at your nearest PACS godown.", "Obtain a warehouse receipt to pledge for a loan."], gu: ["તમારી સૌથી નજીકની PACS ગોદામમાં સંગ્રહ નોંધાવો.", "ધિરાણ માટે ગીરવે રાખવા ગોદામ રસીદ મેળવો."], pa: ["ਆਪਣੀ ਸਭ ਤੋਂ ਨੇੜਲੀ PACS ਗੋਦਾਮ ਵਿੱਚ ਸਟੋਰੇਜ ਦਰਜ ਕਰਵਾਓ।", "ਕਰਜ਼ੇ ਲਈ ਗਿਰਵੀ ਰੱਖਣ ਲਈ ਗੋਦਾਮ ਰਸੀਦ ਲਵੋ।"], te: ["మీ సమీప PACS గోదాములో నిల్వను నమోదు చేయండి.", "రుణం కోసం తాకట్టు పెట్టడానికి గోదాము రసీదు పొందండి."], kn: ["ನಿಮ್ಮ ಹತ್ತಿರದ PACS ಗೋದಾಮಿನಲ್ಲಿ ಶೇಖರಣೆಯನ್ನು ನೋಂದಾಯಿಸಿ.", "ಸಾಲಕ್ಕಾಗಿ ಜಮೀನುದಾರಿ ಮಾಡಲು ಗೋದಾಮು ರಸೀದಿ ಪಡೆಯಿರಿ."] },
    source: { label: { en: "PACS / Warehousing", gu: "PACS / ગોદામ", pa: "PACS / ਗੋਦਾਮ", te: "PACS / గోదాము", kn: "PACS / ಗೋದಾಮು" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "agro-input-supply",
    name: { en: "Agro-input Supply", gu: "કૃષિ સામગ્રી પુરવઠો", pa: "ਖੇਤੀ ਸਮੱਗਰੀ ਸਪਲਾਈ", te: "వ్యవసాయ ఇన్‌పుట్ సరఫరా", kn: "ಕೃಷಿ ಇನ್‌ಪುಟ್ ಸರಬರಾಜು" },
    category: "agro-inputs",
    summary: { en: "Seeds, fertilisers and farm equipment supplied through the cooperative.", gu: "સહકારી દ્વારા પુરા થતા બીજ, ખાતર અને કૃષિ સાધનો.", pa: "ਸਹਿਕਾਰੀ ਰਾਹੀਂ ਸਪਲਾਈ ਕੀਤੇ ਬੀਜ, ਖਾਦਾਂ ਅਤੇ ਖੇਤੀ ਉਪਕਰਣ।", te: "సహకార సంస్థ ద్వారా విత్తనాలు, ఎరువులు మరియు వ్యవసాయ పరికరాల సరఫరా.", kn: "ಸಹಕಾರ ಸಂಸ್ಥೆಯ ಮೂಲಕ ಸರಬರಾಜಾಗುವ ಬೀಜಗಳು, ಗೊಬ್ಬರಗಳು ಮತ್ತು ಕೃಷಿ ಉಪಕರಣಗಳು." },
    description:
      { en: "PACS supply certified seeds, fertilisers, pesticides and farm equipment in bulk to members at fair prices.", gu: "PACS ધૃત બીજ, ખાતર, જંતુનાશકો અને કૃષિ સાધનો સભ્યોને યોગ્ય ભાવે જથ્થાબંધ પુરા પાડે છે.", pa: "PACS ਮੈਂਬਰਾਂ ਨੂੰ ਵਾਜਬ ਕੀਮਤਾਂ 'ਤੇ ਪ੍ਰਮਾਣਿਤ ਬੀਜ, ਖਾਦਾਂ, ਕੀਟਨਾਸ਼ਕ ਅਤੇ ਖੇਤੀ ਉਪਕਰਣ ਥੋਕ ਵਿੱਚ ਸਪਲਾਈ ਕਰਦੀਆਂ ਹਨ।", te: "PACS ధృవీకరించిన విత్తనాలు, ఎరువులు, పురుగుమందులు మరియు వ్యవసాయ పరికరాలను సభ్యులకు సరసమైన ధరలకు టోకుగా సరఫరా చేస్తాయి.", kn: "PACS ಪ್ರಮಾಣೀಕೃತ ಬೀಜಗಳು, ಗೊಬ್ಬರಗಳು, ಕೀಟನಾಶಕಗಳು ಮತ್ತು ಕೃಷಿ ಉಪಕರಣಗಳನ್ನು ನ್ಯಾಯಯುತ ಬೆಲೆಗಳಲ್ಲಿ ಸದಸ್ಯರಿಗೆ ಟೋಕಾಗಿ ಸರಬರಾಜು ಮಾಡುತ್ತವೆ." },
    whoCanUse: { en: ["PACS member farmers.", "Village residents in the society's area."], gu: ["PACS સભ્ય ખેડૂતો.", "સોસાયટીના વિસ્તારમાં ગામના રહેવાસીઓ."], pa: ["PACS ਮੈਂਬਰ ਕਿਸਾਨ।", "ਸੋਸਾਇਟੀ ਦੇ ਖੇਤਰ ਵਿੱਚ ਪਿੰਡ ਦੇ ਨਿਵਾਸੀ।"], te: ["PACS సభ్య రైతులు.", "సొసైటీ ప్రాంతంలోని గ్రామ నివాసులు."], kn: ["PACS ಸದಸ್ಯ ರೈತರು.", "ಸೊಸೈಟಿ ಪ್ರದೇಶದ ಗ್ರಾಮ ನಿವಾಸಿಗಳು."] },
    howToAccess: { en: ["Place a request at the PACS sale counter or branches.", "Pay against the invoice and collect inputs."], gu: ["PACS વેચાણ કાઉન્ટર અથવા શાખાઓ પર વિનંતી કરો.", "ઇન્વોઇસ સામે ચુકવણી કરો અને સામગ્રી મેળવો."], pa: ["PACS ਵਿਕਰੀ ਕਾਊਂਟਰ ਜਾਂ ਸ਼ਾਖਾਵਾਂ ਵਿੱਚ ਬੇਨਤੀ ਰੱਖੋ।", "ਇਨਵਾਇਸ ਵਿਰੁੱਧ ਭੁਗਤਾਨ ਕਰੋ ਅਤੇ ਸਮੱਗਰੀ ਲਵੋ।"], te: ["PACS అమ్మకపు కౌంటర్ లేదా శాఖల్లో అభ్యర్థన ఉంచండి.", "ఇన్వాయిస్‌కు వ్యతిరేకంగా చెల్లించి ఇన్‌పుట్‌లను సేకరించండి."], kn: ["PACS ಮಾರಾಟ ಕೌಂಟರ್ ಅಥವಾ ಶಾಖೆಗಳಲ್ಲಿ ವಿನಂತಿ ಸಲ್ಲಿಸಿ.", "ಇನ್‌ವಾಯ್ಸ್ ವಿರುದ್ಧ ಪಾವತಿಸಿ ಮತ್ತು ಇನ್‌ಪುಟ್‌ಗಳನ್ನು ಸಂಗ್ರಹಿಸಿ."] },
    source: { label: { en: "PACS / Agro-supply", gu: "PACS / કૃષિ પુરવઠો", pa: "PACS / ਖੇਤੀ ਸਪਲਾਈ", te: "PACS / వ్యవసాయ సరఫరా", kn: "PACS / ಕೃಷಿ ಸರಬರಾಜು" }, url: "https://www.moc.gov.in" },
  },
  {
    slug: "pmfby-enrolment",
    name: { en: "PMFBY Enrolment", gu: "PMFBY નોંધણી", pa: "PMFBY ਦਾਖਲਾ", te: "PMFBY నమోదు", kn: "PMFBY ನೋಂದಣಿ" },
    category: "insurance",
    summary: { en: "Enrol in crop insurance under PMFBY through your cooperative or CSC.", gu: "તમારી સહકારી અથવા CSC દ્વારા PMFBY હેઠળ પાક વીમામાં નોંધણી કરો.", pa: "ਆਪਣੀ ਸਹਿਕਾਰੀ ਜਾਂ CSC ਰਾਹੀਂ PMFBY ਤਹਿਤ ਫਸਲ ਬੀਮੇ ਵਿੱਚ ਦਾਖਲ ਹੋਵੋ।", te: "మీ సహకార సంస్థ లేదా CSC ద్వారా PMFBY కింద పంట బీమాలో నమోదు చేయండి.", kn: "ನಿಮ್ಮ ಸಹಕಾರ ಸಂಸ್ಥೆ ಅಥವಾ CSC ಮೂಲಕ PMFBY ಅಡಿ ಬೆಳೆ ವಿಮೆಯಲ್ಲಿ ನೋಂದಾಯಿಸಿ." },
    description:
      { en: "Pradhan Mantri Fasal Bima Yojana protects farmers against crop loss. PACS, banks and CSCs act as enrolment and claim-filing channels.", gu: "પ્રધાન મંત્રી ફસલ બીમા યોજના ખેડૂતોને પાક નુકસાન સામે રક્ષણ આપે છે. PACS, બેંકો અને CSC નોંધણી અને દાવો દાખલ કરવાના માર્ગો તરીકે કામ કરે છે.", pa: "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫਸਲ ਬੀਮਾ ਯੋਜਨਾ ਕਿਸਾਨਾਂ ਨੂੰ ਫਸਲ ਨੁਕਸਾਨ ਤੋਂ ਬਚਾਉਂਦੀ ਹੈ। PACS, ਬੈਂਕ ਅਤੇ CSC ਦਾਖਲੇ ਅਤੇ ਦਾਅਵਾ ਦਾਇਰ ਕਰਨ ਦੇ ਚੈਨਲ ਵਜੋਂ ਕੰਮ ਕਰਦੇ ਹਨ।", te: "ప్రధాన మంత్రి ఫసల్ బీమా యోజన రైతులను పంట నష్టం నుండి రక్షిస్తుంది. PACS, బ్యాంకులు మరియు CSCలు నమోదు మరియు దావా దాఖలు మార్గాలుగా పనిచేస్తాయి.", kn: "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬೀಮಾ ಯೋಜನೆ ರೈತರನ್ನು ಬೆಳೆ ನಷ್ಟದಿಂದ ರಕ್ಷಿಸುತ್ತದೆ. PACS, ಬ್ಯಾಂಕುಗಳು ಮತ್ತು CSCಗಳು ನೋಂದಣಿ ಮತ್ತು ದಾವೆ ದಾಖಲಿಸುವ ಮಾರ್ಗಗಳಾಗಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತವೆ." },
    whoCanUse: { en: ["All farmers, loanee and non-loanee, within notified areas."], gu: ["જાહેર કરેલા વિસ્તારોમાં તમામ ખેડૂતો — ધિરાણ લેતા અને ન લેતા."], pa: ["ਸੂਚਿਤ ਖੇਤਰਾਂ ਵਿੱਚ ਸਾਰੇ ਕਿਸਾਨ, ਕਰਜ਼ਾ ਲੈਣ ਵਾਲੇ ਅਤੇ ਨਾ ਲੈਣ ਵਾਲੇ।"], te: ["నోటిఫై చేసిన ప్రాంతాల్లో అందరు రైతులు — అప్పు తీసుకున్నవారు మరియు తీసుకోనివారు."], kn: ["ಪ್ರಕಟಿಸಿದ ಪ್ರದೇಶಗಳಲ್ಲಿ ಎಲ್ಲಾ ರೈತರು — ಸಾಲ ಪಡೆದವರು ಮತ್ತು ಪಡೆಯದವರು."] },
    howToAccess: { en: ["Sign a consent letter before the season deadline.", "Enrol at PACS / CSC / bank and keep land records."], gu: ["સીઝનની અંતિમ તારીખ પહેલાં સંમતિ પત્ર પર હસ્તાક્ષર કરો.", "PACS / CSC / બેંક પર નોંધણી કરો અને જમીન રેકોર્ડ રાખો."], pa: ["ਸੀਜ਼ਨ ਦੀ ਸਮਾਂ ਸੀਮਾ ਤੋਂ ਪਹਿਲਾਂ ਸਹਿਮਤੀ ਪੱਤਰ 'ਤੇ ਦਸਤਖਤ ਕਰੋ।", "PACS / CSC / ਬੈਂਕ ਵਿੱਚ ਦਾਖਲ ਹੋਵੋ ਅਤੇ ਜ਼ਮੀਨੀ ਰਿਕਾਰਡ ਰੱਖੋ।"], te: ["సీజన్ గడువుకు ముందు సమ్మతి పత్రంపై సంతకం చేయండి.", "PACS / CSC / బ్యాంకులో నమోదు చేయండి మరియు భూ రికార్డులను ఉంచండి."], kn: ["ಋತುವಿನ ಗಡುವಿಗೆ ಮೊದಲು ಸಮ್ಮತಿ ಪತ್ರಕ್ಕೆ ಸಹಿ ಮಾಡಿ.", "PACS / CSC / ಬ್ಯಾಂಕ್‌ನಲ್ಲಿ ನೋಂದಾಯಿಸಿ ಮತ್ತು ಭೂ ದಾಖಲೆಗಳನ್ನು ಇರಿಸಿ."] },
    source: { label: { en: "PMFBY", gu: "PMFBY", pa: "PMFBY", te: "PMFBY", kn: "PMFBY" }, url: "https://pmfby.gov.in" },
  },
  {
    slug: "cooperative-subsidy",
    name: { en: "Cooperative Subsidy", gu: "સહકારી સબસિડી", pa: "ਸਹਿਕਾਰੀ ਸਬਸਿਡੀ", te: "సహకార సబ్సిడీ", kn: "ಸಹಕಾರ ಸಬ್ಸಿಡಿ" },
    category: "subsidy",
    summary: { en: "Capital, interest and infrastructure subsidies for farmer cooperatives.", gu: "ખેડૂત સહકારી સંસ્થાઓ માટે મૂડી, વ્યાજ અને માળખાકીય સબસિડી.", pa: "ਕਿਸਾਨ ਸਹਿਕਾਰੀਆਂ ਲਈ ਪੂੰਜੀ, ਵਿਆਜ ਅਤੇ ਢਾਂਚਾਗਤ ਸਬਸਿਡੀਆਂ।", te: "రైతు సహకార సంస్థలకు మూలధన, వడ్డీ మరియు మౌలిక సదుపాయ సబ్సిడీలు.", kn: "ರೈತ ಸಹಕಾರ ಸಂಸ್ಥೆಗಳಿಗೆ ಬಂಡವಾಳ, ಬಡ್ಡಿ ಮತ್ತು ಮೂಲಸೌಕರ್ಯ ಸಬ್ಸಿಡಿಗಳು." },
    description:
      { en: "The Ministry of Cooperation and allies run subsidy schemes for cooperative infrastructure — godowns, processing units and interest subvention.", gu: "સહકાર મંત્રાલય અને સંબંધિત સંસ્થાઓ સહકારી માળખા માટે સબસિડી યોજનાઓ ચલાવે છે — ગોદામો, પ્રક્રિયા એકમો અને વ્યાજ સબસિડી.", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ ਅਤੇ ਸੰਬੰਧਿਤ ਸੰਸਥਾਵਾਂ ਸਹਿਕਾਰੀ ਢਾਂਚੇ ਲਈ ਸਬਸਿਡੀ ਯੋਜਨਾਵਾਂ ਚਲਾਉਂਦੀਆਂ ਹਨ — ਗੋਦਾਮ, ਪ੍ਰੋਸੈਸਿੰਗ ਯੂਨਿਟ ਅਤੇ ਵਿਆਜ ਸਬਸਿਡੀ।", te: "సహకార మంత్రిత్వ శాఖ మరియు అనుబంధ సంస్థలు సహకార మౌలిక సదుపాయాల కోసం సబ్సిడీ పథకాలను నిర్వహిస్తాయి — గోదాములు, ప్రాసెసింగ్ యూనిట్లు మరియు వడ్డీ సబ్సిడీ.", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ ಮತ್ತು ಮಿತ್ರ ಸಂಸ್ಥೆಗಳು ಸಹಕಾರ ಮೂಲಸೌಕರ್ಯಕ್ಕಾಗಿ ಸಬ್ಸಿಡಿ ಯೋಜನೆಗಳನ್ನು ನಡೆಸುತ್ತವೆ — ಗೋದಾಮುಗಳು, ಸಂಸ್ಕರಣಾ ಘಟಕಗಳು ಮತ್ತು ಬಡ್ಡಿ ಸಬ್ಸಿಡಿ." },
    whoCanUse: { en: ["Registered cooperatives / PACS within scheme scope.", "Farmers applying through eligible cooperative channels."], gu: ["યોજનાના ક્ષેત્રમાં નોંધાયેલા સહકારી / PACS.", "લાયક સહકારી માર્ગો દ્વારા અરજી કરતા ખેડૂતો."], pa: ["ਯੋਜਨਾ ਦੇ ਘੇਰੇ ਵਿੱਚ ਰਜਿਸਟਰਡ ਸਹਿਕਾਰੀਆਂ / PACS।", "ਯੋਗ ਸਹਿਕਾਰੀ ਚੈਨਲਾਂ ਰਾਹੀਂ ਅਰਜ਼ੀ ਦੇਣ ਵਾਲੇ ਕਿਸਾਨ।"], te: ["పథకం పరిధిలో నమోదైన సహకార సంస్థలు / PACS.", "అర్హత గల సహకార మార్గాల ద్వారా దరఖాస్తు చేసే రైతులు."], kn: ["ಯೋಜನೆಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ನೋಂದಾಯಿತ ಸಹಕಾರ ಸಂಸ್ಥೆಗಳು / PACS.", "ಅರ್ಹ ಸಹಕಾರ ಮಾರ್ಗಗಳ ಮೂಲಕ ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ರೈತರು."] },
    howToAccess: { en: ["Check eligibility against current guidelines.", "Submit the application via the portal or nodal office."], gu: ["વર્તમાન માર્ગદર્શિકાઓ સામે લાયકાત તપાસો.", "પોર્ટલ અથવા નોડલ ઓફિસ દ્વારા અરજી જમા કરો."], pa: ["ਮੌਜੂਦਾ ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼ਾਂ ਦੇ ਆਧਾਰ 'ਤੇ ਯੋਗਤਾ ਜਾਂਚੋ।", "ਪੋਰਟਲ ਜਾਂ ਨੋਡਲ ਦਫ਼ਤਰ ਰਾਹੀਂ ਅਰਜ਼ੀ ਜਮ੍ਹਾਂ ਕਰੋ।"], te: ["ప్రస్తుత మార్గదర్శకాల ప్రకారం అర్హతను తనిఖీ చేయండి.", "పోర్టల్ ద్వారా లేదా నోడల్ కార్యాలయం ద్వారా దరఖాస్తును సమర్పించండి."], kn: ["ಪ್ರಸ್ತುತ ಮಾರ್ಗಸೂಚಿಗಳಿಗೆ ಅನುಗುಣವಾಗಿ ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಿ.", "ಪೋರ್ಟಲ್ ಅಥವಾ ನೋಡಲ್ ಕಚೇರಿ ಮೂಲಕ ಅರ್ಜಿಯನ್ನು ಸಲ್ಲಿಸಿ."] },
    source: { label: { en: "Ministry of Cooperation", gu: "સહકાર મંત્રાલય", pa: "ਸਹਿਕਾਰਿਤਾ ਮੰਤਰਾਲਾ", te: "సహకార మంత్రిత్వ శాఖ", kn: "ಸಹಕಾರ ಸಚಿವಾಲಯ" }, url: "https://www.moc.gov.in" },
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
