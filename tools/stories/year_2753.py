# -*- coding: utf-8 -*-
"""2026-11-19 (user): the present year moves from ๒๗๔๒ to ๒๗๕๓, with the ๒๗๔๒–๒๗๕๓ story.

Canon arithmetic (dynasty from ๒๒๓๒, Rama IX born 5 Dec ๒๓๗๐ and crowned 9 Jun ๒๔๐๑, สัปปายะ from ๒๓๘๐):
dynasty ๕๒๑ ปี · Rama IX ๓๘๒ พรรษา, ๓๘๓ on 5 Dec ๒๗๕๓ · reign ๓๕๒ ปี · สัปปายะ ๓๗๓ ปี.
มหาราช reigns: ๑๑๒ years before Rama IX + ๓๕๒ = ๔๖๔ of ๕๒๑ = 89.1% -> ๘๙%.
Same tabs as year_2742.py. '๒๗๔๒' elsewhere is now history (the mid-term amendment) and stays.
The home page's present-day card moves to PM 36 ธีรภัทร (ภัทร): ก้าวไกล ๒๘๗ + ไทยรักษาชาติ ๙๘ = ๓๘๕
after the ๒๗๔๘ mid-term election (user's timeline). Run from the repo root."""
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
TOKENS = [('๒๗๔๒', '๒๗๕๓'), ('๓๗๒ พรรษา', '๓๘๓ พรรษา'), ('๓๗๑ พรรษา', '๓๘๒ พรรษา'), ('๓๔๑ ปี', '๓๕๒ ปี'),
          ('๓๖๒ ปี', '๓๗๓ ปี'), ('๕๑๐ ปี', '๕๒๑ ปี'), ('flex: 341 1 0', 'flex: 352 1 0'), ('flex:341 1 0', 'flex:352 1 0'),
          ('๔๕๓ / ๕๒๑ ปี', '๔๖๔ / ๕๒๑ ปี')]
LEFT = ['๓๗๑ พรรษา', '๓๔๑ ปี', '๓๖๒ ปี', '๕๑๐ ปี', '๔๕๓', '๒๗๔๒']


def sweep(s, tag):
    for a, b in TOKENS:
        s = s.replace(a, b)
    for x in LEFT:
        assert x not in s, (tag, x)
    return s


INDEX = [
    ('<div class="intro-year">๒๓๗๕ — ๒๗๔๒</div>', '<div class="intro-year">๒๓๗๕ — ๒๗๕๓</div>'),
    ('ปัจจุบัน พ.ศ. ๒๗๔๒</span>', 'ปัจจุบัน พ.ศ. ๒๗๕๓</span>'),
    ('<h2 class="h2">สยาม ณ พ.ศ. ๒๗๔๒</h2>', '<h2 class="h2">สยาม ณ พ.ศ. ๒๗๕๓</h2>'),
    ('<div class="big">๓๔๑<small>ปีแห่งการครองราชย์</small></div>', '<div class="big">๓๕๒<small>ปีแห่งการครองราชย์</small></div>'),
    ('พระชนมพรรษา ๓๗๑ พรรษา ด้วยวิทยาการแพทย์ไทย', 'พระชนมพรรษา ๓๘๒ พรรษา ด้วยวิทยาการแพทย์ไทย'),
    ('<h3>นายกรัฐมนตรีคนที่ ๓๕ · &ldquo;โรม&rdquo;</h3>', '<h3>นายกรัฐมนตรีคนที่ ๓๖ · &ldquo;ภัทร&rdquo;</h3>'),
    ('<div class="big">๓๑๘<small>เสียงฝ่ายรัฐบาล</small></div>', '<div class="big">๓๘๕<small>เสียงฝ่ายรัฐบาล</small></div>'),
    ('<div class="big">๓๖๒<small>ปี</small></div>', '<div class="big">๓๗๓<small>ปี</small></div>'),
]
GOV_P_START = '<p>รังสิมันต์ โรม (พรรคก้าวไกล) · รัฐบาลรังสิมันต์ ๓ (ครม. ชุดที่ ๒)'
GOV_P_NEW = ('<p>ธีรภัทร วัฒนากร (พรรคก้าวไกล) · รัฐบาลภัทร หลังเลือกตั้งกลางเทอม ๑๓ ต.ค. ๒๗๔๘ &mdash; '
             'ก้าวไกล ๒๘๗ + ไทยรักษาชาติ ๙๘ · ครม. ก้าวไกลพรรคเดียว ไทยรักษาชาติรับตำแหน่งรัฐมนตรีช่วย</p>')
