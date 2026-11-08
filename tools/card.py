#!/usr/bin/env python3
"""Render the closing card: dawn over the mountains, a car on the road out of the city, `exit 0`.

Writes assets/card-dark.svg and assets/card-light.svg. Standard library only.

    python3 tools/card.py assets/
"""
import math
import os
import random
import sys

W, H = 1200, 300
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
THEMES = {
    "dark": dict(page="#0d1117", sky=("#04060b", "#141a3a", "#4a2360", "#b0466a", "#f0a04b"),
                 sun="#ffd38a", glow="#ff9f5a", far="#5a2f5e", mid="#2f1f42", near="#141327", ground="#0b0c18",
                 road="#07080f", line="#d4a72c", tail="#ff3b3b", star="#c9d1d9", text="#e6edf3", dim="#8b949e",
                 haze="#f0a04b"),
    "light": dict(page="#ffffff", sky=("#cfd9ea", "#e3d9ea", "#f3d3d0", "#f8c8a8", "#fbd38d"),
                  sun="#fff3d6", glow="#ffb36b", far="#c9a9c4", mid="#9c7fa1", near="#6b5a7c", ground="#4d4260",
                  road="#2e2838", line="#bf8700", tail="#e5322f", star="#ffffff", text="#1f2328", dim="#59636e",
                  haze="#fbd38d"),
}
SUN = (835, 172)
VANISH = (842, 198)
HORIZON = 196


def ridge(rng, y0, amp, rough, seed_shift=0.0, step=8):
    """Mountain silhouette as an SVG path (filled down to the bottom)."""
    pts = []
    phase = [rng.uniform(0, 6.28) for _ in range(4)]
    for x in range(-10, W + 11, step):
        t = x / W
        y = (y0
             - amp * (0.55 * math.sin(t * 5.1 + phase[0]) + 0.3 * math.sin(t * 11.7 + phase[1])
                      + 0.15 * math.sin(t * 23.0 + phase[2]))
             - rough * rng.uniform(-1, 1))
        # open a pass where the road leaves the valley
        y += amp * 0.9 * math.exp(-((x - VANISH[0]) / 70) ** 2)
        pts.append((x, y))
    d = "M-10 %d " % H + " ".join(f"L{x} {y:.1f}" for x, y in pts) + f" L{W + 10} {H} Z"
    return d


K = (322 - HORIZON) * 3.0     # perspective: screen y = HORIZON + K / z
FX = K / 1.5                   # camera 1.5 units above the road
HALF = 2.3                     # half road width, world units


def centre_x(z):
    """World x of the road centre at distance z: an S-bend near us, straightening into the pass."""
    return 2.6 * math.sin(z / 7.5 + 2.2) - 2.6 + 0.9 * math.sin(z / 23.0)


def project(xw, z):
    return VANISH[0] + xw * FX / z, HORIZON + K / z


def zs(n=140, z0=2.6, z1=900.0):
    return [z0 * (z1 / z0) ** (i / n) for i in range(n + 1)]


def road_polygon():
    left = [project(centre_x(z) - HALF, z) for z in zs()]
    right = [project(centre_x(z) + HALF, z) for z in zs()]
    poly = left + right[::-1]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly) + " Z"


