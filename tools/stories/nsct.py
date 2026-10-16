# -*- coding: utf-8 -*-
"""New tab: ศนท. (ศูนย์กลางสหภาพนักเรียนนิสิตนักศึกษาแห่งประเทศไทย / NSCT) with its anthem (2026-10-16).
Run from the repo root. Facts come from protest-2737-tab; nothing about the group is invented beyond it."""
import io, re, json, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb

TID, BTN_IC, BTN = 'nsct-tab', '📚', 'ศนท.'
ICON, TITLE = '📚', 'ศนท. &mdash; ศูนย์กลางสหภาพนักเรียนนิสิตนักศึกษาแห่งประเทศไทย'
LEAD = ('NSCT &mdash; เครือข่ายนักเรียน นิสิต และนักศึกษาทั่วประเทศ ผู้นำการชุมนุมเดือนมกราคม ๒๗๓๖ ที่กดดันรัฐบาลเสียงข้างมากเด็ดขาด ๔๑๓ เสียง '
        'จนนายกรัฐมนตรีรังสิมันต์ โรม ประกาศยุบสภาคืนอำนาจให้ประชาชน &mdash; และเมื่อผลเลือกตั้งใหม่ออกมาเท่าเดิม ศนท. ก็ยอมรับฉันทามตินั้นตามกติกา')

def media_new():
    return ('  <div class="nwc-card" style="margin-top: 12px">\n'
            '    <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 10px">'
            '<span style="font-size: 14px; color: var(--nw-acc-2); font-weight: 700; font-family: var(--nw-serif)">🎬 มิวสิกวิดีโอ (Official Music Audio)</span>'
            '<span style="font-size: 11px; color: var(--nw-text-2)">NSCT Music &middot; ๓:๒๕</span></div>\n'
            '    <video controls preload="metadata" playsinline poster="images/nsct_album.jpg" style="width: 100%; max-width: 860px; display: block; margin: 0 auto; border-radius: 10px; background: #000">'
            '<source src="video/nsct_anthem.mp4" type="video/mp4">เบราว์เซอร์ของคุณไม่รองรับการเล่นวิดีโอ</video>\n'
            '  </div>\n'
            '  <div class="nwc-card" style="margin-top: 12px">\n'
            '    <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap">'
            '<span style="font-size: 14px; color: var(--nw-acc-2); font-weight: 700; font-family: var(--nw-serif)">🎵 แบบเสียงอย่างเดียว</span>'
            '<span style="font-size: 11px; color: var(--nw-text-2)">๓:๒๑</span></div>\n'
            '    <div class="audio-box" style="margin-top: 8px">\n'
            '      <button type="button" onclick="playAudioMobile(this, \'audio/nsct_anthem.mp3\')" style="width: 100%; padding: 10px 16px; background: var(--nw-surface); color: var(--nw-text); border: 1px solid var(--nw-line); border-radius: 8px; font-weight: 700; font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px">'
            '<span style="font-size: 15px">▶️</span> กดเล่นเพลงบนมือถือ / Play Audio</button>\n'
            '      <audio controls preload="metadata" playsinline webkit-playsinline src="audio/nsct_anthem.mp3" style="width: 100%; height: 36px; border-radius: 6px; margin-top: 6px">'
            '<source src="audio/nsct_anthem.mp3" type="audio/mpeg">เบราว์เซอร์ของคุณไม่รองรับการเล่นไฟล์เสียง</audio>\n'
            '    </div>\n'
            '  </div>')

