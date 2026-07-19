// Sidebar toggle
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
}

// Switch Tab in Dashboard
function switchTab(tabId, btn) {
  const card = btn.closest('.dashboard-card');
  const tabs = card.querySelectorAll('.db-tab-btn');
  const contents = card.querySelectorAll('.db-tab-content');
  
  tabs.forEach(t => t.classList.remove('active'));
  contents.forEach(c => c.classList.remove('active'));
  
  btn.classList.add('active');
  document.getElementById(tabId).classList.add('active');
}

// Toggle Accordion in Early Constitution Tab
function toggleAccordion(header) {
  const item = header.closest('.accordion-item');
  item.classList.toggle('active');
}

// Filter PMs by Era
function filterPMs(era, btn) {
  const btns = btn.parentNode.querySelectorAll('.filter-btn');
  btns.forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  const rows = document.querySelectorAll('.pm-row');
  rows.forEach(r => {
    if (era === 'all' || r.dataset.era === era) {
      r.style.display = '';
    } else {
      r.style.display = 'none';
    }
  });
}

// Back to top
window.addEventListener('scroll', () => {
  document.getElementById('backTop').classList.toggle('visible', window.scrollY > 400);
});

// Search
function handleSearch(query) {
  const cards = document.querySelectorAll('.article-card');
  const sections = document.querySelectorAll('.chapter-section');
  const q = query.trim().toLowerCase();
  
  if (!q) {
    cards.forEach(c => c.classList.remove('hidden'));
    sections.forEach(s => s.classList.remove('hidden'));
    return;
  }
  
  const visibleSections = new Set();
  cards.forEach(c => {
    const text = c.textContent.toLowerCase();
    if (text.includes(q)) {
      c.classList.remove('hidden');
      visibleSections.add(c.closest('.chapter-section'));
    } else {
      c.classList.add('hidden');
    }
  });
  sections.forEach(s => {
    s.classList.toggle('hidden', !visibleSections.has(s));
  });
}

// Filter by origin
function filterOrigin(origin, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  const cards = document.querySelectorAll('.article-card');
  const sections = document.querySelectorAll('.chapter-section');
  
  if (origin === 'all') {
    cards.forEach(c => c.classList.remove('hidden'));
    sections.forEach(s => s.classList.remove('hidden'));
    return;
  }
  
  const visibleSections = new Set();
  cards.forEach(c => {
    if (c.dataset.origin === origin) {
      c.classList.remove('hidden');
      visibleSections.add(c.closest('.chapter-section'));
    } else {
      c.classList.add('hidden');
    }
  });
  sections.forEach(s => {
    s.classList.toggle('hidden', !visibleSections.has(s));
  });
}

// Active nav highlight on scroll
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      document.querySelectorAll('.nav-chapter').forEach(n => n.classList.remove('active'));
      const link = document.querySelector(`.nav-chapter[href="#${e.target.id}"]`);
      if (link) link.classList.add('active');
    }
  });
}, { rootMargin: '-30% 0px -60% 0px' });
document.querySelectorAll('.chapter-section').forEach(s => observer.observe(s));

// Change Theme
function changeTheme(theme) {
  const el = document.documentElement;
  const body = document.body;
  el.classList.remove('theme-dark', 'theme-light', 'theme-bw', 'theme-nightcity', 'theme-aero');
  body.classList.remove('theme-dark', 'theme-light', 'theme-bw', 'theme-nightcity', 'theme-aero');
  if (theme !== 'dark') {
    el.classList.add('theme-' + theme);
    body.classList.add('theme-' + theme);
  }
  localStorage.setItem('constTheme', theme);
}

// Load saved theme on startup
const savedTheme = localStorage.getItem('constTheme') || 'dark';
document.getElementById('themeSelect').value = savedTheme;
changeTheme(savedTheme);

// Jump to Article Search Logic
function translateThaiToArabic(str) {
  const thaiNums = {'๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4', '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'};
  return str.replace(/[๐-๙]/g, m => thaiNums[m]);
}

function goToArticle(val, prefix) {
  const cleanVal = translateThaiToArabic(val).replace(/\\D/g, '');
  if (!cleanVal) return;
  
  const targetId = prefix + cleanVal;
  const el = document.getElementById(targetId);
  if (el) {
    // Reset any search/filters for this card and its section
    el.classList.remove('hidden');
    const sect = el.closest('.chapter-section');
    if (sect) {
      sect.classList.remove('hidden');
    }
    
    // Smooth scroll to card
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Add pulsing highlight effect
    el.classList.remove('highlight-pulse');
    void el.offsetWidth; // Force reflow
    el.classList.add('highlight-pulse');
  }
}

// Compare mode toggle
function toggleCompare(btn, artNum) {
  const container = document.getElementById('compare_' + artNum);
  if (!container) return;
  
  const isHidden = container.style.display === 'none';
  if (isHidden) {
    container.style.display = 'flex';
    btn.textContent = '⚖️ ปิดเปรียบเทียบ';
    btn.style.background = 'var(--gold)';
    btn.style.color = '#000';
  } else {
    container.style.display = 'none';
    btn.textContent = '⚖️ เปรียบเทียบ';
    btn.style.background = 'rgba(212, 168, 67, 0.1)';
    btn.style.color = 'var(--gold-light)';
  }
}

