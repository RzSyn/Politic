# build_charter_files.py — สร้างไฟล์ Word / PDF / สารบัญ ของรัฐธรรมนูญ ๒๕๒๕ จากตัวบทใน website_new.html
#
#   python tools/build_charter_files.py
#
# ตัวบทอ่านจาก website_new.html (สร้างโดย tools/build_site.py) ซึ่งรวมการแก้ไขเพิ่มเติมทุกรอบแล้ว
# ไม่ได้ใช้ files/processed_constitution.txt แบบ Genarate/generate_*.py ที่ตกรุ่นไปแล้ว
# ผลลัพธ์:
#   files/รัฐธรรมนูญ_๒๕๒๕_แก้ไขเพิ่มเติม.docx   (รูปแบบเดียวกับ Genarate/generate_word.py + ตราครุฑหน้าแรก)
#   files/สารบัญรัฐธรรมนูญ.docx
#   constitution_2525.html                        (หน้าพิมพ์แบบราชกิจจานุเบกษา ใช้พิมพ์ PDF)
#   files/รัฐธรรมนูญ_๒๕๒๕_แก้ไขเพิ่มเติม.pdf      (พิมพ์จาก constitution_2525.html ด้วย Chromium)
# แล้วอ่านทั้งสามไฟล์กลับมาเทียบกับตัวบทในเว็บทีละมาตรา หยุดทันทีถ้าไม่ตรง

import html
import os
import re
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'website_new.html')
BASE = 'รัฐธรรมนูญ_๒๕๒๕_แก้ไขเพิ่มเติม'
WORD_OUT = os.path.join(ROOT, 'files', BASE + '.docx')
TOC_OUT = os.path.join(ROOT, 'files', 'สารบัญรัฐธรรมนูญ.docx')
HTML_OUT = os.path.join(ROOT, 'constitution_2525.html')
PDF_OUT = os.path.join(ROOT, 'files', BASE + '.pdf')
GARUDA_PNG = os.path.join(ROOT, 'images', 'Thai_Garuda_emblem.png')
GARUDA_SVG = 'images/Thai_Garuda_emblem.svg'      # relative to constitution_2525.html
THAI_FONT = 'TH Sarabun New'
FULL_TITLE = 'รัฐธรรมนูญแห่งราชอาณาจักรไทย พุทธศักราช ๒๕๒๕'

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def thai(n):
    return str(n).translate(str.maketrans('0123456789', '๐๑๒๓๔๕๖๗๘๙'))


def text_of(fragment):
    """Visible text of an HTML fragment: tooltips dropped, <br> kept as newlines."""
    fragment = re.sub(r'<span class="tooltiptext">.*?</span>', '', fragment, flags=re.S)
    fragment = re.sub(r'<br\s*/?>', '\n', fragment)
    fragment = html.unescape(re.sub(r'<[^>]+>', '', fragment))
    return '\n'.join(re.sub(r'[ \t]+', ' ', line).strip() for line in fragment.split('\n')).strip()


def split_lines(lines):
    """Turn loose lines into ('list', num, text) / ('para', text) items."""
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(\([๐-๙]+\))\s*(.*)', line, re.S)
        items.append(('list', m.group(1), m.group(2)) if m else ('para', line))
    return items


# ==================== Read the charter from website_new.html ====================

src = open(SRC, encoding='utf-8').read()
pre = src[src.index('<section class="nw-preamble"'):]
pre = pre[:pre.index('</section>')]
title = text_of(re.search(r'<h2>(.*?)</h2>', pre, re.S).group(1))
king_lines = text_of(re.search(r'<p class="nw-preamble-sub">(.*?)</p>', pre, re.S).group(1)).split('\n')
preamble = [text_of(p) for p in re.findall(r'<p>(.*?)</p>', pre, re.S)]

