# -*- coding: utf-8 -*-
"""Cabinet tab (2026-11-19, user): the full line-up of รัฐบาลภัทร, from the ๒๗๔๔ MOP and later canon.

Rebuilds the phat1 set from rome3b (the ๒๗๔๓ cabinet) so nothing from the grey placeholder version stays:
  ภัทร  นายกรัฐมนตรี ควบ กลาโหม และ แรงงานและสวัสดิการสังคม
  ศักดินัย นุ่มหนู  เกษตรและสหกรณ์ (แทนภาคิน) — no photo yet: "รอรูป" box
  ธนาธร  อุตสาหกรรม ควบ นวัตกรรมและเทคโนโลยี และ ทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์
  everyone else as in ๒๗๔๓; พิธา is ฯพณฯ (cabinet resolution ๓๐ ธ.ค. ๒๗๕๐).
๑๖ people, all ก้าวไกล; ไทยรักษาชาติ holds deputy posts in every ministry (names not given).
Both sites. Run from the repo root (replaces whatever phat1 set is there)."""
import io
import re
import sys

sys.path.insert(0, 'tools')
import tab_blocks as tb

OLD = 'website_constitution.html'
ORANGE = '#fb923c'


def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)


def one(s, a, b, tag=''):
    assert s.count(a) == 1, (tag, a[:80], s.count(a))
    return s.replace(a, b)


def card_at(r, label):
    k = r.index(label + '</span>')
    c0 = r.rindex('<div style="background', 0, k)
    return c0, tb.div_span(r, c0)


def name_block(card):
    m = re.search(r'(line-height: ?1\.55;?">)(.*?)(</div>)', card, re.S)
    return m.start(2), m.end(2)


def set_name(card, html):
    a, b = name_block(card)
    return card[:a] + html + card[b:]


def set_party(card, text):
    m = re.search(r'(line-height: ?1\.65;?">)(.*?)(</div>)', card, re.S)
    return card[:m.start(2)] + text + card[m.end(2):]


def relabel(card, old_no_label, new_no_label, old_icon, new_icon):
    card = one(card, old_no_label + '</span>', new_no_label + '</span>', 'label')
    card = one(card, 'src="images/ministry_%d.png" alt="%s"' % old_icon, 'src="images/ministry_%d.png" alt="%s"' % new_icon, 'icon')
    return card


