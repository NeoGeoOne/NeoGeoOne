#!/usr/bin/env python3
"""Render the toolbox card: a tower at night, one floor per layer, every tool a neon sign.

Writes assets/stack-dark.svg and assets/stack-light.svg. Standard library only.

    python3 tools/stack.py assets/
"""
import os
import random
import sys

# Top floor first: from the agents down to the machine.
LAYERS = [
    ("agents", "pink", ["Claude Code", "OpenCode", "Hermes", "OpenClaw", "Gemini CLI"]),
    ("interfaces", "cyan", ["MCP", "ACP", "A2A", "Agent Skills"]),
    ("automation", "cyan", ["n8n", "Hermes Kanban", "Playwright"]),
    ("inference", "cyan", ["Ollama", "llama.cpp", "vLLM", "LM Studio"]),
    ("training", "cyan", ["Unsloth", "PyTorch", "Hugging Face"]),
    ("media", "cyan", ["ComfyUI", "Whisper", "text-to-speech", "FFmpeg"]),
    ("databases", "amber", ["Qdrant", "PostgreSQL", "MariaDB", "SQLite"]),
    ("code", "amber", ["Python", "uv", "Node.js", "TypeScript", "PHP", "Git"]),
    ("shell", "amber", ["Bash", "PowerShell", "cmd", "tmux"]),
    ("runtime", "red", ["Docker", "Docker Compose", "Portainer", "QEMU", "VirtualBox"]),
    ("web", "red", ["nginx", "Apache", "PHP-FPM"]),
    ("network", "red", ["WireGuard", "Tailscale", "SSH", "Little Snitch"]),
    ("storage", "red", ["LVM", "Samba", "rsync"]),
    ("system", "red", ["Debian", "Ubuntu", "Red Hat", "CentOS", "Windows", "Windows Server"]),
]
FLICKER = {"A2A"}  # the newest protocol gets the unsteady sign

W = 1200
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FS = 17                      # tool sign font size; the image shows at ~0.7x in a README column
CW = FS * 0.6                # monospace advance; textLength pins it so every font fits its sign
PAD, GAP, TAG_H = 11, 10, 25
ROW_H = 34
TOP = 112                    # roof and antenna above the first floor
BASE = 46
H = TOP + ROW_H * len(LAYERS) + BASE
TX0, TX1 = 70, 1050          # tower facade
LABEL_X, TOOLS_X = 92, 300   # floor label column, first sign
SIGN_X = 1088                # vertical TOOLBOX sign

THEMES = {
    "dark": dict(sky=("#04060b", "#0d1220", "#1b1430", "#2a1636"), far="#121826", far2="#151c2b",
                 tower="#0f141f", edge="#2a3346", slab="#1e2638", win="#d4a72c", tagbg="#0b0f17",
                 label="#8b949e", num="#6e5a2a", ground="#07090f", rain="#9ad7ff", rain_op=0.16,
                 beam="#9ad7ff", beam_op=0.10, light="#ff3b3b", glow=2.2, page="#0d1117",
                 pink="#ff4fd8", cyan="#39c5cf", amber="#d4a72c", red="#e5534b"),
    "light": dict(sky=("#f6f8fa", "#eef1f5", "#f3e3dc", "#f0c4a6"), far="#c9d1db", far2="#b9c2cd",
                  tower="#d6dde6", edge="#7d8a99", slab="#b9c2cd", win="#bf8700", tagbg="#f6f8fa",
                  label="#59636e", num="#9a8a66", ground="#b9c2cd", rain="#7d8a99", rain_op=0.22,
                  beam="#ffffff", beam_op=0.0, light="#cf222e", glow=0.0, page="#ffffff",
                  pink="#bf3989", cyan="#0a7a85", amber="#9a6700", red="#cf222e"),
}


def tag_w(name):
    return len(name) * CW + 2 * PAD


def aria():
    rows = "; ".join(f"{name}: {', '.join(tools)}" for name, _, tools in LAYERS)
    return f"Toolbox as a tower at night, one floor per layer from top to bottom. {rows}."


def city(rng, c):
    """Distant blocks behind the tower; only the margins and the sky above the roof show them."""
    out = []
    x = -20
    while x < W + 20:
        w = rng.randint(40, 110)
        h = rng.randint(140, 440)
        y = H - BASE - h + 20
        fill = c["far"] if rng.random() < 0.5 else c["far2"]
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h + BASE}" fill="{fill}"/>')
        for wy in range(y + 10, H - BASE, 14):
            for wx in range(x + 6, x + w - 6, 11):
                if rng.random() < 0.07:
                    dur = rng.uniform(6, 18)
                    out.append(f'<rect class="win" x="{wx}" y="{wy}" width="4" height="6" fill="{c["win"]}" '
                               f'opacity="0.55" style="animation-duration:{dur:.1f}s;animation-delay:-{rng.uniform(0, dur):.1f}s"/>')
        x += w + rng.randint(2, 14)
    return "".join(out)