chapters = []
for sec in re.finditer(r'<section class="nw-chapter" id="ch_\d+">(.*?)</section>', src, re.S):
    body = sec.group(1)
    head = re.search(r'<div class="nw-ch-no">(.*?)</div><div><h2>(.*?)</h2>', body, re.S)
    ch = {'no': text_of(head.group(1)), 'name': text_of(head.group(2)), 'blocks': []}
    body = body[body.index('</header>') + 9:]
    for m in re.finditer(r'<h3 class="nw-part">(.*?)</h3>'
                         r'|<article class="nw-art[^"]*" id="art_(\d+)"[^>]*>(.*?)</article>'
                         r'|<div class="nw-clause">(.*?)</div>'
                         r'|<div class="nw-signature">(.*?)</div>', body, re.S):
        if m.group(1) is not None:
            ch['blocks'].append(('part', text_of(m.group(1)).split('\n')))
        elif m.group(2) is not None:
            art = m.group(3)
            art = art[art.index('<div class="nw-art-body">'):]
            art = re.sub(r'<div class="nw-compare".*', '', art, flags=re.S)   # the 2540 comparison is not charter text
            items = []
            for p in re.finditer(r'<p class="(article-text|sub-para|list-item)">(.*?)</p>', art, re.S):
                if p.group(1) == 'list-item':
                    num = re.match(r'\s*<span class="list-num">(.*?)</span>\s*', p.group(2), re.S)
                    items.append(('list', text_of(num.group(1)), text_of(p.group(2)[num.end():])))
                else:
                    items.append(('para', text_of(p.group(2))))
            assert items and items[0][0] == 'para', 'article %s does not open with its text' % m.group(2)
            ch['blocks'].append(('art', int(m.group(2)), items))
        elif m.group(4) is not None:
            # a clause the site shows after an article belongs to that article (e.g. ม.๒๙๕)
            assert ch['blocks'] and ch['blocks'][-1][0] == 'art', 'clause with no article before it'
            ch['blocks'][-1][2].extend(split_lines(text_of(m.group(4)).split('\n')))
        else:
            ch['blocks'].append(('sign', text_of(m.group(5)).split('\n')))
    chapters.append(ch)

arts = [b for ch in chapters for b in ch['blocks'] if b[0] == 'art']
nums = [b[1] for b in arts]
assert nums == list(range(1, 1161)), 'articles are not ๑–๑๑๖๐ in order'
assert len(chapters) == 38, len(chapters)
print('อ่านจาก website_new.html: %d หมวด, %d มาตรา' % (len(chapters), len(arts)))


def chapter_lines(ch):
    return [x for x in (ch['no'], ch['name']) if x]


def chapter_label(ch):
    return ' '.join(chapter_lines(ch))


def chapter_range(ch):
    n = [b[1] for b in ch['blocks'] if b[0] == 'art']
    return (min(n), max(n)) if n else None


# ==================== Word helpers (same look as Genarate/generate_word.py) ====================

def set_thai_language(run):
    rPr = run._element.get_or_add_rPr()
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'th-TH')
    lang.set(qn('w:bidi'), 'th-TH')
    lang.set(qn('w:eastAsia'), 'th-TH')
    rPr.append(lang)


def set_document_thai_language(doc):
    styles_element = doc.styles.element
    docDefaults = styles_element.find(qn('w:docDefaults'))
    if docDefaults is None:
        docDefaults = OxmlElement('w:docDefaults')
        styles_element.insert(0, docDefaults)
    rPrDefault = docDefaults.find(qn('w:rPrDefault'))
    if rPrDefault is None:
        rPrDefault = OxmlElement('w:rPrDefault')
        docDefaults.append(rPrDefault)
    rPr = rPrDefault.find(qn('w:rPr'))
    if rPr is None:
        rPr = OxmlElement('w:rPr')
        rPrDefault.append(rPr)
    rFonts = OxmlElement('w:rFonts')
    for k in ('ascii', 'hAnsi', 'cs', 'eastAsia'):
        rFonts.set(qn('w:' + k), THAI_FONT)
    rPr.append(rFonts)
    for tag in ('w:sz', 'w:szCs'):
        el = OxmlElement(tag)
        el.set(qn('w:val'), '32')
        rPr.append(el)
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'th-TH')
    lang.set(qn('w:bidi'), 'th-TH')
    lang.set(qn('w:eastAsia'), 'th-TH')
    rPr.append(lang)

    style = doc.styles['Normal']
    style.font.name = THAI_FONT
    style.font.size = Pt(16)
    style.element.rPr.rFonts.set(qn('w:cs'), THAI_FONT)
    pf = style.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.15


