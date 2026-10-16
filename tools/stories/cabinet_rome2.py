# -*- coding: utf-8 -*-
"""Cabinet tab: add "รัฐบาลรังสิมันต์ ๒" (after ทักษิประชา/ไทยรักไทย left and อุดมการณ์ใหม่ joined, 2737)
as the default set; the first Rome cabinet stays as "รังสิมันต์ ๑". Line-up from the user, 2026-10-16:
Atom = deputy PM (economy) + foreign affairs; ภาคิน = agriculture; สุรเชษฐ์ = transport; everything else as
in Rome 1 minus the people whose parties left. Run from the repo root."""
import io, re, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb

MF, NIP = 'ก้าวไกล', 'อุดมการณ์ใหม่'
PCOL = {MF: '#fb923c', NIP: '#ef4444'}
PM = 'รังสิมันต์ โรม (โรม)'
ATOM = 'ฯพณฯ ศาสตราจารย์ ดร. นายแพทย์ วิทยสิทธิ์ ประสิทธิ์ผล (อะตอม)'
PAKIN = 'ดร. ภาคิน เมธาปรีชากุล'
SURACHET = 'สุรเชษฐ์ ประวีณวงศ์วุฒิ'
ROWS = [
    (2, 'กระทรวงกลาโหม', PM, MF),
    (3, 'กระทรวงการคลัง', 'ศิริกัญญา ตันสกุล (ไหม)', MF),
    (4, 'กระทรวงการต่างประเทศ', ATOM, MF),
    (5, 'กระทรวงการท่องเที่ยวและกีฬา', 'พรรณิการ์ วานิช (ช่อ)', MF),
    (6, 'กระทรวงเกษตรและสหกรณ์', PAKIN, NIP),
    (7, 'กระทรวงคมนาคม', SURACHET, MF),
    (8, 'กระทรวงทรัพยากรธรรมชาติและสิ่งแวดล้อม', 'อภิชาติ ศิริสุนทร', MF),
    (9, 'กระทรวงดิจิทัลเพื่อเศรษฐกิจและสังคม', 'ณัฐพงษ์ เรืองปัญญาวุฒิ (เท้ง)', MF),
    (10, 'กระทรวงพลังงาน', 'พิจารณ์ เชาวพัฒนวงศ์', MF),
    (11, 'กระทรวงพาณิชย์', 'พิธา ลิ้มเจริญรัตน์ (ทิม)', MF),
    (12, 'กระทรวงมหาดไทย', 'ชัยธวัช ตุลาธน (ต๋อม)', MF),
    (13, 'กระทรวงยุติธรรม', 'ปิยบุตร แสงกนกกุล', MF),
    (14, 'กระทรวงแรงงานและสวัสดิการสังคม', 'ณัฐวุฒิ บัวประทุม', MF),
    (15, 'กระทรวงวัฒนธรรม', 'พรรณิการ์ วานิช (ช่อ)', MF),
    (16, 'กระทรวงศึกษาธิการ', 'พริษฐ์ วัชรสินธุ (ไอติม)', MF),
    (17, 'กระทรวงสาธารณสุข', 'วาโย อัศวรุ่งเรือง (หมอวาโย)', MF),
    (18, 'กระทรวงอุตสาหกรรม', 'ธนาธร จึงรุ่งเรืองกิจ (เอก)', MF),
    (19, 'กระทรวงนวัตกรรมและเทคโนโลยี', 'ธนาธร จึงรุ่งเรืองกิจ (เอก)', MF),
    (20, 'กระทรวงทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์', 'ธนาธร จึงรุ่งเรืองกิจ (เอก)', MF),
    (21, 'กระทรวงหลักประกันและความเป็นธรรมทางสังคม', 'ณัฐวุฒิ บัวประทุม', MF),
]
DEPUTIES = [('รองนายกรัฐมนตรี', 'พิธา ลิ้มเจริญรัตน์ (ทิม)', MF),
            ('รองนายกรัฐมนตรีฝ่ายเศรษฐกิจ', ATOM, MF)]
