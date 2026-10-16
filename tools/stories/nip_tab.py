# -*- coding: utf-8 -*-
"""2026-10-16: (1) protest tab says ดร. ภาคิน เมธาปรีชากุล founded พรรคอุดมการณ์ใหม่; (2) new tab
"พรรคสีแดงใหม่" about พรรคอุดมการณ์ใหม่ (NIP), after the red-party tab. Run from the repo root."""
import io, json, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb
from PIL import Image

def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='').write(s)

im = Image.open('C:/Users/ASUA/Downloads/Thai Political Campaign Portrait Poster.png').convert('RGB')
im.thumbnail((900, 1100), Image.LANCZOS); im.save('images/nip_pakin_poster.jpg', quality=86)

# ---- (1) protest tab ----
P1 = ('ส.ส. ดาวเด่นนโยบาย ๓๕ คน แยกไปตั้งพรรคอุดมการณ์ใหม่',
      'ส.ส. ดาวเด่นนโยบาย ๓๕ คน นำโดย <strong>ดร. ภาคิน เมธาปรีชากุล</strong> ผู้ก่อตั้งและหัวหน้าพรรค แยกไปตั้งพรรคอุดมการณ์ใหม่')
P2 = ('ส.ส. ๓๕ คน + ทักษิณ ตั้ง "อุดมการณ์ใหม่"', 'ดร. ภาคิน เมธาปรีชากุล นำ ส.ส. ๓๕ คน + ทักษิณ ตั้ง "อุดมการณ์ใหม่"')
P3 = ('ส.ส. ๓๕ คนมองว่าการเป็นฝ่ายค้านแบบไร้ทิศทาง', 'ส.ส. ๓๕ คนซึ่งมี ดร. ภาคิน เมธาปรีชากุล เป็นผู้ก่อตั้งพรรค มองว่าการเป็นฝ่ายค้านแบบไร้ทิศทาง')
for f in ['src/tabs/protest-2737-tab.html', 'website_constitution.html']:
    s = rd(f)
    if 'ผู้ก่อตั้งและหัวหน้าพรรค แยกไปตั้งพรรคอุดมการณ์ใหม่' in s:
        print('skip protest', f); continue
    for a, b in (P1, P2, P3):
        assert s.count(a) == 1, (f, a, s.count(a)); s = s.replace(a, b)
    wr(f, s); print('ok protest', f)

# ---- (2) new tab ----
TID, BTN_IC, BTN = 'new-red-party-tab', '🔥', 'พรรคสีแดงใหม่'
ICON, TITLE = '🔥', 'พรรคสีแดงใหม่ &mdash; พรรคอุดมการณ์ใหม่ (New Ideology Party &middot; NIP)'
LEAD = ('พรรคที่เกิดจากการแตกหักของทักษิประชา ก่อตั้งโดย <strong>ดร. ภาคิน เมธาปรีชากุล</strong> พร้อม ส.ส. ดาวเด่นนโยบาย ๓๕ คน และ ฯพณฯ พล.ต.อ.ทักษิณ ชินวัตร '
        '&mdash; จากพรรคที่ยังไม่มีอยู่ในต้นปี ๒๗๓๖ สู่พรรคอันดับ ๒ ของประเทศ (14.91%) และพรรคร่วมรัฐบาลรังสิมันต์ ๒')
MUSIC_NEW = ('  <div class="nwc-card" style="margin-top: 12px"><div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap">'
             '<span style="font-size: 14px; color: var(--nw-acc-2); font-weight: 700; font-family: var(--nw-serif)">🎵 เพลง "อุดมการณ์ใหม่"</span>'
             '<span style="font-size: 11px; color: var(--nw-text-2)">๔:๑๐</span></div>'
             '<div class="audio-box" style="margin-top: 8px"><button type="button" onclick="playAudioMobile(this, \'audio/nip_udomkan.mp3\')" style="width: 100%; padding: 10px 16px; background: var(--nw-surface); color: var(--nw-text); border: 1px solid var(--nw-line); border-radius: 8px; font-weight: 700; font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px">'
             '<span style="font-size: 15px">▶️</span> กดเล่นเพลงบนมือถือ / Play Audio</button>'
             '<audio controls preload="metadata" playsinline webkit-playsinline src="audio/nip_udomkan.mp3" style="width: 100%; height: 36px; border-radius: 6px; margin-top: 6px"><source src="audio/nip_udomkan.mp3" type="audio/mpeg">เบราว์เซอร์ของคุณไม่รองรับการเล่นไฟล์เสียง</audio></div>'
             '<div style="background: var(--nw-surface-2); padding: 10px 14px; border-left: 3px solid #ef4444; border-radius: 6px; font-size: 12.5px; color: var(--nw-text); line-height: 1.8; font-style: italic; margin-top: 8px">'
             'เปลี่ยนความจริงใจ ให้เป็นผลงาน<br>นี่คือสัญญา เลือดเนื้อและศรัทธา<br>พรรคอุดมการณ์ใหม่ ก้าวไปเพื่อทุกคน!</div></div>')
