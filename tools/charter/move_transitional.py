# -*- coding: utf-8 -*-
"""Move บทเฉพาะกาล (ม.๓๓๘-๓๖๐) to the very end of the 2525 charter (user ruling 2026-10-20).

New numbering:  n <= 337 unchanged;  361..1160 -> n-23 (หมวด ๑๗ starts at ม.๓๓๘, the special
chapter becomes ม.๑๑๓๐-๑๑๓๗);  338..360 -> n+800 (บทเฉพาะกาล becomes ม.๑๑๓๘-๑๑๖๐).
Section ids follow page order: ch_17..ch_37 -> ch_16..ch_36, บทเฉพาะกาล -> ch_37.  The
countersignature moves with the end of the charter.  compare panes (2540 text) and the 2375
charter (early-art-text) are never touched.  Run once from the repo root.
"""
import glob
import io
import re

OLD = 'website_constitution.html'
TH = '๐๑๒๓๔๕๖๗๘๙'


def th2i(x):
    return int(''.join(str(TH.index(c)) if c in TH else c for c in x))


def i2th(n):
    return ''.join(TH[int(c)] for c in str(n))


big = []


def f(n):
    if n > 1160:
        big.append(n)
        return n
    if 338 <= n <= 360:
        return n + 800
    if n >= 361:
        return n - 23
    return n


def renum_digits(tok):
    """Renumber one number token, keeping its script (Thai or Arabic digits)."""
    n = f(th2i(tok))
    return i2th(n) if tok[0] in TH else str(n)


NUM = r'[๐-๙0-9]+'
SEP = r'(?:\s*[-–]\s*|&ndash;|\s*ถึง\s*|\s*และ\s*|\s*หรือ\s*|,\s*|\s*,\s*)'
PRE = r'(?:มาตรา\s*|ม\.\s*)'
CHAIN = re.compile(r'%s%s(?:/%s)?(?:%s%s?%s(?:/%s)?)*' % (PRE, NUM, NUM, SEP, PRE, NUM, NUM))
ATTR = re.compile(r'(id="art_|data-target="|href="#art_)(\d+)(")')
chained = []


def remap_text(s):
    def chain(m):
        txt = m.group(0)
        nums = list(re.finditer(r'(?<!/)' + NUM, txt))
        vals = [th2i(x.group(0)) for x in nums]
        if len(vals) > 1:
            segs = {0 if v < 338 else 1 if v <= 360 else 2 for v in vals}
            if len(segs) > 1 and re.search(r'[-–]|&ndash;|ถึง', txt):
                raise SystemExit('range crosses the moved block: ' + txt)
            if any(v >= 338 for v in vals[1:]):
                chained.append(txt)
        return re.sub(r'(?<!/)' + NUM, lambda x: renum_digits(x.group(0)), txt)
    s = CHAIN.sub(chain, s)
    return ATTR.sub(lambda m: m.group(1) + str(f(int(m.group(2)))) + m.group(3), s)


def protected_spans(s):
    """Spans of compare panes and the 2375 charter, matched by <div> depth."""
    spans = []
    for m in re.finditer(r'<div class="(compare-container|early-art-text)[^"]*"', s):
        depth, i = 0, m.start()
        for t in re.finditer(r'<div\b|</div>', s[m.start():]):
            depth += 1 if t.group(0) == '<div' else -1
            if depth == 0:
                spans.append((m.start(), m.start() + t.end()))
                break
    spans.sort()
    return spans


def remap_outside(s):
    out, last = [], 0
    for a, b in protected_spans(s):
        if a < last:
            continue
        out.append(remap_text(s[last:a]))
        out.append(s[a:b])
        last = b
    out.append(remap_text(s[last:]))
    return ''.join(out)


WORDING = [
    ('๘ มาตราสุดท้ายของรัฐธรรมนูญ (ม.๑๑๕๓-๑๑๖๐)', '๘ มาตราก่อนบทเฉพาะกาล (ม.๑๑๕๓-๑๑๖๐)'),
    ('หมวดพิเศษท้ายรัฐธรรมนูญ (ม.๑๑๕๓-๑๑๖๐)', 'หมวดพิเศษของรัฐธรรมนูญ (ม.๑๑๕๓-๑๑๖๐)'),
]


def wording(s):
    for o, n in WORDING:
        s = s.replace(o, n)
    return s


def move_block(s):
    open16 = '<section class="chapter-section" id="ch_16">'
    a = s.index(open16)
    b = s.index('</section>', a) + len('</section>\n')
    trans = s[a:b]
    assert 'id="art_338"' in trans and 'id="art_360"' in trans and 'id="art_361"' not in trans
    s = s[:a] + s[b:]
    c = s.index('<section class="chapter-section" id="ch_37">')
    d = s.index('</section>', c)
    sig = re.search(r'<div class="signature">.*?</div>', s[c:d], re.S)
    s = s[:c + sig.start()] + s[c + sig.end():]
    d = s.index('</section>', c) + len('</section>\n')
    end = trans.rindex('</section>')
    lead = re.search(r'\s*$', trans[:end]).start()
    trans = trans[:lead] + sig.group(0) + trans[lead:]
    s = s[:d] + trans + s[d:]
    # nav: the บทเฉพาะกาล link goes after the special chapter
    nav = re.search(r'<a href="#ch_16" class="nav-chapter"[^>]*>บทเฉพาะกาล[^<]*</a>\n', s)
    s = s[:nav.start()] + s[nav.end():]
    k = s.index('\n', s.index('<a href="#ch_37" class="nav-chapter"')) + 1
    s = s[:k] + nav.group(0) + s[k:]
    # section ids follow page order
    def cid(m):
        n = int(m.group(2))
        n = 37 if n == 16 else n - 1 if n >= 17 else n
        return '%s%d%s' % (m.group(1), n, m.group(3))
    return re.sub(r'(id="ch_|href="#ch_)(\d+)(")', cid, s)


def rw(path, fn):
    s = io.open(path, encoding='utf-8').read()
    io.open(path, 'w', encoding='utf-8', newline='').write(fn(s))


def stale_js(s):
    # js/constitution.js still used an older special-chapter numbering (ม.๑๑๒๙-๑๑๓๖)
    def fix(m):
        n = int(m.group(2))
        return m.group(1) + str(n + 1) + m.group(3) if 1129 <= n <= 1136 else m.group(0)
    s = re.sub(r'(data-target=")(\d+)(")', fix, s)
    return re.sub(r'(มาตรา )([๐-๙]+)', lambda m: m.group(1) + (i2th(th2i(m.group(2)) + 1)
                  if 1129 <= th2i(m.group(2)) <= 1136 else m.group(2)), s)


def main():
    rw(OLD, lambda s: remap_outside(wording(move_block(s))))
    for p in sorted(glob.glob('src/tabs/*.html')) + ['js/glossary-data.js']:
        rw(p, lambda s: remap_outside(wording(s)))
    rw('js/constitution.js', stale_js)
    for p in sorted(glob.glob('tools/charter/ch*.txt')):
        rw(p, remap_text)
    print('numbers > 1160 left alone:', sorted(set(big)))
    for c in sorted(set(chained)):
        print('chain:', c)


if __name__ == '__main__':
    main()
