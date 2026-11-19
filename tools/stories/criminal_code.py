# -*- coding: utf-8 -*-
"""New tab: ประมวลกฎหมายอาญา of this universe (user, 2026-11-19).

Text: the real ประมวลกฎหมายอาญา as promulgated in พ.ศ. ๒๔๙๙ (tools/data/criminal_code_2499.txt, from Wikisource),
the base the user chose. Wording is unchanged. Canon differences, as the user set them:
  * the real มาตรา ๑๑๒ (ความผิดฐานหมิ่นประมาทพระมหากษัตริย์) does not exist; the real ๑๑๓ is ๑๑๒ and every later
    section moves down by one (๓๙๘ -> ๓๙๗), cross-references included;
  * penalties are those from before ๖ ต.ค. ๒๕๑๙ — no increase from คำสั่งคณะปฏิรูปการปกครองแผ่นดิน ฉบับที่ ๔๑
    (real ๑๑๘ ๑๓๓–๑๓๖ ๑๓๘ ๑๙๘ ๒๐๖ ๓๒๖ ๓๒๘ ๓๙๓); the ๒๔๙๙ text already carries them.
The promulgating act (its date and countersignature) is left out: only the code itself is shown.
Both sites. Run once from the repo root."""
import html
import io
import re
import sys

sys.path.insert(0, 'tools')
sys.path.insert(0, 'tools/stories')
import tab_blocks as tb
from story_2742_2753 import add_tab, rd, wr, OLD

TH = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
AR = str.maketrans('0123456789', '๐๑๒๓๔๕๖๗๘๙')
NUM = r'[๐-๙]+'
REF = re.compile(r'(มาตรา\s*)(' + NUM + r')((?:\s*(?:[-–]|ถึง|และ|หรือ|,)\s*(?:มาตรา\s*)?' + NUM + r')*)')
ORDER41_REAL = [118, 133, 134, 135, 136, 138, 198, 206, 326, 328, 393]   # 112 is gone in this universe


def th(n): return str(n).translate(AR)
def val(t): return int(t.translate(TH))
def canon(n): return n - 1 if n > 112 else n


# ---------------------------------------------------------------- parse
src = rd('tools/data/criminal_code_2499.txt')
m1 = [m.start() for m in re.finditer(r'มาตรา๑(?![๐-๙])', src)][1]        # the code's own มาตรา ๑ (the act has one too)
start = src.rindex('ภาค ๑', 0, m1)
end = src.index('\nหมายเหตุ', m1)
body = src[start:end]
body = re.sub(r'(?<!\n)มาตรา(?=[๐-๙])', '\nมาตรา', body)            # two sections sometimes share a line
lines = [l.strip() for l in body.split('\n') if l.strip()]
HEAD = re.compile(r'^(ภาค|ลักษณะ|หมวด|ส่วนที่)\s*([๐-๙]+)$')

nodes, i = [], 0
while i < len(lines):
    l = lines[i]
    h = HEAD.match(l)
    if h:
        nodes.append(['head', h.group(1), h.group(2), lines[i + 1]])
        i += 2
        continue
    s = re.match(r'^มาตรา([๐-๙]+)(.*)$', l)
    if s:
        nodes.append(['sec', val(s.group(1)), [s.group(2).strip()]])
    elif nodes and nodes[-1][0] == 'head':        # a heading title that runs over two lines
        nodes[-1][3] += ' ' + l
    else:
        assert nodes and nodes[-1][0] == 'sec', ('text before any section', l[:60])
        nodes[-1][2].append(l)
    i += 1

nums = [n[1] for n in nodes if n[0] == 'sec']
assert nums == list(range(1, 399)), 'sections are not ๑–๓๙๘ in order'

# ---------------------------------------------------------------- canon numbering
refs_to_112 = []


def remap(text, where):
    def one(m):
        def num(k):
            n = val(k.group(0))
            if n == 112:
                refs_to_112.append((where, m.group(0)))
            return th(canon(n))
        return m.group(1) + re.sub(NUM, num, m.group(0)[len(m.group(1)):])
    return REF.sub(one, text)


out = []
for n in nodes:
    if n[0] == 'sec':
        if n[1] == 112:
            continue
        out.append(['sec', canon(n[1]), [remap(p, n[1]) for p in n[2]], n[1]])
    else:
        out.append(n)
