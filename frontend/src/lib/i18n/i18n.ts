export const LOCALES = ["en", "hi", "gu", "mr", "bn", "ta"] as const;
export type Locale = (typeof LOCALES)[number];
