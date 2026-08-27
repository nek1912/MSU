export const LOCALES = [
  "en", "hi", "mr", "bn", "ta", "te", "kn", "pa", "gu", "or", "ml", "ur",
] as const;
export type Locale = (typeof LOCALES)[number];