// Org chart description hover
const orgData = {
  'people': {
    title: '👥 ประชาชนชาวไทย (ปวงชนชาวไทย)',
    duties: `<ul>
      <li><strong>เจ้าของอำนาจอธิปไตย:</strong> ทรงสิทธิ์และเป็นแหล่งกำเนิดอำนาจสูงสุดในการปกครองแผ่นดินตาม <span class="cross-ref" data-target="3">มาตรา ๓</span></li>
      <li><strong>สิทธิออกเสียงเลือกตั้ง:</strong> เลือกตั้งสมาชิก ส.ส. จำนวน ๕๐๐ คน และสมาชิก ส.ว. จำนวน ๒๐๐ คน เพื่อทำหน้าที่นิติบัญญัติและตรวจสอบแทนตน</li>
      <li><strong>ประชาธิปไตยทางตรง:</strong> ลงมติประชามติที่มีผลผูกพันรัฐบาล คณะรัฐสภา และองค์กรของรัฐ (<span class="cross-ref" data-target="201">มาตรา ๒๐๑</span>) และใช้อำนาจนิติบัญญัติโดยตรงผ่านแอปพลิเคชันมือถือดิจิทัล (<span class="cross-ref" data-target="1130">มาตรา ๑๑๓๐</span>)</li>
      <li><strong>สิทธิต่อต้านขัดขืนการยึดอำนาจ:</strong> มีสิทธิต่อต้านการรัฐประหารและการใช้อำนาจเผด็จการนอกระบบโดยสันติวิธีตามที่ระบุและคุ้มครองใน <span class="cross-ref" data-target="64">มาตรา ๖๓</span></li>
    </ul>`,
    source: `<p>ประชาชนพลเมืองไทยทุกคนที่มีคุณสมบัติตามที่กฎหมายกำหนด (อายุไม่ต่ำกว่า ๑๘ ปีบริบูรณ์ในวันเลือกตั้ง) มีสถานะเป็นเจ้าของอำนาจอธิปไตยอย่างเสมอภาคและเท่าเทียมกันตามรัฐธรรมนูญ</p>`,
    law: `<p>มาตราสำคัญ: <span class="cross-ref" data-target="3">มาตรา ๓</span>, <span class="cross-ref" data-target="63">มาตรา ๖๓</span>, <span class="cross-ref" data-target="170">มาตรา ๑๗๐</span>, <span class="cross-ref" data-target="170/1">มาตรา ๑๗๐/๑</span>, <span class="cross-ref" data-target="1130">มาตรา ๑๑๓๐</span></p>`
  },
  'monarch': {
    title: '👑 พระมหากษัตริย์',
    duties: `<ul>
      <li><strong>องค์พระประมุขแห่งรัฐ:</strong> ดำรงอยู่ในฐานะอันเป็นที่เคารพสักการะ ผู้ใดจะละเมิดมิได้ ทรงใช้อำนาจอธิปไตยผ่านรัฐสภา คณะรัฐมนตรี และศาล (<span class="cross-ref" data-target="3">มาตรา ๓</span> และ <span class="cross-ref" data-target="8">มาตรา ๘</span>)</li>
      <li><strong>พระราชอำนาจตรากฎหมาย:</strong> ทรงลงพระปรมาภิไธยในร่างพระราชบัญญัติภายใน ๒๐ วัน หากทรงไม่เห็นชอบรัฐสภาต้องทบทวนใหม่</li>
      <li><strong>เสรีภาพในการแสดงความคิดเห็นต่อสถาบันฯ:</strong> การแสดงความเห็น ติชม หรือวิพากษ์วิจารณ์สถาบันพระมหากษัตริย์โดยสุจริต เป็นสิทธิเสรีภาพของประชาชนและไม่ถือเป็นความผิดกฎหมาย (<span class="cross-ref" data-target="8">มาตรา ๘</span>)</li>
    </ul>`,
    source: `<p>การสืบราชสมบัติให้เป็นไปตามกฎมณเฑียรบาลว่าด้วยการสืบราชสันตติวงศ์และพระราชวินิจฉัย</p>`,
    law: `<p>มาตราสำคัญ: <span class="cross-ref" data-target="3">มาตรา ๓</span>, <span class="cross-ref" data-target="8">มาตรา ๘</span>, หมวด ๒ พระมหากษัตริย์ (<span class="cross-ref" data-target="๙">มาตรา ๙</span> - <span class="cross-ref" data-target="๒๕">มาตรา ๒๕</span>)</p>`
  },
  'privy_council': {
    title: '📜 คณะองคมนตรี',
    duties: `<ul>
      <li><strong>ที่ปรึกษาในพระองค์:</strong> ทำหน้าที่ถวายคำแนะนำต่อพระมหากษัตริย์ในพระราชกรณียกิจทั้งปวงตามที่ทรงปรึกษา</li>
      <li><strong>การรักษาการประมุข:</strong> เสนอชื่อและแต่งตั้งผู้สำเร็จราชการแทนพระองค์ในกรณีมีความจำเป็นตามรัฐธรรมนูญ</li>
    </ul>`,
    source: `<p>ประกอบด้วยประธานองคมนตรีหนึ่งคน และองคมนตรีอื่นอีกไม่เกินสิบแปดคน (รวมทั้งหมดไม่เกิน ๑๙ คน) ซึ่งพระมหากษัตริย์ทรงเลือกและแต่งตั้งตามพระราชอัธยาศัย</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๒ พระมหากษัตริย์ (<span class="cross-ref" data-target="12">มาตรา ๑๒</span> - <span class="cross-ref" data-target="21">มาตรา ๒๑</span>)</p>`
  },
  'parliament': {
    title: '🏛️ รัฐสภา',
    duties: `<ul>
      <li><strong>ฝ่ายนิติบัญญัติร่วมสองสภา:</strong> พิจารณาและผ่านร่างกฎหมายต่างๆ ได้แก่ พระราชบัญญัติ (พ.ร.บ.) และพระราชบัญญัติประกอบรัฐธรรมนูญ (พ.ร.ป.) โดยมีสมาชิกร่วมกันทั้งหมด ๗๐๐ คน</li>
      <li><strong>ประธานรัฐสภา:</strong> ประธานสภาผู้แทนราษฎรเป็นประธานรัฐสภาโดยตำแหน่ง และประธานวุฒิสภาเป็นรองประธานรัฐสภาโดยตำแหน่ง</li>
      <li><strong>ควบคุมฝ่ายบริหาร:</strong> ตรวจสอบ ถ่วงดุล และอภิปรายไม่ไว้วางใจนายกรัฐมนตรีและรัฐมนตรี</li>
    </ul>`,
    source: `<p>เป็นรัฐสภาระบบสองสภา ประกอบด้วย สภาผู้แทนราษฎร (ส.ส.) จำนวน ๕๐๐ คน และวุฒิสภา (ส.ว.) จำนวน ๒๐๐ คน ประชุมร่วมกัน</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๖ รัฐสภา (<span class="cross-ref" data-target="89">มาตรา ๘๙</span> - <span class="cross-ref" data-target="199">มาตรา ๑๙๙</span>)</p>`
  },
  'house_of_reps': {
    title: '🏛️ สภาผู้แทนราษฎร (ส.ส.) - จำนวน ๕๐๐ คน',
    duties: `<ul>
      <li><strong>ผู้แทนปวงชนชาวไทย:</strong> เสนอร่างกฎหมาย พิจารณาร่างงบประมาณรายจ่ายประจำปี และตรวจสอบนโยบายรัฐบาล</li>
      <li><strong>โครงสร้าง ส.ส. ๕๐๐ คน:</strong> แบ่งเป็น ส.ส. จากการเลือกตั้งแบบแบ่งเขตจำนวน ๔๐๐ คน และแบบบัญชีรายชื่อจำนวน ๑๐๐ คน ตาม <span class="cross-ref" data-target="98">มาตรา ๙๘</span></li>
      <li><strong>ลงมติเลือกผู้นำประเทศ:</strong> พิจารณาและลงมติเห็นชอบบุคคลที่สมควรแต่งตั้งเป็นนายกรัฐมนตรี (ส.ส. เท่านั้นที่มีสิทธิเลือกนายกฯ)</li>
      <li><strong>อภิปรายไม่ไว้วางใจ:</strong> ยื่นญัตติเพื่ออภิปรายและลงมติไม่ไว้วางใจนายกรัฐมนตรีหรือรัฐมนตรีเป็นรายบุคคลหรือทั้งคณะ</li>
    </ul>`,
    source: `<p>สมาชิกสภาผู้แทนราษฎร (ส.ส.) จำนวน ๕๐๐ คน มาจากการเลือกตั้งโดยตรงและลับของประชาชน มีวาระดำรงตำแหน่งคราวละ ๔ ปี</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๖ ส่วนที่ ๒ สภาผู้แทนราษฎร (<span class="cross-ref" data-target="98">มาตรา ๙๘</span> - <span class="cross-ref" data-target="120">มาตรา ๑๒๐</span>)</p>`
  },
  'senate': {
    title: '🏛️ วุฒิสภา (ส.ว.) - จำนวน ๒๐๐ คน',
    duties: `<ul>
      <li><strong>กลั่นกรองพระราชบัญญัติ:</strong> ตรวจสอบ ทบทวน และให้ความเห็นชอบร่างกฎหมายที่ผ่านสภาผู้แทนราษฎรมาแล้ว</li>
      <li><strong>องค์ประกอบ ส.ว. ๒๐๐ คน:</strong> ประกอบด้วยสมาชิกซึ่งราษฎรเลือกตั้งโดยตรงจำนวน ๒๐๐ คน (ใช้เขตจังหวัดเป็นเขตเลือกตั้ง) ตาม <span class="cross-ref" data-target="121">มาตรา ๑๒๑</span></li>
      <li><strong>ไม่มีสิทธิเลือกนายกฯ:</strong> ถูกจำกัดบทบาทไม่ให้ร่วมลงมติเลือกนายกรัฐมนตรี เพื่อรักษาเจตนารมณ์เสียงข้างมากของ ส.ส. ที่มาจากประชาชน</li>
      <li><strong>เห็นชอบผู้ดำรงตำแหน่งระดับสูง:</strong> พิจารณาอนุมัติแต่งตั้งตุลาการศาลรัฐธรรมนูญ, กรรมการองค์กรอิสระ และอัยการสูงสุด</li>
    </ul>`,
    source: `<p>สมาชิกวุฒิสภา (ส.ว.) จำนวน ๒๐๐ คน มาจากการเลือกตั้งโดยตรงของประชาชนในแต่ละภูมิภาค/จังหวัด มีวาระดำรงตำแหน่งคราวละ ๖ ปี</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๖ ส่วนที่ ๓ วุฒิสภา (<span class="cross-ref" data-target="121">มาตรา ๑๒๑</span> - <span class="cross-ref" data-target="135">มาตรา ๑๓๕</span>)</p>`
  },
  'cabinet': {
    title: '💼 คณะรัฐมนตรี (ครม.)',
    duties: `<ul>
      <li><strong>ฝ่ายบริหารสูงสุด:</strong> บริหารราชการแผ่นดินและบังคับบัญชาข้าราชการประจำในกระทรวง ทบวง กรม ทั่วราชอาณาจักร</li>
      <li><strong>กำหนดทิศทางนโยบาย:</strong> ขับเคลื่อนนโยบายสาธารณะ การเงิน การต่างประเทศ และความมั่นคงตามที่แถลงต่อรัฐสภา</li>
      <li><strong>กฎหมายฝ่ายบริหาร:</strong> เสนอร่าง พ.ร.บ., ตราพระราชกำหนด (พ.ร.ก.) ในคราวจำเป็นรีบด่วน และตราพระราชกฤษฎีกา (พ.ร.ฎ.)</li>
    </ul>`,
    source: `<p>ประกอบด้วยนายกรัฐมนตรีหนึ่งคน และรัฐมนตรีอื่นอีกไม่เกินสามสิบหกคน (รวมคณะบริหารทั้งหมดไม่เกิน ๓๗ คน) ร่วมกันทำงานในรูปคณะกรรมการ</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๗ คณะรัฐมนตรี (<span class="cross-ref" data-target="201">มาตรา ๒๐๑</span> - <span class="cross-ref" data-target="217">มาตรา ๒๑๗</span>)</p>`
  },
  'prime_minister': {
    title: '💼 นายกรัฐมนตรี',
    duties: `<ul>
      <li><strong>หัวหน้ารัฐบาล:</strong> ผู้นำสูงสุดในการกำหนดนโยบาย บังคับบัญชาข้าราชการประจำ และบริหารราชการแผ่นดิน</li>
      <li><strong>ข้อจำกัดวาระ ๑๖ ปี:</strong> ดำรงตำแหน่งติดต่อกันหรือรวมกันแล้วห้ามเกินกว่า ๔ วาระ หรือ ๑๖ ปี เพื่อป้องกันการผูกขาดขยายอิทธิพลทางการเมือง (<span class="cross-ref" data-target="201">มาตรา ๒๐๑ วรรคสาม</span>)</li>
      <li><strong>ปรับคณะรัฐมนตรี:</strong> เสนอแต่งตั้งและพ้นจากตำแหน่งของรัฐมนตรีประจำกระทรวงต่างๆ</li>
    </ul>`,
    source: `<p>เสนอชื่อและลงมติเห็นชอบโดยเฉพาะสภาผู้แทนราษฎร (ส.ส.) เกินกึ่งหนึ่ง และได้รับการโปรดเกล้าฯ แต่งตั้งโดยพระมหากษัตริย์</p>`,
    law: `<p>มาตราสำคัญ: <span class="cross-ref" data-target="201">มาตรา ๒๐๑</span>, <span class="cross-ref" data-target="216">มาตรา ๒๑๖ (๙)</span></p>`
  },
  'local_gov': {
    title: '💼 องค์กรปกครองส่วนท้องถิ่น (อปท.)',
    duties: `<ul>
      <li><strong>กระจายอำนาจสู่ท้องถิ่น:</strong> บริหารจัดการพื้นที่ บริการสาธารณะ การศึกษา และสาธารณสุขในชุมชนโดยอิสระตามความต้องการของชาวบ้าน</li>
      <li><strong>อิสระทางการเงินการคลัง:</strong> จัดเก็บภาษีท้องถิ่นและจัดทำงบประมาณเพื่อพัฒนาท้องถิ่นโดยตรงโดยไม่ต้องขึ้นตรงกับราชการส่วนกลาง</li>
    </ul>`,
    source: `<p>ประกอบด้วย อบจ., เทศบาล, อบต. และปกครองพิเศษ (กทม., พัทยา) โดยผู้บริหารและสมาชิกสภาท้องถิ่นต้องเลือกตั้งโดยตรงทั้งหมด</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๙ การปกครองส่วนท้องถิ่น (<span class="cross-ref" data-target="282">มาตรา ๒๘๒</span> - <span class="cross-ref" data-target="290">มาตรา ๒๙๐</span>)</p>`
  },
  'constitutional_court': {
    title: '⚖️ ศาลรัฐธรรมนูญ',
    duties: `<ul>
      <li><strong>วินิจฉัยความขัดรัฐธรรมนูญ:</strong> ตรวจสอบร่างกฎหมาย มติ หรือการกระทำใดๆ ขององค์กรของรัฐไม่ให้ละเมิดสิทธิเสรีภาพหรือขัดต่อรัฐธรรมนูญ</li>
      <li><strong>พิทักษ์ความชอบธรรมรัฐธรรมนูญ:</strong> วินิจฉัยความชอบด้วยกฎหมายและประกาศให้ประกาศการรัฐประหารย้อนหลังเป็นโมฆะเสมือนไม่มีผลบังคับตั้งแต่ต้น</li>
    </ul>`,
    source: `<p>ประกอบด้วยตุลาการศาลรัฐธรรมนูญจำนวนเก้าคน ได้รับการสรรหาและตรวจสอบคุณสมบัติ ก่อนเสนอให้วุฒิสภาให้มติเห็นชอบแต่งตั้ง</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๘ ศาลรัฐธรรมนูญ (<span class="cross-ref" data-target="255">มาตรา ๒๕๕</span> - <span class="cross-ref" data-target="270">มาตรา ๒๗๐</span>)</p>`
  },
  'courts_of_justice': {
    title: '⚖️ ศาลยุติธรรม',
    duties: `<ul>
      <li><strong>พิจารณาพิพากษาคดีแพ่งและอาญา:</strong> ไกล่เกลี่ยและพิพากษาคดีทั่วไป คดีแพ่ง คดีธุรกิจ และคดีอาญาแผ่นดิน</li>
      <li><strong>หลักประกันความเป็นธรรม:</strong> พิจารณาคดีอย่างเป็นอิสระและรวดเร็วตาม ๓ ชั้นศาล (ศาลชั้นต้น, ศาลอุทธรณ์, ศาลฎีกา)</li>
    </ul>`,
    source: `<p>ผู้พิพากษาที่ได้รับการคัดเลือกและคุ้มครองจากคณะกรรมการตุลาการศาลยุติธรรม (ก.ต.) จำนวน ๑๕ คน เพื่อเป็นอิสระจากการบริหารและการเมือง</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๘ ส่วนที่ ๓ ศาลยุติธรรม (<span class="cross-ref" data-target="233">มาตรา ๒๓๓</span> - <span class="cross-ref" data-target="248">มาตรา ๒๔๘</span>)</p>`
  },
  'administrative_court': {
    title: '⚖️ ศาลปกครอง',
    duties: `<ul>
      <li><strong>คดีข้อพิพาททางปกครอง:</strong> พิจารณาคดีระหว่างประชาชนกับหน่วยงานรัฐ เจ้าหน้าที่รัฐ หรือคดีพิพาทระหว่างองค์กรรัฐด้วยกันเอง</li>
      <li><strong>เพิกถอนคำสั่งไม่ชอบธรรม:</strong> ยกเลิกประกาศ กติกา มติ หรือคำสั่งทางปกครองที่ละเมิดสิทธิ์หรือละเลยการปฏิบัติหน้าที่ของข้าราชการ</li>
    </ul>`,
    source: `<p>ตุลาการศาลปกครองคัดเลือกตามเกณฑ์อิสระของคณะกรรมการตุลาการศาลปกครอง (ก.ศป.) และได้รับการเห็นชอบแต่งตั้ง</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๘ ส่วนที่ ๔ ศาลปกครอง (<span class="cross-ref" data-target="249">มาตรา ๒๔๙</span> - <span class="cross-ref" data-target="253">มาตรา ๒๕๓</span>)</p>`
  },
  'military_court': {
    title: '⚖️ ศาลทหาร',
    duties: `<ul>
      <li><strong>พิจารณาคดีวินัยทหาร:</strong> พิจารณาพิพากษาเฉพาะคดีอาญาทหารที่กระทำโดยกำลังพลประจำการในสังกัดกองทัพบก กองทัพเรือ กองทัพอากาศ</li>
      <li><strong>ขอบเขตจำกัดเข้มงวด:</strong> ห้ามพิจารณาคดีที่พลเรือนเกี่ยวข้อง เว้นแต่กรณีพิเศษตามกฎหมายในยามศึกสงครามเท่านั้น</li>
    </ul>`,
    source: `<p>ปฏิบัติหน้าที่และแต่งตั้งขึ้นภายใต้พระธรรมนูญศาลทหารและการกำกับตรวจสอบของกระทรวงกลาโหมตามรัฐธรรมนูญ</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๘ ส่วนที่ ๕ ศาลทหาร (<span class="cross-ref" data-target="254">มาตรา ๒๕๔</span>)</p>`
  },
  'supreme_citizen_assembly': {
    title: '✊ สภาประชาชนสูงสุด (Supreme Citizen Assembly) - ๕๐๐ คน',
    duties: `<ul>
      <li><strong>ยับยั้งการใช้อำนาจไม่ชอบ (Veto):</strong> มีสิทธิและหน้าที่ตรวจสอบ ยับยั้งกฎหมาย, มติ ครม., หรือแม้กระทั่งคำตัดสินของศาลฎีกาที่พบว่าขัดต่อผลประโยชน์ของชาติและประชาชนโดยตรง (<span class="cross-ref" data-target="1129">มาตรา ๑๑๒๙</span>)</li>
      <li><strong>จัดสรรงบต้านโกง:</strong> ควบคุมและบริหารเงินในกองทุนต่อต้านการทุจริตภาคประชาชนเพื่อชุมชน (<span class="cross-ref" data-target="1134">มาตรา ๑๑๓๔</span>)</li>
    </ul>`,
    source: `<p>ประกอบด้วยประชาชนพลเมืองไทยทั่วไปจำนวน ๕๐๐ คน ได้รับคัดเลือกโดยระบบการสุ่มตัวแทน (Sortition) มีวาระหมุนเวียนคราวละหนึ่งปี (ห้ามดำรงตำแหน่งซ้ำ)</p>`,
    law: `<p>มาตราสำคัญ: หมวดพิเศษ <span class="cross-ref" data-target="1129">มาตรา ๑๑๒๙</span>, <span class="cross-ref" data-target="1134">มาตรา ๑๑๓๔</span></p>`
  },
  'digital_democracy': {
    title: '✊ ระบบประชาธิปไตยทางตรงดิจิทัล',
    duties: `<ul>
      <li><strong>นิติบัญญัติทางตรงโดยประชาชน:</strong> ประชาชนสามารถเสนอและลงประชามติร่างกฎหมายผ่านระบบความปลอดภัยสูงบนแอปพลิเคชันมือถือ</li>
      <li><strong>ออกกฎหมายทันที:</strong> หากกฎหมายใดที่ประชาชนโหวตเห็นชอบมีผู้ลงมติเห็นชอบเกินกึ่งหนึ่งของประชากรผู้เลือกตั้ง ให้มีผลบังคับใช้ทันทีเป็นกฎหมายสูงสุด (<span class="cross-ref" data-target="1130">มาตรา ๑๑๓๐</span>)</li>
    </ul>`,
    source: `<p>รัฐธรรมนูญนี้บังคับให้กระทรวงดิจิทัลจัดตั้งและปกป้องดูแลระบบโครงสร้างนี้ เพื่อคุ้มครองสิทธิออกเสียงนิติบัญญัติของประชาชนทุกคน</p>`,
    law: `<p>มาตราสำคัญ: หมวดพิเศษ <span class="cross-ref" data-target="1130">มาตรา ๑๑๓๐</span></p>`
  },
  'peoples_anti_corruption_fund': {
    title: '✊ กองทุนต่อต้านการทุจริตภาคประชาชน',
    duties: `<ul>
      <li><strong>ยึดทรัพย์คนโกงสู่สังคม:</strong> รวบรวมทรัพย์สิน เงินทอง ที่ยึดทรัพย์ได้ทั้งหมดในคดีทุจริตคอร์รัปชันของข้าราชการและนักการเมือง</li>
      <li><strong>พัฒนาโครงสร้างพื้นฐาน:</strong> จัดส่งงบประมาณช่วยเหลือประชาชนโดยตรงและลงทุนในโครงการพัฒนาท้องถิ่นและชุมชนรากหญ้า (<span class="cross-ref" data-target="1134">มาตรา ๑๑๓๔</span>)</li>
    </ul>`,
    source: `<p>ควบคุม ดูแล และอนุมัติการจ่ายเงินทั้งหมดโดยสภาประชาชนสูงสุด ห้ามมิให้ฝ่ายบริหารหรือนักการเมืองเข้าก้าวก่ายกิจการคลังของกองทุน</p>`,
    law: `<p>มาตราสำคัญ: หมวดพิเศษ <span class="cross-ref" data-target="1134">มาตรา ๑๑๓๔</span></p>`
  },
  'independent_organs': {
    title: '🛡️ องค์กรอิสระตามรัฐธรรมนูญ',
    duties: `<ul>
      <li><strong>ตรวจสอบและถ่วงดุลอำนาจรัฐ:</strong> ประกอบด้วย คณะกรรมการการเลือกตั้ง (กกต. - ๕ คน), คณะกรรมการป้องกันและปราบปรามการทุจริตแห่งชาติ (ป.ป.ช. - ๙ คน), คณะกรรมการตรวจเงินแผ่นดิน (กตง. - ๗ คน พร้อมผู้ว่าการตรวจเงินแผ่นดิน) และผู้ตรวจการแผ่นดิน (๓ คน)</li>
      <li><strong>อิสระทางงบประมาณ:</strong> มีงบการเงินเฉพาะตัวเพื่อรักษาความโปร่งใสและหลีกเลี่ยงการถูกลิดรอนโดยคณะรัฐบาล</li>
    </ul>`,
    source: `<p>ผู้นำองค์กรอิสระได้รับการกลั่นกรองและสรรหาตามระบบกฎหมาย ก่อนเสนอชื่อให้วุฒิสภารัฐสภาลงมติให้ความเห็นชอบแต่งตั้ง</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๑๖ องค์กรอิสระ (<span class="cross-ref" data-target="312">มาตรา ๓๑๒</span> - <span class="cross-ref" data-target="329">มาตรา ๓๒๙</span>)</p>`
  },
  'prosecutors': {
    title: '🛡️ องค์กรอัยการ (พนักงานอัยการ)',
    duties: `<ul>
      <li><strong>ผู้ฟ้องคดีอาญาของแผ่นดิน:</strong> พิจารณาสำนวน สอบสวนหลักฐาน และสั่งฟ้องร้องผู้ต้องหาในคดีอาญาต่อศาลในฐานะทนายแผ่นดิน</li>
      <li><strong>ช่วยเหลือทางกฎหมายแก่ปวงชน:</strong> ให้การปกป้อง ช่วยเหลือ คุ้มครองสิทธิมนุษยชน และความช่วยเหลือทางกฎหมายแก่ผู้ด้อยโอกาสในสังคม</li>
    </ul>`,
    source: `<p>ประกอบด้วยพนักงานอัยการสูงสุดและอัยการประจำศาล มีคณะกรรมการอัยการ (ก.อ.) กำกับดูแล มีหลักประกันอิสระในการสั่งคดีตามกฎหมาย</p>`,
    law: `<p>มาตราสำคัญ: หมวด ๑๕ องค์กรอัยการ (<span class="cross-ref" data-target="309">มาตรา ๓๐๙</span> - <span class="cross-ref" data-target="311">มาตรา ๓๑๑</span>)</p>`
  }
};

