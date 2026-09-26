---
name: constitution-site
description: Working rules for the รัฐธรรมนุญจำลอง site (one 5MB website_constitution.html). Load before ANY edit to that file, and again whenever a mistake happens so the lesson gets written down. Covers the structural hazard that makes broken nesting invisible, the mandatory validation script, insertion recipes, shell/encoding traps, site conventions, the commit-and-push-every-change rule, and a running log of mistakes already made — which must be appended to whenever a new one occurs.
---

# รัฐธรรมนุญจำลอง — working rules

> General lessons that apply to any website now live in the user-level skills
> **safe-web-editing** (structure checks, splicing, shell traps, headless-Chrome
> verification, git hygiene — with reusable scripts) and **antigravity-agy**
> (image generation and other delegation through the `agy` CLI). This file keeps
> what is specific to this site; where both say the same thing, this one wins.

Fictional worldbuilding site: a simulated Thai constitution, 38 chapters plus a
53-tab dashboard. Invented history, PMs, parties and institutions are
**intentional**. Never "correct" them toward real-world facts.

Almost everything lives in one file: `website_constitution.html`
(~5.5 MB, ~68k lines). Assets in `images/` (107 MB), `audio/`, `js/`, `css/`.

---

## RULE 1 — Commit and push after every change

The user's explicit standing instruction. Do not batch work.

```bash
git add -A && git commit -m "<what changed>" && git push
```

Rationale: one 5 MB file where a bad splice can corrupt the whole site. Every
commit is a restore point. During one session 12 separate pieces of work sat
uncommitted at once — a single bad write would have destroyed all of it.

If a splice goes wrong and the work is committed, recovery is
`git checkout -- website_constitution.html`. If it is not committed, there is
no recovery. **Commit first, then edit.**

---

## RULE 2 — Tag counts do NOT prove the structure is sound

This is the single most important fact about this file.

Damage here consistently takes the form of **balanced `<div>` counts with wrong
nesting order**. Every naive check passes. The page still renders. The bug only
shows as content appearing on tabs it does not belong to.

Real cases:

- A `</div>` closed `chakri-tab` early, leaving the whole ราชวงศ์จักรี body
  outside any `.db-tab-content`. It rendered on **every** tab. Counts were
  11886/11886 — perfectly balanced.
- Two new panels were spliced **inside** `kpptp-tab` instead of beside it.
  Counts balanced (58/58, 93/93, 86/86). Only the overlap check caught it.

The user has said the original damage came from **Antigravity**, which broke the
structure and could not fix it. Treat misnesting as the default suspicion.

### The validation script — run after EVERY structural edit

```python
import re
src = open('website_constitution.html', encoding='utf-8').read()
stack, extra, spans = [], [], {}
for m in re.finditer(r'<div\b([^>]*)>|</div>', src):
    if m.group(0) == '</div>':
        if stack:
            o = stack.pop()
            if o[1]: spans[o[1]] = (o[0], src[:m.start()].count('\n') + 1)
        else:
            extra.append(src[:m.start()].count('\n') + 1)
    else:
        a = m.group(1) or ''
        idm = re.search(r'id="([^"]+)"', a)
        stack.append((src[:m.start()].count('\n') + 1,
                      idm.group(1) if (idm and 'db-tab-content' in a) else None))
sp = sorted((v[0], v[1], k) for k, v in spans.items())
overlaps = [(sp[i+1][2], sp[i][2]) for i in range(len(sp)-1) if sp[i+1][0] < sp[i][1]]
buttons = set(re.findall(r"switchTab\('([^']+)'", src))
print(f"unclosed {len(stack)} | stray {len(extra)} | panels {len(spans)} | overlaps {overlaps}")
print(f"buttons {len(buttons)} == panels: {buttons == set(spans)}")
```

**Expected healthy output:**

```
unclosed 2 | stray 0 | panels 53 | overlaps []
buttons 53 == panels: True
```

- `unclosed 2` is correct and expected — `dashboard-card` and `preamble-section`
  are knowingly left open to EOF; the browser closes them. Do not "fix" these.
- `overlaps` must be `[]`. Any entry means a panel is nested inside another.
- Buttons and panels must match exactly, both directions.

Also verify every panel sits inside the tab container:

```python
ho = src[:src.index('<section id="history_and_pms"')].count('\n') + 1
hc = src[:src.index('</section>', src.index('id="kpptp-tab"'))].count('\n') + 1
outside = [k for k, (s, e) in spans.items() if not (ho < s and e < hc)]
```

### Do NOT use per-line depth counting

A naive line-by-line depth walk reports **false overlaps**, because the file
contains lines like:

```html
</div><div id="independent-organs-tab" class="db-tab-content">
```

One line closes and opens. Always scan in document order with a stack.

Likewise, a slice-and-count of one panel's line range can report 435/434 for the
same reason. Trust the stack walk, not the slice count.

---

## RULE 3 — Insertion recipe (this is where mistakes happen)

Three separate splices went wrong in one session. Follow this exactly.

### Find a tag's real span

```python
def span(marker):
    a = src.index(marker)
    s = src.rindex('<div', 0, a)      # ← the actual opening tag
    d = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', src[s:]):
        d += 1 if m.group(0) != '</div>' else -1
        if d == 0:
            return s, s + m.end()
```

**The trap:** `src.index('id="kpptp-tab"')` points at the *attribute*, not the
tag. Starting the walk there begins one tag late, so it closes one level early
and everything spliced at that point lands *inside* the panel. Always
`rindex('<div', 0, a)` first.