def add_thai_run(paragraph, text, bold=False, size=Pt(16)):
    run = paragraph.add_run(text)
    run.font.name = THAI_FONT
    run._element.rPr.rFonts.set(qn('w:cs'), THAI_FONT)
    run.font.bold = bold
    run.font.size = size
    rPr = run._element.get_or_add_rPr()
    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), str(int(size.pt * 2)))
    rPr.append(szCs)
    if bold:
        rPr.append(OxmlElement('w:bCs'))
    set_thai_language(run)
    return run


def add_lines(paragraph, lines, bold=False, size=Pt(16)):
    for i, line in enumerate(lines):
        run = add_thai_run(paragraph, line, bold=bold, size=size)
        if i < len(lines) - 1:
            run.add_break()


def new_paragraph(doc, align=None, before=None, after=None, first=None, left=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)
    if first is not None:
        pf.first_line_indent = Cm(first)
    if left is not None:
        pf.left_indent = Cm(left)
    pPr = p._element.get_or_add_pPr()
    rPr = OxmlElement('w:rPr')
    rPr.append(OxmlElement('w:noProof'))
    pPr.append(rPr)
    return p


def page_number_field(paragraph):
    for kind, text in (('begin', None), (None, ' PAGE '), ('end', None)):
        run = paragraph.add_run()
        if kind:
            el = OxmlElement('w:fldChar')
            el.set(qn('w:fldCharType'), kind)
        else:
            el = OxmlElement('w:instrText')
            el.set(qn('xml:space'), 'preserve')
            el.text = text
        run._element.append(el)


def setup_page(doc):
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = section.right_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    hp = section.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_thai_run(hp, 'ราชกิจจานุเบกษา  ฉบับพิเศษ', size=Pt(12))
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page_number_field(fp)


def finalize_document(doc):
    settings = doc.settings.element
    proof = OxmlElement('w:proofState')
    proof.set(qn('w:spelling'), 'clean')
    proof.set(qn('w:grammar'), 'clean')
    settings.append(proof)
    lang = settings.find(qn('w:themeFontLang'))
    if lang is None:
        lang = OxmlElement('w:themeFontLang')
        settings.append(lang)
    lang.set(qn('w:val'), 'th-TH')
    lang.set(qn('w:bidi'), 'th-TH')


def new_document():
    doc = Document()
    setup_page(doc)
    set_document_thai_language(doc)
    doc.core_properties.title = FULL_TITLE
    doc.core_properties.author = 'รัฐธรรมนุญจำลอง'
    return doc


# ==================== Main Word document ====================

def add_items(doc, items, art_no=None):
    for k, item in enumerate(items):
        if item[0] == 'list':
            p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=1, left=2.2, first=-0.7)
            add_thai_run(p, item[1] + ' ')
            add_thai_run(p, item[2])
        else:
            p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=3, first=1.5)
            if k == 0 and art_no is not None:
                add_thai_run(p, 'มาตรา %s  ' % thai(art_no), bold=True)
            add_thai_run(p, item[1])


doc = new_document()
p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=24, after=6)
p.add_run().add_picture(GARUDA_PNG, width=Cm(3.2))
p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, after=18)
add_thai_run(p, title, bold=True, size=Pt(22))
p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, after=18)
add_lines(p, king_lines)
for para in preamble:
    p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=6, first=2)
    add_thai_run(p, para)

