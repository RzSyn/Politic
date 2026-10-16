# -*- coding: utf-8 -*-
"""Structure check for website_constitution.html (see .claude/skills/constitution-site RULE 2).
Healthy: unclosed 2 | stray 0 | overlaps [] | buttons==panels True | outside [] | broken refs []"""
import io, os, re, sys

f = sys.argv[1] if len(sys.argv) > 1 else 'website_constitution.html'
src = io.open(f, encoding='utf-8').read()
clean = re.sub(r'<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->',
               lambda m: re.sub(r'[^\n]', ' ', m.group(0)), src, flags=re.S | re.I)
stack, stray, spans = [], 0, {}
for m in re.finditer(r'<div\b([^>]*)>|</div>', clean):
    if m.group(0) == '</div>':
        if stack:
            s, pid = stack.pop()
            if pid:
                spans[pid] = (s, m.end())
        else:
            stray += 1
    else:
        a = m.group(1) or ''
        idm = re.search(r'\bid="([^"]+)"', a)
        stack.append((m.start(), idm.group(1) if idm and 'db-tab-content' in a else None))
sp = sorted((s, e, k) for k, (s, e) in spans.items())
overlaps = [(sp[i + 1][2], sp[i][2]) for i in range(len(sp) - 1) if sp[i + 1][0] < sp[i][1]]
buttons = set(re.findall(r"switchTab\('([^']+)'", src))
ho = clean.index('<section id="history_and_pms"')
hc = clean.index('</section>', max(e for s, e in spans.values()))
outside = [k for k, (s, e) in spans.items() if not (ho < s and e < hc)]
refs = set(re.findall(r'(?:src|href)="([^"#?]{1,200})(?:[?#][^"]*)?"', src))
broken = sorted(r for r in refs if not r.startswith(('http', 'data:', 'mailto:', 'javascript:', '//')) and not os.path.exists(r))
ok = not stray and not overlaps and buttons == set(spans) and not outside and not broken
print(f'unclosed {len(stack)} | stray {stray} | panels {len(spans)} | overlaps {overlaps} | buttons==panels {buttons == set(spans)} '
      f'| outside {outside} | broken refs {broken[:5]}  => {"OK" if ok else "CHECK"}')
sys.exit(0 if ok else 1)
