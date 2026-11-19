# -*- coding: utf-8 -*-
"""PM 36: ธีรภัทร วัฒนากร (ภัทร), ก้าวไกล, ๑๒ พ.ค. ๒๗๔๔ – ปัจจุบัน (user's ๒๗๔๒–๒๗๕๓ timeline, 2026-11-19).

Seats only, as the user chose: ๒๗๔๔ ก้าวไกล ๒๖๕ (+ ไทยรักษาชาติ ๘๖ = ๓๕๑, ๗๐.๒%);
๒๗๔๘ mid-term ก้าวไกล ๒๘๗ (+ ไทยรักษาชาติ ๙๘ = ๓๘๕). No vote totals or district/list split invented.
Also: Rome's term ends ๒๗๔๔; พิธา (PM 17) gets (ฯพณฯ) like อะตอม, approved by the cabinet ๓๐ ธ.ค. ๒๗๕๐.
Both sites. Run once from the repo root."""
import io
import re
import sys

sys.path.insert(0, 'tools')
import tab_blocks as tb


def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)


def one(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:70], s.count(a))
    return s.replace(a, b)


OLD = 'website_constitution.html'


def panel(s, tid):
    p0 = s.index('<div id="%s"' % tid)
    return p0, tb.div_span(s, p0)


def in_tab(path, tid, fn):
    """Apply fn to the tab's text: the src/tabs file for the new site, the panel for the old site."""
    if path == OLD:
        s = rd(OLD)
        p0, p1 = panel(s, tid)
        wr(OLD, s[:p0] + fn(s[p0:p1]) + s[p1:])
    else:
        wr(path, fn(rd(path)))


def both(tid, fn):
    in_tab('src/tabs/%s.html' % tid, tid, fn)
    in_tab(OLD, tid, fn)


# ---------- roster row ----------
DESC = ('นายกรัฐมนตรีคนที่ ๓๖ (ธีรภัทร วัฒนากร / พรรคก้าวไกล) (พ.ศ. ๒๗๔๔-ปัจจุบัน) | '
        'ส.ส. ผู้ยืนหยัดจากนครสวรรค์ เขต ๒ ผู้ย้ายจากเสรีรวมไทยมาก้าวไกล | '
        'เลือกตั้ง ๑๒ พ.ค. ๒๗๔๔ ก้าวไกลได้ ๒๖๕/๕๐๐ ที่นั่ง &mdash; ทุกพรรคที่เหลือลงนาม MOU ร่วม ๒๓๕ ที่นั่ง ส่งภาคิน (ภู) ชิงนายกฯ '
        'แต่ก้าวไกลออก MOP &ldquo;คำมั่นสัญญาแห่งสีส้ม&rdquo; ไม่ถอย | ไทยรักษาชาติฉีก MOU มาร่วมรัฐบาล ๓๕๑/๕๐๐ (๗๐.๒%) '
        'ไม่ขอตำแหน่งรัฐมนตรี ขอเพียงรัฐมนตรีช่วย | เลือกตั้งกลางเทอมครั้งแรก ๑๓ ต.ค. ๒๗๔๘ ก้าวไกล ๒๘๗ + ไทยรักษาชาติ ๙๘ = ๓๘๕ เสียง | '
        'ธ.ค. ๒๗๕๐ นำรัฐบาลต้าน &ldquo;กบฏจอมพลรวบอำนาจ&rdquo; ถอยไปตั้งหลักที่นครปฐม แล้วลงนามประกาศ ๓ ฉบับคืนอำนาจ | '
        'รัฐบาลที่ยุบพรรคสหายไทยแลนด์ (๒๗๕๑) และ ๖ พรรคตามกฎหมายความโปร่งใสพรรค (๒๗๕๒) ผ่านกระบวนการศาลทั้งหมด')
