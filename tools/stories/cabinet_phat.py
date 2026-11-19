# -*- coding: utf-8 -*-
"""Cabinet tab (2026-11-19, user's ๒๗๔๒–๒๗๕๓ timeline): รัฐบาลภัทร (๒๗๔๔–ปัจจุบัน).

The ๒๗๔๓ line-up in the timeline (โรม นายกฯ+กลาโหม, พิธา รองนายกฯ+พาณิชย์, อะตอม ต่างประเทศ, ศิริกัญญา คลัง,
ปิยบุตร ยุติธรรม, พริษฐ์ ศึกษาธิการ, ธนาธร นวัตกรรมฯ, ๑๘ คน) is the existing set rome3b, which now ends in ๒๗๔๔.
The user said ภัทร's government keeps that line-up. Four posts have no holder in the story: กลาโหม (โรม left
with the premiership), แรงงานฯ (ภัทร became PM), เกษตรฯ (ภาคิน, อุดมการณ์ใหม่) and อุตสาหกรรม (ธนกฤต,
สหายไทยแลนด์) — both parties broke with ก้าวไกล in ๒๗๔๔. They are grey "ยังไม่ระบุ" boxes; no names invented.
ไทยรักษาชาติ holds only deputy-minister posts (names not given). Both sites. Run once from the repo root."""
import io
import re
import sys

sys.path.insert(0, 'tools')
import tab_blocks as tb

JS = ("var w=this.closest('[data-cabs]');w.querySelectorAll('[data-cab]').forEach(function(e){e.hidden=e.getAttribute('data-cab')!=='%s'});"
      "w.querySelectorAll('.cab-btn').forEach(function(b){b.setAttribute('aria-pressed',b===this?'true':'false')},this)")
GREY = '#9ca3af'
OLD = 'website_constitution.html'


def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)


def one(s, a, b, tag=''):
    assert s.count(a) == 1, (tag, a[:80], s.count(a))
    return s.replace(a, b)


def grey(r, label):
    k = r.index(label + '</span>')
    c0 = r.rindex('<div style="background', 0, k)
    c1 = tb.div_span(r, c0)
    card = r[c0:c1]
    photo = re.search(r'<img src="images/cab/[^"]*"[^>]*>|<div role="img"[^>]*>[^<]*</div>', card).group(0)
    st = re.search(r'style="([^"]*)"', photo).group(1)
    st = re.sub(r'border: ?3px solid #[0-9a-f]{6}', 'border: 3px solid ' + GREY, st)
    st = re.sub(r';? ?background: ?#[0-9a-f]{6}.*$', '', st).rstrip('; ')
    box = ('<div role="img" aria-label="ยังไม่ระบุ" style="%s; background: #4b5563; display: flex; align-items: center; '
           'justify-content: center; color: #d1d5db; font-size: 13px">ยังไม่ระบุ</div>') % st
    card = card.replace(photo, box)
    card = re.sub(r'border-top: ?3px solid #[0-9a-f]{6}', 'border-top: 3px solid ' + GREY, card, count=1)
    card = re.sub(r'(<span style="[^"]*color: ?)#[0-9a-f]{6}(;[^"]*font-weight: ?700[^"]*">' + re.escape(label) + ')',
                  r'\g<1>' + GREY + r'\2', card)
    name = re.search(r'(line-height: ?1\.55;?">)(.*?)(</div>)', card, re.S)
    card = card[:name.start(2)] + 'ยังไม่ระบุตัวบุคคล' + card[name.end(2):]
    party = re.search(r'(line-height: ?1\.65;?">)(.*?)(</div>)', card, re.S)
    card = card[:party.start(2)] + 'ไทม์ไลน์ยังไม่ได้ระบุผู้ดำรงตำแหน่งในรัฐบาลภัทร' + card[party.end(2):]
    return r[:c0] + card + r[c1:]


