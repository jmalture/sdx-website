# sdx-website

The sdx-app.com marketing website: static pages built with [Astro](https://astro.build), plus one small
Node endpoint for the contact form. Replaces the WordPress/Elementor site (Jira D26-1565).

## How it works

- **One template per page, all languages.** `src/templates/Home.astro` renders the homepage; the
  route files `src/pages/index.astro`, `src/pages/en/index.astro` and `src/pages/cs/index.astro`
  only pass the language. Texts live in `src/i18n/<page>.json` as `{ "de": {...}, "en": {...}, "cs": {...} }`;
  missing keys fall back to German.
- **Language switch** = link to the same template in the other language (`/`, `/en/`, `/cs/`), so
  every language is real, indexable HTML with `hreflang` and canonical tags.
- **Sections** are components in `src/components/<page>/`. Each one carries its own CSS and the small
  vanilla scripts it needs (copied from the former Elementor HTML widgets).
- `src/styles/legacy.css` holds the Elementor/theme CSS the ported markup still relies on, reduced to
  the rules that match (see `tools/migrate/purge_css.py`). It shrinks as sections are cleaned up.
- `src/scripts/site.ts` replaces the bits of Elementor JS the design used: entrance animations,
  sticky header, language select, contact form submit.
- `src/pages/api/contact.ts` is the only server route: validation, honeypot, rate limit, the enquiry
  is stored as JSON lines before the mail is sent over SMTP.

## Commands

```
npm install
npm run dev       # http://localhost:4321
npm run build     # static pages in dist/client, server in dist/server
npm start         # serves dist (needs a build first)
```

## Deployment (Hostinger Node.js app)

- Build command `npm run build`, start command `npm start` (`node ./dist/server/entry.mjs`),
  Node 20.3 or newer.
- Environment variables: see `.env.example` (SMTP settings, recipients, `SUBMISSIONS_DIR`).
- `HOST` and `PORT` are read by the server; Hostinger sets `PORT`.

## Performance rules (same as our PHP themes)

- No third-party requests; fonts self-hosted (Inter variable, latin preloaded, latin-ext on demand).
- All CSS inlined into the HTML; scripts are small, deferred modules.
- One LCP image per page with `fetchpriority="high"`; everything else lazy; videos `preload="none"`.
- Target: 100 in PageSpeed (mobile and desktop) on every page and language.

See `docs/MIGRATION.md` for the plan, work packages and status.