### Never grab the first `</section>`

`src.index('</section>')` finds the one closing `<section class="hero">` near
line 2083 — nowhere near the tabs. A panel spliced there ends up inside the hero
banner. Tab panels live inside **`<section id="history_and_pms">`**.

Assert containment before writing:

```python
host_o = src.index('<section id="history_and_pms"')
host_c = src.index('</section>', insertion_point)
assert host_o < insertion_point < host_c, "must land inside the tab container"
```

### Never end a replacement regex on a run of closing tags

Replacing a repeated block with `re.compile(r'<div ...>.*?</div></div>', re.S)`
does **not** stop at the end of the block. It stops at the first place two
closes happen to sit together — which, for a row of cards, is the end of the
*first card*. The rest of the row survives and each replacement leaves a
surplus `</div>`.

This happened while swapping five flag rows: two-cell rows kept their old
second cell, and the validator reported `unclosed 1 | stray 4`.

Match the block's real extent by walking depth from its opening tag, exactly as
in **Find a tag's real span** above — or, when the block is one line, replace
the whole line by index after asserting its shape:

```python
old = lines[n - 1]
assert old.count('</div>') == old.count('<div') + 1, 'unexpected shape'
lines[n - 1] = new_row
```

### Adding a new tab — both halves are required

1. **Panel** — insert as a *sibling* after the last panel closes, inside the host
   section: `<div id="NAME-tab" class="db-tab-content"> … </div>`
2. **Button** — beside a related one in the nav:
   ```html
   <button class="db-tab-btn" onclick="switchTab('NAME-tab', this)"
           style="border-color:rgba(R,G,B,0.6);color:#HEX;">EMOJI ชื่อแถบ</button>
   ```
3. Validate. Buttons and panels must both come out at the new count.

Keep button labels short — `🔴 พรรคสีแดง`, not a parenthetical list. Long labels
wrap to two lines and look wrong.

---

## RULE 4 — Shell and encoding traps

Every one of these cost a failed command in real sessions.

| Trap | Symptom | Fix |
|---|---|---|
| PowerShell here-string `@'…'@` in a Bash call | `@` becomes the commit subject line | Use `git commit -F -` with a Bash heredoc |
| Bash heredoc with large Thai/emoji content | `unexpected EOF while looking for matching` | Write the script or HTML to a file with the Write tool, then run/splice it |
| Python printing Thai on Windows | `UnicodeEncodeError: 'charmap' codec` | Prefix every command: `PYTHONIOENCODING=utf-8 python …` |
| `"\\v%d.js"` in a Python path | `\v` is a vertical tab → `Invalid argument` | Use raw strings or `os.path.join` |
| `grep -P` | `-P supports only unibyte and UTF-8 locales` | Use Python `re`, or `grep -oE` |
| ripgrep lookahead `(?!…)` | `look-around … is not supported` | Filter in Python instead |
| Non-greedy `.*?` across the whole file | Matches content in unrelated sections | Scope the regex to one panel's slice first |
| Downloading from Wikimedia with no User-Agent | HTTP 200 but the body is a ~2 KB HTML error page, saved happily under a `.svg`/`.png` name | Always send `curl -A "<something descriptive>"`; check the first bytes are not `<!DOCTYPE html>` |
| Counting `<svg` / `</svg>` across the whole file | Reports one unclosed tag; the extra `<svg` is a string inside minified Leaflet at line ~1361 | Only count inside markup, or ignore `<script>` regions |
| `file://` with Thai path in the browser tool | Cannot open | Validate structurally instead; browser preview is not available for this file |
| Writing a JS regex like `/renovate/` through a Python string in a Bash heredoc | The file got a literal backspace (``), the regex never matched, and the feature silently did nothing | Write JS through the Write tool or a raw string, avoid `` in spliced JS (use `(?:[=&]|$)`), then `grep` the result for `` |
| Needing to *see* a tab that only appears after a click | The Browser pane is hidden and `chrome --headless --screenshot` can't click | Drive headless Chrome over the DevTools protocol from Node (global `WebSocket`, `Runtime.evaluate` to click and scroll, `Page.captureScreenshot`); then make a PIL contact sheet and Read that one image |
| Screenshot of the preview comes back solid dark navy | The Browser pane is hidden (`tabs_context` says so); the page itself is fine | Check `tabs_context` first; while hidden, verify with `javascript_tool` (innerText, computed colour, getBoundingClientRect) instead of retrying screenshots |

**Always read a file's real bytes before assuming.** Reading
`website_constitution.html` whole fails (5 MB > 256 KB limit) — use `offset`/
`limit`, Grep, or Python.

---

## RULE 5 — Verify claims against the file, never from memory

The user checks sources. When a figure is used, be able to name the line it came
from. When asked "เอามาจากไหน", answer with line numbers.

Before writing any factual claim, grep for it. Two examples where checking
changed the answer:

- Four places said `จอมพล (กองทัพบก)`. Three were จอมพลคงฤทธิ์; **one at line
  ~40021 was จอมพลปฏิวัติ พิบูลอสงไขย — a different person.** A blind
  replace-all would have corrupted a villain's record.
- PM 4's term count was assumed to be one 8-year term. The site actually
  documents `วาระละ ๘ ปี` for the modern era only; the older constitution used
  4-year terms, making it two terms. The user had to correct this.

**Check `images/` and git history before creating any asset.** A tab having no
`<img>` does not mean no artwork exists. Before drawing or generating anything:

