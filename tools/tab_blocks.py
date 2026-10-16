# -*- coding: utf-8 -*-
"""Render one tab's content twice from a small block list: for the new site (.nwc components)
and for the old site (inline styles).  Used for the story tabs added since 2026-09 (by-election,
ส.ส.ผู้ยืนหยัด, welfare, protest ...).

Blocks:
  ('stats', [(big, small), ...])      ('h', section title)          ('sub', small heading)
  ('p', html)                          ('note', html)                ('quote', html)
  ('list', [html, ...])                ('table', headers, rows)      ('time', [(when, title, html), ...])
  ('split', img, alt, caption, [(label, value), ...])               ('figure', img, alt, caption[, max_width_px])
  ('raw', new_site_html, old_site_html)

old_render(..., accent=('#fdba74', '251,146,60')) picks the old site's colour.
"""
import re


def new_render(icon, title, lead, blocks):
    o = ['<div class="nwc">',
         f'  <header class="nwc-head"><div class="nwc-head-ic">{icon}</div><div><h3>{title}</h3><p>{lead}</p></div></header>']
    sec = False
    for b in blocks:
        k = b[0]
        if k == 'h':
            if sec:
                o.append('</section>')
            o += ['<section class="nwc-sec">', f'  <h4>{b[1]}</h4>']
            sec = True
        elif k == 'sub':
            o.append(f'  <h5 class="nwc-subhead">{b[1]}</h5>')
        elif k == 'stats':
            o.append('  <div class="nwc-stats">' + ''.join(f'<div class="nwc-stat"><b>{x}</b><span>{y}</span></div>' for x, y in b[1]) + '</div>')
        elif k == 'p':
            o.append(f'  <div class="nwc-body"><p>{b[1]}</p></div>')
        elif k == 'quote':
            o.append(f'  <div class="nwc-note"><p>💬 <em>{b[1]}</em></p></div>')
        elif k == 'note':
            o.append(f'  <div class="nwc-note"><p>{b[1]}</p></div>')
        elif k == 'list':
            o.append('  <div class="nwc-body"><ul class="nwc-list">' + ''.join(f'<li>{x}</li>' for x in b[1]) + '</ul></div>')
        elif k == 'table':
            o.append('  <div class="nwc-scroll"><table class="nwc-table"><thead><tr>' + ''.join(f'<th>{x}</th>' for x in b[1]) +
                     '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in b[2]) + '</tbody></table></div>')
        elif k == 'time':
            o.append('  <div class="nwc-time">' + ''.join(
                f'<div class="nwc-time-row"><div class="nwc-when">{w}</div><div><h5>{t}</h5><p>{p}</p></div></div>' for w, t, p in b[1]) + '</div>')
        elif k == 'split':
            _, img, alt, cap, rows = b
            o.append(f'  <div class="nwc-split"><figure class="nwc-figure"><img src="{img}" alt="{alt}" loading="lazy"><figcaption>{cap}</figcaption></figure>'
                     '<div><dl class="nwc-dl">' + ''.join(f'<dt>{x}</dt><dd>{y}</dd>' for x, y in rows) + '</dl></div></div>')
        elif k == 'raw':
            o.append(b[1])
        elif k == 'figure':
            mw = b[4] if len(b) > 4 else 560
            o.append(f'  <figure class="nwc-figure" style="max-width: {mw}px; margin: 0 auto 14px"><img src="{b[1]}" alt="{b[2]}" loading="lazy" style="width: 100%; height: auto; object-fit: contain"><figcaption>{b[3]}</figcaption></figure>')
        else:
            raise ValueError(k)
    if sec:
        o.append('</section>')
    o.append('</div>')
    return '\n'.join(o)


def old_render(icon, title, lead, blocks, accent=('#fdba74', '251,146,60')):
    C, rgb = accent
    BOX = f'background:rgba(15,18,25,0.6); border:1px solid rgba({rgb},0.28); border-radius:12px; padding:16px 18px;'
    TXT = 'font-size:13.5px; color:var(--text-muted); line-height:1.85;'
    TD = 'padding:8px 11px; border-bottom:1px solid rgba(255,255,255,0.07); vertical-align:top;'
    o = [f'<div style="background:linear-gradient(135deg, rgba({rgb},0.10) 0%, rgba(15,23,42,0.95) 100%); border:1px solid rgba({rgb},0.35); border-radius:18px; padding:26px;">',
         f'  <div style="display:flex; gap:16px; align-items:center; margin-bottom:18px;"><div style="font-size:38px;">{icon}</div><div><h3 style="color:{C}; font-family:\'Outfit\',sans-serif; margin:0 0 6px; font-size:25px; font-weight:800;">{title}</h3><p style="color:var(--text-muted); font-size:14px; margin:0; line-height:1.7;">{lead}</p></div></div>']
    for b in blocks:
        k = b[0]
        if k == 'h':
            o.append(f'  <div style="font-family:\'Outfit\',sans-serif; font-size:17px; font-weight:800; color:{C}; margin:28px 0 12px;">{b[1]}</div>')
        elif k == 'sub':
            o.append(f'  <div style="font-size:15px; font-weight:700; color:{C}; margin:16px 0 8px;">{b[1]}</div>')
        elif k == 'stats':
            o.append('  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px;">' + ''.join(
                f'<div style="{BOX} text-align:center;"><div style="font-family:\'Outfit\',sans-serif; font-size:21px; font-weight:800; color:{C};">{x}</div>'
                f'<div style="font-size:11.5px; color:var(--text-muted); margin-top:5px; line-height:1.5;">{y}</div></div>' for x, y in b[1]) + '</div>')
        elif k == 'p':
            o.append(f'  <div style="{TXT} margin-bottom:10px;">{b[1]}</div>')
        elif k in ('note', 'quote'):
            body = f'💬 <em>{b[1]}</em>' if k == 'quote' else b[1]
            o.append(f'  <div style="background:rgba({rgb},0.08); border:1px solid rgba({rgb},0.3); border-left:4px solid {C}; border-radius:10px; padding:13px 16px; margin:12px 0; {TXT}">{body}</div>')
        elif k == 'list':
            o.append(f'  <ul style="{TXT} margin:0 0 10px; padding-left:22px;">' + ''.join(f'<li>{x}</li>' for x in b[1]) + '</ul>')
        elif k == 'table':
            o.append('  <div style="overflow-x:auto; margin-bottom:10px;"><table style="width:100%; border-collapse:collapse; min-width:520px; font-size:13px; color:var(--text-muted);"><tr>' +
                     ''.join(f'<th style="text-align:left; {TD} color:{C}; border-bottom:1.5px solid {C};">{x}</th>' for x in b[1]) + '</tr>' +
                     ''.join('<tr>' + ''.join(f'<td style="{TD}">{c}</td>' for c in r) + '</tr>' for r in b[2]) + '</table></div>')
        elif k == 'time':
            for w, t, p in b[1]:
                o.append(f'  <div style="{BOX} border-left:3px solid {C}; margin-bottom:12px;"><div style="font-family:\'Outfit\',sans-serif; font-size:12px; font-weight:800; color:{C}; margin-bottom:4px;">{w}</div>'
                         f'<div style="font-size:15px; font-weight:700; color:var(--text); margin-bottom:4px;">{t}</div><div style="{TXT}">{p}</div></div>')
        elif k == 'split':
            _, img, alt, cap, rows = b
            o.append('  <div style="display:flex; gap:20px; flex-wrap:wrap; align-items:flex-start;">'
                     f'<div style="flex:0 1 260px; max-width:100%;"><img src="{img}" alt="{alt}" loading="lazy" style="width:100%; border-radius:12px; border:2px solid rgba({rgb},0.45); display:block;"><div style="font-size:11.5px; color:var(--text-muted); margin-top:7px;">{cap}</div></div>'
                     '<div style="flex:1 1 320px;">' + ''.join(
                         f'<div style="display:flex; gap:12px; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.06); flex-wrap:wrap;"><div style="flex:0 0 120px; font-size:12.5px; font-weight:700; color:{C};">{x}</div>'
                         f'<div style="flex:1 1 200px; font-size:13.5px; color:var(--text-muted); line-height:1.8;">{y}</div></div>' for x, y in rows) + '</div></div>')
        elif k == 'raw':
            o.append(b[2])
        elif k == 'figure':
            mw = b[4] if len(b) > 4 else 560
            o.append(f'  <div style="max-width:{mw}px; margin:10px auto 16px;"><img src="{b[1]}" alt="{b[2]}" loading="lazy" style="width:100%; height:auto; border-radius:12px; display:block;"><div style="font-size:11.5px; color:var(--text-muted); margin-top:7px; text-align:center;">{b[3]}</div></div>')
        else:
            raise ValueError(k)
    o.append('</div>')
    return '\n'.join(o)


def balanced(x):
    return len(re.findall(r'<div\b[^>]*>', x)) == x.count('</div>')


def div_span(s, start):
    """End offset of the <div> that opens at `start` (which must be the '<' of that tag)."""
    assert s.startswith('<div', start), s[start:start + 30]
    d = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', s[start:]):
        d += -1 if m.group(0) == '</div>' else 1
        if d == 0:
            return start + m.end()
    raise ValueError('unclosed div')
