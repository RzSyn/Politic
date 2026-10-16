# -*- coding: utf-8 -*-
"""2026-10-16 batch (user): Democrat card fix; "รัฐบาลรังสิมันต์ ๒" -> "๓" (the current government is
Rome 3, after the 3rd election in May ๒๗๓๗); orange-party Rome card gets terms ๒ (๒๗๓๖, same seats as
term ๑, slightly different votes) and ๓ (๒๗๓๗, the current parliament: ๒๖๐ seats); roster row ๓๕;
a "สถานะในสภาชุดปัจจุบัน" line on every active party card. Run from the repo root."""
import io, re, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb

def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)
def one(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:60], s.count(a)); return s.replace(a, b)

DEM = ('อดีตนายกฯ คนที่ ๑๓ และนายกคนปัจจุบัน คนที่ ๒๘', 'อดีตนายกฯ คนที่ ๑๓ และ ๒๘')
ROME_FILES = ['src/tabs/atom-tab.html', 'src/tabs/cabinet-tab.html', 'src/tabs/new-red-party-tab.html',
              'src/tabs/welfare-economy-tab.html', 'index.html', 'website_constitution.html']

# ---- orange-party Rome card ----
TERMS = [  # label, votes, seats, district, list
    ('• วาระที่ ๒ (พ.ศ. ๒๗๓๖)', '24,212,906', 258, 217, 41),
    ('• วาระที่ ๓ (พ.ศ. ๒๗๓๗)', '24,309,457', 260, 218, 42),
]
def pct(seats): return f'{seats / 5:.1f}%'
def term_block(t1, label, votes, seats, d, l):
    b = t1.replace('<!-- Term 1 -->', '<!-- Term ' + label[12] + ' -->')
    b = re.sub(r'• วาระที่ ๑ \(พ\.ศ\. ๒๗๓๑\)', label, b)
    b = b.replace('24,148,120', votes).replace('(258/500)', f'({seats}/500)').replace('51.6%', pct(seats))
    b = re.sub(r'(>)258(</div>)', lambda m: m.group(1) + str(seats) + m.group(2), b, count=1)
    b = re.sub(r'(>)217(</div>)', lambda m: m.group(1) + str(d) + m.group(2), b, count=1)
    b = re.sub(r'(>)41(</div>)', lambda m: m.group(1) + str(l) + m.group(2), b, count=1)
    return b
ROME_WORK_OLD = 'เพิ่งเข้ารับตำแหน่ง ยังไม่มีผลงานให้บันทึก'
ROME_WORK_NEW = ('ยุบสภาตามข้อเรียกร้องของ ศนท. แล้วชนะเลือกตั้งซ้ำด้วยผลเท่าเดิมใน พ.ศ. ๒๗๓๖ (รัฐบาลโรม ๒) '
                 'จากนั้นทักษิประชาฉีก MOU &mdash; การเลือกตั้งครั้งที่ ๓ เดือนพฤษภาคม ๒๗๓๗ ผลคงที่ เป็น<strong>รัฐบาลโรม ๓</strong> '
                 'ก้าวไกล ๒๖๐ + อุดมการณ์ใหม่ ๓๖ + ธรรมปัญญา ๒๑ = ๓๑๗ เสียง &mdash; ความนิยมพรรค 84&ndash;89% หนุนเป็นนายกฯ 59.72%')

def orange(s, site):
    a = s.index('<!-- 8. รังสิมันต์ โรม'); st = s.index('<div', a); e = tb.div_span(s, st)
    card = s[st:e]
    if 'วาระที่ ๓ (พ.ศ. ๒๗๓๗)' in card:
        return s
    card = card.replace('สถิติผลเลือกตั้ง ๑ วาระ', 'สถิติผลเลือกตั้ง ๓ วาระ')
    t0 = card.index('<!-- Term 1 -->')
    blk_start = card.index('<div', t0); blk_end = tb.div_span(card, blk_start)
    t1 = card[t0:blk_end]
    extra = ''.join('\n  ' + term_block(t1, *t) for t in TERMS)
    card = card[:blk_end] + extra + card[blk_end:]
    card = one(card, ROME_WORK_OLD, ROME_WORK_NEW, site + ' work')
    card = card.replace('📜 ผลงาน:', '📜 รัฐบาลโรม ๑&ndash;๓:')
    assert tb.balanced(card), site
    return s[:st] + card + s[e:]

# ---- roster row 35 ----
ROW_OLD = 'ก้าวไกลได้ ๕๑.๖% (๒๕๘ ที่นั่ง) เกินครึ่งสภาด้วยพรรคเดียว'
ROW_NEW = (ROW_OLD + ' | ยุบสภาตามข้อเรียกร้องของ ศนท. แล้วเลือกตั้งใหม่ ๒๗๓๖ ผลเท่าเดิม (รัฐบาลโรม ๒) | ทักษิประชาฉีก MOU '
           'ลากไทยรักไทยไปเป็นฝ่ายค้าน | เลือกตั้งครั้งที่ ๓ พ.ค. ๒๗๓๗ ผลคงที่ &mdash; รัฐบาลโรม ๓: ก้าวไกล ๒๖๐ + อุดมการณ์ใหม่ ๓๖ + ธรรมปัญญา ๒๑ = ๓๑๗ เสียง')

