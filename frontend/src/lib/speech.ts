export interface SpeechService {
  supported: boolean;
  listen: (locale: string, onTranscript: (text: string) => void) => () => void;
  speak: (text: string, locale: string) => void;
  stopSpeaking: () => void;
}

let currentAudio: HTMLAudioElement | null = null;
let currentObjectUrl: string | null = null;

function stopAll() {
  if (currentAudio) {
    try { currentAudio.pause(); } catch { /* noop */ }
    currentAudio = null;
  }
  if (currentObjectUrl) {
    try { URL.revokeObjectURL(currentObjectUrl); } catch { /* noop */ }
    currentObjectUrl = null;
  }
  window.speechSynthesis?.cancel();
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
      stopAll();

      const cleanText = text
        .replace(/\[chunk:[a-f0-9]+\]/g, "")
        .replace(/\*\*([^*]+)\*\*/g, "$1")
        .replace(/\n+/g, ". ")
        .trim();
      if (!cleanText) return;

      // For Indian languages, fetch backend Sarvam TTS and play the result
      if (locale !== "en") {
        const ttsText = cleanText.slice(0, 500);
        const formData = new FormData();
        formData.append("text", ttsText);
        formData.append("language", locale);

        fetch("/api/speak", { method: "POST", body: formData })
          .then((res) => (res.ok ? res.blob() : Promise.reject()))
          .then((blob) => {
            if (blob.size < 500) return Promise.reject();
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            currentAudio = audio;
            currentObjectUrl = url;
            audio.onended = () => stopAll();
            audio.onerror = () => stopAll();
            // Fire play() — user gesture is still active in this microtask
            audio.play().catch(() => {
              stopAll();
              // Final fallback: browser TTS
              speakBrowser(cleanText, locale);
            });
          })
          .catch(() => {
            speakBrowser(cleanText, locale);
          });
        return;
      }

      // English: browser TTS directly
      speakBrowser(cleanText, locale);
    },
    stopSpeaking() {
      stopAll();
    },
  };
}

function speakBrowser(text: string, locale: string) {
  const synthesis = window.speechSynthesis;
  if (!synthesis) return;
  const utterance = new SpeechSynthesisUtterance(text);
  const voices = synthesis.getVoices();
  const match =
    voices.find((v) => v.lang.startsWith(locale === "en" ? "en" : locale)) ||
    voices.find((v) => v.lang.startsWith("en"));
  if (match) utterance.voice = match;
  synthesis.cancel();
  synthesis.speak(utterance);
}
