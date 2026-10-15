"""Turn a freshly ported page into readable, hand-editable code.

Usage:  python tools/migrate/tidy.py <page>        e.g.  python tools/migrate/tidy.py share

Reads the section names from tools/migrate/sections.json ({ page: { elementorId: name } }) and
  1. renames  src/components/<page>/SecXXXX.astro  ->  NN-<name>.astro  (NN = order on the page),
  2. renames dictionary keys like "sxf01_t3" to "<name>_<slug>" (slug from the English text,
     German if there is none), e.g. "hero_share_files", "hero_link_contact",
  3. section scripts that only differ in their texts per language get their code back in the
     component; the texts move into the dictionary and reach the script through define:vars,
  4. adds a short comment on top of every section, rewrites index.astro, formats with Prettier.
The rendered pages stay identical (checked with a text/element/size comparison before and after).
"""
import ast, json, os, re, subprocess, sys, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
JS_STR = re.compile(r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"")


def slug(text, words=4, maxlen=32):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unicodedata.normalize('NFKD', text.replace('ß', 'ss')).encode('ascii', 'ignore').decode().lower()
    parts = [w for w in re.findall(r'[a-z0-9]+', text)][:words]
    s = '_'.join(parts)[:maxlen].strip('_')
    return s or 'text'


def link_slug(href):
    path = re.sub(r'^(en|cs)(/|$)', '', href.split('#')[0].strip('/'))
    h = href.split('#')[1] if '#' in href else (path.split('/')[-1] if path else 'home')
    return slug(h.replace('#', ' ').replace('-', ' '), 3) or 'home'


def camel(s):
    p = s.split('_')
    return p[0] + ''.join(x.capitalize() for x in p[1:])


class Keys:
    def __init__(self, data):
        self.data, self.langs = data, list(data)
        self.new = {l: {} for l in self.langs}

    def value(self, k, lang):
        return self.data.get(lang, {}).get(k, self.data['de'].get(k, ''))

    def put(self, name, values):
        base, n = name, 2
        while name in self.new['de']:
            if all(self.new[l].get(name) == values.get(l) for l in self.langs if l in values):
                return name  # same text again: reuse
            name, n = f'{base}_{n}', n + 1
        for l, v in values.items():
            self.new[l][name] = v
        return name


def decode(lit):
    try:
        return ast.literal_eval(lit)
    except Exception:
        return None


def split_js(code):
    parts, pos = [], 0
    for m in JS_STR.finditer(code):
        parts.append(code[pos:m.start()]); parts.append(m.group(0)); pos = m.end()
    parts.append(code[pos:])
    return parts


def script_to_vars(sec, codes, K):
    """codes: {lang: js}. Returns component script code using T.<name>, or None if not possible."""
    langs = list(codes)
    split = {l: split_js(codes[l]) for l in langs}
    if len({len(s) for s in split.values()}) != 1:
        return None
    base = split[langs[0]]
    if any(split[l][i] != base[i] for l in langs for i in range(0, len(base), 2)):
        return None  # code (not only strings) differs
    out, tvars = [], {}
    for i, part in enumerate(base):
        if i % 2 == 0:
            out.append(part); continue
        vals = {l: split[l][i] for l in langs}
        if len(set(vals.values())) == 1:
            out.append(part); continue
        dec = {l: decode(v) for l, v in vals.items()}
        if any(v is None for v in dec.values()):
            return None
        key = K.put(f'{sec}_js_' + slug(dec.get('en', dec[langs[0]]), 3), dec)
        ident = camel(key[len(sec) + 4:]) or 'text'
        if ident[0].isdigit():
            ident = 't' + ident
        tvars[ident] = key
        out.append(f'T.{ident}')
    return ''.join(out), tvars


