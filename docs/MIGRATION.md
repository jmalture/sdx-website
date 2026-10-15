# Migration: WordPress/Elementor → Astro (Jira D26-1565)

Goal: sdx-app.com with identical design and content, one template per page for all languages,
100/100 PageSpeed, deployed from this repository to a Hostinger Node.js app.

## Starting point (inventory, 15.10.2026)

| Page | WordPress | Languages | Built from |
|---|---|---|---|
| Homepage | 358 / 455 / 480 | DE `/`, EN `/en/`, CZ `/cs/` | 27 HTML widgets + native hero, logo band, Why SDX, SDX unterwegs, form |
| Features overview | 759 | DE `/features/` | HTML widgets |
| External Share | 610 / 650 | DE `/external-share/`, EN `/en/external-sharing/` | 18 HTML widgets |
| Audits | 696 | DE `/audits/` | HTML widgets |
| Impressum / Legal notice | 244 / 245 | DE `/impressum/`, EN `/en/legal-notice/` | Gutenberg text |
| Datenschutz / Privacy policy | 602 / 3 | DE `/datenschutz/`, EN `/en/privacy-policy/` | Gutenberg text |
| Header / footer | 213, 21, 484 / 444, 39, 488 | per language | Elementor templates |

Per page WordPress loads 14 scripts (incl. jQuery) and 17–20 stylesheets. The three language copies
of each page have the same DOM; only texts, attributes and links differ.

## Method

1. `tools/migrate/port_home.py` walks the DE/EN/CZ render of a page in parallel and writes one
   component per section; every text or attribute that differs becomes a dictionary key.
2. `tools/migrate/purge_css.py` keeps only the WordPress/Elementor CSS rules that can match the page.
3. Elementor runtime features are replaced by `src/scripts/site.ts` (animations, sticky header,
   language select, form) and plain CSS (logo carousel).
4. Visual check against the live site at 390 / 820 / 1440 px, then PageSpeed.
   Each page gets its own purged stylesheet (`legacy.css` homepage, `legacy-share.css` External Share),
   imported by its template, so a page only carries the CSS it needs.
5. Afterwards each section can be cleaned up (Elementor wrapper classes removed, its CSS moved
   into the component) without changing the look; `legacy.css` shrinks accordingly.

The migration tools read files outside the repo (rendered pages and downloaded CSS/media); paths
are set with the `SRC` and `SITE` environment variables.

## Work packages and status

| # | Package | Status |
|---|---|---|
| 1 | Project setup: repo, Astro, fonts, base layout, header with mega menu + language switch, footer | done (v0.1) |
| 2 | i18n: one template per page, dictionaries de/en/cs, hreflang, canonical, switcher | done for all pages |
| 3 | Homepage port (all 15 sections, DE/EN/CZ) | done (v0.1), visual check against live pending |
| 4 | Features overview, External Share (DE/EN), Audits | done: External Share DE/EN, Features and Audits DE/EN/CZ (EN/CZ translated, review pending) |
| 5 | Impressum, Datenschutz (DE/EN) | done as Markdown (live text + Impressum fixes: e-mail, DDG); Datenschutz [PRÜFEN] points and Wordfence/WordPress parts to be updated before launch |
| 6 | Media: AVIF/WebP with srcset for all images, posters, OG image | open |
| 7 | Contact form endpoint + SMTP | done (code), SMTP account and recipient pending |
| 8 | SEO: meta per page, JSON-LD, sitemap, robots.txt, 301 redirects from WordPress URLs | partly (meta, hreflang, sitemap) |
| 9 | Performance and QA: PageSpeed 100 on all pages and languages, a11y, iPhone, visual diff | open (baseline below) |
| 10 | Hostinger Node.js app, GitHub auto-deploy, staging, launch, domain switch | open |

## PageSpeed baseline (local build, no compression, 15.10.2026)

Homepage DE: mobile 78 (LCP 5.3 s: hero PNG), desktop 98; accessibility 93, best practices 100, SEO 100.
Next steps for 100: AVIF/WebP hero with correct `sizes`, gzip/brotli on the server, smaller
inlined CSS (section cleanup), contrast fixes flagged by Lighthouse.

## Readable code

After porting, `tools/migrate/tidy.py` gives every section a file name and every text a readable key
(`hero_share_files` instead of `sxf01_t3`) and formats the code. How to edit: `docs/EDITING.md`.

## Open points

- Form recipient and SMTP mailbox (the WordPress form still sends to hostinger@alture.io).
- Header: DE has the Features mega menu, EN/CZ headers in WordPress still had older menus. The new
  site uses the mega menu in all languages (EN/CZ texts translated, links to DE pages where no
  translation exists yet).
- Content editing after launch: in git (developer/Claude) for now; a Git-based admin UI (Keystatic) can be added later.
- Datenschutz: the Wordfence section and other WordPress-specific parts no longer apply on the new site; contact form storage changed (JSON file before e-mail). Update before launch.
