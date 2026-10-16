# -*- coding: utf-8 -*-
"""ศนท. tab (2026-10-16, user): the rally was March ๒๗๓๗, peaceful, at ธรรมศาสตร์ ท่าพระจันทร์ /
อนุสาวรีย์ประชาธิปไตย / สนามหลวง; founded ๒๗๓๗ by 35 student leaders; anthem lyrics. Both sites.
Run from the repo root."""
import io, re, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb

LYRICS = """จากเหนือจรดใต้ เราร่วมทางเดียวกัน
เสียงเยาวชนก้องกลางแผ่นดินไทย
มือของเราประสาน ใจของเรามั่น
สร้างวันพรุ่งนี้ด้วยความเข้าใจ

ให้สิทธิ์ทุกเสียงได้ยืนอย่างเท่าเทียม
ให้ความหวังเริ่มจากเราในวันนี้

ศูนย์กลางสหภาพนักเรียน นิสิต นักศึกษา
ร่วมรักษาประชาธิปไตยให้มั่นคง
ศนท. ก้าวไปด้วยใจซื่อตรง
เพื่อบ้านเมืองที่ทุกคนมีส่วนร่วม

ในห้องเรียน ในชุมชน เราฟังกัน
ต่างความคิดก็ร่วมสร้างทางสดใส
ด้วยความกล้าและไมตรีเป็นพลัง
ให้ความเป็นธรรมเติบโตในเมืองไทย

ให้สิทธิ์ทุกเสียงได้ยืนอย่างเท่าเทียม
ให้ความหวังเริ่มจากเราในวันนี้

ศูนย์กลางสหภาพนักเรียน นิสิต นักศึกษา
ร่วมรักษาประชาธิปไตยให้มั่นคง
ศนท. ก้าวไปด้วยใจซื่อตรง
เพื่อบ้านเมืองที่ทุกคนมีส่วนร่วม

ชายและหญิง ร่วมร้องประสาน
คนรุ่นใหม่จับมือก้าวเดิน
ยืนหยัดด้วยปัญญาและความกล้า
เพื่อวันพรุ่งนี้ที่งดงามกว่าเดิม

ศูนย์กลางสหภาพนักเรียน นิสิต นักศึกษา
ร่วมรักษาประชาธิปไตยให้มั่นคง
ศนท. ก้าวไปด้วยใจซื่อตรง
เพื่อบ้านเมืองที่ทุกคนมีส่วนร่วม
เพื่อบ้านเมืองที่ทุกคนมีส่วนร่วม

ศนท. ก้าวไป&mdash;ร่วมใจก้าวไป!"""
LYR_HTML = '<br>'.join(l if l else '' for l in LYRICS.split('\n')).replace('<br><br>', '<br><br>')

PLACES = 'มหาวิทยาลัยธรรมศาสตร์ ท่าพระจันทร์ &middot; อนุสาวรีย์ประชาธิปไตย &middot; สนามหลวง'
REPL = [
    ('ผู้นำการชุมนุมเดือนมกราคม ๒๗๓๖', 'ผู้นำการชุมนุมอย่างสงบเดือนมีนาคม ๒๗๓๗'),
    ('ผู้นำการชุมนุม ม.ค. ๒๗๓๖ ที่นำไปสู่การยุบสภา', 'ผู้นำการชุมนุมอย่างสงบ มี.ค. ๒๗๓๗ ที่นำไปสู่การยุบสภา'),
    ('บทบาทในการเมือง ๒๗๓๖', 'บทบาทในการเมือง ๒๗๓๗'),
    ('กลางปี ๒๗๓๖', 'หลังการชุมนุม'),
    ('ปลายปี ๒๗๓๖', 'เลือกตั้งใหม่'),
]

def fix(seg, site):
    for a, b in REPL:
        assert seg.count(a) == 1, (site, a, seg.count(a)); seg = seg.replace(a, b)
    # stats card and timeline row both say "ม.ค. ๒๗๓๖"
    assert seg.count('ม.ค. ๒๗๓๖') == 2, (site, seg.count('ม.ค. ๒๗๓๖'))
    seg = seg.replace('ม.ค. ๒๗๓๖', 'มี.ค. ๒๗๓๗')
    seg = seg.replace('การชุมนุมใหญ่ต่อรัฐบาล ๔๑๓ เสียง', 'ชุมนุมอย่างสงบ ๓ จุด &mdash; ไม่มีการใช้ความรุนแรง')
    a = seg.index('ชุมนุมกดดันรัฐบาล ๔๑๓ เสียง')
    p_end = seg.index('รวมตัวชุมนุม', a) + len('รวมตัวชุมนุม')
    seg = seg[:p_end] + (f'อย่างสงบ ณ <strong>{PLACES}</strong> โดยไม่มีการใช้ความรุนแรง') + seg[p_end:]
    seg = seg.replace('ชุมนุมกดดันรัฐบาล ๔๑๓ เสียง', 'ชุมนุมอย่างสงบกดดันรัฐบาล ๔๑๓ เสียง', 1)
    # facts on the group
    key = 'ศนท. &middot; NSCT</'
    i = seg.index(key)
    if site == 'new':
        row = seg.rindex('<dt>', 0, i)
        end = seg.index('</dd>', i) + 5
        seg = seg[:end] + '<dt>ก่อตั้ง</dt><dd>พ.ศ. ๒๗๓๗</dd><dt>แกนนำ</dt><dd>แกนนำนักศึกษา ๓๕ คน</dd>' + seg[end:]
    else:
        st = seg.rindex('<div style="display:flex; gap:12px; padding:8px 0;', 0, i); en = tb.div_span(seg, st)
        row = seg[st:en]
        new_rows = ''.join(row.replace('ชื่อย่อ', k, 1).replace('ศนท. &middot; NSCT', v, 1) for k, v in
                           [('ก่อตั้ง', 'พ.ศ. ๒๗๓๗'), ('แกนนำ', 'แกนนำนักศึกษา ๓๕ คน')])
        seg = seg[:en] + new_rows + seg[en:]
    # lyrics under the audio-only player
    j = seg.index('audio/nsct_anthem.mp3')
    k = seg.index('</audio>', j) + len('</audio>')
    k = seg.index('</div>', k) + len('</div>')   # close .audio-box
    if site == 'new':
        box = ('<div style="background: var(--nw-surface-2); padding: 12px 16px; border-left: 3px solid #f97316; border-radius: 6px; '
               'font-size: 13px; color: var(--nw-text); line-height: 1.85; font-style: italic; margin-top: 10px">' + LYR_HTML + '</div>')
    else:
        box = ('<div style="background:rgba(249,115,22,0.06); padding:12px 16px; border-left:3px solid #f97316; border-radius:6px; '
               'font-size:13px; color:var(--text); line-height:1.85; font-style:italic; margin-top:10px;">' + LYR_HTML + '</div>')
    seg = seg[:k] + box + seg[k:]
    assert tb.balanced(seg), site
    return seg

f = 'src/tabs/nsct-tab.html'
s = io.open(f, encoding='utf-8').read(); assert 'ร่วมใจก้าวไป' not in s
io.open(f, 'w', encoding='utf-8', newline='').write(fix(s, 'new')); print('ok', f)
f = 'website_constitution.html'
s = io.open(f, encoding='utf-8').read()
p0 = s.index('<div id="nsct-tab"'); p1 = tb.div_span(s, p0)
assert 'ร่วมใจก้าวไป' not in s[p0:p1]
s = s[:p0] + fix(s[p0:p1], 'old') + s[p1:]
io.open(f, 'w', encoding='utf-8', newline='').write(s); print('ok', f)
