# -*- coding: utf-8 -*-
"""Generate jagged crack polylines for the 404 page (deterministic)."""
import math, random

random.seed(2375)
W = H = 1000
paths = []   # (depth, d)


def walk(x, y, ang, steps, seg, jitter, depth, spawn):
    pts = [(x, y)]
    for i in range(steps):
        ang += random.uniform(-jitter, jitter)
        L = seg * random.uniform(0.55, 1.35)
        x += math.cos(ang) * L
        y += math.sin(ang) * L
        pts.append((x, y))
        if depth < 3 and random.random() < spawn and i > 1:
            side = random.choice((-1, 1))
            walk(x, y, ang + side * random.uniform(0.5, 1.15),
                 max(2, steps // 2 - depth), seg * 0.72, jitter * 1.25,
                 depth + 1, spawn * 0.55)
        if not (-60 < x < W + 60 and -60 < y < H + 60):
            break
    d = 'M' + ' L'.join('%.0f %.0f' % p for p in pts)
    paths.append((depth, d))


# the main fault runs the whole height, a little off centre
walk(516, -30, math.radians(88), 26, 46, 0.30, 0, 0.34)
# two long secondary faults
walk(-30, 250, math.radians(14), 18, 52, 0.34, 1, 0.3)
walk(1030, 700, math.radians(190), 17, 50, 0.34, 1, 0.3)
# corner shatters
walk(60, 980, math.radians(-64), 10, 40, 0.42, 2, 0.28)
walk(940, 40, math.radians(116), 10, 40, 0.42, 2, 0.28)
walk(150, 60, math.radians(58), 9, 38, 0.45, 2, 0.26)

main = [d for dep, d in paths if dep == 0]
mid = [d for dep, d in paths if dep == 1]
hair = [d for dep, d in paths if dep >= 2]

out = []
for d in main:
    out.append('  <path class="deep" d="%s"/>' % d)
    out.append('  <path d="%s"/>' % d)
for d in mid:
    out.append('  <path d="%s"/>' % d)
for d in hair:
    out.append('  <path class="hair" d="%s"/>' % d)

print('\n'.join(out))
print('\n<!-- %d paths: main %d, mid %d, hair %d -->'
      % (len(paths), len(main), len(mid), len(hair)))
