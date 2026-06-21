# generate_website.py — สร้างเว็บไซต์รัฐธรรมนูญจำลองฉบับสมบูรณ์
import os, re, sys, html as html_mod
sys.stdout.reconfigure(encoding='utf-8')

wd = r"c:\Users\ASUA\OneDrive\Documents\รัฐธรรมนุญจำลอง"
processed_text_path = os.path.join(wd, "processed_constitution.txt")
output_html_path = os.path.join(wd, "website_constitution.html")

def to_thai(n):
    m = {'0':'๐','1':'๑','2':'๒','3':'๓','4':'๔','5':'๕','6':'๖','7':'๗','8':'๘','9':'๙'}
    return ''.join(m.get(d,d) for d in str(n))

with open(processed_text_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_ch1 = text.find("หมวด ๑")
cover_and_preamble = text[:idx_ch1].strip()
body_text = text[idx_ch1:].strip()
cover_pars = [p.strip() for p in re.split(r'\n\s*\n', cover_and_preamble) if p.strip()]
body_pars = [p.strip() for p in re.split(r'\n\s*\n', body_text) if p.strip()]

# --- Classify paragraphs and assign origins ---
MODIFIED_MARKERS = [
    "ปวงชนชาวไทยทรงใช้อำนาจอธิปไตยได้โดยตรง",
    "การติชม การวิพากษ์วิจารณ์",
    "การยึดอำนาจการปกครอง การรัฐประหาร",
    "ถอดถอน (Recall)",
    "ความเป็นส่วนตัวทางดิจิทัล",
    "ผู้แจ้งเบาะแสการทุจริต",
    "ห้าพันคน มีสิทธิเข้าชื่อร้องขอต่อประธานรัฐสภา",
    "ดำรงตำแหน่งนายกรัฐมนตรีติดต่อกันเกินกว่า",
    "ผลผูกพันคณะรัฐมนตรี รัฐสภา",
    "ดำรงตำแหน่งครบกำหนดตามมาตรา ๒๐๑ วรรคสาม",
    "ห้าพันคน มีสิทธิเข้าชื่อร้องขอต่อประธานวุฒิสภา",
    "ประชาชนผู้มีสิทธิเลือกตั้งจำนวนไม่น้อยกว่าห้าหมื่นคนร่วมกันเข้าชื่อเสนอ สมาชิก",
    "ห้าพันคน มีสิทธิเข้าชื่อร้องขอต่อประธานรัฐสภาเพื่อให้รัฐสภาพิจารณากฎหมายในเรื่องใด",
]

ORIGIN_LABELS = {
    'original': ('คงเดิมจาก รธน. ๒๔๔๕', 'badge-original'),
    'modified': ('แก้ไขโดยสภาร่างรัฐธรรมนูญ', 'badge-modified'),
    'ch13_16': ('สภาร่างฯ + ประชามติรอบที่ ๑-๒', 'badge-assembly'),
    'ch17_26': ('ประชามติรอบที่ ๓', 'badge-ref3'),
    'ch27_36': ('ประชามติรอบที่ ๔-๕', 'badge-ref45'),
    'special': ('ประชามติรอบที่ ๕ (พิเศษ)', 'badge-special'),
    'transitional': ('บทเฉพาะกาล (คงเดิม)', 'badge-original'),
}

# Parse into structured data
chapters = []
current_chapter = None
art_counter = 1
current_zone = 'original'  # original, ch13_16, transitional, ch17_26, ch27_36, special

for pt in body_pars:
    is_chapter = pt.startswith("หมวด") or pt.startswith("=") or pt.startswith("หมวดพิเศษ")
    is_transitional = pt.startswith("บทเฉพาะกาล")
    is_part = pt.startswith("ส่วน")
    is_article = pt.startswith("มาตรา")
    is_sig = pt.startswith("ผู้รับสนอง")

    if is_chapter or is_transitional:
        clean = pt.replace("=","").strip()
        title_lines = [l.strip() for l in clean.split('\n') if l.strip()]
        title = ' '.join(title_lines)

        # Determine zone
        if "หมวด ๑๓" in pt or "หมวด ๑๔" in pt or "หมวด ๑๕" in pt or "หมวด ๑๖" in pt:
            current_zone = 'ch13_16'
        elif is_transitional:
            current_zone = 'transitional'
        elif "หมวดพิเศษ" in pt or "อำนาจสูงสุดพิทักษ์ประชาชน" in pt:
            current_zone = 'special'
        elif any(f"หมวด {to_thai(n)}" in pt for n in range(17, 27)):
            current_zone = 'ch17_26'
        elif any(f"หมวด {to_thai(n)}" in pt for n in range(27, 37)):
            current_zone = 'ch27_36'
        elif any(f"หมวด {to_thai(n)}" in pt for n in range(1, 13)):
            current_zone = 'original'

        ch_id = f"ch_{len(chapters)}"
        current_chapter = {'id': ch_id, 'title': title, 'zone': current_zone, 'items': []}
        chapters.append(current_chapter)

    elif is_part and current_chapter:
        current_chapter['items'].append({'type': 'part', 'text': pt})

    elif is_article and current_chapter:
        match = re.match(r'^(มาตรา\s+[๐-๙/\s]+(?:ทวิ|ตรี|จัตวา)?)\s+(.*)', pt, re.DOTALL)
        if match:
            _, content = match.groups()
            label = f"มาตรา {to_thai(art_counter)}"
            
            # Determine origin
            if current_zone == 'original':
                origin = 'original'
                for marker in MODIFIED_MARKERS:
                    if marker in content:
                        origin = 'modified'
                        break
            else:
                origin = current_zone
            
            current_chapter['items'].append({
                'type': 'article',
                'num': art_counter,
                'label': label,
                'content': content,
                'origin': origin,
            })
            art_counter += 1

    elif is_sig:
        if current_chapter:
            current_chapter['items'].append({'type': 'signature'})
    else:
        if current_chapter:
            current_chapter['items'].append({'type': 'text', 'text': pt})

total_articles = art_counter - 1

# --- Build HTML ---
def esc(s):
    return html_mod.escape(s)

def render_article_html(item):
    label = esc(item['label'])
    origin_key = item['origin']
    origin_label, badge_class = ORIGIN_LABELS.get(origin_key, ORIGIN_LABELS['original'])
    
    content = item['content']
    lines = content.split('\n')
    
    parts = []
    first_line = esc(lines[0].strip()) if lines else ''
    parts.append(f'<p class="article-text"><span class="art-num">{label}</span> {first_line}</p>')
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        lm = re.match(r'^(\([๐-๙]+\))\s*(.*)', line)
        if lm:
            num, txt = lm.groups()
            parts.append(f'<p class="list-item"><span class="list-num">{esc(num)}</span> {esc(txt)}</p>')
        else:
            parts.append(f'<p class="sub-para">{esc(line)}</p>')
    
    body_html = '\n'.join(parts)
    return f'''<div class="article-card" id="art_{item['num']}" data-origin="{origin_key}">
  <div class="article-header">
    <span class="badge {badge_class}">{origin_label}</span>
  </div>
  <div class="article-body">{body_html}</div>
</div>'''

# Render chapters for nav
nav_items = []
for ch in chapters:
    first_art = ''
    last_art = ''
    for it in ch['items']:
        if it['type'] == 'article':
            if not first_art:
                first_art = str(it['num'])
            last_art = str(it['num'])
    range_str = f" (ม.{to_thai(int(first_art))}-{to_thai(int(last_art))})" if first_art else ""
    short = ch['title'][:40] + ('...' if len(ch['title']) > 40 else '')
    nav_items.append(f'<a href="#{ch["id"]}" class="nav-chapter" onclick="closeSidebar()">{esc(short)}{range_str}</a>')
nav_html = '\n'.join(nav_items)

# Render body
body_sections = []
for ch in chapters:
    _, badge_class = ORIGIN_LABELS.get(ch['zone'], ORIGIN_LABELS['original'])
    items_html = []
    for it in ch['items']:
        if it['type'] == 'article':
            items_html.append(render_article_html(it))
        elif it['type'] == 'part':
            lines = [esc(l.strip()) for l in it['text'].split('\n') if l.strip()]
            items_html.append(f'<div class="part-title">{"<br>".join(lines)}</div>')
        elif it['type'] == 'signature':
            items_html.append('<div class="signature">ผู้รับสนองพระบรมราชโองการ<br><strong>นายกรัฐมนตรี</strong></div>')
        elif it['type'] == 'text':
            items_html.append(f'<div class="normal-text">{esc(it["text"])}</div>')
    
    body_sections.append(f'''<section class="chapter-section" id="{ch['id']}">
  <div class="chapter-heading"><h2>{esc(ch['title'])}</h2></div>
  {''.join(items_html)}
</section>''')

all_body = '\n'.join(body_sections)

# Preamble
preamble_title = esc(cover_pars[0]) if cover_pars else ''
preamble_king = '<br>'.join(esc(l.strip()) for l in cover_pars[1].split('\n') if l.strip()) if len(cover_pars) > 1 else ''
preamble_texts = ''.join(f'<p class="preamble-p">{esc(p)}</p>' for p in cover_pars[2:])

full_html = f'''<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>รัฐธรรมนูญแห่งราชอาณาจักรไทย พุทธศักราช ๒๕๒๕</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
:root {{
  --bg-dark: #0a0e1a;
  --bg-card: rgba(255,255,255,0.04);
  --bg-card-hover: rgba(255,255,255,0.07);
  --gold: #d4a843;
  --gold-light: #f0d68a;
  --text: #e8e8e8;
  --text-muted: #8899aa;
  --accent-blue: #3b82f6;
  --accent-green: #10b981;
  --accent-orange: #f59e0b;
  --accent-purple: #8b5cf6;
  --accent-red: #ef4444;
  --accent-gold: #d4a843;
  --glass: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.1);
  --sidebar-w: 320px;
  --header-h: 64px;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: 'Sarabun', sans-serif;
  background: var(--bg-dark);
  color: var(--text);
  line-height: 1.7;
  overflow-x: hidden;
}}
/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {{ width:8px; }}
::-webkit-scrollbar-track {{ background: #111827; }}
::-webkit-scrollbar-thumb {{ background: var(--gold); border-radius:4px; }}

/* ===== HEADER ===== */
.top-header {{
  position: fixed; top:0; left:0; right:0; height: var(--header-h);
  background: rgba(10,14,26,0.92); backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  display: flex; align-items: center; padding: 0 24px; z-index: 1000;
  justify-content: space-between;
}}
.header-left {{ display:flex; align-items:center; gap:16px; }}
.menu-btn {{
  display:none; background:none; border:none; color:var(--gold); font-size:24px; cursor:pointer;
}}
.header-title {{ font-size:18px; font-weight:700; color:var(--gold); }}
.header-search {{
  position:relative; width: 340px;
}}
.header-search input {{
  width:100%; padding:8px 16px 8px 40px; border-radius:24px;
  background: rgba(255,255,255,0.08); border:1px solid var(--glass-border);
  color:var(--text); font-family:'Sarabun'; font-size:15px; outline:none;
  transition: all .3s;
}}
.header-search input:focus {{
  border-color: var(--gold); background: rgba(255,255,255,0.12);
}}
.header-search::before {{
  content:'🔍'; position:absolute; left:14px; top:50%; transform:translateY(-50%); font-size:14px;
}}
.filter-btns {{
  display:flex; gap:6px; align-items:center;
}}
.filter-btn {{
  padding:4px 12px; border-radius:16px; font-size:12px; cursor:pointer;
  border:1px solid var(--glass-border); background:transparent; color:var(--text-muted);
  font-family:'Sarabun'; transition: all .3s;
}}
.filter-btn.active, .filter-btn:hover {{
  background: var(--gold); color:#000; border-color: var(--gold); font-weight:600;
}}

/* ===== SIDEBAR ===== */
.sidebar {{
  position:fixed; top:var(--header-h); left:0; bottom:0; width:var(--sidebar-w);
  background: rgba(10,14,26,0.95); backdrop-filter: blur(10px);
  border-right:1px solid var(--glass-border);
  overflow-y:auto; z-index:900; padding:16px 0;
  transition: transform .3s;
}}
.sidebar-title {{
  font-size:14px; font-weight:700; color:var(--gold); text-transform:uppercase;
  letter-spacing:2px; padding:8px 20px 12px; border-bottom:1px solid var(--glass-border);
}}
.nav-chapter {{
  display:block; padding:10px 20px; font-size:13px; color:var(--text-muted);
  text-decoration:none; border-left:3px solid transparent; transition: all .2s;
}}
.nav-chapter:hover, .nav-chapter.active {{
  background: rgba(212,168,67,0.1); color:var(--gold); border-left-color:var(--gold);
}}

/* ===== MAIN ===== */
.main {{
  margin-left: var(--sidebar-w); margin-top: var(--header-h); min-height:100vh;
}}

/* ===== HERO ===== */
.hero {{
  position:relative; padding:80px 60px 60px; text-align:center;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  border-bottom:2px solid var(--gold);
  overflow:hidden;
}}
.hero::before {{
  content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%;
  background: radial-gradient(circle at 30% 40%, rgba(212,168,67,0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(59,130,246,0.06) 0%, transparent 50%);
  animation: heroGlow 12s ease-in-out infinite alternate;
}}
@keyframes heroGlow {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(3deg); }}
}}
.hero-content {{ position:relative; z-index:1; max-width:900px; margin:0 auto; }}
.hero-emblem {{ font-size:80px; margin-bottom:16px; filter:drop-shadow(0 0 30px rgba(212,168,67,0.3)); }}
.hero h1 {{
  font-size:36px; font-weight:800; color:var(--gold-light);
  text-shadow:0 2px 20px rgba(212,168,67,0.3);
  margin-bottom:12px;
}}
.hero .subtitle {{ font-size:18px; color:var(--text-muted); margin-bottom:40px; }}

/* Stats */
.stats-grid {{
  display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:40px;
}}
.stat-card {{
  background:var(--glass); border:1px solid var(--glass-border); border-radius:16px;
  padding:24px 16px; backdrop-filter:blur(10px); transition:transform .3s;
}}
.stat-card:hover {{ transform:translateY(-4px); }}
.stat-num {{ font-size:36px; font-weight:800; color:var(--gold); }}
.stat-label {{ font-size:13px; color:var(--text-muted); margin-top:4px; }}

/* History */
.history-box {{
  text-align:left; background:var(--glass); border:1px solid var(--glass-border);
  border-radius:20px; padding:32px 40px; margin-top:20px; backdrop-filter:blur(10px);
}}
.history-box h3 {{ color:var(--gold); font-size:20px; margin-bottom:16px; }}
.history-box p {{ color:var(--text-muted); font-size:15px; margin-bottom:12px; line-height:1.8; }}
.history-box .highlight {{ color:var(--gold-light); font-weight:600; }}
.timeline {{
  display:flex; flex-wrap:wrap; gap:12px; margin-top:20px;
}}
.timeline-item {{
  flex:1; min-width:140px; background:rgba(212,168,67,0.08); border:1px solid rgba(212,168,67,0.2);
  border-radius:12px; padding:16px; text-align:center;
}}
.timeline-item .round {{ font-size:12px; color:var(--gold); font-weight:700; text-transform:uppercase; }}
.timeline-item .desc {{ font-size:13px; color:var(--text-muted); margin-top:6px; }}

/* ===== PREAMBLE ===== */
.preamble-section {{
  max-width:900px; margin:40px auto; padding:0 40px;
}}
.preamble-section h2 {{
  text-align:center; font-size:24px; color:var(--gold); margin-bottom:20px;
}}
.preamble-p {{
  text-indent:3em; font-size:16px; color:var(--text); margin-bottom:12px;
}}

/* ===== CHAPTERS ===== */
.chapter-section {{
  max-width:900px; margin:0 auto; padding:20px 40px 40px;
}}
.chapter-heading {{
  position:sticky; top:var(--header-h); z-index:50;
  background: linear-gradient(135deg, rgba(30,27,75,0.95), rgba(15,23,42,0.95));
  backdrop-filter:blur(10px);
  border:1px solid var(--glass-border); border-radius:16px;
  padding:24px; margin-bottom:24px; text-align:center;
}}
.chapter-heading h2 {{
  font-size:22px; font-weight:700; color:var(--gold-light);
}}

/* Parts */
.part-title {{
  text-align:center; font-size:17px; font-weight:700; color:var(--accent-blue);
  padding:16px; margin:20px 0 12px;
  border-top:1px solid var(--glass-border); border-bottom:1px solid var(--glass-border);
}}

/* Articles */
.article-card {{
  background:var(--bg-card); border:1px solid var(--glass-border);
  border-radius:12px; padding:20px 24px; margin-bottom:12px;
  transition: all .3s; border-left:3px solid transparent;
}}
.article-card:hover {{
  background:var(--bg-card-hover); transform:translateX(4px);
}}
.article-card[data-origin="original"] {{ border-left-color: var(--accent-blue); }}
.article-card[data-origin="modified"] {{ border-left-color: var(--accent-green); }}
.article-card[data-origin="ch13_16"] {{ border-left-color: var(--accent-green); }}
.article-card[data-origin="ch17_26"] {{ border-left-color: var(--accent-orange); }}
.article-card[data-origin="ch27_36"] {{ border-left-color: var(--accent-purple); }}
.article-card[data-origin="special"] {{ border-left-color: var(--accent-gold); }}
.article-card[data-origin="transitional"] {{ border-left-color: var(--accent-blue); }}

.article-header {{ margin-bottom:8px; }}
.badge {{
  display:inline-block; padding:3px 10px; border-radius:12px;
  font-size:11px; font-weight:600; letter-spacing:0.5px;
}}
.badge-original {{ background:rgba(59,130,246,0.15); color:#60a5fa; }}
.badge-modified {{ background:rgba(16,185,129,0.15); color:#34d399; }}
.badge-assembly {{ background:rgba(16,185,129,0.15); color:#34d399; }}
.badge-ref3 {{ background:rgba(245,158,11,0.15); color:#fbbf24; }}
.badge-ref45 {{ background:rgba(139,92,246,0.15); color:#a78bfa; }}
.badge-special {{ background:rgba(212,168,67,0.2); color:var(--gold-light); }}

.article-text {{ font-size:16px; line-height:1.8; }}
.art-num {{ font-weight:800; color:var(--gold); font-size:17px; }}
.sub-para {{ font-size:16px; text-indent:2em; margin-top:4px; line-height:1.8; }}
.list-item {{ margin-left:2.5em; font-size:15px; margin-top:2px; }}
.list-num {{ font-weight:600; color:var(--accent-blue); margin-right:6px; }}

.normal-text {{ font-size:15px; color:var(--text-muted); padding:8px 0; }}
.signature {{
  text-align:right; font-size:16px; padding:30px 40px; color:var(--text-muted);
}}
.signature strong {{ color:var(--gold); }}

/* Hidden articles (filtered out) */
.article-card.hidden {{ display:none; }}
.chapter-section.hidden {{ display:none; }}

/* ===== BACK TO TOP ===== */
.back-top {{
  position:fixed; bottom:24px; right:24px; width:48px; height:48px;
  background:var(--gold); color:#000; border:none; border-radius:50%;
  font-size:20px; cursor:pointer; z-index:999; opacity:0; transition: all .3s;
  box-shadow:0 4px 20px rgba(212,168,67,0.4);
}}
.back-top.visible {{ opacity:1; }}
.back-top:hover {{ transform:scale(1.1); }}

/* ===== LEGEND ===== */
.legend {{
  display:flex; flex-wrap:wrap; gap:12px; justify-content:center; margin:30px auto;
  max-width:900px; padding:0 40px;
}}
.legend-item {{
  display:flex; align-items:center; gap:6px; font-size:13px; color:var(--text-muted);
}}
.legend-dot {{
  width:12px; height:12px; border-radius:50%;
}}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {{
  .sidebar {{ transform:translateX(-100%); }}
  .sidebar.open {{ transform:translateX(0); }}
  .main {{ margin-left:0; }}
  .menu-btn {{ display:block; }}
  .stats-grid {{ grid-template-columns:repeat(2,1fr); }}
  .hero {{ padding:40px 20px; }}
  .chapter-section, .preamble-section {{ padding:20px; }}
  .header-search {{ width:200px; }}
  .filter-btns {{ display:none; }}
}}
@media (max-width: 600px) {{
  .stats-grid {{ grid-template-columns:1fr 1fr; }}
  .hero h1 {{ font-size:24px; }}
  .timeline {{ flex-direction:column; }}
}}

/* Smooth scroll */
html {{ scroll-behavior:smooth; }}
</style>
</head>
<body>

<!-- HEADER -->
<header class="top-header">
  <div class="header-left">
    <button class="menu-btn" onclick="toggleSidebar()">☰</button>
    <span class="header-title">รัฐธรรมนูญ ๒๕๒๕</span>
  </div>
  <div class="header-search">
    <input type="text" id="searchInput" placeholder="ค้นหามาตรา, คำสำคัญ..." oninput="handleSearch(this.value)">
  </div>
  <div class="filter-btns">
    <button class="filter-btn active" onclick="filterOrigin('all', this)">ทั้งหมด</button>
    <button class="filter-btn" onclick="filterOrigin('original', this)">เดิม</button>
    <button class="filter-btn" onclick="filterOrigin('modified', this)">แก้ไข</button>
    <button class="filter-btn" onclick="filterOrigin('ch13_16', this)">สภาร่างฯ</button>
    <button class="filter-btn" onclick="filterOrigin('ch17_26', this)">ประชามติ ๓</button>
    <button class="filter-btn" onclick="filterOrigin('ch27_36', this)">ประชามติ ๔-๕</button>
    <button class="filter-btn" onclick="filterOrigin('special', this)">พิเศษ</button>
  </div>
</header>

<!-- SIDEBAR -->
<nav class="sidebar" id="sidebar">
  <div class="sidebar-title">📜 สารบัญ</div>
  {nav_html}
</nav>

<!-- MAIN -->
<main class="main">

<!-- HERO -->
<section class="hero">
  <div class="hero-content">
    <div class="hero-emblem">🦅</div>
    <h1>รัฐธรรมนูญแห่งราชอาณาจักรไทย<br>พุทธศักราช ๒๕๒๕</h1>
    <p class="subtitle">ฉบับประชาชนเป็นใหญ่ — ผ่านประชามติ ๕ รอบ</p>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-num">{to_thai(total_articles)}</div>
        <div class="stat-label">มาตรา</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{to_thai(len(chapters))}</div>
        <div class="stat-label">หมวด</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">๓,๐๐๐</div>
        <div class="stat-label">ผู้ร่วมร่าง</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">๕</div>
        <div class="stat-label">รอบประชามติ</div>
      </div>
    </div>

    <div class="history-box">
      <h3>📖 ประวัติการร่างรัฐธรรมนูญ</h3>
      <p>รัฐธรรมนูญฉบับนี้ถือกำเนิดขึ้นในสมัย <span class="highlight">นายกรัฐมนตรี อภิสิทธิ์ เวชชาชีวะ</span> ภายใต้พระบารมีปกเกล้าปกกระหม่อมของ <span class="highlight">พระบาทสมเด็จพระเจ้าอยู่หัว รัชกาลที่ ๙</span> ด้วยเจตนารมณ์ให้ประชาชนเป็นเจ้าของอำนาจอธิปไตยอย่างแท้จริง</p>
      <p>เนื่องจากประชาชนต้องการแก้ไขรัฐธรรมนูญให้มี <span class="highlight">ความเป็นประชาชนมากกว่าเดิม</span> และ <span class="highlight">ทันสมัยกว่าเดิม</span> จึงมีการจัดตั้ง <span class="highlight">สภาร่างรัฐธรรมนูญ</span> (สสร.) ขึ้นเป็นสภาแยกเพื่อร่างรัฐธรรมนูญโดยเฉพาะ ประกอบด้วย <span class="highlight">นักวิชาการ ๒,๒๑๐ คน</span> และ <span class="highlight">ตัวแทนชาวบ้าน ๗๙๐ คน</span> รวม ๓,๐๐๐ คน</p>
      <p>รัฐธรรมนูญฉบับนี้ใช้แทน <span class="highlight">รัฐธรรมนูญแห่งราชอาณาจักรไทย พุทธศักราช ๒๔๔๕</span> ซึ่งมี ๑๖ หมวด ๔๕๘ มาตรา โดยผ่านการทำ <span class="highlight">ประชามติ ๕ รอบ</span> ก่อนประกาศใช้</p>

      <div class="timeline">
        <div class="timeline-item">
          <div class="round">ประชามติรอบ ๑</div>
          <div class="desc">รับหลักการร่าง รธน. ใหม่</div>
        </div>
        <div class="timeline-item">
          <div class="round">ประชามติรอบ ๒</div>
          <div class="desc">หมวด ๑-๑๖ และหลักการสิทธิ</div>
        </div>
        <div class="timeline-item">
          <div class="round">ประชามติรอบ ๓</div>
          <div class="desc">หมวด ๑๗-๒๖ ขยายสิทธิ</div>
        </div>
        <div class="timeline-item">
          <div class="round">ประชามติรอบ ๔</div>
          <div class="desc">หมวด ๒๗-๓๖ กลไกตรวจสอบ</div>
        </div>
        <div class="timeline-item">
          <div class="round">ประชามติรอบ ๕</div>
          <div class="desc">หมวดพิเศษ อำนาจสูงสุด</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- LEGEND -->
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:var(--accent-blue)"></div> คงเดิมจาก รธน. ๒๔๔๕</div>
  <div class="legend-item"><div class="legend-dot" style="background:var(--accent-green)"></div> แก้ไขโดยสภาร่างรัฐธรรมนูญ</div>
  <div class="legend-item"><div class="legend-dot" style="background:var(--accent-orange)"></div> ประชามติรอบที่ ๓</div>
  <div class="legend-item"><div class="legend-dot" style="background:var(--accent-purple)"></div> ประชามติรอบที่ ๔-๕</div>
  <div class="legend-item"><div class="legend-dot" style="background:var(--accent-gold)"></div> ประชามติรอบที่ ๕ (พิเศษ)</div>
</div>

<!-- PREAMBLE -->
<div class="preamble-section">
  <h2>{preamble_title}</h2>
  <div style="text-align:center;color:var(--text-muted);margin-bottom:20px;">{preamble_king}</div>
  {preamble_texts}
</div>

<!-- CHAPTERS -->
{all_body}

</main>

<!-- BACK TO TOP -->
<button class="back-top" id="backTop" onclick="window.scrollTo(0,0)">▲</button>

<script>
// Sidebar toggle
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('open');
}}
function closeSidebar() {{
  document.getElementById('sidebar').classList.remove('open');
}}

// Back to top
window.addEventListener('scroll', () => {{
  document.getElementById('backTop').classList.toggle('visible', window.scrollY > 400);
}});

// Search
function handleSearch(query) {{
  const cards = document.querySelectorAll('.article-card');
  const sections = document.querySelectorAll('.chapter-section');
  const q = query.trim().toLowerCase();
  
  if (!q) {{
    cards.forEach(c => c.classList.remove('hidden'));
    sections.forEach(s => s.classList.remove('hidden'));
    return;
  }}
  
  const visibleSections = new Set();
  cards.forEach(c => {{
    const text = c.textContent.toLowerCase();
    if (text.includes(q)) {{
      c.classList.remove('hidden');
      visibleSections.add(c.closest('.chapter-section'));
    }} else {{
      c.classList.add('hidden');
    }}
  }});
  sections.forEach(s => {{
    s.classList.toggle('hidden', !visibleSections.has(s));
  }});
}}

// Filter by origin
function filterOrigin(origin, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  const cards = document.querySelectorAll('.article-card');
  const sections = document.querySelectorAll('.chapter-section');
  
  if (origin === 'all') {{
    cards.forEach(c => c.classList.remove('hidden'));
    sections.forEach(s => s.classList.remove('hidden'));
    return;
  }}
  
  const visibleSections = new Set();
  cards.forEach(c => {{
    if (c.dataset.origin === origin) {{
      c.classList.remove('hidden');
      visibleSections.add(c.closest('.chapter-section'));
    }} else {{
      c.classList.add('hidden');
    }}
  }});
  sections.forEach(s => {{
    s.classList.toggle('hidden', !visibleSections.has(s));
  }});
}}

// Active nav highlight on scroll
const observer = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      document.querySelectorAll('.nav-chapter').forEach(n => n.classList.remove('active'));
      const link = document.querySelector(`.nav-chapter[href="#${{e.target.id}}"]`);
      if (link) link.classList.add('active');
    }}
  }});
}}, {{ rootMargin: '-30% 0px -60% 0px' }});
document.querySelectorAll('.chapter-section').forEach(s => observer.observe(s));
</script>
</body>
</html>'''

with open(output_html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

fsize = os.path.getsize(output_html_path)
print(f"✅ เว็บไซต์สร้างเรียบร้อย!")
print(f"   Path: {output_html_path}")
print(f"   Size: {fsize:,} bytes")
print(f"   จำนวนมาตรา: {total_articles}")
print(f"   จำนวนหมวด: {len(chapters)}")
