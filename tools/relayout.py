# -*- coding: utf-8 -*-
"""Re-lay out a legacy tab into the new site's component markup.

The old panels carry their looks in inline styles.  This walks the markup,
recognises the recurring shapes (header, stat grid, note box, panel, card,
table, figure) and re-emits them with the .nwc-* classes, keeping every word
of the content.  Scripts and styles inside a tab are kept verbatim.
"""
from html.entities import html5 as HTML5_ENTITIES
import json
import os
import re
import sys
from html.parser import HTMLParser

VOID = {'img', 'br', 'hr', 'input', 'source', 'meta', 'link', 'col', 'area', 'embed'}
SELF_OK = {'rect', 'path', 'circle', 'line', 'polygon', 'polyline', 'ellipse', 'use', 'stop',
           'image', 'animate', 'animatetransform', 'fegaussianblur', 'marker', 'pattern', 'text'}
SVG_CASE = {'viewbox': 'viewBox', 'preserveaspectratio': 'preserveAspectRatio',
            'gradientunits': 'gradientUnits', 'gradienttransform': 'gradientTransform',
            'patternunits': 'patternUnits', 'clippathunits': 'clipPathUnits',
            'stroke-dasharray': 'stroke-dasharray', 'textlength': 'textLength'}
EMOJI = re.compile(r'^\s*([☀-➿⬀-⯿️⃣🀀-🫿]+)\s*')


class Node:
    def __init__(self, tag, attrs=None, selfclose=False):
        self.tag = tag
        self.attrs = {SVG_CASE.get(k, k): v for k, v in dict(attrs or {}).items()}
        self.kids = []
        self.parent = None
        self.selfclose = selfclose

    def add(self, n):
        if isinstance(n, Node):
            n.parent = self
        self.kids.append(n)

    @property
    def style(self):
        return (self.attrs.get('style') or '').replace(' ', '')

    def el(self, tag=None):
        return [k for k in self.kids if isinstance(k, Node) and k.tag != '#raw'
                and (tag is None or k.tag == tag)]

    def text(self):
        return ''.join(k.text() if isinstance(k, Node) else k for k in self.kids)

    def flat_text(self):
        return ' '.join(self.text().split())

    def inner(self):
        return ''.join(render(k) for k in self.kids)


