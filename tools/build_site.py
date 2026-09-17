# -*- coding: utf-8 -*-
"""Build website_new.html, the rebuilt single-page site, from the content of
website_constitution.html.

Phase 1 of the renovation: the new shell and the full charter (preamble,
38 chapters, 1,160 articles with their tags, 2540 comparisons, clauses and
signature). The 68 dashboard tabs still live on the old page; the new page
lists them in its archive section until they are moved in later phases.

Run from the project root:  python tools/build_site.py
"""
import html
import os
import re
import sys

SRC = 'website_constitution.html'
OUT = 'website_new.html'
TH = '๐๑๒๓๔๕๖๗๘๙'


def thai(n):
    return str(n).translate(str.maketrans('0123456789', TH))


def span_at(src, start):
    """End index of the <div> element opening at `start` (a stack walk, never a count)."""
    d = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', src[start:]):
        d += 1 if m.group(0) != '</div>' else -1
        if d == 0:
            return start + m.end()
    raise ValueError('unclosed div at %d' % start)


def inner(block):
    return block[block.index('>') + 1:block.rindex('</div>')].strip()


src = open(SRC, encoding='utf-8').read()

# ── mourning dedication: reused verbatim ─────────────────────────────────────
m0 = src.index('<div class="mourning-container">')
mourning = src[m0:span_at(src, m0)]

# ── preamble ─────────────────────────────────────────────────────────────────
p0 = src.index('<div class="preamble-section">')
ch0 = src.index('<section class="chapter-section" id="ch_0"')
pre = src[p0:ch0]
pre_title = re.search(r'<h2>(.*?)</h2>', pre).group(1)
pre_sub = re.search(r'<h2>.*?</h2>\s*<div[^>]*>(.*?)</div>', pre, re.S).group(1)
pre_paras = re.findall(r'<p class="preamble-p">(.*?)</p>', pre, re.S)
assert pre_paras, 'preamble paragraphs not found'

# ── chapters ─────────────────────────────────────────────────────────────────
ORIGIN = {  # data-origin -> (css key, filter label)
    'original': ('original', 'คงเดิมจาก ๒๔๔๕'), 'modified': ('modified', 'แก้ไขโดยสภาร่างฯ'),
    'ch13_16': ('assembly', 'สภาร่างฯ + ประชามติ ๑-๒'), 'ch17_26': ('ref3', 'ประชามติรอบที่ ๓'),
    'ch27_36': ('ref45', 'ประชามติรอบที่ ๔-๕'), 'special': ('special', 'ประชามติรอบที่ ๕ (พิเศษ)'),
    'transitional': ('transitional', 'บทเฉพาะกาล'), 'later': ('later', 'เพิ่มเติมภายหลัง'),
}
starts = [(m.start(), m.group(1)) for m in re.finditer(r'<section class="chapter-section" id="(ch_\d+)"', src)]
assert len(starts) == 38, len(starts)
end_all = src.index('<!-- GLOSSARY PANEL -->', starts[-1][0])

chapters, total = [], 0
for k, (pos, cid) in enumerate(starts):
    stop = starts[k + 1][0] if k + 1 < len(starts) else end_all
    sec = src[pos:stop]
    title = html.unescape(re.search(r'<h2>(.*?)</h2>', sec).group(1)).strip()
    tm = re.match(r'^(หมวด\s*[๐-๙]+|หมวดพิเศษ|บทเฉพาะกาล)\s*:?\s*(.*)$', title)
    ch_no, ch_name = (tm.group(1), tm.group(2)) if tm else ('', title)
    stats = re.search(r'<div class="chapter-stats">(.*?)</div>', sec, re.S)
    items = []
    for m in re.finditer(r'<div class="(part-title|article-card|normal-text|signature)"', sec):
        kind = m.group(1)
        if any(a <= m.start() < b for a, b, _ in items):     # nested inside a card already taken
            continue
        end = span_at(sec, m.start())
        items.append((m.start(), end, kind))
    blocks = []
    for a, b, kind in items:
        block = sec[a:b]
        if kind == 'article-card':
            aid = re.search(r'id="art_(\d+)"', block).group(1)
            origin = re.search(r'data-origin="([^"]+)"', block).group(1)
            tag = html.unescape(re.search(r'<span class="badge [^"]+">([^<]+)</span>', block).group(1)).strip()
            bi = block.index('<div class="article-body">')
            body = inner(block[bi:span_at(block, bi)])
            body = re.sub(r'<span class="art-num">[^<]*</span>\s*', '', body, count=1)
            cmp_html = ''
            ci = block.find('<div class="compare-container"')
            if ci >= 0:
                cmp_html = inner(block[ci:span_at(block, ci)])
            blocks.append(('art', aid, origin, tag, body, cmp_html))
            total += 1
        elif kind == 'part-title':
            blocks.append(('part', inner(block)))
        elif kind == 'normal-text':
            blocks.append(('clause', inner(block)))
        else:
            blocks.append(('sign', inner(block)))
    nums = [int(b[1]) for b in blocks if b[0] == 'art']
    chapters.append({'id': cid, 'no': ch_no, 'name': ch_name, 'stats': stats.group(1).strip() if stats else '',
                     'blocks': blocks, 'range': (min(nums), max(nums)) if nums else None, 'count': len(nums)})
