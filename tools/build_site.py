# -*- coding: utf-8 -*-
"""Build website_new.html, the new site, which lives beside the old one
(index.html lets the reader pick either).

Sources
  src/hub.json          groups and topics, in hub order
  src/tabs/<id>.html    one file per topic — the new site's own layout for it
  src/tabs/_loose.html  scripts, styles and modals the topics share
  src/head.html         Leaflet, the geojson and the audio helper the topics need
  src/tail.html, src/tail_script.html
  website_constitution.html   the charter (preamble, 38 chapters, 1,160 articles)
  tools/site_template.html

Content updates go into both sites: the old page by hand, the new one in src/
(or, for the charter, by editing the old page and rebuilding).

Run from the project root:  python tools/build_site.py
"""
import html
import json
import re

SRC = 'website_constitution.html'
OUT = 'website_new.html'
TH = '๐๑๒๓๔๕๖๗๘๙'


def thai(n):
    return str(n).translate(str.maketrans('0123456789', TH))


def read(path):
    return open(path, encoding='utf-8').read()


def span_at(src, start):
    """End of the <div> element opening at `start` (a stack walk, never a count)."""
    d = 0
    for m in re.finditer(r'<div(?=[\s>])[^>]*>|</div>', src[start:]):
        d += 1 if m.group(0) != '</div>' else -1
        if d == 0:
            return start + m.end()
    raise ValueError('unclosed div at %d' % start)


def inner(block):
    return block[block.index('>') + 1:block.rindex('</div>')].strip()


def balanced(text, label):
    depth = 0
    for m in re.finditer(r'<div(?=[\s>])[^>]*>|</div>', text):
        depth += 1 if m.group(0) != '</div>' else -1
        assert depth >= 0, 'stray </div> in ' + label
    assert depth == 0, 'unclosed <div> in ' + label


# ── archive from src/ ────────────────────────────────────────────────────────
hub_data = json.load(open('src/hub.json', encoding='utf-8'))
tab_ids = [t['id'] for g in hub_data for t in g['topics']]
assert len(tab_ids) == len(set(tab_ids)) and len(tab_ids) >= 60
tabs = []
for tid in tab_ids:
    t = read('src/tabs/%s.html' % tid).strip()
    assert t.startswith('<div id="%s" class="db-tab-content' % tid), tid
    balanced(t, tid)
    if tid == 'history-tab':
        t = t.replace('class="db-tab-content"', 'class="db-tab-content active"', 1)
    tabs.append(t)
loose = read('src/tabs/_loose.html')
balanced(loose, '_loose.html')

hub = []
for gi, g in enumerate(hub_data):
    tiles = ''.join(
        '<button type="button" class="db-tab-btn nw-topic%s" data-tab="%s" onclick="switchTab(\'%s\', this)" style="--i:%d">'
        '<span class="nw-topic-ic">%s</span><span class="nw-topic-tx">%s</span></button>'
        % (' active' if t['id'] == 'history-tab' else '', t['id'], t['id'], k, t['icon'], html.escape(t['label']))
        for k, t in enumerate(g['topics']))
    hub.append('<details class="nw-group nw-reveal" data-group="%d" open><summary><span class="nw-group-ic">%s</span>'
               '<span class="nw-group-no">%s</span><span class="nw-group-name">%s</span><span class="nw-group-count">%s หัวข้อ</span></summary>'
               '<div class="nw-topics">%s</div></details>'
               % (gi, g['icon'], thai('%02d' % (gi + 1)), html.escape(g['name']), thai(len(g['topics'])), tiles))

# ── charter from the old page ────────────────────────────────────────────────
src = read(SRC)
m0 = src.index('<div class="mourning-container">')
mourning = src[m0:span_at(src, m0)]
p0 = src.index('<div class="preamble-section">')
pre = src[p0:src.index('<section class="chapter-section" id="ch_0"')]
pre_title = re.search(r'<h2>(.*?)</h2>', pre).group(1)
pre_sub = re.search(r'<h2>.*?</h2>\s*<div[^>]*>(.*?)</div>', pre, re.S).group(1)
pre_paras = re.findall(r'<p class="preamble-p">(.*?)</p>', pre, re.S)