def rain(rng, c):
    out = []
    for k in range(150):
        cls = ("rf", "rm", "rn")[k % 3]
        x, y = rng.uniform(0, W + 60), rng.uniform(0, H)
        ln = {"rf": 10, "rm": 16, "rn": 24}[cls]
        out.append(f'<line class="{cls}" x1="{x:.0f}" y1="{y:.0f}" x2="{x - ln * 0.18:.1f}" y2="{y + ln:.0f}" '
                   f'style="animation-delay:-{rng.uniform(0, 2.6):.2f}s"/>')
    return f'<g stroke="{c["rain"]}" stroke-width="1" opacity="{c["rain_op"]}">{"".join(out)}</g>'


def facade(rng, c):
    """Tower body, unlit window grid, floor slabs and the stepped roof with its antenna."""
    y0, y1 = TOP, H - BASE
    o = [f'<rect x="{TX0 + 300}" y="58" width="360" height="{TOP - 58 + 2}" fill="{c["tower"]}" stroke="{c["edge"]}"/>',
         f'<rect x="{TX0 + 200}" y="86" width="560" height="{TOP - 86 + 2}" fill="{c["tower"]}" stroke="{c["edge"]}"/>',
         f'<line x1="{TX0 + 480}" y1="10" x2="{TX0 + 480}" y2="58" stroke="{c["edge"]}" stroke-width="2"/>',
         f'<line x1="{TX0 + 468}" y1="30" x2="{TX0 + 492}" y2="30" stroke="{c["edge"]}" stroke-width="1.5"/>',
         f'<circle class="blink" cx="{TX0 + 480}" cy="9" r="3.2" fill="{c["light"]}" filter="url(#glow)"/>',
         f'<rect x="{TX0}" y="{y0}" width="{TX1 - TX0}" height="{y1 - y0}" fill="{c["tower"]}" stroke="{c["edge"]}"/>']
    for wy in range(66, TOP - 4, 12):
        for wx in range(TX0 + 312, TX0 + 650, 14):
            if rng.random() < 0.12:
                o.append(f'<rect x="{wx}" y="{wy}" width="5" height="6" fill="{c["win"]}" opacity="0.35"/>')
    for i in range(len(LAYERS) + 1):
        y = y0 + i * ROW_H
        o.append(f'<line x1="{TX0}" y1="{y}" x2="{TX1}" y2="{y}" stroke="{c["slab"]}" stroke-width="1"/>')
    o.append(f'<line x1="{TOOLS_X - 14}" y1="{y0}" x2="{TOOLS_X - 14}" y2="{y1}" stroke="{c["slab"]}" stroke-width="1"/>')
    return "".join(o)


def floors(rng, c):
    o = []
    n = len(LAYERS)
    for i, (name, tone, tools) in enumerate(LAYERS):
        cy = TOP + i * ROW_H + ROW_H / 2
        col = c[tone]
        o.append(f'<text x="{LABEL_X}" y="{cy + 5:.1f}" font-family="{FONT}" font-size="14" fill="{c["num"]}">'
                 f'{n - i:02d}</text>'
                 f'<text x="{LABEL_X + 34}" y="{cy + 5.5:.1f}" font-family="{FONT}" font-size="16" fill="{c["label"]}">{name}</text>')
        x = TOOLS_X
        for tool in tools:
            w = tag_w(tool)
            cls = ' class="neon"' if tool in FLICKER else ""
            o.append(f'<g{cls} filter="url(#glow)">'
                     f'<rect x="{x:.1f}" y="{cy - TAG_H / 2:.1f}" width="{w:.1f}" height="{TAG_H}" rx="4" '
                     f'fill="{c["tagbg"]}" fill-opacity="0.9" stroke="{col}" stroke-width="1.4"/>'
                     f'<text x="{x + PAD:.1f}" y="{cy + FS * 0.34:.1f}" font-family="{FONT}" font-size="{FS}" fill="{col}" '
                     f'textLength="{len(tool) * CW:.1f}" lengthAdjust="spacingAndGlyphs">{tool}</text></g>')
            x += w + GAP
        assert x - GAP <= TX1 - 16, f"floor '{name}' overflows the facade ({x - GAP:.0f} > {TX1 - 16})"
        o.append(windows(rng, c, x + 14, cy))
    return "".join(o)


