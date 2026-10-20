"""One-off text fixes in ม.๑-๓๖๐ found by the 2026-10-20 audit (tools/charter/audit_conflicts.md).

Each edit asserts that its target occurs exactly once, so running it twice fails loudly.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML = os.path.join(ROOT, 'website_constitution.html')

EDITS = [
    # ม.๓๑ carries the text of 2540 ม.๓๒ as its last paragraph, still labelled "มาตรา ๓๒".
    ('<p class="sub-para"><span class="cross-ref" data-target="32">มาตรา ๓๒</span>  บุคคลจะไม่ต้องรับโทษอาญา',
     '<p class="sub-para">บุคคลจะไม่ต้องรับโทษอาญา'),
    # Placeholder articles claimed ranges ("ถึง มาตรา ๑๔๘") that hold other articles.
    ('<span class="art-num">มาตรา ๑๓๗</span> ถึง <span class="cross-ref" data-target="148">มาตรา ๑๔๘</span> (ย้าย',
     '<span class="art-num">มาตรา ๑๓๗</span> (ย้าย'),
    ('<span class="art-num">มาตรา ๑๘๖</span> ถึง <span class="cross-ref" data-target="198">มาตรา ๑๙๘</span> (ย้าย',
     '<span class="art-num">มาตรา ๑๘๖</span> (ย้าย'),
    ('<span class="art-num">มาตรา ๑๘๗</span> ถึง <span class="cross-ref" data-target="200">มาตรา ๒๐๐</span> (ย้าย',
     '<span class="art-num">มาตรา ๑๘๗</span> (ย้าย'),
    ('<span class="art-num">มาตรา ๒๘๔</span> ถึง <span class="cross-ref" data-target="303">มาตรา ๓๐๓</span> (ย้าย',
     '<span class="art-num">มาตรา ๒๘๔</span> (ย้าย'),
    # ม.๒๙๘ cited a non-existent "มาตรา ๓๑๔/๑"; the office holders who file asset accounts are in ม.๒๗๘.
    ('ผู้ดำรงตำแหน่งตาม<span class="cross-ref" data-target="314">มาตรา ๓๑๔</span>/๑ และ',
     'ผู้ดำรงตำแหน่งตาม<span class="cross-ref" data-target="278">มาตรา ๒๗๘</span> และ'),
    # The office is called ผู้ตรวจการแผ่นดินของรัฐสภา everywhere else in the charter.
    ('<div class="part-title">ส่วนที่ ๓<br>ผู้ตรวจการแผ่นดิน</div>',
     '<div class="part-title">ส่วนที่ ๓<br>ผู้ตรวจการแผ่นดินของรัฐสภา</div>'),
]

src = open(HTML, encoding='utf-8').read()
for old, new in EDITS:
    assert src.count(old) == 1, (old[:60], src.count(old))
    src = src.replace(old, new)
open(HTML, 'w', encoding='utf-8').write(src)
print('applied %d text fixes' % len(EDITS))
