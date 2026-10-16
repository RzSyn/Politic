# -*- coding: utf-8 -*-
"""2026-10-16: (A) Atom replaces Somkid as deputy PM (economy) on the economy and public-finance tabs;
(B) topic count ๖๙ -> ๗๖; (C) the present year moves from ๒๗๓๑ to ๒๗๓๘.

Year arithmetic (canon: dynasty from ๒๒๓๒, Rama IX born 5 Dec ๒๓๗๐ and crowned ๒๔๐๑, สัปปายะ from ๒๓๘๐):
dynasty ๕๐๖ ปี (crossed ๕๐๐ in ๒๗๓๒) · Rama IX ๓๖๗ พรรษา, ๓๖๘ on 5 Dec ๒๗๓๘ · reign ๓๓๗ ปี · สัปปายะ ๓๕๘ ปี.
Only tabs that speak about the present are touched; '๒๗๓๑' elsewhere is history (the 2731 election).
Run from the repo root."""
import io, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb

def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)
def one(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:60], s.count(a)); return s.replace(a, b)

# ---- (A) ----
ATOM = 'ฯพณฯ ศ.ดร.นพ.วิทยสิทธิ์ ประสิทธิ์ผล'
A = [('src/tabs/welfare-economy-tab.html', [
        ('สมคิด จาตุศรีพิทักษ์ (ทักษิประชา)', f'{ATOM} (ก้าวไกล)'),
        ('ภาพรวมนโยบายเศรษฐกิจ', 'ภาพรวมนโยบายเศรษฐกิจ &mdash; ควบรัฐมนตรีว่าการกระทรวงการต่างประเทศ'),
        ('ผู้รับผิดชอบในรัฐบาลปัจจุบัน', 'ผู้รับผิดชอบในรัฐบาลปัจจุบัน (รัฐบาลรังสิมันต์ ๒)')]),
     ('src/tabs/public-finance-tab.html', [
        ('(ส่วน ดร.สมคิด จาตุศรีพิทักษ์ อดีตนายกฯ คนที่ ๓๒ เป็นรองนายกรัฐมนตรีฝ่ายเศรษฐกิจ)',
         f'(รองนายกรัฐมนตรีฝ่ายเศรษฐกิจคือ {ATOM} อดีตนายกฯ คนที่ ๓๓)')])]
OLD_A = [p for _, ps in A for p in ps]

# ---- (B) ----
B = [('๖๙ หัวข้อ', '๗๖ หัวข้อ'), ('๖๙ แถบ', '๗๖ แถบ'), ('panels 69', 'panels 76')]

# ---- (C) ----
YEAR_TABS = ['chakri', 'maharaj', 'national-days', 'rama9', 'sappaya', 'siam-medicine']
C_SPECIFIC = [
    ('๔๙๙ ปีแห่งราชวงศ์จักรี (พ.ศ. ๒๒๓๒ – ๒๗๓๑)', '๕๐๖ ปีแห่งราชวงศ์จักรี (พ.ศ. ๒๒๓๒ – ๒๗๓๘ · ครบ ๕๐๐ ปีเมื่อ พ.ศ. ๒๗๓๒)'),
    ('ถึงปี ๒๗๓๑ ราชวงศ์ดำรงมา ๔๙๙ ปี', 'ถึงปี ๒๗๓๘ ราชวงศ์ดำรงมา ๕๐๖ ปี (ครบ ๕๐๐ ปีเมื่อ พ.ศ. ๒๗๓๒)'),
]
C_TOKENS = [('๒๗๓๑', '๒๗๓๘'), ('๓๖๑ พรรษา', '๓๖๘ พรรษา'), ('๓๖๐ พรรษา', '๓๖๗ พรรษา'), ('๓๓๐ ปี', '๓๓๗ ปี'),
            ('๓๕๑ ปี', '๓๕๘ ปี'), ('๔๙๙ ปี', '๕๐๖ ปี'), ('(๓๒๒ ปี)', '(๓๓๗ ปี)')]

def year_sweep(s, tag):
    for a, b in C_SPECIFIC:
        s = s.replace(a, b)
    for a, b in C_TOKENS:
        s = s.replace(a, b)
    return s

