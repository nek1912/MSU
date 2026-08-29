import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "../api";
import { partitionRuns, hasVoice, pickVoice, speakSegments } from "../speech";

// Minimal WAV hex (doesn't need to be valid audio for the test; we stub Audio).
const FAKE_HEX = "000000";

beforeEach(() => {
  vi.resetAllMocks();
  // Stub Audio so play() resolves and onended fires, letting playAzure settle.
  class StubAudio {
    onended: (() => void) | null = null;
    onerror: (() => void) | null = null;
    constructor(_src?: string) {
      void _src;
    }
    play() {
      Promise.resolve().then(() => this.onended?.());
      return Promise.resolve();
    }
  }
  (globalThis as unknown as { Audio: typeof StubAudio }).Audio = StubAudio;
});

describe("partitionRuns", () => {
  it("merges contiguous same-language segments", () => {
    const out = partitionRuns([
      { text: "Hello ", language: "en" },
      { text: "world", language: "en" },
      { text: "नमस्ते", language: "hi" },
    ]);
    expect(out).toEqual([
      { text: "Hello world", language: "en" },
      { text: "नमस्ते", language: "hi" },
    ]);
  });

  it("returns empty array for empty input", () => {
    expect(partitionRuns([])).toEqual([]);
  });
});

describe("hasVoice / pickVoice", () => {
  it("returns false/undefined when no speechSynthesis (jsdom/node)", () => {
    expect(hasVoice("en")).toBe(false);
    expect(pickVoice("hi")).toBeUndefined();
  });
});

describe("speakSegments", () => {
  it("falls back to Azure per run and resolves", async () => {
    const spy = vi
      .spyOn(api, "fetchVoiceSpeak")
      .mockResolvedValue({ audio: FAKE_HEX, language: "hi" });

    await speakSegments([{ text: "नमस्ते", language: "hi" }]);

    expect(spy).toHaveBeenCalledWith([{ text: "नमस्ते", language: "hi" }]);
  });

  it("uses Azure for each language run when no browser voice matches", async () => {
    const spy = vi
      .spyOn(api, "fetchVoiceSpeak")
      .mockResolvedValue({ audio: FAKE_HEX, language: "hi" });

    await speakSegments([
      { text: "Hello ", language: "en" },
      { text: "world", language: "en" },
      { text: "नमस्ते", language: "hi" },
    ]);

    // Two distinct runs (en, hi) => two Azure fetches.
    expect(spy).toHaveBeenCalledTimes(2);
    expect(spy).toHaveBeenCalledWith([{ text: "Hello world", language: "en" }]);
    expect(spy).toHaveBeenCalledWith([{ text: "नमस्ते", language: "hi" }]);
  });
});
