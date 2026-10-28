#!/usr/bin/env python3
"""Render the self-updating profile images: a typing terminal and a contribution skyline.

Reads only public data of the GitHub user from the GitHub API (needs GITHUB_TOKEN; the Actions token is enough).
Writes terminal-{dark,light}.svg and skyline-{dark,light}.svg into the output folder. Standard library only.

    GITHUB_TOKEN=... python3 tools/render.py NeoGeoOne out/
"""
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

try:
    from zoneinfo import ZoneInfo
    LOCAL = ZoneInfo("Europe/Berlin")
except Exception:  # tzdata missing: fall back to UTC
    LOCAL = dt.timezone.utc

API = "https://api.github.com"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
THEMES = {
    "dark": dict(bg="#0d1117", bar="#161b22", frame="#30363d", text="#c9d1d9", dim="#8b949e", prompt="#39c5cf",
                 ok="#3fb950", amber="#d4a72c", sky0="#04060b", sky1="#0d1117", city="#151c2b", win="#d4a72c",
                 win2="#39c5cf", unlit="#1f2636"),
    "light": dict(bg="#ffffff", bar="#f6f8fa", frame="#d0d7de", text="#1f2328", dim="#59636e", prompt="#0a7a85",
                  ok="#1a7f37", amber="#9a6700", sky0="#dfe7f1", sky1="#f6f8fa", city="#c9d1db", win="#bf8700",
                  win2="#0a7a85", unlit="#b9c2cd"),
}


def api(path, token, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {token}", "User-Agent": "profile-render",
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(login, token):
    q = ("query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{"
         "weeks{contributionDays{date contributionCount}}}}}}")
    data = api("/graphql", token, {"query": q, "variables": {"l": login}})
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"])
             for w in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]]
    events = api(f"/users/{login}/events/public?per_page=1", token)
    last = None
    if events:
        t = dt.datetime.fromisoformat(events[0]["created_at"].replace("Z", "+00:00")).astimezone(LOCAL)
        last = f"{t:%Y-%m-%d} · {'night' if t.hour >= 20 or t.hour < 6 else 'day'}"
    return weeks, last