assert not refs_to_112, refs_to_112          # nothing else in the code points at the real ม.๑๑๒
assert [n[1] for n in out if n[0] == 'sec'] == list(range(1, 398))

# ---------------------------------------------------------------- render
TXT = "color: var(--nw-text-2, var(--text-muted)); font-size: 14px; line-height: 1.9; margin: 0 0 6px"
SEC = "background: var(--nw-surface-2, rgba(15,18,25,0.6)); border: 1px solid var(--nw-line, rgba(255,255,255,0.08)); border-radius: 10px; padding: 12px 16px; margin: 0 0 8px"
NO = "color: #fcd34d; font-weight: 800; margin-right: 6px"
SUM = "cursor: pointer; font-weight: 800; color: #fcd34d; font-size: 15.5px; padding: 12px 16px"
DET = "border: 1px solid rgba(252,211,77,0.35); border-radius: 12px; margin: 0 0 10px; background: rgba(252,211,77,0.04)"
H4 = "font-family: var(--nw-serif, 'Outfit', sans-serif); font-size: 19px; font-weight: 800; color: #fcd34d; margin: 26px 0 12px; text-align: center"
H5 = "font-size: 15px; font-weight: 800; color: var(--nw-text, var(--text)); margin: 18px 0 8px; text-align: center"
H6 = "font-size: 14px; font-weight: 700; color: var(--nw-text, var(--text)); margin: 14px 0 8px; text-align: center; opacity: .9"
MARK = "display: inline-block; font-size: 11px; font-weight: 700; color: #1a0a0a; background: #86efac; border-radius: 9px; padding: 1px 8px; margin-left: 6px; vertical-align: middle"
order41 = {canon(n) for n in ORDER41_REAL}


def esc(t): return html.escape(t, quote=False)


def sec_html(n):
    _, no, paras, real = n
    tag = ''          # no marks: ๖ ต.ค. ๒๕๑๙ and the reform council's order do not exist in this universe (user)
    first = '<p><b>มาตรา %s</b>%s%s</p>' % (th(no), esc(paras[0]), tag)
    rest = ''.join('<p class="cc-li">%s</p>' % esc(p) if re.match(r'^\([๐-๙ก-ฮ]+\)', p) else '<p>%s</p>' % esc(p)
                   for p in paras[1:])
    return '<div class="cc-sec" id="cc_%d">%s%s</div>' % (no, first, rest)


parts, open_det, rng = [], False, []


def close():
    global open_det
    if open_det:
        parts.append('</details>')
        open_det = False


# group: one <details> per ลักษณะ; ภาค ๓ (ลหุโทษ, no ลักษณะ) is one too
sections_by_group = []
k = 0
while k < len(out):
    n = out[k]
    if n[0] == 'head' and n[1] == 'ภาค':
        close()
        parts.append('<h4 class="cc-h4">ภาค %s &middot; %s</h4>' % (n[2], esc(n[3])))
        nxt = out[k + 1]
        if not (nxt[0] == 'head' and nxt[1] == 'ลักษณะ'):
            parts.append(('DET', 'ภาค %s %s' % (n[2], n[3]), k + 1))
            open_det = True
    elif n[0] == 'head' and n[1] == 'ลักษณะ':
        close()
        parts.append(('DET', 'ลักษณะ %s %s' % (n[2], n[3]), k + 1))
        open_det = True
    elif n[0] == 'head':
        parts.append('<div class="%s">%s %s<br>%s</div>' % ('cc-h5' if n[1] == 'หมวด' else 'cc-h6', n[1], n[2], esc(n[3])))
    else:
        parts.append(sec_html(n))
    k += 1
close()


def det_range(start):
    nos = []
    for n in out[start:]:
        if n[0] == 'head' and n[1] in ('ภาค', 'ลักษณะ'):
            break
        if n[0] == 'sec':
            nos.append(n[1])
    return nos[0], nos[-1]


html_parts = []
for p in parts:
    if isinstance(p, tuple):
        a, b = det_range(p[2])
        html_parts.append('<details class="cc-det"><summary>%s &nbsp;<span class="cc-rng">(ม.%s&ndash;%s)</span></summary>'
                          '<div class="cc-in">' % (esc(p[1]), th(a), th(b)))
    elif p == '</details>':
        html_parts.append('</div></details>')
    else:
        html_parts.append(p)