ORIGIN = {
    'original': ('original', 'คงเดิมจาก ๒๔๔๕'), 'modified': ('modified', 'แก้ไขโดยสภาร่างฯ'),
    'ch13_16': ('assembly', 'สภาร่างฯ + ประชามติ ๑-๒'), 'ch17_26': ('ref3', 'ประชามติรอบที่ ๓'),
    'ch27_36': ('ref45', 'ประชามติรอบที่ ๔-๕'), 'special': ('special', 'ประชามติรอบที่ ๕ (พิเศษ)'),
    'transitional': ('transitional', 'บทเฉพาะกาล'), 'later': ('later', 'เพิ่มเติมภายหลัง'),
}
starts = [(m.start(), m.group(1)) for m in re.finditer(r'<section class="chapter-section" id="(ch_\d+)"', src)]
assert len(starts) == 38
end_all = src.index('<!-- GLOSSARY PANEL -->', starts[-1][0])
chapters, total = [], 0
for k, (pos, cid) in enumerate(starts):
    secx = src[pos:starts[k + 1][0] if k + 1 < len(starts) else end_all]
    title = html.unescape(re.search(r'<h2>(.*?)</h2>', secx).group(1)).strip()
    tm = re.match(r'^(หมวด\s*[๐-๙]+|หมวดพิเศษ|บทเฉพาะกาล)\s*:?\s*(.*)$', title)
    ch_no, ch_name = (tm.group(1), tm.group(2)) if tm else ('', title)
    items = []
    for m in re.finditer(r'<div class="(part-title|article-card|normal-text|signature)"', secx):
        if any(a <= m.start() < b for a, b, _ in items):
            continue
        items.append((m.start(), span_at(secx, m.start()), m.group(1)))
    blocks = []
    for a, b, kind in items:
        block = secx[a:b]
        if kind == 'article-card':
            aid = re.search(r'id="art_(\d+)"', block).group(1)
            origin = re.search(r'data-origin="([^"]+)"', block).group(1)
            tag = html.unescape(re.search(r'<span class="badge [^"]+">([^<]+)</span>', block).group(1)).strip()
            bi = block.index('<div class="article-body">')
            body = re.sub(r'<span class="art-num">[^<]*</span>\s*', '', inner(block[bi:span_at(block, bi)]), count=1)
            ci = block.find('<div class="compare-container"')
            cmp_html = inner(block[ci:span_at(block, ci)]) if ci >= 0 else ''
            blocks.append(('art', aid, origin, tag, body, cmp_html))
            total += 1
        elif kind == 'part-title':
            blocks.append(('part', inner(block)))
        elif kind == 'normal-text':
            blocks.append(('clause', inner(block)))
        else:
            blocks.append(('sign', inner(block)))
    nums = [int(b[1]) for b in blocks if b[0] == 'art']
    chapters.append({'id': cid, 'no': ch_no, 'name': ch_name, 'blocks': blocks,
                     'range': (min(nums), max(nums)) if nums else None, 'count': len(nums)})
assert total == 1160, total


def art_html(aid, origin, tag, body, cmp_html):
    cmp_btn = cmp_panel = ''
    if cmp_html:
        cmp_btn = '<button type="button" class="nw-art-act" data-compare="%s">เทียบกับ รธน. ๒๕๔๐</button>' % aid
        cmp_panel = '<div class="nw-compare" id="compare_%s" hidden>%s</div>' % (aid, cmp_html)
    return ('<article class="nw-art nw-o-%s" id="art_%s" data-origin="%s">'
            '<div class="nw-art-no"><span>มาตรา</span><b>%s</b></div>'
            '<div class="nw-art-main"><div class="nw-art-meta"><span class="nw-tag">%s</span>%s</div>'
            '<div class="nw-art-body">%s</div>%s</div></article>'
            ) % (ORIGIN[origin][0], aid, origin, thai(aid), html.escape(tag), cmp_btn, body, cmp_panel)


toc, doc = ['<a class="nw-toc-link" href="#preamble"><span class="nw-toc-no">คำปรารภ</span></a>'], []
for ch in chapters:
    rng = ''
    if ch['range']:
        a, b = ch['range']
        rng = 'ม.%s' % thai(a) if a == b else 'ม.%s–%s' % (thai(a), thai(b))
    toc.append('<a class="nw-toc-link" href="#%s"><span class="nw-toc-no">%s</span><span class="nw-toc-range">%s</span>'
               '<span class="nw-toc-name">%s</span></a>' % (ch['id'], html.escape(ch['no'] or 'หมวด'), rng, html.escape(ch['name'])))
    parts = ['<section class="nw-chapter" id="%s"><header class="nw-ch-head nw-reveal"><div class="nw-ch-no">%s</div>'
             '<div><h2>%s</h2><div class="nw-ch-meta"><span>%s มาตรา</span><span>%s</span></div></div></header>'
             % (ch['id'], html.escape(ch['no'] or '—'), html.escape(ch['name']), thai(ch['count']), rng)]
    for b in ch['blocks']:
        if b[0] == 'art':
            parts.append(art_html(*b[1:]))
        elif b[0] == 'part':
            parts.append('<h3 class="nw-part">%s</h3>' % b[1])
        elif b[0] == 'clause':
            parts.append('<div class="nw-clause">%s</div>' % b[1])
        else:
            parts.append('<div class="nw-signature">%s</div>' % b[1])
    parts.append('</section>')
    doc.append(''.join(parts))

filters = ''.join('<button type="button" class="nw-chip" data-filter="%s">%s</button>' % (k, v[1]) for k, v in ORIGIN.items())
legend = ''.join('<span class="nw-legend-item nw-o-%s"><i></i>%s</span>' % (v[0], v[1]) for v in ORIGIN.values())

page = read('tools/site_template.html')
for key, value in [('HEAD_RES', read('src/head.html')), ('MOURNING', mourning), ('HUB', ''.join(hub)),
                   ('STAGE', '\n'.join(tabs) + '\n' + loose), ('PRE_TITLE', pre_title), ('PRE_SUB', pre_sub),
                   ('PRE_PARAS', ''.join('<p>%s</p>' % p for p in pre_paras)), ('TOC', ''.join(toc)),
                   ('CHAPTERS', '\n'.join(doc)), ('FILTERS', filters), ('LEGEND', legend),
                   ('TAIL', read('src/tail.html')), ('TAIL_SCRIPT', read('src/tail_script.html')),
                   ('TOPIC_COUNT', thai(len(tab_ids)))]:
    assert page.count('{{%s}}' % key) == 1, key
    page = page.replace('{{%s}}' % key, value)
assert not re.search(r'\{\{[A-Z_]+\}\}', page)
open(OUT, 'w', encoding='utf-8').write(page)
print('%s: %d topics, %d chapters, %d articles, %d KB' % (OUT, len(tabs), len(chapters), total, len(page.encode('utf-8')) // 1024))