def media_old():
    box = 'background:rgba(15,18,25,0.6); border:1px solid rgba(249,115,22,0.3); border-radius:12px; padding:16px 18px; margin-top:12px;'
    return (f'  <div style="{box}">'
            '<div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">'
            '<span style="font-size:14px; color:#fdba74; font-weight:700;">🎬 มิวสิกวิดีโอ (Official Music Audio)</span><span style="font-size:11px; color:var(--text-muted);">NSCT Music &middot; ๓:๒๕</span></div>'
            '<video controls preload="metadata" playsinline poster="images/nsct_album.jpg" style="width:100%; max-width:860px; display:block; margin:0 auto; border-radius:10px; background:#000;">'
            '<source src="video/nsct_anthem.mp4" type="video/mp4">เบราว์เซอร์ของคุณไม่รองรับการเล่นวิดีโอ</video></div>\n'
            f'  <div style="{box}">'
            '<div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;">'
            '<span style="font-size:14px; color:#fdba74; font-weight:700;">🎵 แบบเสียงอย่างเดียว</span><span style="font-size:11px; color:var(--text-muted);">๓:๒๑</span></div>'
            '<div class="audio-box" style="margin-top:8px;">'
            '<button type="button" onclick="playAudioMobile(this, \'audio/nsct_anthem.mp3\')" style="width:100%; padding:10px 16px; background:rgba(249,115,22,0.15); color:#fff; border:1px solid rgba(249,115,22,0.5); border-radius:8px; font-weight:700; font-size:13px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;">'
            '<span style="font-size:15px;">▶️</span> กดเล่นเพลงบนมือถือ / Play Audio</button>'
            '<audio controls preload="metadata" playsinline webkit-playsinline src="audio/nsct_anthem.mp3" style="width:100%; height:36px; border-radius:6px; margin-top:6px;">'
            '<source src="audio/nsct_anthem.mp3" type="audio/mpeg">เบราว์เซอร์ของคุณไม่รองรับการเล่นไฟล์เสียง</audio></div></div>')

B = [
    ('stats', [('ศนท. / NSCT', 'ชื่อย่อไทย / อังกฤษ'), ('ม.ค. ๒๗๓๖', 'การชุมนุมใหญ่ต่อรัฐบาล ๔๑๓ เสียง'),
               ('ยุบสภา', 'ผลของการชุมนุม &mdash; นายกฯ รังสิมันต์ประกาศเอง'), ('ยอมรับผล', 'เมื่อเลือกตั้งใหม่ได้ผลเท่าเดิมทุกพรรค')]),
    ('figure', 'images/shnt_banner.jpg', 'ศนท. ศูนย์กลางสหภาพนักเรียนนิสิตนักศึกษาแห่งประเทศไทย', 'ศนท. &mdash; ศูนย์กลางสหภาพนักเรียนนิสิตนักศึกษาแห่งประเทศไทย', 900),
    ('h', '📋 ข้อมูลกลุ่ม'),
    ('split', 'images/shnt_emblem.jpg', 'ตราสัญลักษณ์ ศนท.', 'ตราสัญลักษณ์ ศนท.', [
        ('ชื่อเต็ม', 'ศูนย์กลางสหภาพนักเรียนนิสิตนักศึกษาแห่งประเทศไทย'),
        ('ชื่อย่อ', 'ศนท. &middot; NSCT'),
        ('สมาชิก', 'นักเรียน นิสิต และนักศึกษาทั่วประเทศ'),
        ('ตราสัญลักษณ์', 'หนังสือที่เปิดออก &mdash; ความรู้และการศึกษา &middot; รูปคนชูมือรวมพลังกันเหนือหนังสือ &mdash; พลังของคนรุ่นใหม่'),
        ('บทบาทสำคัญ', 'ผู้นำการชุมนุม ม.ค. ๒๗๓๖ ที่นำไปสู่การยุบสภา'),
        ('เพลงประจำกลุ่ม', '"พลังแห่งนักเรียนนิสิตนักศึกษา" (Rally Anthem) &mdash; NSCT Music')]),
    ('h', '✊ บทบาทในการเมือง ๒๗๓๖'),
    ('time', [('ม.ค. ๒๗๓๖', 'ชุมนุมกดดันรัฐบาล ๔๑๓ เสียง',
               'หลังก้าวไกล ทักษิประชา ไทยรักไทย และธรรมปัญญา รวมกันได้ ๔๑๓ เสียง ศนท. มองว่ารัฐบาลชุดนี้ "มีอำนาจล้นพ้นและเบ็ดเสร็จเกินไปจนทำลายสมดุลประชาธิปไตย" จึงรวมตัวชุมนุม'),
              ('กลางปี ๒๗๓๖', 'นายกฯ ประกาศยุบสภา',
               'ขณะพรรคร่วมรัฐบาลยังประชุมกันวุ่นวาย รังสิมันต์ โรม แถลงผ่านโทรทัศน์และสื่อรวมการเฉพาะกิจแห่งประเทศไทย ประกาศยุบสภา &mdash; "เราเองก็เคยเป็นคนกลุ่มนี้ คนที่เรียกร้องประชาธิปไตยจนเราทำสำเร็จ"'),
              ('ปลายปี ๒๗๓๖', 'ยอมรับฉันทามติ',
               'การเลือกตั้งใหม่ได้ผลเท่าเดิมทุกพรรคทั้ง ๕๐๐ เสียง ศนท. ยอมรับผลตามกติกา &mdash; ดุลอำนาจที่เปลี่ยนไปหลังจากนั้นเกิดจากทักษิประชาฉีก MOU เอง')]),
    ('note', '🔗 รายละเอียดเหตุการณ์ทั้งหมด ผลโพล และการเกิดพรรคอุดมการณ์ใหม่ อยู่ในแถบ &ldquo;📣 การประท้วง &amp; ทิศทางใหม่ ๒๗๓๗&rdquo;'),
    ('h', '🎵 เพลงประจำกลุ่ม &mdash; "พลังแห่งนักเรียนนิสิตนักศึกษา" (Rally Anthem)'),
    ('figure', 'images/nsct_album.jpg', 'ปกอัลบั้ม พลังแห่งนักเรียนนิสิตนักศึกษา', 'ปกอัลบั้ม &mdash; NSCT Music &middot; Official Music Audio', 420),
    ('raw', media_new(), media_old()),
]

