# -*- coding: utf-8 -*-
"""Cabinet tab (2026-10-29, user): คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ ชุดที่ ๒ (๒๗๓๙–ปัจจุบัน).
พรรคสหายไทยแลนด์ (๑ ที่นั่ง) joins the government; ธนาธร gives up กระทรวงอุตสาหกรรม to ธนกฤต ใจเพชร
(no photo: a grey box). Everything else is copied from ชุดที่ ๑, which stays as the older set.
Both sites. Run from the repo root."""
import io
import re
import sys

sys.path.insert(0, 'tools')
import tab_blocks as tb

JS = ("var w=this.closest('[data-cabs]');w.querySelectorAll('[data-cab]').forEach(function(e){e.hidden=e.getAttribute('data-cab')!=='%s'});"
      "w.querySelectorAll('.cab-btn').forEach(function(b){b.setAttribute('aria-pressed',b===this?'true':'false')},this)")
OLD_BTN_LABEL = '🟠 รัฐบาลรังสิมันต์ ๓ · ๒๗๓๗&ndash;ปัจจุบัน</button>'
NEW_BTN = ('<button type="button" class="cab-btn" aria-pressed="true" onclick="%s">'
           '🟠 รัฐบาลรังสิมันต์ ๓ ชุดที่ ๒ · ๒๗๓๙&ndash;ปัจจุบัน</button>') % (JS % 'rome3b')
NAME = 'ธนกฤต ใจเพชร'
PARTY = 'พรรคสหายไทยแลนด์'
GREY = '#9ca3af'


def block_span(s, a):
    d = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', s[a:]):
        d += 1 if m.group(0) != '</div>' else -1
        if d == 0:
            return a, a + m.end()


def one(s, old, new):
    assert s.count(old) == 1, (old[:80], s.count(old))
    return s.replace(old, new)


def make_set2(r):
    r = r.replace('<div data-cab="rome2">', '<div data-cab="rome3b">', 1)
    r = one(r, 'คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ &mdash; ก้าวไกล&ndash;อุดมการณ์ใหม่&ndash;ธรรมปัญญา',
            'คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ ชุดที่ ๒ &mdash; ก้าวไกล&ndash;อุดมการณ์ใหม่&ndash;ธรรมปัญญา&ndash;สหายไทยแลนด์')
    r = one(r, '>๑๗ / ๓๖</div>', '>๑๘ / ๓๖</div>')
    r = one(r, '>ก้าวไกล ๒๐ · อุดมการณ์ใหม่ ๑</div>', '>ก้าวไกล ๑๙ · อุดมการณ์ใหม่ ๑ · สหายไทยแลนด์ ๑</div>')
    r = one(r, 'รัฐบาลผสม ๓ พรรค ๓๑๗ / ๕๐๐ เสียง (ก้าวไกล ๒๖๐ &middot; อุดมการณ์ใหม่ ๓๖ &middot; ธรรมปัญญา ๒๑)',
            'รัฐบาลผสม ๔ พรรค ๓๑๘ / ๕๐๐ เสียง (ก้าวไกล ๒๖๐ &middot; อุดมการณ์ใหม่ ๓๖ &middot; ธรรมปัญญา ๒๑ &middot; สหายไทยแลนด์ ๑)')
    # Thanathorn's other two cards no longer say "ควบ อุตสาหกรรม"
    r = one(r, '>ควบ อุตสาหกรรม &middot; ทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์</span>', '>ควบ ทรัพย์สินทางปัญญาและเศรษฐกิจสร้างสรรค์</span>')
    r = one(r, '>ควบ อุตสาหกรรม &middot; นวัตกรรมและเทคโนโลยี</span>', '>ควบ นวัตกรรมและเทคโนโลยี</span>')
    # the industry card: card from the <div style="background…"> that holds ministry 18
    k = r.index('๑๘. กระทรวงอุตสาหกรรม</span>')
    c0 = r.rindex('<div style="background', 0, k)
    c0, c1 = block_span(r, c0)
    card = r[c0:c1]
    img = re.search(r'<img src="images/cab/thanathorn\.jpg[^>]*>', card).group(0)
    style = re.search(r'style="([^"]*)"', img).group(1)
    box_style = style.replace('#fb923c', GREY)
    box = ('<div role="img" aria-label="%s" style="%s; background: #4b5563; display: flex; align-items: center; '
           'justify-content: center; color: #d1d5db; font-size: 13px">%s</div>') % (NAME, box_style.rstrip('; '), NAME)
    card = card.replace(img, box)
    card = re.sub(r'border-top: ?3px solid #fb923c', lambda m: m.group(0).replace('#fb923c', GREY), card, count=1)
    name_div = re.search(r'(line-height: ?1\.55;?">)(ธนาธร จึงรุ่งเรืองกิจ \(เอก\).*?)(</div>)', card)
    card = card[:name_div.start(2)] + NAME + card[name_div.end(2):]
    card = card.replace('>พรรคก้าวไกล</div>', '>%s</div>' % PARTY)
    assert 'ธนาธร' not in card and 'thanathorn' not in card and card.count(PARTY) == 1, card
    r = r[:c0] + card + r[c1:]
    assert tb.balanced(r)
    return r


for f in ['src/tabs/cabinet-tab.html', 'website_constitution.html']:
    s = io.open(f, encoding='utf-8').read()
    if 'data-cab="rome3b"' in s:
        print('skip', f)
        continue
    a = s.index('<div data-cab="rome2">')
    a, b = block_span(s, a)
    set1 = s[a:b]
    set2 = make_set2(set1)
    set1 = one(set1, 'คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ &mdash;', 'คณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ ชุดที่ ๑ &mdash;')
    set1 = set1.replace('<div data-cab="rome2">', '<div data-cab="rome2" hidden>', 1)
    s = s[:a] + set2 + set1 + s[b:]
    # buttons: the new set first and pressed; the old one becomes ชุดที่ ๑ · ๒๗๓๗–๒๗๓๙
    i = s.index(OLD_BTN_LABEL)
    b0 = s.rindex('<button', 0, i)
    old_btn = s[b0:i + len(OLD_BTN_LABEL)]
    assert 'aria-pressed="true"' in old_btn
    new_old = old_btn.replace('aria-pressed="true"', 'aria-pressed="false"').replace(
        '🟠 รัฐบาลรังสิมันต์ ๓ · ๒๗๓๗&ndash;ปัจจุบัน', '🟠 รัฐบาลรังสิมันต์ ๓ ชุดที่ ๑ · ๒๗๓๗&ndash;๒๗๓๙')
    s = s[:b0] + NEW_BTN + new_old + s[i + len(OLD_BTN_LABEL):]
    io.open(f, 'w', encoding='utf-8', newline='').write(s)
    print('ok', f)
