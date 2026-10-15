"""Collect the WordPress/Elementor CSS the homepage loads and keep only rules that can match it.

Selector matching runs against the rendered DE homepage (header, page, footer; EN/CZ share the
same DOM). Pseudo-classes/elements are ignored for matching, and classes that scripts add at
runtime are treated as present, so hover/focus/animation states survive. Output order follows
the original <link> order, so the cascade stays the same.
"""
import os, re, sys
import tinycss2
from bs4 import BeautifulSoup
import soupsieve as sv

SRC = os.environ.get('SRC', '/home/claude/mig/src')
SITE = os.environ.get('SITE', '/home/claude/mig/site')
# usage: purge_css.py [<rendered page in SRC> <output css in src/styles>]  (default: homepage -> legacy.css)
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'home-de.html'
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src/styles',
                                   sys.argv[2] if len(sys.argv) > 2 else 'legacy.css'))
SKIP = ('themer-blocks.css', 'swiper.min.css', 'e-swiper.min.css', 'google-fonts/')

FILES = [  # same order as the <link> tags on the live page (fonts, swiper and themer blocks left out)
    'wp-content/themes/hello-elementor/assets/css/reset.css',
    'wp-content/themes/hello-elementor/assets/css/theme.css',
    'wp-content/themes/hello-elementor/assets/css/header-footer.css',
    'wp-content/plugins/elementor/assets/css/frontend.min.css',
    'wp-content/uploads/elementor/css/post-6.css',
    'wp-content/plugins/elementor-pro/assets/css/modules/sticky.min.css',
    'wp-content/plugins/elementor/assets/css/widget-icon-list.min.css',
    'wp-content/plugins/elementor/assets/css/widget-heading.min.css',
    'wp-content/plugins/elementor/assets/css/widget-image.min.css',
    'wp-content/plugins/elementor-pro/assets/css/widget-form.min.css',
    'wp-content/uploads/elementor/css/post-358.css',
    'wp-content/uploads/elementor/css/base-desktop.css',
    'wp-content/uploads/elementor/css/base-mobile.css',
    'wp-content/uploads/elementor/css/post-213.css',
    'wp-content/uploads/elementor/css/post-444.css',
]
# classes added at runtime (Elementor JS replacements in src/scripts/site.ts, section scripts)
RUNTIME = {'animated', 'elementor-sticky--effects', 'elementor-sticky--active', 'elementor-sticky', 'is-open',
           'is-closed', 'is-active', 'is-on', 'in', 'is-visible', 'e-lazyloaded', 'elementor-message',
           'elementor-message-success', 'elementor-message-danger', 'elementor-form-waiting',
           'elementor-error', 'elementor-field-type-acceptance'}

doc = BeautifulSoup(open(f'{SRC}/{PAGE}', encoding='utf-8').read(), 'lxml')
if len(sys.argv) > 1:  # other pages: take the stylesheets in the order the page links them
    FILES = [re.sub(r'^https://sdx-app\.com/', '', l['href']).split('?')[0] for l in doc.select('link[rel=stylesheet]')
             if 'sdx-app.com/wp-content/' in l['href'] and not any(x in l['href'] for x in SKIP)]
# classes the page's own inline scripts toggle (classList.add/toggle/remove, also several args)
for sc in doc.find_all('script'):
    for args in re.findall(r'classList\.(?:add|toggle|remove)\(([^)]*)\)', sc.get_text()):
        RUNTIME.update(re.findall(r"['\"]([A-Za-z][\w-]*)['\"]", args))
# add runtime classes everywhere they could appear so selectors using them still match
anims = set()
for el in doc.select('.elementor-invisible'):
    el['class'] = el.get('class', []) + ['animated']
for el in doc.select('[data-settings]'):
    m = re.search(r'"_?animation":"([^"]+)"', el['data-settings'])
    if m:
        el['class'] = el.get('class', []) + [m.group(1)]
        anims.add(m.group(1))
hdr = doc.select_one('[data-elementor-type=header] > .e-con')
if hdr:
    hdr['class'] += ['elementor-sticky', 'elementor-sticky--active', 'elementor-sticky--effects']

PSEUDO = re.compile(r'::?[a-zA-Z-]+(\((?:[^()]|\([^()]*\))*\))?')


def matches(sel):
    s = sel.strip()
    if not s:
        return False
    if s in (':root', 'html', 'body', '*') or s.startswith(':root') or s.startswith('html'):
        return True
    for c in RUNTIME:
        s = re.sub(r'\.' + re.escape(c) + r'(?![\w-])', '', s)
    s = PSEUDO.sub('', s)
    s = re.sub(r'\s*([>+~])\s*$', '', s).strip()
    if not s or s in ('>', '+', '~'):
        return True
    try:
        return doc.select_one(s) is not None
    except Exception:
        return True  # unknown syntax: keep


def purge(rules):
    out = []
    for r in rules:
        if r.type == 'qualified-rule':
            sel = tinycss2.serialize(r.prelude)
            keep = [x for x in split_selectors(sel) if matches(x)]
            if keep:
                out.append(', '.join(x.strip() for x in keep) + '{' + tinycss2.serialize(r.content).strip() + '}')
        elif r.type == 'at-rule':
            kw = r.lower_at_keyword
            if kw in ('media', 'supports', 'container', 'layer') and r.content is not None:
                inner = purge(tinycss2.parse_rule_list(r.content, skip_comments=True, skip_whitespace=True))
                if inner:
                    out.append('@' + r.at_keyword + tinycss2.serialize(r.prelude) + '{' + ''.join(inner) + '}')
            elif kw == 'keyframes' or kw.endswith('keyframes'):
                out.append(tinycss2.serialize([r]))
            elif kw in ('font-face', 'import', 'charset', 'custom-media'):
                continue
            else:
                out.append(tinycss2.serialize([r]))
    return out


def split_selectors(sel):
    parts, depth, cur = [], 0, ''
    for ch in sel:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += ch
    parts.append(cur)
    return parts


chunks, total_in = [], 0
for f in FILES:
    css = open(os.path.join(SITE, f), encoding='utf-8').read()
    total_in += len(css)
    rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
    kept = purge(rules)
    chunks.append(f'/* {os.path.basename(f)} */\n' + '\n'.join(kept))
# inline <style> blocks from <head> that matter (WP global styles, Elementor inline)
for st in doc.head.find_all('style'):
    if st.get('id') in ('global-styles-inline-css', 'elementor-frontend-inline-css'):
        kept = purge(tinycss2.parse_stylesheet(st.get_text(), skip_comments=True, skip_whitespace=True))
        chunks.append(f'/* {st.get("id")} */\n' + '\n'.join(kept))
out = '\n'.join(chunks)
out = re.sub(r'(?:https://sdx-app\.com)?/wp-content/uploads/\d{4}/\d{2}/', '/media/', out)  # media is served from /media/
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(out + '\n')
print(f'in {total_in} bytes -> out {len(out)} bytes; animations {sorted(anims)}')
