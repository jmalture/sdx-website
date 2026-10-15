"""Translation helper for pages that exist only in German.

  python tools/migrate/strings.py extract <page-de.html> <strings.json>
      collects every visible text, translatable attribute and human-readable string literal in the
      page's scripts (JSON-LD included) into { "<German>": { "en": "", "cs": "" } }.
  python tools/migrate/strings.py apply <page-de.html> <strings.json> <lang> <out.html> [old=new ...]
      writes a copy of the page with the texts replaced, plus optional link replacements
      (e.g. /audits/=/en/audits/). The copies are then ported with port_page.py like real pages.
"""
import json, re, sys
from bs4 import BeautifulSoup, NavigableString, Comment

ATTRS = ('alt', 'title', 'aria-label', 'placeholder', 'content', 'data-more', 'data-less', 'data-label')
JS_STR = re.compile(r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"")


def human(s):
    """A string literal worth translating: has letters, and a space or an umlaut/capital word."""
    if not re.search(r'[A-Za-zÄÖÜäöüß]{2}', s) or re.search(r'^[\w.#-]+$', s) and not re.search(r'[ÄÖÜäöüß]', s) and not s[:1].isupper():
        return False
    if re.match(r'^(M\d|<path|<svg|linear-gradient|rgba?\(|#|\.|\[|var\(|calc\(|translate|cubic|[a-z-]+:)', s):
        return False
    if '<' in s and not re.search(r'>[^<]*[A-Za-zÄÖÜäöüß]{3}', s):
        return False
    return True


def page(path):
    d = BeautifulSoup(open(path, encoding='utf-8').read(), 'lxml')
    return d, d.select_one('[data-elementor-type=wp-page]')


def walk(root, fn_text, fn_attr, fn_script):
    for el in list(root.descendants):
        if isinstance(el, Comment):
            continue
        if isinstance(el, NavigableString):
            if el.parent is None or el.parent.name in ("script", "style"):
                continue
            fn_text(el)
        else:
            for a in ATTRS:
                if el.get(a):
                    fn_attr(el, a)
            if el.name == 'script':
                fn_script(el)


def script_strings(code, ld=False):
    if ld:
        out = []
        def rec(o):
            if isinstance(o, dict): [rec(v) for k, v in o.items() if k not in ('@type', '@context')]
            elif isinstance(o, list): [rec(v) for v in o]
            elif isinstance(o, str) and human(o): out.append(o)
        rec(json.loads(code)); return out
    import ast
    out = []
    for m in JS_STR.finditer(code):
        try:
            v = ast.literal_eval(m.group(0))
        except Exception:
            continue
        if human(v):
            out.append(v)
    return out


def extract(src, dst):
    d, root = page(src)
    found = {}
    def add(s):
        s = s.strip()
        if s and re.search(r'[A-Za-zÄÖÜäöüß]', s):
            found.setdefault(s, {'en': '', 'cs': ''})
    walk(root, lambda t: add(str(t)), lambda el, a: add(el[a]),
         lambda el: [add(s) for s in script_strings(el.string or '', el.get('type') == 'application/ld+json')])
    json.dump(found, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(found), 'strings,', sum(len(k) for k in found), 'chars')


def apply(src, table, lang, dst, links):
    tr = {k: v[lang] for k, v in json.load(open(table, encoding='utf-8')).items() if v.get(lang)}
    d, root = page(src)
    def t(s):
        core = s.strip()
        if core in tr:
            return s.replace(core, tr[core])
        return s
    def fix_link(v):
        return links.get(v, v)
    def text(el):
        n = t(str(el))
        if n != str(el):
            el.replace_with(n)
    def attr(el, a):
        el[a] = t(el[a])
    def script(el):
        code = el.string or ''
        if el.get('type') == 'application/ld+json':
            o = json.loads(code)
            def rec(x):
                if isinstance(x, dict): return {k: rec(v) for k, v in x.items()}
                if isinstance(x, list): return [rec(v) for v in x]
                if isinstance(x, str): return tr.get(x, x)
                return x
            el.string = json.dumps(rec(o), ensure_ascii=False); return
        import ast
        def rep(m):
            try:
                v = ast.literal_eval(m.group(0))
            except Exception:
                return m.group(0)
            core = v.strip() if isinstance(v, str) else None
            if core and core in tr:
                q = m.group(0)[0]
                nv = v.replace(core, tr[core])
                return q + nv.replace('\\', '\\\\').replace(q, '\\' + q) + q
            return m.group(0)
        el.string = JS_STR.sub(rep, code)
    walk(root, text, attr, script)
    for a in root.select('a[href]'):
        a['href'] = fix_link(a['href'])
    open(dst, 'w', encoding='utf-8').write(str(d))
    left = [k for k in json.load(open(table, encoding='utf-8')) if k not in tr]
    print(dst, 'untranslated', len(left), left[:5])


if __name__ == '__main__':
    if sys.argv[1] == 'extract':
        extract(sys.argv[2], sys.argv[3])
    else:
        apply(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], dict(a.split('=', 1) for a in sys.argv[6:]))
