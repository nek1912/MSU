import { fetchVoiceSpeak, type SpeechSegment } from "./api";

export type { SpeechSegment };

export interface SpeechService {
  supported: boolean;
  listen: (locale: string, onTranscript: (text: string) => void) => () => void;
  speak: (text: string, locale: string) => void;
  stopSpeaking: () => void;
}

// Monotonic token for cancelling in-flight playback when a newer request starts
// or the user stops. Incrementing this invalidates any pending utterance/audio.
let _speakToken = 0;
let _activeAudio: HTMLAudioElement | null = null;
let _activeAudioResolve: (() => void) | null = null;

function stopAllPlayback(): void {
  _speakToken++;
  if (typeof window !== "undefined" && window.speechSynthesis) {
    try {
      window.speechSynthesis.cancel();
    } catch {
      /* noop */
    }
  }
  if (_activeAudio) {
    try {
      _activeAudio.pause();
    } catch {
      /* noop */
    }
    _activeAudio = null;
  }
  if (_activeAudioResolve) {
    const r = _activeAudioResolve;
    _activeAudioResolve = null;
    r();
  }
}

export function hasVoice(lang: string): boolean {
  if (typeof window === "undefined" || !window.speechSynthesis) return false;
  const voices = window.speechSynthesis.getVoices();
  const prefix = lang === "en" ? "en" : lang;
  return voices.some((v) => v.lang.startsWith(prefix));
}

export function pickVoice(lang: string): SpeechSynthesisVoice | undefined {
  if (typeof window === "undefined" || !window.speechSynthesis) return undefined;
  const voices = window.speechSynthesis.getVoices();
  const prefix = lang === "en" ? "en" : lang;
  // NO English fallback: if no matching voice exists, return undefined so the
  // caller falls back to Azure for THAT language (never silently swap to English
  // for hi/gu/mr/bn).
  return voices.find((v) => v.lang.startsWith(prefix));
}

export function partitionRuns(segments: SpeechSegment[]): SpeechSegment[] {
  const runs: SpeechSegment[] = [];
  for (const seg of segments) {
    const last = runs[runs.length - 1];
    if (last && last.language === seg.language) {
      const sep = last.text.endsWith(" ") || seg.text.startsWith(" ") ? "" : " ";
      last.text += sep + seg.text;
    } else {
      runs.push({ language: seg.language, text: seg.text });
    }
  }
  return runs;
}

function hexToBase64(hex: string): string {
  let bin = "";
  for (let i = 0; i < hex.length; i += 2) {
    bin += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
  }
  return btoa(bin);
}

function playBrowser(text: string, voice: SpeechSynthesisVoice, token: number): Promise<void> {
  return new Promise((resolve) => {
    if (token !== _speakToken || typeof window === "undefined" || !window.speechSynthesis) {
      return resolve();
    }
    const u = new SpeechSynthesisUtterance(text);
    u.voice = voice;
    u.lang = voice.lang;
    const done = () => {
      u.onend = null;
      u.onerror = null;
      resolve();
    };
    u.onend = done;
    u.onerror = done;
    try {
      window.speechSynthesis.speak(u);
    } catch {
      resolve();
    }
  });
}

function playAzure(hex: string, token: number): Promise<void> {
  return new Promise((resolve, reject) => {
    if (token !== _speakToken) return resolve();
    let audio: HTMLAudioElement;
    try {
      audio = new Audio(`data:audio/wav;base64,${hexToBase64(hex)}`);
    } catch (e) {
      return reject(e);
    }
    _activeAudio = audio;
    _activeAudioResolve = resolve;
    const cleanup = () => {
      audio.onended = null;
      audio.onerror = null;
      if (_activeAudio === audio) _activeAudio = null;
      if (_activeAudioResolve === resolve) _activeAudioResolve = null;
    };
    audio.onended = () => {
      cleanup();
      resolve();
    };
    audio.onerror = () => {
      cleanup();
      reject(new Error("azure audio playback failed"));
    };
    audio.play().catch((e) => {
      cleanup();
      reject(e);
    });
  });
}

/**
 * Hybrid read-aloud: for each contiguous language run, play via the browser
 * SpeechSynthesis if a matching voice exists, otherwise fetch Azure audio for
 * that run. Runs play sequentially (no overlap). A newer call (or stopSpeaking)
 * cancels the current playback via the monotonic token.
 */
export async function speakSegments(
  segments: SpeechSegment[],
  opts?: { onToken?: (token: number) => void },
): Promise<void> {
  stopAllPlayback();
  const token = ++_speakToken;
  opts?.onToken?.(token);

  const runs = partitionRuns(segments || []);
  for (const run of runs) {
    if (token !== _speakToken) return;
    const voice = pickVoice(run.language);
    if (voice) {
      await playBrowser(run.text, voice, token);
    } else {
      let hex: string | null = null;
      try {
        const res = await fetchVoiceSpeak([{ text: run.text, language: run.language }]);
        hex = res.audio;
      } catch {
        hex = null;
      }
      if (hex == null) continue;
      try {
        await playAzure(hex, token);
      } catch {
        // audio unavailable for this run; continue with the next
      }
    }
    if (token !== _speakToken) return;
  }
}

export function createSpeechService(): SpeechService {
  const isBrowser = typeof window !== "undefined";
  const SpeechRecognition =
    isBrowser
      ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)
      : undefined;
  const synthesis = isBrowser ? window.speechSynthesis : undefined;

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
        try {
          rec.stop();
        } catch {
          /* noop */
        }
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
      stopAllPlayback();
    },
  };
}