#!/usr/bin/env python3
"""The airship over the night city: the 3D model in the profile README.

Writes the ASCII STL to stdout. Needs numpy and scipy.

    python3 tools/model/airship.py > airship.stl
"""
import math
import random
import sys
import numpy as np
from scipy.spatial import ConvexHull
from geo import Mesh, box, cbox, cylinder, tube, quad, tri, to_stl

def hull(points):
    P = np.array(points, float)
    h = ConvexHull(P)
    c = P.mean(0)
    m = Mesh()
    for s in h.simplices:
        t = P[s]
        n = np.cross(t[1] - t[0], t[2] - t[0])
        if n @ (t[0] - c) < 0:
            t = t[[0, 2, 1]]
        m.add([t.copy()])
    return m


def tower(x, y, w, d, h, rng, detail=True):
    """Setback skyscraper with roof gear."""
    m = Mesh()
    tiers = 1 if h < 14 else (2 if h < 30 else 3)
    z = 0; cw, cd = w, d
    for k in range(tiers):
        th = h * ([1.0], [0.62, 0.38], [0.5, 0.3, 0.2])[tiers - 1][k]
        m.add(cbox(x, y, z, cw, cd, th))
        z += th; cw *= 0.72; cd *= 0.72
    if detail:
        if h > 26:
            m.add(cylinder(x, y, z, z + h * 0.28, min(cw, cd) * 0.12, 5, r1=0))
        else:
            m.add(cbox(x + rng.uniform(-.2, .2) * cw, y + rng.uniform(-.2, .2) * cd, z, cw * .35, cd * .3, 1.2))
    return m


def tower(x, y, w, d, h, rng, detail=True):
    """Setback skyscraper with roof gear."""
    m = Mesh()
    tiers = 1 if h < 14 else (2 if h < 30 else 3)
    z = 0; cw, cd = w, d
    for k in range(tiers):
        th = h * ([1.0], [0.62, 0.38], [0.5, 0.3, 0.2])[tiers - 1][k]
        m.add(cbox(x, y, z, cw, cd, th))
        z += th; cw *= 0.72; cd *= 0.72
    if detail:
        if h > 26:
            m.add(cylinder(x, y, z, z + h * 0.28, min(cw, cd) * 0.12, 5, r1=0))
        else:
            m.add(cbox(x + rng.uniform(-.2, .2) * cw, y + rng.uniform(-.2, .2) * cd, z, cw * .35, cd * .3, 1.2))
    return m