```bash
ls images/ | grep -i <topic>
git rev-list --all --objects | awk '{print $2}' | grep -i <topic>
```

And verify the files are what their extension claims — several are not:

```bash
head -c 40 images/<file>        # <!DOCTYPE html> means it is an error page
```

Real case: the flag tab was rewritten with seven hand-drawn SVG flags. The user
asked whether correct images already existed. They did — `flag1.svg`,
`flag4.svg` (a 65 KB white elephant) and `flag7.svg` were real artwork deleted
by commit `e28a463`, whose message claims the opposite of what it did. Of the
seven files it touched, four were Wikimedia error pages; it kept those and
deleted the three genuine ones. All `images/flag*.png` are still error pages,
referenced nowhere.

**Do not invent numbers unless told to.** When data is missing, say which fields
are missing and ask. The user will often say "คิดขึ้นมาเองได้เลย" — only then
invent, and keep invented figures internally consistent:

- seats ÷ 5 = the stated percentage (500-seat house)
- แบ่งเขต + บัญชีรายชื่อ = total seats
- raw votes ÷ popular-vote% = a turnout that grows sensibly across eras
- respect any ceiling the user sets (e.g. "must not exceed พิธา วาระ ๒" = 76.89% / 384 seats)

---

## RULE 6 — Site conventions

**คณะราษฎร vs คณะประชาราษฎร.** In canon, คณะราษฎร is หลวงประดิษฐ์มนูธรรม's
faction and is always framed negatively. Any *positive* people's movement uses
the name **คณะประชาราษฎร** (user ruling 2026-09-16) — e.g. the ๒๕๗๓ youth
movement "คณะประชาราษฎรที่ ๓" and its "หมุดประชาราษฎรที่ ๓". Never write
คณะราษฎร in a positive light. Likewise ปรีดี / เจ้าพระยาประดิษฐ์มนูธรรม is the
proven assassin in the ร.๘ case — no text may call him vindicated.

**Numerals.** Thai numerals (๐-๙) for years, counts, article numbers. Arabic is
tolerated inside statistics blocks where the site already mixes them.

**Duplicate function definitions.** `switchTab` and `playAudioMobile` are defined
both inline in the HTML and in `js/constitution.js`. **`js/constitution.js` loads
last (near line 66615) and wins.** Editing the inline copies does nothing. The
two `switchTab` bodies differ.

**Tab panels** are `<div id="X-tab" class="db-tab-content">`. `switchTab` hides
by that class — anything outside it can never be hidden.

**Audio + lyrics block** (reuse verbatim, swap colours):

```html
<div class="audio-box">
  <button type="button" onclick="playAudioMobile(this, 'audio/NAME.mp3')" …>
    <span style="font-size:15px;">▶️</span> กดเล่นเพลงบนมือถือ / Play Audio
  </button>
  <audio controls preload="metadata" playsinline webkit-playsinline src="audio/NAME.mp3" …>
    <source src="audio/NAME.mp3" type="audio/mpeg">
    เบราว์เซอร์ของคุณไม่รองรับการเล่นไฟล์เสียง
  </audio>
</div>
```
Lyrics go below in an italic box with a coloured left border.

**Person cards** (`figures-tab`, `villains-tab`) use `tri-layout` /
`tri-profile-card` / `tri-stage`. Portrait frame is 243.75 × 304.69.

**PM roster rows** (`pms-tab`) are `<tr class="pm-row" data-era="era-N">` with
exactly **7 cells**. Portrait 220 × 275.

**Party tab PM cards** carry a stat card per term: raw votes, Popular Vote %,
ส.ส. ในสภา (n/500), โพลแรก/โพลหลัง, then a 3-column grid (ส.ส. รวม / แบ่งเขต /
บัญชีรายชื่อ), plus a footer line `จัดตั้งรัฐบาลสถาปนานายกฯ คนที่ …`. The right
column carries a ฉายา badge, name, party/years line, then achievements as
bulleted items with emoji headings.

**Images.** Portraits are ratio ~0.80 (e.g. 800×1000). Crop landscape sources
centred, keep full height, save JPEG q92. Check the result with Read before
using it.

---

## RULE 7 — Cross-references must stay consistent

Facts are duplicated across tabs. Changing one means sweeping for the others.

When a new PM is added, update **all** of:
- the roster row in `pms-tab`
- the roster intro count (`ทำเนียบนายกรัฐมนตรีทั้ง ๓๓ คน`)
- the tab button label (`🏛️ ทำเนียบนายกรัฐมนตรี (๓๓ ท่าน)`)
- the previous PM's end year — two PMs cannot both be `ปัจจุบัน`
- the party card in `parties-tab` (`นายกรัฐมนตรีคนปัจจุบัน: …`)
- the democracy timeline era in `timelineData`
- the party tab card, if the party has one

Sweep afterwards:

```bash
grep -c '๒๖๙๘-ปัจจุบัน' website_constitution.html          # must be 0
grep -n 'นายกรัฐมนตรีคนปัจจุบัน' website_constitution.html  # only one Thai PM
```