for ci, ch in enumerate(chapters):
    p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=24, after=12)
    p.paragraph_format.keep_with_next = True
    if ci:
        p.paragraph_format.page_break_before = True      # every chapter starts a new page, as before
    add_lines(p, chapter_lines(ch), bold=True, size=Pt(18))
    for b in ch['blocks']:
        if b[0] == 'part':
            p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=12, after=6)
            p.paragraph_format.keep_with_next = True
            add_lines(p, b[1], bold=True)
        elif b[0] == 'art':
            add_items(doc, b[2], art_no=b[1])
        else:
            p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.RIGHT, before=24)
            add_thai_run(p, b[1][0])
            for line in b[1][1:]:
                p = new_paragraph(doc, align=WD_ALIGN_PARAGRAPH.RIGHT)
                add_thai_run(p, line, bold=True)

finalize_document(doc)
doc.save(WORD_OUT)
print('Word: %s (%s bytes)' % (os.path.relpath(WORD_OUT, ROOT), format(os.path.getsize(WORD_OUT), ',')))

# ==================== Table of contents ====================

toc = new_document()
p = new_paragraph(toc, align=WD_ALIGN_PARAGRAPH.CENTER, before=36, after=6)
add_thai_run(p, 'สารบัญ', bold=True, size=Pt(24))
p = new_paragraph(toc, align=WD_ALIGN_PARAGRAPH.CENTER, after=24)
add_thai_run(p, FULL_TITLE, bold=True, size=Pt(18))
table = toc.add_table(rows=1, cols=3)
table.style = 'Table Grid'
table.autofit = False
widths = (Cm(10), Cm(3), Cm(3))
for col, w in zip(table.columns, widths):
    col.width = w      # the grid widths; LibreOffice ignores per-cell widths alone


def shade(cell, fill):
    el = OxmlElement('w:shd')
    el.set(qn('w:fill'), fill)
    el.set(qn('w:val'), 'clear')
    cell._element.get_or_add_tcPr().append(el)


for cell, w, label, size in zip(table.rows[0].cells, widths, ('หมวด / รายการ', 'มาตราเริ่มต้น', 'มาตราสุดท้าย'),
                                 (Pt(16), Pt(14), Pt(14))):
    cell.width = w
    shade(cell, '2C3E50')
    cp = cell.paragraphs[0]
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_thai_run(cp, label, bold=True, size=size).font.color.rgb = RGBColor(255, 255, 255)
toc_rows = []
for i, ch in enumerate(chapters):
    first, last = chapter_range(ch)
    toc_rows.append((chapter_label(ch), first, last))
    row = table.add_row()
    for cell, w, value, align in zip(row.cells, widths, (chapter_label(ch), thai(first), thai(last)),
                                     (None, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER)):
        cell.width = w
        shade(cell, 'EBF5FB' if i % 2 == 0 else 'FFFFFF')
        cp = cell.paragraphs[0]
        if align is not None:
            cp.alignment = align
        add_thai_run(cp, value, size=Pt(14))
p = new_paragraph(toc, before=18)
add_thai_run(p, 'รวมทั้งสิ้น %s หมวด  %s มาตรา' % (thai(len(chapters)), thai(len(arts))), bold=True)
finalize_document(toc)
toc.save(TOC_OUT)
print('สารบัญ: %s' % os.path.relpath(TOC_OUT, ROOT))

# ==================== Print page (constitution_2525.html) ====================

esc = html.escape


def items_html(items, art_no):
    out = []
    for k, item in enumerate(items):
        if item[0] == 'list':
            out.append('<p class="list-item"><span class="list-num">%s</span>%s</p>' % (esc(item[1]), esc(item[2])))
        elif k == 0:
            out.append('<p class="article"><span class="bold">มาตรา %s</span> %s</p>' % (thai(art_no), esc(item[1])))
        else:
            out.append('<p class="sub-paragraph">%s</p>' % esc(item[1]))
    return '\n'.join(out)


