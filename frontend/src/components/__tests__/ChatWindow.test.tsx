import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act, cleanup } from "@testing-library/react";
import { ChatWindow } from "../ChatWindow";
import * as api from "@/lib/api";
import type { Locale } from "@/lib/i18n/i18n";

// Control the locale returned by useI18n between renders.
let mockLocale: Locale = "en";
vi.mock("@/lib/i18n/provider", () => ({
  useI18n: () => ({ t: (k: string) => k, locale: mockLocale, setLocale: () => {} }),
}));
vi.mock("next/navigation", () => ({
  useSearchParams: () => ({ get: () => null }),
}));
vi.mock("next/link", () => ({
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  default: ({ children, ...rest }: any) => {
    // Render an anchor so the component tree mounts without a router context.
    return <a {...rest}>{children}</a>;
  },
}));
vi.mock("@/components/motion/Reveal", () => ({
  // Avoid pulling in gsap/ScrollTrigger (needs matchMedia) for this unit test.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Reveal: ({ children }: any) => <>{children}</>,
}));
vi.mock("@/lib/api", () => ({
  sendChat: vi.fn().mockResolvedValue({
    answer: "ok",
    language: "en",
    domain: "unknown",
    intent: "unknown",

    entities: [],
    confidence: 0,
    confidence_level: "none",
    citations: [],
    abstained: false,
    follow_up_question: null,
  }),
}));

beforeEach(() => {
  mockLocale = "en";
  vi.clearAllMocks();
  if (!globalThis.crypto?.randomUUID) {
    Object.defineProperty(globalThis, "crypto", {
      value: { randomUUID: () => "test-session-id" },
      configurable: true,
    });
  }
  if (!window.matchMedia) {
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));
  }
  if (!Element.prototype.scrollIntoView) {
    Element.prototype.scrollIntoView = vi.fn();
  }
});

afterEach(() => {
  cleanup();
});

describe("ChatWindow ui_language_explicit", () => {
  it("first message is NOT marked explicit", async () => {
    render(<ChatWindow />);
    fireEvent.change(screen.getByPlaceholderText(/chat\.placeholder/i), {
      target: { value: "hello" },
    });
    await act(async () => {
      fireEvent.click(screen.getByLabelText(/send/i));
    });
    expect(api.sendChat).toHaveBeenCalledWith(
      expect.objectContaining({ ui_language_explicit: false }),
    );
  });

  it("language switch marks the next message explicit", async () => {
    const { rerender } = render(<ChatWindow />);

    // Send one message in the default locale so a "last sent locale" exists.
    fireEvent.change(screen.getByPlaceholderText(/chat\.placeholder/i), {
      target: { value: "hello" },
    });
    await act(async () => {
      fireEvent.click(screen.getByLabelText(/send/i));
    });

    // Simulate the user switching the UI language to Hindi, then force a
    // re-render so ChatWindow reads the new locale (the mock returns it live).
    await act(async () => {
      mockLocale = "hi";
      rerender(<ChatWindow />);
    });

    fireEvent.change(screen.getByPlaceholderText(/chat\.placeholder/i), {
      target: { value: "namaste" },
    });
    await act(async () => {
      fireEvent.click(screen.getByLabelText(/send/i));
    });

    expect(api.sendChat).toHaveBeenLastCalledWith(
      expect.objectContaining({ language: "hi", ui_language_explicit: true }),
    );
  });

  it("stays non-explicit when locale is unchanged after a switch", async () => {
    const { rerender } = render(<ChatWindow />);

    fireEvent.change(screen.getByPlaceholderText(/chat\.placeholder/i), {
      target: { value: "hello" },
    });
    await act(async () => {
      fireEvent.click(screen.getByLabelText(/send/i));
    });

    await act(async () => {
      mockLocale = "hi";
      rerender(<ChatWindow />);
    });

    // First message after switching -> explicit true
    fireEvent.change(screen.getByPlaceholderText(/chat\.placeholder/i), {
      target: { value: "namaste" },
    });
    await act(async () => {
      fireEvent.click(screen.getByLabelText(/send/i));
    });
    expect(api.sendChat).toHaveBeenLastCalledWith(
      expect.objectContaining({ language: "hi", ui_language_explicit: true }),
    );

    // Second message without further switching -> explicit false
    fireEvent.change(screen.getByPlaceholderText(/chat\.placeholder/i), {
      target: { value: "phir" },
    });
    await act(async () => {
      fireEvent.click(screen.getByLabelText(/send/i));
    });
    expect(api.sendChat).toHaveBeenLastCalledWith(
      expect.objectContaining({ language: "hi", ui_language_explicit: false }),
    );
  });
});
