# -*- coding: utf-8 -*-
"""Do the dashboard tabs cite the right 2525 article? For every "มาตรา N" / "ม.N" in src/tabs (except the
tabs about other charters), compare the text around the citation with article N's own text using shared
character 4-grams, and list the weakest matches for a human to read. Run from the repo root.
usage: python tools/charter/audit_refs.py [how_many]"""
import glob
import html
import io
import os
import re
import sys

TH = '๐๑๒๓๔๕๖๗๘๙'
def th2i(x): return int(''.join(str(TH.index(c)) if c in TH else c for c in x))
def clean(t): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
SKIP = {'early-const-tab.html', 'charter-2445-tab.html', 'constitutions-tab.html'}

src = io.open('website_constitution.html', encoding='utf-8').read()
pos = [(m.start(), int(m.group(1))) for m in re.finditer(r'id="art_(\d+)"', src)]
ART = {}
for k, (p, n) in enumerate(pos):
    end = pos[k + 1][0] if k + 1 < len(pos) else p + 6000
    t = clean(src[p:end])
    t = t[t.find('มาตรา'):]
    ART[n] = t[:700]

def grams(t):
    t = re.sub(r'[^฀-๿A-Za-z]', '', t)
    return {t[i:i + 4] for i in range(len(t) - 3)}

rows = []
for f in sorted(glob.glob('src/tabs/*.html')):
    name = os.path.basename(f)
    if name in SKIP:
        continue
    t = clean(io.open(f, encoding='utf-8').read())
    for m in re.finditer(r'(?:มาตรา\s*|ม\.\s*)([๐-๙]{1,4})(?![๐-๙,])', t):
        n = th2i(m.group(1))
        if not 1 <= n <= 1160:
            continue
        ctx = t[max(0, m.start() - 110):m.end() + 110]
        a = ART[n]
        g1, g2 = grams(ctx), grams(a[8:])
        score = len(g1 & g2) / max(1, min(len(g1), len(g2)))
        rows.append((score, name, n, ctx, a[:160]))
rows.sort()
k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
print('citations checked:', len(rows))
for score, name, n, ctx, a in rows[:k]:
    print(f'\n[{score:.2f}] {name}  ม.{n}\n   TAB: {ctx}\n   ART: {a}')