CSS = ('<style>.cc-code .cc-sec{%s}.cc-code p{%s}.cc-code .cc-li{padding-left:22px}.cc-code b{%s}.cc-code .cc-mark{%s}'
       '.cc-code details{%s}.cc-code summary{%s}.cc-code .cc-rng{font-weight:600;opacity:.75}.cc-code .cc-in{padding:4px 14px 12px}'
       '.cc-code .cc-h4{%s}.cc-code .cc-h5{%s}.cc-code .cc-h6{%s}</style>') % (SEC, TXT, NO, MARK, DET, SUM, H4, H5, H6)
CODE = '<div class="cc-code">' + CSS + '\n'.join(html_parts) + '</div>'
assert tb.balanced(CODE)

real_list = ' '.join('%s&rarr;%s' % (th(n), th(canon(n))) for n in ORDER41_REAL)
BLOCKS = [
    ('stats', [('๓๙๗ มาตรา', 'ไม่มีมาตรา ๑๑๒ แบบในโลกจริง &mdash; มาตราที่ตามมาเลื่อนลงหนึ่ง'),
               ('๓ ภาค', 'บทบัญญัติทั่วไป &middot; ความผิด &middot; ลหุโทษ'),
               ('มาตรา ๑๑๒', 'ความผิดฐานกบฏ (มาตรา ๑๑๓ ในโลกจริง)')]),
    ('note', '📌 <strong>ต่างจากโลกจริงอย่างไร</strong> &mdash; ประมวลกฎหมายอาญาของจักรวาลนี้ไม่มีความผิดฐานหมิ่นประมาท ดูหมิ่น '
             'หรือแสดงความอาฆาตมาดร้ายพระมหากษัตริย์ (มาตรา ๑๑๒ ในโลกจริง) &mdash; มาตรา ๑๑๓ ในโลกจริง (ความผิดฐานกบฏ) '
             'จึงเป็น<strong>มาตรา ๑๑๒</strong> และทุกมาตราหลังจากนั้นเลื่อนลงหนึ่งจนถึงมาตรา ๓๙๗ รวมทั้งการอ้างถึงมาตราในตัวบท '
             ''),
    ('p', 'ถ้อยคำในตัวบทเหมือนประมวลกฎหมายอาญาของโลกจริงฉบับประกาศใช้ พ.ศ. ๒๔๙๙ ทุกตัวอักษร เปลี่ยนเฉพาะเลขมาตรา '
          '&mdash; กดที่ชื่อลักษณะเพื่อเปิดอ่าน'),
    ('raw', CODE, CODE),
]

def replace_tab():
    tid, icon, title = 'criminal-code-tab', '⚖️', 'ประมวลกฎหมายอาญา'
    lead = 'ประมวลกฎหมายอาญาที่ใช้บังคับในราชอาณาจักร ๓ ภาค ๓๙๗ มาตรา &mdash; ไม่มีความผิดฐานหมิ่นพระมหากษัตริย์'
    wr('src/tabs/%s.html' % tid, '<div id="%s" class="db-tab-content">\n%s\n</div>\n' % (tid, tb.new_render(icon, title, lead, BLOCKS)))
    s = rd(OLD)
    p0 = s.index('<div id="%s"' % tid)
    p1 = tb.div_span(s, p0)
    new = '<div id="%s" class="db-tab-content">\n%s\n</div>' % (tid, tb.old_render(icon, title, lead, BLOCKS, accent=('#fcd34d', '252,211,77')))
    assert tb.balanced(new)
    wr(OLD, s[:p0] + new + s[p1:])


if __name__ == '__main__' and '--replace' in sys.argv:
    replace_tab()
    print('criminal code tab rebuilt')
elif __name__ == '__main__':
    add_tab('criminal-code-tab', '⚖️', 'ประมวลกฎหมายอาญา', 'ประมวลกฎหมายอาญา',
            'ประมวลกฎหมายอาญาที่ใช้บังคับในราชอาณาจักร ๓ ภาค ๓๙๗ มาตรา &mdash; ไม่มีความผิดฐานหมิ่นพระมหากษัตริย์'
            '', BLOCKS, 'hierarchy-laws-tab', ('#fcd34d', '252,211,77'))
    for f in ['index.html', 'README.md', 'tools/site_template.html', OLD]:
        t = rd(f)
        wr(f, t.replace('๘๐ หัวข้อ', '๘๑ หัวข้อ').replace('๘๐ แถบ', '๘๑ แถบ'))
    print('criminal code: %d sections, %d marked' % (len(nums) - 1, len(order41)))