body = ['''<div class="first-page-header">
  <table class="gazette-meta"><tr>
    <td style="text-align:left;width:35%">เล่ม ๙๙ ตอนที่ ๑๔๕ ก</td>
    <td style="text-align:center;width:30%;font-weight:bold">ราชกิจจานุเบกษา</td>
    <td style="text-align:right;width:35%">๑๑ ตุลาคม ๒๕๒๕</td>
  </tr></table>
  <hr class="double-line">
  <div class="garuda-container"><img src="''' + GARUDA_SVG + '''" class="garuda-img" alt=""></div>
  <div class="main-title">''' + esc(title) + '''</div>
  <div class="king-title">''' + '<br>'.join(map(esc, king_lines)) + '''</div>
</div>''', '<div class="preamble-container">']
body += ['<p class="preamble">%s</p>' % esc(p) for p in preamble]
body.append('</div>')
for ch in chapters:
    body.append('<div class="chapter-title">%s</div>' % '<br>'.join(map(esc, chapter_lines(ch))))
    for b in ch['blocks']:
        if b[0] == 'part':
            body.append('<div class="part-title">%s</div>' % '<br>'.join(map(esc, b[1])))
        elif b[0] == 'art':
            body.append(items_html(b[2], b[1]))
        else:
            body.append('<div class="signature-container">%s</div>' % '<br>'.join(map(esc, b[1])))

page = '''<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>''' + FULL_TITLE + '''</title>
<!-- สร้างโดย tools/build_charter_files.py จาก website_new.html — อย่าแก้ไฟล์นี้ด้วยมือ -->
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
  @page {
    size: A4;
    margin: 3cm 2.5cm 2.5cm 2.5cm;
    @top-left { content: "เล่ม ๙๙ ตอนที่ ๑๔๕ ก"; font-family: 'Sarabun', sans-serif; font-size: 10pt; border-bottom: 0.5px solid #000; padding-bottom: 5px; }
    @top-center { content: "ราชกิจจานุเบกษา"; font-family: 'Sarabun', sans-serif; font-size: 10pt; border-bottom: 0.5px solid #000; padding-bottom: 5px; }
    @top-right { content: "หน้า " counter(page, thai); font-family: 'Sarabun', sans-serif; font-size: 10pt; border-bottom: 0.5px solid #000; padding-bottom: 5px; }
  }
  @page :first {
    margin-top: 1.5cm;
    @top-left { content: none; } @top-center { content: none; } @top-right { content: none; }
  }
  body { font-family: 'Sarabun', sans-serif; font-size: 15pt; line-height: 1.6; color: #000; margin: 0; padding: 0; }
  p { text-align: justify; text-justify: inter-word; margin: 0.3em 0; }
  /* Chromium paints the stacked Thai marks of a line pushed to the next page at the foot of this one;
     clipping each paragraph fragment to its own box removes those stray marks */
  p, .chapter-title, .part-title, .signature-container { overflow: hidden; }
  p.preamble, p.normal { text-indent: 1.5cm; }
  p.article { text-indent: 1.5cm; margin: 0.4em 0; }
  p.sub-paragraph { text-indent: 1.5cm; margin: 0.2em 0; }
  p.list-item { text-indent: 0; margin: 0.2em 0 0.2em 1.2cm; padding-left: 1cm; }   /* number sits in the padding, inside the clip */
  span.list-num { display: inline-block; width: 1cm; margin-left: -1cm; }
  .bold { font-weight: bold; }
  .chapter-title { font-size: 16pt; font-weight: bold; text-align: center; margin: 1.5em 0 0.8em; page-break-after: avoid; line-height: 1.4; }
  .part-title { font-size: 15pt; font-weight: bold; text-align: center; margin: 1.2em 0 0.6em; page-break-after: avoid; line-height: 1.4; }
  .first-page-header { text-align: center; margin-bottom: 1.5em; }
  .gazette-meta { width: 100%; border-collapse: collapse; margin-bottom: 5px; font-size: 11pt; }
  .gazette-meta td { padding: 0; }
  .double-line { border: none; border-top: 1px solid #000; border-bottom: 3px double #000; height: 4px; margin: 0 0 1.5em; }
  .garuda-container { margin: 1em auto; text-align: center; }
  .garuda-img { width: 100px; height: auto; }
  .main-title { font-size: 20pt; font-weight: bold; margin: 0.5em 0; line-height: 1.3; }
  .king-title { font-size: 16pt; font-weight: bold; line-height: 1.7; margin-bottom: 1em; }
  .preamble-container { margin-bottom: 2em; }
  .signature-container { margin-top: 2.5em; margin-left: 55%; text-align: left; line-height: 1.7; page-break-inside: avoid; font-weight: bold; }
</style>
</head>
<body>
''' + '\n'.join(body) + '''
</body>
</html>
'''
open(HTML_OUT, 'w', encoding='utf-8').write(page)
print('หน้าพิมพ์: %s' % os.path.relpath(HTML_OUT, ROOT))