def airship():
    """Advertising airship drifting over the night city, searchlights sweeping the streets."""
    rng = random.Random(1982)
    m = Mesh()
    # --- city: dense core under the ship, lower edges
    m.add(box(-66, -42, -1.5, 66, 42, 0))
    for i in range(-6, 7):
        for j in range(-3, 4):
            if rng.random() < 0.47:
                continue
            x = i * 10.2 + rng.uniform(-1.2, 1.2); y = j * 10.5 + rng.uniform(-1.2, 1.2)
            core = math.exp(-((x / 55) ** 2 + (y / 38) ** 2))
            h = rng.uniform(13, 22) + 18 * core * rng.uniform(0.4, 1.0)
            m.add(tower(x, y, rng.uniform(5, 7.5), rng.uniform(5, 8), h, rng, detail=h > 30))
    zc = 66
    L, R = 52, 12.5
    # --- hull: ogive profile (blunt nose, long taper), faceted like panelled skin
    rings = []
    nu = 26
    prof = []
    for k in range(21):
        t = k / 20                      # 0 = tail, 1 = nose
        x = -L + 2 * L * t
        r = R * (math.sin(math.pi * t) ** 0.62) * (0.75 + 0.25 * t)
        prof.append((x, max(r, 0.25)))
    for x, r in prof:
        rings.append([np.array([x, r * math.cos(2 * math.pi * u / nu), zc + r * math.sin(2 * math.pi * u / nu)])
                      for u in range(nu)])
    # loft builds along +z; our rings run along +x, so orient caps by hand
    hullm = Mesh()
    for r0, r1 in zip(rings, rings[1:]):
        for u in range(nu):
            v = (u + 1) % nu
            hullm.add(quad(r0[u], r1[u], r1[v], r0[v]))
    for rr, flip in ((rings[0], True), (rings[-1], False)):
        c = np.mean(rr, axis=0)
        for u in range(nu):
            t = tri(c, rr[(u + 1) % nu], rr[u]) if flip else tri(c, rr[u], rr[(u + 1) % nu])
            hullm.add([t])
    m.add(hullm)
    # longitudinal strakes: rigid frame lines along the top and flanks
    for ang in (90, 35, 145):
        a = math.radians(ang)
        pts = [(x, (r + 0.25) * math.cos(a), zc + (r + 0.25) * math.sin(a)) for x, r in prof[2:-2]]
        m.add(tube(pts, 0.35, 3))
    # --- tail: cruciform fins with rudders
    for ang in (45, 135, 225, 315):
        fin = hull([(-36, 0, 0), (-50, 0, 0), (-55, 0, 17), (-44, 0, 16),
                    (-36, 0.7, 0), (-50, 0.7, 0), (-55, 0.7, 17), (-44, 0.7, 16)])
        rud = hull([(-55.3, 0, 2), (-58, 0, 2), (-58.5, 0, 16), (-55.6, 0, 16),
                    (-55.3, 0.5, 2), (-58, 0.5, 2), (-58.5, 0.5, 16), (-55.6, 0.5, 16)])
        m.add(fin.add(rud).move(0, -0.35, 4).rot("x", ang).move(0, 0, zc))
    # --- flank screens, both sides: frame, panel, scan-line slats
    for side in (-1, 1):
        y0 = side * (R - 0.6)
        m.add(box(-26, min(y0, y0 + side * 1.4), zc - 7.5, 22, max(y0, y0 + side * 1.4), zc + 7.5))
        for k in range(11):
            z = zc - 6.6 + k * 1.25
            x0 = -25 + rng.uniform(0, 5); x1 = 21 - rng.uniform(0, 8)
            yy = y0 + side * 1.4
            m.add(box(x0, min(yy, yy + side * 0.5), z, x1, max(yy, yy + side * 0.5), z + 0.62))
    # --- gondola with window band
    gz = zc - R - 1.5
    m.add(hull([(-13, -3.4, gz + 2), (13, -3.4, gz + 2), (16, 0, gz), (-15, 0, gz),
                (-13, 3.4, gz + 2), (13, 3.4, gz + 2), (-11, 0, gz - 4.5), (11, 0, gz - 4.5)]))
    for k in range(5):
        x = -10 + k * 4.4
        for side in (-1, 1):
            m.add(box(x, side * 3.35 - 0.2, gz - 0.2, x + 3.2, side * 3.35 + 0.2, gz + 1.2))
    # --- engine nacelles with three-blade props
    for sx, sy in ((14, 1), (14, -1), (-18, 1), (-18, -1)):
        y = sy * (R + 3.5); z = zc - 5
        m.add(cylinder(0, 0, -4, 4, 1.8, 8, r1=1.2).rot("y", 90).move(sx, y, z))
        m.add(box(sx - 1, min(sy * (R - 1), y), z - 0.3, sx + 1, max(sy * (R - 1), y), z + 0.3))
        for b in range(3):
            blade = hull([(0, 0, 0), (0, 0.5, 0), (0.2, 0.25, 4.2), (-0.2, 0.25, 4.2)])
            m.add(blade.rot("x", b * 120).move(sx - 4.4, y, z))
    # --- searchlights: long cones of light reaching down into the streets
    for x, tx, ty in ((8, 18, -16), (-6, -22, 12), (-20, -4, -26)):
        top = np.array([x, 0.0, gz - 3])
        tip_c = np.array([tx, ty, 0.5])
        d = top - tip_c; d /= np.linalg.norm(d)
        u = np.cross(d, [0, 0, 1.0]); u /= np.linalg.norm(u); w = np.cross(d, u)
        base = [tip_c + 6 * (math.cos(2 * math.pi * k / 14) * u + math.sin(2 * math.pi * k / 14) * w) for k in range(14)]
        for k in range(14):
            m.add([tri(base[k], base[(k + 1) % 14], top)])
        m.add(cylinder(x, 0, gz - 3.4, gz - 2.2, 1.0, 8))
    return m


if __name__ == "__main__":
    text, facets = to_stl(airship(), "airship")
    sys.stdout.write(text)
    print(f"{facets} facets, {len(text) / 1024:.1f} KB", file=sys.stderr)