def make(r, badge_style):
    def badge(text):
        return '<span style="%s">%s</span>' % (badge_style, text)

    r = r.replace('<div data-cab="rome3b" hidden>', '<div data-cab="phat1">', 1)
    r = one(r, 'คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ ชุดที่ ๒ &mdash; ก้าวไกล&ndash;อุดมการณ์ใหม่&ndash;ธรรมปัญญา&ndash;สหายไทยแลนด์',
            'คณะรัฐมนตรีรัฐบาลภัทร &mdash; ก้าวไกล (ไทยรักษาชาติรับตำแหน่งรัฐมนตรีช่วยและผู้ช่วยในทุกกระทรวง)', 'title')
    r = one(r, '>๑๘ / ๓๖</div>', '>๑๖ / ๓๖</div>', 'people')
    r = one(r, '>ก้าวไกล ๑๙ · อุดมการณ์ใหม่ ๑ · สหายไทยแลนด์ ๑</div>', '>ก้าวไกล ๒๑</div>', 'parties')
    g = r.index('<div style="display: grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr))')
    g1 = tb.div_span(r, g)
    r = r[:g1] + ('<div class="nwc-note" style="margin: 14px 0"><p>ตามเอกสาร MOP ปี ๒๗๔๔ &mdash; ไทยรักษาชาติไม่ขอเก้าอี้รัฐมนตรีว่าการ '
                  'แต่ได้ตำแหน่งรัฐมนตรีช่วยและผู้ช่วยที่มีอำนาจเท่ากันในทุกกระทรวง (ยังไม่ได้ระบุรายชื่อ)</p></div>') + r[g1:]
    # prime minister
    r = one(r, 'src="images/pm35.jpg" alt="รังสิมันต์ โรม"', 'src="images/pm36.jpg" alt="ธีรภัทร วัฒนากร"', 'pm img')
    pm = r.index('src="images/pm36.jpg"')
    p0 = r.rindex('<div style="background', 0, pm)
    p1 = tb.div_span(r, p0)
    pc = one(r[p0:p1], 'รังสิมันต์ โรม (โรม)', 'ธีรภัทร วัฒนากร (ภัทร)', 'pm name')
    m = re.search(r'(line-height: ?1\.75;?">)(นายกรัฐมนตรีคนที่ ๓๕.*?)(</div>)', pc, re.S)
    pc = pc[:m.start(2)] + ('นายกรัฐมนตรีคนที่ ๓๖ ควบรัฐมนตรีว่าการกระทรวงกลาโหม และกระทรวงแรงงานและสวัสดิการสังคม &mdash; '
                            'รัฐบาลผสมก้าวไกล + ไทยรักษาชาติ ๓๕๑ / ๕๐๐ เสียง (๗๐.๒%) หลังเลือกตั้ง ๒๗๔๔ &middot; '
                            'หลังเลือกตั้งกลางเทอม ๒๗๔๘ รวม ๓๘๕ เสียง (ก้าวไกล ๒๘๗ &middot; ไทยรักษาชาติ ๙๘)') + pc[m.end(2):]
    r = r[:p0] + pc + r[p1:]
    # ภัทร: his labour card gets the badge, and a copy of it becomes the defence card
    l0, l1 = card_at(r, '๑๔. กระทรวงแรงงานและสวัสดิการสังคม')
    labour = r[l0:l1]
    assert 'ธีรภัทร' in labour
    name_html = 'ธีรภัทร วัฒนากร (ภัทร)'
    labour = set_name(labour, name_html + badge('ควบ นายกรัฐมนตรี &middot; กลาโหม'))
    r = r[:l0] + labour + r[l1:]
    d0, d1 = card_at(r, '๒. กระทรวงกลาโหม')
    defence = relabel(labour, '๑๔. กระทรวงแรงงานและสวัสดิการสังคม', '๒. กระทรวงกลาโหม',
                      (14, 'กระทรวงแรงงานและสวัสดิการสังคม'), (2, 'กระทรวงกลาโหม'))
    defence = set_name(defence, name_html + badge('ควบ นายกรัฐมนตรี &middot; แรงงานและสวัสดิการสังคม'))
    r = r[:d0] + defence + r[d1:]
    # ศักดินัย นุ่มหนู replaces ภาคิน at agriculture
    a0, a1 = card_at(r, '๖. กระทรวงเกษตรและสหกรณ์')
    ag = r[a0:a1]
    photo = re.search(r'<img src="images/cab/[^"]*"[^>]*>', ag).group(0)
    st = re.search(r'style="([^"]*)"', photo).group(1).replace('#ef4444', ORANGE)
    ag = ag.replace(photo, '<div data-photo-pending="ศักดินัย นุ่มหนู" style="%s; background: #1f2937; display: flex; '
                           'align-items: center; justify-content: center; color: #9ca3af; font-size: 13px">👤 รอรูป</div>' % st.rstrip('; '))
    ag = ag.replace('#ef4444', ORANGE)
    ag = set_name(ag, 'ศักดินัย นุ่มหนู')
    ag = set_party(ag, 'พรรคก้าวไกล &middot; แทนภาคิน เมธาปรีชากุล')
    r = r[:a0] + ag + r[a1:]
    # ธนาธร: industry joins his two ministries
    i0, i1 = card_at(r, '๑๙. กระทรวงนวัตกรรมและเทคโนโลยี')
    inno = r[i0:i1]
    inno2 = one(inno, '>ควบ ทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์</span>', '>ควบ อุตสาหกรรม &middot; ทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์</span>', 'inno badge')
    r = r[:i0] + inno2 + r[i1:]
    ip0, ip1 = card_at(r, '๒๐. กระทรวงทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์')
    ip = one(r[ip0:ip1], '>ควบ นวัตกรรมและเทคโนโลยี</span>', '>ควบ อุตสาหกรรม &middot; นวัตกรรมและเทคโนโลยี</span>', 'ip badge')
    r = r[:ip0] + ip + r[ip1:]
    n0, n1 = card_at(r, '๑๘. กระทรวงอุตสาหกรรม')
    ind = relabel(inno, '๑๙. กระทรวงนวัตกรรมและเทคโนโลยี', '๑๘. กระทรวงอุตสาหกรรม',
                  (19, 'กระทรวงนวัตกรรมและเทคโนโลยี'), (18, 'กระทรวงอุตสาหกรรม'))
    ind = one(ind, '>ควบ ทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์</span>', '>ควบ นวัตกรรมและเทคโนโลยี &middot; ทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์</span>', 'ind badge')
    r = r[:n0] + ind + r[n1:]
    # พิธา: ฯพณฯ
    r = r.replace('>พิธา ลิ้มเจริญรัตน์ (ทิม)<', '>ฯพณฯ พิธา ลิ้มเจริญรัตน์ (ทิม)<')
    for gone in ('รังสิมันต์', 'ภาคิน (', 'ดร. ภาคิน', 'ธนกฤต', 'ยังไม่ระบุ', 'สหายไทยแลนด์ ๑', 'อุดมการณ์ใหม่</'):
        assert gone not in r, gone
    return r


def tab(t):
    s0 = re.search(r'<div data-cab="rome3b" hidden>', t).start()
    rome = t[s0:tb.div_span(t, s0)]
    badge_style = re.search(r'<span style="([^"]*background: #bfdbfe[^"]*)">ควบ', rome).group(1)
    p0 = re.search(r'<div data-cab="phat1">', t).start()
    p1 = tb.div_span(t, p0)
    t = t[:p0] + make(rome, badge_style) + t[p1:]
    note_old = re.search(r'ตำแหน่งสีเทายังไม่ระบุตัวบุคคล', t)
    assert note_old is None
    return t


f = 'src/tabs/cabinet-tab.html'
wr(f, tab(rd(f)))
s = rd(OLD)
p0 = s.index('<div id="cabinet-tab"')
p1 = tb.div_span(s, p0)
wr(OLD, s[:p0] + tab(s[p0:p1]) + s[p1:])
print('รัฐบาลภัทร: full line-up')
