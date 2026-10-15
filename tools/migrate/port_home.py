"""One-off migration: WordPress/Elementor homepage (DE/EN/CZ) -> one Astro template + dictionaries.

Inputs (outside the repo, see tools/migrate/README.md):
  SRC/home-{de,en,cs}.html   rendered pages from sdx-app.com
  SITE/wp-content/...        the CSS and media files those pages load
Outputs (inside the repo):
  src/components/home/*.astro    one component per homepage section
  src/components/Header.astro / Footer.astro
  src/i18n/home.json, src/i18n/chrome.json   texts per language
  src/styles/legacy.css          purged Elementor/theme CSS the markup still needs
  public/media/*                 images and videos used by the page
The DOM of the three languages is identical except for texts, attributes and links (checked
before porting), so the generator walks them in parallel and turns every difference into a key.
"""
import json, os, re, shutil, sys
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
import tinycss2

SRC = os.environ.get('SRC', '/home/claude/mig/src')
SITE = os.environ.get('SITE', '/home/claude/mig/site')
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LANGS = ['de', 'en', 'cs']
VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'track', 'wbr', 'area', 'col', 'embed', 'param'}
DROP_ATTRS = {'data-element_type', 'data-e-type', 'data-widget_type', 'data-settings', 'data-elementor-post-type',
              'data-elementor-id', 'data-elementor-type'}
MEDIA_RE = re.compile(r'(?:https://sdx-app\.com)?/wp-content/uploads/(?:\d{4}/\d{2}/)?([A-Za-z0-9._-]+\.(?:png|jpe?g|webp|mp4|svg))')

media_used = set()


def media(v):
    def rep(m):
        media_used.add(m.group(0))
        return '/media/' + m.group(1)
    return MEDIA_RE.sub(rep, v)