MUSIC_OLD = ('  <div style="background:rgba(15,18,25,0.6); border:1px solid rgba(239,68,68,0.3); border-radius:12px; padding:16px 18px; margin-top:12px;">'
             '<div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;"><span style="font-size:14px; color:#fca5a5; font-weight:700;">🎵 เพลง "อุดมการณ์ใหม่"</span><span style="font-size:11px; color:var(--text-muted);">๔:๑๐</span></div>'
             '<div class="audio-box" style="margin-top:8px;"><button type="button" onclick="playAudioMobile(this, \'audio/nip_udomkan.mp3\')" style="width:100%; padding:10px 16px; background:rgba(239,68,68,0.15); color:#fff; border:1px solid rgba(239,68,68,0.5); border-radius:8px; font-weight:700; font-size:13px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;">'
             '<span style="font-size:15px;">▶️</span> กดเล่นเพลงบนมือถือ / Play Audio</button>'
             '<audio controls preload="metadata" playsinline webkit-playsinline src="audio/nip_udomkan.mp3" style="width:100%; height:36px; border-radius:6px; margin-top:6px;"><source src="audio/nip_udomkan.mp3" type="audio/mpeg">เบราว์เซอร์ของคุณไม่รองรับการเล่นไฟล์เสียง</audio></div>'
             '<div style="background:rgba(239,68,68,0.06); padding:10px 14px; border-left:3px solid #ef4444; border-radius:6px; font-size:12.5px; color:var(--text); line-height:1.8; font-style:italic; margin-top:8px;">'
             'เปลี่ยนความจริงใจ ให้เป็นผลงาน<br>นี่คือสัญญา เลือดเนื้อและศรัทธา<br>พรรคอุดมการณ์ใหม่ ก้าวไปเพื่อทุกคน!</div></div>')

