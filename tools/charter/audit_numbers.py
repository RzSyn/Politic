# -*- coding: utf-8 -*-
"""Audit article numbering of the 2525 charter in website_constitution.html and website_new.html.
Checks: art_1..art_1160 present once each and in page order; every card's "มาตรา N" label equals
its id; every data-target / #art_ link resolves; the last sections are บทเฉพาะกาล then หมวดพิเศษ,
with the countersignature at the very end. Run from the repo root."""
import io
import re
import sys

TH = '๐๑๒๓๔๕๖๗๘๙'
def th2i(x): return int(''.join(str(TH.index(c)) if c in TH else c for c in x))

ok = True
def bad(msg):
    global ok
    ok = False
    print('  !!', msg)

for f in ['website_constitution.html', 'website_new.html']:
    s = io.open(f, encoding='utf-8').read()
    print(f)
    ids = [int(m.group(1)) for m in re.finditer(r'id="art_(\d+)"', s)]
    if ids != list(range(1, 1161)):
        missing = sorted(set(range(1, 1161)) - set(ids)); dup = sorted({i for i in ids if ids.count(i) > 1})
        bad(f'ids not 1..1160 in order (count {len(ids)}, missing {missing[:5]}, dup {dup[:5]})')
    # label check: first "มาตรา N" after each id, before the next id
    pos = [(m.start(), int(m.group(1))) for m in re.finditer(r'id="art_(\d+)"', s)]
    wrong = []
    for k, (p, n) in enumerate(pos):
        end = pos[k + 1][0] if k + 1 < len(pos) else p + 6000
        m = re.search(r'มาตรา\s*([๐-๙0-9,]+)', re.sub(r'<[^>]+>', ' ', s[p:end]))
        if not m or th2i(m.group(1).replace(',', '')) != n:
            wrong.append((n, m.group(1) if m else None))
    if wrong:
        bad(f'{len(wrong)} labels differ from ids, e.g. {wrong[:5]}')
    targets = set(re.findall(r'(?:data-target="|href="#art_)(\d+)"', s))
    dead = sorted(int(t) for t in targets if not (1 <= int(t) <= 1160))
    if dead:
        bad(f'cross-refs to missing articles: {dead[:10]}')
    # ending order
    i_trans = s.rfind('บทเฉพาะกาล')
    t_first = s.find('id="art_1130"'); t_last = s.find('id="art_1152"'); sp_first = s.find('id="art_1153"'); sig = s.rfind('ผู้รับสนองพระบรมราชโองการ')
    sec = lambda n: s.rfind('<section', 0, s.find(f'id="art_{n}"'))
    head = lambda n: re.sub(r'<[^>]+>', ' ', s[sec(n):sec(n) + 600])
    if 'บทเฉพาะกาล' not in head(1130):
        bad('ม.๑๑๓๐ is not the first article of บทเฉพาะกาล')
    if 'หมวดพิเศษ' not in head(1153):
        bad('ม.๑๑๕๓ is not the first article of หมวดพิเศษ')
    if not (t_first < t_last < sp_first < sig):
        bad('order is not บทเฉพาะกาล -> หมวดพิเศษ -> ผู้รับสนองฯ')
    print('  ids', len(ids), '| labels checked', len(pos), '| cross-ref targets', len(targets))
print('=> OK' if ok else '=> CHECK')
sys.exit(0 if ok else 1)
