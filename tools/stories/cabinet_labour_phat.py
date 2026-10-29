# -*- coding: utf-8 -*-
"""Cabinet รังสิมันต์ ๓ (2026-10-29, user): กระทรวงแรงงานและสวัสดิการสังคม goes to ธีรภัทร วัฒนากร (ภัทร).
ณัฐวุฒิ keeps หลักประกันและความเป็นธรรมทางสังคม only. Rome 1's set is history and stays as it was.
Both sites. Run from the repo root."""
import io
import re

from PIL import Image

# 440x550 face like the other ministers (images/phat.jpg is already 4:5)
Image.open('images/phat.jpg').convert('RGB').resize((440, 550), Image.LANCZOS).save('images/cab/phat.jpg', quality=92)

NEW = 'ธีรภัทร วัฒนากร (ภัทร)'
BADGE = re.compile(r'<span style="[^"]*">ควบ (หลักประกันและความเป็นธรรมทางสังคม|แรงงานและสวัสดิการสังคม)</span>')


def rome2(s):
    a = s.index('data-cab="rome2"')
    return a, s.index('data-cab="rome"', a)


for f in ['src/tabs/cabinet-tab.html', 'website_constitution.html']:
    s = io.open(f, encoding='utf-8').read()
    if 'images/cab/phat.jpg' in s:
        print('skip', f)
        continue
    a, b = rome2(s)
    r = s[a:b]
    # the labour card: from its photo to its party line
    k = r.index('๑๔. กระทรวงแรงงานและสวัสดิการสังคม</span>')
    c0 = r.rindex('<img src="images/cab/', 0, k)
    c1 = r.index('พรรคก้าวไกล</div>', k)
    card = r[c0:c1]
    assert card.count('ณัฐวุฒิ บัวประทุม') == 2, card
    card = card.replace('src="images/cab/nattawut_b2.jpg?v=2" alt="ณัฐวุฒิ บัวประทุม"', f'src="images/cab/phat.jpg?v=2" alt="{NEW}"')
    card, n = BADGE.subn('', card)
    assert n == 1
    card = card.replace('ณัฐวุฒิ บัวประทุม', NEW)
    assert 'ณัฐวุฒิ' not in card
    r = r[:c0] + card + r[c1:]
    # ณัฐวุฒิ's remaining card loses its "ควบ แรงงาน…" badge
    r, n = BADGE.subn('', r)
    assert n == 1
    assert r.count('>๑๖ / ๓๖</div>') == 1
    r = r.replace('>๑๖ / ๓๖</div>', '>๑๗ / ๓๖</div>')
    s = s[:a] + r + s[b:]
    io.open(f, 'w', encoding='utf-8', newline='').write(s)
    print('ok', f)

# welfare-economy: the minister in charge of the wage
OLD1 = 'รัฐมนตรีว่าการคือ ณัฐวุฒิ บัวประทุม (พรรคก้าวไกล) ในรัฐบาลรังสิมันต์ โรม'
NEW1 = 'รัฐมนตรีว่าการคือ ธีรภัทร วัฒนากร (พรรคก้าวไกล) ในรัฐบาลรังสิมันต์ โรม'
ROW = re.compile(r'(รัฐมนตรีว่าการกระทรวงแรงงานและสวัสดิการสังคม</td><td[^>]*>)ณัฐวุฒิ บัวประทุม( \(ก้าวไกล\)</td>)')
for f in ['src/tabs/welfare-economy-tab.html', 'website_constitution.html']:
    s = io.open(f, encoding='utf-8').read()
    if NEW1 in s:
        print('skip', f)
        continue
    assert s.count(OLD1) == 1
    s = s.replace(OLD1, NEW1)
    s, n = ROW.subn(lambda m: m.group(1) + 'ธีรภัทร วัฒนากร' + m.group(2), s)
    assert n == 1
    io.open(f, 'w', encoding='utf-8', newline='').write(s)
    print('ok', f)
