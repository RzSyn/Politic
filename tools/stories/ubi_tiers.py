# -*- coding: utf-8 -*-
"""Economy tab (2026-10-16, user): the 399,000 UBI is the *special* UBI for low-income people; add a
regular UBI for everyone that is lower than it. Chosen: 33.5% of the monthly minimum wage = 381,900 baht,
which keeps ม.๑๑๕๖ ("ไม่ต่ำกว่าเส้นความยากจน", 379,050) true. Special recipients get the special amount
instead of (not on top of) the regular one. Both sites. Run from the repo root."""
import io, re, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb

TH = '๐๑๒๓๔๕๖๗๘๙'
def th(x): return ''.join(TH[int(c)] if c.isdigit() else c for c in str(x))
WAGE_M, SPECIAL, POV, POP, QUOTA = 1_140_000, 399_000, 379_050, 89_310_000, 1_200_000
GDP = 30_418_500 * POP
REG = WAGE_M * 335 // 1000
assert REG == 381_900 and POV < REG < SPECIAL
REG_N = POP - QUOTA
REG_Y = REG * 12 * REG_N
n = lambda x: th(f'{x:,}')
tril = th(f'{REG_Y / 1e12:,.2f}'); share = th(f'{REG_Y / GDP * 100:.2f}')

NOTE = (f'💵 <strong>UBI มี ๒ ระดับ</strong> &mdash; <strong>UBI ปกติ {n(REG)} บาท</strong> (๓๓.๕% ของค่าแรงขั้นต่ำต่อเดือน) สำหรับคนไทยทุกคน ตั้งแต่เกิดจนตายตามมาตรา ๑๑๕๖ '
        f'และ <strong>UBI พิเศษ {n(SPECIAL)} บาท</strong> (๓๕%) สำหรับผู้มีรายได้น้อย ๑.๒ ล้านคน ซึ่งได้รับแทน UBI ปกติ ไม่ได้รับซ้อน '
        f'&mdash; งบ UBI ปกติ (ผู้รับ {th(f"{REG_N / 1e6:.2f}")} ล้านคน) ปีละ {tril} ล้านล้านบาท ({share}% ของ GDP)')

TEXT = [
    ('>UBI ต่อคนต่อเดือน<', '>UBI พิเศษต่อคนต่อเดือน (ผู้มีรายได้น้อย)<', 1),
    ('💸 UBI (จำกัด ๑.๒ ล้านคน)', '💸 UBI พิเศษสำหรับผู้มีรายได้น้อย (จำกัด ๑.๒ ล้านคน)', 1),
    ('&mdash; UBI ๓๙๙,๐๐๐ บาท สูงกว่าเส้นความยากจน ๓๗๙,๐๕๐ บาท',
     f'&mdash; UBI ปกติ {n(REG)} บาทสำหรับคนไทยทุกคน สูงกว่าเส้นความยากจน ๓๗๙,๐๕๐ บาท ส่วน UBI พิเศษ ๓๙๙,๐๐๐ บาทสำหรับผู้มีรายได้น้อย', 1),
    ('สูงกว่า UBI ต่อเดือน', 'สูงกว่า UBI พิเศษต่อเดือน', 1),
    ('ผู้ได้รับ UBI ทุกคนจึงอยู่เหนือเส้นความยากจน', 'ผู้ได้รับ UBI ทั้งสองระดับจึงอยู่เหนือเส้นความยากจน', 1),
    ('>ของ UBI<', '>ของ UBI พิเศษ<', 1),
]

def tr_with(seg, text):
    i = seg.index(text); a = seg.rindex('<tr', 0, i); b = seg.index('</tr>', i) + 5
    return a, b

def apply(seg, site):
    if 'UBI ปกติ' in seg:
        return seg
    for a, b, c in TEXT:
        assert seg.count(a) == c, (site, a, seg.count(a)); seg = seg.replace(a, b)
    seg = seg.replace('๙๕% ของ UBI', '๙๕% ของ UBI พิเศษ')
    # summary table: a regular-UBI row before the special one
    a, b = tr_with(seg, '💸 UBI พิเศษสำหรับผู้มีรายได้น้อย')
    row = seg[a:b]
    reg = (row.replace('💸 UBI พิเศษสำหรับผู้มีรายได้น้อย (จำกัด ๑.๒ ล้านคน)', '💵 UBI ปกติ (คนไทยทุกคน)')
              .replace('๓๙๙,๐๐๐ / เดือน', f'{n(REG)} / เดือน')
              .replace('เงินถ้วนหน้าสำหรับกลุ่มเป้าหมาย อยู่ได้สบายโดยไม่ต้องทำงาน',
                       'รายได้พื้นฐานของคนไทยทุกคนตามมาตรา ๑๑๕๖ &mdash; ๓๓.๕% ของค่าแรงขั้นต่ำต่อเดือน สูงกว่าเส้นความยากจน'))
    assert reg != row and n(REG) in reg
    seg = seg[:a] + reg + seg[a:]
    # per day/month/year table: the row whose first cell is exactly "UBI"
    m = re.search(r'<tr>(<td[^>]*>)UBI(</td>).*?</tr>', seg, re.S); assert m, site
    row = m.group(0)
    special = row.replace('>UBI<', '>UBI พิเศษ<', 1)
    regular = row.replace('>UBI<', '>UBI ปกติ<', 1).replace('๓๙๙,๐๐๐', n(REG)).replace('๔,๗๘๘,๐๐๐', n(REG * 12))
    assert n(REG * 12) in regular
    seg = seg[:m.start()] + regular + special + seg[m.end():]
    # note after the UBI formula paragraph
    i = seg.index('สูตรคำนวณ:')
    if site == 'new':
        p_end = seg.index('</div>', seg.index('</p>', i)) + len('</div>')
        seg = seg[:p_end] + f'\n  <div class="nwc-note"><p>{NOTE}</p></div>' + seg[p_end:]
    else:
        st = seg.rindex('<div', 0, i); p_end = tb.div_span(seg, st)
        seg = seg[:p_end] + ('\n  <div style="background:rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.3); border-left:4px solid #6ee7b7; '
                             f'border-radius:10px; padding:13px 16px; margin:12px 0; font-size:13.5px; color:var(--text-muted); line-height:1.85;">{NOTE}</div>') + seg[p_end:]
    seg = seg.replace('สูตรคำนวณ:', 'สูตรคำนวณ UBI พิเศษ:', 1)
    assert tb.balanced(seg), site
    return seg

f = 'src/tabs/welfare-economy-tab.html'
s = io.open(f, encoding='utf-8').read(); io.open(f, 'w', encoding='utf-8', newline='').write(apply(s, 'new')); print('ok', f)
f = 'website_constitution.html'
s = io.open(f, encoding='utf-8').read()
p0 = s.index('<div id="welfare-economy-tab"'); p1 = tb.div_span(s, p0)
s = s[:p0] + apply(s[p0:p1], 'old') + s[p1:]
io.open(f, 'w', encoding='utf-8', newline='').write(s); print('ok', f)
print('regular UBI', REG, 'budget', tril, 'share', share)