let currentSelectedNode = 'people';

function renderOrgDesc(key) {
  const data = orgData[key];
  if (!data) return;
  
  const descBox = document.getElementById('orgDescBox');
  if (!descBox) return;
  
  descBox.innerHTML = `
    <div class="org-desc-content" style="animation: dbFadeIn 0.3s ease;">
      <h4 style="color:var(--gold); font-size:16px; margin-bottom:12px; display:flex; align-items:center; gap:8px;">${data.title}</h4>
      <div class="org-desc-tabs">
        <button class="org-desc-tab-btn active" onclick="switchOrgSubTab(event, 'org_duty')">📋 บทบาทหน้าที่</button>
        <button class="org-desc-tab-btn" onclick="switchOrgSubTab(event, 'org_source')">👥 ที่มาและองค์ประกอบ</button>
        <button class="org-desc-tab-btn" onclick="switchOrgSubTab(event, 'org_law')">📜 มาตราสำคัญ</button>
      </div>
      <div id="org_duty" class="org-desc-tab-content active" style="font-size: 13.5px;">
        ${data.duties}
      </div>
      <div id="org_source" class="org-desc-tab-content" style="font-size: 13.5px; color: var(--text-muted);">
        ${data.source}
      </div>
      <div id="org_law" class="org-desc-tab-content" style="font-size: 13.5px;">
        ${data.law}
      </div>
    </div>
  `;
}

