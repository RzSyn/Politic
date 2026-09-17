# -*- coding: utf-8 -*-
"""Build website_new.html, the rebuilt single-page site, from the content of
website_constitution.html.

Layout, top to bottom: masthead, hero band, the topic hub (every one of the
68 archive topics as a button, grouped as before), the stage where the
chosen topic opens, then the charter (preamble, 38 chapters, 1,160
articles) with its own filters and table of contents.

Topic panels move across verbatim with the scripts and styles around them,
so every interactive piece keeps working; css/site.css retones them to the
new design. The charter is re-set in new markup.

Run from the project root:  python tools/build_site.py
"""
import html
import re

SRC = 'website_constitution.html'
OUT = 'website_new.html'
TH = '๐๑๒๓๔๕๖๗๘๙'


def thai(n):
    return str(n).translate(str.maketrans('0123456789', TH))


def span_at(src, start):
    """End of the <div> element opening at `start` (a stack walk, never a count)."""
    d = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', src[start:]):
        d += 1 if m.group(0) != '</div>' else -1
        if d == 0:
            return start + m.end()
    raise ValueError('unclosed div at %d' % start)


def inner(block):
    return block[block.index('>') + 1:block.rindex('</div>')].strip()


def blocks_of(src, tag):
    return [m.group(0) for m in re.finditer(r'<%s\b[^>]*>.*?</%s>' % (tag, tag), src, re.S)]


src = open(SRC, encoding='utf-8').read()

# ── head resources the topics need: geojson, inline Leaflet CSS/JS, audio helper ──
head = src[:src.index('<body')]
head_res = [m.group(0) for m in re.finditer(r'<script src="js/world_geojson\.js"></script>|<style>.*?</style>|<script>.*?</script>', head, re.S)]
assert len(head_res) == 4, len(head_res)

# ── the archive: hub groups from the old nav, panels and their loose scripts ──
sec = src.index('<section id="history_and_pms"')
sec_end = src.index('<!-- PREAMBLE -->')
first_panel = src.rindex('<div', 0, src.index('class="db-tab-content', sec))
nav = src[sec:first_panel]
nav_res = blocks_of(nav, 'style') + blocks_of(nav, 'script')
stage_end = src.rindex('</section>', sec, sec_end)
stage_html = src[first_panel:stage_end].rstrip()

panels = re.findall(r'<div id="([\w-]+-tab)" class="db-tab-content', stage_html)
assert len(panels) == 68, len(panels)
# nothing but panels, styles and scripts may sit in the stage region
rest, pos = [], 0
for m in re.finditer(r'<div id="[\w-]+-tab" class="db-tab-content[^"]*"[^>]*>|<style\b|<script\b', stage_html):
    if m.start() < pos:
        continue
    rest.append(stage_html[pos:m.start()])
    if m.group(0).startswith('<div'):
        pos = span_at(stage_html, m.start())
    else:
        tag = 'style' if m.group(0) == '<style' else 'script'
        pos = stage_html.index('</%s>' % tag, m.start()) + len(tag) + 3
rest.append(stage_html[pos:])
# loose pieces between panels (modals, comments) travel along; the region must still balance
depth = 0
for m in re.finditer(r'<div\b[^>]*>|</div>', stage_html):
    depth += 1 if m.group(0) != '</div>' else -1
    assert depth >= 0, 'stray </div> in the topic region'
assert depth == 0, 'unclosed <div> in the topic region'
loose = re.findall(r'<(\w+)[^>]*?\sid="([^"]+)"', re.sub(r'<!--.*?-->', '', ''.join(rest), flags=re.S))

groups = []
titles = [(m.start(), html.unescape(m.group(1)).strip())
          for m in re.finditer(r'<span>((?:📜|👑|🏛️|👤|🤖)\s*[๑-๕]\.[^<]+)</span>', nav)]
for i, (pos, name) in enumerate(titles):
    stop = titles[i + 1][0] if i + 1 < len(titles) else len(nav)
    topics = [(tid, html.unescape(label).strip()) for tid, label in
              re.findall(r'<button class="db-tab-btn[^"]*" onclick="switchTab\(\'([^\']+)\', this\)"[^>]*>([^<]*)</button>', nav[pos:stop])]
    groups.append((name, topics))
assert len(groups) == 5 and sum(len(t) for _, t in groups) == 68
assert sorted(t for _, ts in groups for t, _ in ts) == sorted(panels)

# ── tail: the old glossary panel, back-to-top, and the inline helper script ──
tail = src[src.index('<!-- GLOSSARY PANEL -->'):src.index('<script src="js/constitution.js"></script>')]
tail_script = src[src.index('<script src="js/portrait-hall.js"></script>'):src.index('</body>')]
tail_script = tail_script[len('<script src="js/portrait-hall.js"></script>'):].strip()
assert tail_script.startswith('<script>') and tail_script.endswith('</script>')

