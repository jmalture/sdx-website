"""Port one more WordPress/Elementor page (all its languages) to an Astro template + dictionary.

Usage:  python tools/migrate/port_page.py <name> <lang>=<file> [<lang>=<file> ...]
  e.g.  python tools/migrate/port_page.py share de=share-de.html en=share-en.html

The first language is the base (its classes and structure are used; Elementor CSS is keyed to its
element ids). The pages must have the same DOM apart from texts, attributes and links.
Writes src/components/<name>/Sec*.astro + index.astro and src/i18n/<name>.json, copies media.
Header and footer are shared and not touched. Run purge_css.py for the page's CSS afterwards.
"""
import json, os, re, shutil, sys
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))
import port_home as ph  # noqa: E402  (render/Dict/media helpers)


def main(name, files):
    langs = [l for l, _ in files]
    ph.LANGS[:] = langs  # Dict and render iterate over ph.LANGS
    docs = {l: BeautifulSoup(open(os.path.join(ph.SRC, f), encoding='utf-8').read(), 'lxml') for l, f in files}
    pages = {l: docs[l].select_one('[data-elementor-type=wp-page]') for l in langs}
    page_id = pages[langs[0]].get('data-elementor-id')
    secs = {l: pages[l].find_all(attrs={'data-element_type': 'container'}, recursive=False) for l in langs}
    assert len({len(s) for s in secs.values()}) == 1, 'section count differs between languages'
    data = {l: {} for l in langs}
    names = []
    for i, base in enumerate(secs[langs[0]]):
        sid = base.get('data-id')
        D = ph.Dict(f'{sid}_' if sid[0].isalpha() else f's{sid}_')  # keys must be valid identifiers
        markup = ph.render([secs[l][i] for l in langs], D, 't')
        for l in langs:
            data[l].update(D.data[l])
        comp = ''.join(w.capitalize() for w in re.split(r'[^a-z0-9]', 'sec ' + sid) if w)
        names.append(comp)
        ph.write(f'src/components/{name}/{comp}.astro', ph.component(markup, name, 't'))
    ph.write(f'src/i18n/{name}.json', json.dumps(data, ensure_ascii=False, indent=1))
    imports = '\n'.join(f"import {c} from './{c}.astro';" for c in names)
    body = '\n'.join(f'  <{c} lang={{lang}} />' for c in names)
    ph.write(f'src/components/{name}/index.astro', '---\n' + imports + '\nconst { lang } = Astro.props;\n---\n'
             f'<div class="elementor elementor-{page_id}">\n' + body + '\n</div>\n')
    for m in sorted(ph.media_used):
        rel = re.sub(r'^https://sdx-app\.com', '', m).lstrip('/')
        src = os.path.join(ph.SITE, rel)
        dst = os.path.join(ph.OUT, 'public/media', os.path.basename(rel))
        if os.path.exists(src):
            shutil.copyfile(src, dst)
        else:
            print('MISSING media', m)
    print('page', page_id, 'sections', names, 'keys', len(data[langs[0]]))


if __name__ == '__main__':
    main(sys.argv[1], [a.split('=', 1) for a in sys.argv[2:]])
