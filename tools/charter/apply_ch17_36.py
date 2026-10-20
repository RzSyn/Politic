"""Rewrite the article text of หมวด ๑๗-๓๖ (ม.๓๓๘-๑,๑๒๗) in website_constitution.html.

Each chapter keeps its 8 topics and every article keeps its number and topic, so the
dashboard tabs that cite these articles stay correct.  Topic t of a chapter sits at
articles start+t, start+8+t, start+16+t, start+24+t, start+32+t.

Source files: tools/charter/chNN.txt, one line per article:  t.k|text
(t = topic 0-7, k = 1-5 = which of the topic's five articles).
ม.๑,๑๒๘-๑,๑๒๙ and หมวดพิเศษ are never touched.

    python tools/charter/apply_ch17_36.py            # all chapter files present
    python tools/charter/apply_ch17_36.py 17 18      # only these chapters
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML = os.path.join(ROOT, 'website_constitution.html')
HERE = os.path.dirname(os.path.abspath(__file__))

# numbering after move_transitional.py put บทเฉพาะกาล at the end (หมวด ๑๗ starts at ม.๓๓๘)
STARTS = [338, 378, 418, 458, 498, 538, 578, 618, 658, 698,
          738, 778, 818, 857, 896, 935, 974, 1013, 1052, 1091, 1130]
PROTECTED = {1128, 1129}
TH = '๐๑๒๓๔๕๖๗๘๙'


def thai(n):
    return ''.join(TH[int(c)] for c in str(n))


def load(ch):
    start, end = STARTS[ch - 17], STARTS[ch - 16]
    texts = {}
    with open(os.path.join(HERE, 'ch%d.txt' % ch), encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            key, text = line.split('|', 1)
            t, k = (int(x) for x in key.split('.'))
            n = start + t + 8 * (k - 1)
            assert start <= n < end and n not in PROTECTED, (ch, key, n)
            assert n not in texts, (ch, key, 'duplicate')
            assert 'ผู้ใช้บริการ' not in text and '|' not in text, (ch, key)
            texts[n] = text.strip()
    want = set(range(start, end)) - PROTECTED
    missing = sorted(want - set(texts))
    assert not missing, (ch, 'missing', missing)
    return texts


def main():
    chapters = [int(a) for a in sys.argv[1:]] or [
        c for c in range(17, 37) if os.path.exists(os.path.join(HERE, 'ch%d.txt' % c))]
    src = open(HTML, encoding='utf-8').read()
    count = 0
    for ch in chapters:
        for n, text in load(ch).items():
            a = src.index('id="art_%d"' % n)
            b = src.index('<p class="article-text">', a)
            e = src.index('</p>', b)
            assert b < src.index('id="art_', a + 10), n   # the paragraph belongs to this card
            head = '<p class="article-text"><span class="art-num">มาตรา %s</span> ' % thai(n)
            assert src.startswith(head, b), n
            src = src[:b] + head + text + src[e:]
            count += 1
    open(HTML, 'w', encoding='utf-8').write(src)
    print('rewrote %d articles in chapters %s' % (count, chapters))


if __name__ == '__main__':
    main()