def path_d(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def card(theme):
    c = THEMES[theme]
    rng = random.Random(2019)
    # dashed centre line, one dash every 2.5 world units
    dashes = []
    z = 3.0
    while z < 160:
        (x1, y1), (x2, y2) = project(centre_x(z), z), project(centre_x(z + 1.1), z + 1.1)
        dashes.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke-width="{max(0.35, 9.0 / z):.2f}"/>')
        z += 2.5
    # the car keeps to the right lane and drives away at constant speed (in the world, not on screen)
    zc0, zc1 = 4.2, 260.0
    lane_z = [zc0 + (zc1 - zc0) * (i / 400) ** 1.0 for i in range(401)]
    lane = [project(centre_x(z) + HALF * 0.45, z) for z in lane_z]
    car_path = path_d(lane)
    seg = [math.dist(lane[i], lane[i + 1]) for i in range(len(lane) - 1)]
    total = sum(seg); acc = [0.0]
    for d in seg:
        acc.append(acc[-1] + d)
    frames = []
    for k in range(25):
        zt = zc0 * (zc1 / zc0) ** (k / 24)          # ease: equal ratios of distance per step
        j = min(range(len(lane_z)), key=lambda i: abs(lane_z[i] - zt))
        frames.append(f"{k / 24 * 100:.1f}%{{offset-distance:{acc[j] / total * 100:.2f}%;"
                      f"transform:scale({2.6 * zc0 / zt:.3f})}}")
    # telephone poles along the left shoulder, receding into the pass
    poles = []
    for k in range(14):
        z = 7.0 * 1.33 ** k
        xw = centre_x(z) - HALF - 1.4
        bx, by = project(xw, z)
        top = HORIZON + (K / z) - 2.6 * FX / z
        wdt = max(0.5, 4.0 / z)
        poles.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx:.1f}" y2="{top:.1f}" stroke-width="{wdt:.2f}"/>'
                     f'<line x1="{bx - 0.3 * FX / z:.1f}" y1="{top + 0.15 * FX / z:.1f}" x2="{bx + 0.3 * FX / z:.1f}" '
                     f'y2="{top + 0.15 * FX / z:.1f}" stroke-width="{wdt * 0.7:.2f}"/>')
    stars = []
    if theme == "dark":
        for _ in range(70):
            x, y = rng.uniform(0, W), rng.uniform(0, 120) ** 1.0
            y = y * (y / 120) ** 0.4
            op = rng.uniform(0.15, 0.7) * (1 - y / 140)
            cls = ' class="tw"' if rng.random() < 0.25 else ""
            stars.append(f'<circle{cls} cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(0.5, 1.3):.2f}" '
                         f'fill="{c["star"]}" opacity="{op:.2f}" style="animation-delay:{rng.uniform(0, 6):.1f}s"/>')
    far = ridge(rng, 168, 44, 1.2)
    mid = ridge(rng, 196, 26, 1.5)
    near_l = f"M-10 {H} L-10 190 Q120 196 230 236 T420 {H} Z"
    near_r = f"M{W + 10} {H} L{W + 10} 186 Q1080 190 990 232 T850 {H} Z"
    sky = c["sky"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Dawn over the mountains; a car drives out of the city towards the sun. exit 0">',
         "<defs>",
         '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">' +
         "".join(f'<stop offset="{off}" stop-color="{col}"/>' for off, col in zip((0, 0.3, 0.55, 0.72, 0.82), sky)) +
         "</linearGradient>",
         f'<radialGradient id="glow" cx="{SUN[0] / W:.3f}" cy="{SUN[1] / H:.3f}" r="0.55" gradientTransform="translate({SUN[0] / W:.3f} {SUN[1] / H:.3f}) scale(1 0.4) translate(-{SUN[0] / W:.3f} -{SUN[1] / H:.3f})">'
         f'<stop offset="0" stop-color="{c["glow"]}" stop-opacity="0.75"/><stop offset="1" stop-color="{c["glow"]}" stop-opacity="0"/></radialGradient>',
         f'<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["haze"]}" stop-opacity="0"/>'
         f'<stop offset="1" stop-color="{c["haze"]}" stop-opacity="0.28"/></linearGradient>',
         f'<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["page"]}" stop-opacity="0"/>'
         f'<stop offset="1" stop-color="{c["page"]}" stop-opacity="0.9"/></linearGradient>',
         f'<linearGradient id="shore" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["haze"]}" stop-opacity="0.35"/>'
         f'<stop offset="1" stop-color="{c["haze"]}" stop-opacity="0"/></linearGradient>',
         '<filter id="bloom" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6" result="b"/>'
         '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
         '<filter id="tl" x="-300%" y="-300%" width="700%" height="700%"><feGaussianBlur stdDeviation="1.6" result="b"/>'
         '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
         '<clipPath id="type"><rect class="typer" x="56" y="250" height="34" width="0"/></clipPath>',
         "</defs>",
         "<style>",
         ".sun{animation:rise 24s ease-out forwards}@keyframes rise{from{transform:translateY(14px)}to{transform:translateY(0)}}",
         ".tw{animation:tw 5s ease-in-out infinite}@keyframes tw{50%{opacity:0.05}}",
         ".stars{animation:fade 30s linear forwards}@keyframes fade{to{opacity:0.25}}",
         f".car{{offset-path:path('{car_path}');offset-rotate:0deg;animation:drive 18s linear 1s infinite}}",
         "@keyframes drive{" + "".join(frames) + "}",
         ".fadecar{animation:fadecar 18s linear 1s infinite}@keyframes fadecar{0%{opacity:0}3%{opacity:1}90%{opacity:1}100%{opacity:0}}",
         ".lamp{animation:lamp 2.4s ease-in-out infinite alternate}@keyframes lamp{to{opacity:0.75}}",
         ".typer{animation:type 0.9s steps(8) 2s forwards}@keyframes type{to{width:150px}}",
         ".cursor{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}",
         "@media (prefers-reduced-motion: reduce){*{animation:none!important}.typer{width:150px}.car{offset-distance:12%}}",
         "</style>",
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<g class="stars">{"".join(stars)}</g>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
         f'<g class="sun"><circle cx="{SUN[0]}" cy="{SUN[1]}" r="44" fill="{c["sun"]}" filter="url(#bloom)"/>'
         + "".join(f'<rect x="{SUN[0] - 50}" y="{SUN[1] + 6 + k * 7}" width="100" height="{1.2 + k * 0.8:.1f}" fill="{sky[3]}" opacity="0.55"/>'
                   for k in range(4)) + "</g>",
         f'<path d="{far}" fill="{c["far"]}"/>',
         f'<rect y="110" width="{W}" height="90" fill="url(#haze)"/>',
         f'<path d="{mid}" fill="{c["mid"]}"/>',
         f'<rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="{c["ground"]}"/>',
         f'<rect y="{HORIZON}" width="{W}" height="26" fill="url(#shore)"/>',
         f'<path d="{road_polygon()}" fill="{c["road"]}"/>',
         f'<g stroke="{c["line"]}" stroke-linecap="round" opacity="0.8">{"".join(dashes)}</g>',
         f'<g stroke="{c["near"]}" stroke-linecap="round">{"".join(poles)}</g>',
         # the car: a dark body and two red tail lights, seen from behind
         f'<g class="fadecar"><g class="car"><g>'
         f'<rect x="-11" y="-7" width="22" height="9" rx="2.5" fill="{c["road"]}" stroke="{c["near"]}" stroke-width="0.8"/>'
         f'<rect x="-7.5" y="-12" width="15" height="6" rx="2" fill="{c["road"]}" stroke="{c["near"]}" stroke-width="0.8"/>'
         f'<g class="lamp" filter="url(#tl)"><rect x="-10" y="-4.5" width="4.5" height="2.2" rx="1" fill="{c["tail"]}"/>'
         f'<rect x="5.5" y="-4.5" width="4.5" height="2.2" rx="1" fill="{c["tail"]}"/></g>'
         f"</g></g></g>",
         f'<path d="{near_l}" fill="{c["near"]}"/>',
         f'<path d="{near_r}" fill="{c["near"]}"/>',
         f'<rect y="{H - 70}" width="{W}" height="70" fill="url(#fog)"/>',
         f'<text x="60" y="276" font-family="{FONT}" font-size="22" fill="{c["text"]}" clip-path="url(#type)">'
         f'<tspan fill="{c["dim"]}">$ </tspan>exit 0</text>',
         f'<rect class="cursor" x="196" y="259" width="11" height="21" fill="{c["dim"]}" opacity="0.8"/>',
         "</svg>"]
    return "\n".join(o) + "\n"


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        with open(os.path.join(out, f"card-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(card(theme))


if __name__ == "__main__":
    main()