**Article numbers are referenced everywhere.** On 2026-09-16 a new มาตรา ๒๙๖
(the constitution-drafting procedure) was inserted into หมวด ๑๒ and every
article from the old ๒๙๖ up shifted by one, so the charter now has
**๑,๑๖๐ มาตรา**. Doing that touched: `id="art_N"`, `data-target="N"`
cross-refs, "มาตรา N" / "ม.N" text including lists and ranges
("ม.๑,๑๕๓-๑,๑๖๐", "มาตรา ๘๐๒ และ ๑๑๖๐"), the sidebar nav ranges, the
chapter-map cards, ~160 refs across 17 dashboard tabs, and totals
("๑,๑๖๐ มาตรา"). **Never renumber inside `.compare-container`** — those panes
quote 2540 numbering even in their "ฉบับแก้ไขใหม่" half. Check afterwards that
ids run 1..N with no gaps, every `data-target` resolves, and the nav ranges are
contiguous. Historical statements keep historical counts: the referendum tab's
"ฉบับที่ผ่านมติ" stays ๑,๑๕๙ because ม.๒๙๖ was added after promulgation.
Clauses (๒)–(๗) of ม.๒๙๕ sit as loose text in a `div.normal-text` *after* the
card closes, not inside it.

**`timelineData`** (around line 2396) is an array of
`{title, desc1, desc2, desc3, result}` rendered by `selectTimelineEra(index)`.
It is index-driven with no hardcoded length, so adding entries is safe — but
each entry needs a matching `<button onclick="selectTimelineEra(N, this)">`.
Verify by executing the array with node, not by eye.

---

## RULE 8 — Record every mistake in this file, immediately

**This skill is the memory. If a mistake is not written down here, it will
happen again.** Standing instruction from the user: เรียนรู้จากความผิดพลาด.

### When something goes wrong

The moment a command fails, a splice lands in the wrong place, a fact turns out
wrong, or the user corrects something:

1. **Fix it** — and say plainly what broke and why. Never quietly re-run and
   hope. The user reads the reasoning, not just the result.
2. **Write it into this file** — into the matching rule if one fits (a shell
   failure goes in the RULE 4 table, a bad splice in RULE 3), otherwise into the
   mistake log below.
3. **Commit both together** — the fix and the skill update, in one commit, then
   push. The lesson must not outlive the session in memory alone.

### What counts as worth recording

Record it if a future session could repeat it:

- a command that failed for an environment reason (quoting, encoding, a flag)
- a wrong assumption about the file's structure or conventions
- a fact asserted without checking that turned out wrong
- a user correction — **especially** a correction, because it means the
  reasoning was wrong, not just the typing
- a near-miss caught by validation — those are the most valuable, since the
  validation is the only thing standing between a bad splice and a broken site

Do **not** record: one-off typos with no pattern, anything already covered.

### How to write an entry

State what was done, what actually happened, and the rule that prevents it.
Be concrete — line numbers, the exact wrong string, the exact right one. Vague
entries ("be careful with splices") teach nothing.

Do not soften entries to look better. An entry that hides what really happened
is worse than no entry, because it creates false confidence.

---

## Mistake log

Newest last. Entries here have all actually happened.

**Grabbed the first `</section>` in the file.** Spliced a new tab panel at
`src.index('</section>')`, which is the one closing `<section class="hero">`
near line 2083. The panel landed inside the hero banner, ~38,000 lines from the
tab container. Counts stayed balanced, so nothing looked wrong. → RULE 3:
assert the insertion point is inside `<section id="history_and_pms">`.

**Searched for an id attribute instead of the opening tag.** Used
`src.index('id="kpptp-tab"')` as the start of a div walk. That position is the
*attribute*, so the first regex match was the *next* `<div`, the depth counter
started one tag late and hit zero one level early. Two new panels were spliced
**inside** `kpptp-tab`. Div counts: 58/58, 93/93, 86/86 — all balanced. Only the
overlap check caught it. → RULE 3: always `rindex('<div', 0, a)` first.

**Used PowerShell here-string syntax in a Bash call.** `git commit -m @'…'@`
put a literal `@` on line 1, making it the commit subject. Had to amend. → RULE
4: `git commit -F -` with a Bash heredoc.

