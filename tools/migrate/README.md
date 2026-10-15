# Migration tools (one-off)

Used once to port the WordPress/Elementor pages; kept for reference and for porting the remaining pages.

- `port_home.py`: rendered DE/EN/CZ homepage → section components + `src/i18n/home.json`, footer, header base.
- `port_page.py`: same for any other page, e.g. `python tools/migrate/port_page.py share de=share-de.html en=share-en.html`
  → `src/components/share/*`, `src/i18n/share.json`. Template, route files and meta are written by hand.
- `purge_css.py`: WordPress/Elementor CSS → `src/styles/legacy.css` (only rules that match the page).

Inputs live outside the repo: `SRC` = folder with `home-de.html`, `home-en.html`, `home-cs.html`
(rendered pages), `SITE` = folder with the downloaded `wp-content/...` CSS and media.
After the first port the components were edited by hand (logo band, form, header), so re-running
the port overwrites those edits.

Other pages: `python tools/migrate/purge_css.py share-de.html legacy-share.css` (stylesheets taken in the page's own link order).