FORMER = {'ธนาธร จึงรุ่งเรืองกิจ (เอก)': 'อดีตนายกฯ คนที่ ๑๖', 'พิธา ลิ้มเจริญรัตน์ (ทิม)': 'อดีตนายกฯ คนที่ ๑๗',
          'ศิริกัญญา ตันสกุล (ไหม)': 'อดีตนายกฯ คนที่ ๑๘', 'ณัฐพงษ์ เรืองปัญญาวุฒิ (เท้ง)': 'อดีตนายกฯ คนที่ ๑๙',
          'พริษฐ์ วัชรสินธุ (ไอติม)': 'อดีตนายกฯ คนที่ ๒๐', 'ปิยบุตร แสงกนกกุล': 'อดีตนายกฯ คนที่ ๒๙', ATOM: 'อดีตนายกฯ คนที่ ๓๓'}
EXTRA = {PAKIN: 'หัวหน้าพรรคอุดมการณ์ใหม่'}
PHOTO = {PM: 'rome', 'ศิริกัญญา ตันสกุล (ไหม)': 'sirikanya', ATOM: 'atom', 'พรรณิการ์ วานิช (ช่อ)': 'pannika2', PAKIN: 'pakin',
         SURACHET: 'surachet', 'อภิชาติ ศิริสุนทร': 'apichat', 'ณัฐพงษ์ เรืองปัญญาวุฒิ (เท้ง)': 'nattaphong',
         'พิจารณ์ เชาวพัฒนวงศ์': 'pijarn', 'พิธา ลิ้มเจริญรัตน์ (ทิม)': 'pita', 'ชัยธวัช ตุลาธน (ต๋อม)': 'chaithawat',
         'ปิยบุตร แสงกนกกุล': 'piyabutr', 'ณัฐวุฒิ บัวประทุม': 'nattawut_b2', 'พริษฐ์ วัชรสินธุ (ไอติม)': 'parit',
         'วาโย อัศวรุ่งเรือง (หมอวาโย)': 'wayo2', 'ธนาธร จึงรุ่งเรืองกิจ (เอก)': 'thanathorn'}
TH = '๐๑๒๓๔๕๖๗๘๙'
def th(n): return ''.join(TH[int(c)] if c.isdigit() else c for c in str(n))
def short(m): return m.replace('กระทรวง', '', 1)

posts = {}
for n, m, who, p in ROWS: posts.setdefault(who, []).append(short(m))
for t, who, p in DEPUTIES: posts.setdefault(who, []).append(t)
posts[PM].insert(0, 'นายกรัฐมนตรี')
assert len(posts) == 16 and all(w in PHOTO for w in posts), set(posts) - set(PHOTO)
by_party = {MF: 1, NIP: 0}
for n, m, who, p in ROWS: by_party[p] += 1
assert sum(by_party.values()) == 21

TXT = 'var(--nw-text, var(--text))'; TXT2 = 'var(--nw-text-2, var(--text-muted))'
SURF = 'var(--nw-surface-2, rgba(15,18,25,0.6))'; LINE = 'var(--nw-line, rgba(255,255,255,0.08))'
SERIF = "var(--nw-serif, 'Outfit', sans-serif)"
def badge(t, bg): return (f'<span style="font-size: 10px; font-weight: 800; color: #1a0a0a; background: {bg}; border-radius: 10px; '
                          f'padding: 2px 8px; margin: 0 0 0 6px; vertical-align: middle; white-space: normal; max-width: 100%; display: inline-block">{t}</span>')
def badges(who, this):
    b = badge(FORMER[who], '#fde68a') if who in FORMER else ''
    b += badge(EXTRA[who], '#fecaca') if who in EXTRA else ''
    others = [x for x in posts[who] if x != this]
    return b + (badge('ควบ ' + ' &middot; '.join(others), '#bfdbfe') if others else '')
def face(who, c):
    return (f'<img src="images/cab/{PHOTO[who]}.jpg?v=2" alt="{who}" loading="lazy" style="width: 220px; height: 275px; max-width: 100%; '
            f'border-radius: 8px; border: 3px solid {c}; flex-shrink: 0; object-fit: cover">')