**Chained `python -c "…"` and a heredoc in one command.** Bash failed with
``unexpected EOF while looking for matching ` `` — while committing this very
skill file, which already warned about heredoc fragility. → Run validation and
commit as separate calls.

**Assumed a term length instead of checking.** Reasoned that because PM 30 is
labelled "วาระที่ ๒ และ ๓", PM 4's eight years must be one term. The user
corrected it: under รธน. ๒๔๔๕ a term was 4 years, so it is two terms. The site
states `วาระละ ๘ ปี` for the modern era only (lines 16444, 38535, 38574) — the
evidence was there and went unread. → RULE 5: grep before asserting.

**Nearly ran a replace-all across different people.** Four places contained
`จอมพล (กองทัพบก)`. Three were จอมพลคงฤทธิ์; one (~line 40021) was
**จอมพลปฏิวัติ พิบูลอสงไขย**, a different character. Checking each occurrence's
nearest `tri-profile-name` first prevented corrupting a villain's record. →
RULE 5: identify *whose* record each match belongs to before any bulk edit.

**Left twelve pieces of work uncommitted at once.** Four new tabs, four binary
assets and many edits sat unsaved while the user kept requesting more. A single
bad splice would have destroyed all of it. The user then made commit-and-push
standing policy. → RULE 1.

**Under-reported available data.** Used `๗๒.๙%` for Thaksin's 2680 election
from the roster line, without checking the fuller record at line 39207 — which
also had seat counts (๓๖๔/๕๐๐) and both poll figures (๔๑% → ๖๘.๗%). The user
asked "เอามาจากไหน" and the better source surfaced. → RULE 5: find *all*
occurrences of a fact, then use the richest one.

**Drew artwork without checking whether artwork existed.** Rebuilt the flag
tab with seven hand-made SVG flags, having only checked that the *tab* had no
`<img>`. `images/` and git history both held real files. The user had to ask
twice before the check happened. → RULE 5: search `images/` and
`git rev-list --all --objects` before creating any asset.

**Ended a replacement regex on `</div></div>`.** Swapping five flag rows, the
non-greedy match stopped at the end of the first *cell* instead of the row.
Two-cell rows kept their old second cell and each row gained a surplus close;
validator reported `unclosed 1 | stray 4`. Recovery by `git checkout` and
`git stash` were both refused by the permission classifier as irreversible, so
the fix had to go forward: rebuild the five affected lines by index. → RULE 3,
and note that reverting is not always available — prefer an edit that cannot
break in the first place.

**Trusted a commit message over the bytes.** `e28a463` says "Replace SVG flag
error files with real 320px PNG flag thumbnails from Wikipedia". It replaced
real files with error pages. Read the bytes, not the subject line.

**Derived a structure from a count instead of reading it.** Wrote that
referendum round 5 ratified "หมวด ๓๗-๓๘" because the site says ๓๘ หมวด. No
such chapters exist: the charter is หมวด ๑-๓๖ + บทเฉพาะกาล + หมวดพิเศษ
(ม.๑๑๕๒-๑๑๕๙). Then labelled the chapter map's rounds from the referendum tab's
prose ("รอบที่ ๔") when every article carries its own tag
("ประชามติรอบที่ ๔-๕"). → RULE 5: the per-article tags and the `<h>` headings
are the source of truth; extract them, don't infer them.

**Changed an emoji that appears in two tabs.** `🇪🇺 สหพันธรัฐใหม่ (TSL)`
occurs on geopolitics-tab and on world-economy-tab ("TSL / EU"); the assert
caught the second copy. Scope replacements to one panel's span.

**Invented a whole cast when the user had one.** Built the cabinet tab with 20
made-up minister names because the site named none. The user already had the
full line-up — real politicians, several holding two ministries, the PM holding
three — and replaced every name. → Before inventing *named people*, ask. Numbers
and flavour text can be invented on "คิดขึ้นมาเองได้เลย"; a roster of
characters is the user's to cast. Also: use the site's spelling of titles
(`พล.ต.อ.ทักษิณ`, 3 existing uses) over a typed variant (`พล.ตร.อ.`, 0 uses).

**Copied real-world 2475 history into canon.** The constitutions table said
ร.๗ granted the ๒๓๗๕ charter "ร่วมกับคณะราษฎร", and I copied that into a new
card. The user caught it. In this site's canon ร.๗ granted it himself, without
violence; คณะราษฎร is หลวงประดิษฐ์มนูธรรม's faction, filed under villains, and the
"๔ ทหารเสือ" refused to join it *because* the charter had already been granted
(chakri-tab). This is the same leak as Manopakorn's ๒๔๗๕ dates. → Anything
touching 2475 — คณะราษฎร, สมุดปกเหลือง, ๒๔ มิถุนายน, "ฉบับถาวร ๑๐ ธันวาคม" —
is probably real history, not canon. Check it against rama7-tab and chakri-tab
before repeating it, even when the text is already on the site.

**Read every article's badge one article late.** Each article is a card:
`<div class="article-card" id="art_N" data-origin="…">` → header with
`<span class="badge …">` → body with `มาตรา N`. The badge comes **before** the
number. Scanning forward from "มาตรา N" for the next badge returns article
N+1's. Two consequences, both real: (1) earlier in the session the user's
request to mark ม.๑๐๘ "แก้ไขจาก รธน. ๒๔๔๕" was applied to ม.๑๐๙, because the
edit was scoped "between มาตรา ๑๐๘ and มาตรา ๑๐๙" — which is ม.๑๐๙'s header;
(2) the ๒๔๔๕ tab's amended list, per-chapter bars and a "moved article" claim
were all built on shifted tags. Caught only when a tooltip forced a look at the
raw markup. → Address an article by its card: `id="art_N"`, and read its badge
between that id and `<div class="article-body">`. Never infer ownership of a
badge from proximity to the number.

---

## Known-good baseline

```
unclosed 2 (dashboard-card, preamble-section) | stray 0 | panels 53 | overlaps []
buttons 53 == panels: True
13 inline <script> blocks, all pass node --check
0 broken local references
pms-tab: 34 rows (1 header + 33 PMs), every row 7 cells
charter: 1,160 article cards art_1..art_1160 contiguous; 377 data-target cross-refs all resolve;
         38 sidebar chapters with contiguous ranges ม.๑-๑,๑๖๐; data-origin values:
         original, modified, ch13_16, ch17_26, ch27_36, special, transitional, later
