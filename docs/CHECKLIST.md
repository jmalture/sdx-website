# Checklist: sdx-website

Project-specific checks for the verify loop (verify-loop skill, profile `astro-site`). The profile holds the
general checks for every Astro site; this file adds what only matters here. A note that would apply to any
site on this stack moves to the profile.

## Before every push

- `npm run build` passes, `npm run check:format` passes.
- Pushing to `main` deploys to Hostinger in about 2-3 minutes; check the live page after that, not only local.

## Layout

- Every section's content lines up with the header's content box (1180 px; 130-1310 at 1440 wide).
  Community pages use `.sxf.scx .sxf-wrap { max-width: 1180px }`; other `.sxf` pages still use 1280 px.
- No section is narrower than the header unless it is a deliberate reading column.
- `.scx .scx-frame` resets `margin`: any spacing on a framed image needs the `.scx` prefix too, or it is lost
  (the article cover once sat glued to the byline for this reason).

## Community hub (`/community/`, `/en/community/`)

- Hidden on purpose: no link in header, mobile menu or footer; `noindex, follow`; left out of the sitemap.
  Not a failure. To publish: restore the links (texts in `src/i18n/chrome.json`), remove the robots meta in
  both Community templates and the `/community/` check in `astro.config.mjs`.
- Filter bar: categories and search on one row, levels below; on phones search comes first.
- Switching a filter, a level or typing a search never moves the page: the results area keeps the height
  of the full list (`reserve()` in `CommunityHub.astro`). Arriving cards ease in; reduced motion skips that.
- The filter state lives in the URL (`?cat=&level=&q=`) and survives a reload.
- Empty result shows the empty state with a working reset button.

## Community article (`/community/<slug>/`)

- Cover image has clear space above it (48 px from the byline).
- Content column is the full 1180 px. The sticky TOC ("Inhalt") hangs in the left margin from 1640 px wide
  and is hidden below; the active TOC entry follows the scroll.
- "Weiterlesen" and the CTA line up with the article above.
- Reading time = words (intro + steps + body) / 50 per minute (`src/lib/community.ts`); card, byline and
  JSON-LD show the same number.
- Step screenshots open in the lightbox; Esc and the close button work; focus returns to the screenshot.
- Screenshots come from sdx-dev1 and show no client names.

## Known open items (not failures)

- ZIP Upload article: the "additive update" claim comes from Ben's feature doc and is not yet checked on dev1.
