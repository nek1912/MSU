"use client";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { Locale } from "./i18n";
import { translate } from "./dictionaries";

type I18nContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
};

const I18nContext = createContext<I18nContextValue | null>(null);

const VALID_LOCALES: Locale[] = ["en", "hi", "gu"];

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  // On mount, restore saved language from localStorage/cookie
  useEffect(() => {
    try {
      const saved = localStorage.getItem("app_locale") as Locale;
      if (saved && VALID_LOCALES.includes(saved)) {
        setLocaleState(saved);
      }
    } catch {}
  }, []);

  const setLocale = useCallback((newLocale: Locale) => {
    if (!VALID_LOCALES.includes(newLocale)) return;
    setLocaleState(newLocale);
    try {
      localStorage.setItem("app_locale", newLocale);
      document.cookie = `app_locale=${newLocale}; path=/; max-age=31536000`;
    } catch {}
  }, []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) =>
      translate(locale, key, vars),
    [locale],
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-locale", locale);
    document.documentElement.setAttribute("lang", locale);
  }, [locale]);

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within LanguageProvider");
  return ctx;
}
