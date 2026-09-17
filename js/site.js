/* website_new.html — the topic hub and stage, the charter's reading tools,
   search across both, cross-reference previews and mourning mode.
   Loads after js/constitution.js and wraps its switchTab, which the moved
   topic panels still call from their own buttons. */
(function () {
  'use strict';

  var TH = '๐๑๒๓๔๕๖๗๘๙';
  function toArabic(s) { return String(s).replace(/[๐-๙]/g, function (c) { return TH.indexOf(c); }); }
  function toThai(s) { return String(s).replace(/[0-9]/g, function (c) { return TH[+c]; }); }
  function norm(s) { return toArabic(s).toLowerCase().replace(/\s+/g, ' '); }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  // ── topic hub and stage ─────────────────────────────────────────────────
  var topics = $$('.nw-topic');
  var stage = $('#stage');
  function topicButton(id) { return $('.nw-topic[data-tab="' + id + '"]'); }
  function crumb(id) {
    var btn = topicButton(id);
    if (!btn) return;
    var group = btn.closest('.nw-group');
    $('#nwCrumbGroup').textContent = group ? $('.nw-group-name', group).textContent : '';
    $('#nwCrumbTopic').textContent = $('.nw-topic-tx', btn).textContent;
    var i = topics.indexOf(btn);
    $('#nwPrev').disabled = i <= 0;
    $('#nwNext').disabled = i >= topics.length - 1;
  }
  var legacySwitch = window.switchTab;
  var current = 'history-tab';
  window.switchTab = function (id, btn) {
    var hubBtn = topicButton(id);
    if (typeof legacySwitch === 'function') legacySwitch(id, hubBtn || btn);
    current = id;
    crumb(id);
    if (!btn || !stage.contains(btn)) {                 // chosen from the hub or the menu: bring the topic into view
      stage.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };
  function openTopic(id) { window.switchTab(id, topicButton(id)); }
  $('#nwPrev').addEventListener('click', function () { var i = topics.indexOf(topicButton(current)); if (i > 0) openTopic(topics[i - 1].dataset.tab); });
  $('#nwNext').addEventListener('click', function () { var i = topics.indexOf(topicButton(current)); if (i < topics.length - 1) openTopic(topics[i + 1].dataset.tab); });
  $$('[data-open]').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); openTopic(a.dataset.open); }); });
  crumb(current);

  // phones start with only the first group open
  if (window.matchMedia && matchMedia('(max-width: 720px)').matches) {
    $$('.nw-group').forEach(function (g, i) { g.open = i === 0; });
  }

  // ── charter: search and origin filters ──────────────────────────────────
  var arts = $$('.nw-art'), chapters = $$('.nw-chapter'), preamble = $('#preamble');
  var query = '', origin = 'all', index = null;
  function applyCharter() {
    var q = norm(query.trim());
    if (q && !index) index = arts.map(function (a) { return norm($('.nw-art-body', a).textContent); });
    var shown = 0, filtering = !!q || origin !== 'all';
    arts.forEach(function (a, i) {
      var ok = (origin === 'all' || a.dataset.origin === origin) && (!q || index[i].indexOf(q) >= 0 || a.id.slice(4) === q);
      a.classList.toggle('is-hidden', !ok);
      if (ok) shown++;
    });
    chapters.forEach(function (ch) {
      var any = !!ch.querySelector('.nw-art:not(.is-hidden)');
      ch.classList.toggle('is-hidden', filtering && !any);
      $$('.nw-part, .nw-clause', ch).forEach(function (el) { el.classList.toggle('is-hidden', filtering); });
      var link = $('.nw-toc-link[href="#' + ch.id + '"]');
      if (link) link.classList.toggle('is-empty', filtering && !any);
    });
    if (preamble) preamble.classList.toggle('is-hidden', filtering);
    var r = $('#nwResult');
    r.hidden = !filtering;
    if (filtering) r.textContent = shown ? 'ตัวบท: พบ ' + toThai(shown.toLocaleString('en-US')) + ' มาตรา' : 'ตัวบท: ไม่พบมาตราที่ตรงกับเงื่อนไข';
  }
  function applyHub() {
    var q = norm(query.trim()), shown = 0;
    topics.forEach(function (t) {
      var ok = !q || norm(t.textContent).indexOf(q) >= 0;
      t.classList.toggle('is-filtered-out', !ok);
      if (ok) shown++;
    });
    $$('.nw-group').forEach(function (g) {
      var any = !!g.querySelector('.nw-topic:not(.is-filtered-out)');
      g.classList.toggle('is-empty', !any);
      if (q && any) g.open = true;
    });
    var r = $('#nwHubResult');
    r.hidden = !q;
    if (q) r.textContent = shown ? 'พบ ' + toThai(shown) + ' หัวข้อ' : 'ไม่พบหัวข้อ — ดูผลในตัวบทด้านล่าง';
  }
  var timer = 0;
  $('#nwQ').addEventListener('input', function (e) {
    query = e.target.value;
    clearTimeout(timer);
    timer = setTimeout(function () { applyHub(); applyCharter(); }, 180);
  });
  $$('.nw-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      origin = chip.dataset.filter;
      $$('.nw-chip').forEach(function (c) { c.classList.toggle('is-on', c === chip); });
      applyCharter();
    });
  });
  var searchToggle = $('.nw-search-toggle');
  searchToggle.addEventListener('click', function () {
    var s = $('.nw-search');
    s.classList.toggle('is-open');
    if (s.classList.contains('is-open')) $('#nwQ').focus();
  });

  // ── jump to an article ──────────────────────────────────────────────────
  function goTo(num) {
    var el = document.getElementById('art_' + num);
    if (!el) return false;
    if (el.classList.contains('is-hidden')) {
      query = ''; origin = 'all'; $('#nwQ').value = '';
      $$('.nw-chip').forEach(function (c) { c.classList.toggle('is-on', c.dataset.filter === 'all'); });
      applyHub(); applyCharter();
    }
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.classList.remove('is-flash'); void el.offsetWidth; el.classList.add('is-flash');
    return true;
  }
  $('#nwJump').addEventListener('submit', function (e) {
    e.preventDefault();
    var input = $('#nwJumpInput'), n = toArabic(input.value).replace(/\D/g, '');
    if (n && !goTo(n)) { input.setCustomValidity('ไม่พบมาตรานี้'); input.reportValidity(); }
  });
  $('#nwJumpInput').addEventListener('input', function () { this.setCustomValidity(''); });

  // ── comparisons with the 2540 charter ───────────────────────────────────
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-compare]');
    if (!btn) return;
    var panel = document.getElementById('compare_' + btn.dataset.compare);
    panel.hidden = !panel.hidden;
    btn.setAttribute('aria-expanded', String(!panel.hidden));
    btn.textContent = panel.hidden ? 'เทียบกับ รธน. ๒๕๔๐' : 'ปิดการเปรียบเทียบ';
  });

  // ── cross-reference previews: hover on desktop, tap everywhere ──────────
  var popup = $('#nwPopup'), hideTimer = 0, pinned = false;
  function showRef(ref) {
    var raw = ref.dataset.target || '', num = toArabic(raw).replace(/\D/g, '');
    var target = document.getElementById('art_' + num);
    popup.innerHTML = '<div class="nw-popup-head"><b>มาตรา ' + toThai(raw) + '</b>' +
      (target ? '<a href="#art_' + num + '" data-goto="' + num + '">ไปที่มาตรานี้ ›</a>' : '') + '</div>' +
      (target ? $('.nw-art-body', target).innerHTML : '<p>ไม่พบเนื้อหามาตรานี้</p>');
    popup.hidden = false;
    var r = ref.getBoundingClientRect(), pw = popup.offsetWidth, ph = popup.offsetHeight;
    var top = r.top - ph - 8 < 80 ? r.bottom + window.pageYOffset + 8 : r.top + window.pageYOffset - ph - 8;
    popup.style.top = top + 'px';
    popup.style.left = Math.max(12, Math.min(r.left + r.width / 2 - pw / 2, document.documentElement.clientWidth - pw - 12)) + 'px';
  }
  if (window.matchMedia && matchMedia('(hover: hover)').matches) {
    document.addEventListener('mouseover', function (e) {
      var ref = e.target.closest('.cross-ref');
      if (ref && !popup.contains(ref)) { clearTimeout(hideTimer); showRef(ref); }
      else if (popup.contains(e.target)) clearTimeout(hideTimer);
    });
    document.addEventListener('mouseout', function (e) {
      if (!e.target.closest('.cross-ref') && !popup.contains(e.target)) return;
      clearTimeout(hideTimer);
      hideTimer = setTimeout(function () { if (!pinned) popup.hidden = true; }, 220);
    });
  }
  document.addEventListener('click', function (e) {
    var go = e.target.closest('[data-goto]');
    if (go) { e.preventDefault(); popup.hidden = true; pinned = false; goTo(go.dataset.goto); return; }
    var ref = e.target.closest('.cross-ref');
    if (ref && !popup.contains(ref)) { pinned = true; showRef(ref); return; }
    if (!popup.contains(e.target)) { pinned = false; popup.hidden = true; }
  });

  // ── charter table of contents ───────────────────────────────────────────
  var toc = $('#nwToc'), scrim = $('#nwScrim'), links = {};
  $$('.nw-toc-link').forEach(function (l) { links[l.getAttribute('href').slice(1)] = l; });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        $$('.nw-toc-link.is-here').forEach(function (l) { l.classList.remove('is-here'); });
        var l = links[en.target.id];
        if (!l) return;
        l.classList.add('is-here');
        if (!toc.classList.contains('is-open')) {
          var tr = toc.getBoundingClientRect(), lr = l.getBoundingClientRect();
          if (lr.top < tr.top || lr.bottom > tr.bottom) toc.scrollTop += lr.top - tr.top - tr.height / 3;
        }
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    chapters.concat(preamble ? [preamble] : []).forEach(function (s) { io.observe(s); });
  }
  function openToc(on) { toc.classList.toggle('is-open', on); scrim.hidden = !on; }
  $('.nw-toc-toggle').addEventListener('click', function () { openToc(!toc.classList.contains('is-open')); });
  toc.addEventListener('click', function (e) { if (e.target.closest('.nw-toc-link')) openToc(false); });
  scrim.addEventListener('click', function () { openToc(false); });

  // ── masthead: highlight where the reader is ─────────────────────────────
  var navLinks = $$('.nw-nav a[href^="#"]');
  var marks = [['hub', $('#hub')], ['stage', stage], ['charter', $('#charter')]];
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var y = window.pageYOffset + 120, here = 'hub';
      marks.forEach(function (m) { if (m[1] && m[1].offsetTop <= y) here = m[0]; });
      if (here === 'stage') here = 'hub';
      navLinks.forEach(function (a) { a.classList.toggle('is-on', a.getAttribute('href') === '#' + here && !a.dataset.open); });
      ticking = false;
    });
  }, { passive: true });

  // ── mourning mode: the old bw theme for the panels, html.mourning for the new layout ──
  var mBtn = $('#nwMourning');
  function setMourning(on) {
    document.documentElement.classList.toggle('mourning', on);
    if (typeof window.changeTheme === 'function') window.changeTheme(on ? 'bw' : 'dark');
    mBtn.setAttribute('aria-pressed', String(on));
  }
  setMourning(document.documentElement.classList.contains('mourning'));
  mBtn.addEventListener('click', function () { setMourning(!document.documentElement.classList.contains('mourning')); });

  // deep links: #art_8 opens the article, #some-tab opens that topic
  var h = location.hash.slice(1);
  if (/^art_\d+$/.test(h)) setTimeout(function () { goTo(h.slice(4)); }, 60);
  else if (topicButton(h)) setTimeout(function () { openTopic(h); }, 60);
})();