# ── mourning dedication (verbatim) and preamble ──────────────────────────────
m0 = src.index('<div class="mourning-container">')
mourning = src[m0:span_at(src, m0)]
p0 = src.index('<div class="preamble-section">')
ch0 = src.index('<section class="chapter-section" id="ch_0"')
pre = src[p0:ch0]
pre_title = re.search(r'<h2>(.*?)</h2>', pre).group(1)
pre_sub = re.search(r'<h2>.*?</h2>\s*<div[^>]*>(.*?)</div>', pre, re.S).group(1)
pre_paras = re.findall(r'<p class="preamble-p">(.*?)</p>', pre, re.S)

# ── chapters ─────────────────────────────────────────────────────────────────
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
    stop = starts[k + 1][0] if k + 1 < len(starts) else end_all
    secx = src[pos:stop]
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


# ── render ───────────────────────────────────────────────────────────────────
def split_emoji(label):
    m = re.match(r'^(\S+)\s+(.*)$', label)
    if m and not re.match(r'[฀-๿a-zA-Z0-9(]', m.group(1)):
        return m.group(1), m.group(2)
    return '•', label


hub = []
for gi, (gname, topics) in enumerate(groups):
    icon, rest_name = split_emoji(gname)
    rest_name = re.sub(r'^[๑-๕]\.\s*', '', rest_name)
    tiles = ''.join(
        '<button type="button" class="db-tab-btn nw-topic%s" data-tab="%s" onclick="switchTab(\'%s\', this)">'
        '<span class="nw-topic-ic">%s</span><span class="nw-topic-tx">%s</span></button>'
        % (' active' if tid == 'history-tab' else '', tid, tid, split_emoji(label)[0], html.escape(split_emoji(label)[1]))
        for tid, label in topics)
    hub.append('<details class="nw-group" data-group="%d" open><summary><span class="nw-group-ic">%s</span>'
               '<span class="nw-group-no">%s</span><span class="nw-group-name">%s</span><span class="nw-group-count">%s หัวข้อ</span></summary>'
               '<div class="nw-topics">%s</div></details>' % (gi, icon, thai('%02d' % (gi + 1)), html.escape(rest_name), thai(len(topics)), tiles))


def art_html(aid, origin, tag, body, cmp_html):
    key = ORIGIN[origin][0]
    cmp_btn = cmp_panel = ''
    if cmp_html:
        cmp_btn = '<button type="button" class="nw-art-act" data-compare="%s">เทียบกับ รธน. ๒๕๔๐</button>' % aid
        cmp_panel = '<div class="nw-compare" id="compare_%s" hidden>%s</div>' % (aid, cmp_html)
    return ('<article class="nw-art nw-o-%s" id="art_%s" data-origin="%s">'
            '<div class="nw-art-no"><span>มาตรา</span><b>%s</b></div>'
            '<div class="nw-art-main"><div class="nw-art-meta"><span class="nw-tag">%s</span>%s</div>'
            '<div class="nw-art-body">%s</div>%s</div></article>') % (key, aid, origin, thai(aid), html.escape(tag), cmp_btn, body, cmp_panel)


toc, doc = ['<a class="nw-toc-link" href="#preamble"><span class="nw-toc-no">คำปรารภ</span></a>'], []
for ch in chapters:
    rng = ''
    if ch['range']:
        a, b = ch['range']
        rng = 'ม.%s' % thai(a) if a == b else 'ม.%s–%s' % (thai(a), thai(b))
    toc.append('<a class="nw-toc-link" href="#%s"><span class="nw-toc-no">%s</span><span class="nw-toc-range">%s</span>'
               '<span class="nw-toc-name">%s</span></a>' % (ch['id'], html.escape(ch['no'] or 'หมวด'), rng, html.escape(ch['name'])))
    parts = ['<section class="nw-chapter" id="%s"><header class="nw-ch-head"><div class="nw-ch-no">%s</div>'
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

tpl = open('tools/site_template.html', encoding='utf-8').read()
page = (tpl.replace('{{HEAD_RES}}', '\n'.join(head_res + nav_res))
           .replace('{{MOURNING}}', mourning)
           .replace('{{HUB}}', ''.join(hub))
           .replace('{{STAGE}}', stage_html)
           .replace('{{PRE_TITLE}}', pre_title)
           .replace('{{PRE_SUB}}', pre_sub)
           .replace('{{PRE_PARAS}}', ''.join('<p>%s</p>' % p for p in pre_paras))
           .replace('{{TOC}}', ''.join(toc))
           .replace('{{CHAPTERS}}', '\n'.join(doc))
           .replace('{{FILTERS}}', filters)
           .replace('{{LEGEND}}', legend)
           .replace('{{TAIL}}', tail)
           .replace('{{TAIL_SCRIPT}}', tail_script)
           .replace('{{TOPIC_COUNT}}', thai(68)))
assert not re.search(r'\{\{[A-Z_]+\}\}', page), re.findall(r'\{\{[A-Z_]+\}\}', page)
open(OUT, 'w', encoding='utf-8').write(page)
print('%s: %d topics, %d chapters, %d articles, %d KB; loose elements kept: %s' % (OUT, len(panels), len(chapters), total, len(page.encode('utf-8')) // 1024, [i for _, i in loose]))