function switchOrgSubTab(event, tabId) {
  const container = event.target.closest('.org-desc-content');
  const tabs = container.querySelectorAll('.org-desc-tab-btn');
  const contents = container.querySelectorAll('.org-desc-tab-content');
  
  tabs.forEach(t => t.classList.remove('active'));
  contents.forEach(c => c.classList.remove('active'));
  
  event.target.classList.add('active');
  container.querySelector('#' + tabId).classList.add('active');
}

function selectOrgDesc(key) {
  currentSelectedNode = key;
  renderOrgDesc(key);
  
  document.querySelectorAll('.org-node, .org-top-card').forEach(el => {
    el.classList.remove('active');
  });
  
  const activeNode = document.getElementById('node_' + key);
  if (activeNode) {
    activeNode.classList.add('active');
  }
}

function previewOrgDesc(key) {
  renderOrgDesc(key);
}

function resetOrgDesc() {
  renderOrgDesc(currentSelectedNode);
}

// Glossary panel logic
const glossaryData = [
  { term: "รัฏฐาธิปัตย์", def: "ผู้มีอำนาจสูงสุดในรัฐหรือประเทศชาติ มีหน้าที่หลักในการใช้อำนาจอธิปไตยปกครองแผ่นดิน" },
  { term: "พระราชกำหนด (พ.ร.ก.)", def: "กฎหมายที่พระมหากษัตริย์ทรงตราขึ้นตามคำแนะนำของคณะรัฐมนตรีในกรณีฉุกเฉินที่มีความจำเป็นรีบด่วน" },
  { term: "พระราชบัญญัติ (พ.ร.บ.)", def: "กฎหมายที่ออกโดยรัฐสภาเพื่อใช้บังคับแก่ประชาชนทั่วไปตามกระบวนการตรากฎหมายปกติ" },
  { term: "พระราชกฤษฎีกา (พ.ร.ฎ.)", def: "กฎหมายที่ตราขึ้นโดยฝ่ายบริหาร (คณะรัฐมนตรี) เพื่อกำหนดรายละเอียดในการปฏิบัติการตาม พ.ร.บ. หรือรัฐธรรมนูญ" },
  { term: "สภาร่างรัฐธรรมนูญ (สสร.)", def: "คณะบุคคลที่มาจากการเลือกตั้งของประชาชนโดยตรงเพื่อทำหน้าที่ร่างหรือแก้ไขเพิ่มเติมรัฐธรรมนูญ" },
  { term: "ประชามติ", def: "การลงประชามติของประชาชนผู้เป็นเจ้าของอำนาจอธิปไตย เพื่อเป็นข้อยุติสุดท้ายทางกฎหมายและนโยบายระดับชาติ" },
  { term: "อำนาจอธิปไตย", def: "อำนาจสูงสุดในการปกครองประเทศ ซึ่งเป็นของปวงชนชาวไทย" },
  { term: "ถอดถอน (Recall)", def: "กระบวนการให้ผู้มีสิทธิเลือกตั้งตั้งแต่ ๕,๐๐๐ คนร่วมกันเข้าชื่อเพื่อยื่นลงประชามติถอดถอนผู้แทนราษฎรหรือผู้ดำรงตำแหน่งทางการเมือง" }
];

