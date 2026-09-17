/* <portrait-hall base="images/hall/"> — the walk-it-yourself portrait hall.
   Drawn on a canvas like the homepage intro. Drag (or swipe sideways on a
   phone), use the wheel or arrow keys, the ‹ › buttons, or click the rail.
   Needs js/hall-data.js loaded first.

   Differences from the Claude Design study it grew out of: it only draws while
   something moves, sideways swipes work on phones, jumps no longer fight the
   snap-to-portrait, it waits for a real size inside hidden tabs, and only
   King Rama IX has the gilded frame. */
(function () {
  'use strict';
  if (!window.customElements || customElements.get('portrait-hall')) return;

  var P = 800, KING9 = 4, PM33 = 21, MINP = -1.3, MAXP = PM33 + 0.5;
  var FD = "'Taviraj','Sarabun',serif", FS = "'Sarabun',system-ui,sans-serif";
  var GOLD = '#d4af37';

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function mk(tag, css, parent) {
    var el = document.createElement(tag);
    if (css) el.style.cssText = css;
    if (parent) parent.appendChild(el);
    return el;
  }

  class Hall extends HTMLElement {
    connectedCallback() {
      if (this._api || !window.HALL_DATA) return;
      this._api = build(this);
    }
    disconnectedCallback() {
      if (this._api) { this._api.destroy(); this._api = null; }
    }
  }

  function build(el) {
    var DATA = window.HALL_DATA, base = el.getAttribute('base') || 'images/hall/';
    el.style.cssText += ';position:relative;display:block;overflow:hidden;outline:none;cursor:grab;touch-action:pan-y;' +
      'background:radial-gradient(ellipse 80% 62% at 50% 44%,#17150f 0%,#0a0908 58%,#040404 100%)';
    el.tabIndex = 0;
    el.innerHTML = '';

    var canvas = mk('canvas', 'position:absolute;inset:0;width:100%;height:100%;display:block', el);
    var ctx = canvas.getContext('2d');
    mk('div', 'position:absolute;inset:0;pointer-events:none;background:' +
      'radial-gradient(ellipse 72% 62% at 50% 44%,transparent 28%,rgba(4,4,4,.82) 100%),' +
      'linear-gradient(180deg,rgba(4,4,4,.9),transparent 20%,transparent 78%,rgba(4,4,4,.75))', el);
    var capLayer = mk('div', 'position:absolute;inset:0;pointer-events:none;overflow:hidden', el);

    var dead = false, raf = 0, images = [];
    function img(src) {
      var im = new Image();
      im.decoding = 'async';
      im.onload = function () { if (!dead) requestRender(); };
      im.src = src;
      images.push(im);
      return im;
    }

    // ── items: kings in pairs, King Rama IX alone, PMs in pairs, PM 33 alone ──
    var items = [];
    DATA.kings.forEach(function (k, i) {
      var solo = i === 8;
      items.push({ slot: solo ? KING9 : Math.floor(i / 2), side: solo ? 0 : (i % 2 ? 1 : -1),
        sharp: img(base + k.img + '.jpg'), soft: img(base + k.img + 'b.jpg'),
        label: k.label, name: k.name, years: k.years, gold: solo, era: 0 });
    });
    DATA.pms.forEach(function (pm, i) {
      var solo = i === 32;
      items.push({ slot: solo ? PM33 : 5 + Math.floor(i / 2), side: solo ? 0 : (i % 2 ? 1 : -1),
        sharp: img(base + pm.img + '.jpg'), soft: img(base + pm.img + 'b.jpg'),
        label: pm.label, name: pm.name, years: pm.years, gold: false, era: 1 });
    });

    var g = null, vw = 0, vh = 0, dpr = 1, T = 1, woodTex = null, goldTex = null;
    var p = -0.35, vel = 0, drag = null, jump = null, engaged = false;

    // ── frame textures, painted once per size ────────────────────────────────
    function frameTexture(gold, scale) {
      var fw = g.fw * scale, fh = g.fh * scale, m = g.m * scale, pad = fw * (gold ? 0.095 : 0.062);
      var c = document.createElement('canvas');
      c.width = Math.max(1, Math.ceil((fw + 2 * m) * T));
      c.height = Math.max(1, Math.ceil((fh + 2 * m) * T));
      var x = c.getContext('2d');
      x.scale(T, T);
      x.translate(m, m);
      function ring() { x.beginPath(); x.rect(0, 0, fw, fh); x.rect(pad, pad, fw - 2 * pad, fh - 2 * pad); }
      var body = x.createLinearGradient(0, 0, fw, fh);
      (gold
        ? [[0, '#fff1b8'], [0.16, '#d8ad3e'], [0.3, '#8a6414'], [0.46, '#f7dc85'], [0.6, '#b8871f'], [0.76, '#fff0b0'], [1, '#9c7418']]
        : [[0, '#6b4526'], [0.3, '#3d2513'], [0.52, '#7a4f2a'], [0.78, '#33200f'], [1, '#5a3a1f']]
      ).forEach(function (s) { body.addColorStop(s[0], s[1]); });

      x.save();
      x.shadowColor = 'rgba(0,0,0,.72)';
      x.shadowBlur = 0.13 * fw * T;
      x.shadowOffsetY = 0.045 * fw * T;
      x.fillStyle = body; ring(); x.fill('evenodd');
      if (gold) { x.shadowColor = 'rgba(255,214,110,.55)'; x.shadowBlur = 0.32 * fw * T; x.shadowOffsetY = 0; ring(); x.fill('evenodd'); }
      x.restore();

      if (!gold) {                                   // wood grain along the rails, then down the stiles
        [[0, 0, fw, pad, 1], [0, fh - pad, fw, pad, 1], [0, pad, pad, fh - 2 * pad, 0], [fw - pad, pad, pad, fh - 2 * pad, 0]]
          .forEach(function (r) {
            x.save();
            x.beginPath(); x.rect(r[0], r[1], r[2], r[3]); x.clip();
            for (var i = 0; i < 22; i++) {
              var t = (i + 0.5) / 22;
              x.strokeStyle = i % 3 ? 'rgba(0,0,0,.22)' : 'rgba(255,208,152,.07)';
              x.lineWidth = fw * (0.002 + (i % 4) * 0.001);
              x.beginPath();
              if (r[4]) {
                var yy = r[1] + t * r[3];
                x.moveTo(r[0], yy);
                x.bezierCurveTo(fw * 0.35, yy + fw * 0.005, fw * 0.65, yy - fw * 0.005, fw, yy);
              } else {
                var xx = r[0] + t * r[2];
                x.moveTo(xx, r[1]);
                x.bezierCurveTo(xx + fw * 0.005, fh * 0.35, xx - fw * 0.005, fh * 0.65, xx, fh);
              }
              x.stroke();
            }
            x.restore();
          });
      }

      var lw = fw * 0.012;                           // bevels: lit top-left, shaded bottom-right
      x.lineWidth = lw;
      x.strokeStyle = gold ? '#fff3c4' : 'rgba(255,214,164,.28)';
      x.beginPath(); x.moveTo(lw / 2, fh); x.lineTo(lw / 2, lw / 2); x.lineTo(fw, lw / 2); x.stroke();
      x.beginPath(); x.moveTo(fw - pad, pad); x.lineTo(fw - pad, fh - pad); x.lineTo(pad, fh - pad); x.stroke();
      x.strokeStyle = gold ? '#7a5610' : 'rgba(0,0,0,.58)';
      x.beginPath(); x.moveTo(fw - lw / 2, 0); x.lineTo(fw - lw / 2, fh - lw / 2); x.lineTo(0, fh - lw / 2); x.stroke();
      x.beginPath(); x.moveTo(pad, fh - pad); x.lineTo(pad, pad); x.lineTo(fw - pad, pad); x.stroke();
      x.lineWidth = fw * 0.004;
      x.strokeStyle = gold ? 'rgba(122,86,16,.6)' : 'rgba(0,0,0,.42)';
      [[0, 0, pad, pad], [fw, 0, fw - pad, pad], [0, fh, pad, fh - pad], [fw, fh, fw - pad, fh - pad]].forEach(function (l) {
        x.beginPath(); x.moveTo(l[0], l[1]); x.lineTo(l[2], l[3]); x.stroke();
      });
      x.lineWidth = fw * 0.011;                      // gold fillet around the picture
      x.strokeStyle = gold ? '#fff3c4' : '#c9a24a';
      x.strokeRect(pad - fw * 0.006, pad - fw * 0.006, fw - 2 * pad + fw * 0.012, fh - 2 * pad + fw * 0.012);

      if (gold) {                                    // beading and corner rosettes
        var inset = fw * 0.046, r = fw * 0.0075, step = fw * 0.031;
        x.fillStyle = '#fff6d6';
        [[inset, inset, fw - inset, inset], [fw - inset, inset, fw - inset, fh - inset],
         [fw - inset, fh - inset, inset, fh - inset], [inset, fh - inset, inset, inset]].forEach(function (e) {
          var len = Math.hypot(e[2] - e[0], e[3] - e[1]), n = Math.floor(len / step);
          for (var j = 0; j < n; j++) {
            x.beginPath();
            x.arc(e[0] + (e[2] - e[0]) * j / n, e[1] + (e[3] - e[1]) * j / n, r, 0, Math.PI * 2);
            x.fill();
          }
        });
        [[inset, inset], [fw - inset, inset], [inset, fh - inset], [fw - inset, fh - inset]].forEach(function (pt) {
          [[0.042, '#7a5610'], [0.034, '#e8c25a'], [0.022, '#f3d27a'], [0.013, '#fffbe6']].forEach(function (rg) {
            x.fillStyle = rg[1];
            x.beginPath(); x.arc(pt[0], pt[1], fw * rg[0], 0, Math.PI * 2); x.fill();
          });
        });
      }
      return c;
    }

    // ── geometry; returns false while the element has no size (a hidden tab) ──
    function layout() {
      vw = el.clientWidth;
      vh = el.clientHeight;
      if (vw < 40 || vh < 40) { g = null; return false; }
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(vw * dpr);
      canvas.height = Math.round(vh * dpr);
      var narrow = vw < 760, near = 560, f = P / (P + near);
      var fwProj = Math.min(narrow ? vw * 0.34 : vw * 0.168, vh * 0.30, 268);
      g = { near: near, W: (narrow ? vw * 0.26 : Math.min(vw * 0.198, 322)) / f, fw: fwProj / f / 0.88 };
      g.fh = g.fw * 1.28;
      g.D = Math.max(g.fw * 2.6, 900);
      g.m = g.fw * 0.16;
      g.halfW = g.W + g.fw * 0.75;
      g.wallH = g.fh * 3.25;
      T = 0.92 * dpr;
      woodTex = frameTexture(false, 1);
      goldTex = frameTexture(true, 1.1);
      return true;
    }

    function proj(x, y, d) { var k = P / (P + d); return [vw / 2 + x * k, vh * 0.455 + y * k]; }
    function quad(a, b, c, d, fill) {
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.lineTo(d[0], d[1]); ctx.closePath();
      ctx.fillStyle = fill; ctx.fill();
    }
    function line(a, b, color, w) {
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]);
      ctx.strokeStyle = color; ctx.lineWidth = w; ctx.stroke();
    }

    function look(it) {
      var f = it.side === 0 ? 1 - clamp((p - (it.slot + 0.06)) / 0.4, 0, 1) : 1;   // lone portraits step aside as you pass
      if (f <= 0.004) return null;
      var dist = g.near + (it.slot - p) * g.D;
      if (dist <= 30 || dist >= g.near + 3.4 * g.D) return null;
      var far = Math.max(0, dist - g.near) / g.D;
      var o = clamp(1.28 - far / 2.6, 0, 1);
      if (dist < g.near * 0.6) o *= clamp((dist - 30) / (g.near * 0.6 - 30), 0, 1);
      return { o: o * f, s: clamp(1 - far * 1.3, 0, 1), c: clamp(1 - far * 1.7, 0, 1), d: dist };
    }

    // ── the room ─────────────────────────────────────────────────────────────
    function room() {
      var dN = -P * 0.55, dF = g.near + 3.9 * g.D, hw = g.halfW;
      var fy = g.fh * 1.45, wt = g.fh * 0.05 - g.wallH / 2, wb = g.fh * 0.05 + g.wallH / 2;
      var dado = wt + g.wallH * 0.645, cw = hw * 0.62;
      ctx.globalAlpha = 1;
      quad(proj(-hw, fy, dN), proj(hw, fy, dN), proj(hw, fy, dF), proj(-hw, fy, dF), '#100e0b');
      var cg = ctx.createLinearGradient(0, proj(0, fy, dN)[1], 0, proj(0, fy, dF)[1]);
      cg.addColorStop(0, '#5e171c'); cg.addColorStop(1, '#1c0809');
      quad(proj(-cw, fy, dN), proj(cw, fy, dN), proj(cw, fy, dF), proj(-cw, fy, dF), cg);
      line(proj(-cw, fy, dN), proj(-cw, fy, dF), 'rgba(184,147,63,.85)', 2);
      line(proj(cw, fy, dN), proj(cw, fy, dF), 'rgba(184,147,63,.85)', 2);
      for (var j = Math.ceil((p - 0.9) * 4); j <= Math.floor((p + 3.9) * 4); j++) {
        var dd = g.near + (j / 4 - p) * g.D;
        if (dd > dN) line(proj(-hw, fy, dd), proj(hw, fy, dd), 'rgba(0,0,0,.28)', 1.5);
      }
      quad(proj(-hw, wt, dN), proj(hw, wt, dN), proj(hw, wt, dF), proj(-hw, wt, dF), '#0b0a08');
      quad(proj(-hw * 0.3, wt, dN), proj(hw * 0.3, wt, dN), proj(hw * 0.3, wt, dF), proj(-hw * 0.3, wt, dF), '#141109');
      line(proj(-hw * 0.3, wt, dN), proj(-hw * 0.3, wt, dF), 'rgba(184,147,63,.3)', 1);
      line(proj(hw * 0.3, wt, dN), proj(hw * 0.3, wt, dF), 'rgba(184,147,63,.3)', 1);
      ctx.globalCompositeOperation = 'lighter';
      for (var c = Math.floor(p) - 1; c <= Math.ceil(p + 3.4); c++) {
        var dl = g.near + (c + 0.5 - p) * g.D;
        if (dl < 60) continue;
        var lp = proj(0, wt, dl), rad = g.fw * 0.5 * P / (P + dl);
        if (rad < 1.5) continue;
        var lg = ctx.createRadialGradient(lp[0], lp[1], 0, lp[0], lp[1], rad);
        lg.addColorStop(0, 'rgba(255,232,170,.40)');
        lg.addColorStop(1, 'rgba(255,232,170,0)');
        ctx.fillStyle = lg;
        ctx.fillRect(lp[0] - rad, lp[1] - rad, rad * 2, rad * 2);
      }
      ctx.globalCompositeOperation = 'source-over';
      [-1, 1].forEach(function (s) {
        var x = s * hw;
        quad(proj(x, wt, dN), proj(x, wt, dF), proj(x, dado, dF), proj(x, dado, dN), '#1a150d');
        quad(proj(x, dado, dN), proj(x, dado, dF), proj(x, wb, dF), proj(x, wb, dN), '#0d0b08');
        line(proj(x, dado, dN), proj(x, dado, dF), '#b8933f', 2);
        for (var k = Math.floor(p) - 2; k <= Math.ceil(p + 4); k++) {
          var d1 = g.near + (k + 0.45 - p) * g.D, d2 = d1 + 0.1 * g.D;
          if (d2 <= dN || d1 >= dF) continue;
          d1 = Math.max(d1, dN);
          quad(proj(x, wt, d1), proj(x, wt, d2), proj(x, wb, d2), proj(x, wb, d1), 'rgba(0,0,0,.38)');
          line(proj(x, wt, d1), proj(x, wb, d1), 'rgba(184,147,63,.18)', 1);
          line(proj(x, wt, d2), proj(x, wb, d2), 'rgba(184,147,63,.18)', 1);
        }
      });
    }

    // ── portraits ────────────────────────────────────────────────────────────
    function photo(im, u0, u1, dx, dy, dw, dh, ratio) {
      if (!im.complete || !im.naturalWidth || dw <= 0) return;
      var iw = im.naturalWidth, ih = im.naturalHeight, sx = 0, sy = 0, sw = iw, sh = ih;
      if (iw / ih > ratio) { sw = ih * ratio; sx = (iw - sw) / 2; } else { sh = iw / ratio; sy = (ih - sh) * 0.22; }
      ctx.drawImage(im, sx + u0 * sw, sy, (u1 - u0) * sw, sh, dx, dy, dw, dh);
    }

    function glow(it, v) {                           // lamp light on the wall and a pool on the floor
      var sc = it.side ? 1 : 1.1, fw = g.fw * sc, fh = g.fh * sc, k = P / (P + v.d);
      if (k <= 0 || k > 6) return;
      var cx = vw / 2 + it.side * g.W * k, cy = vh * 0.455, yc = it.side ? -g.fh * 0.12 : g.fh * 0.1;
      ctx.globalCompositeOperation = 'lighter';
      var r1 = fw * 1.45 * k, wy = cy + (yc - fh * 0.15) * k;
      var wash = ctx.createRadialGradient(cx, wy, 0, cx, wy, r1);
      wash.addColorStop(0, 'rgba(255,226,152,' + (0.13 * v.o).toFixed(3) + ')');
      wash.addColorStop(1, 'rgba(255,226,152,0)');
      ctx.fillStyle = wash;
      ctx.fillRect(cx - r1, wy - r1, r1 * 2, r1 * 2);
      var rx = fw * 0.95 * k, ry = fw * 0.2 * k;
      if (rx > 2) {
        ctx.save();
        ctx.translate(vw / 2 + it.side * g.W * 0.84 * k, cy + g.fh * 1.45 * k);
        ctx.scale(1, ry / rx);
        var pool = ctx.createRadialGradient(0, 0, 0, 0, 0, rx);
        pool.addColorStop(0, 'rgba(255,220,150,' + (0.16 * v.o).toFixed(3) + ')');
        pool.addColorStop(1, 'rgba(255,220,150,0)');
        ctx.fillStyle = pool;
        ctx.beginPath(); ctx.arc(0, 0, rx, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
      }
      ctx.globalCompositeOperation = 'source-over';
    }

    function portrait(it, v) {
      var sc = it.side ? 1 : 1.1, fw = g.fw * sc, fh = g.fh * sc, m = g.m * sc;
      var tex = it.gold ? goldTex : woodTex, pad = fw * (it.gold ? 0.095 : 0.062);
      var d = v.d, yc = it.side ? -g.fh * 0.12 : g.fh * 0.1, cy = vh * 0.455;
      var ow = fw + 2 * m, oh = fh + 2 * m, ang = it.side ? 0.4887 : 0, cos = Math.cos(ang), sin = Math.sin(ang);
      function at(a) {
        var dd = d - it.side * a * sin, k = P / (P + dd);
        return { x: vw / 2 + (it.side * g.W + a * cos) * k, k: k };
      }
      var eA = at(-ow / 2), eB = at(ow / 2), rise = Math.abs(eA.k - eB.k) * oh / 2;
      var N = it.side ? Math.max(2, Math.min(44, Math.ceil(rise / 0.8))) : 1;
      var pa0 = -fw / 2 + pad, pa1 = fw / 2 - pad, ratio = (fw - 2 * pad) / (fh - 2 * pad);
      for (var i = 0; i < N; i++) {
        var a0 = -ow / 2 + ow * i / N, a1 = -ow / 2 + ow * (i + 1) / N;
        var e0 = at(a0), e1 = at(a1), em = at((a0 + a1) / 2);
        if (em.k <= 0 || em.k > 6) continue;
        var x0 = Math.floor(e0.x * dpr) / dpr, x1 = Math.ceil(e1.x * dpr) / dpr;
        var ia0 = Math.max(a0, pa0), ia1 = Math.min(a1, pa1);
        if (ia1 > ia0) {
          var q0 = Math.floor(at(ia0).x * dpr) / dpr, q1 = Math.ceil(at(ia1).x * dpr) / dpr;
          var py = cy + (yc - fh / 2 + pad) * em.k, ph = (fh - 2 * pad) * em.k;
          var u0 = (ia0 - pa0) / (pa1 - pa0), u1 = (ia1 - pa0) / (pa1 - pa0);
          ctx.globalAlpha = v.o;
          photo(it.soft, u0, u1, q0, py, q1 - q0, ph, ratio);
          if (v.s > 0.01) { ctx.globalAlpha = v.o * v.s; photo(it.sharp, u0, u1, q0, py, q1 - q0, ph, ratio); }
        }
        ctx.globalAlpha = v.o;
        ctx.drawImage(tex, tex.width * i / N, 0, tex.width / N, tex.height, x0, cy + (yc - oh / 2) * em.k, x1 - x0, oh * em.k);
      }
      ctx.globalAlpha = 1;
    }

    // ── captions as live text, sharp at any size ─────────────────────────────
    var capPool = [];
    for (var ci = 0; ci < 9; ci++) {
      var n = mk('div', 'position:absolute;left:0;top:0;transform:translate(-9999px,0);text-align:center;' +
        'will-change:transform,opacity;line-height:1.35;text-wrap:balance', capLayer);
      n._l = mk('div', 'font-family:' + FS + ';font-weight:600;letter-spacing:.06em;color:' + GOLD + ';font-size:.62em;text-shadow:0 2px 10px rgba(0,0,0,.95)', n);
      n._n = mk('div', 'font-family:' + FD + ';font-weight:600;color:#f4ead2;font-size:1em;white-space:pre-line;margin-top:.18em;text-shadow:0 2px 14px rgba(0,0,0,.98)', n);
      n._y = mk('div', 'font-family:' + FS + ';font-weight:400;color:#b3a88f;font-size:.6em;margin-top:.2em;text-shadow:0 2px 10px rgba(0,0,0,.95)', n);
      capPool.push(n);
    }
    function captions(vis) {
      var used = 0;
      vis.slice(-capPool.length).forEach(function (o) {
        var it = o.it, v = o.v;
        if (v.c < 0.02) return;
        var node = capPool[used++];
        var sc = it.side ? 1 : 1.1, fw = g.fw * sc, fh = g.fh * sc, k = P / (P + v.d);
        var w = fw * (it.side ? (vw < 760 ? 1.05 : 1.3) : 2.0) * k;
        var y = vh * 0.455 + ((it.side ? -g.fh * 0.12 : g.fh * 0.1) + fh / 2 + fw * 0.07) * k;
        var x = vw / 2 + it.side * g.W * k;
        if (node._t !== it) {
          node._t = it;
          node._l.textContent = it.label;
          node._n.textContent = it.name;
          node._y.textContent = it.years;
        }
        node.style.width = w.toFixed(1) + 'px';
        node.style.fontSize = Math.max(6, fw * 0.085 * k).toFixed(2) + 'px';
        node.style.transform = 'translate(' + (x - w / 2).toFixed(1) + 'px,' + y.toFixed(1) + 'px)';
        node.style.opacity = (v.o * v.c).toFixed(3);
      });
      for (var i = used; i < capPool.length; i++) capPool[i].style.opacity = '0';
    }

    // ── UI: readout, square black-and-gold ‹ › buttons, era rail ─────────────
    var readK = mk('div', 'font-size:11px;letter-spacing:.28em;color:#8b7a52;font-weight:600',
      mk('div', 'position:absolute;left:22px;top:20px;font-family:' + FS + ';pointer-events:none', el));
    var readN = mk('div', 'font-family:' + FD + ';font-size:17px;color:#f4ead2;margin-top:6px;font-weight:600', readK.parentNode);

    var rail = mk('div', 'position:absolute;left:0;right:0;bottom:0;height:58px;display:flex;align-items:flex-end;padding:0 22px 14px', el);
    var track = mk('div', 'position:relative;flex:1;height:26px;cursor:pointer', rail);
    mk('div', 'position:absolute;left:0;top:0;width:' + (100 * 5 / 22) + '%;height:11px;' +
      'border:1px solid rgba(212,175,55,.55);border-top:0', track);
    mk('div', 'position:absolute;left:' + (100 * 5 / 22) + '%;right:0;top:0;height:11px;' +
      'border-bottom:1px solid rgba(212,175,55,.3);border-right:1px solid rgba(212,175,55,.3)', track);
    mk('div', 'position:absolute;left:2%;top:13px;font:600 10px ' + FS + ';letter-spacing:.2em;color:#b3964f', track).textContent = 'รัชกาลที่ ๑–๙';
    mk('div', 'position:absolute;left:' + (100 * 5 / 22 + 2) + '%;top:13px;font:600 10px ' + FS + ';letter-spacing:.2em;color:#8a8170', track)
      .textContent = 'นายกรัฐมนตรีคนที่ ๑–๓๓';
    var marker = mk('div', 'position:absolute;top:-4px;left:0;width:9px;height:9px;background:#f3dc8a;margin-left:-4.5px;' +
      'transform:rotate(45deg);box-shadow:0 0 10px rgba(243,220,138,.8)', track);

    [['‹', -1, 'left:16px'], ['›', 1, 'right:16px']].forEach(function (b) {
      var btn = mk('button', 'position:absolute;top:50%;' + b[2] + ';transform:translateY(-50%);width:44px;height:44px;' +
        'border-radius:2px;border:1px solid rgba(212,175,55,.8);background:linear-gradient(180deg,#16130c,#0a0907);color:#e2c170;' +
        'font:400 24px ' + FS + ';line-height:1;cursor:pointer;box-shadow:0 0 22px rgba(212,175,55,.18),inset 0 0 14px rgba(212,175,55,.06);' +
        'outline:1px solid rgba(212,175,55,.25);outline-offset:-5px;transition:box-shadow .3s,color .3s,border-color .3s', el);
      btn.type = 'button';
      btn.textContent = b[0];
      btn.setAttribute('aria-label', b[1] > 0 ? 'ภาพถัดไป' : 'ภาพก่อนหน้า');
      btn.addEventListener('mouseenter', function () { btn.style.color = '#f6dd92'; btn.style.borderColor = '#f3dc8a'; btn.style.boxShadow = '0 0 34px rgba(212,175,55,.38),inset 0 0 18px rgba(212,175,55,.12)'; });
      btn.addEventListener('mouseleave', function () { btn.style.color = '#e2c170'; btn.style.borderColor = 'rgba(212,175,55,.8)'; btn.style.boxShadow = '0 0 22px rgba(212,175,55,.18),inset 0 0 14px rgba(212,175,55,.06)'; });
      btn.addEventListener('click', function () { goTo(Math.round(p) + b[1]); });
    });

    var hint = mk('div', 'position:absolute;left:0;right:0;bottom:68px;text-align:center;font:400 12px ' + FS +
      ';letter-spacing:.08em;color:#8a8170;pointer-events:none;transition:opacity .4s;padding:0 60px', el);
    hint.textContent = 'ลากหรือปัดเพื่อเดินในหอภาพ · ‹ › เปลี่ยนภาพ · แตะรางด้านล่างเพื่อข้าม';

    var focusIdx = -1;
    function onFocus(i) {
      var era = i > KING9 ? 1 : 0;
      readK.textContent = era ? 'PRIME MINISTERS' : 'CHAKRI DYNASTY';
      readN.textContent = era ? 'นายกรัฐมนตรีแห่งราชอาณาจักรไทย' : 'พระมหากษัตริย์แห่งราชวงศ์จักรี';
      marker.style.left = ((i + 0.5) / 22 * 100) + '%';
    }

    // ── render and motion: frames only while something moves ────────────────
    function render() {
      if (!g && !layout()) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, vw, vh);
      room();
      var vis = [];
      items.forEach(function (it) {
        if (Math.abs(it.slot - p) > 4) return;
        var v = look(it);
        if (v) vis.push({ it: it, v: v });
      });
      vis.sort(function (a, b) { return b.v.d - a.v.d; });
      vis.forEach(function (o) { glow(o.it, o.v); });
      vis.forEach(function (o) { portrait(o.it, o.v); });
      captions(vis);
      var f = Math.round(clamp(p, 0, PM33));
      if (f !== focusIdx) { focusIdx = f; onFocus(f); }
    }

    function step() {                                // advance one frame; true while still moving
      if (jump) {
        var q = Math.min(1, (performance.now() - jump.t0) / jump.dur);
        p = jump.from + (jump.to - jump.from) * (1 - Math.pow(1 - q, 3));
        if (q >= 1) { p = jump.to; jump = null; }
        return !!jump;
      }
      if (drag) return true;
      if (Math.abs(vel) > 0.0006) {
        p = clamp(p + vel, MINP, MAXP);
        vel *= 0.92;
        return true;
      }
      vel = 0;
      var target = clamp(Math.round(p), 0, PM33);   // settle on the nearest portrait
      if (Math.abs(target - p) > 0.002) { p += (target - p) * 0.1; return true; }
      p = target;
      return false;
    }
    function frame() {
      raf = 0;
      if (dead) return;
      var moving = step();
      render();
      if (moving || drag) kick();
    }
    function kick() {
      if (raf || dead) return;
      var fired = false;
      function go() { if (!fired) { fired = true; frame(); } }
      raf = requestAnimationFrame(go) || 1;
      setTimeout(go, 120);   // a background tab pauses animation frames; never leave a kick hanging
    }
    function requestRender() { kick(); }

    function goTo(to) {
      var t = clamp(to, 0, PM33);
      vel = 0;
      jump = { from: p, to: t, t0: performance.now(), dur: 420 + Math.min(900, Math.abs(t - p) * 90) };
      kick();
    }

    // ── input ────────────────────────────────────────────────────────────────
    track.addEventListener('pointerdown', function (e) {
      e.stopPropagation();
      var r = track.getBoundingClientRect();
      goTo(Math.round((e.clientX - r.left) / r.width * 22 - 0.5));
    });
    el.addEventListener('pointerdown', function (e) {
      if (e.target.tagName === 'BUTTON' || track.contains(e.target)) return;
      jump = null;
      drag = { x: e.clientX, y: e.clientY, p: p, touch: e.pointerType === 'touch' };
      engaged = true;
      hint.style.opacity = '0';
      el.style.cursor = 'grabbing';
      if (el.setPointerCapture) { try { el.setPointerCapture(e.pointerId); } catch (err) {} }
      kick();
    });
    el.addEventListener('pointermove', function (e) {
      if (!drag) return;
      // phones: sideways swipes walk (vertical ones still scroll the page); mouse: either direction
      var d = drag.touch ? (e.clientX - drag.x) : (e.clientY - drag.y) + (e.clientX - drag.x);
      var np = clamp(drag.p - d * 0.0055, MINP, MAXP);
      vel = (np - p) * 0.5;
      p = np;
    });
    function up() {
      if (!drag) return;
      drag = null;
      el.style.cursor = 'grab';
      kick();
    }
    el.addEventListener('pointerup', up);
    el.addEventListener('pointercancel', up);
    el.addEventListener('wheel', function (e) {
      if (!engaged && document.activeElement !== el) return;
      e.preventDefault();
      jump = null;
      vel += e.deltaY * 0.00018;
      kick();
    }, { passive: false });
    el.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { goTo(Math.round(p) + 1); e.preventDefault(); }
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { goTo(Math.round(p) - 1); e.preventDefault(); }
    });
    el.addEventListener('focus', function () { engaged = true; hint.style.opacity = '0'; });

    // ── size: tabs start hidden, so wait for a real size before painting ─────
    var waiting = 0;
    function resized() {
      if (dead) return;
      if (layout()) { kick(); return; }
      // still hidden: check again shortly, in case no resize notification arrives when the tab opens
      if (!waiting) waiting = setTimeout(function () { waiting = 0; if (!g) resized(); }, 500);
    }
    var ro = window.ResizeObserver ? new ResizeObserver(resized) : null;
    if (ro) ro.observe(el); else window.addEventListener('resize', resized);
    resized();

    return {
      goTo: goTo,
      destroy: function () {
        dead = true;
        if (raf) cancelAnimationFrame(raf);
        if (waiting) clearTimeout(waiting);
        if (ro) ro.disconnect(); else window.removeEventListener('resize', resized);
        images.forEach(function (im) { im.onload = null; });
      }
    };
  }

  customElements.define('portrait-hall', Hall);
})();