B = [
    ('stats', [('๓๖ ส.ส.', '๓๕ คนจากทักษิประชา + ทักษิณ'), ('ก.ย. ๒๗๓๗', 'ก่อตั้งพรรค'), ('14.91%', 'ความนิยม ต.ค. ๒๗๓๗ &mdash; อันดับ ๒ ของประเทศ'),
               ('๓๑๗ เสียง', 'รัฐบาลที่ร่วม (ก้าวไกล ๒๖๐ + อุดมการณ์ใหม่ ๓๖ + ธรรมปัญญา ๒๑)'), ('27.34%', 'ทักษิณ &mdash; อันดับ ๒ โพลคนทำงาน'),
               ('๑ กระทรวง', 'เกษตรและสหกรณ์ (ดร. ภาคิน)')]),
    ('figure', 'images/logo_nip.jpg', 'โลโก้พรรคอุดมการณ์ใหม่', 'โลโก้พรรคอุดมการณ์ใหม่ &mdash; คบเพลิงในอักษร อม พร้อมลูกศรชี้ขึ้น', 300),
    ('h', '👤 ผู้ก่อตั้งและหัวหน้าพรรค'),
    ('split', 'images/nip_pakin_poster.jpg', 'ดร. ภาคิน เมธาปรีชากุล', 'ดร. ภาคิน เมธาปรีชากุล &mdash; หัวหน้าพรรคอุดมการณ์ใหม่', [
        ('ชื่อ', 'ดร. ภาคิน เมธาปรีชากุล'),
        ('บทบาทในพรรค', 'ผู้ก่อตั้งและหัวหน้าพรรคอุดมการณ์ใหม่'),
        ('ตำแหน่งในสภา', 'สมาชิกสภาผู้แทนราษฎรแบบบัญชีรายชื่อ'),
        ('ตำแหน่งในรัฐบาล', 'รัฐมนตรีว่าการกระทรวงเกษตรและสหกรณ์ (รัฐบาลรังสิมันต์ ๒)'),
        ('ก่อนก่อตั้งพรรค', 'ส.ส. พรรคทักษิประชา &mdash; หนึ่งในกลุ่ม ส.ส. ดาวเด่นนโยบายราว ๓๘ คนของพรรค'),
        ('รองหัวหน้าพรรค', 'ฯพณฯ พล.ต.อ.ทักษิณ ชินวัตร (อดีตนายกฯ คนที่ ๔ และ ๓๐)')]),
    ('quote', '"การเมืองที่ดี เริ่มได้จากคนรุ่นใหม่ที่ไม่ยอมแพ้"'),

    ('h', '🔥 กำเนิดพรรค'),
    ('time', [('ปลายปี ๒๗๓๖', 'ทักษิประชาฉีก MOU',
               'หลังเลือกตั้งใหม่ได้ผลเท่าเดิม ผู้บริหารทักษิประชาฉีก MOU ขั้วส้มแดงและลากไทยรักไทยไปเป็นฝ่ายค้าน หวังให้รัฐบาลก้าวไกลเหลือเสียงปริ่มน้ำแล้วล้ม'),
              ('ก.ย. ๒๗๓๗', 'อะตอมแยกตัวเป็นคนแรก', 'ฯพณฯ ศ.ดร.นพ.วิทยสิทธิ์ ประสิทธิ์ผล ย้ายไปก้าวไกล ทักษิประชาเหลือ ๘๖ คน'),
              ('ก.ย. ๒๗๓๗', 'ดร. ภาคิน ตั้งพรรคอุดมการณ์ใหม่',
               'ดร. ภาคิน เมธาปรีชากุล นำ ส.ส. ดาวเด่นนโยบาย ๓๕ คนแยกตัวมาก่อตั้งพรรค ทักษิประชาเหลือ ๕๑ คน'),
              ('หลังจากนั้น', 'ทักษิณย้ายตาม &mdash; เข้าร่วมรัฐบาล',
               'พล.ต.อ.ทักษิณ ชินวัตร ย้ายมาเป็น ส.ส. คนที่ ๓๖ และรองหัวหน้าพรรค พรรคเข้าร่วมรัฐบาล ทำให้ขั้วรัฐบาลกลับมาที่ ๓๑๗ เสียง ส่วนทักษิประชาเหลือ ๕๐ คน')]),
    ('note', '🧭 เหตุผลของการแยกตัว: การฉีก MOU เป็นการคำนวณการเมืองที่ผิดพลาดและขัดเจตนารมณ์ของประชาชนที่เพิ่งยืนยันผลเลือกตั้งเดิม '
             'ฝ่ายค้านที่มี ส.ส. ๕๐ คนแต่ขาดทีมทำงานจะตรวจสอบรัฐบาลได้ไม่ต่อเนื่อง และเมื่อฝ่ายค้านอ่อน ระบบถ่วงดุลทั้งระบบก็อ่อนตาม '
             '&mdash; ในสมาชิก ๘๖ คน มีคนที่โดดเด่นในงานสภาและนโยบายราว ๓๘ คน เมื่อ ๓๕ คนและทักษิณออกมา ทักษิประชาเหลือคนหลักเพียงสุดารัตน์กับสมคิด'),

    ('h', '💡 อุดมการณ์และบทบาท'),
    ('quote', '"อนาคตดี อุดมการณ์ใหม่ มุ่งนำไป สู่ชัยประชาชน"'),
    ('p', 'สโลแกนวาง "อนาคตดี" (ผลลัพธ์ที่จับต้องได้) คู่กับ "อุดมการณ์ใหม่" (การแยกตัวจากการเมืองแบบเกมอำนาจของพรรคเดิม) แล้วปิดด้วย "ชัยประชาชน" '
          '&mdash; ชัยชนะที่นับคือของประชาชน ไม่ใช่ของพรรค'),
    ('list', ['<strong>สายกลางแนวปฏิบัตินิยม</strong> &mdash; ยึด "การเมืองแห่งผลงาน" (Performance Politics) มากกว่าจุดยืนซ้าย&ndash;ขวา',
              '<strong>คานอำนาจจากภายในรัฐบาล</strong> &mdash; ทำให้ฝ่ายรัฐบาลมี ๓๑๗ เสียง เกินกึ่งหนึ่งแต่ไม่ถึง ๒ ใน ๓ ตรงกับข้อเรียกร้องเรื่องสมดุลของ ศนท.',
              '<strong>บรรทัดฐานใหม่</strong> &mdash; การแยกพรรคไม่ใช่การทรยศ เมื่อพรรคเดิมเป็นฝ่ายละทิ้งเจตจำนงของประชาชนก่อน',
              '<strong>คนรุ่นใหม่นำ คนมีประสบการณ์หนุน</strong> &mdash; หัวหน้าพรรคคือ ดร. ภาคิน ส่วนอดีตนายกฯ อย่างทักษิณเป็นรองหัวหน้าพรรค']),

    ('h', '📊 คะแนนนิยม (ก้าวหน้าโพล)'),
    ('table', ['ช่วง', 'ความนิยมพรรค', 'หมายเหตุ'], [
        ['ม.ค. ๒๗๓๖', '0.00%', 'ยังไม่ได้ตั้งพรรค'], ['ธ.ค. ๒๗๓๖', '1.84%', 'เริ่มติดโพลครั้งแรกหลังทักษิประชาฉีก MOU'],
        ['ส.ค. ๒๗๓๗', '3.16%', 'รายเดือน'], ['ก.ย. ๒๗๓๗', '8.84% &ndash; 8.97%', 'หลังตั้งพรรค (รายเดือน / รายไตรมาส)'],
        ['ต.ค. ๒๗๓๗ สัปดาห์ ๑', '13.16%', ''], ['ต.ค. ๒๗๓๗ สัปดาห์ ๒', '13.97%', ''],
        ['ต.ค. ๒๗๓๗ สัปดาห์ ๓', '<strong>14.91%</strong>', 'พรรคอันดับ ๒ ของประเทศ']]),
    ('p', 'ในโพลบุคคลที่ทำงานเยอะที่สุด ไตรมาส ๓/๒๗๓๗ (N=25,000) ฯพณฯ พล.ต.อ.ทักษิณ ชินวัตร ได้อันดับ ๒ ที่ 27.34% '
          'สูสีกับอันดับ ๑ (ธีรภัทร วัฒนากร 28.40%) &mdash; ปัจจัยหลักที่ดันพรรคขึ้นเป็นอันดับ ๒ ของประเทศอย่างรวดเร็ว'),

    ('h', '🎵 เพลงประจำพรรค'),
    ('raw', MUSIC_NEW, MUSIC_OLD),
    ('note', '🔗 การ์ดพรรคอยู่ในแถบ &ldquo;🗳️ พรรคการเมือง&rdquo; &middot; เหตุการณ์ทั้งหมดอยู่ในแถบ &ldquo;📣 การประท้วง &amp; ทิศทางใหม่ ๒๗๓๗&rdquo; &middot; ตำแหน่งในรัฐบาลอยู่ในแถบ &ldquo;🏛️ คณะรัฐมนตรี&rdquo;'),
]