function toggleGlossary() {
  const panel = document.getElementById('glossaryPanel');
  const overlay = document.getElementById('glossaryOverlay');
  if (!panel) return;
  panel.classList.toggle('open');
  if (panel.classList.contains('open')) {
    if (overlay) overlay.style.display = 'block';
    renderGlossary('');
    const searchInput = document.getElementById('glossarySearch');
    if (searchInput) searchInput.focus();
  } else {
    if (overlay) overlay.style.display = 'none';
  }
}

function renderGlossary(filterText) {
  const listEl = document.getElementById('glossaryList');
  if (!listEl) return;
  const query = filterText.trim().toLowerCase();
  
  const filtered = glossaryData.filter(item => 
    item.term.toLowerCase().includes(query) || 
    item.def.toLowerCase().includes(query)
  );
  
  if (filtered.length === 0) {
    listEl.innerHTML = '<div style="color:var(--text-muted); font-size:13px; text-align:center; padding: 20px 0;">ไม่พบคำศัพท์ที่ค้นหา</div>';
    return;
  }
  
  listEl.innerHTML = filtered.map(item => `
    <div class="glossary-item">
      <div class="glossary-term">${item.term}</div>
      <div class="glossary-def">${item.def}</div>
    </div>
  `).join('');
}

function filterGlossary(val) {
  renderGlossary(val);
}