# ---- party status lines ----
GOV, OPP, NONE = ('🟢 รัฐบาล', '#4ade80', '74,222,128'), ('🔴 ฝ่ายค้าน', '#f87171', '248,113,113'), ('⚪ ไม่มีที่นั่งในสภา', '#cbd5e1', '203,213,225')
STATUS = {
    'ก้าวไกล': (GOV, 'แกนนำรัฐบาล · ส.ส. ๒๖๐ คน · นายกรัฐมนตรี รังสิมันต์ โรม'),
    'อุดมการณ์ใหม่': (GOV, 'พรรคร่วมรัฐบาล · ส.ส. ๓๖ คน'),
    'ธรรมปัญญา': (GOV, 'พรรคร่วมรัฐบาล · ส.ส. ๒๑ คน · ไม่ฉีก MOU'),
    'ทักษิประชา': (OPP, 'ส.ส. ๕๐ คน · ฉีก MOU ปลายปี ๒๗๓๖ · ถูกแบนโควตาวิปฝ่ายค้าน ๖ เดือน'),
    'ไทยรักไทย': (OPP, 'ส.ส. ๔๖ คน · ออกจากรัฐบาลตามทักษิประชา'),
    'ไทยรักษาชาติ': (OPP, 'ส.ส. ๒๔ คน · แกนนำฝ่ายค้าน (ร.ท. ปรีชาพล พงษ์พานิช)'),
    'ชาติพัฒนา': (OPP, 'ส.ส. ๒๓ คน'),
    'ชาติไทย': (OPP, 'ส.ส. ๒๑ คน'),
    'กิจสังคม': (OPP, 'ส.ส. ๑๙ คน'),
    'เสรีรวมไทย': (NONE, 'เสียที่นั่งทั้งหมดในการเลือกตั้งซ่อม ๓๑ ธ.ค. ๒๗๓๒'),
    'ประชาธิปัตย์': (NONE, 'เสียที่นั่งทั้งหมดในการเลือกตั้งซ่อม ๓๑ ธ.ค. ๒๗๓๒'),
    'รวมไทยสร้างชาติ': (NONE, 'เสียที่นั่งทั้งหมดในการเลือกตั้งซ่อม ๓๑ ธ.ค. ๒๗๓๒'),
    'ความหวังใหม่': (NONE, 'เสียที่นั่งทั้งหมดในการเลือกตั้งซ่อม ๓๑ ธ.ค. ๒๗๓๒'),
    'ภูมิใจไทย': (NONE, ''),
    'หัวใจไทย': (NONE, ''),
}
def status_div(kind, text, site):
    (label, col, rgb) = kind
    detail = f' &middot; {text}' if text else ''
    if site == 'new':
        return (f'<div class="party-status" style="font-size: 12.5px; margin-top: 6px; color: var(--nw-text-2)">สถานะในสภาชุดปัจจุบัน (รัฐบาลโรม ๓): '
                f'<span style="background: rgba({rgb},0.15); color: {col}; border: 1px solid rgba({rgb},0.4); padding: 1px 8px; border-radius: 999px; font-weight: 700">{label}</span>{detail}</div>')
    return (f'<div class="party-status" style="font-size:12.5px; margin-top:6px; color:var(--text-muted);">สถานะในสภาชุดปัจจุบัน (รัฐบาลโรม ๓): '
            f'<span style="background:rgba({rgb},0.15); color:{col}; border:1px solid rgba({rgb},0.4); padding:1px 8px; border-radius:999px; font-weight:700;">{label}</span>{detail}</div>')

def parties(seg, site):
    if 'class="party-status"' in seg:
        return seg
    for name, (kind, text) in STATUS.items():
        mk = f'>พรรค{name}</span>'
        assert seg.count(mk) == 1, (site, name, seg.count(mk))
        i = seg.index(mk); hd = seg.rindex('<div', 0, i); he = tb.div_span(seg, hd)
        seg = seg[:he] + status_div(kind, text, site) + seg[he:]
    return seg

# ---- apply ----
for f in ROME_FILES:
    s = rd(f); n = s.count('รังสิมันต์ ๒')
    s = s.replace('รังสิมันต์ ๒', 'รังสิมันต์ ๓'); wr(f, s); print('rename', f, n)

s = rd('src/tabs/parties-tab.html')
if DEM[0] in s: s = one(s, *DEM, 'dem new')
s = parties(s, 'new'); wr('src/tabs/parties-tab.html', s); print('parties new')
s = rd('src/tabs/orange-party-tab.html'); s = orange(s, 'new'); wr('src/tabs/orange-party-tab.html', s); print('orange new')
s = rd('src/tabs/pms-tab.html')
if 'รัฐบาลโรม ๓:' not in s: s = one(s, ROW_OLD, ROW_NEW, 'row new')
wr('src/tabs/pms-tab.html', s); print('row new')

s = rd('website_constitution.html')
if DEM[0] in s: s = one(s, *DEM, 'dem old')
p0 = s.index('<div id="parties-tab"'); p1 = tb.div_span(s, p0); s = s[:p0] + parties(s[p0:p1], 'old') + s[p1:]
s = orange(s, 'old')
if 'รัฐบาลโรม ๓:' not in s: s = one(s, ROW_OLD, ROW_NEW, 'row old')
wr('website_constitution.html', s); print('old done')
