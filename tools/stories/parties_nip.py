# -*- coding: utf-8 -*-
"""Parties tab (2026-10-16): add พรรคอุดมการณ์ใหม่ (NIP) between ก้าวไกล and ทักษิประชา, make
รังสิมันต์ โรม head of ก้าวไกล, สุดารัตน์ head of ทักษิประชา (now opposition). Both sites.
Run from the repo root."""
import io, re, sys
sys.path.insert(0, 'tools')
import tab_blocks as tb

NIP_SEP = ('ปลายปี ๒๗๓๖ หลังการเลือกตั้งใหม่ได้ผลเท่าเดิมทุกพรรค ผู้บริหารพรรคทักษิประชาตัดสินใจ<strong>ฉีก MOU ขั้วส้มแดง</strong> และลากไทยรักไทยออกไปเป็นฝ่ายค้าน '
           'ด้วยหวังให้รัฐบาลก้าวไกลเหลือเสียงปริ่มน้ำแล้วล้ม &mdash; ส.ส. สายทำงานมองว่าเป็นการคำนวณการเมืองที่ผิดพลาด ขัดเจตนารมณ์ของประชาชนที่เพิ่งยืนยันผลเลือกตั้งเดิม '
           'และฝ่ายค้านแบบไร้ทิศทางจะทำให้ระบบตรวจสอบอ่อนแอ ส.ส. ดาวเด่นนโยบาย ๓๕ คนจึงแยกตัวตั้งพรรคอุดมการณ์ใหม่ (ก.ย. ๒๗๓๗) โดยมี ฯพณฯ พล.ต.อ.ทักษิณ ชินวัตร '
           'ย้ายตามมาเป็นคนที่ ๓๖ แล้วเข้าร่วมรัฐบาลรังสิมันต์ โรม เป็นขั้ว ๓๑๗ เสียง &mdash; ความนิยมพุ่งจาก 0% เป็น 14.91% ขึ้นเป็นพรรคอันดับ ๒ ของประเทศภายในไม่ถึง ๒ ปี')
NIP_SLOGAN = '"อนาคตดี อุดมการณ์ใหม่ มุ่งนำไป สู่ชัยประชาชน"'
NIP_ANALYSIS = ('สโลแกนวาง "อนาคตดี" (ผลลัพธ์ที่จับต้องได้) คู่กับ "อุดมการณ์ใหม่" (การแยกตัวจากการเมืองแบบเกมอำนาจของพรรคเดิม) แล้วปิดด้วย "ชัยประชาชน" '
                '&mdash; บอกว่าชัยชนะที่นับคือของประชาชน ไม่ใช่ของพรรค ในเชิงรัฐศาสตร์ อุดมการณ์ใหม่เป็นพรรคสายกลางแนวปฏิบัตินิยมที่ยึด "การเมืองแห่งผลงาน" '
                '(Performance Politics) อ้างความชอบธรรมจากการรักษาสัญญากับผู้เลือกตั้ง มากกว่าจุดยืนซ้าย&ndash;ขวา บทบาทเชิงระบบคือพรรคร่วมที่คานอำนาจจากภายในรัฐบาล '
                'ทำให้ฝ่ายรัฐบาลมี ๓๑๗ เสียง เกินกึ่งหนึ่งแต่ไม่ถึง ๒ ใน ๓ ตรงกับข้อเรียกร้องเรื่องสมดุลของ ศนท. และวางบรรทัดฐานว่าการแยกพรรคไม่ใช่การทรยศ '
                'เมื่อพรรคเดิมเป็นฝ่ายละทิ้งเจตจำนงของประชาชนก่อน')
NIP_LYRICS = 'เปลี่ยนความจริงใจ ให้เป็นผลงาน<br>นี่คือสัญญา เลือดเนื้อและศรัทธา<br>พรรคอุดมการณ์ใหม่ ก้าวไปเพื่อทุกคน!'
NIP_LEADER = ('ดร. ภาคิน เมธาปรีชากุล (หัวหน้าพรรค)</strong> &nbsp;|&nbsp; ฯพณฯ พล.ต.อ. ทักษิณ ชินวัตร (รองหัวหน้าพรรค &mdash; อดีตนายกฯ คนที่ ๔ และ ๓๐)'
              ' &nbsp;|&nbsp; ส.ส. ๓๖ คน &middot; พรรคร่วมรัฐบาล')

MF_LEAD_OLD = 'ศ.ดร.ปิยบุตร แสงกนกกุล (หัวหน้าพรรคคนปัจจุบัน)</strong> &nbsp;|&nbsp; อดีตหัวหน้าพรรค: '
MF_LEAD_NEW = ('รังสิมันต์ โรม (หัวหน้าพรรคคนปัจจุบัน)</strong> &nbsp;|&nbsp; นายกรัฐมนตรีคนปัจจุบัน: รังสิมันต์ โรม (นายกฯ คนที่ ๓๕ · พรรคก้าวไกล)'
               ' &nbsp;|&nbsp; อดีตหัวหน้าพรรค: ศ.ดร.ปิยบุตร แสงกนกกุล (อดีตนายกฯ คนที่ ๒๙), ')