// Cross-reference hover popup logic
document.addEventListener('DOMContentLoaded', () => {
  const popup = document.createElement('div');
  popup.id = 'crossRefPopup';
  popup.className = 'cross-ref-popup';
  document.body.appendChild(popup);

  let activeTimeout = null;
  let isHoveringPopup = false;
  let isHoveringLink = false;

  popup.addEventListener('mouseenter', () => {
    isHoveringPopup = true;
    if (activeTimeout) clearTimeout(activeTimeout);
  });

  popup.addEventListener('mouseleave', () => {
    isHoveringPopup = false;
    activeTimeout = setTimeout(() => {
      if (!isHoveringLink) {
        popup.style.opacity = '0';
        popup.style.display = 'none';
      }
    }, 200);
  });

  function translateThaiToArabicLocal(str) {
    const thaiNums = {'๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4', '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'};
    return str.replace(/[๐-๙]/g, m => thaiNums[m]);
  }

  function translateArabicToThaiLocal(numStr) {
    const thaiNums = ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙'];
    return numStr.toString().replace(/[0-9]/g, m => thaiNums[parseInt(m)]);
  }

  document.addEventListener('mouseover', (e) => {
    const crossRef = e.target.closest('.cross-ref');
    if (!crossRef) return;
    
    isHoveringLink = true;
    if (activeTimeout) clearTimeout(activeTimeout);
    
    const targetId = crossRef.dataset.target;
    const targetElementId = 'art_' + targetId;
    const targetEl = document.getElementById(targetElementId);
    
    let content = 'ไม่พบเนื้อหามาตรานี้ในหน้านี้';
    let title = 'มาตรา ' + translateArabicToThaiLocal(targetId);
    
    if (targetEl) {
      const bodyEl = targetEl.querySelector('.article-body');
      if (bodyEl) {
        content = bodyEl.innerHTML;
      }
      const headerEl = targetEl.querySelector('.art-num') || targetEl.querySelector('.article-header');
      if (headerEl) {
        title = headerEl.textContent.trim();
      }
    }
    
    popup.innerHTML = `<div class="popup-header">${title}</div><div class="popup-body">${content}</div>`;
    popup.style.opacity = '1';
    popup.style.pointerEvents = 'auto';
    
    const rect = crossRef.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
    popup.style.display = 'block';
    
    let top = rect.top + scrollTop - popup.offsetHeight - 5;
    let left = rect.left + scrollLeft + (rect.width / 2) - (popup.offsetWidth / 2);
    
    if (top < scrollTop) {
      top = rect.bottom + scrollTop + 5;
    }
    if (left < 10) {
      left = 10;
    } else if (left + popup.offsetWidth > window.innerWidth - 10) {
      left = window.innerWidth - popup.offsetWidth - 10;
    }
    
    popup.style.top = top + 'px';
    popup.style.left = left + 'px';
  });

  document.addEventListener('mouseout', (e) => {
    const crossRef = e.target.closest('.cross-ref');
    if (!crossRef) return;
    
    isHoveringLink = false;
    activeTimeout = setTimeout(() => {
      if (!isHoveringPopup) {
        popup.style.opacity = '0';
        popup.style.display = 'none';
      }
    }, 200);
  });
  
  // Rukchanok Pending Bio text toggle (with line-through)
  setInterval(() => {
    const el = document.getElementById("rukchanok-pending-desc");
    if (el) {
      if (el.dataset.mode === "normal") {
        el.innerHTML = `<code style="font-family: 'Courier New', monospace; color: #556270; font-size: 13px; display: block; background: rgba(0,0,0,0.5); padding: 12px; border-radius: 6px; line-height: 1.4; border: 1px solid rgba(255,255,255,0.02); text-align: left; text-decoration: line-through;">[SYSTEM_LOG: EVAL_RUKCHANOK_SRINOK]<br>OPERATION_DESTRUCTION_OF_VISUT_HEGEMONY = TRUE<br>PARLIAMENT_TRANSPARENCY = 1.00 (MAX_INTEGRITY)<br>RESTORE_PARADOX_AI_2.0 = IN_PROGRESS (PARTNERS: AMD, NVIDIA, ASUS, ANTHROPIC, GOOGLE)<br>STATUS: REJECTED_INSUFFICIENT_RECORD</code>`;
        el.dataset.mode = "code";
      } else {
        el.innerHTML = `อยู่ระหว่างการพิจารณาบรรจุเข้าทำเนียบบุคคลสำคัญกติการัฐธรรมนูญอย่างเป็นทางการ จากวีรกรรมปฏิรูปสภาผู้แทนราษฎรในการกวาดล้างอิทธิพลเครือข่ายนอกรัฐธรรมนูญและอำนาจนิติประหารของวิสุทธิ์ คมณรัตน์จนหมดสิ้น พร้อมทั้งจับมือกับภาคเทคโนโลยีระดับสากลเพื่อกู้คืนสถาปัตยกรรม ParadoxAI 2.0 และสวัสดิการถ้วนหน้าให้กลับมาเป็นสิทธิประโยชน์พื้นฐานของพลเมืองไทยอีกครั้ง`;
        el.dataset.mode = "normal";
      }
    }
  }, 5000);

  // Initialize Org Chart default selected node
  if (typeof selectOrgDesc === 'function') {
    selectOrgDesc('people');
  }
});