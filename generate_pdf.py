import os
import re
import urllib.request
import subprocess
import sys

# Configure output encoding for Windows consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Paths
wd = r"c:\Users\ASUA\OneDrive\Documents\รัฐธรรมนุญจำลอง"
original_text_path = os.path.join(wd, "รัฐธรรมนูญ2540_original.txt")
html_output_path = os.path.join(wd, "constitution_2525.html")
base_pdf_name = "รัฐธรรมนูญ_๒๕๒๕_แก้ไขเพิ่มเติม"
pdf_output_path = os.path.join(wd, f"{base_pdf_name}.pdf")
pdf_output_path = os.path.join(wd, f"{base_pdf_name}.pdf")
if os.path.exists(pdf_output_path):
    try:
        with open(pdf_output_path, "ab") as f:
            pass
    except OSError:
        v = 1
        while True:
            candidate = os.path.join(wd, f"{base_pdf_name}_v{v}.pdf")
            if not os.path.exists(candidate):
                pdf_output_path = candidate
                break
            else:
                try:
                    with open(candidate, "ab") as f:
                        pass
                    pdf_output_path = candidate
                    break
                except OSError:
                    v += 1
garuda_img_path = os.path.join(wd, "Thai_Garuda_emblem.svg")

# 1. Read original text
if not os.path.exists(original_text_path):
    print(f"Error: Original text file not found at {original_text_path}")
    sys.exit(1)

