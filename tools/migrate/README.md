# Migration tools

Used to port the WordPress/Elementor pages to this repository, and to port new pages the same way.
The rendered WordPress pages and the downloaded `wp-content` files are inputs that live outside the
repo; point `SRC` (folder with the rendered `<page>-<lang>.html`) and `SITE` (folder with
`wp-content/...`) at them.

| Script | What it does |
|---|---|
| `port_home.py` | First port of the homepage (DE/EN/CZ) incl. header and footer. Kept for reference; re-running it overwrites hand edits. |
| `port_page.py` | Ports any page: `python tools/migrate/port_page.py <name> de=<file> en=<file> cs=<file>`. Writes `src/components/<name>/Sec*.astro`, `src/i18n/<name>.json`, copies media. |
| `strings.py` | For pages that exist only in German: `extract` lists all texts into a JSON table, you fill in `en`/`cs`, `apply` writes translated copies of the page (with link rewrites) that `port_page.py` then ports like real language versions. |
| `tidy.py` | Makes a ported page readable: `python tools/migrate/tidy.py <name>`. Section names come from `sections.json`; renames files to `NN-<section>.astro`, keys to `<section>_<words>`, moves script texts into the dictionary, formats with Prettier. |
| `purge_css.py` | `python tools/migrate/purge_css.py <page-de.html> legacy-<name>.css` keeps only the WordPress/Elementor CSS rules that match the page (and classes its scripts toggle). |

## Porting a new page

1. Download the rendered page per language (`Invoke-WebRequest https://sdx-app.com/<url> -OutFile <name>-de.html`)
   and any new `wp-content/uploads/elementor/css/post-<id>.css` and media into `SITE`.
2. Only German? `strings.py extract`, translate, `strings.py apply ... en` / `cs` with the link map.
3. `port_page.py <name> de=… en=… cs=…`, add the section names to `sections.json`, `tidy.py <name>`.
4. `purge_css.py <name>-de.html legacy-<name>.css`.
5. Write `src/templates/<Name>.astro` (copy `Audits.astro`), `src/i18n/<name>.meta.json` and one route
   file per language under `src/pages/`. Add links in `src/i18n/chrome.json` (header/footer).
6. `npm run build`, check every language at 390 / 820 / 1440 px against the live page.