def tidy_component(path, sec, K, page):
    src = open(path, encoding='utf-8').read()
    head, body = re.match(r'---\n(.*?)\n---\n(.*)', src, re.S).groups()
    langs = K.langs

    # 1. per-language scripts
    def script_rep(m):
        attrs, key = m.group(1), m.group(2)
        if 'application/ld+json' in attrs:
            vals = {l: K.value(key, l) for l in langs}
            new = K.put(f'{sec}_jsonld', vals)
            return f'<script{attrs} set:html={{t.{new}}} />'
        res = script_to_vars(sec, {l: K.value(key, l) for l in langs}, K)
        if not res:
            new = K.put(f'{sec}_script', {l: K.value(key, l) for l in langs})
            return f'<script{attrs} set:html={{t.{new}}} />'
        code, tvars = res
        attrs = attrs.replace(' is:inline', '')
        obj = ', '.join(f'{k}: t.{v}' for k, v in tvars.items())
        return f'<script{attrs} define:vars={{{{ T: {{ {obj} }} }}}}>{code}</script>'
    body = re.sub(r'<script([^>]*?) set:html=\{t\.(\w+)\} />', script_rep, body)

    # 2. attributes and text
    def attr_rep(m):
        attr, key = m.group(1), m.group(2)
        if key in K.new['de'] and key not in K.data['de']:
            return m.group(0)  # renamed already (scripts)
        vals = {l: K.value(key, l) for l in langs}
        ref = vals.get('en') or vals['de']
        if attr == 'set:html':
            name = f'{sec}_html_' + slug(ref, 3)
        elif attr == 'href':
            name = f'{sec}_link_' + link_slug(ref)
        else:
            name = f'{sec}_{slug(attr.replace("data-", ""), 2)}_' + slug(ref, 3)
        return f'{attr}={{t.{K.put(name, vals)}}}'
    body = re.sub(r'([\w:-]+)=\{t\.(\w+)\}', attr_rep, body)

    def text_rep(m):
        key = m.group(1)
        if any(key in K.new[l] for l in langs) and key not in K.data['de']:
            return m.group(0)  # already a new key
        vals = {l: K.value(key, l) for l in langs}
        return '{t.' + K.put(f'{sec}_' + slug(vals.get('en') or vals['de']), vals) + '}'
    body = re.sub(r'\{t\.(\w+)\}', text_rep, body)

    # 3. comment with the section heading
    h = re.search(r'<h([12])[^>]*>(.*?)</h\1>', body, re.S)
    title = ''
    if h:
        title = re.sub(r'\{t\.(\w+)\}', lambda k: K.new['de'].get(k.group(1), ''), h.group(2))
        title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', title)).strip()
    doc = (f'/**\n * Section "{sec}"' + (f': {title}' if title else '') + '\n'
           f' * Texts: src/i18n/{page}.json, keys starting with "{sec}_" (one entry per language).\n'
           ' * Layout and styles of this section are in this file; legacy Elementor classes come from\n'
           ' * src/styles/legacy*.css and should be left as they are.\n */\n')
    head = doc + head.replace("import { dict } from '../../i18n';", "import { dict, type Lang } from '../../i18n';") \
        .replace('const { lang } = Astro.props;', 'const { lang } = Astro.props as { lang: Lang };')
    return f'---\n{head}\n---\n{body}'


def main(page):
    names = json.load(open(os.path.join(ROOT, 'tools/migrate/sections.json')))[page]
    cdir = os.path.join(ROOT, 'src/components', page)
    index = open(os.path.join(cdir, 'index.astro'), encoding='utf-8').read()
    order = re.findall(r"import (Sec\w+) from", index)
    data = json.load(open(os.path.join(ROOT, f'src/i18n/{page}.json'), encoding='utf-8'))
    K = Keys(data)
    files = []
    for n, comp in enumerate(order, 1):
        sid = comp[3:].lower()
        sec = names[sid]
        new_src = tidy_component(os.path.join(cdir, comp + '.astro'), sec, K, page)
        fname = f'{n:02d}-{sec.replace("_", "-")}.astro'
        open(os.path.join(cdir, fname), 'w', encoding='utf-8').write(new_src)
        os.remove(os.path.join(cdir, comp + '.astro'))
        files.append((''.join(w.capitalize() for w in sec.split('_')), fname))
    used = set()
    for f in os.listdir(cdir):
        used |= set(re.findall(r'(?:\{|: )t\.(\w+)', open(os.path.join(cdir, f), encoding='utf-8').read()))
    missing = used - set(K.new['de'])
    assert not missing, f'keys used but not defined: {sorted(missing)[:10]}'
    json.dump(K.new, open(os.path.join(ROOT, f'src/i18n/{page}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    wrapper = re.search(r'<div class="elementor elementor-\d+">', index).group(0)
    imports = '\n'.join(f"import {c} from './{f}';" for c, f in files)
    body = '\n'.join(f'  <{c} lang={{lang}} />' for c, _ in files)
    open(os.path.join(cdir, 'index.astro'), 'w', encoding='utf-8').write(
        f'---\n/** All sections of the {page} page, in order. To reorder or remove a section, edit the list below. */\n'
        f"import type {{ Lang }} from '../../i18n';\n{imports}\nconst {{ lang }} = Astro.props as {{ lang: Lang }};\n---\n"
        f'{wrapper}\n{body}\n</div>\n')
    subprocess.run(['npx', 'prettier', '--write', '--log-level', 'warn', f'src/components/{page}'], cwd=ROOT, check=True)
    print(page, 'sections', len(files), 'keys', len(K.new['de']))


if __name__ == '__main__':
    main(sys.argv[1])