class Build(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node('#root')
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.cur.add(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.add(Node(tag, attrs, selfclose=True))

    def handle_endtag(self, tag):
        p = self.cur
        while p is not self.root and p.tag != tag:
            p = p.parent
        if p is not self.root:
            self.cur = p.parent

    def handle_data(self, d):
        self.cur.add(d)

    def handle_entityref(self, name):
        known = (name + ';') in HTML5_ENTITIES
        self.cur.add('&' + name + (';' if known else ''))

    def handle_charref(self, name):
        self.cur.add('&#' + name + ';')

    def handle_comment(self, d):
        self.cur.add('<!--' + d + '-->')


def attrs_str(n):
    out = []
    for k, v in n.attrs.items():
        out.append(' ' + k if v is None else ' %s="%s"' % (k, v))
    return ''.join(out)


def render(n):
    if not isinstance(n, Node):
        return n
    if n.tag == '#root':
        return n.inner()
    if n.tag == '#raw':
        return n.attrs['html']
    if n.tag in VOID:
        return '<%s%s>' % (n.tag, attrs_str(n))
    if n.selfclose and not n.kids and n.tag in SELF_OK:
        return '<%s%s />' % (n.tag, attrs_str(n))
    return '<%s%s>%s</%s>' % (n.tag, attrs_str(n), n.inner(), n.tag)


def plain(n, cls=None):
    """Drop the inline look, keep the element."""
    n.attrs.pop('style', None)
    if cls:
        have = n.attrs.get('class', '')
        n.attrs['class'] = (have + ' ' + cls).strip()
    return n


def split_icon(s):
    m = EMOJI.match(s)
    return (m.group(1), s[m.end():].strip()) if m else ('', s.strip())


def is_titleish(n):
    """A short bold line that introduces the box it sits in."""
    if not isinstance(n, Node) or n.tag not in ('div', 'h3', 'h4', 'h5', 'p', 'span'):
        return False
    t = n.flat_text()
    if not t or len(t) > 110:
        return False
    if n.tag in ('h3', 'h4', 'h5'):
        return True
    st = n.style
    bold = 'font-weight:800' in st or 'font-weight:700' in st or 'font-weight:bold' in st
    return bold and not n.el('div')


def keep_layout_only(n):
    """Keep a grid or flex row's shape, drop its colours."""
    fields = ('display', 'grid-template-columns', 'grid-template-rows', 'gap',
              'flex-wrap', 'align-items', 'justify-content', 'flex-direction', 'flex')
    keep = []
    for part in (n.attrs.get('style') or '').split(';'):
        if part.strip() and part.split(':')[0].strip() in fields:
            keep.append(part.strip())
    if keep:
        n.attrs['style'] = '; '.join(keep)
    else:
        n.attrs.pop('style', None)
    return n


def transform(n, top=False):
    if not isinstance(n, Node):
        return n
    if n.tag in ('script', 'style', 'svg', '#raw'):
        return n
    n.kids = [transform(k) for k in n.kids]

    if n.tag == 'table':
        plain(n, 'nwc-table')
        wrap = Node('div', {'class': 'nwc-scroll'})
        wrap.add(n)
        return wrap
    if n.tag in ('th', 'td', 'tr', 'thead', 'tbody'):
        return plain(n)
    if n.tag == 'figure':
        plain(n, 'nwc-figure')
        for i in n.el('img'):
            i.attrs.pop('style', None)
            i.attrs.setdefault('loading', 'lazy')
        for c in n.el('figcaption'):
            plain(c)
        return n
    if n.tag != 'div':
        return n

    st = n.style
    kids = n.el()

    # anything drawn with CSS keeps every declaration it has
    if any(m in st for m in ('conic-gradient', 'radial-gradient', 'border-radius:50%', 'position:absolute',
                             'position:relative;width', 'clip-path', 'transform:', 'animation:', 'writing-mode',
                             'aspect-ratio', 'background-image')):
        return n

    # ── header: icon square + heading block ───────────────────────────────
    if len(kids) == 2 and re.search(r'width:(\d+)px;height:\1px', kids[0].style) \
            and (kids[1].el('h3') or kids[1].el('h4')):
        h = (kids[1].el('h3') or kids[1].el('h4'))[0]
        head = Node('header', {'class': 'nwc-head'})
        ic = Node('div', {'class': 'nwc-head-ic'})
        ic.add(kids[0].flat_text() or '📄')
        head.add(ic)
        box = Node('div')
        h3 = Node('h3')
        h3.kids = h.kids
        box.add(h3)
        for p in kids[1].el():
            if p is not h:
                box.add(plain(p))
        head.add(box)
        return head

    # ── stat grid ─────────────────────────────────────────────────────────
    if 'grid-template-columns:repeat(auto-fit' in st and len(kids) >= 2 and all(
            len(k.el()) == 2 and not k.el()[0].el() and len(k.el()[0].flat_text()) <= 30
            for k in kids):
        g = Node('div', {'class': 'nwc-stats'})
        for k in kids:
            a, b = k.el()
            stat = Node('div', {'class': 'nwc-stat'})
            big = Node('b')
            big.kids = a.kids
            small = Node('span')
            small.kids = b.kids
            stat.add(big)
            stat.add(small)
            g.add(stat)
        return g

    # ── note box: a rule down the left ────────────────────────────────────
    if 'border-left:4px' in st and kids and is_titleish(kids[0]):
        ic, title = split_icon(kids[0].flat_text())
        note = Node('div', {'class': 'nwc-note'})
        icon = Node('div', {'class': 'nwc-note-ic'})
        icon.add(ic or '📌')
        note.add(icon)
        body = Node('div')
        h5 = Node('h5')
        h5.add(title)
        body.add(h5)
        for k in n.kids:
            if k is not kids[0]:
                body.add(k)
        note.add(body)
        return note

    # ── panel with a title line → a section, or a titled card ─────────────
    if len(kids) >= 2 and is_titleish(kids[0]) and 'border-radius' in st and 'background' in st:
        ic, title = split_icon(kids[0].flat_text())
        big = top and len(n.flat_text()) > 220
        box = Node('section', {'class': 'nwc-sec'}) if big else Node('div', {'class': 'nwc-card'})
        head = Node('h4' if big else 'h5')
        head.add(title)
        box.add(head)
        for k in n.kids:
            if k is not kids[0]:
                box.add(k)
        return box

    # ── plain card ────────────────────────────────────────────────────────
    if re.search(r'background:(rgba\(|linear-gradient|#)', st) and 'border-radius' in st and 'padding' in st:
        return plain(n, 'nwc-card')

    # ── grids and flex rows keep their shape, lose the colours ────────────
    if st.startswith('display:grid') or st.startswith('display:flex'):
        return keep_layout_only(n)

    return n


def topic_meta(tab_id):
    """icon and label for a topic, as the hub lists it."""
    hub = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'hub.json')
    for group in json.load(open(hub, encoding='utf-8')):
        for t in group['topics']:
            if t['id'] == tab_id:
                return t.get('icon', '📄'), t['label']
    return '📄', ''


def relayout(path):
    src = open(path, encoding='utf-8', newline='').read().replace(chr(13), '')
    keep = []

    def stash(m):
        keep.append(m.group(0))
        return '<!--KEEP%d-->' % (len(keep) - 1)

    src = re.sub(r'<(script|style)\b.*?</\1>', stash, src, flags=re.S)
    builder = Build()
    builder.feed(src)
    tab = builder.root.el('div')[0]
    tab_id = tab.attrs.get('id')
    tab_cls = tab.attrs.get('class')

    inner = tab.el()
    if len(inner) == 1 and inner[0].tag == 'div' and ('text-align:left' in inner[0].style
                                                      or inner[0].attrs.get('class') == 'nwc'):
        tab.kids = inner[0].kids

    wrap = Node('div', {'class': 'nwc'})
    wrap.kids = [transform(k, top=True) for k in tab.kids]
    # every topic opens with the same kind of header
    if not any(isinstance(k, Node) and k.tag == 'header' for k in wrap.kids):
        icon, label = topic_meta(tab_id)
        if label:
            head = Node('header', {'class': 'nwc-head'})
            ic = Node('div', {'class': 'nwc-head-ic'})
            ic.add(icon)
            head.add(ic)
            box = Node('div')
            h3 = Node('h3')
            h3.add(label)
            box.add(h3)
            head.add(box)
            wrap.kids.insert(0, head)

    out = '<div id="%s" class="%s">\n%s\n</div>\n' % (tab_id, tab_cls, render(wrap))
    out = re.sub(chr(10) + '{3,}', chr(10) + chr(10), out)
    return re.sub(r'<!--KEEP(\d+)-->', lambda m: keep[int(m.group(1))], out)


def balanced(markup):
    """Count divs outside scripts, comments and attributes, where markup hides."""
    bare = re.sub(r'<(script|style)\b.*?</\1>', ' ', markup, flags=re.S)
    bare = re.sub(r'<!--.*?-->', ' ', bare, flags=re.S)
    bare = re.sub(r'=\s*"[^"]*"', chr(61) + chr(34) + chr(34), bare)
    return len(re.findall(r'<div(?=[\s>])[^>]*>', bare)) == len(re.findall(r'</div>', bare))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        markup = relayout(p)
        assert balanced(markup), p
        open(p, 'w', encoding='utf-8', newline=chr(10)).write(markup)
        print('relaid ' + p)