ROME_ADD = (' | ๒๗๔๒ ผลักดันรัฐธรรมนูญแก้ไขเพิ่มเติมให้มีเลือกตั้งกลางวาระ | ๒๗๔๓ ครม. ก้าวไกล ๑๘ ตำแหน่ง | '
            'ส่งไม้ต่อให้ธีรภัทร (ภัทร) หลังเลือกตั้ง ๒๗๔๔')


def roster(t):
    rows = list(re.finditer(r'<tr class="pm-row".*?</tr>', t, re.S))
    rome = rows[-1].group(0)
    assert 'images/pm35.jpg' in rome
    new_rome = rome.replace('๒๗๓๑-ปัจจุบัน', '๒๗๓๑-๒๗๔๔')
    last_td = new_rome.rindex('</td>')
    new_rome = new_rome[:last_td] + ROME_ADD + new_rome[last_td:]
    row = rome
    row = re.sub(r'>\s*๓๕\s*</td>', '>๓๖</td>', row, count=1)
    row = row.replace('images/pm35.jpg', 'images/pm36.jpg').replace('alt="รังสิมันต์ โรม"', 'alt="ธีรภัทร วัฒนากร"')
    row = row.replace('<strong>รังสิมันต์ โรม</strong>', '<strong>ธีรภัทร วัฒนากร (ภัทร)</strong>')
    row = row.replace('Rangsiman Rome', 'Teerapat Wattanakorn')
    row = row.replace('๒๗๓๑-ปัจจุบัน', '๒๗๔๔-ปัจจุบัน')
    a = row.rindex('<td')
    a = row.index('>', a) + 1
    b = row.rindex('</td>')
    row = row[:a] + DESC + row[b:]
    assert 'รังสิมันต์' not in row and 'ธีรภัทร' in row, 'clone left Rome behind'
    t = t[:rows[-1].start()] + new_rome + '\n\n' + row + t[rows[-1].end():]
    t = one(t, 'ทำเนียบนายกรัฐมนตรีทั้ง ๓๕ คน', 'ทำเนียบนายกรัฐมนตรีทั้ง ๓๖ คน', 'roster count')
    # พิธา (PM 17): ฯพณฯ from ๓๐ ธ.ค. ๒๗๕๐
    t = one(t, '<strong>พิธา ลิ้มเจริญรัตน์</strong>', '<strong>พิธา ลิ้มเจริญรัตน์ (ฯพณฯ)</strong>', 'pita roster')
    return t


both('pms-tab', roster)
both('portrait-hall-tab', lambda t: one(t, 'ทั้ง ๓๕ คน &mdash;', 'ทั้ง ๓๖ คน &mdash;', 'hall count'))

# ---------- hall data ----------
h = rd('js/hall-data.js')
h = one(h, "['รังสิมันต์ โรม', '๒๗๓๑ – ปัจจุบัน']", "['รังสิมันต์ โรม', '๒๗๓๑ – ๒๗๔๔'],\n    ['ธีรภัทร วัฒนากร', '๒๗๔๔ – ปัจจุบัน']", 'hall')
h = one(h, "['พิธา ลิ้มเจริญรัตน์', ", "['พิธา ลิ้มเจริญรัตน์ (ฯพณฯ)', ", 'hall pita')
wr('js/hall-data.js', h)
for f in ('index.html', OLD, 'tools/site_template.html'):
    wr(f, one(rd(f), 'hall-data.js?v=2731', 'hall-data.js?v=2753', f))

# ---------- present-tense mentions of Rome ----------
both('parties-tab', lambda t: one(
    t.replace('รังสิมันต์ โรม นายกฯ คนที่ ๓๕ (พ.ศ. ๒๗๓๑-ปัจจุบัน)', 'รังสิมันต์ โรม นายกฯ คนที่ ๓๕ (พ.ศ. ๒๗๓๑-๒๗๔๔) และธีรภัทร (ภัทร) นายกฯ คนที่ ๓๖ (พ.ศ. ๒๗๔๔-ปัจจุบัน)'),
    'นายกรัฐมนตรีคนปัจจุบัน: รังสิมันต์ โรม (นายกฯ คนที่ ๓๕ · พรรคก้าวไกล)',
    'นายกรัฐมนตรีคนปัจจุบัน: ธีรภัทร วัฒนากร (นายกฯ คนที่ ๓๖ · พรรคก้าวไกล)', 'parties current'))