# ==================== PDF (Chromium through Playwright) ====================

node = r'''
const { chromium } = require('playwright');
(async () => {
  const p = process.env.HTTPS_PROXY;
  const opts = process.env.CHROME ? { executablePath: process.env.CHROME } : {};
  if (p) opts.proxy = { server: p };
  const browser = await chromium.launch(opts);
  const page = await browser.newPage();
  await page.goto(process.argv[1], { waitUntil: 'networkidle', timeout: 120000 });
  await page.evaluate(() => document.fonts.ready);
  const ok = await page.evaluate(() => document.fonts.check('15pt Sarabun', 'ก'));
  if (!ok) { console.error('Sarabun did not load'); process.exit(2); }
  await page.pdf({ path: process.argv[2], format: 'A4', preferCSSPageSize: true, printBackground: true });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
'''
env = dict(os.environ)
env.setdefault('NODE_PATH', subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip())
res = subprocess.run(['node', '-e', node, 'file://' + HTML_OUT, PDF_OUT], env=env, capture_output=True, text=True)
if res.returncode:
    sys.exit('PDF failed: ' + (res.stderr or res.stdout)[-800:])
print('PDF: %s (%s bytes)' % (os.path.relpath(PDF_OUT, ROOT), format(os.path.getsize(PDF_OUT), ',')))

# ==================== Read every output back and compare with the site ====================

squash = lambda s: re.sub(r'\s+', '', s).replace('ํา', 'ำ')
expected = squash(''.join([title] + king_lines + preamble + [
    ''.join(chapter_lines(ch)) + ''.join(
        ''.join(b[1]) if b[0] in ('part', 'sign') else
        'มาตรา' + thai(b[1]) + ''.join(''.join(it[1:]) for it in b[2])
        for b in ch['blocks'])
    for ch in chapters]))

got_word = squash(''.join(p.text for p in Document(WORD_OUT).paragraphs))
assert got_word == expected, 'Word text differs from website_new.html'
gazette_head = lambda s: re.sub(r'เล่ม๙๙ตอนที่๑๔๕กราชกิจจานุเบกษา(หน้า[๐-๙]+|๑๑ตุลาคม๒๕๒๕)', '', s)
got_html = gazette_head(squash(text_of(page[page.index('<body>'):])))
assert got_html == expected, 'print page text differs from website_new.html'
import fitz  # PyMuPDF
pdf = fitz.open(PDF_OUT)
got_pdf = gazette_head(squash(''.join(pg.get_text() for pg in pdf)))
if got_pdf != expected:
    i = next((k for k, (a, b) in enumerate(zip(got_pdf, expected)) if a != b), min(len(got_pdf), len(expected)))
    sys.exit('PDF text differs at %d: pdf …%s… / site …%s…' % (i, got_pdf[i - 40:i + 40], expected[i - 40:i + 40]))
toc_doc = Document(TOC_OUT)
assert len(toc_doc.tables[0].rows) == len(chapters) + 1
print('ตรวจแล้ว: Word, หน้าพิมพ์ และ PDF (%d หน้า) ตรงกับตัวบทในเว็บทุกตัวอักษร (%s ตัว)'
      % (pdf.page_count, format(len(expected), ',')))