def card(label, who, p, icon):
    c = PCOL[p]
    return (f'<div style="background: {SURF}; border: 1px solid {LINE}; border-top: 3px solid {c}; border-radius: 11px; padding: 16px 15px; display: flex; flex-direction: column; gap: 12px; align-items: center; text-align: center">'
            f'{face(who, c)}<div style="min-width: 0; width: 100%"><div style="display: flex; align-items: center; justify-content: center; gap: 8px">{icon}'
            f'<span style="font-size: 11.5px; color: {c}; font-weight: 700; line-height: 1.4">{label}</span></div>'
            f'<div style="font-size: 14px; color: {TXT}; font-weight: 800; font-family: {SERIF}; margin: 5px 0 5px 0; line-height: 1.55">{who}{badges(who, label.split(". ", 1)[-1].replace("กระทรวง", "", 1))}</div>'
            f'<div style="font-size: 11.8px; color: {TXT2}; line-height: 1.65">พรรค{p}</div></div></div>')
IMG = lambda n, m: f'<img src="images/ministry_{n}.png" alt="{m}" style="width: 30px; height: 30px; object-fit: contain; flex-shrink: 0">'
DEP_ICON = '<span style="font-size: 20px; line-height: 1">🎖️</span>'
HEAD = lambda t: f'<div style="font-family: {SERIF}; font-size: 16px; font-weight: 800; color: #fdba74; margin: 18px 0 10px">{t}</div>'
GRID = lambda items: '<div style="display: grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap: 12px">' + ''.join(items) + '</div>'
STAT = ('<div style="display: grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); gap: 10px; margin: 16px 0">' + ''.join(
    f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; padding: 13px 15px; text-align: center">'
    f'<div style="font-family: {SERIF}; font-size: 21px; font-weight: 800; color: #fdba74">{b}</div>'
    f'<div style="font-size: 11.5px; color: {TXT2}; margin-top: 5px; line-height: 1.55">{t}</div></div>'
    for b, t in [(f'{th(len(posts))} / ๓๖', 'บุคคลในคณะรัฐมนตรี จากเพดาน ๑ + ๓๕ ตามมาตรา ๑๘๘'),
                 ('๒๑ + ๒', 'ส่วนราชการระดับกระทรวง (รวมสำนักนายกรัฐมนตรี) และรองนายกรัฐมนตรี ๒ ตำแหน่ง'),
                 (f'ก้าวไกล {th(by_party[MF])} · อุดมการณ์ใหม่ {th(by_party[NIP])}', 'จำนวนกระทรวงที่แต่ละพรรคดูแล'),
                 (f'{th(len(FORMER))} ท่าน', 'อดีตนายกรัฐมนตรีร่วมคณะ')]) + '</div>')
PMBOX = (f'<div style="background: {SURF}; border: 1px solid rgba(251,146,60,0.4); border-radius: 14px; padding: 18px 20px; margin-bottom: 6px; display: flex; gap: 18px; align-items: center; flex-wrap: wrap">'
         '<img src="images/pm35.jpg" alt="รังสิมันต์ โรม" style="width: 220px; height: 275px; max-width: 100%; object-fit: cover; border-radius: 8px; border: 3px solid #fb923c; flex-shrink: 0">'
         '<div style="flex: 1; min-width: 240px"><div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">'
         '<img src="images/ministry_1.png" alt="สำนักนายกรัฐมนตรี" style="width: 30px; height: 30px; object-fit: contain">'
         '<span style="font-size: 12px; color: #fdba74; font-weight: 700">๑. สำนักนายกรัฐมนตรี &middot; หัวหน้าคณะรัฐมนตรี</span></div>'
         f'<div style="font-family: {SERIF}; font-size: 20px; font-weight: 800; color: {TXT}; margin: 6px 0 4px 0">{PM} <span style="font-size: 13px; color: #fdba74">(พรรคก้าวไกล)</span></div>'
         f'<div style="font-size: 12.5px; color: {TXT2}; line-height: 1.75">นายกรัฐมนตรีคนที่ ๓๕ ควบรัฐมนตรีว่าการกระทรวงกลาโหม &mdash; รัฐบาลผสม ๓ พรรค ๓๑๗ / ๕๐๐ เสียง '
         '(ก้าวไกล ๒๖๐ &middot; อุดมการณ์ใหม่ ๓๖ &middot; ธรรมปัญญา ๒๑)</div></div></div>')
