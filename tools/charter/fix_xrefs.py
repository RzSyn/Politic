"""Fix article cross-references in ม.๑-๓๖๐ that still carry 2540 numbering.

The 2525 charter was adapted from the 2540 constitution, but many "มาตรา N" references
inside ม.๑-๓๖๐ were copied without renumbering.  Each 2525 article is matched to its
2540 source by text overlap; a reference is rewritten when the 2540 source cites the
same position and that 2540 article now lives under a different 2525 number.

    python tools/charter/fix_xrefs.py plan    # write tools/charter/xref_plan.tsv
    python tools/charter/fix_xrefs.py apply   # apply the plan (plus OVERRIDES)

Only the article bodies are touched; .compare-container panes quote 2540 and are
left alone.  Run tools/validate_old.py afterwards.
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML = os.path.join(ROOT, 'website_constitution.html')
OLD = os.path.join(ROOT, 'constitution_2540.html')
PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xref_plan.tsv')
TH = '๐๑๒๓๔๕๖๗๘๙'

# (citing article, old number, occurrence among that number in the article starting at 1) -> new number
# Filled in by hand where the 2540 match cannot decide; 0 means "leave as is".
OVERRIDES = {
    (31, 32, 1): 0,      # text of 2540 ม.๓๒ pasted into ม.๓๑; label removed by fix_charter_text.py
    (137, 148, 1): 0, (186, 198, 1): 0, (187, 200, 1): 0, (284, 303, 1): 0,  # placeholder ranges
    (269, 1, 1): 0,      # "ภายใต้บังคับมาตรา ๑" is correct
    (158, 170, 1): 159,  # people's legislative initiative (2540 ม.๑๗๐)
    (359, 170, 1): 159,
    (164, 172, 1): 162,  # bills go to the House first (2540 ม.๑๗๒)
    (183, 314, 1): 295,  # constitutional amendment
    (298, 314, 1): 0,    # fixed to ม.๒๗๘ by fix_charter_text.py (it was "๓๑๔/๑")
    (339, 130, 1): 131,  # term of the Senate (2540 ม.๑๓๐)
}

REF = re.compile(r'<span class="cross-ref" data-target="(\d+)">มาตรา ([๐-๙]+)</span>|มาตรา ([๐-๙]+)')


def a2i(x):
    return int(''.join(str(TH.index(c)) for c in x))


def thai(n):
    return ''.join(TH[int(c)] for c in str(n))


def text(fragment):
    fragment = re.sub(r'<span class="tooltiptext">.*?</span>', '', fragment, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()


def bodies(src):
    """{n: (start, end)} of the citable part of each article card (before any compare pane)."""
    starts = [(int(m.group(1)), m.start()) for m in re.finditer(r'id="art_(\d+)"', src)]
    out = {}
    for i, (n, st) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else src.index('</section>', st)
        c = src.find('compare-container', st, end)
        out[n] = (st, c if c > 0 else end)
    return out


def refs_in(src, st, end):
    """Every article reference in a body, in document order: (match, number)."""
    out = []
    for m in REF.finditer(src, st, end):
        if m.group(3) and src[max(0, m.start() - 22):m.start()].endswith('art-num">'):
            continue
        out.append((m, a2i(m.group(2) or m.group(3))))
    return out


def old_articles():
    raw = open(OLD, encoding='utf-8').read()
    raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S)
    lines = [l.strip() for l in html.unescape(re.sub(r'<[^>]+>', '\n', raw)).splitlines() if l.strip()]
    arts, cur = {}, None
    for l in lines:
        m = re.match(r'^มาตรา ([๐-๙]+)$', l)
        if m:
            cur = a2i(m.group(1))
            arts[cur] = ''
        elif cur and not re.match(r'^(หมวด|ส่วนที่) ', l):
            arts[cur] += ' ' + l
    return arts


def shingles(t, k=6):
    t = re.sub(r'มาตรา [๐-๙]+', '', t)
    t = re.sub(r'[\s()๐-๙]', '', t)
    return {t[i:i + k] for i in range(max(1, len(t) - k))}


def plan():
    src = open(HTML, encoding='utf-8').read()
    spans = bodies(src)
    new = {n: text(src[a:b].split('</div>', 2)[-1] if False else src[a:b]) for n, (a, b) in spans.items() if n <= 360}
    old = old_articles()
    osh = {k: shingles(v) for k, v in old.items()}
    match = {}
    for n in range(1, 361):
        a = shingles(new[n])
        best = (0.0, None)
        for k, b in osh.items():
            j = len(a & b) / len(a | b) if a and b else 0
            if j > best[0]:
                best = (j, k)
        match[n] = best
    inv = {}
    for n, (j, k) in match.items():
        if j >= 0.5:
            inv.setdefault(k, []).append(n)
    rows = []
    for n in range(1, 361):
        j, k = match[n]
        found = refs_in(src, *spans[n])
        olds = [a2i(x) for x in re.findall(r'มาตรา ([๐-๙]+)', old[k])] if j >= 0.5 else []
        ok = {m for K in olds for m in inv.get(K, [])}
        seen = {}
        aligned = len(olds) == len(found)
        for idx, (m, N) in enumerate(found):
            seen[N] = seen.get(N, 0) + 1
            sug, how = None, ''
            if aligned:
                # same position in the 2540 source: the citation must point where that article went
                if olds[idx] not in inv or N in inv[olds[idx]]:
                    if olds[idx] in inv or N in ok:
                        continue
                else:
                    sug, how = inv[olds[idx]][0], 'position'
            elif N in ok:
                continue
            elif N in olds and N in inv and N not in inv[N]:
                sug, how = inv[N][0], 'same-number'
            if sug == N:
                continue
            ctx = text(src[max(spans[n][0], m.start() - 300):m.end()])[-90:]
            rows.append([n, N, seen[N], sug or '', how, ctx, new.get(N, '')[:60],
                         new.get(sug, '')[:60] if sug else ''])
    with open(PLAN, 'w', encoding='utf-8') as f:
        f.write('n\told\tocc\tnew\thow\tcontext\told_target\tnew_target\n')
        for r in rows:
            f.write('\t'.join(str(x).replace('\t', ' ') for x in r) + '\n')
    print('%d references in plan, %d without a proposal' % (len(rows), sum(1 for r in rows if not r[3])))


def apply():
    src = open(HTML, encoding='utf-8').read()
    spans = bodies(src)
    todo = {}
    for line in open(PLAN, encoding='utf-8').read().splitlines()[1:]:
        n, N, occ, new = line.split('\t')[:4]
        key = (int(n), int(N), int(occ))
        val = OVERRIDES.get(key, int(new) if new else 0)
        if val:
            todo[key] = val
    for key, val in OVERRIDES.items():
        if val:
            todo[key] = val
    edits = []
    for n in sorted({k[0] for k in todo}):
        seen = {}
        for m, N in refs_in(src, *spans[n]):
            seen[N] = seen.get(N, 0) + 1
            M = todo.pop((n, N, seen[N]), None)
            if not M:
                continue
            assert 1 <= M <= 1160
            edits.append((m.start(), m.end(),
                          '<span class="cross-ref" data-target="%d">มาตรา %s</span>' % (M, thai(M))))
    assert not todo, ('not found', todo)
    for a, b, rep in sorted(edits, reverse=True):
        src = src[:a] + rep + src[b:]
    open(HTML, 'w', encoding='utf-8').write(src)
    print('rewrote %d references' % len(edits))


if __name__ == '__main__':
    {'plan': plan, 'apply': apply}[sys.argv[1]]()
