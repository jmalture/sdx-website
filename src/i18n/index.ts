/** Languages of the site. DE is the default and lives at the root, the others under /<code>/. */
export const LANGS = [
  { code: 'de', locale: 'de-DE', og: 'de_DE', name: 'Deutsch' },
  { code: 'en', locale: 'en-US', og: 'en_US', name: 'English' },
  { code: 'cs', locale: 'cs-CZ', og: 'cs_CZ', name: 'Čeština' },
] as const;

export type Lang = (typeof LANGS)[number]['code'];

/**
 * Texts of one dictionary file ({ de: {...}, en: {...}, cs: {...} }) for one language.
 * Missing keys fall back to German, so a new section shows DE text until it is translated.
 */
export function dict<T extends Record<string, Record<string, string>>>(data: T, lang: Lang): Record<string, string> {
  return { ...data.de, ...(data[lang] ?? {}) };
}

export function langInfo(lang: Lang) {
  return LANGS.find((l) => l.code === lang)!;
}
