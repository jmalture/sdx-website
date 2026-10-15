# Editing the site

Everything is plain files: HTML-like `.astro` components, JSON with the texts, Markdown for the
legal pages. Run `npm run dev`, open http://localhost:4321 and every save shows up in the browser.

## Where things are

```
src/
  pages/                     URLs. One tiny file per URL, it only picks the template and language
    index.astro              /            -> <Home lang="de" />
    en/index.astro           /en/         -> <Home lang="en" />
    external-share/ …        /external-share/, /en/external-sharing/
    features/ audits/ …      /features/ /en/features/ /cs/funkce/, /audits/ /en/audits/ /cs/audity/
    impressum/ datenschutz/  plus /en/legal-notice/ and /en/privacy-policy/
    api/contact.ts           the contact form endpoint (the only server code)
  templates/                 one template per page: Home, Share, Features, Audits, Legal
  components/<page>/         the sections of a page, numbered in page order
    01-hero.astro            markup + the section's own CSS (<style is:global>) + its script
    index.astro              the list of sections; reorder or remove sections here
  components/Header.astro    site header (mega menu, language select)
  components/Footer.astro    site footer
  i18n/<page>.json           all texts of a page: { "de": {...}, "en": {...}, "cs": {...} }
  i18n/<page>.meta.json      <title> and meta description per language
  i18n/chrome.json           header ("h_…") and footer ("footer_…") texts and links
  content/legal/*.md         Impressum and Datenschutz, one Markdown file per language
  scripts/site.ts            shared behaviour: animations, sticky header, language switch, form
  styles/                    fonts.css, site.css (own rules), legacy*.css (generated, see below)
public/media/                images and videos, served as /media/<file>
```

## Common changes

**Change a text.** Search for the text in `src/i18n/<page>.json` and edit it in every language.
Keys are named `<section>_<words>`, e.g. `hero_share_files` is in `01-hero.astro`. A key that is
missing in `en` or `cs` falls back to German, so a new text shows up in German until it is
translated.

**Texts inside a section script** (for example the demo file names in an animation) are keys with
`_js_` in their name, e.g. `website_sync_js_press_release_nov`. The script reads them as `T.<name>`.
Two scripts on the External Share page (custom layouts, notifications) differ in more than their
texts between DE and EN; they are stored whole per language as `custom_layouts_script` and
`notifications_script`.

**Change a link.** Links that differ per language are keys with `_link_` (e.g. `hero_link_kontakt`).
Links that are the same in every language are written in the component.

**Change the look of a section.** Open the section file. Its CSS is in the `<style is:global>`
block at the top; class names are prefixed per page (`sdxt-`, `sxf-`, `sxa-`, `sfx-`), so a rule
only affects its own section. Leave the long `elementor-…` class names on the wrappers alone: the
generated `legacy*.css` uses them for spacing and layout.

**Title and description for Google.** `src/i18n/<page>.meta.json`.

**Header and footer.** Texts and links in `src/i18n/chrome.json`, markup in
`src/components/Header.astro` / `Footer.astro`.

**Legal pages.** Edit `src/content/legal/impressum.de.md` etc. like a document. A `\` at the end of
a line is a line break inside a paragraph, an empty line starts a new paragraph, `## ` is a heading.

**Images.** Put the file into `public/media/` and reference it as `/media/<file>`.

**Add a section.** Copy a section file, rename it (`05-new-thing.astro`), add it to the page's
`index.astro`, and add its texts to the page JSON with a new prefix.

## Generated files (do not edit by hand)

- `src/styles/legacy.css`, `legacy-share.css`, `legacy-features.css`, `legacy-audits.css`,
  `legacy-legal.css`: the WordPress/Elementor CSS each page still needs, reduced to the rules that
  match (`tools/migrate/purge_css.py`). Own CSS goes into the section or `site.css`.

## Before you push

```
npm run format     # Prettier, same formatting everywhere
npm run build      # must finish without errors
```

Pushing to `main` deploys (once the Hostinger app is connected). New pages and languages:
see `tools/migrate/README.md`.