def make_phat(r):
    r = r.replace('<div data-cab="rome3b">', '<div data-cab="phat1">', 1)
    r = one(r, 'คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ ชุดที่ ๒ &mdash; ก้าวไกล&ndash;อุดมการณ์ใหม่&ndash;ธรรมปัญญา&ndash;สหายไทยแลนด์',
            'คณะรัฐมนตรีรัฐบาลภัทร &mdash; ก้าวไกล (ไทยรักษาชาติรับตำแหน่งรัฐมนตรีช่วยและผู้ช่วย)', 'title')
    g = r.index('<div style="display: grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr))')
    r = r[:g] + ('<div class="nwc-note" style="margin: 14px 0"><p>คณะรัฐมนตรีชุดนี้ยกมาจาก ครม. ปี ๒๗๔๓ ทั้งชุด เปลี่ยนเพียงนายกรัฐมนตรี '
                 '&mdash; อุดมการณ์ใหม่และสหายไทยแลนด์ไม่ได้ร่วมรัฐบาลแล้ว ส่วนไทยรักษาชาติไม่ขอตำแหน่งรัฐมนตรีว่าการ '
                 'ขอเพียงรัฐมนตรีช่วยและผู้ช่วยที่มีอำนาจเท่ากัน &middot; ตำแหน่งสีเทายังไม่ระบุตัวบุคคล</p></div>') + r[tb.div_span(r, g):]
    r = one(r, 'src="images/pm35.jpg" alt="รังสิมันต์ โรม"', 'src="images/pm36.jpg" alt="ธีรภัทร วัฒนากร"', 'pm img')
    pm = r.index('src="images/pm36.jpg"')
    pc0 = r.rindex('<div style="background', 0, pm)
    pc1 = tb.div_span(r, pc0)
    card = r[pc0:pc1]
    card = one(card, 'รังสิมันต์ โรม (โรม)', 'ธีรภัทร วัฒนากร (ภัทร)', 'pm name')
    txt = re.search(r'(line-height: ?1\.75;?">)(นายกรัฐมนตรีคนที่ ๓๕.*?)(</div>)', card, re.S)
    card = card[:txt.start(2)] + ('นายกรัฐมนตรีคนที่ ๓๖ &mdash; ชุดแรกหลังเลือกตั้ง ๑๒ พ.ค. ๒๗๔๔ รัฐบาล ๓๕๑ / ๕๐๐ เสียง '
                                  '(ก้าวไกล ๒๖๕ &middot; ไทยรักษาชาติ ๘๖) &middot; หลังเลือกตั้งกลางเทอม ๑๓ ต.ค. ๒๗๔๘ '
                                  'รัฐบาล ๓๘๕ / ๕๐๐ เสียง (ก้าวไกล ๒๘๗ &middot; ไทยรักษาชาติ ๙๘)') + card[txt.end(2):]
    r = r[:pc0] + card + r[pc1:]
    for label in ('๒. กระทรวงกลาโหม', '๖. กระทรวงเกษตรและสหกรณ์', '๑๔. กระทรวงแรงงานและสวัสดิการสังคม', '๑๘. กระทรวงอุตสาหกรรม'):
        r = grey(r, label)
    for gone in ('รังสิมันต์', 'ภาคิน', 'ธนกฤต', 'สหายไทยแลนด์ ๑'):
        assert gone not in r, gone
    return r


HEAD_OLD = ('รัฐบาลปัจจุบัน รังสิมันต์ โรม นายกรัฐมนตรีคนที่ ๓๕ &middot; พรรคก้าวไกล &middot; พ.ศ. ๒๗๓๑ &ndash; ปัจจุบัน')
HEAD_NEW = ('รัฐบาลปัจจุบัน ธีรภัทร วัฒนากร (ภัทร) นายกรัฐมนตรีคนที่ ๓๖ &middot; พรรคก้าวไกล &middot; พ.ศ. ๒๗๔๔ &ndash; ปัจจุบัน')
NOTE_NEW = ('🆕 <strong>รัฐบาลชุดปัจจุบัน</strong> คือรัฐบาลภัทร &mdash; หลังเลือกตั้ง ๑๒ พ.ค. ๒๗๔๔ ก้าวไกลได้ ๒๖๕ ที่นั่ง '
            'และไทยรักษาชาติฉีก MOU มาร่วมรัฐบาล (๓๕๑ เสียง) หลังเลือกตั้งกลางเทอม ๑๓ ต.ค. ๒๗๔๘ เพิ่มเป็น ๓๘๕ เสียง '
            '(ก้าวไกล ๒๘๗ · ไทยรักษาชาติ ๙๘) นำโดย <strong>ธีรภัทร วัฒนากร</strong> นายกรัฐมนตรีคนที่ ๓๖ &mdash; '
            'รัฐบาลรังสิมันต์ ๑&ndash;๓ (๒๗๓๑&ndash;๒๗๔๔) และรัฐบาลก่อนหน้ายังเก็บไว้ครบ &mdash; เลือกดูคณะรัฐมนตรีแต่ละรัฐบาลได้จากปุ่มด้านล่าง')


def tab(t):
    t = one(t, HEAD_OLD, HEAD_NEW, 'head')
    n0 = t.index('🆕 <strong')
    strong = t[n0 + 2:t.index('>', n0) + 1]                 # keeps the old site's coloured <strong ...>
    t = t[:n0] + NOTE_NEW.replace('<strong>รัฐบาลชุดปัจจุบัน', strong + 'รัฐบาลชุดปัจจุบัน', 1) + t[t.index('</', t.index('ยังเก็บไว้ครบ', n0)):]
    s0 = re.search(r'<div data-cab="rome3b">', t).start()
    s1 = tb.div_span(t, s0)
    rome = t[s0:s1]
    phat = make_phat(rome)
    rome = rome.replace('<div data-cab="rome3b">', '<div data-cab="rome3b" hidden>', 1)
    t = t[:s0] + phat + rome + t[s1:]
    t = one(t, '<button type="button" class="cab-btn" aria-pressed="true" onclick="%s">🟠 รัฐบาลรังสิมันต์ ๓ ชุดที่ ๒ · ๒๗๓๙&ndash;ปัจจุบัน</button>' % (JS % 'rome3b'),
            ('<button type="button" class="cab-btn" aria-pressed="true" onclick="%s">🟠 รัฐบาลภัทร · ๒๗๔๔&ndash;ปัจจุบัน</button>' % (JS % 'phat1')) +
            ('<button type="button" class="cab-btn" aria-pressed="false" onclick="%s">🟠 รัฐบาลรังสิมันต์ ๓ ชุดที่ ๒ · ๒๗๓๙&ndash;๒๗๔๔</button>' % (JS % 'rome3b')), 'buttons')
    return t


f = 'src/tabs/cabinet-tab.html'
wr(f, tab(rd(f)))
s = rd(OLD)
p0 = s.index('<div id="cabinet-tab"')
p1 = tb.div_span(s, p0)
wr(OLD, s[:p0] + tab(s[p0:p1]) + s[p1:])
print('cabinet: รัฐบาลภัทร added')