def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)

NEW = f'<div id="{TID}" class="db-tab-content">\n' + tb.new_render(ICON, TITLE, LEAD, B) + '\n</div>\n'
OLD = f'\n<div id="{TID}" class="db-tab-content">\n' + tb.old_render(ICON, TITLE, LEAD, B, accent=('#fdba74', '249,115,22')) + '\n</div>'
assert tb.balanced(NEW) and tb.balanced(OLD) and '%%' not in NEW + OLD

h = rd('src/hub.json'); assert TID not in h
anchor = '''        "id": "protest-2737-tab",
        "icon": "📣",
        "label": "การประท้วง & ทิศทางใหม่ ๒๗๓๗"
      },'''
assert h.count(anchor) == 1
h = h.replace(anchor, anchor + f'\n      {{\n        "id": "{TID}",\n        "icon": "{BTN_IC}",\n        "label": "{BTN}"\n      }},')
json.loads(h); wr('src/hub.json', h); wr(f'src/tabs/{TID}.html', NEW)

s = rd('website_constitution.html'); assert TID not in s
btn = """<button class="db-tab-btn" onclick="switchTab('protest-2737-tab', this)" style="border-color:rgba(251,146,60,0.6);color:#fdba74;">📣 การประท้วง &amp; ทิศทางใหม่ ๒๗๓๗</button>"""
assert s.count(btn) == 1, s.count(btn)
s = s.replace(btn, btn + f"""\n          <button class="db-tab-btn" onclick="switchTab('{TID}', this)" style="border-color:rgba(249,115,22,0.6);color:#fdba74;">{BTN_IC} {BTN}</button>""")
p0 = s.index('<div id="protest-2737-tab"'); end = tb.div_span(s, p0)
assert s.index('<section id="history_and_pms"') < end < s.index('</section>', end)
s = s[:end] + OLD + s[end:]
assert s.count(f'id="{TID}"') == 1
wr('website_constitution.html', s)
print('ok')
