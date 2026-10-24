# -*- coding: utf-8 -*-
"""Put หมวดพิเศษ back at the very end of the 2525 charter, บทเฉพาะกาล before it (user ruling 2026-10-24).

Before:  หมวด ๑-๓๖ ม.๑-๑๑๒๙ · หมวดพิเศษ ม.๑๑๓๐-๑๑๓๗ (ch_36) · บทเฉพาะกาล ม.๑๑๓๘-๑๑๖๐ (ch_37) · ผู้รับสนองฯ
After:   หมวด ๑-๓๖ ม.๑-๑๑๒๙ · บทเฉพาะกาล ม.๑๑๓๐-๑๑๕๒ (ch_36) · หมวดพิเศษ ม.๑๑๕๓-๑๑๖๐ (ch_37) · ผู้รับสนองฯ

Renumbering: 1130..1137 -> n+23 ; 1138..1160 -> n-8 ; everything else unchanged.
Same machinery as move_transitional.py (compare panes and the 2375 charter are never touched).
Run once from the repo root.
"""
import glob
import io
import re
import sys

sys.path.insert(0, 'tools/charter')
import move_transitional as mt   # reuse the parser; its f() is replaced below

big = []


def f(n):
    if n > 1160:
        big.append(n)
        return n
    if 1130 <= n <= 1137:
        return n + 23
    if 1138 <= n <= 1160:
        return n - 8
    return n


def renum_digits(tok):
    n = f(mt.th2i(tok))
    return mt.i2th(n) if tok[0] in mt.TH else str(n)


chained = []


def remap_text(s):
    def chain(m):
        txt = m.group(0)
        nums = list(re.finditer(r'(?<!/)' + mt.NUM, txt))
        vals = [mt.th2i(x.group(0)) for x in nums]
        if len(vals) > 1:
            segs = {0 if v < 1130 else 1 if v <= 1137 else 2 for v in vals}
            if len(segs) > 1 and re.search(r'[-–]|&ndash;|ถึง', txt):
                raise SystemExit('range crosses the moved block: ' + txt)
            if any(v >= 1130 for v in vals[1:]):
                chained.append(txt)
        return re.sub(r'(?<!/)' + mt.NUM, lambda x: renum_digits(x.group(0)), txt)
    s = mt.CHAIN.sub(chain, s)
    return mt.ATTR.sub(lambda m: m.group(1) + str(f(int(m.group(2)))) + m.group(3), s)


def remap_outside(s):
    out, last = [], 0
    for a, b in mt.protected_spans(s):
        if a < last:
            continue
        out.append(remap_text(s[last:a]))
        out.append(s[a:b])
        last = b
    out.append(remap_text(s[last:]))
    return ''.join(out)


WORDING = [  # applied after renumbering
    ('๘ มาตราก่อนบทเฉพาะกาล (ม.๑๑๕๓-๑๑๖๐)', '๘ มาตราสุดท้ายของรัฐธรรมนูญ (ม.๑๑๕๓-๑๑๖๐)'),
    ('หมวดพิเศษของรัฐธรรมนูญ (ม.๑๑๕๓-๑๑๖๐)', 'หมวดพิเศษท้ายรัฐธรรมนูญ (ม.๑๑๕๓-๑๑๖๐)'),
]


def wording(s):
    for o, n in WORDING:
        s = s.replace(o, n)
    return s


def move_block(s):
    a = s.index('<section class="chapter-section" id="ch_36">')
    b = s.index('</section>', a) + len('</section>\n')
    special = s[a:b]
    assert 'id="art_1130"' in special and 'id="art_1137"' in special and 'id="art_1138"' not in special
    s = s[:a] + s[b:]
    c = s.index('<section class="chapter-section" id="ch_37">')
    d = s.index('</section>', c)
    trans_part = s[c:d]
    assert 'id="art_1138"' in trans_part and 'id="art_1160"' in trans_part
    sig = re.search(r'<div class="signature">.*?</div>', trans_part, re.S)
    s = s[:c + sig.start()] + s[c + sig.end():]
    d = s.index('</section>', c) + len('</section>\n')
    end = special.rindex('</section>')
    lead = re.search(r'\s*$', special[:end]).start()
    special = special[:lead] + sig.group(0) + special[lead:]
    s = s[:d] + special + s[d:]
    # nav: the special-chapter link goes after บทเฉพาะกาล
    nav = re.search(r'<a href="#ch_36" class="nav-chapter"[^>]*>หมวดพิเศษ[^<]*</a>\n', s)
    s = s[:nav.start()] + s[nav.end():]
    k = s.index('\n', s.index('<a href="#ch_37" class="nav-chapter"')) + 1
    s = s[:k] + nav.group(0) + s[k:]
    # section ids follow page order: swap 36 <-> 37
    return re.sub(r'(id="ch_|href="#ch_)(3[67])(")', lambda m: m.group(1) + ('37' if m.group(2) == '36' else '36') + m.group(3), s)


def rw(path, fn):
    s = io.open(path, encoding='utf-8').read()
    io.open(path, 'w', encoding='utf-8', newline='').write(fn(s))


def main():
    rw(mt.OLD, lambda s: wording(remap_outside(move_block(s))))
    for p in sorted(glob.glob('src/tabs/*.html')) + ['js/glossary-data.js', 'js/constitution.js']:
        rw(p, lambda s: wording(remap_outside(s)))
    for p in sorted(glob.glob('tools/charter/ch*.txt')):
        rw(p, remap_text)
    print('numbers > 1160 left alone:', sorted(set(big)))
    for c in sorted(set(chained)):
        print('chain:', c)


if __name__ == '__main__':
    main()
