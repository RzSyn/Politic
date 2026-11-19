# -*- coding: utf-8 -*-
"""จอมพลอัคนี ศรีวัฒนาวุธ: the user's photo (marshal's uniform at อนุสาวรีย์ประชาธิปไตย, 2026-11-19).
images/akkani.jpg (4:5 crop) replaces the pending box in villains-tab; images/akkani_monument.jpg (full)
goes into coup-2750-tab after the stats. Both sites. Run once from the repo root."""
import io
import re
import sys

sys.path.insert(0, 'tools')
import tab_blocks as tb

OLD = 'website_constitution.html'


def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)


def both(tid, fn):
    f = 'src/tabs/%s.html' % tid
    wr(f, fn(rd(f), 'new'))
    s = rd(OLD)
    p0 = s.index('<div id="%s"' % tid)
    p1 = tb.div_span(s, p0)
    wr(OLD, s[:p0] + fn(s[p0:p1], 'old') + s[p1:])


def villains(t, site):
    m = re.search(r'<div data-photo-pending="จอมพลอัคนี ศรีวัฒนาวุธ"[^>]*>[^<]*</div>', t)
    assert m and t.count('data-photo-pending="จอมพลอัคนี') == 1
    return t[:m.start()] + '<img src="images/akkani.jpg" alt="จอมพลอัคนี ศรีวัฒนาวุธ" class="tri-profile-img">' + t[m.end():]


CAP = 'จอมพลอัคนี ศรีวัฒนาวุธ ที่อนุสาวรีย์ประชาธิปไตย'


def coup(t, site):
    assert 'akkani_monument.jpg' not in t
    fig = tb.new_render('', '', '', [('figure', 'images/akkani_monument.jpg', CAP, CAP, 760)]) if site == 'new' \
        else tb.old_render('', '', '', [('figure', 'images/akkani_monument.jpg', CAP, CAP, 760)])
    fig = next(line for line in fig.split('\n') if 'akkani_monument.jpg' in line).strip()   # the one figure line
    assert tb.balanced(fig)
    # after the stats row: the first "ก่อนการยึดอำนาจ" heading
    k = t.index('🪖 ก่อนการยึดอำนาจ')
    h = t.rindex('<section', 0, k) if site == 'new' else t.rindex('<div', 0, k)
    return t[:h] + fig + '\n' + t[h:]


both('villains-tab', villains)
both('coup-2750-tab', coup)
print('อัคนี photo added')