NEW = f'<div id="{TID}" class="db-tab-content">\n' + tb.new_render(ICON, TITLE, LEAD, B) + '\n</div>\n'
OLD = f'\n<div id="{TID}" class="db-tab-content">\n' + tb.old_render(ICON, TITLE, LEAD, B, accent=('#fca5a5', '239,68,68')) + '\n</div>'
assert tb.balanced(NEW) and tb.balanced(OLD) and '%%' not in NEW + OLD

h = rd('src/hub.json'); assert TID not in h
anchor = '''        "id": "red-party-tab",
        "icon": "🔴",
        "label": "พรรคสีแดง"
      },'''
assert h.count(anchor) == 1
h = h.replace(anchor, anchor + f'\n      {{\n        "id": "{TID}",\n        "icon": "{BTN_IC}",\n        "label": "{BTN}"\n      }},')
json.loads(h); wr('src/hub.json', h); wr(f'src/tabs/{TID}.html', NEW)

s = rd('website_constitution.html'); assert TID not in s
btn = """switchTab('red-party-tab', this)" style="border-color:rgba(239,68,68,0.6);color:#f87171;">🔴 พรรคสีแดง</button>"""
assert s.count(btn) == 1
s = s.replace(btn, btn + f"""\n          <button class="db-tab-btn" onclick="switchTab('{TID}', this)" style="border-color:rgba(239,68,68,0.6);color:#fca5a5;">{BTN_IC} {BTN}</button>""")
p0 = s.index('<div id="red-party-tab"'); end = tb.div_span(s, p0)
assert s.index('<section id="history_and_pms"') < end < s.index('</section>', end)
s = s[:end] + OLD + s[end:]
assert s.count(f'id="{TID}"') == 1
wr('website_constitution.html', s)
print('ok tab')
