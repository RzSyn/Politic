/* The glory around King Rama IX's portrait, shared by the homepage intro and
   the หอภาพเหมือน tab. Both call it on their own canvas:

     HallAura.back(ctx, s)   before the portrait: spotlight cone, turning sunburst, breathing halo
     HallAura.front(ctx, s)  after the portrait: rising gold sparks, and a flash ring on arrival

   s = { cx, cy: screen centre of the frame; fw, fh: frame size in world units;
         k: projection scale; ceilY: screen y of the ceiling above it;
         amount: 0-1; now: ms clock; shock: ms since arrival, or -1 }
   Textures are painted once, so a frame costs a few dozen image copies. */
(function () {
  var rays = null, spark = null, seeds = [];
  for (var i = 0; i < 90; i++) {
    seeds.push({ x: Math.random(), size: Math.random(), speed: 0.00006 + Math.random() * 0.00012,
      phase: Math.random(), twinkle: 0.4 + Math.random() * 0.9 });
  }

  function textures() {
    if (rays) return;
    rays = document.createElement('canvas');
    rays.width = rays.height = 512;
    var x = rays.getContext('2d'), c = 256, n = 32;
    for (var j = 0; j < n; j++) {
      var a = j / n * Math.PI * 2, wide = j % 2 === 0, half = wide ? 0.07 : 0.025;
      var g = x.createRadialGradient(c, c, 0, c, c, c);
      g.addColorStop(0, 'rgba(255,240,190,' + (wide ? 0.95 : 0.6) + ')');
      g.addColorStop(0.3, 'rgba(255,214,120,' + (wide ? 0.4 : 0.22) + ')');
      g.addColorStop(1, 'rgba(255,196,90,0)');
      x.fillStyle = g;
      x.beginPath(); x.moveTo(c, c); x.arc(c, c, c, a - half, a + half); x.closePath(); x.fill();
    }
    spark = document.createElement('canvas');
    spark.width = spark.height = 64;
    var s = spark.getContext('2d');
    var core = s.createRadialGradient(32, 32, 0, 32, 32, 32);
    core.addColorStop(0, 'rgba(255,255,245,1)');
    core.addColorStop(0.14, 'rgba(255,238,180,.9)');
    core.addColorStop(0.45, 'rgba(255,204,100,.22)');
    core.addColorStop(1, 'rgba(255,204,100,0)');
    s.fillStyle = core; s.fillRect(0, 0, 64, 64);
    s.globalCompositeOperation = 'lighter';
    [[0, 32, 64, 32, 0, 31, 64, 2], [32, 0, 32, 64, 31, 0, 2, 64]].forEach(function (f) {   // star flare
      var lg = s.createLinearGradient(f[0], f[1], f[2], f[3]);
      lg.addColorStop(0, 'rgba(255,244,210,0)');
      lg.addColorStop(0.5, 'rgba(255,244,210,.95)');
      lg.addColorStop(1, 'rgba(255,244,210,0)');
      s.fillStyle = lg; s.fillRect(f[4], f[5], f[6], f[7]);
    });
  }

  function back(ctx, s) {
    if (!(s.amount > 0.01)) return;
    textures();
    var a = s.amount, t = s.now, k = s.k;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';

    var topW = s.fw * k * 0.4, botW = s.fw * k * 2.1, by = s.cy + s.fh * k * 0.8;   // spotlight from the ceiling
    var cone = ctx.createLinearGradient(0, s.ceilY, 0, by);
    cone.addColorStop(0, 'rgba(255,240,190,' + (0.38 * a).toFixed(3) + ')');
    cone.addColorStop(1, 'rgba(255,220,140,0)');
    ctx.fillStyle = cone;
    ctx.beginPath();
    ctx.moveTo(s.cx - topW / 2, s.ceilY); ctx.lineTo(s.cx + topW / 2, s.ceilY);
    ctx.lineTo(s.cx + botW / 2, by); ctx.lineTo(s.cx - botW / 2, by);
    ctx.closePath(); ctx.fill();

    var R = s.fh * k * 3.6;                                                         // sunburst, two layers turning apart
    ctx.translate(s.cx, s.cy);
    ctx.rotate(t * 0.00009);
    ctx.globalAlpha = 0.55 * a;
    ctx.drawImage(rays, -R / 2, -R / 2, R, R);
    ctx.rotate(-t * 0.00024);
    ctx.globalAlpha = 0.3 * a;
    ctx.drawImage(rays, -R * 0.35, -R * 0.35, R * 0.7, R * 0.7);
    ctx.restore();

    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    var hr = s.fh * k * 1.3, pulse = 0.82 + 0.18 * Math.sin(t / 650);                // breathing halo
    var halo = ctx.createRadialGradient(s.cx, s.cy, 0, s.cx, s.cy, hr);
    halo.addColorStop(0, 'rgba(255,232,160,' + (0.6 * a * pulse).toFixed(3) + ')');
    halo.addColorStop(0.5, 'rgba(255,204,100,' + (0.24 * a * pulse).toFixed(3) + ')');
    halo.addColorStop(1, 'rgba(255,190,80,0)');
    ctx.fillStyle = halo;
    ctx.fillRect(s.cx - hr, s.cy - hr, hr * 2, hr * 2);
    ctx.restore();
  }

  function front(ctx, s) {
    if (!(s.amount > 0.01)) return;
    textures();
    var a = s.amount, t = s.now, k = s.k;
    var W = s.fw * k * 3, H = s.fh * k * 2.4, base = s.cy + s.fh * k;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    seeds.forEach(function (sd) {                                                  // gold sparks rising and twinkling
      var life = (t * sd.speed + sd.phase) % 1;
      var x = s.cx + (sd.x - 0.5) * W + Math.sin(t * 0.0011 + sd.x * 20) * s.fw * k * 0.06;
      var y = base - life * H;
      var tw = Math.pow(Math.sin(t * 0.004 * sd.twinkle + sd.size * 30), 2);
      var al = a * Math.sin(life * Math.PI) * (0.3 + 0.7 * tw);
      if (al < 0.02) return;
      var size = s.fw * k * (0.035 + sd.size * 0.08) * (0.7 + 0.5 * tw);
      ctx.globalAlpha = al;
      ctx.drawImage(spark, x - size / 2, y - size / 2, size, size);
    });
    if (s.shock >= 0 && s.shock < 1800) {                                           // arrival: flash and a ring of light
      var q = s.shock / 1800, fade = (1 - q) * (1 - q);
      var fr = s.fh * k * 1.8;
      var flash = ctx.createRadialGradient(s.cx, s.cy, 0, s.cx, s.cy, fr);
      flash.addColorStop(0, 'rgba(255,248,220,' + (0.7 * fade).toFixed(3) + ')');
      flash.addColorStop(1, 'rgba(255,220,140,0)');
      ctx.globalAlpha = 1;
      ctx.fillStyle = flash;
      ctx.fillRect(s.cx - fr, s.cy - fr, fr * 2, fr * 2);
      [0, 0.18].forEach(function (lag) {
        var qq = Math.max(0, q - lag) / (1 - lag);
        if (qq <= 0) return;
        ctx.globalAlpha = (1 - qq) * 0.9;
        ctx.strokeStyle = '#ffe6a0';
        ctx.lineWidth = Math.max(1, s.fw * k * 0.05 * (1 - qq));
        ctx.beginPath();
        ctx.arc(s.cx, s.cy, s.fw * k * (0.6 + qq * 3.4), 0, Math.PI * 2);
        ctx.stroke();
      });
    }
    ctx.restore();
  }

  window.HallAura = { back: back, front: front };
})();
