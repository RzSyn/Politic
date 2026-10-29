# -*- coding: utf-8 -*-
"""Parties tab (2026-10-29, user): add พรรคสหายไทยแลนด์ — socialist, founded and led by วิชัย เคียวเหล็ก
(สหายวิชัย), 1 MP, joined รัฐบาลรังสิมันต์ ๓ in ๒๗๓๙ (ครม. ชุดที่ ๒, กระทรวงอุตสาหกรรม: ธนกฤต ใจเพชร).
Logo and song from the user; no slogan or lyrics were given, so the card has neither.
Built from the NIP card, placed after ธรรมปัญญา. Both sites. Run from the repo root."""
import io
import re
import shutil
import sys

from PIL import Image

sys.path.insert(0, 'tools')
import tab_blocks as tb

DL = 'C:/Users/ASUA/Downloads/'
im = Image.open(DL + 'สหายไทยแลนด์.jpg').convert('RGB')
im.thumbnail((600, 600), Image.LANCZOS)
im.save('images/logo_sahai.jpg', quality=92)
shutil.copyfile(DL + 'อุดมการณ์ของสหาย.mp3', 'audio/sahai_udomkan.mp3')

RED = '#ef4444'
LEADER = ('วิชัย เคียวเหล็ก (สหายวิชัย) &mdash; ผู้ก่อตั้งและหัวหน้าพรรค</strong>'
          ' &nbsp;|&nbsp; ส.ส. ๑ คน &middot; พรรคร่วมรัฐบาล (ตั้งแต่ ๒๗๓๙)')
STORY = ('พรรคแนวสังคมนิยม ก่อตั้งโดยนายวิชัย เคียวเหล็ก หรือ "สหายวิชัย" ซึ่งเป็นหัวหน้าพรรคด้วย &mdash; '
         'ปี ๒๗๓๙ รัฐบาลรังสิมันต์ โรม ดึงพรรคสหายไทยแลนด์ (ส.ส. ๑ คน) เข้าร่วมรัฐบาล เป็นขั้ว ๔ พรรค ๓๑๘ เสียง '
         'ธนาธร จึงรุ่งเรืองกิจ สละเก้าอี้รัฐมนตรีว่าการกระทรวงอุตสาหกรรมให้ <strong>ธนกฤต ใจเพชร</strong> จากพรรคสหายไทยแลนด์ '
         'กลายเป็นคณะรัฐมนตรีรัฐบาลรังสิมันต์ ๓ ชุดที่ ๒')
STATUS = 'พรรคร่วมรัฐบาล (ครม. ชุดที่ ๒ ตั้งแต่ ๒๗๓๙) · ส.ส. ๑ คน'


def one(s, a, b):
    assert s.count(a) == 1, (a[:60], s.count(a))
    return s.replace(a, b)


def card_of(s, marker):
    i = s.index(marker)
    chain = []
    for st in reversed([m.start() for m in re.finditer(r'<div\b', s[:i])]):
        e = tb.div_span(s, st)
        if e > i:
            chain.append((st, e))
        if len(chain) == 3:
            return chain[2]


def sahai_from(c):
    c = one(c, 'src="images/logo_nip.jpg" alt="พรรคอุดมการณ์ใหม่"', 'src="images/logo_sahai.jpg" alt="พรรคสหายไทยแลนด์"')
    c = one(c, '>พรรคอุดมการณ์ใหม่</span>', '>พรรคสหายไทยแลนด์</span>')
    c = one(c, 'New Ideology Party (NIP)', 'Sahai Thailand Party')
    c = one(c, '&middot; พรรคร่วมรัฐบาล · ส.ส. ๓๖ คน</div>', '&middot; %s</div>' % STATUS)
    a = c.index('หัวหน้าพรรค/ผู้นำ:</strong>'); a = c.index('<strong', a); a = c.index('>', a) + 1
    b = c.index('</span></div>', a)
    c = c[:a] + LEADER + c[b:]
    m = re.search(r'(<div style="font-size: ?13px; ?color: ?var\(--[^)]*\); ?line-height: ?1\.6; ?margin-top: ?6px;?">).*?(</div>)', c, re.S)
    c = c[:m.start()] + m.group(1) + STORY + m.group(2) + c[m.end():]
    # no slogan / analysis given: drop that block
    m = re.search(r'\s*<div style="margin-top: ?8px; ?padding-top: ?8px; ?border-top: ?1px solid [^"]*">.*?สโลแกน: .*?</p>\s*</div>', c, re.S)
    c = c[:m.start()] + c[m.end():]
    c = one(c, 'เพลง "อุดมการณ์ใหม่"', 'เพลง "อุดมการณ์ของสหาย"')
    c = one(c, 'AUDIO &amp; LYRICS AVAILABLE', 'AUDIO AVAILABLE')
    assert c.count('audio/nip_udomkan.mp3') == 3
    c = c.replace('audio/nip_udomkan.mp3', 'audio/sahai_udomkan.mp3')
    m = re.search(r'\s*<div style="[^"]*font-style: ?italic;?">.*?</div>', c, re.S)
    c = c[:m.start()] + c[m.end():]
    c = c.replace('#f87171', RED)
    for bad in ('อุดมการณ์ใหม่', 'ภาคิน', 'nip_', 'NIP', 'ทักษิณ'):
        assert bad not in c, bad
    assert tb.balanced(c)
    return c


for f in ['src/tabs/parties-tab.html', 'website_constitution.html']:
    s = io.open(f, encoding='utf-8').read()
    if 'Sahai Thailand Party' in s:
        print('skip', f)
        continue
    nst, ne = card_of(s, 'New Ideology Party (NIP)')
    card = sahai_from(s[nst:ne])
    tst, te = card_of(s, 'Thampanya Party')
    assert 'Thai Rak Thai Party' in s[te:te + 6000]
    s = s[:te] + '\n\n          ' + card + s[te:]
    io.open(f, 'w', encoding='utf-8', newline='').write(s)
    print('ok', f)
