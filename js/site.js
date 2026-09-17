/* website_new.html — reading tools for the charter: search, origin filters,
   jump to article, 2540 comparisons, cross-reference previews, table of
   contents, glossary and mourning mode. */
(function () {
  'use strict';

  var TH = '๐๑๒๓๔๕๖๗๘๙';
  function toArabic(s) { return String(s).replace(/[๐-๙]/g, function (c) { return TH.indexOf(c); }); }
  function toThai(s) { return String(s).replace(/[0-9]/g, function (c) { return TH[+c]; }); }
  function norm(s) { return toArabic(s).toLowerCase().replace(/\s+/g, ' '); }
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  var arts = $$('.art');
  var chapters = $$('.chapter');
  var preamble = $('#preamble');
  var result = $('#result');

  // ── search and filters work together ────────────────────────────────────
  var query = '', origin = 'all', index = null;
  function buildIndex() {
    if (index) return;
    index = arts.map(function (a) { return norm($('.art-body', a).textContent); });
  }
  function apply() {
    var q = norm(query.trim());
    if (q) buildIndex();
    var shown = 0;
    arts.forEach(function (a, i) {
      var ok = (origin === 'all' || a.dataset.origin === origin) && (!q || index[i].indexOf(q) >= 0 || toArabic(a.id.slice(4)) === q);
      a.classList.toggle('is-hidden', !ok);
      if (ok) shown++;
    });
    var filtering = q || origin !== 'all';
    chapters.forEach(function (ch) {
      var any = !!ch.querySelector('.art:not(.is-hidden)');
      ch.classList.toggle('is-hidden', filtering && !any);
      $$('.part, .clause', ch).forEach(function (el) { el.classList.toggle('is-hidden', !!filtering); });
      var link = $('.toc-link[href="#' + ch.id + '"]');
      if (link) link.classList.toggle('is-empty', filtering && !any);
    });
    if (preamble) preamble.classList.toggle('is-hidden', !!filtering);
    if (filtering) {
      result.hidden = false;
      result.textContent = shown ? 'พบ ' + toThai(shown.toLocaleString('en-US')) + ' มาตรา' : 'ไม่พบมาตราที่ตรงกับเงื่อนไข';
    } else {
      result.hidden = true;
    }
  }
  var searchTimer = 0;
  $('#q').addEventListener('input', function (e) {
    query = e.target.value;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(apply, 180);
  });
  $$('.chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      origin = chip.dataset.filter;
      $$('.chip').forEach(function (c) { c.classList.toggle('is-on', c === chip); });
      apply();
    });
  });

  // ── jump to an article ──────────────────────────────────────────────────
  function goTo(num) {
    var el = document.getElementById('art_' + num);
    if (!el) return false;
    if (el.classList.contains('is-hidden')) {           // clear filters that hide it
      query = ''; origin = 'all'; $('#q').value = '';
      $$('.chip').forEach(function (c) { c.classList.toggle('is-on', c.dataset.filter === 'all'); });
      apply();
    }
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    el.classList.remove('is-flash'); void el.offsetWidth; el.classList.add('is-flash');
    return true;
  }
  $('#jump').addEventListener('submit', function (e) {
    e.preventDefault();
    var n = toArabic($('#jumpInput').value).replace(/\D/g, '');
    if (n && !goTo(n)) { $('#jumpInput').setCustomValidity('ไม่พบมาตรานี้'); $('#jumpInput').reportValidity(); }
  });
  $('#jumpInput').addEventListener('input', function () { this.setCustomValidity(''); });

  // ── 2540 comparisons ────────────────────────────────────────────────────
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-compare]');
    if (!btn) return;
    var panel = document.getElementById('compare_' + btn.dataset.compare);
    if (!panel) return;
    panel.hidden = !panel.hidden;
    btn.setAttribute('aria-expanded', String(!panel.hidden));
    btn.textContent = panel.hidden ? 'เทียบกับ รธน. ๒๕๔๐' : 'ปิดการเปรียบเทียบ';
  });

  // ── cross-reference previews: hover on desktop, tap on touch ────────────
  var popup = $('#popup'), hideTimer = 0, pinned = null;
  function showRef(ref) {
    var num = toArabic(ref.dataset.target || '').replace(/[^\d]/g, '');
    var target = document.getElementById('art_' + num);
    var title = 'มาตรา ' + toThai(ref.dataset.target || '');
    popup.innerHTML = '<div class="popup-head"><b>' + title + '</b>' +
      (target ? '<a href="#art_' + num + '" data-goto="' + num + '">ไปที่มาตรานี้ ›</a>' : '') + '</div>' +
      (target ? $('.art-body', target).innerHTML : '<p>ไม่พบเนื้อหามาตรานี้ในหน้านี้</p>');
    popup.hidden = false;
    var r = ref.getBoundingClientRect(), pw = popup.offsetWidth, ph = popup.offsetHeight;
    var top = r.top + window.pageYOffset - ph - 8;
    if (r.top - ph - 8 < 120) top = r.bottom + window.pageYOffset + 8;
    var left = Math.max(12, Math.min(r.left + r.width / 2 - pw / 2, document.documentElement.clientWidth - pw - 12));
    popup.style.top = top + 'px';
    popup.style.left = left + 'px';
  }
  function hideSoon() { clearTimeout(hideTimer); hideTimer = setTimeout(function () { if (!pinned) popup.hidden = true; }, 220); }
  var hover = window.matchMedia && matchMedia('(hover: hover)').matches;
  if (hover) {
    document.addEventListener('mouseover', function (e) {
      var ref = e.target.closest('.cross-ref');
      if (ref && !popup.contains(ref)) { clearTimeout(hideTimer); showRef(ref); }
      else if (popup.contains(e.target)) clearTimeout(hideTimer);
    });
    document.addEventListener('mouseout', function (e) {
      if (e.target.closest('.cross-ref') || popup.contains(e.target)) hideSoon();
    });
  }
  document.addEventListener('click', function (e) {
    var go = e.target.closest('[data-goto]');
    if (go) { e.preventDefault(); popup.hidden = true; pinned = null; goTo(go.dataset.goto); return; }
    var ref = e.target.closest('.cross-ref');
    if (ref) { pinned = ref; showRef(ref); return; }
    if (!popup.contains(e.target)) { pinned = null; popup.hidden = true; }
  });

  // ── table of contents: where am I, and the drawer on small screens ──────
  var toc = $('#toc'), scrim = $('#scrim');
  var links = {};
  $$('.toc-link').forEach(function (l) { links[l.getAttribute('href').slice(1)] = l; });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        $$('.toc-link.is-here').forEach(function (l) { l.classList.remove('is-here'); });
        var l = links[en.target.id];
        if (l) {
          l.classList.add('is-here');
          if (!toc.classList.contains('is-open')) {
            var tr = toc.getBoundingClientRect(), lr = l.getBoundingClientRect();
            if (lr.top < tr.top || lr.bottom > tr.bottom) toc.scrollTop += lr.top - tr.top - tr.height / 3;
          }
        }
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    chapters.concat(preamble ? [preamble] : []).forEach(function (s) { io.observe(s); });
  }
  function openToc(on) {
    toc.classList.toggle('is-open', on);
    scrim.hidden = !on && $('#glossary').hidden;
  }
  $('.toc-toggle').addEventListener('click', function () { openToc(!toc.classList.contains('is-open')); });
  toc.addEventListener('click', function (e) { if (e.target.closest('.toc-link')) openToc(false); });

  // mobile search toggle
  var searchToggle = $('.search-toggle');
  if (searchToggle) searchToggle.addEventListener('click', function () {
    var s = $('.search');
    s.classList.toggle('is-open');
    if (s.classList.contains('is-open')) $('#q').focus();
  });

  // ── glossary ────────────────────────────────────────────────────────────
  var glossary = $('#glossary'), gList = $('#glossaryList');
  function renderGlossary(text) {
    var q = norm(text || '');
    var items = (window.GLOSSARY || []).filter(function (g) { return !q || norm(g.term + ' ' + g.def).indexOf(q) >= 0; });
    gList.innerHTML = items.length ? items.map(function (g) {
      return '<div class="g-item"><div class="g-term">' + g.term + '</div><div class="g-def">' + g.def + '</div></div>';
    }).join('') : '<p class="g-def">ไม่พบคำศัพท์ที่ค้นหา</p>';
  }
  function openGlossary(on) {
    glossary.hidden = !on;
    scrim.hidden = !on && !toc.classList.contains('is-open');
    if (on) { renderGlossary($('#glossaryQ').value); $('#glossaryQ').focus(); }
  }
  $('#glossaryBtn').addEventListener('click', function () { openGlossary(true); });
  $('#glossaryClose').addEventListener('click', function () { openGlossary(false); });
  $('#glossaryQ').addEventListener('input', function () { renderGlossary(this.value); });
  scrim.addEventListener('click', function () { openGlossary(false); openToc(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    openGlossary(false); openToc(false); popup.hidden = true; pinned = null;
  });

  // ── mourning mode (shares the old site's saved 'bw' theme) ──────────────
  var mBtn = $('#mourningBtn');
  function setMourning(on) {
    document.documentElement.classList.toggle('mourning', on);
    mBtn.setAttribute('aria-pressed', String(on));
    try { localStorage.setItem('constTheme', on ? 'bw' : 'dark'); } catch (e) {}
  }
  mBtn.setAttribute('aria-pressed', String(document.documentElement.classList.contains('mourning')));
  mBtn.addEventListener('click', function () { setMourning(!document.documentElement.classList.contains('mourning')); });

  // ── back to top ─────────────────────────────────────────────────────────
  var toTop = $('#toTop'), ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { toTop.classList.toggle('is-on', window.pageYOffset > 900); ticking = false; });
  }, { passive: true });

  // deep links such as website_new.html#art_8
  if (/^#art_\d+$/.test(location.hash)) setTimeout(function () { goTo(location.hash.slice(5)); }, 50);
})();