```

(Panel count has since grown past 53 — trust `validate.py`'s buttons == panels check over the number above.)

Check all inline scripts:

```python
for k, m in enumerate(re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', src, re.S | re.I)):
    open(f'chk_{k}.js', 'w', encoding='utf-8').write(m.group(1))
    # then: node --check chk_k.js
```

Check every local asset resolves:

```python
missing = [f for f in set(re.findall(r'(?:src|href)="([^"]{1,200})"', src))
           if not f.startswith(('http', '#', 'data:', 'mailto:', 'javascript:'))
           and not os.path.exists(f.split('?')[0])]
```

## Lesson: animated 3D scenes (index.html intro hall, หอภาพเหมือน tab)

- A CSS 3D walk (perspective + moving `translate3d`, big gradient walls, box-shadows, animated `filter: blur`) ran at **4-7 fps** in the user's screen recording, even after moving the motion to CSS transitions. The browser re-rasterises 3D layers whenever their projected scale changes, which is every frame of a walk.
- What works: draw the scene on a `<canvas>`. Paint frames, gilding and captions **once** into offscreen canvases, fake the angle with thin vertical strips (strip count from the edge rise, x snapped to device pixels so seams don't show), crossfade a tiny pre-blurred JPEG to the sharp one instead of blurring. Measured 0.5-0.7 ms per frame.
- To check smoothness, don't trust a hidden Browser pane (rAF and CSS transitions stall there). Ask for a screen recording and measure per-frame change with OpenCV (`cv2` and ffmpeg are installed). To see a canvas, POST `toDataURL` to a throwaway local receiver and Read the file; don't print base64 into the transcript.
- Where it lives now: `index.html` is the entry page (seal intro, then the auto walk; no gallery there). The walk-it-yourself version is `js/portrait-hall.js` (`<portrait-hall>`) on `portrait-hall-tab` in group 1. Both read the roster from `js/hall-data.js`; portraits are `images/hall/<id>.jpg` + `<id>b.jpg`. Only King Rama IX gets the gilded frame (the Claude Design study also gilded PM 33 — don't copy that).
- A canvas component inside a hidden tab has zero size: guard `layout()` against it and re-check until the tab opens. Never let one `requestAnimationFrame` be the only wake-up: a kick made while the tab is in the background can hang forever, so pair it with a timeout fallback.

## The rebuild (website_new.html) — in progress since 2026-09-17

The user asked for the whole site to be rebuilt with the same content: formal, dark (any colour, just not bright), still one page, done in phases. It is **not** a re-theme — a `?renovate` recolour was tried and rejected.

- `tools/build_site.py` generates `website_new.html` from `website_constitution.html` using `tools/site_template.html`; styles in `css/site.css`, behaviour in `js/site.js`, glossary lifted into `js/glossary-data.js`. Re-run the build after editing charter content in the old file; never hand-edit `website_new.html` while the generator owns it.
- Phase 1 (done): shell, table of contents, search + origin filters, jump-to-article, 2540 comparisons, cross-ref previews, glossary, mourning mode (reuses the dedication block verbatim and the saved `constTheme = 'bw'`), full charter.
- Next phases: move the 68 dashboard tabs group by group into the new page's archive section; until then it links to the old page.
- Check a build with: div/section/article balance, `art_1..art_1160` contiguous, every `.cross-ref` resolves, 11 compare panels, no missing local files — then DevTools screenshots.

## Re-laying out the new site's tabs (tools/relayout.py)

- The 68 topic panels carry their looks in **inline styles**, so a structural
  transformer can re-shape them: header, stat grid, note box, section, card,
  table, figure become `.nwc-*`.  Run it per file, then check the visible text
  is unchanged (ignoring emoji) before writing.
- **Run it once per file.**  A second pass wraps `.nwc` inside `.nwc` and adds a
  second header.  The tool now unwraps an existing `.nwc` first, but a check for
  `class="nwc-head"` appearing twice is the quick way to spot damage.
- **Never strip a style that draws something**: conic/radial gradients, 50%
  radii, absolute positioning, transforms, animations.  Those panels keep every
  declaration.
- **Self-closing tags matter inside SVG.**  Re-emitting `<rect ... />` as
  `<rect ...>` nests the following shapes inside it and the chart renders empty.
  Only SVG shapes may be serialised self-closed; `<div/>` must become a pair.
- `&D` in "R&D" arrives at HTMLParser as an entity reference; only re-add the
  semicolon when the name really is an HTML5 entity.
- Counting `<div` to check balance also counts markup inside scripts, comments,
  attributes and prose.  Strip those first, and count `<div...>` with its `>`.

## The backslash trap, again

Writing Python through a `Bash` heredoc mangles backslashes: `\b` and `\n`
reach the file as a real backspace or newline and the script breaks in a way that
only shows up as a "SyntaxWarning" or a regex that never matches.  Use `chr(10)`,
`chr(92)` or the `Write` tool instead.

## Headless Chrome reports prefers-reduced-motion: reduce

Both the CDP screenshot runner and the in-app browser pane report reduced motion,
so anything gated on it never appears in a screenshot.  Degrade to a fade instead
of removing the element, and the animation stays verifiable.

**The user's own machine has reduced motion on too.**  Their recording of the
ten-second intro showed the Garuda vanishing at ~3.2 s, before the title ever
appeared — the short "reduce" branch, not a bug in the timeline.  So a reduced
branch must keep the **same duration and the same beats**; only the movement
changes: no push-in, no grain jitter, no bounce, no sweep — fades on the same
delays.  Cutting the sequence short is what reads as "โดนตัด".

## Shared css/js carry a ?v= stamp — bump it on every change

`website_constitution.html` and `tools/site_template.html` load
`css/constitution.css`, `css/site.css`, `js/constitution.js` and
`js/glossary-data.js` with `?v=YYYYMMDD`.  Editing one of those files without
bumping the stamp means the browser keeps the old copy: twice in one session a
fix looked like it had not worked at all (the glossary's new buttons, then an
image that kept its old crop) because the CDP profile and the user's browser
both served the cached file.  Bump the stamp in **both** files, rebuild, then
screenshot.

## Never animate the whole `<body>` on these pages

Handing the new site's intro over to the page with
`html.nw-page-in body { animation: ... transform/opacity }` blanked the screen
for about **0.7 s** before anything appeared — the user's recording shows solid
black from 4.0 s to 4.7 s.  A 5.9 MB document promoted to its own composited
layer cannot be rasterised in one frame.  Animate a small overlay instead: a
fixed veil div that fades out, or the iris circle, both of which are cheap.
The same trap explains an earlier "the iris never opens" reading of a headless
capture: the black frames were the stall, not a slow animation.

## A link audit that only greps `href=` misses half the site's navigation

Reported to the user that `website_constitution.html` was a dead end with no way
back to `index.html`.  It has one: a `<button class="db-tab-btn"
onclick="window.location.href='index.html'">หน้าแรก 🏠</button>` at line ~1673.
The sweep had been `grep -oE 'href="(index|website_new)\.html[^"]*"'`, which
cannot see navigation done through `onclick`, `location.href`, `location.assign`
or `window.open`.  The user answered with a screenshot of the button.

→ When auditing navigation on these pages, search for the **destination**, not
the attribute:

```bash
grep -oE "[^\"']*index\.html[^\"']*" website_constitution.html | sort -u
```

and remember this file drives most of its UI from `onclick`, not from `<a>`.
The same blind spot applies to counting tabs (`switchTab('x-tab', this)`) and to
audio (`playAudioMobile(this, 'audio/…')`).

## Headless Chrome for layout checks — the Browser pane cannot do it

`document.documentElement.clientWidth` is **0** while the Browser pane is hidden,
so every element's `getBoundingClientRect()` collapses and an overflow check
reports all 68 tabs as broken.  Run layout audits through the CDP harness with
`Emulation.setDeviceMetricsOverride` instead (`scratchpad/layout_check.mjs`),
which gives a real viewport.  Measured that way: at 1440 px both sites are clean;
at 390 px the new site overflows on 19 of 68 tabs and the old site on 43.

## The backslash trap bit again — and a `%` one beside it

Patching a Python file through a `Bash` heredoc turned `r'<div\b[^>]*>'` into
`r'<div<BS>[^>]*>'` — a literal 0x08.  The file *ran*, the regex silently matched
slightly the wrong thing, and the damage was invisible in every editor view;
`sed -n '130p' file | cat -A` is what showed the `^H`.  Two lessons:

- never write a regex through a heredoc — use the `Write`/`Edit` tool, or build
  the string with `chr(92) + 'b'`;
- when a `Edit` says "String to replace not found" on a line you can see, the
  line contains a character you cannot.  Check with `cat -A` before assuming the
  tool is wrong.

In the same script, `'…๘๙.๔% ให้…' % (a, b, c)` raised
`TypeError: not enough arguments for format string`.  Thai percentages are
common in this site's copy — double every literal `%` in a `%`-formatted
template, or use `.format`/f-strings.

## Nav on the old site is `onclick`, not `href`

Auditing "can you get back to the home page from here" with
`grep 'href="index.html"'` reported the old site as a dead end.  It is not:
line ~1673 carries `<button class="db-tab-btn"
onclick="window.location.href='index.html'">หน้าแรก 🏠</button>`.  Most of this
file's navigation, audio and tab switching is driven from `onclick`
(`switchTab`, `playAudioMobile`, `window.location.href`), so search for the
**destination string**, never for the attribute.

## Insert beside a sibling card by walking out from a marker

To add a card next to an existing one (the new song beside เพลงมหารัฐบุรุษ),
do not chain `s.index('</div>', …)` three times to "walk out" of it — that is
the RULE 3 trap in another costume.  Walk outward instead: from the marker's
position, step back through `<div` openings and, for each, walk its depth to
find the matching close; take the first span that reaches past the marker *and*
contains every other string the real card must contain (its heading and its
`<audio src>`).  That lands on the card, not on an inner wrapper.

## Check `git status` before `git add -A`

The user drops their own material into the project folder (e.g. a
`ครอบครัวนิวตรอน/` folder and its `.zip`, added 2026-09-22). A blind
`git add -A` committed and pushed them with an unrelated change. This time
the user wanted them in the repo anyway, but that is luck, not process.
Look at `git status --short` first, and when something appears that this
session did not create, name it and ask — or stage explicit paths.
`test.zip` is the one file the user wants kept out.

## "Lock" a date means label it, not move it

When the user asks to lock or fix the date a section's data comes from
(e.g. the family section "ข้อมูล ณ วันที่ ๑ มกราคม ๒๗๓๑"), that is a
statement of when the snapshot was taken. It is not a request to move the
site's present year or any event date. Compute what the snapshot implies
(ages from real birthdays on that day) and leave the timeline alone. A
round of offering to shift the present to ๒๗๓๒ cost several turns before
the user spelled this out.

## `%%` leaked into CSS from %-formatted templates

Three old-site panels (มหาราช, SEATO, THE ATOM GROUP) went live with
`width:100%%`, `max-width:100%%` and `0%%, … 100%%` gradients: the markup was
built as a `'…' % (…)` template, where `%%` is right, then the template text was
reused somewhere that never ran the `%` operator. Browsers drop the invalid
declaration, so images lost their width and gradients vanished — silently.
Found 2026-09-26 by accident while reading another panel; 11 in the old file,
3 in `src/tabs`. → Build markup with f-strings, and before writing any panel
`assert '%%' not in fragment`; grep the whole file for `%%` after a session.

## Adding a PM also moves the portrait halls

`index.html` and `js/portrait-hall.js` placed PMs in pairs and "PM 33 alone"
with a hard-coded `i === 32` and slot `21`. When PM 34 was added it landed in
slot 21 as well — on top of PM 33's solo frame — and nobody noticed. Both now
compute the last slot from `HALL_DATA.pms.length` (the latest PM stands alone
at the end). When adding a PM: add the row to `js/hall-data.js`, the two hall
images `images/hall/pN.jpg` + `pNb.jpg` (360×460, `b` = blurred), and bump the
`?v=` on `hall-data.js` / `portrait-hall.js` in index, old site and template.

## A new PM's ideology badge copies the party's existing badge

Gave PM 35 (ก้าวไกล) the badge "เสรีนิยมก้าวหน้า (ขั้วส้มแดง)" — invented a
sub-label. Every other ก้าวไกล PM already carries
"เสรีนิยมก้าวหน้า (โดยอนุรักษ์สถาบันกษัตริย์ไว้)"; the user corrected it. →
When adding a PM, copy the whole `pm-ideology` span from an earlier PM of the
same party (text and colours), don't compose a new one.

## `rindex('<div', 0, a + 1)` does not find the tag that starts at `a`

Replacing the whole `election-2731-tab` panel, the span helper did
`s.rindex('<div', 0, a + 1)` with `a` already on `<div id="…"`. The search
window `s[0:a+1]` cannot contain a 4-character match that starts at `a`, so it
returned the *previous* `<div` — the end of the preceding panel — and the new
panel overwrote that block while the old panel survived. The validator still
said OK (balanced, 70 panels); only `grep -c 'id="election-2731-tab"'` = 2 and
leftover old figures showed it. Recovered with `git checkout` of the files this
script alone had changed. → Use
`st = a if s.startswith('<div', a) else s.rindex('<div', 0, a)`, and after
replacing a panel assert its id occurs exactly once and grep for the old text.

## A note anchored on a *reference* to a tab lands in the wrong tab

The "รัฐบาลชุดปัจจุบัน" note meant for the old site's `cabinet-tab` was spliced
next to the phrase `คณะรัฐมนตรีชุดล่าสุดที่บันทึกไว้` — but the first match
of that phrase outside the heading was a cross-reference inside
`public-finance-tab` ("ดูแถบ … คณะรัฐมนตรีชุดล่าสุดที่บันทึกไว้"). The note sat
in the finance tab for two sessions; the validator cannot see this (structure
was fine). Found only when a later edit asserted the note was inside the
cabinet panel. → Scope every search to the target panel's span first
(`s.index(x, panel_start, panel_end)`), and after inserting, check which
`db-tab-content` panel the new text actually sits in.

## Cabinet tab holds several governments

`cabinet-tab` now has a switcher (`div[data-cabs]`, buttons `.cab-btn`, sets
`div[data-cab="rome|banyat|atom2"]`, default `rome` — the current government) driven by inline
`onclick`, with its own small `<style>`. Rome's set is a
placeholder with `id="cab-rome-list"`; Banyat's set is deliberately an all-black "ไม่มีข้อมูล" box (user: his cabinet changed every week, so there is no stable line-up) — do not fill it — when the user supplies a line-up,
replace that placeholder box with the minister grid (copy the atom2 markup).
Never delete an older cabinet; add a new set and button instead.

Rome's cabinet was filled 2026-09-26 from the user's table (21 ministries,
15 people): cards are generated with the ministry number as
`images/ministry_N.png`, a "ควบ …" badge for anyone holding several posts
(let that badge wrap — a nowrap one overflowed the card) and an "อดีตนายกฯ"
badge for former PMs. The headless-Chrome profile caches HTML: when a check
shows the pre-edit page, add `?nc=N` to the URL before suspecting the edit.

**Former-PM badges from memory missed three people.** The first Rome cabinet
marked only Thaksin, Somkid and Piyabutr as อดีตนายกฯ; Thanathorn (16),
Nattaphong (19) and Parit (20) are former PMs too and got no badge. → Before
tagging anyone "อดีตนายกฯ", run every minister's name against
`js/hall-data.js` (`node -e` over `HALL_DATA.pms`) and take the numbers from it.

Rome's cabinet cards carry a 96×120 face (same as the PM box). Faces are
192×240 thumbnails in `images/cab/<key>.jpg` (don't point at the 3000 px
originals; `images/pm17.jpg` is a 1×1 stub — Pita's photo is `pita.jpg`).
People without a photo have `<div data-photo-pending="NAME" …>👤 รอรูป</div>`:
when the user sends one, crop 4:5, save to `images/cab/`, and replace that
div (every occurrence of the name) with
`<img src="images/cab/KEY.jpg" alt="NAME" loading="lazy" style="width: 96px; height: 120px; border-radius: 10px; border: 2px solid PARTYCOLOUR; flex-shrink: 0; object-fit: cover">`.

**Finding photos of real politicians (user: any source is fine, the site is private).**
What worked 2026-09-26: (1) th.wikipedia `prop=pageimages&piprop=original`;
(2) party sites are WordPress — `https://<site>/wp-json/wp/v2/media?search=<name>`
lists every upload with size (peoplesparty.or.th had official portraits;
ptp.or.th only news graphics); (3) for the rest, Bing Images in the in-app
browser, then read `a.iusc[m]` → `murl` with `javascript_tool`. Scripted
requests to Bing/DuckDuckGo get empty pages or 403, and WebSearch/WebFetch
were erroring. Always contact-sheet the candidates and reject graphics with
text, mid-shout shots and blurry crowd photos.