def windows(rng, c, x0, cy):
    """Window grid in the facade space a floor leaves free; a few are lit, some of those flicker."""
    o = []
    for wy in (cy - 10, cy + 2):
        for wx in range(int(x0), TX1 - 14, 13):
            r = rng.random()
            if r < 0.16:
                cls = ""
                if r < 0.04:
                    dur = rng.uniform(7, 20)
                    cls = f' class="win" style="animation-duration:{dur:.1f}s;animation-delay:-{rng.uniform(0, dur):.1f}s"'
                o.append(f'<rect{cls} x="{wx}" y="{wy:.0f}" width="6" height="8" fill="{c["win"]}" opacity="0.5"/>')
            else:
                o.append(f'<rect x="{wx}" y="{wy:.0f}" width="6" height="8" fill="{c["slab"]}" opacity="0.7"/>')
    return "".join(o)


def sign(c):
    """Vertical neon sign on the tower's flank."""
    letters = "TOOLBOX"
    top = TOP + 40
    step = 44
    hgt = step * len(letters) + 18
    o = [f'<line x1="{TX1}" y1="{top + 20}" x2="{SIGN_X - 20}" y2="{top + 20}" stroke="{c["edge"]}" stroke-width="2"/>',
         f'<line x1="{TX1}" y1="{top + hgt - 20}" x2="{SIGN_X - 20}" y2="{top + hgt - 20}" stroke="{c["edge"]}" stroke-width="2"/>',
         f'<g class="neon2" filter="url(#glow)">'
         f'<rect x="{SIGN_X - 20}" y="{top}" width="40" height="{hgt}" rx="5" fill="{c["tagbg"]}" fill-opacity="0.9" '
         f'stroke="{c["pink"]}" stroke-width="1.6"/>']
    for k, ch in enumerate(letters):
        o.append(f'<text x="{SIGN_X}" y="{top + 38 + k * step}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="26" font-weight="700" fill="{c["pink"]}">{ch}</text>')
    o.append("</g>")
    return "".join(o)


def beams(c):
    if not c["beam_op"]:
        return ""
    o = []
    for cls, x in (("sweep", 230), ("sweep2", 900)):
        o.append(f'<polygon class="{cls}" style="transform-origin:{x}px {H - BASE}px" '
                 f'points="{x - 4},{H - BASE} {x + 4},{H - BASE} {x + 60},-40 {x - 60},-40" fill="url(#beam)"/>')
    return "".join(o)


def card(theme):
    c = THEMES[theme]
    rng = random.Random(2049)
    sky = c["sky"]
    glow = (f'<filter id="glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="{c["glow"]}" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>') if c["glow"] else \
           '<filter id="glow"><feMerge><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{aria()}">',
         "<defs>",
         '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">' +
         "".join(f'<stop offset="{off}" stop-color="{col}"/>' for off, col in zip((0, 0.35, 0.75, 1), sky)) +
         "</linearGradient>",
         f'<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{c["beam"]}" stop-opacity="{c["beam_op"]}"/>'
         f'<stop offset="1" stop-color="{c["beam"]}" stop-opacity="0"/></linearGradient>',
         f'<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["page"]}" stop-opacity="0"/>'
         f'<stop offset="1" stop-color="{c["page"]}" stop-opacity="0.9"/></linearGradient>',
         glow,
         "</defs>",
         "<style>",
         ".rf{animation:fall 2.6s linear infinite}.rm{animation:fall 1.7s linear infinite}.rn{animation:fall 1.05s linear infinite}",
         f"@keyframes fall{{from{{transform:translateY(-{H}px)}}to{{transform:translateY({H}px)}}}}",
         ".win{animation-name:win;animation-iteration-count:infinite;animation-timing-function:steps(1)}",
         "@keyframes win{0%{opacity:0.55}46%{opacity:0.06}71%{opacity:0.55}}",
         ".neon{animation:flicker 7s infinite}.neon2{animation:flicker 11s 3s infinite}",
         "@keyframes flicker{0%,18%,22%,62%,64%,100%{opacity:1}20%,63%{opacity:0.25}21%{opacity:0.7}}",
         ".sweep{transform-box:view-box;animation:sweep 14s ease-in-out infinite alternate}",
         ".sweep2{transform-box:view-box;animation:sweep 19s ease-in-out infinite alternate-reverse}",
         "@keyframes sweep{from{transform:rotate(-24deg)}to{transform:rotate(22deg)}}",
         ".blink{animation:blink 1.2s steps(1) infinite}@keyframes blink{50%{opacity:0}}",
         "@media (prefers-reduced-motion: reduce){*{animation:none!important}}",
         "</style>",
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         beams(c),
         city(rng, c),
         facade(rng, c),
         floors(rng, c),
         sign(c),
         f'<rect y="{H - BASE}" width="{W}" height="{BASE}" fill="{c["ground"]}"/>',
         f'<rect y="{H - BASE}" width="{W}" height="{BASE}" fill="url(#fog)"/>',
         rain(rng, c),
         "</svg>"]
    return "\n".join(o) + "\n"


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        with open(os.path.join(out, f"stack-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(card(theme))


if __name__ == "__main__":
    main()