INDEX = [
    ('<div class="intro-year">๒๓๗๕ — ๒๗๓๑</div>', '<div class="intro-year">๒๓๗๕ — ๒๗๓๘</div>'),
    ('ปัจจุบัน พ.ศ. ๒๗๓๑</span>', 'ปัจจุบัน พ.ศ. ๒๗๓๘</span>'),
    ('<h2 class="h2">สยาม ณ พ.ศ. ๒๗๓๑</h2>', '<h2 class="h2">สยาม ณ พ.ศ. ๒๗๓๘</h2>'),
    ('<div class="big">๓๒๒<small>ปีแห่งการครองราชย์</small></div>', '<div class="big">๓๓๗<small>ปีแห่งการครองราชย์</small></div>'),
    ('<p>เสด็จขึ้นครองราชย์ ๙ มิถุนายน ๒๔๐๑ · พระชนมพรรษา ๓๖๐ พรรษา ด้วยวิทยาการแพทย์ไทยอันดับ ๑ ของโลก</p>',
     '<p>เสด็จขึ้นครองราชย์ ๙ มิถุนายน ๒๔๐๑ · พระชนมพรรษา ๓๖๗ พรรษา ด้วยวิทยาการแพทย์ไทยอันดับ ๑ ของโลก · ราชวงศ์จักรีครบ ๕๐๐ ปีเมื่อ พ.ศ. ๒๗๓๒</p>'),
    ('<h3>นายกรัฐมนตรีคนที่ ๓๓ · &ldquo;อะตอม&rdquo;</h3>', '<h3>นายกรัฐมนตรีคนที่ ๓๕ · &ldquo;โรม&rdquo;</h3>'),
    ('<div class="big">88.96%<small>เสียงในสภา</small></div>', '<div class="big">๓๑๗<small>เสียงฝ่ายรัฐบาล</small></div>'),
    ('<p>ศ.ดร.นพ.วิทยสิทธิ์ ประสิทธิ์ผล (ฯพณฯ) · วาระที่ ๒ ปีที่ ๒ · ทำลายสถิติโลก 86.48% ของรัฐบาลทักษิณเมื่อ พ.ศ. ๒๗๒๒</p>',
     '<p>รังสิมันต์ โรม (พรรคก้าวไกล) · รัฐบาลรังสิมันต์ ๒ &mdash; ก้าวไกล ๒๖๐ + อุดมการณ์ใหม่ ๓๖ + ธรรมปัญญา ๒๑ · ความนิยมพรรคก้าวไกล 84.29% (ต.ค. ๒๗๓๗)</p>'),
    ('<div class="big">๓๔๓<small>ปี</small></div>', '<div class="big">๓๕๘<small>ปี</small></div>'),
    ('<span>นายกฯ ๓๓ คน</span>', '<span>นายกฯ ๓๕ คน</span>'),
]
TL_OLD = ('<div class="tl-row hot rv"><div class="yr">๒๗๓๑<small>ปัจจุบัน</small></div><div><h4>วาระที่ ๒ ปีที่ ๒</h4>'
          '<p>รัฐธรรมนูญ ๑,๑๖๐ มาตรา ๓๘ หมวด ยังคงเป็นกติกาสูงสุดของแผ่นดิน</p></div></div>')
TL_NEW = ('<div class="tl-row rv"><div class="yr">๒๗๓๑</div><div><h4>รังสิมันต์ โรม นายกฯ คนที่ ๓๕</h4><p>การกลับมาของก้าวไกลในรอบ ๕๑ ปี &mdash; ขั้วส้มแดง ๔๑๒ เสียง</p></div></div>\n'
          '        <div class="tl-row rv"><div class="yr">๒๗๓๒</div><div><h4>ราชวงศ์จักรีครบ ๕๐๐ ปี</h4><p>นับจากการสถาปนาราชวงศ์ใน พ.ศ. ๒๒๓๒</p></div></div>\n'
          '        <div class="tl-row rv"><div class="yr">๒๗๓๖</div><div><h4>ม็อบ ศนท. &mdash; นายกฯ ยุบสภาคืนอำนาจ</h4><p>เลือกตั้งใหม่ผลเท่าเดิม ก่อนทักษิประชาฉีก MOU</p></div></div>\n'
          '        <div class="tl-row hot rv"><div class="yr">๒๗๓๘<small>ปัจจุบัน</small></div><div><h4>รัฐบาลรังสิมันต์ ๒</h4>'
          '<p>ก้าวไกล · อุดมการณ์ใหม่ · ธรรมปัญญา ๓๑๗ เสียง &mdash; รัฐธรรมนูญ ๑,๑๖๐ มาตรา ๓๘ หมวด ยังคงเป็นกติกาสูงสุดของแผ่นดิน</p></div></div>')

# ---- apply: new site sources ----
for f, pairs in A:
    s = rd(f)
    for a, b in pairs: s = one(s, a, b, f)
    wr(f, s); print('A', f)
for t in YEAR_TABS:
    f = f'src/tabs/{t}-tab.html'; s = rd(f); s2 = year_sweep(s, f)
    assert '๒๗๓๑' not in s2; wr(f, s2); print('C', f, s != s2)
for f in ['tools/site_template.html', 'README.md']:
    s = rd(f)
    for a, b in B: s = s.replace(a, b)
    wr(f, s); print('B', f)
s = rd('index.html')
for a, b in B: s = s.replace(a, b)
for a, b in INDEX: s = one(s, a, b, 'index')
s = one(s, TL_OLD, TL_NEW, 'index timeline')
assert '๒๗๓๑' in s  # the new 2731 timeline row
wr('index.html', s); print('index')

# ---- apply: old site ----
f = 'website_constitution.html'; s = rd(f)
for a, b in OLD_A: s = one(s, a, b, 'old A')
for a, b in B: s = s.replace(a, b)
for t in YEAR_TABS:
    p0 = s.index(f'<div id="{t}-tab"'); p1 = tb.div_span(s, p0)
    seg = year_sweep(s[p0:p1], t); assert '๒๗๓๑' not in seg, t
    s = s[:p0] + seg + s[p1:]
wr(f, s); print('old')