assert total == 1160, total

# ── archive: the dashboard's five groups and their tabs (still on the old page) ──
groups = []
nav_end = src.index('class="db-tab-content"')
titles = [(m.start(), html.unescape(m.group(1)).strip())
          for m in re.finditer(r'<span>((?:📜|👑|🏛️|👤|🤖)\s*[๑-๕]\.[^<]+)</span>', src[:nav_end])]
for i, (pos, name) in enumerate(titles):
    stop = titles[i + 1][0] if i + 1 < len(titles) else nav_end
    labels = [html.unescape(x).strip() for x in
              re.findall(r'<button class="db-tab-btn[^"]*" onclick="switchTab\(\'[^\']+\', this\)"[^>]*>([^<]*)</button>', src[pos:stop])]
    groups.append((name, labels))
assert len(groups) == 5 and sum(len(l) for _, l in groups) == 68, [len(l) for _, l in groups]

# ── glossary data, lifted from js/constitution.js ────────────────────────────
js = open('js/constitution.js', encoding='utf-8').read()
g0 = js.index('const glossaryData = [')
g1 = js.index('];', g0) + 2
open('js/glossary-data.js', 'w', encoding='utf-8').write(
    '/* Glossary for website_new.html, generated by tools/build_site.py from js/constitution.js. */\n'
    'window.GLOSSARY = ' + js[g0 + len('const glossaryData = '):g1] + '\n')

# ── render ───────────────────────────────────────────────────────────────────
def art_html(aid, origin, tag, body, cmp_html):
    key = ORIGIN[origin][0]
    cmp_btn = cmp_panel = ''
    if cmp_html:
        cmp_btn = '<button type="button" class="art-act" data-compare="%s">เทียบกับ รธน. ๒๕๔๐</button>' % aid
        cmp_panel = '<div class="compare" id="compare_%s" hidden>%s</div>' % (aid, cmp_html)
    return ('<article class="art o-%s" id="art_%s" data-origin="%s">'
            '<div class="art-no"><span>มาตรา</span><b>%s</b></div>'
            '<div class="art-main"><div class="art-meta"><span class="tag">%s</span>%s</div>'
            '<div class="art-body">%s</div>%s</div></article>') % (key, aid, origin, thai(aid), html.escape(tag), cmp_btn, body, cmp_panel)


toc, doc = [], []
toc.append('<a class="toc-link" href="#preamble"><span class="toc-no">คำปรารภ</span></a>')
for ch in chapters:
    rng = ''
    if ch['range']:
        a, b = ch['range']
        rng = 'ม.%s' % thai(a) if a == b else 'ม.%s–%s' % (thai(a), thai(b))
    toc.append('<a class="toc-link" href="#%s"><span class="toc-no">%s</span><span class="toc-name">%s</span><span class="toc-range">%s</span></a>'
               % (ch['id'], html.escape(ch['no'] or 'หมวด'), html.escape(ch['name']), rng))
    parts = ['<section class="chapter" id="%s"><header class="ch-head"><div class="ch-no">%s</div><h2>%s</h2>'
             '<div class="ch-meta">%s</div></header>' % (ch['id'], html.escape(ch['no']), html.escape(ch['name']),
                                                          '%s มาตรา · %s' % (thai(ch['count']), rng) if rng else '')]
    for b in ch['blocks']:
        if b[0] == 'art':
            parts.append(art_html(*b[1:]))
        elif b[0] == 'part':
            parts.append('<h3 class="part">%s</h3>' % b[1])
        elif b[0] == 'clause':
            parts.append('<div class="clause">%s</div>' % b[1])
        else:
            parts.append('<div class="signature">%s</div>' % b[1])
    parts.append('</section>')
    doc.append(''.join(parts))

filters = ''.join('<button type="button" class="chip" data-filter="%s">%s</button>' % (k, v[1]) for k, v in ORIGIN.items())
legend = ''.join('<span class="legend-item o-%s"><i></i>%s</span>' % (v[0], v[1]) for v in ORIGIN.values())
archive = ''.join(
    '<div class="arch-group"><h3>%s</h3><ul>%s</ul></div>' % (html.escape(name), ''.join('<li>%s</li>' % html.escape(l) for l in labels))
    for name, labels in groups)

tpl = open('tools/site_template.html', encoding='utf-8').read()
page = (tpl.replace('{{MOURNING}}', mourning)
           .replace('{{PRE_TITLE}}', pre_title)
           .replace('{{PRE_SUB}}', pre_sub)
           .replace('{{PRE_PARAS}}', ''.join('<p>%s</p>' % p for p in pre_paras))
           .replace('{{TOC}}', ''.join(toc))
           .replace('{{CHAPTERS}}', '\n'.join(doc))
           .replace('{{FILTERS}}', filters)
           .replace('{{LEGEND}}', legend)
           .replace('{{ARCHIVE}}', archive)
           .replace('{{TAB_COUNT}}', thai(68)))
assert '{{' not in page
open(OUT, 'w', encoding='utf-8').write(page)
print('%s: %d chapters, %d articles, %d KB' % (OUT, len(chapters), total, len(page.encode('utf-8')) // 1024))