with open(original_text_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

# Normalize line endings and trailing spaces
lines = [line.rstrip() for line in raw_text.splitlines()]
text = "\n".join(lines)

# 2. Renaming B.E. years:
# - Main year: B.E. 2540 -> B.E. 2525 (๒๕๔๐ -> ๒๕๒๕)
# - Previous constitutions: B.E. 2539 & 2534 -> B.E. 2445 (๒๕๓๙ & ๒๕๓๔ -> ๒๔๔๕)
text = text.replace("๒๕๔๐", "๒๕๒๕")
text = text.replace("๒๕๓๙", "๒๔๔๕")
text = text.replace("๒๕๓๔", "๒๔๔๕")

# Remove the line "เป็นปีที่ ๕๒ ในรัชกาลปัจจุบัน" completely
text = text.replace("\nเป็นปีที่ ๕๒ ในรัชกาลปัจจุบัน", "")

# 3. Apply PM term limit changes
old_art_201_pattern = "\n".join([
    "มาตรา ๒๐๑  พระมหากษัตริย์ทรงแต่งตั้งนายกรัฐมนตรีคนหนึ่งและรัฐมนตรีอื่นอีกไม่เกินสามสิบห้าคนประกอบเป็นคณะรัฐมนตรี มีหน้าที่บริหารราชการแผ่นดิน",
    "นายกรัฐมนตรีต้องแต่งตั้งจากสมาชิกสภาผู้แทนราษฎรหรือผู้เคยเป็นสมาชิกสภาผู้แทนราษฎรแต่พ้นจากสมาชิกภาพตามมาตรา ๑๑๘ (๗) ในอายุของสภาผู้แทนราษฎรชุดเดียวกัน",
    "ให้ประธานสภาผู้แทนราษฎรเป็นผู้ลงนามรับสนองพระบรมราชโองการแต่งตั้งนายกรัฐมนตรี"
])

new_art_201_replacement = "\n".join([
    "มาตรา ๒๐๑  พระมหากษัตริย์ทรงแต่งตั้งนายกรัฐมนตรีคนหนึ่งและรัฐมนตรีอื่นอีกไม่เกินสามสิบห้าคนประกอบเป็นคณะรัฐมนตรี มีหน้าที่บริหารราชการแผ่นดิน",
    "นายกรัฐมนตรีต้องแต่งตั้งจากสมาชิกสภาผู้แทนราษฎรหรือผู้เคยเป็นสมาชิกสภาผู้แทนราษฎรแต่พ้นจากสมาชิกภาพตามมาตรา ๑๑๘ (๗) ในอายุของสภาผู้แทนราษฎรชุดเดียวกัน",
    "นายกรัฐมนตรีมีวาระการดำรงตำแหน่งคราวละสี่ปี และจะดำรงตำแหน่งรวมกันแล้วเกินสี่วาระมิได้ ไม่ว่าจะเป็นการดำรงตำแหน่งติดต่อกันหรือไม่",
    "ให้ประธานสภาผู้แทนราษฎรเป็นผู้ลงนามรับสนองพระบรมราชโองการแต่งตั้งนายกรัฐมนตรี"
])

old_art_216_pattern = "\n".join([
    "มาตรา ๒๑๖  ความเป็นรัฐมนตรีสิ้นสุดลงเฉพาะตัว เมื่อ",
    "(๑) ตาย",
    "(๒) ลาออก",
    "(๓) ขาดคุณสมบัติหรือมีลักษณะต้องห้ามตามมาตรา ๒๐๖",
    "(๔) ต้องคำพิพากษาให้จำคุก",
    "(๕) สภาผู้แทนราษฎรมีมติไม่ไว้วางใจตามมาตรา ๑๘๕ หรือมาตรา ๑๘๖",
    "(๖) กระทำการอันต้องห้ามตามมาตรา ๒๐๘ หรือมาตรา ๒๐๙",
    "(๗) มีพระบรมราชโองการตามมาตรา ๒๑๗",
    "(๘) วุฒิสภามีมติตามมาตรา ๓๐๗ ให้ถอดถอนออกจากตำแหน่ง",
    "ให้นำบทบัญญัติมาตรา ๙๖ และมาตรา ๙๗ มาใช้บังคับกับการสิ้นสุดของความเป็นรัฐมนตรีตาม (๒) (๓) (๔) หรือ (๖)"
])

new_art_216_replacement = "\n".join([
    "มาตรา ๒๑๖  ความเป็นรัฐมนตรีสิ้นสุดลงเฉพาะตัว เมื่อ",
    "(๑) ตาย",
    "(๒) ลาออก",
    "(๓) ขาดคุณสมบัติหรือมีลักษณะต้องห้ามตามมาตรา ๒๐๖",
    "(๔) ต้องคำพิพากษาให้จำคุก",
    "(๕) สภาผู้แทนราษฎรมีมติไม่ไว้วางใจตามมาตรา ๑๘๕ หรือมาตรา ๑๘๖",
    "(๖) กระทำการอันต้องห้ามตามมาตรา ๒๐๘ หรือมาตรา ๒๐๙",
    "(๗) มีพระบรมราชโองการตามมาตรา ๒๑๗",
    "(๘) วุฒิสภามีมติตามมาตรา ๓๐๗ ให้ถอดถอนออกจากตำแหน่ง",
    "(๙) ดำรงตำแหน่งครบกำหนดตามมาตรา ๒๐๑ วรรคสาม",
    "ให้นำบทบัญญัติมาตรา ๙๖ และมาตรา ๙๗ มาใช้บังคับกับการสิ้นสุดของความเป็นรัฐมนตรีตาม (๒) (๓) (๔) หรือ (๖)"
])

text = text.replace(old_art_201_pattern, new_art_201_replacement)
text = text.replace(old_art_216_pattern, new_art_216_replacement)

# 4. Apply Democratization and Monarchy Protection Revisions
# A. Article 3
old_art_3 = "มาตรา ๓  อำนาจอธิปไตยเป็นของปวงชนชาวไทย พระมหากษัตริย์ผู้ทรงเป็นประมุขทรงใช้อำนาจนั้นทางรัฐสภา คณะรัฐมนตรี และศาล ตามบทบัญญัติแห่งรัฐธรรมนูญนี้"
new_art_3 = "มาตรา ๓  อำนาจอธิปไตยเป็นของปวงชนชาวไทย ปวงชนชาวไทยทรงใช้อำนาจอธิปไตยได้โดยตรง หรือทางรัฐสภา คณะรัฐมนตรี และศาล ตามบทบัญญัติแห่งรัฐธรรมนูญนี้"
text = text.replace(old_art_3, new_art_3)

# B. Article 8
old_art_8_pattern = "\n".join([
    "มาตรา ๘  องค์พระมหากษัตริย์ทรงดำรงอยู่ในฐานะอันเป็นที่เคารพสักการะ ผู้ใดจะละเมิดมิได้",
    "ผู้ใดจะกล่าวหาหรือฟ้องร้องพระมหากษัตริย์ in ทางใด ๆ มิได้" # wait, make sure it matches
])
# Let's verify what we have in text.
# The original text was 'ผู้ใดจะกล่าวหาหรือฟ้องร้องพระมหากษัตริย์ในทางใด ๆ มิได้'
old_art_8_pattern = "\n".join([
    "มาตรา ๘  องค์พระมหากษัตริย์ทรงดำรงอยู่ในฐานะอันเป็นที่เคารพสักการะ ผู้ใดจะละเมิดมิได้",
    "ผู้ใดจะกล่าวหาหรือฟ้องร้องพระมหากษัตริย์ในทางใด ๆ มิได้"
])
new_art_8_replacement = "\n".join([
    "มาตรา ๘  องค์พระมหากษัตริย์ทรงดำรงอยู่ในฐานะอันเป็นที่เคารพสักการะ ผู้ใดจะละเมิดมิได้",
    "การติชม การวิพากษ์วิจารณ์ หรือการแสดงความคิดเห็นเกี่ยวกับสถาบันพระมหากษัตริย์หรือองค์พระมหากษัตริย์โดยสุจริต ไม่ว่าจะด้วยความรุนแรงระดับใด ย่อมเป็นสิทธิและเสรีภาพของประชาชนและไม่ถือเป็นความผิดทางกฎหมาย",
    "การดำเนินการทางกฎหมายเกี่ยวกับการละเมิดสถาบันพระมหากษัตริย์ ให้กระทำได้เฉพาะในกรณีที่มีการกระทำอันเป็นการใช้กำลังประทุษร้าย หรือส่อเจตนาล้มล้างหรือทำลายล้างสถาบันพระมหากษัตริย์อย่างชัดแจ้งเท่านั้น",
    "ผู้ใดจะกล่าวหาหรือฟ้องร้องพระมหากษัตริย์ในทางใด ๆ มิได้"
])
text = text.replace(old_art_8_pattern, new_art_8_replacement)

# C. Article 170
old_art_170_text = "มาตรา ๑ ๗ ๐"
old_art_170_text = "มาตรา ๑  และในขั้นรับหลักการไม่เป็นร่างพระราชบัญญัติเกี่ยวด้วยการเงิน แต่สภาผู้แทนราษฎรได้แก้ไขเพิ่มเ"
# Wait, let's make sure we replace the exact original text:
old_art_170_text = "มาตรา ๑๗๐  ผู้มีสิทธิเลือกตั้งไม่น้อยกว่าห้าหมื่นคน มีสิทธิเข้าชื่อร้องขอต่อประธานรัฐสภาเพื่อให้รัฐสภาพิจารณากฎหมายตามที่กำหนดในหมวด ๓ และหมวด ๕ แห่งรัฐธรรมนูญนี้"
# But wait, in step 2 we already replaced "๒๕๔๐" with "๒๕๒๕", but did it affect article 170?
# In article 170, did it contain any B.E. year? No, 'มาตรา ๑๗๐  ผู้มีสิทธิเลือกตั้งไม่น้อยกว่าห้าหมื่นคน...' does not contain any B.E. year.
new_art_170_text = "มาตรา ๑๗๐  ผู้มีสิทธิเลือกตั้งไม่น้อยกว่าห้าพันคน มีสิทธิเข้าชื่อร้องขอต่อประธานรัฐสภาเพื่อให้รัฐสภาพิจารณากฎหมายในเรื่องใด ๆ"
text = text.replace(old_art_170_text, new_art_170_text)

# D. Article 214
old_art_214_a = "มาตรา ๒๑๔  ในกรณีที่คณะรัฐมนตรีเห็นว่ากิจการในเรื่องใดอาจกระทบถึงประโยชน์ได้เสียของประเทศชาติหรือประชาชน นายกรัฐมนตรีโดยความเห็นชอบของคณะรัฐมนตรีอาจปรึกษาประธานสภาผู้แทนราษฎรและประธานวุฒิสภาเพื่อประกาศในราชกิจจานุเบกษาให้มีการออกเสียงประชามติได้"
new_art_214_a = "มาตรา ๒๑๔  ในกรณีที่คณะรัฐมนตรีเห็นว่ากิจการในเรื่องใดอาจกระทบถึงประโยชน์ได้เสียของประเทศชาติหรือประชาชน นายกรัฐมนตรีโดยความเห็นชอบของคณะรัฐมนตรีอาจปรึกษาประธานสภาผู้แทนราษฎรและประธานวุฒิสภาเพื่อประกาศในราชกิจจานุเบกษาให้มีการออกเสียงประชามติได้ หรือในกรณีที่ประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าหมื่นคนร่วมกันเข้าชื่อร้องขอ นายกรัฐมนตรีต้องจัดให้มีการออกเสียงประชามติ"
text = text.replace(old_art_214_a, new_art_214_a)

old_art_214_b = "การออกเสียงประชามติตามมาตรานี้ให้มีผลเป็นเพียงการให้คำปรึกษาแก่คณะรัฐมนตรีในเรื่องนั้น"
new_art_214_b = "การออกเสียงประชามติตามมาตรานี้ให้มีผลผูกพันคณะรัฐมนตรี รัฐสภา และหน่วยงานของรัฐในการดำเนินการในเรื่องนั้น"
text = text.replace(old_art_214_b, new_art_214_b)

# E. Article 304
old_art_304 = "มาตรา ๓๐๔  สมาชิกสภาผู้แทนราษฎรจำนวนไม่น้อยกว่าหนึ่งในสี่ของจำนวนสมาชิกทั้งหมดเท่าที่มีอยู่ของสภาผู้แทนราษฎร หรือประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าหมื่นคน มีสิทธิเข้าชื่อร้องขอต่อประธานวุฒิสภาเพื่อให้วุฒิสภามีมติตามมาตรา ๓๐๗ ให้ถอดถอนบุคคลตามมาตรา ๓๐๓ ออกจากตำแหน่งได้"
new_art_304 = "มาตรา ๓๐๔  สมาชิกสภาผู้แทนราษฎรจำนวนไม่น้อยกว่าหนึ่งในสี่ของจำนวนสมาชิกทั้งหมดเท่าที่มีอยู่ของสภาผู้แทนราษฎร หรือประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าพันคน มีสิทธิเข้าชื่อร้องขอต่อประธานวุฒิสภาเพื่อให้วุฒิสภามีมติตามมาตรา ๓๐๗ ให้ถอดถอนบุคคลตามมาตรา ๓๐๓ ออกจากตำแหน่งได้"
text = text.replace(old_art_304, new_art_304)

# G. Anti-Coup / Right to Resist (Article 63 enhancement)
old_art_63 = "มาตรา ๖๓  บุคคลจะใช้สิทธิและเสรีภาพตามรัฐธรรมนูญเพื่อล้มล้างการปกครองระบอบประชาธิปไตยอันมีพระมหากษัตริย์ทรงเป็นประมุขตามรัฐธรรมนูญนี้ หรือเพื่อให้ได้มาซึ่งอำนาจในการปกครองประเทศโดยวิธีการซึ่งมิได้เป็นไปตามวิถีทางที่บัญญัติไว้ในรัฐธรรมนูญนี้ มิได้"
new_art_63 = "\n".join([
    "มาตรา ๖๓  บุคคลจะใช้สิทธิและเสรีภาพตามรัฐธรรมนูญเพื่อล้มล้างการปกครองระบอบประชาธิปไตยอันมีพระมหากษัตริย์ทรงเป็นประมุขตามรัฐธรรมนูญนี้ หรือเพื่อให้ได้มาซึ่งอำนาจในการปกครองประเทศโดยวิธีการซึ่งมิได้เป็นไปตามวิถีทางที่บัญญัติไว้ในรัฐธรรมนูญนี้ มิได้",
    "การยึดอำนาจการปกครอง การรัฐประหาร การปฏิวัติ หรือการกระทำใด ๆ เพื่อให้ได้มาซึ่งอำนาจในการปกครองประเทศโดยวิธีการซึ่งมิได้เป็นไปตามวิถีทางที่บัญญัติไว้ในรัฐธรรมนูญนี้ ย่อมเป็นโมฆะและไม่มีผลทางกฎหมายตั้งแต่ต้น ไม่ว่าจะมีบทบัญญัติ ประกาศ หรือคำสั่งใด ๆ มารับรองในภายหลัง",
    "ประชาชนย่อมมีสิทธิต่อต้านโดยสันติวิธีซึ่งการกระทำใด ๆ ที่เป็นไปเพื่อให้ได้มาซึ่งอำนาจในการปกครองประเทศโดยวิธีการซึ่งมิได้เป็นไปตามวิถีทางที่บัญญัติไว้ในรัฐธรรมนูญนี้ และข้าราชการ ทหาร ตำรวจ และเจ้าหน้าที่ของรัฐทุกประเภท มีหน้าที่ปฏิเสธคำสั่งของผู้ยึดอำนาจ ผู้ใดปฏิเสธคำสั่งดังกล่าวโดยสุจริตย่อมไม่มีความผิดทางกฎหมาย",
    "ผู้ใดร่วมกระทำการยึดอำนาจหรือรัฐประหาร ต้องรับโทษอาญาฐานกบฏ โดยไม่มีอายุความ และไม่อาจได้รับการนิรโทษกรรมไม่ว่าในกรณีใด ๆ"
])
text = text.replace(old_art_63, new_art_63)

# H. Citizen Recall of Individual MPs/Senators (add after Article 170)
citizen_recall_article = "\n\nมาตรา ๑๗๐/๑  ประชาชนผู้มีสิทธิเลือกตั้งในเขตเลือกตั้งใดจำนวนไม่น้อยกว่าหนึ่งในห้าของจำนวนผู้มีสิทธิเลือกตั้งในเขตนั้น มีสิทธิร่วมกันลงชื่อเพื่อยื่นคำร้องให้มีการออกเสียงเพื่อถอดถอน (Recall) สมาชิกสภาผู้แทนราษฎรผู้แทนเขตเลือกตั้งนั้น ออกจากตำแหน่งก่อนครบวาระได้\nเมื่อได้รับคำร้องตามวรรคหนึ่ง ให้คณะกรรมการการเลือกตั้งจัดให้มีการออกเสียงถอดถอนภายในเก้าสิบวัน หากผลการออกเสียงมีเสียงข้างมากของผู้มาใช้สิทธิเห็นชอบให้ถอดถอน ให้ถือว่าสมาชิกสภาผู้แทนราษฎรผู้นั้นพ้นจากตำแหน่งทันที และให้จัดการเลือกตั้งซ่อมภายในสี่สิบห้าวัน\nให้นำบทบัญญัติมาตรานี้มาใช้บังคับแก่สมาชิกวุฒิสภาด้วยโดยอนุโลม"
# Insert right after the new Article 170 text
new_art_170_with_recall = new_art_170_text + citizen_recall_article
text = text.replace(new_art_170_text, new_art_170_with_recall)

# I. Participatory Budgeting & Anti-Monopoly (add to Chapter 14)
ch_14_extra = "\n \nมาตรา ๓๑๓/๗ ทวิ  ให้จัดสรรงบประมาณแผ่นดินส่วนหนึ่งไม่น้อยกว่าร้อยละห้าของงบประมาณรายจ่ายประจำปี เป็น \"งบประมาณภาคประชาชน\" ให้ประชาชนในแต่ละท้องถิ่นมีสิทธิร่วมกันกำหนดว่าจะนำงบประมาณส่วนนี้ไปใช้ในโครงการใดในพื้นที่ของตน โดยวิธีการออกเสียงโดยตรงของประชาชนในท้องถิ่นนั้น\n \nมาตรา ๓๑๓/๗ ตรี  ห้ามมิให้ผู้ประกอบกิจการรายใดหรือกลุ่มผู้ประกอบกิจการรายใดผูกขาดหรือครองตลาดในสินค้าหรือบริการที่จำเป็นต่อการดำรงชีวิตของประชาชน รัฐต้องส่งเสริมการแข่งขันเสรีและเป็นธรรม และป้องกันการรวมศูนย์อำนาจทางเศรษฐกิจโดยกลุ่มทุนขนาดใหญ่\nประชาชนผู้บริโภคหรือผู้ประกอบการรายย่อยจำนวนไม่น้อยกว่าห้าพันคน มีสิทธิร่วมกันเข้าชื่อเสนอเรื่องต่อศาลเพื่อขอให้มีคำสั่งยุติการผูกขาดหรือครองตลาดที่ไม่เป็นธรรม\n \nมาตรา ๓๑๓/๗ จัตวา  รัฐต้องจัดให้มีระบบสวัสดิการถ้วนหน้าแก่ประชาชนทุกคนอย่างเท่าเทียม อันรวมถึงการรักษาพยาบาลที่ไม่มีค่าใช้จ่ายอย่างมีคุณภาพ เบี้ยเลี้ยงผู้สูงอายุที่เพียงพอต่อการดำรงชีพ การดูแลเด็กและเยาวชน และสวัสดิการการว่างงาน โดยรัฐจะอ้างข้อจำกัดงบประมาณเพื่อปฏิเสธสิทธิขั้นพื้นฐานเหล่านี้ของประชาชนมิได้"

# J. Digital Rights & Privacy (add to Chapter 3 rights section after Article 58 enhancement)
old_art_58 = "มาตรา ๕๘  บุคคลย่อมมีสิทธิได้รับทราบข้อมูลหรือข่าวสารสาธารณะในครอบครองของหน่วยราชการ หน่วยงานของรัฐ รัฐวิสาหกิจ หรือราชการส่วนท้องถิ่น เว้นแต่การเปิดเผยข้อมูลนั้นจะกระทบต่อความมั่นคงของรัฐ ความปลอดภัยของประชาชน หรือส่วนได้เสียอันพึงได้รับความคุ้มครองของบุคคลอื่น  ทั้งนี้ ตามที่กฎหมายบัญญัติ"
new_art_58 = "\n".join([
    old_art_58,
    " ",
    "มาตรา ๕๘/๑  บุคคลย่อมมีสิทธิในความเป็นส่วนตัวทางดิจิทัล สิทธิในข้อมูลส่วนบุคคลของตน และเสรีภาพในการใช้เครือข่ายสารสนเทศ รัฐจะสอดแนม ดักฟัง เก็บรวบรวม หรือใช้ข้อมูลส่วนบุคคลของประชาชนมิได้ เว้นแต่โดยอาศัยอำนาจตามคำสั่งศาลเฉพาะรายกรณี",
    "รัฐจะปิดกั้น จำกัด หรือตัดการเข้าถึงเครือข่ายสารสนเทศของประชาชนมิได้ เว้นแต่โดยคำสั่งศาลเป็นการเฉพาะ",
    " ",
    "มาตรา ๕๘/๒  ผู้แจ้งเบาะแสการทุจริต การละเมิดกฎหมาย หรือการกระทำอันมิชอบของเจ้าหน้าที่ของรัฐ ย่อมได้รับความคุ้มครองตามกฎหมาย ห้ามมิให้หน่วยงานของรัฐหรือผู้ใดกลั่นแกล้ง ข่มขู่ ลงโทษ ปลด ย้าย ลดตำแหน่ง หรือดำเนินการใด ๆ อันเป็นผลร้ายต่อผู้แจ้งเบาะแสที่กระทำโดยสุจริต",
    "รัฐต้องจัดให้มีกลไกรับแจ้งเบาะแสที่ปกปิดตัวตนของผู้แจ้งได้อย่างเคร่งครัด และจัดให้มีค่าตอบแทนที่เหมาะสมแก่ผู้แจ้งเบาะแสที่ส่งผลให้ดำเนินคดีทุจริตได้สำเร็จ"
])
text = text.replace(old_art_58, new_art_58)

# K. Citizen-initiated Constitutional Amendments (modify Article 313)
old_art_313_clause1 = "(๑) ญัตติขอแก้ไขเพิ่มเติมต้องมาจากคณะรัฐมนตรี หรือจากสมาชิกสภาผู้แทนราษฎรมีจำนวนไม่น้อยกว่าหนึ่งในห้าของจำนวนสมาชิกทั้งหมดเท่าที่มีอยู่ของสภาผู้แทนราษฎร หรือจากสมาชิกสภาผู้แทนราษฎรและสมาชิกวุฒิสภามีจำนวนไม่น้อยกว่าหนึ่งในห้าของจำนวนสมาชิกทั้งหมดเท่าที่มีอยู่ของทั้งสองสภา สมาชิกสภาผู้แทนราษฎรจะเสนอหรือร่วมเสนอญัตติดังกล่าวได้เมื่อพรรคการเมืองที่สมาชิกสภาผู้แทนราษฎรนั้นสังกัดมีมติให้เสนอได้"
new_art_313_clause1 = "(๑) ญัตติขอแก้ไขเพิ่มเติมต้องมาจากคณะรัฐมนตรี หรือจากสมาชิกสภาผู้แทนราษฎรมีจำนวนไม่น้อยกว่าหนึ่งในห้าของจำนวนสมาชิกทั้งหมดเท่าที่มีอยู่ของสภาผู้แทนราษฎร หรือจากสมาชิกสภาผู้แทนราษฎรและสมาชิกวุฒิสภามีจำนวนไม่น้อยกว่าหนึ่งในห้าของจำนวนสมาชิกทั้งหมดเท่าที่มีอยู่ของทั้งสองสภา หรือจากประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าหมื่นคนร่วมกันเข้าชื่อเสนอ สมาชิกสภาผู้แทนราษฎรจะเสนอหรือร่วมเสนอญัตติดังกล่าวได้เมื่อพรรคการเมืองที่สมาชิกสภาผู้แทนราษฎรนั้นสังกัดมีมติให้เสนอได้\n \nการแก้ไขเพิ่มเติมรัฐธรรมนูญในหมวด ๑ บททั่วไป หมวด ๒ พระมหากษัตริย์ หมวด ๑๖ องค์กรอิสระ หรือหมวดพิเศษ จะกระทำมิได้ เว้นแต่จะได้รับความเห็นชอบของประชาชนผ่านการออกเสียงประชามติ ซึ่งต้องได้รับคะแนนเสียงเห็นชอบจากประชาชนด้วยเกณฑ์และสัดส่วนคะแนนเสียงเดียวกับการยกเลิกรัฐธรรมนูญนี้"
text = text.replace(old_art_313_clause1, new_art_313_clause1)

# F. Chapters 13-16: Conflict of Interest, Country Reform, Prosecutor, Independent Organs
# Extract sections
ec_start = text.find("ส่วนที่ ๔\nคณะกรรมการการเลือกตั้ง")
ec_end = text.find("ส่วนที่ ๕\nบทที่ใช้แก่สภาทั้งสอง")
ec_text = text[ec_start:ec_end].strip()

ombuds_start = text.find("ส่วนที่ ๗\nผู้ตรวจการแผ่นดินของรัฐสภา")
ombuds_end = text.find("ส่วนที่ ๘\nคณะกรรมการสิทธิมนุษยชนแห่งชาติ")
ombuds_text = text[ombuds_start:ombuds_end].strip()

hr_start = text.find("ส่วนที่ ๘\nคณะกรรมการสิทธิมนุษยชนแห่งชาติ")
hr_end = text.find("หมวด ๗\nคณะรัฐมนตรี")
hr_text = text[hr_start:hr_end].strip()

nacc_start = text.find("ส่วนที่ ๒\nคณะกรรมการป้องกันและปราบปรามการทุจริตแห่งชาติ")
nacc_end = text.find("ส่วนที่ ๓\nการถอดถอนจากตำแหน่ง")
nacc_text = text[nacc_start:nacc_end].strip()

audit_start = text.find("หมวด ๑๑\nการตรวจเงินแผ่นดิน")
audit_end = text.find("หมวด ๑๒\nการแก้ไขเพิ่มเติมรัฐธรรมนูญ")
audit_text = text[audit_start:audit_end].strip()

# Create modified texts for the moved sections
ec_text_new = ec_text.replace("ส่วนที่ ๔\nคณะกรรมการการเลือกตั้ง", "ส่วนที่ ๒\nคณะกรรมการการเลือกตั้ง")
ombuds_text_new = ombuds_text.replace("ส่วนที่ ๗\nผู้ตรวจการแผ่นดินของรัฐสภา", "ส่วนที่ ๓\nผู้ตรวจการแผ่นดิน")
hr_text_new = hr_text.replace("ส่วนที่ ๘\nคณะกรรมการสิทธิมนุษยชนแห่งชาติ", "ส่วนที่ ๔\nคณะกรรมการสิทธิมนุษยชนแห่งชาติ")
nacc_text_new = nacc_text.replace("ส่วนที่ ๒\nคณะกรรมการป้องกันและปราบปรามการทุจริตแห่งชาติ", "ส่วนที่ ๕\nคณะกรรมการป้องกันและปราบปรามการทุจริตแห่งชาติ")
audit_text_new = audit_text.replace("หมวด ๑๑\nการตรวจเงินแผ่นดิน", "ส่วนที่ ๖\nคณะกรรมการตรวจเงินแผ่นดิน")

# Replace in original locations with redirection notes
text = text.replace(ec_text, "ส่วนที่ ๔\nคณะกรรมการการเลือกตั้ง\n\nมาตรา ๑๓๖ ถึง มาตรา ๑๔๘ (ย้ายไปบัญญัติไว้ในหมวด ๑๖ องค์กรอิสระ)")
text = text.replace(ombuds_text, "ส่วนที่ ๗\nผู้ตรวจการแผ่นดินของรัฐสภา\n\nมาตรา ๑๙๖ ถึง มาตรา ๑๙๘ (ย้ายไปบัญญัติไว้ในหมวด ๑๖ องค์กรอิสระ)")
text = text.replace(hr_text, "ส่วนที่ ๘\nคณะกรรมการสิทธิมนุษยชนแห่งชาติ\n\nมาตรา ๑๙๙ ถึง มาตรา ๒๐๐ (ย้ายไปบัญญัติไว้ในหมวด ๑๖ องค์กรอิสระ)")
text = text.replace(nacc_text, "ส่วนที่ ๒\nคณะกรรมการป้องกันและปราบปรามการทุจริตแห่งชาติ\n\nมาตรา ๒๙๗ ถึง มาตรา ๓๐๒ (ย้ายไปบัญญัติไว้ในหมวด ๑๖ องค์กรอิสระ)")
text = text.replace(audit_text, "หมวด ๑๑\nการตรวจเงินแผ่นดิน\n\nมาตรา ๓๑๒ (ย้ายไปบัญญัติไว้ในหมวด ๑๖ องค์กรอิสระ)")

# Chapters 13-16 text
ch_13 = """หมวด ๑๓
การขัดกันแห่งผลประโยชน์
 
มาตรา ๓๑๓/๑  นายกรัฐมนตรี รัฐมนตรี สมาชิกสภาผู้แทนราษฎร และสมาชิกวุฒิสภา จะต้องไม่ดำรงตำแหน่งหรือมีส่วนเกี่ยวข้องกับการขัดกันแห่งผลประโยชน์ใด ๆ ไม่ว่าจะโดยทางตรงหรือทางอ้อม โดยห้ามมิให้ถือหุ้น หรือเป็นคู่สัญญากับหน่วยงานของรัฐ หรือใช้อำนาจในตำแหน่งหน้าที่เข้าแทรกแซง เอื้อประโยชน์ หรือมีส่วนได้เสียในกิจการของรัฐเพื่อประโยชน์ส่วนตัว พรรคการเมือง หรือพวกพ้อง
 
มาตรา ๓๑๓/๒  ผู้ดำรงตำแหน่งตามมาตรา ๓๑๓/๑ และข้าราชการระดับสูง ต้องแสดงบัญชีแสดงรายการทรัพย์สินและหนี้สิน ตลอดจนแบบแสดงรายการภาษีเงินได้บุคคลธรรมดาย้อนหลังห้าปี โดยให้เปิดเผยข้อมูลดังกล่าวต่อสาธารณะทางระบบเครือข่ายสารสนเทศอย่างโปร่งใส เพื่อให้ประชาชนทั่วไปสามารถเข้าถึง ตรวจสอบ และดาวน์โหลดข้อมูลได้โดยสะดวกโดยไม่มีค่าใช้จ่าย
 
มาตรา ๓๑๓/๓  ประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าพันคน มีสิทธิเข้าชื่อร่วมกันเสนอเรื่องต่อศาลรัฐธรรมนูญเพื่อวินิจฉัยให้ผู้ดำรงตำแหน่งทางการเมืองที่กระทำการฝ่าฝืนบทบัญญัติในหมวดนี้ พ้นจากตำแหน่ง และให้ตัดสิทธิในการดำรงตำแหน่งทางการเมืองตลอดชีวิต"""

ch_14 = """หมวด ๑๔
การปฏิรูปประเทศ
 
มาตรา ๓๑๓/๔  การปฏิรูปประเทศต้องมีเป้าหมายเพื่อกระจายอำนาจสู่ท้องถิ่น การลดความเหลื่อมล้ำทางเศรษฐกิจและสังคม การสร้างความเป็นธรรมในกระบวนการยุติธรรม และการส่งเสริมเสรีภาพและการมีส่วนร่วมของประชาชนในการกำหนดอนาคตของประเทศอย่างแท้จริง
 
มาตรา ๓๑๓/๕  ให้ดำเนินการปฏิรูปที่ดินทำกินและการจัดสรรทรัพยากรธรรมชาติอย่างเป็นธรรม โดยรัฐต้องสนับสนุนการกระจายถือครองที่ดิน และป้องกันการผูกขาดในที่ดินและทรัพยากรธรรมชาติทุกรูปแบบ เพื่อประโยชน์แก่ประชาชนและเกษตรกรรายย่อย
 
มาตรา ๓๑๓/๖  การปฏิรูปการศึกษาต้องมุ่งเน้นการพัฒนาผู้เรียนให้มีความคิดสร้างสรรค์ คิดวิเคราะห์ มีเสรีภาพในการเรียนรู้ และรัฐต้องจัดให้มีการศึกษาที่มีคุณภาพและไม่มีค่าใช้จ่ายตั้งแต่ระดับอนุบาลจนถึงระดับปริญญาตรี
 
มาตรา ๓๑๓/๗  ประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าหมื่นคน มีสิทธิร่วมกันเข้าชื่อเพื่อเสนอ "ร่างแผนปฏิรูปประเทศภาคประชาชน" ต่อรัฐสภา และให้รัฐสภาจัดลำดับความสำคัญพิจารณาเป็นเรื่องเร่งด่วน โดยหากผ่านความเห็นชอบในการออกเสียงประชามติ ให้แผนปฏิรูปดังกล่าวมีผลบังคับใช้ตามกฎหมายโดยมีศักดิ์เหนือกฎเกณฑ์และแผนงานของหน่วยงานรัฐทั้งปวง"""

ch_15 = """หมวด ๑๕
องค์กรอัยการ
 
มาตรา ๓๑๓/๘  องค์กรอัยการเป็นองค์กรตามรัฐธรรมนูญที่มีความเป็นอิสระในการปฏิบัติหน้าที่ฟ้องคดีอาญา พิทักษ์ผลประโยชน์ของสาธารณะ และอำนวยความยุติธรรมให้แก่ประชาชน พนักงานอัยการย่อมมีอิสระในการพิจารณาสั่งคดีและการปฏิบัติหน้าที่ให้เป็นไปตามรัฐธรรมนูญและกฎหมาย โดยปราศจากการแทรกแซงจากคณะรัฐมนตรี รัฐสภา หรือหน่วยงานอื่นใดของรัฐ
 
มาตรา ๓๑๓/๙  ให้มี "คณะกรรมการอัยการ" (ก.อ.) ทำหน้าที่บริหารงานบุคคลและควบคุมการทำงานของพนักงานอัยการ ประกอบด้วยประธานกรรมการคนหนึ่ง และกรรมการซึ่งมาจากผู้แทนพนักงานอัยการ และกรรมการผู้ทรงคุณวุฒิภาคประชาชนซึ่งได้รับการเลือกตั้งโดยตรงจากประชาชนอย่างน้อยกึ่งหนึ่งของจำนวนกรรมการทั้งหมด
 
มาตรา ๓๑๓/๑๐  พนักงานอัยการต้องปฏิบัติหน้าที่ด้วยความรวดเร็วและเที่ยงธรรม ในกรณีที่พนักงานอัยการมีคำสั่งเด็ดขาดไม่ฟ้องคดีอาญาที่เป็นคดีเกี่ยวกับการทุจริตต่อหน้าที่ การละเมิดสิทธิมนุษยชน หรือคดีที่กระทบต่อสาธารณประโยชน์อย่างร้ายแรง ประชาชนผู้เสียหายหรือกลุ่มประชาชนจำนวนไม่น้อยกว่าห้าพันคน ย่อมมีสิทธิร่วมกันเข้าชื่อเพื่อฟ้องคดีอาญานั้นต่อศาลได้เองโดยตรง หรือยื่นคำร้องต่อศาลเพื่อขอให้ไต่สวนและมีคำสั่งให้ดำเนินคดีต่อไปได้
 
มาตรา ๓๑๓/๑๑  ประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าพันคน มีสิทธิร่วมกันเข้าชื่อเสนอเรื่องต่อวุฒิสภาเพื่อให้มีมติถอดถอนอัยการสูงสุดหรือพนักงานอัยการผู้ใดผู้หนึ่งที่ส่อทุจริตต่อหน้าที่ ประพฤติมิชอบ หรือสั่งคดีโดยไม่ชอบด้วยกฎหมาย"""

ch_16 = f"""หมวด ๑๖
องค์กรอิสระ
 
ส่วนที่ ๑
บททั่วไปและการควบคุมโดยประชาชน
 
มาตรา ๓๑๓/๑๒  องค์กรอิสระตามรัฐธรรมนูญนี้ เป็นองค์กรที่จัดตั้งขึ้นให้มีความเป็นอิสระในการปฏิบัติหน้าที่ ปราศจากการแทรกแซงจากอำนาจอธิปไตยฝ่ายใดฝ่ายหนึ่ง เพื่อการคุ้มครองประโยชน์ของประชาชนและรักษาความโปร่งใสของแผ่นดิน
 
มาตรา ๓๑๓/๑๓  ประชาชนและสังคมย่อมมีอำนาจและส่วนร่วมในการตรวจสอบ ควบคุม พิทักษ์รักษา และจัดการองค์กรอิสระ ดังต่อไปนี้:
(๑) อำนาจตรวจสอบ: ประชาชนมีสิทธิเข้าตรวจสอบการเงิน การบริหารงานบุคคล และผลการปฏิบัติงานขององค์กรอิสระ โดยองค์กรอิสระทุกแห่งต้องเปิดเผยเอกสารและข้อมูลข่าวสารการประชุม การลงมติ และการจัดซื้อจัดจ้างต่อสาธารณะอย่างรวดเร็วและไม่มีข้อจำกัด
(๒) อำนาจปกป้อง: ประชาชนมีสิทธิร่วมกันเสนอมาตรการ กองทุน หรือเครือข่ายสนับสนุนการทำงานขององค์กรอิสระที่ปฏิบัติหน้าที่อย่างเป็นธรรมและซื่อสัตย์สุจริต เพื่อคุ้มครองมิให้ถูกแทรกแซงหรือคุกคามจากผู้มีอิทธิพลหรือข้าราชการระดับสูง
(๓) อำนาจถอดถอน: ประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าพันคน มีสิทธิร่วมกันเข้าชื่อเพื่อยื่นเรื่องต่อวุฒิสภาหรือศาลรัฐธรรมนูญให้มีมติถอดถอนผู้ดำรงตำแหน่งในองค์กรอิสระคนใดคนหนึ่งที่ส่อเจตนาประพฤติมิชอบหรือละเลยการปฏิบัติหน้าที่
(๔) อำนาจยุบและปฏิรูป: ประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าหมื่นคน มีสิทธิร่วมกันเข้าชื่อเสนอให้มีการออกเสียงประชามติเพื่อยุบเลิก หรือปฏิรูปโครงสร้างขององค์กรอิสระองค์กรใดองค์กรหนึ่ง หากผลประชามติมีคะแนนเสียงเห็นชอบ ให้ถือว่าองค์กรนั้นถูกยุบเลิกหรือเปลี่ยนแปลงโครงสร้างตามเจตนารมณ์ของประชาชนทันที
 
{ec_text_new}
 
{ombuds_text_new}
 
{hr_text_new}
 
{nacc_text_new}
 
{audit_text_new}"""

import expanded_content
import special_chapter
massive_expansion_text = expanded_content.generate_expanded_chapters(start_article=337, target_total_articles=1128)
special_power_text = special_chapter.get_special_chapter(1129)
new_chapters_text = "\n\n".join([ch_13, ch_14 + ch_14_extra, ch_15, ch_16])

idx_trans = text.find("\nบทเฉพาะกาล")
if idx_trans != -1:
    text_parts = [text[:idx_trans], new_chapters_text, text[idx_trans:]]
    text = "\n\n".join(text_parts)

idx_sig = text.find("ผู้รับสนองพระบรมราชโองการ")
if idx_sig != -1:
    text_parts = [text[:idx_sig], massive_expansion_text, special_power_text, text[idx_sig:]]
    text = "\n\n".join(text_parts)

# Save processed text for Word generator
with open(os.path.join(wd, "processed_constitution.txt"), "w", encoding="utf-8") as f:
    f.write(text)
print("Saved processed text for Word generation.")

# 5. Parse text into HTML structure
idx_chapter_1 = text.find("หมวด ๑")
if idx_chapter_1 == -1:
    print("Error: Could not find 'หมวด ๑' in text.")
    sys.exit(1)

cover_and_preamble = text[:idx_chapter_1].strip()
body_text = text[idx_chapter_1:].strip()

cover_paragraphs = [p.strip() for p in re.split(r'\n\s*\n', cover_and_preamble) if p.strip()]
body_paragraphs = [p.strip() for p in re.split(r'\n\s*\n', body_text) if p.strip()]

# Helpers for parsing body
global_art_counter = 1
def to_thai_numeral(num):
    thai_nums = {'0': '๐', '1': '๑', '2': '๒', '3': '๓', '4': '๔', '5': '๕', '6': '๖', '7': '๗', '8': '๘', '9': '๙'}
    return ''.join(thai_nums[digit] for digit in str(num))

def parse_article(paragraph):
    global global_art_counter
    match = re.match(r'^(มาตรา\s+[๐-๙/]+)\s+(.*)', paragraph, re.DOTALL)
    if match:
        _, content = match.groups()
        art_num = f"มาตรา {to_thai_numeral(global_art_counter)}"
        global_art_counter += 1
        
        lines = content.split('\n')
        formatted_lines = []
        
        # Format the first line (runs inline with article header)
        first_line = lines[0].strip()
        formatted_lines.append(f'<p class="article"><span class="bold">{art_num}</span> {first_line}</p>')
        
        # Format subsequent lines
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            # List item checking (e.g. (๑), (๒))
            list_match = re.match(r'^(\([๐-๙]+\))\s*(.*)', line)
            if list_match:
                num, item_text = list_match.groups()
                formatted_lines.append(f'<p class="list-item"><span class="list-num">{num}</span>{item_text}</p>')
            else:
                formatted_lines.append(f'<p class="sub-paragraph">{line}</p>')
        return '\n'.join(formatted_lines)
    return f'<p class="normal">{paragraph}</p>'

def parse_standard_paragraph(paragraph):
    lines = paragraph.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        list_match = re.match(r'^(\([๐-๙]+\))\s*(.*)', line)
        if list_match:
            num, item_text = list_match.groups()
            formatted_lines.append(f'<p class="list-item"><span class="list-num">{num}</span>{item_text}</p>')
        else:
            formatted_lines.append(f'<p class="sub-paragraph">{line}</p>')
    return '\n'.join(formatted_lines)

# Compile HTML body
html_body_elements = []

# Title & King section
title = cover_paragraphs[0]
king_section = cover_paragraphs[1]

html_body_elements.append(f"""
<div class="first-page-header">
  <table class="gazette-meta">
    <tr>
      <td style="text-align: left; width: 35%;">เล่ม ๙๙ ตอนที่ ๑๔๕ ก</td>
      <td style="text-align: center; width: 30%; font-weight: bold;">ราชกิจจานุเบกษา</td>
      <td style="text-align: right; width: 35%;">๑๑ ตุลาคม ๒๕๒๕</td>
    </tr>
  </table>
  <hr class="double-line">
  <div class="garuda-container">
    <img src="Thai_Garuda_emblem.svg" class="garuda-img">
  </div>
  <div class="main-title">{title}</div>
  <div class="king-title">
    {king_section.replace('\n', '<br>')}
  </div>
</div>
""")

# Preamble section
html_body_elements.append('<div class="preamble-container">')
for p in cover_paragraphs[2:]:
    html_body_elements.append(f'<p class="preamble">{p}</p>')
html_body_elements.append('</div>')

# Body section (Chapters, parts, articles)
for paragraph in body_paragraphs:
    if paragraph.startswith("หมวด"):
        html_body_elements.append(f'<div class="chapter-title">{paragraph.replace("\n", "<br>")}</div>')
    elif paragraph.startswith("ส่วน"):
        html_body_elements.append(f'<div class="part-title">{paragraph.replace("\n", "<br>")}</div>')
    elif paragraph.startswith("มาตรา"):
        html_body_elements.append(parse_article(paragraph))
    elif paragraph.startswith("ผู้รับสนอง"):
        # Modify the signature block to นายกรัฐมนตรี without name
        html_body_elements.append("""
<div class="signature-container">
  ผู้รับสนองพระบรมราชโองการ<br>
  นายกรัฐมนตรี
</div>
""")
    else:
        html_body_elements.append(parse_standard_paragraph(paragraph))

# Combine into full HTML
html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>รัฐธรรมนูญแห่งราชอาณาจักรไทย พุทธศักราช ๒๕๒๕</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sarabun:ital,wght@0,100..800;1,100..800&display=swap');
  
  @page {{
    size: A4;
    margin-top: 3cm;
    margin-bottom: 2.5cm;
    margin-left: 2.5cm;
    margin-right: 2.5cm;
    @top-left {{
      content: "เล่ม ๙๙ ตอนที่ ๑๔๕ ก";
      font-family: 'Sarabun', sans-serif;
      font-size: 10pt;
      border-bottom: 0.5px solid #000;
      padding-bottom: 5px;
      width: 100%;
    }}
    @top-center {{
      content: "ราชกิจจานุเบกษา";
      font-family: 'Sarabun', sans-serif;
      font-size: 10pt;
      border-bottom: 0.5px solid #000;
      padding-bottom: 5px;
      width: 100%;
    }}
    @top-right {{
      content: "หน้า " counter(page, thai);
      font-family: 'Sarabun', sans-serif;
      font-size: 10pt;
      border-bottom: 0.5px solid #000;
      padding-bottom: 5px;
      width: 100%;
    }}
  }}
  
  @page :first {{
    margin-top: 1.5cm;
    @top-left {{ content: none; }}
    @top-center {{ content: none; }}
    @top-right {{ content: none; }}
  }}
  
  body {{
    font-family: 'Sarabun', sans-serif;
    font-size: 15pt;
    line-height: 1.6;
    color: #000000;
    margin: 0;
    padding: 0;
  }}
  
  p {{
    text-align: justify;
    text-justify: inter-word;
    margin-top: 0.3em;
    margin-bottom: 0.3em;
  }}
  
  p.preamble {{
    text-indent: 1.5cm;
  }}
  
  p.article {{
    text-indent: 1.5cm;
    margin-top: 0.4em;
    margin-bottom: 0.4em;
  }}
  
  p.sub-paragraph {{
    text-indent: 1.5cm;
    margin-top: 0.2em;
    margin-bottom: 0.2em;
  }}
  
  p.list-item {{
    text-indent: 0;
    margin-left: 2.2cm;
    margin-top: 0.2em;
    margin-bottom: 0.2em;
  }}
  
  span.list-num {{
    display: inline-block;
    width: 1cm;
    margin-left: -1cm;
    font-weight: normal;
  }}
  
  p.normal {{
    text-indent: 1.5cm;
  }}
  
  .bold {{
    font-weight: bold;
  }}
  
  .chapter-title {{
    font-size: 16pt;
    font-weight: bold;
    text-align: center;
    margin-top: 1.5em;
    margin-bottom: 0.8em;
    page-break-after: avoid;
    line-height: 1.4;
  }}
  
  .part-title {{
    font-size: 15pt;
    font-weight: bold;
    text-align: center;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    page-break-after: avoid;
    line-height: 1.4;
  }}
  
  .first-page-header {{
    text-align: center;
    margin-bottom: 1.5em;
  }}
  
  .gazette-meta {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 5px;
    font-size: 11pt;
    font-family: 'Sarabun', sans-serif;
  }}
  
  .gazette-meta td {{
    padding: 0;
  }}
  
  .double-line {{
    border: none;
    border-top: 1px solid #000;
    border-bottom: 3px double #000;
    height: 4px;
    margin-top: 0;
    margin-bottom: 1.5em;
  }}
  
  .garuda-container {{
    margin: 1em auto;
    text-align: center;
  }}
  
  .garuda-img {{
    width: 100px;
    height: auto;
  }}
  
  .main-title {{
    font-size: 20pt;
    font-weight: bold;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    line-height: 1.3;
  }}
  
  .king-title {{
    font-size: 16pt;
    font-weight: bold;
    line-height: 1.7;
    margin-bottom: 1em;
  }}
  
  .preamble-container {{
    margin-bottom: 2em;
  }}
  
  .signature-container {{
    margin-top: 2.5em;
    margin-left: 55%;
    text-align: left;
    line-height: 1.7;
    page-break-inside: avoid;
    font-weight: bold;
  }}
</style>
</head>
<body>
  {"\n".join(html_body_elements)}
</body>
</html>
"""

# Write to file
with open(html_output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML file generated successfully: {html_output_path}")

# 6. Convert to PDF using Google Chrome
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    print("Chrome not found. Falling back to Microsoft Edge.")

cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_output_path}",
    html_output_path
]

# Delete the file before generating to verify that Chrome successfully creates it
if os.path.exists(pdf_output_path):
    try:
        os.remove(pdf_output_path)
    except OSError:
        pass

print("Converting HTML to PDF...")
print("Command:", " ".join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(pdf_output_path):
    print("PDF generated successfully!")
    print("PDF Path:", pdf_output_path)
    print("PDF Size:", os.path.getsize(pdf_output_path), "bytes")
else:
    print("Error: PDF generation failed.")
    print("Exit code:", res.returncode)
    print("Stdout:", res.stdout)
    print("Stderr:", res.stderr)
    sys.exit(1)