def terminal(theme, last):
    c = THEMES[theme]
    lines = [
        ("cmd", "systemctl status neogeoone"),
        ("ok", "● neogeoone.service - night shift"),
        ("out", "     Loaded: loaded (/etc/systemd/system/neogeoone.service; enabled)"),
        ("out", "     Active: active (running) since a long time ago"),
        ("cmd", "journalctl -u neogeoone --since dusk"),
        ("log", "02:14  question   what does it really cost?"),
        ("log", "02:51  measured   not guessed"),
        ("log", "03:30  offline    still works"),
        ("log", "04:02  backup     restored, not just taken"),
        ("log", "04:06  status     within baseline"),
        ("cmd", "last -n 1 neogeoone"),
        ("out", f"neogeoone  pts/0   {last or 'quiet so far'}"),
    ]
    W, LH, X, Y0, FS, CW = 1200, 24, 28, 74, 15, 9.0
    H = Y0 + LH * (len(lines) + 1) + 10
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Terminal: systemctl status neogeoone, active (running); night log; last activity {escape(last or "quiet so far")}">',
         "<style>text{white-space:pre}.ln{opacity:0;animation:show .25s linear forwards}@keyframes show{from{opacity:0}to{opacity:1}}"
         ".ty{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:type var(--d) steps(var(--n)) forwards}"
         "@keyframes type{to{transform:scaleX(1)}}.cur{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
         "@media (prefers-reduced-motion: reduce){.ln{opacity:1!important;animation:none!important}"
         ".ty{transform:none!important;animation:none!important}}</style>",
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="{c["bg"]}" stroke="{c["frame"]}"/>',
         f'<path d="M1 11 a10 10 0 0 1 10-10 h{W-22} a10 10 0 0 1 10 10 v25 h-{W-2} z" fill="{c["bar"]}"/>',
         *[f'<circle cx="{24 + i*20}" cy="19" r="6" fill="{col}"/>' for i, col in enumerate(("#ff5f56", "#ffbd2e", "#27c93f"))],
         f'<text x="{W/2}" y="24" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{c["dim"]}">neogeoone@nightcity: ~</text>']
    t = 0.4
    for i, (kind, txt) in enumerate(lines):
        y = Y0 + i * LH
        if kind == "cmd":
            n = len(txt); dur = n * 0.045
            o.append(f'<g class="ln" style="animation-delay:{t:.2f}s"><text x="{X}" y="{y}" font-family="{FONT}" font-size="{FS}">'
                     f'<tspan fill="{c["prompt"]}">$ </tspan></text>'
                     f'<g class="ty" style="--d:{dur:.2f}s;--n:{n};animation-delay:{t:.2f}s"><text x="{X + 2*CW}" y="{y}" '
                     f'font-family="{FONT}" font-size="{FS}" fill="{c["text"]}">{escape(txt)}</text></g></g>')
            t += dur + 0.35
        else:
            fill = {"ok": c["ok"], "log": c["text"], "out": c["dim"]}[kind]
            body = escape(txt)
            if kind == "ok":
                body = f'<tspan fill="{c["ok"]}">●</tspan><tspan fill="{c["text"]}">{escape(txt[1:])}</tspan>'
            if kind == "out" and "active (running)" in txt:
                a, b = txt.split("active (running)")
                body = f'{escape(a)}<tspan fill="{c["ok"]}" font-weight="bold">active (running)</tspan>{escape(b)}'
            if kind == "log":
                ts, rest = txt[:5], txt[5:]
                body = f'<tspan fill="{c["amber"]}">{ts}</tspan>{escape(rest)}'
            o.append(f'<text class="ln" style="animation-delay:{t:.2f}s" x="{X}" y="{y}" font-family="{FONT}" '
                     f'font-size="{FS}" fill="{fill}">{body}</text>')
            t += 0.12
    y = Y0 + len(lines) * LH
    o.append(f'<g class="ln" style="animation-delay:{t:.2f}s"><text x="{X}" y="{y}" font-family="{FONT}" font-size="{FS}" '
             f'fill="{c["prompt"]}">$ </text><rect class="cur" x="{X + 2*CW}" y="{y-13}" width="9" height="16" fill="{c["prompt"]}"/></g>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def skyline(theme, weeks):
    c = THEMES[theme]
    rng = random.Random(52)
    W, H, base = 1200, 190, 160
    n = len(weeks) or 1
    step = (W - 40) / n
    bw = step * 0.78
    top = max(weeks) if weeks and max(weeks) > 0 else 1
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Contribution skyline: one building per week, {sum(weeks)} contributions in the last year">',
         "<style>.tw{animation:tw var(--t) steps(1) infinite}@keyframes tw{0%{opacity:1}48%{opacity:.25}70%{opacity:1}}"
         "@media (prefers-reduced-motion: reduce){.tw{animation:none}}</style>",
         f'<defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["sky0"]}"/>'
         f'<stop offset="1" stop-color="{c["sky1"]}"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="10" fill="url(#s)"/>']
    for i, v in enumerate(weeks):
        h = rng.randint(45, 135)  # the city is always there; the lit windows are the contributions
        x = 20 + i * step
        o.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{c["city"]}"/>')
        rows = int((h - 8) // 9); cols = max(1, int((bw - 4) // 6)); lit = v
        for r in range(rows):
            for k in range(cols):
                on = lit > 0 and rng.random() < min(1, 0.35 + v / top)
                if on:
                    lit -= 1
                wx, wy = x + 3 + k * 6, base - h + 5 + r * 9
                if on:
                    cls = f' class="tw" style="--t:{rng.uniform(5, 14):.1f}s"' if rng.random() < 0.15 else ""
                    o.append(f'<rect{cls} x="{wx:.1f}" y="{wy:.1f}" width="3" height="4" fill="{rng.choice((c["win"], c["win2"]))}"/>')
                else:
                    o.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="3" height="4" fill="{c["unlit"]}"/>')
    o.append(f'<rect x="20" y="{base}" width="{W-40}" height="1" fill="{c["frame"]}"/>')
    o.append(f'<text x="20" y="{base + 20}" font-family="{FONT}" font-size="12" fill="{c["dim"]}">'
             f'last 52 weeks · one building per week · lights = public contributions · redrawn daily</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def main():
    login, out = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    weeks, last = fetch(login, token)
    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        with open(os.path.join(out, f"terminal-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(terminal(theme, last))
        with open(os.path.join(out, f"skyline-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(skyline(theme, weeks))
    print(f"rendered: {len(weeks)} weeks, {sum(weeks)} contributions, last activity: {last or 'none public'}")


if __name__ == "__main__":
    main()