TL_OLD_HOT = '<div class="tl-row hot rv"><div class="yr">๒๗๔๒<small>ปัจจุบัน</small></div>'
TL_ADD = (
    '        <div class="tl-row rv"><div class="yr">๒๗๔๔<small>๑๒ พ.ค.</small></div><div><h4>ธีรภัทร (ภัทร) นายกฯ คนที่ ๓๖</h4>'
    '<p>ก้าวไกล ๒๖๕ ที่นั่ง &mdash; ไทยรักษาชาติฉีก MOU มาร่วมรัฐบาล ๓๕๑ เสียง</p></div></div>\n'
    '        <div class="tl-row rv"><div class="yr">๒๗๔๘<small>๑๓ ต.ค.</small></div><div><h4>เลือกตั้งกลางเทอมครั้งแรก</h4>'
    '<p>ก้าวไกล ๒๘๗ · ไทยรักษาชาติ ๙๘ &mdash; นิวตรอนชนะนครปฐม เขต ๑ ด้วยคะแนน ๑๐๐%</p></div></div>\n'
    '        <div class="tl-row rv"><div class="yr">๒๗๕๐<small>๑๐–๑๔ ธ.ค.</small></div><div><h4>กบฏจอมพลรวบอำนาจ ล้มเหลว</h4>'
    '<p>นิวตรอนยืนประท้วงเดี่ยวที่อนุสาวรีย์ประชาธิปไตย &mdash; รัฐบาลกลับทำเนียบ นิวตรอนเป็นรัฐบุรุษคนที่สี่</p></div></div>\n'
    '        <div class="tl-row hot rv"><div class="yr">๒๗๕๓<small>ปัจจุบัน</small></div><div><h4>รัฐบาลภัทร</h4>'
    '<p>หลังยุบสหายไทยแลนด์ (๒๗๕๑) และ ๖ พรรคตามกฎหมายความโปร่งใสพรรค (๒๗๕๒) &mdash; '
    'รัฐธรรมนูญ ๑,๑๖๐ มาตรา ๓๘ หมวด ยังคงเป็นกติกาสูงสุดของแผ่นดิน</p></div></div>')

if __name__ == '__main__':
    for t in YEAR_TABS:
        f = 'src/tabs/%s-tab.html' % t
        wr(f, sweep(rd(f), f))
    s = rd('index.html')
    for a, b in INDEX:
        s = one(s, a, b, 'index')
    p0 = s.index(GOV_P_START)
    s = s[:p0] + GOV_P_NEW + s[s.index('</p>', p0) + 4:]
    # the ๒๗๔๒ row stops being "now"; the new rows follow it
    s = one(s, TL_OLD_HOT, '<div class="tl-row rv"><div class="yr">๒๗๔๒</div>', 'tl hot')
    a = s.index('<div class="tl-row rv"><div class="yr">๒๗๔๒</div>')
    e = s.index('</div></div>', a) + len('</div></div>')
    s = s[:e] + '\n' + TL_ADD + s[e:]
    wr('index.html', s)
    f = 'website_constitution.html'
    s = rd(f)
    for t in YEAR_TABS:
        p0 = s.index('<div id="%s-tab"' % t)
        p1 = tb.div_span(s, p0)
        s = s[:p0] + sweep(s[p0:p1], 'old ' + t) + s[p1:]
    wr(f, s)
    print('year moved to ๒๗๕๓')
