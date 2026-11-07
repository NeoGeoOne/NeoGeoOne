"""Tiny mesh toolkit for ASCII STL models. Triangles are (3,3) numpy arrays, z is up."""
import math
import numpy as np


class Mesh:
    def __init__(self, tris=None):
        self.tris = [] if tris is None else list(tris)

    def add(self, other):
        self.tris.extend(other.tris if isinstance(other, Mesh) else other)
        return self

    def __len__(self):
        return len(self.tris)

    def map(self, fn):
        return Mesh([np.array([fn(v) for v in t]) for t in self.tris])

    def move(self, dx=0, dy=0, dz=0):
        d = np.array([dx, dy, dz], float)
        return Mesh([t + d for t in self.tris])

    def scale(self, sx, sy=None, sz=None):
        s = np.array([sx, sx if sy is None else sy, sx if sz is None else sz], float)
        m = Mesh([t * s for t in self.tris])
        if np.prod(s) < 0:  # mirrored: flip winding
            m.tris = [t[[0, 2, 1]] for t in m.tris]
        return m

    def rot(self, axis, deg, about=(0, 0, 0)):
        a = math.radians(deg); c, s = math.cos(a), math.sin(a)
        R = {"x": [[1, 0, 0], [0, c, -s], [0, s, c]],
             "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
             "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]
        R = np.array(R); o = np.array(about, float)
        return Mesh([(t - o) @ R.T + o for t in self.tris])

    def bounds(self):
        a = np.concatenate(self.tris)
        return a.min(0), a.max(0)


def tri(a, b, c):
    return np.array([a, b, c], float)


def quad(a, b, c, d):
    """Counter-clockwise quad seen from outside -> two triangles."""
    return [tri(a, b, c), tri(a, c, d)]


def ring(cx, cy, z, rx, ry, n, phase=0.0):
    return [np.array([cx + rx * math.cos(phase + 2 * math.pi * i / n),
                      cy + ry * math.sin(phase + 2 * math.pi * i / n), z]) for i in range(n)]


def loft(rings, cap_bottom=True, cap_top=True):
    """Connect closed rings (each list of points, same count, CCW seen from +z) into a tube."""
    m = Mesh()
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            m.add(quad(r0[i], r0[j], r1[j], r1[i]))
    if cap_bottom:
        c = np.mean(rings[0], axis=0)
        for i in range(n):
            m.add([tri(c, rings[0][(i + 1) % n], rings[0][i])])
    if cap_top:
        c = np.mean(rings[-1], axis=0)
        for i in range(n):
            m.add([tri(c, rings[-1][i], rings[-1][(i + 1) % n])])
    return m


def box(x0, y0, z0, x1, y1, z1):
    r0 = [np.array(p, float) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))]
    r1 = [p + np.array([0, 0, z1 - z0]) for p in r0]
    m = Mesh()
    for i in range(4):
        j = (i + 1) % 4
        m.add(quad(r0[i], r0[j], r1[j], r1[i]))
    m.add(quad(r0[0], r0[3], r0[2], r0[1]))
    m.add(quad(r1[0], r1[1], r1[2], r1[3]))
    return m


def cbox(cx, cy, z0, w, d, h):
    return box(cx - w / 2, cy - d / 2, z0, cx + w / 2, cy + d / 2, z0 + h)


def frustum(cx, cy, z0, z1, w0, d0, w1, d1):
    r0 = ring_rect(cx, cy, z0, w0, d0)
    r1 = ring_rect(cx, cy, z1, w1, d1)
    return loft([r0, r1])


def ring_rect(cx, cy, z, w, d):
    return [np.array(p, float) for p in ((cx - w / 2, cy - d / 2, z), (cx + w / 2, cy - d / 2, z),
                                          (cx + w / 2, cy + d / 2, z), (cx - w / 2, cy + d / 2, z))]