def esc_text(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return s.replace('{', '&#123;').replace('}', '&#125;')


def esc_attr(s):
    return s.replace('&', '&amp;').replace('"', '&quot;')


class Dict:
    def __init__(self, prefix):
        self.prefix, self.n, self.data = prefix, 0, {l: {} for l in LANGS}

    def add(self, vals, hint='t'):
        # reuse an existing key with the same values (repeated labels)
        for k, v in self.data['de'].items():
            if v == vals[0] and all(self.data[l][k] == vals[i] for i, l in enumerate(LANGS)):
                return k
        self.n += 1
        k = f'{self.prefix}{hint}{self.n}'
        for i, l in enumerate(LANGS):
            self.data[l][k] = vals[i]
        return k


def anim_attrs(el):
    """Elementor entrance animation -> data-anim / data-anim-delay for src/scripts/site.ts."""
    st = el.get('data-settings')
    if not st:
        return ''
    try:
        d = json.loads(st)
    except ValueError:
        return ''
    a = d.get('_animation') or d.get('animation')
    if not a:
        return ''
    return f' data-anim="{a}" data-anim-delay="{d.get("_animation_delay", d.get("animation_delay", 0)) or 0}"'


def render(nodes, D, dict_var):
    de = nodes[0]
    if isinstance(de, Comment):
        return ''
    if isinstance(de, NavigableString):
        vals = [str(n) for n in nodes]
        if len(set(vals)) == 1:
            return esc_text(vals[0])
        lead = re.match(r'^\s*', vals[0]).group(0)
        trail = re.search(r'\s*$', vals[0]).group(0)
        k = D.add([v.strip() for v in vals])
        return f'{lead}{{{dict_var}.{k}}}{trail}'
    name = de.name
    # attributes
    parts = []
    for a, v in de.attrs.items():
        if a in DROP_ATTRS:
            continue
        vals = []
        for n in nodes:
            x = n.attrs.get(a, '')
            x = ' '.join(x) if isinstance(x, list) else x
            vals.append(media(x))
        if a in ('class', 'data-id'):
            vals = [vals[0]] * len(nodes)  # from the base language (other copies only differ in Elementor ids)
        if len(set(vals)) == 1:
            parts.append(a if vals[0] == '' and a not in ('alt', 'value', 'content') else f'{a}="{esc_attr(vals[0])}"')
        else:
            k = D.add(vals, 'a')
            parts.append(f'{a}={{{dict_var}.{k}}}')
    attrs = (' ' + ' '.join(parts)) if parts else ''
    attrs += anim_attrs(de)
    if name in ('style', 'script'):
        bodies = [n.string or n.get_text() for n in nodes]
        if name == 'script' and 'lang_choice_polylang' in bodies[0]:
            return ''  # replaced by site.ts
        body = media(bodies[0])
        if len(set(bodies)) == 1:
            kind = 'is:global' if name == 'style' else 'is:inline'
            return f'<{name} {kind}{attrs}>{body}</{name}>'
        k = D.add([media(b) for b in bodies], 'raw')
        kind = 'is:global' if name == 'style' else 'is:inline'
        return f'<{name} {kind}{attrs} set:html={{{dict_var}.{k}}} />'
    if name in VOID:
        return f'<{name}{attrs} />'
    kids = [list(n.children) for n in nodes]
    if len({len(k) for k in kids}) != 1:
        # structure differs: keep the whole inner HTML per language
        k = D.add([media(n.decode_contents()) for n in nodes], 'html')
        return f'<{name}{attrs} set:html={{{dict_var}.{k}}}></{name}>'
    inner = ''.join(render(c, D, dict_var) for c in zip(*kids))
    return f'<{name}{attrs}>{inner}</{name}>'


def load(lang):
    return BeautifulSoup(open(f'{SRC}/home-{lang}.html', encoding='utf-8').read(), 'lxml')


def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(text)


def component(markup, dict_import, dict_name):
    return ('---\n' + f"import {{ dict }} from '../../i18n';\n" +
            f"import data from '../../i18n/{dict_import}.json';\n" +
            "const { lang } = Astro.props;\n" + f"const {dict_name} = dict(data, lang);\n---\n" + markup + '\n')


def main():
    docs = {l: load(l) for l in LANGS}
    home = Dict('')
    pages = {l: docs[l].select_one('[data-elementor-type=wp-page]') for l in LANGS}
    secs = {l: pages[l].find_all(attrs={'data-element_type': 'container'}, recursive=False) for l in LANGS}
    names = []
    for i, de_sec in enumerate(secs['de']):
        sid = de_sec.get('data-id')
        D = Dict(f'{sid}_')
        markup = render([secs[l][i] for l in LANGS], D, 't')
        for l in LANGS:
            home.data[l].update(D.data[l])
        comp = ''.join(w.capitalize() for w in re.split(r'[^a-z0-9]', 'sec ' + sid) if w)
        names.append((comp, sid))
        write(f'src/components/home/{comp}.astro', component(markup, 'home', 't').replace('../../i18n', '../../i18n'))
    write('src/i18n/home.json', json.dumps(home.data, ensure_ascii=False, indent=1))
    imports = '\n'.join(f"import {c} from './{c}.astro';" for c, _ in names)
    body = '\n'.join(f'  <{c} lang={{lang}} />' for c, _ in names)
    write('src/components/home/index.astro', '---\n' + imports + '\nconst { lang } = Astro.props;\n---\n'
          '<div class="elementor elementor-358">\n' + body + '\n</div>\n')

    # footer: identical structure in all languages
    chrome = Dict('f_')
    foots = [docs[l].select_one('[data-elementor-type=footer]') for l in LANGS]
    fm = render(foots, chrome, 't')
    fm = re.sub(r'^<footer[^>]*>', '<footer class="elementor elementor-444 elementor-location-footer">', fm)
    write('src/components/Footer.astro', component(fm, 'chrome', 't').replace('../../i18n', '../i18n'))
    # header: DE structure, EN/CZ texts come from chrome.json (filled by hand, see README)
    hdr = docs['de'].select_one('[data-elementor-type=header]')
    H = Dict('h_')
    hm = render([hdr, hdr, hdr], H, 't')
    hm = re.sub(r'^<header[^>]*>', '<header class="elementor elementor-213 elementor-location-header sx-header">', hm)
    open(os.path.join(OUT, 'tools/migrate/header-strings.de.json'), 'w').write(json.dumps(
        [s for s in hdr.stripped_strings], ensure_ascii=False, indent=1))
    write('src/components/Header.raw.astro', hm)
    write('src/i18n/chrome.json', json.dumps(chrome.data, ensure_ascii=False, indent=1))

    # meta per language
    meta = {}
    for l in LANGS:
        d = docs[l]
        g = lambda n: (d.find('meta', attrs={'name': n}) or d.find('meta', attrs={'property': n}) or {}).get('content', '')
        meta[l] = {'title': d.title.text, 'description': g('description')}
    write('src/i18n/home.meta.json', json.dumps(meta, ensure_ascii=False, indent=1))

    # media
    for m in sorted(media_used):
        rel = re.sub(r'^https://sdx-app\.com', '', m).lstrip('/')
        src = os.path.join(SITE, rel)
        dst = os.path.join(OUT, 'public/media', os.path.basename(rel))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copyfile(src, dst)
        else:
            print('MISSING media', m)

    # body classes kept for CSS matching
    print('sections', [s for _, s in names], 'home keys', len(home.data['de']), 'footer keys', len(chrome.data['de']))


if __name__ == '__main__':
    main()