both('election-2731-tab', lambda t: one(t, 'นายกรัฐมนตรีคนที่ ๓๕ แห่งราชอาณาจักรไทย (พ.ศ. ๒๗๓๑&ndash;ปัจจุบัน)',
                                        'นายกรัฐมนตรีคนที่ ๓๕ แห่งราชอาณาจักรไทย (พ.ศ. ๒๗๓๑&ndash;๒๗๔๔)', 'e2731'))


# ---------- ก้าวไกล party tab: Rome's card becomes a former PM, ภัทร's card follows ----------
def pm_card(t):
    i = t.index('🟢 นายกรัฐมนตรีคนปัจจุบัน')
    a = None
    for m in reversed(list(re.finditer(r'<div\b', t[:i]))):
        e = tb.div_span(t, m.start())
        if e > i and 'images/pm35.jpg' in t[m.start():e]:
            a = m.start()
            break
    return a, e


def bullets(c):
    """(first bullet, position of the bullet list's closing tag) in a PM card."""
    k = c.index('นายกรัฐมนตรีคนที่ ๓')
    first = c.index('<div>• ', k)
    box = c.rindex('<div', 0, first)
    end = tb.div_span(c, box)
    return first, c.rindex('</div>', 0, end)


def phat_card(rome):
    c = rome.replace('images/pm35.jpg', 'images/pm36.jpg').replace('alt="รังสิมันต์ โรม"', 'alt="ธีรภัทร วัฒนากร"')
    # election stats: keep the box and one term entry as the pattern, show seats only
    j = c.index('สถิติผลเลือกตั้ง')
    t0 = c.rindex('<div', 0, j)
    box = t0 if '<h5>' in c[t0:j] else c.rindex('<div', 0, t0)   # old site: the title is its own div inside the box
    box_end = tb.div_span(c, box)
    head_end = c.index('<!-- Term 1 -->', box)
    t1 = c.index('<!-- Term 1 -->', box) + len('<!-- Term 1 -->')
    entry = c[c.index('<div', t1):tb.div_span(c, c.index('<div', t1))]
    entry_open = entry[:entry.index('>') + 1]
    title = re.search(r'<h5>[^<]*</h5>|<div[^>]*>[^<]*รัฐบาลชุดที่ ๑[^<]*</div>', entry).group(0)
    big = re.search(r'<div style="[^"]*font-size: ?24px[^"]*">[\d,]+</div>', entry).group(0)
    row_i = entry.index('ส.ส. ในสภา')
    row = entry[entry.rindex('<div', 0, row_i):tb.div_span(entry, entry.rindex('<div', 0, row_i))]

    def term(n, year, seats, gov):
        pct = '%.1f%%' % (seats / 5)
        r = re.sub(r'ส\.ส\. ในสภา \(\d+/500\):', 'ส.ส. ในสภา (%d/500):' % seats, row)
        r = re.sub(r'>\d+\.\d%<', '>%s<' % pct, r)
        tt = re.sub(r'รัฐบาลชุดที่ ๑ \(พ\.ศ\. ๒๗๓๑\)', 'รัฐบาลชุดที่ %s (พ.ศ. %s)' % (n, year), title)
        bb = re.sub(r'>[\d,]+<', '>%d ที่นั่ง<' % seats, big)
        return entry_open + tt + bb + r + '<div style="font-size: 11px; opacity: .8; margin-top: 6px; line-height: 1.5">%s</div></div>' % gov

    head = c[box:head_end].replace('สถิติผลเลือกตั้ง ๓ ครั้ง', 'สถิติผลเลือกตั้ง ๒ ครั้ง (ที่นั่ง)')
    terms = (term('๑', '๒๗๔๔', 265, 'รัฐบาลรวม ๓๕๑/๕๐๐ (๗๐.๒%) กับไทยรักษาชาติ ๘๖') +
             term('๒', '๒๗๔๘ · กลางเทอม', 287, 'รัฐบาลรวม ๓๘๕/๕๐๐ กับไทยรักษาชาติ ๙๘'))
    foot = re.search(r'<div style="[^"]*">จัดตั้งรัฐบาลสถาปนานายกฯ คนที่ ๓๕ \(รังสิมันต์ โรม\)</div>', c).group(0)
    foot = foot.replace('คนที่ ๓๕ (รังสิมันต์ โรม)', 'คนที่ ๓๖ (ธีรภัทร วัฒนากร)')
    c = c[:box] + head + terms + foot + '</div>' + c[box_end:]
    # right column
    c = c.replace('นายกรัฐมนตรีคนที่ ๓๕: รังสิมันต์ โรม', 'นายกรัฐมนตรีคนที่ ๓๖: ธีรภัทร วัฒนากร (ภัทร)')
    c = c.replace('พ.ศ. ๒๗๓๑ – ปัจจุบัน', 'พ.ศ. ๒๗๔๔ – ปัจจุบัน')
    lst, close = bullets(c)
    items = [
        '🗳️ เลือกตั้ง ๑๒ พ.ค. ๒๗๔๔:</strong> ก้าวไกลได้ ๒๖๕ ที่นั่ง ไทยรักษาชาติ ๘๖ อุดมการณ์ใหม่ ๘๑ ประชาธิปัตย์ ๒๔ กิจสังคม ๒๐ ชาติไทย ๑๘ '
        'สหายไทยแลนด์ ๕ ทักษิประชา ๑ ไทยรักไทย ๐ &mdash; ทุกพรรคที่เหลือลงนาม MOU ร่วม ๒๓๕ ที่นั่ง ส่งภาคิน (ภู) เป็นแคนดิเดตฝั่ง MOU',
        '🧡 MOP &ldquo;คำมั่นสัญญาแห่งสีส้ม&rdquo;:</strong> ทุกคนคิดว่าก้าวไกลจะถอย แต่ไม่ถอย &mdash; ประกาศ ครม. พรรคเดียว ๒๖๕/๕๐๐ '
        'จนไทยรักษาชาติฉีก MOU เพราะอุดมการณ์ใหม่และสหายไทยแลนด์ตะบัตสัตย์ต่อก้าวไกล แล้วมาร่วมรัฐบาล รวม ๓๕๑/๕๐๐ (๗๐.๒%)',
        '🤝 ไทยรักษาชาติ:</strong> ไม่ขอตำแหน่งรัฐมนตรี ขอเพียงรัฐมนตรีช่วยและผู้ช่วยที่มีอำนาจเท่ากัน ทำงานเข้ากันดี คะแนนนิยมรัฐบาลพุ่ง',
        '🎵 สโลแกนและเพลง:</strong> &ldquo;อนุรักษ์ความดี คงซึ่งการเมืองดี และปากท้องดี เพื่อมีอนาคต&rdquo; &mdash; เปลี่ยนจาก &ldquo;สร้าง&rdquo; เป็น &ldquo;รักษา&rdquo; '
        '&middot; เพลงใหม่ของพรรค &ldquo;ทุ่งฝันวันใหม่&rdquo; ฮิตที่สุด',
        '🙏 ๑๔ มี.ค. ๒๗๔๕:</strong> ประชาชนชุมนุมใหญ่ที่ก้าวไกลเพื่อขอบคุณรัฐบาลที่ทำผลงานดีตลอดปีแรก &middot; ๑ เม.ย. ๒๗๔๕ ภัทรโพสต์ (ผ่านมติ ครม.) '
        'ว่าคำด่าไม่น่ากลัวเท่าคนที่รักต่อหน้าแต่แทงลับหลัง',
        '🗳️ เลือกตั้งกลางเทอม ๑๓ ต.ค. ๒๗๔๘:</strong> ก้าวไกล ๒๘๗ ไทยรักษาชาติ ๙๘ อุดมการณ์ใหม่ ๕๑ ประชาธิปัตย์ ๒๓ กิจสังคม ๒๐ ชาติไทย ๑๘ '
        'สหายไทยแลนด์ ๒ ทักษิประชา ๑ &mdash; รัฐบาล ๓๘๕ เสียง (สว. สีส้มอีก ๑๔๐+) &middot; นิวตรอนชนะนครปฐม เขต ๑ ด้วยคะแนน ๑๐๐%',
        '🛡️ กบฏจอมพลรวบอำนาจ ธ.ค. ๒๗๕๐:</strong> รัฐบาลถอยไปตั้งหลักที่นครปฐม ไม่ยอมรับการยึดอำนาจ ๑๔ ธ.ค. ภัทรลงนามประกาศ ๓ ฉบับ '
        '(พิธาอ่าน) แล้วทยอยกลับทำเนียบ คืนตำแหน่งทั้งหมดให้จอมพลคงฤทธิ์',
        '⚖️ ๒๗๕๑–๒๗๕๒:</strong> หนังสือของวิชัยที่ขอให้ ครม. ทบทวน ฯพณฯ ยังอยู่ในลิ้นชักของภัทร ไม่ได้ตอบ &middot; '
        'ยุบสหายไทยแลนด์ (๒๗๕๑) และ ๖ พรรคตามกฎหมายความโปร่งใสพรรค (๒๗๕๒) ผ่านศาลทั้งหมด &middot; '
        'ลงนามรับสนองพระบรมราชโองการพระราชทานอภัยโทษ ๒ ธ.ค. ๒๗๕๒',
    ]
    one_item = c[lst:tb.div_span(c, lst)]
    tmpl = re.sub(r'<strong>.*</div>$', '<strong>{}</div>', one_item, flags=re.S)
    c = c[:lst] + '\n'.join(tmpl.format(x) for x in items) + '\n' + c[close:]
    assert 'รังสิมันต์' not in c, 'ภัทร card still mentions Rome'
    return c