def cylinder(cx, cy, z0, z1, r, n=12, r1=None, phase=0.0):
    r1 = r if r1 is None else r1
    if r1 == 0:
        base = ring(cx, cy, z0, r, r, n, phase)
        tip = np.array([cx, cy, z1], float)
        m = Mesh()
        for i in range(n):
            m.add([tri(base[i], base[(i + 1) % n], tip)])
        c = np.array([cx, cy, z0], float)
        for i in range(n):
            m.add([tri(c, base[(i + 1) % n], base[i])])
        return m
    return loft([ring(cx, cy, z0, r, r, n, phase), ring(cx, cy, z1, r1, r1, n, phase)])


def ellipsoid(cx, cy, cz, rx, ry, rz, nu=24, nv=12, v0=0.0, v1=math.pi, cap=True):
    """Lat-long ellipsoid; v from 0 (top) to pi (bottom). Partial ranges give domes."""
    rings = []
    for k in range(nv + 1):
        v = v1 - (v1 - v0) * k / nv  # bottom to top
        z = cz + rz * math.cos(v); s = math.sin(v)
        rings.append(ring(cx, cy, z, rx * max(s, 1e-6), ry * max(s, 1e-6), nu))
    return loft(rings, cap_bottom=cap and v1 < math.pi - 1e-9, cap_top=cap and v0 > 1e-9)


def tube(points, r, n=6):
    """Sweep an n-gon along a polyline (list of 3D points)."""
    pts = [np.array(p, float) for p in points]
    rings = []
    up = np.array([0, 0, 1.0])
    for i, p in enumerate(pts):
        t = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        t /= np.linalg.norm(t)
        a = up if abs(t @ up) < 0.9 else np.array([1.0, 0, 0])
        u = np.cross(t, a); u /= np.linalg.norm(u); w = np.cross(t, u)
        rings.append([p + r * (math.cos(2 * math.pi * k / n) * u + math.sin(2 * math.pi * k / n) * w) for k in range(n)])
    return loft(rings)


def prism(poly2d, z0, z1):
    """Extrude a convex or star-shaped (from its centroid) 2D polygon, CCW."""
    r0 = [np.array([x, y, z0]) for x, y in poly2d]
    r1 = [np.array([x, y, z1]) for x, y in poly2d]
    return loft([r0, r1])


def heightfield(x0, y0, x1, y1, nx, ny, fn):
    m = Mesh()
    xs = np.linspace(x0, x1, nx + 1); ys = np.linspace(y0, y1, ny + 1)
    P = [[np.array([x, y, fn(x, y)]) for x in xs] for y in ys]
    for j in range(ny):
        for i in range(nx):
            m.add(quad(P[j][i], P[j][i + 1], P[j + 1][i + 1], P[j + 1][i]))
    return m


def solid_poly(vertices, faces):
    """Polyhedron from vertex list and faces (index lists, CCW from outside, fan-triangulated)."""
    V = [np.array(v, float) for v in vertices]
    m = Mesh()
    for f in faces:
        for k in range(1, len(f) - 1):
            m.add([tri(V[f[0]], V[f[k]], V[f[k + 1]])])
    return m


def fmt(x, d=2):
    s = f"{x:.{d}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def to_stl(mesh, name="model"):
    out = [f"solid {name}"]
    n_ok = 0
    lo, hi = mesh.bounds()
    d = 1 if (hi - lo).max() > 60 else 2  # big scenes: 0.1 unit is finer than a pixel
    for t in mesh.tris:
        nrm = np.cross(t[1] - t[0], t[2] - t[0]); L = np.linalg.norm(nrm)
        if L < 1e-9:
            continue
        nrm /= L
        out.append("facet normal " + " ".join(fmt(c) for c in nrm))
        out.append("outer loop")
        for v in t:
            out.append("vertex " + " ".join(fmt(c, d) for c in v))
        out.append("endloop")
        out.append("endfacet")
        n_ok += 1
    out.append(f"endsolid {name}")
    return "\n".join(out) + "\n", n_ok