TKP_LEAD_OLD = 'ศ.ดร.นพ.วิทยสิทธิ์ ประสิทธิ์ผล (ฯพณฯ) (หัวหน้าพรรค) | นายกรัฐมนตรีคนปัจจุบัน: รังสิมันต์ โรม (นายกฯ คนที่ ๓๕ · พรรคก้าวไกล)'
TKP_LEAD_NEW = 'สุดารัตน์ เกยุราพันธุ์ (หัวหน้าพรรคคนปัจจุบัน) | อดีตหัวหน้าพรรค: ศ.ดร.นพ.วิทยสิทธิ์ ประสิทธิ์ผล (ฯพณฯ) &mdash; ย้ายไปพรรคก้าวไกล ก.ย. ๒๗๓๗'
TKP_STAT_OLD = 'พรรคร่วมรัฐบาล (ขั้วส้มแดง) · ส่งสุดารัตน์ เกยุราพันธุ์ ชิงตำแหน่งนายกรัฐมนตรีในการเลือกตั้ง ๒๗๓๑'
TKP_STAT_NEW = 'ฝ่ายค้าน · ฉีก MOU ขั้วส้มแดงปลายปี ๒๗๓๖ · เหลือ ส.ส. ๕๐ คน หลัง ส.ส. ๓๖ คนแยกไปตั้งพรรคอุดมการณ์ใหม่'
RED_OLD = 'หัวหน้าพรรค: ศ.ดร.นพ.วิทยสิทธิ์ ประสิทธิ์ผล (ฯพณฯ) · พรรคร่วมรัฐบาล (ขั้วส้มแดง) · ส่งสุดารัตน์ เกยุราพันธุ์ ชิงนายกฯ ในการเลือกตั้ง ๒๗๓๑ · '
RED_NEW = 'หัวหน้าพรรค: สุดารัตน์ เกยุราพันธุ์ · ฝ่ายค้าน (ฉีก MOU ปลายปี ๒๗๓๖) · '


def one(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:50], s.count(a))
    return s.replace(a, b)


def mf_card(s):
    i = s.index('Move Forward Party (MFP)')
    chain = []
    for st in reversed([m.start() for m in re.finditer(r'<div\b', s[:i])]):
        e = tb.div_span(s, st)
        if e > i:
            chain.append((st, e))
        if len(chain) == 3:
            return chain[2]


def nip_from(card):
    c = card
    c = re.sub(r'<img src="images/logo_mf\.svg" alt="[^"]*"', '<img src="images/logo_nip.jpg" alt="พรรคอุดมการณ์ใหม่"', c)
    assert 'logo_nip.jpg' in c
    c = one(c, '>พรรคก้าวไกล</span>', '>พรรคอุดมการณ์ใหม่</span>', 'name')
    c = one(c, 'Move Forward Party (MFP)', 'New Ideology Party (NIP)', 'en')
    a = c.index('หัวหน้าพรรค/ผู้นำ:</strong>'); a = c.index('<strong', a); a = c.index('>', a) + 1; b = c.index('</span></div>', a)
    c = c[:a] + NIP_LEADER + c[b:]
    m = re.search(r'(<div[^>]*>)สืบทอดภารกิจผ่านพรรคส่งต่อ.*?(</div>)', c, re.S); assert m
    c = c[:m.start()] + m.group(1) + NIP_SEP + m.group(2) + c[m.end():]
    m = re.search(r'(<em[^>]*>)"การเมืองดี ปากท้องดี มีอนาคต".*?(</em>)', c, re.S); assert m
    c = c[:m.start()] + m.group(1) + NIP_SLOGAN + m.group(2) + c[m.end():]
    m = re.search(r'(วิเคราะห์เชิงอุดมการณ์และบทบาทรัฐศาสตร์:</strong>\s*<p[^>]*>).*?(</p>)', c, re.S); assert m
    c = c[:m.start()] + m.group(1) + NIP_ANALYSIS + m.group(2) + c[m.end():]
    c = one(c, 'เพลง "ก้าวไกลก้าวหน้า"', 'เพลง "อุดมการณ์ใหม่"', 'song')
    assert c.count('audio/mfp_kaoklai.mp3') == 3
    c = c.replace('audio/mfp_kaoklai.mp3', 'audio/nip_udomkan.mp3')
    m = re.search(r'(<div[^>]*font-style: ?italic[^>]*>)\s*ก้าวไกล ก้าวไปด้วยกัน.*?(</div>)', c, re.S); assert m
    c = c[:m.start()] + m.group(1) + '\n                  ' + NIP_LYRICS + '\n                ' + m.group(2) + c[m.end():]
    c = c.replace('#fb923c', '#f87171').replace('rgba(255,165,0,0.2)', 'rgba(248,113,113,0.25)')
    for bad in ('ก้าวไกลก้าวหน้า', 'ปิยบุตร', 'mfp_', 'logo_mf'):
        assert bad not in c, bad
    assert tb.balanced(c)
    return c


for f in ['src/tabs/parties-tab.html', 'website_constitution.html']:
    s = io.open(f, encoding='utf-8').read()
    assert 'New Ideology Party' not in s
    st, e = mf_card(s)
    assert 'Thaksipracha' in s[e:e + 6000] or 'ทักษิประชา' in s[e:e + 3000], 'next card is not ทักษิประชา'
    nip = nip_from(s[st:e])
    s = s[:e] + '\n\n          ' + nip + s[e:]
    s = one(s, MF_LEAD_OLD, MF_LEAD_NEW, 'mf lead')
    s = one(s, TKP_LEAD_OLD, TKP_LEAD_NEW, 'tkp lead')
    s = one(s, TKP_STAT_OLD, TKP_STAT_NEW, 'tkp status')
    if f.startswith('website'):
        s = one(s, RED_OLD, RED_NEW, 'red')
    io.open(f, 'w', encoding='utf-8', newline='').write(s)
    print('ok', f)
f = 'src/tabs/red-party-tab.html'
s = io.open(f, encoding='utf-8').read(); s = one(s, RED_OLD, RED_NEW, 'red'); io.open(f, 'w', encoding='utf-8', newline='').write(s); print('ok', f)
