export interface SpeechService {
  supported: boolean;
  listen: (locale: string, onTranscript: (text: string) => void) => () => void;
  speak: (text: string, locale: string) => void;
  stopSpeaking: () => void;
}

export function createSpeechService(): SpeechService {
  const isBrowser = typeof window !== "undefined";
  const SpeechRecognition =
    isBrowser && typeof window !== "undefined"
      ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ((window as any).SpeechRecognition ||
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (window as any).webkitSpeechRecognition)
      : undefined;
  const synthesis =
    isBrowser && typeof window !== "undefined" ? window.speechSynthesis : undefined;

  return {
    get supported() {
      if (!isBrowser) return false;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const sr = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      return Boolean(sr) && Boolean(window.speechSynthesis);
    },
    listen(locale, onTranscript) {
      if (!SpeechRecognition) return () => {};
      const rec = new SpeechRecognition();
      rec.lang = locale === "en" ? "en-IN" : locale + "-IN";
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      rec.onresult = (e: any) => {
        const text = e.results?.[0]?.[0]?.transcript;
        if (text) onTranscript(text);
      };
      rec.onerror = () => {};
      rec.start();
      return () => {
        try { rec.stop(); } catch { /* noop */ }
      };
    },
    speak(text, locale) {
      if (!synthesis) return;
      const utterance = new SpeechSynthesisUtterance(text);
      const voices = synthesis.getVoices();
      const match =
        voices.find((v) => v.lang.startsWith(locale === "en" ? "en" : locale)) ||
        voices.find((v) => v.lang.startsWith("en"));
      if (match) utterance.voice = match;
      synthesis.cancel();
      synthesis.speak(utterance);
    },
    stopSpeaking() {
      if (synthesis) synthesis.cancel();
    },
  };
}
