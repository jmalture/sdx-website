/**
 * Content collections.
 *
 * community: articles of the Community hub (/community/, /en/community/), one Markdown file per article and
 * language: src/content/community/<lang>/<slug>.md. The same slug in both languages = translations of each other.
 * Frontmatter is checked against the schema below at build time, so a typo in a category fails the build.
 */
import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';

export const CATEGORIES = ['tutorial', 'knowledge', 'news', 'use-case'] as const;
export const LEVELS = ['beginner', 'advanced', 'expert'] as const;

const community = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/community' }),
  schema: z.object({
    title: z.string(),
    /** One or two sentences for the card, the meta description and the article lead. */
    description: z.string(),
    /** Publication date; "updated" is shown when the article was revised. */
    date: z.coerce.date(),
    updated: z.coerce.date().optional(),
    author: z.string().default('SDX Team'),
    authorRole: z.string().optional(),
    category: z.enum(CATEGORIES),
    level: z.enum(LEVELS).default('beginner'),
    /** Feature the article is about (shown as a tag, links to the feature page). */
    feature: z.enum(['external-share', 'zip-upload', 'preview', 'audits', 'platform']).optional(),
    /** "Für wen": roles or situations, 2 to 4 short items. */
    audience: z.array(z.string()).default([]),
    /** "Was Sie lernen": 2 to 4 outcomes. */
    outcomes: z.array(z.string()).default([]),
    /** "Was Sie brauchen": prerequisites, e.g. an SDX account with edit rights. */
    requirements: z.array(z.string()).default([]),
    /** Card and hero image, a path under /media/. */
    cover: z.string(),
    coverAlt: z.string(),
    /** Opening paragraphs in the author's voice ("Heute zeige ich Ihnen …"), shown above the steps. **bold** works. */
    intro: z.array(z.string()).default([]),
    /** Step-by-step guide, rendered as numbered steps with screenshots before the Markdown body. */
    steps: z
      .array(
        z.object({
          title: z.string(),
          text: z.string(),
          image: z.string().optional(),
          alt: z.string().optional(),
          /** Short hint shown in a blue box under the step. */
          tip: z.string().optional(),
        }),
      )
      .default([]),
    /** Slugs of related articles (same language); when empty, articles of the same category are suggested. */
    related: z.array(z.string()).default([]),
    /** Learning path order: lower numbers are shown first in "Start here". */
    order: z.number().default(100),
    draft: z.boolean().default(false),
  }),
});

export const collections = { community };