def party(t):
    a, e = pm_card(t)
    rome = t[a:e]
    p = phat_card(rome)
    r = rome.replace('🟢 นายกรัฐมนตรีคนปัจจุบัน', '⚪ อดีตนายกรัฐมนตรี').replace('พ.ศ. ๒๗๓๑ – ปัจจุบัน', 'พ.ศ. ๒๗๓๑ – ๒๗๔๔')
    first, close = bullets(r)
    lst_item = r[first:tb.div_span(r, first)]
    add = re.sub(r'<strong>.*</div>$', '<strong>📜 ๒๗๔๒–๒๗๔๔:</strong> ผลักดันรัฐธรรมนูญแก้ไขเพิ่มเติมให้มีเลือกตั้งกลางวาระ '
                 '(ม.๙๙/๔&ndash;๙๙/๗) &middot; ๒๗๔๓ ครม. ก้าวไกล ๑๘ ตำแหน่ง &mdash; แล้วส่งไม้ต่อให้ภัทรหลังเลือกตั้ง ๑๒ พ.ค. ๒๗๔๔</div>',
                 lst_item, flags=re.S)
    r = r[:close] + add + '\n' + r[close:]
    gap = '\n<div style="height: 22px"></div>\n'
    t = t[:a] + r + gap + p + t[e:]
    return t.replace('จดหมายเหตุผลงานนายกรัฐมนตรีทั้ง ๘ ท่าน', 'จดหมายเหตุผลงานนายกรัฐมนตรีทั้ง ๙ ท่าน')


both('orange-party-tab', party)
print('PM 36 added')
