# -*- coding: utf-8 -*-
"""2026-11-08 (user): the present year moves from ๒๗๓๘ to ๒๗๔๒ (the mid-term election amendment is ๒๗๔๒).

Canon arithmetic (dynasty from ๒๒๓๒, Rama IX born 5 Dec ๒๓๗๐ and crowned 9 Jun ๒๔๐๑, สัปปายะ from ๒๓๘๐):
dynasty ๕๑๐ ปี · Rama IX ๓๗๑ พรรษา, ๓๗๒ on 5 Dec ๒๗๔๒ · reign ๓๔๑ ปี · สัปปายะ ๓๖๒ ปี.
มหาราช reigns: ๑๑๒ years before Rama IX + ๓๔๑ = ๔๕๓ of ๕๑๐ = 88.8% -> ๘๙% (it still said ๔๓๔ / ๔๙๑, a figure
from before the ๒๗๓๘ sweep, which missed it).
Only the tabs that speak about the present are touched (same list as year_2738.py); '๒๗๓๘' elsewhere is
history (the ๒๗๓๖–๒๗๓๘ poll period). index.html gets the present-day panel and timeline.
Run from the repo root."""
import io
import sys

sys.path.insert(0, 'tools')
import tab_blocks as tb


def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)


def one(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:60], s.count(a))
    return s.replace(a, b)


YEAR_TABS = ['chakri', 'maharaj', 'national-days', 'rama9', 'sappaya', 'siam-medicine']
TOKENS = [('๒๗๓๘', '๒๗๔๒'), ('๓๖๘ พรรษา', '๓๗๒ พรรษา'), ('๓๖๗ พรรษา', '๓๗๑ พรรษา'), ('๓๓๗ ปี', '๓๔๑ ปี'),
          ('๓๕๘ ปี', '๓๖๒ ปี'), ('๕๐๖ ปี', '๕๑๐ ปี'), ('flex: 337 1 0', 'flex: 341 1 0'), ('flex:337 1 0', 'flex:341 1 0'),
          ('๔๓๔ / ๔๙๑ ปี', '๔๕๓ / ๕๑๐ ปี'), ('๘๘% ของอายุราชวงศ์', '๘๙% ของอายุราชวงศ์')]
LEFT = ['๓๖๗ พรรษา', '๓๓๗ ปี', '๓๕๘ ปี', '๕๐๖ ปี', '๔๙๑', '๒๗๓๘']


def sweep(s, tag):
    for a, b in TOKENS:
        s = s.replace(a, b)
    for x in LEFT:
        assert x not in s, (tag, x)
    return s


INDEX = [
    ('<div class="intro-year">๒๓๗๕ — ๒๗๓๘</div>', '<div class="intro-year">๒๓๗๕ — ๒๗๔๒</div>'),
    ('ปัจจุบัน พ.ศ. ๒๗๓๘</span>', 'ปัจจุบัน พ.ศ. ๒๗๔๒</span>'),
    ('<h2 class="h2">สยาม ณ พ.ศ. ๒๗๓๘</h2>', '<h2 class="h2">สยาม ณ พ.ศ. ๒๗๔๒</h2>'),
    ('<div class="big">๓๓๗<small>ปีแห่งการครองราชย์</small></div>', '<div class="big">๓๔๑<small>ปีแห่งการครองราชย์</small></div>'),
    ('พระชนมพรรษา ๓๖๗ พรรษา ด้วยวิทยาการแพทย์ไทย', 'พระชนมพรรษา ๓๗๑ พรรษา ด้วยวิทยาการแพทย์ไทย'),
    ('<div class="big">๓๑๗<small>เสียงฝ่ายรัฐบาล</small></div>', '<div class="big">๓๑๘<small>เสียงฝ่ายรัฐบาล</small></div>'),
    ('รัฐบาลรังสิมันต์ ๓ &mdash; ก้าวไกล ๒๖๐ + อุดมการณ์ใหม่ ๓๖ + ธรรมปัญญา ๒๑ ·',
     'รัฐบาลรังสิมันต์ ๓ (ครม. ชุดที่ ๒) &mdash; ก้าวไกล ๒๖๐ + อุดมการณ์ใหม่ ๓๖ + ธรรมปัญญา ๒๑ + สหายไทยแลนด์ ๑ ·'),
    ('<div class="big">๓๕๘<small>ปี</small></div>', '<div class="big">๓๖๒<small>ปี</small></div>'),
]
TL_OLD = ('<div class="tl-row hot rv"><div class="yr">๒๗๓๘<small>ปัจจุบัน</small></div><div><h4>รัฐบาลรังสิมันต์ ๓</h4>'
          '<p>ก้าวไกล · อุดมการณ์ใหม่ · ธรรมปัญญา ๓๑๗ เสียง &mdash; รัฐธรรมนูญ ๑,๑๖๐ มาตรา ๓๘ หมวด ยังคงเป็นกติกาสูงสุดของแผ่นดิน</p></div></div>')
TL_NEW = ('<div class="tl-row rv"><div class="yr">๒๗๓๙</div><div><h4>ครม. รังสิมันต์ ๓ ชุดที่ ๒</h4>'
          '<p>พรรคสหายไทยแลนด์เข้าร่วมรัฐบาล &mdash; ก้าวไกล · อุดมการณ์ใหม่ · ธรรมปัญญา · สหายไทยแลนด์ ๓๑๘ เสียง</p></div></div>\n'
          '        <div class="tl-row hot rv"><div class="yr">๒๗๔๒<small>ปัจจุบัน</small></div><div><h4>รัฐธรรมนูญแก้ไขเพิ่มเติม &mdash; เลือกตั้งกลางวาระ</h4>'
          '<p>รัฐสภาเห็นชอบ ม.๙๙/๑&ndash;๙๙/๘ &mdash; รัฐธรรมนูญ ๑,๑๖๐ มาตรา ๓๘ หมวด ยังคงเป็นกติกาสูงสุดของแผ่นดิน</p></div></div>')

for t in YEAR_TABS:
    f = 'src/tabs/%s-tab.html' % t
    s = rd(f)
    wr(f, sweep(s, f))
    print('tab', f)

s = rd('index.html')
for a, b in INDEX:
    s = one(s, a, b, 'index')
s = one(s, TL_OLD, TL_NEW, 'index timeline')
assert '๒๗๓๘' not in s
wr('index.html', s)
print('index')

f = 'website_constitution.html'
s = rd(f)
for t in YEAR_TABS:
    p0 = s.index('<div id="%s-tab"' % t)
    p1 = tb.div_span(s, p0)
    s = s[:p0] + sweep(s[p0:p1], 'old ' + t) + s[p1:]
wr(f, s)
print('old')