SET = ('<div data-cab="rome2">' + HEAD('คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๒ &mdash; ก้าวไกล&ndash;อุดมการณ์ใหม่&ndash;ธรรมปัญญา') + STAT + PMBOX +
       HEAD('🎖️ รองนายกรัฐมนตรี') + GRID(card(t, w, p, DEP_ICON) for t, w, p in DEPUTIES) +
       HEAD('🏛️ รัฐมนตรีว่าการกระทรวง') + GRID(card(f'{th(n)}. {m}', w, p, IMG(n, m)) for n, m, w, p in ROWS) + '</div>')
assert tb.balanced(SET)

def js(key):
    return ("var w=this.closest('[data-cabs]');"
            "w.querySelectorAll('[data-cab]').forEach(function(e){e.hidden=e.getAttribute('data-cab')!=='" + key + "'});"
            "w.querySelectorAll('.cab-btn').forEach(function(b){b.setAttribute('aria-pressed',b===this?'true':'false')},this)")
BTN_R1_OLD = '🟠 รัฐบาลรังสิมันต์ · ๒๗๓๑&ndash;ปัจจุบัน'
BTN_R1_NEW = '🟠 รัฐบาลรังสิมันต์ ๑ · ๒๗๓๑&ndash;๒๗๓๖'
BTN_R2 = f'<button type="button" class="cab-btn" aria-pressed="true" onclick="{js("rome2")}">🟠 รัฐบาลรังสิมันต์ ๒ · ๒๗๓๗&ndash;ปัจจุบัน</button>'
NOTE_OLD_HEAD = '🆕 <strong>รัฐบาลชุดปัจจุบัน</strong> คือรัฐบาลผสมขั้วส้มแดง ๔ พรรค ๔๑๒ เสียง'
NOTE_NEW = ('🆕 <strong>รัฐบาลชุดปัจจุบัน</strong> คือรัฐบาลรังสิมันต์ ๒ &mdash; รัฐบาลผสม ๓ พรรค ๓๑๗ เสียง (ก้าวไกล ๒๖๐ · อุดมการณ์ใหม่ ๓๖ · ธรรมปัญญา ๒๑) '
            'นำโดย <strong>รังสิมันต์ โรม</strong> นายกรัฐมนตรีคนที่ ๓๕ หลังทักษิประชาฉีก MOU ปลายปี ๒๗๓๖ และพรรคอุดมการณ์ใหม่เข้าร่วมรัฐบาลเมื่อ ก.ย. ๒๗๓๗ '
            '&mdash; รัฐบาลรังสิมันต์ ๑ (ขั้วส้มแดง ๔ พรรค ๔๑๒ เสียง) และรัฐบาลก่อนหน้าของบัญญัติ บรรทัดฐาน (๒๗๓๐&ndash;๒๗๓๑) ยังเก็บไว้ครบ')

for f in ['src/tabs/cabinet-tab.html', 'website_constitution.html']:
    s = io.open(f, encoding='utf-8').read()
    if 'data-cab="rome2"' in s:
        print('skip (done)', f); continue
    a = s.index('<div data-cab="rome"')
    s = s[:a] + SET + s[a:]
    s = s.replace('<div data-cab="rome">', '<div data-cab="rome" hidden>', 1)
    sw0 = s.index('<div class="cab-switch"'); sw1 = tb.div_span(s, sw0); sw = s[sw0:sw1]
    sw = sw.replace('aria-pressed="true"', 'aria-pressed="false"')
    assert sw.count(BTN_R1_OLD) == 1
    sw = sw.replace(BTN_R1_OLD, BTN_R1_NEW)
    first = sw.index('<button')
    sw = sw[:first] + BTN_R2 + sw[first:]
    s = s[:sw0] + sw + s[sw1:]
    # the old site styles the <strong>; anchor on the text after it
    n0 = s.index('รัฐบาลชุดปัจจุบัน</strong> คือรัฐบาลผสมขั้วส้มแดง ๔ พรรค ๔๑๒ เสียง'); n0 = s.index('</strong>', n0) + len('</strong>')
    n1 = s.index('&mdash; เลือกดูคณะรัฐมนตรีแต่ละรัฐบาลได้จากปุ่มด้านล่าง', n0)
    s = s[:n0] + NOTE_NEW.split('</strong>', 1)[1] + ' ' + s[n1:]
    assert s.count('data-cab="rome2"') == 1 and s.count('data-cab="rome" hidden') == 1
    io.open(f, 'w', encoding='utf-8', newline='').write(s)
    print('ok', f)
