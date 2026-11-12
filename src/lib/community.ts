/** Helpers for the Community hub: URLs, labels, reading time, related articles. */
import { getCollection, type CollectionEntry } from 'astro:content';
import type { Lang } from '../i18n';

export type Article = CollectionEntry<'community'>;
export type CommunityLang = 'de' | 'en';

/** Base path of the hub per language. */
export const HUB: Record<CommunityLang, string> = { de: '/community/', en: '/en/community/' };

/** "de/intro-using-zip-upload" -> "intro-using-zip-upload" */
export const slugOf = (a: Article) => a.id.split('/').slice(1).join('/');
export const langOf = (a: Article) => a.id.split('/')[0] as CommunityLang;
export const urlOf = (a: Article) => `${HUB[langOf(a)]}${slugOf(a)}/`;

/** All published articles of one language, newest first. */
export async function articles(lang: CommunityLang): Promise<Article[]> {
  const all = await getCollection('community', (a) => langOf(a) === lang && !a.data.draft);
  return all.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

/** Colour per category: the SDX folder colours, used for the chip dot and the card accent. */
export const CATEGORY_COLOR: Record<Article['data']['category'], string> = {
  tutorial: '#2A73FF',
  knowledge: '#22C55E',
  news: '#FFA600',
  'use-case': '#C800FF',
};

/** Feature pages the "feature" tag links to. */
export const FEATURE_URL: Record<string, Record<CommunityLang, string>> = {
  'external-share': { de: '/external-share/', en: '/en/external-sharing/' },
  'zip-upload': { de: '/zip-upload/', en: '/en/zip-upload/' },
  preview: { de: '/preview/', en: '/en/preview/' },
  audits: { de: '/audits/', en: '/en/audits/' },
  platform: { de: '/features/', en: '/en/features/' },
};
export const FEATURE_NAME: Record<string, string> = {
  'external-share': 'External Share',
  'zip-upload': 'ZIP Upload',
  preview: 'Preview',
  audits: 'Audits',
  platform: 'SDX',
};

/** Plain words of an article: Markdown body plus the step texts (they are read too). */
export function wordsOf(a: Article): number {
  const text = [a.body ?? '', ...a.data.steps.map((s) => `${s.title} ${s.text} ${s.tip ?? ''}`)]
    .join(' ')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/[#>*_`|[\]()-]/g, ' ');
  return text.split(/\s+/).filter(Boolean).length;
}

/** Number of screenshots a reader has to look at (step images + images in the body). */
export function imagesOf(a: Article): number {
  return a.data.steps.filter((s) => s.image).length + ((a.body ?? '').match(/!\[/g) ?? []).length;
}

/**
 * Reading time in whole minutes, shown on cards and in the article byline.
 */
export function readingMinutes(words: number, images: number): number {
  // TODO(human): turn words and screenshots into minutes (screenshots slow tutorial readers down).
  return Math.max(1, Math.round(words / 200));
}

export const readingTime = (a: Article) => readingMinutes(wordsOf(a), imagesOf(a));

/** Up to `n` related articles: the ones named in `related` first, then same category, then newest. */
export function relatedTo(a: Article, pool: Article[], n = 3): Article[] {
  const others = pool.filter((b) => b.id !== a.id);
  const named = a.data.related.map((s) => others.find((b) => slugOf(b) === s)).filter(Boolean) as Article[];
  const rest = others
    .filter((b) => !named.includes(b))
    .sort((x, y) => Number(y.data.category === a.data.category) - Number(x.data.category === a.data.category));
  return [...named, ...rest].slice(0, n);
}

export const fmtDate = (d: Date, lang: Lang) =>
  d.toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
