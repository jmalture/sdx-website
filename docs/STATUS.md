# Status: known items (not failures)

Read by the verify-loop checker together with `docs/CHECKLIST.md`.

## Community hub (2026-11-12)

- Hidden on purpose: no menu or footer link, `noindex, follow`, not in the sitemap. Reachable by URL only.
- ZIP Upload article: the "additive update" statement comes from Ben's feature document and is not yet checked
  on sdx-dev1 (to confirm).
- Article covers reuse existing site media (`/media/sxf-hero-share-page.webp`) and sdx-dev1 screenshots.

## Site-wide, older than the Community hub (shared header and footer)

- Capture lists `nav.sx-side-panel` as overflow at 390: the closed off-canvas menu sits off screen to the right,
  `body` has `overflow-x: clip`, so the page never scrolls sideways (`scrollWidth === innerWidth`, checked).
- Footer links are 21 px tall at 390 (legacy Elementor footer markup used on every page). Bigger tap targets
  there change the footer on all pages: a separate task, not part of the Community work.
- The capture does not find the mobile menu toggle (the site's own burger markup), so no menu-open shot.
