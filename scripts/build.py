#!/usr/bin/env python3
"""Builds the static SVGs in assets/ for the profile README.

    python scripts/build.py

The live telemetry card is built separately by scripts/telemetry.py
(run daily by .github/workflows/profile.yml).
"""
from __future__ import annotations

import math
import random

from svgkit import (
    BG, CHIP, CYAN, CYAN_MID, DIM, GREEN, LINE, MUTED, PINK, ROOT, TEXT, VIOLET, VIOLET_MID,
    MONO_ADVANCE, delay, esc, fit, icon, mono_width, spans, svg, wrap,
)

OUT = ROOT / "assets"


def smooth(pts: list[tuple[float, float]]) -> str:
    """Catmull-Rom spline through pts, as an SVG path."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


def chevron(x: float, y: float, color: str = CYAN) -> str:
    return (f'<path d="M{x:.1f} {y - 9.6:.1f}l5 4.7-5 4.7" stroke="{color}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def check(x: float, y: float) -> str:
    return (f'<path d="M{x:.1f} {y - 4.6:.1f}l3.6 3.6 7-7.6" stroke="{GREEN}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


# --------------------------------------------------------------------------- hero

def hero() -> str:
    W, H = 1000, 660
    FS = 13.5
    CW = FS * MONO_ADVANCE
    X, TX = 40, 58
    defs: list[str] = []
    b: list[str] = []

    # timeline, seconds
    t_type1, per1 = 0.45, 0.032
    t_agent = (1.45, 1.7, 1.95)
    t_type2, per2 = 2.25, 0.02
    t_train0, t_train1 = 3.2, 5.0
    t_checks = (5.15, 5.35, 5.55)
    t_prompt = 5.8
    t_card = 5.7

    defs += [
        '<clipPath id="win"><rect x="10" y="10" width="980" height="620" rx="14"/></clipPath>',
        '<radialGradient id="gv" cx=".9" cy="0" r=".75"><stop offset="0" stop-color="#a78bfa" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>',
        '<radialGradient id="gc" cx=".05" cy="1" r=".65"><stop offset="0" stop-color="#22d3ee" stop-opacity=".12"/>'
        '<stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>',
        '<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" stitchTiles="stitch"/>'
        '<feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .07 0"/></filter>',
        '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<filter id="shadow" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="10" stdDeviation="9" '
        'flood-color="#010409" flood-opacity=".35"/></filter>',
        '<linearGradient id="tg" x1="0" x2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>',
        '<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22d3ee" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>',
    ]

    # window, glows, grain, title bar
    b.append(f'<rect x="10" y="10" width="980" height="620" rx="14" fill="{BG}" filter="url(#shadow)"/>')
    b.append('<g clip-path="url(#win)">')
    b.append('<rect x="10" y="10" width="980" height="620" fill="url(#gv)"/>'
             '<rect x="10" y="10" width="980" height="620" fill="url(#gc)"/>'
             '<rect x="10" y="10" width="980" height="620" filter="url(#grain)"/>')
    b.append(f'<rect x="10" y="10" width="980" height="40" fill="#0d1119"/><path d="M10 50H990" stroke="{LINE}"/>')
    for cx, c in ((34, "#ff5f57"), (54, "#febc2e"), (74, "#28c840")):
        b.append(f'<circle cx="{cx}" cy="30" r="6" fill="{c}"/>')
    b.append(f'<text class="m" x="500" y="34" font-size="12" fill="{DIM}" text-anchor="middle">'
             f'kavin@chennai: ~/vibe — zsh</text>')

    def typed(idx: int, y: float, segs, t0: float, per: float) -> str:
        n = sum(len(s[0]) for s in segs)
        end = t0 + n * per
        kt = ";".join(f"{k:.4f}" for k in [0.0] + [(t0 + i * per) / end for i in range(n + 1)])
        widths = ";".join(["0"] + [f"{i * CW + 1:.1f}" for i in range(n)] + ["900"])
        xs = ";".join([f"{TX}"] + [f"{TX + i * CW:.1f}" for i in range(n + 1)])
        defs.append(
            f'<clipPath id="ty{idx}"><rect x="{TX - 2}" y="{y - 16}" height="24" width="0">'
            f'<animate attributeName="width" dur="{end:.2f}s" fill="freeze" calcMode="discrete" '
            f'keyTimes="{kt}" values="{widths}"/></rect></clipPath>')
        cursor = (
            f'<rect x="{TX}" y="{y - 13}" width="{CW:.1f}" height="17" fill="{CYAN}" opacity="0">'
            f'<animate attributeName="x" dur="{end:.2f}s" fill="freeze" calcMode="discrete" keyTimes="{kt}" values="{xs}"/>'
            f'<set attributeName="opacity" to=".85" begin="{max(t0 - 0.3, 0):.2f}s" end="{end + 0.12:.2f}s"/></rect>')
        return (f'<text class="m" x="{TX}" y="{y}" font-size="{FS}" clip-path="url(#ty{idx})">{spans(segs)}</text>'
                + cursor)

    # ---- left pane: the session
    y1, ya, y5, y6, yc, y10 = 92, (118, 140, 162), 194, 222, (252, 274, 296), 326
    b.append(f'<g class="fade"{delay(0.15)}>{chevron(X, y1)}</g>')
    b.append(typed(1, y1, [("claude", VIOLET, 700), (" ", TEXT), ('"ship kavin --vibe"', CYAN)], t_type1, per1))

    agent_lines = [
        [("reading every repo, commit and half-finished idea", MUTED)],
        [("plan: ", TEXT), ("train it, serve it, ship it", MUTED)],
        [("handing off to the training loop", MUTED)],
    ]
    for y, t, segs in zip(ya, t_agent, agent_lines):
        b.append(f'<g class="in"{delay(t)}>{icon("claude", TX, y - 11, 12, VIOLET)}'
                 f'<text class="m" x="{TX + 20}" y="{y}" font-size="{FS}">{spans(segs)}</text></g>')

    b.append(f'<g class="fade"{delay(t_type2 - 0.2)}>{chevron(X, y5)}</g>')
    b.append(typed(2, y5, [("python", VIOLET, 700), (" train.py ", TEXT), ("--model ", MUTED), ("kavin ", CYAN),
                           ("--epochs ", MUTED), ("28", CYAN)], t_type2, per2))

    # training curves (shared by the epoch counter and the chart)
    rnd = random.Random(2028)
    steps = [i / 2 for i in range(57)]
    loss = [2.31 * math.exp(-e / 4.8) + 0.07 + abs(rnd.gauss(0, 0.05 * math.exp(-e / 9))) for e in steps]
    acc = [min(0.93, 0.07 + 0.852 * (1 - math.exp(-e / 5.2)) + rnd.gauss(0, 0.012 * math.exp(-e / 14))) for e in steps]
    loss[-1], acc[-1] = 0.081, 0.922

    # epoch counter: 27 transient frames, then the final one stays
    bar_x, bar_w = TX + 106, 168
    dt = (t_train1 - t_train0) / 28

    def epoch_frame(e: int) -> str:
        return (f'<text class="m" x="{TX}" y="{y6}" font-size="{FS}">'
                f'{spans([("epoch ", MUTED), (f"{e:02d}/28", TEXT)])}</text>'
                f'<text class="m" x="{bar_x + bar_w + 14}" y="{y6}" font-size="{FS}">'
                f'{spans([("loss ", MUTED), (f"{loss[e * 2]:.3f}", CYAN, 500)])}</text>')

    for e in range(1, 28):
        b.append(f'<g class="flash"{delay(t_train0 + (e - 1) * dt, dt)}>{epoch_frame(e)}</g>')
    b.append(f'<g class="fade"{delay(t_train0 + 27 * dt, 0.05)}>{epoch_frame(28)}</g>')
    a = t_train0 / t_train1
    b.append(f'<g class="fade"{delay(t_train0, 0.2)}>'
             f'<rect x="{bar_x}" y="{y6 - 8}" width="{bar_w}" height="6" rx="3" fill="{LINE}"/>'
             f'<rect x="{bar_x}" y="{y6 - 8}" width="0" height="6" rx="3" fill="url(#tg)">'
             f'<animate attributeName="width" dur="{t_train1:.2f}s" fill="freeze" keyTimes="0;{a:.4f};1" '
             f'values="0;0;{bar_w}"/></rect></g>')

    checks = [
        [("val_acc ", MUTED), ("0.922", GREEN, 700), ("  296 ISL signs · BiLSTM + attention", MUTED)],
        [("shipped ", MUTED), ("RainCheck · WSF · ISL · Pro-Techt", TEXT)],
        [("saved ", MUTED), ("kavin-v2028", CYAN), (" — ready for inference", MUTED)],
    ]
    for y, t, segs in zip(yc, t_checks, checks):
        b.append(f'<g class="in"{delay(t)}>{check(TX, y)}'
                 f'<text class="m" x="{TX + 20}" y="{y}" font-size="{FS}">{spans(segs)}</text></g>')
    b.append(f'<g class="fade"{delay(t_prompt, 0.1)}>{chevron(X, y10)}'
             f'<rect class="blink" x="{TX}" y="{y10 - 13}" width="{CW:.1f}" height="17" fill="{CYAN}" opacity=".85"/></g>')

    # ---- right pane: the chart
    b.append(f'<path d="M588 66V336" stroke="{LINE}"/>')
    x0, x1, yT, yB = 622, 956, 112, 300
    px = lambda e: x0 + (x1 - x0) * e / 28
    pl = lambda v: yB - (yB - yT) * v / 2.5
    pa = lambda v: yB - (yB - yT) * v
    b.append(f'<g class="fade"{delay(0.3)}>'
             f'<circle cx="617" cy="84" r="3.5" fill="{CYAN}"/>'
             f'<text class="m" x="627" y="88" font-size="12" fill="{TEXT}">train/loss</text>'
             f'<circle cx="725" cy="84" r="3.5" fill="{VIOLET}"/>'
             f'<text class="m" x="735" y="88" font-size="12" fill="{TEXT}">val/acc</text>'
             f'<text class="m" x="{x1}" y="88" font-size="11" fill="{DIM}" text-anchor="end">seed 2028</text>')
    for i in range(5):
        y = yT + (yB - yT) * i / 4
        b.append(f'<path d="M{x0} {y:.1f}H{x1}" stroke="{LINE}" stroke-dasharray="2 5"/>')
    for e in (0, 7, 14, 21, 28):
        b.append(f'<text class="m" x="{px(e):.1f}" y="{yB + 18}" font-size="10" fill="{DIM}" text-anchor="middle">{e}</text>')
    b.append("</g>")
    lp = smooth([(px(e), pl(v)) for e, v in zip(steps, loss)])
    ap = smooth([(px(e), pa(v)) for e, v in zip(steps, acc)])
    tdur = t_train1 - t_train0
    b.append(f'<path class="fade" d="{lp} L{x1} {yB} L{x0} {yB}Z" fill="url(#area)"{delay(t_train1 - 0.4, 0.8)}/>')
    b.append(f'<path class="draw" d="{ap}" pathLength="1" stroke="{VIOLET}" stroke-width="2" stroke-linecap="round" '
             f'filter="url(#glow)"{delay(t_train0, tdur)}/>')
    b.append(f'<path class="draw" d="{lp}" pathLength="1" stroke="{CYAN}" stroke-width="2.2" stroke-linecap="round" '
             f'filter="url(#glow)"{delay(t_train0, tdur)}/>')
    b.append(f'<g class="in"{delay(t_train1)}>'
             f'<circle cx="{x1}" cy="{pl(0.081):.1f}" r="4" fill="{CYAN}" filter="url(#glow)"/>'
             f'<circle cx="{x1}" cy="{pa(0.922):.1f}" r="4" fill="{VIOLET}" filter="url(#glow)"/>'
             f'<text class="m" x="{x1 - 8}" y="{pl(0.081) - 10:.1f}" font-size="11.5" font-weight="700" fill="{CYAN}" text-anchor="end">0.081</text>'
             f'<text class="m" x="{x1 - 8}" y="{pa(0.922) - 10:.1f}" font-size="11.5" font-weight="700" fill="{VIOLET}" text-anchor="end">92.2%</text></g>')

    # ---- model card
    b.append(f'<path class="draw" d="M30 352H970" pathLength="1" stroke="{LINE}"{delay(t_card - 0.2, 0.8)}/>')
    b.append(f'<text class="m in" x="40" y="390" font-size="11" letter-spacing="2.5"{delay(t_card)}>'
             f'{spans([("MODEL CARD", DIM), ("  /  ", DIM), ("kavin-v2028", CYAN)])}</text>')
    b.append(f'<text class="s in" x="37" y="458" font-size="64" fill="{TEXT}"{fit("serif", "Kavin Krish Vijay", 64)}{delay(t_card + 0.15)}>Kavin Krish Vijay</text>')
    tag1 = "Vibe-coded speed."
    b.append(f'<g class="in"{delay(t_card + 0.35)}>'
             f'<text class="m" x="40" y="500" font-size="21" font-weight="800" fill="url(#tg)">{tag1}</text>'
             f'<text class="s" x="{40 + mono_width(tag1, 21) + 12:.1f}" y="501" font-size="31" font-style="italic" '
             f'fill="{TEXT}"{fit("serif-i", "Engineered depth.", 31)}>Engineered depth.</text></g>')
    b.append(f'<g class="in"{delay(t_card + 0.55)}>'
             f'<text class="m" x="40" y="540" font-size="13" fill="{MUTED}">I build ML products end to end and ship them with AI agents —</text>'
             f'<text class="m" x="40" y="562" font-size="13" fill="{TEXT}">then I read every line they write.</text></g>')
    b.append(f'<path class="fade" d="M572 376V574" stroke="{LINE}"{delay(t_card + 0.3)}/>')

    kx, vx, ry, rstep = 600, 704, 392, 25.4
    rows = [
        ("arch", [("applied ML × full-stack", TEXT)]),
        ("trained_on", [("B.Tech CSE · SRM IST '28", TEXT)]),
        ("region", [("Chennai, IN · UTC+5:30", TEXT)]),
        ("co_pilots", [("Claude Code · Cursor · Antigravity", TEXT)]),
        ("peak_hours", [("00:00–04:00", CYAN), (" · night owl", MUTED)]),
        ("status", None),
        ("endpoint", [("krishkavin7512@gmail.com", CYAN)]),
        ("portfolio", [("kavin-dev-portfolio.vercel.app", CYAN)]),
    ]
    for i, (key, segs) in enumerate(rows):
        y = ry + i * rstep
        t = t_card + 0.3 + i * 0.09
        if segs is None:
            value = (f'<circle cx="{vx + 4}" cy="{y - 4.5:.1f}" r="3.5" fill="{GREEN}"/>'
                     f'<circle class="pulse" cx="{vx + 4}" cy="{y - 4.5:.1f}" r="3.5" fill="{GREEN}"{delay(t + 0.6)}/>'
                     f'<text class="m" x="{vx + 16}" y="{y:.1f}" font-size="12.5" font-weight="500" fill="{GREEN}">open to internships</text>')
        else:
            value = f'<text class="m" x="{vx}" y="{y:.1f}" font-size="12.5">{spans(segs)}</text>'
        b.append(f'<g class="in"{delay(t)}><text class="m" x="{kx}" y="{y:.1f}" font-size="11.5" fill="{DIM}">{key}</text>{value}</g>')

    # ---- status bar
    b.append(f'<rect x="10" y="600" width="980" height="30" fill="#0c1018"/><path d="M10 600H990" stroke="{LINE}"/>')
    b.append(f'<g class="fade"{delay(0.2)}>'
             f'<circle cx="30" cy="615" r="3" stroke="{MUTED}" stroke-width="1.4"/>'
             f'<text class="m" x="40" y="619" font-size="11">'
             f'{spans([("main", MUTED), ("    0 errors    1 warning: ", DIM), ("sleeps after midnight", MUTED)])}</text>'
             f'<circle cx="874" cy="615" r="3" fill="{VIOLET}"/>'
             f'<circle class="pulse" cx="874" cy="615" r="3" fill="{VIOLET}"/>'
             f'<text class="m" x="966" y="619" font-size="11" text-anchor="end">{spans([("vibe mode ", DIM), ("on", VIOLET, 700)])}</text></g>')
    b.append("</g>")

    return svg(W, H, f"<defs>{''.join(defs)}</defs>{''.join(b)}",
               fonts=("mono400", "mono500", "mono700", "mono800", "serif", "serif-i"),
               title="Kavin Krish Vijay — applied ML × full-stack. Vibe-coded speed, engineered depth.")


# --------------------------------------------------------------------------- project cards

def vis_rain(acc: str) -> str:
    out = ['<defs><linearGradient id="cloud" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3a52"/>'
           '<stop offset="1" stop-color="#16202e"/></linearGradient></defs>',
           f'<g fill="url(#cloud)" stroke="{acc}" stroke-opacity=".35" filter="url(#cglow)">'
           '<path d="M362 92a16 16 0 0 1 4-31.5 22 22 0 0 1 41.5-6 15 15 0 0 1 16 37.5z"/></g>']
    for i, x in enumerate(range(366, 424, 8)):
        out.append(f'<path class="rain" d="M{x} 100l-3 9" stroke="{acc}" stroke-width="1.8" stroke-linecap="round" '
                   f'style="animation-delay:-{(i * 0.37) % 1.1:.2f}s"/>')
    out.append(f'<path d="M332 130H456" stroke="{acc}" stroke-opacity=".45" stroke-dasharray="3 4"/>'
               f'<text class="m" x="332" y="124" font-size="9" fill="{MUTED}">trigger</text>'
               f'<g class="ping"><rect x="364" y="138" width="84" height="20" rx="10" fill="{GREEN}" fill-opacity=".14" stroke="{GREEN}" stroke-opacity=".7"/>'
               f'<text class="m" x="406" y="152" font-size="10" font-weight="700" fill="{GREEN}" text-anchor="middle">PAYOUT SENT</text></g>')
    return "".join(out)


def vis_map(acc: str) -> str:
    out = ['<defs><radialGradient id="z1"><stop offset="0" stop-color="#f472b6" stop-opacity=".55"/>'
           '<stop offset="1" stop-color="#f472b6" stop-opacity="0"/></radialGradient>'
           '<radialGradient id="z2"><stop offset="0" stop-color="#a78bfa" stop-opacity=".5"/>'
           '<stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>'
           '<clipPath id="mapclip"><rect x="322" y="50" width="136" height="108" rx="10"/></clipPath></defs>',
           '<g clip-path="url(#mapclip)"><rect x="322" y="50" width="136" height="108" fill="#0d121a"/>']
    for x in range(330, 460, 18):
        out.append(f'<path d="M{x} 50V158" stroke="{LINE}"/>')
    for y in range(58, 160, 18):
        out.append(f'<path d="M322 {y}H458" stroke="{LINE}"/>')
    route = "M330 148C346 146 340 124 360 120S394 132 400 108 414 70 448 64"
    out.append('<circle cx="378" cy="88" r="30" fill="url(#z1)"/><circle cx="428" cy="132" r="26" fill="url(#z2)"/>')
    out.append(f'<path d="{route}" stroke="{acc}" stroke-width="2.4" stroke-linecap="round" filter="url(#cglow)"/>')
    out.append(f'<circle r="3.6" fill="#fff"><animateMotion dur="5s" repeatCount="indefinite" path="{route}"/></circle>')
    out.append(f'<circle cx="448" cy="64" r="4" fill="{acc}"/><circle class="pulse" cx="448" cy="64" r="4" fill="{acc}"/></g>')
    out.append(f'<rect x="322" y="50" width="136" height="108" rx="10" stroke="{LINE}"/>')
    return "".join(out)


def vis_hand(acc: str) -> str:
    pts = [(60, 104), (42, 94), (30, 80), (22, 68), (16, 58), (48, 62), (46, 44), (45, 32), (44, 22),
           (60, 60), (60, 40), (60, 27), (60, 15), (72, 62), (74, 44), (75, 32), (76, 23),
           (82, 68), (87, 54), (90, 44), (92, 36)]
    bones = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11),
             (11, 12), (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]
    ox, oy = 336, 48
    P = [(x + ox, y + oy) for x, y in pts]
    out = [f'<g stroke="{acc}" stroke-width="1.6" stroke-linecap="round" stroke-opacity=".75">']
    out += [f'<path d="M{P[a][0]} {P[a][1]}L{P[c][0]} {P[c][1]}"/>' for a, c in bones]
    out.append("</g>")
    for i, (x, y) in enumerate(P):
        tip = i in (4, 8, 12, 16, 20)
        out.append(f'<circle cx="{x}" cy="{y}" r="{3.2 if tip else 2.4}" fill="{VIOLET if tip else TEXT}"'
                   + (f' class="tip" style="animation-delay:{i * 0.12:.2f}s"' if tip else "") + "/>")
    # detection box corners + prediction
    bx0, by0, bx1, by1 = 344, 58, 430, 160
    c = 10
    out.append(f'<path d="M{bx0} {by0 + c}V{by0}H{bx0 + c}M{bx1 - c} {by0}H{bx1}V{by0 + c}M{bx1} {by1 - c}V{by1}H{bx1 - c}'
               f'M{bx0 + c} {by1}H{bx0}V{by1 - c}" stroke="{CYAN}" stroke-width="1.6"/>')
    out.append(f'<rect x="400" y="34" width="60" height="20" rx="5" fill="{CYAN}" fill-opacity=".14" stroke="{CYAN}" stroke-opacity=".6"/>'
               f'<text class="m" x="430" y="48" font-size="10" fill="{CYAN}" text-anchor="middle" font-weight="700">hello .97</text>')
    return "".join(out)


def vis_scan(acc: str) -> str:
    rnd = random.Random(412)
    out = [f'<rect x="330" y="52" width="122" height="104" rx="12" fill="#0d121a" stroke="{LINE}"/>']
    x = 346
    while x < 436:
        w = rnd.choice((1.5, 1.5, 2.5, 3.5))
        out.append(f'<rect x="{x:.1f}" y="72" width="{w}" height="42" fill="{TEXT}" fill-opacity=".85"/>')
        x += w + rnd.choice((1.8, 2.6, 3.4))
    c = 8
    out.append(f'<path d="M340 {66 + c}V66H{340 + c}M{442 - c} 66H442V{66 + c}M442 {120 - c}V120H{442 - c}'
               f'M{340 + c} 120H340V{120 - c}" stroke="{acc}" stroke-width="1.6"/>')
    out.append(f'<rect class="scan" x="336" y="66" width="110" height="2" fill="{acc}" filter="url(#cglow)"/>')
    out.append(f'<text class="m" x="391" y="136" font-size="9.5" fill="{MUTED}" text-anchor="middle">SN 2027-0412</text>'
               f'<text class="m" x="391" y="149" font-size="9.5" font-weight="700" fill="{GREEN}" text-anchor="middle">warranty: active</text>')
    return "".join(out)


CARD_CSS = """
.rain{animation:rain 1.1s linear infinite}
@keyframes rain{0%{transform:translateY(-6px);opacity:0}25%{opacity:1}100%{transform:translateY(18px);opacity:0}}
.ping{animation:ping 3.3s ease-in-out infinite}
@keyframes ping{0%,55%{opacity:.35}70%,100%{opacity:1}}
.tip{transform-box:fill-box;transform-origin:center;animation:tip 2.4s ease-in-out infinite}
@keyframes tip{0%,100%{transform:scale(1)}50%{transform:scale(1.6)}}
.scan{animation:scan 2.6s ease-in-out infinite alternate}
@keyframes scan{from{transform:translateY(0)}to{transform:translateY(52px)}}
"""

CARDS = [
    dict(file="card-raincheck", idx="01", accent=CYAN, kicker="PARAMETRIC INSURANCE · HACKATHON",
         title="RainCheck", metric="DEVTrails '26 · phase 2 shipped",
         desc="Weekly income cover for India's food-delivery riders. When rain, heat or AQI crosses a "
              "trigger, the payout fires on its own — zero claims, zero paperwork.",
         role="built the Flutter rider app",
         stack=[("flutter", "Flutter"), ("nextdotjs", "Next.js"), ("express", "Express"),
                ("xgboost", "XGBoost"), ("mongodb", "MongoDB")],
         visual=vis_rain),
    dict(file="card-wsf", idx="02", accent=VIOLET, kicker="WOMEN'S SAFETY · TEAM BUILD",
         title="WSF", metric="edge AI · safe routes · auto-SOS",
         desc="Learns risk zones from incident data, routes people around them, and fires SOS on its "
              "own — via route-drift checks and on-device audio sensing.",
         role="rebuilt location tracking + Supabase schema",
         stack=[("flutter", "Flutter"), ("fastapi", "FastAPI"), ("nextdotjs", "Next.js"),
                ("supabase", "Supabase"), ("mapbox", "Mapbox")],
         visual=vis_map),
    dict(file="card-isl", idx="03", accent=VIOLET, kicker="COMPUTER VISION · SOLO BUILD",
         title="ISL Recognition", metric="92.2% val acc · 296 signs · live",
         desc="Real-time Indian Sign Language from a webcam. BiLSTM + attention over MediaPipe "
              "landmarks, live sentences, and a Teach mode that learns new signs instantly.",
         role="model, API and UI — end to end",
         stack=[("tensorflow", "TensorFlow"), ("mediapipe", "MediaPipe"), ("fastapi", "FastAPI"),
                ("react", "React")],
         visual=vis_hand),
    dict(file="card-protecht", idx="04", accent=CYAN, kicker="SERVICE PLATFORM · TEAM BUILD",
         title="Pro-Techt", metric="vibe-coded with Lovable + Supabase",
         desc="One portal for consumers, partners and service centers: warranty tracking, OCR + "
              "barcode product capture, live chat and SLA analytics, all role-based.",
         role="integrated the team's feature work + docs",
         stack=[("react", "React"), ("typescript", "TypeScript"), ("vite", "Vite"),
                ("supabase", "Supabase"), ("tailwindcss", "Tailwind")],
         visual=vis_scan),
]


def card(c: dict) -> str:
    W, H = 480, 300
    acc = c["accent"]
    b = [
        '<defs><filter id="cglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<radialGradient id="cg" cx="1" cy="0" r=".9"><stop offset="0" stop-color="{acc}" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient></defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#cg)"/>',
        f'<text class="m" x="24" y="38" font-size="11.5" font-weight="700" fill="{acc}">{c["idx"]}</text>',
        f'<text class="m" x="50" y="38" font-size="10" letter-spacing="1.6" fill="{DIM}">{esc(c["kicker"])}</text>',
        f'<path d="M447 31l9-9m-6 0h6v6" stroke="{DIM}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<text class="s" x="22" y="94" font-size="40" fill="{TEXT}"{fit("serif", c["title"], 40)}>{esc(c["title"])}</text>',
        f'<text class="m" x="24" y="120" font-size="12" font-weight="500" fill="{acc}">{esc(c["metric"])}</text>',
        c["visual"](acc),
    ]
    lines = wrap(c["desc"], 57)
    assert len(lines) <= 3, (c["file"], lines)
    for i, ln in enumerate(lines):
        b.append(f'<text class="m" x="24" y="{178 + i * 19}" font-size="12.5" fill="{MUTED}">{esc(ln)}</text>')
    b.append(chevron(24, 245, acc).replace("l5 4.7-5 4.7", "l4.4 4.2-4.4 4.2"))
    b.append(f'<text class="m" x="38" y="245" font-size="12">{spans([("my part  ", DIM), (c["role"], TEXT)])}</text>')
    x, cw = 24.0, 10.5 * MONO_ADVANCE
    for slug, label in c["stack"]:
        has_icon = icon(slug, 0, 0, 12, TEXT) != ""
        w = 18 + (18 if has_icon else 0) + len(label) * cw
        if x + w > W - 24:
            break
        b.append(f'<rect x="{x:.1f}" y="260" width="{w:.1f}" height="22" rx="6" fill="{CHIP}" stroke="{LINE}"/>')
        tx = x + 9
        if has_icon:
            b.append(icon(slug, tx, 265, 12, MUTED))
            tx += 18
        b.append(f'<text class="m" x="{tx:.1f}" y="275" font-size="10.5" fill="{TEXT}">{esc(label)}</text>')
        x += w + 6
    return svg(W, H, "".join(b), css=CARD_CSS, fonts=("mono400", "mono500", "mono700", "serif"),
               title=f'{c["title"]} — {c["metric"]}')


# --------------------------------------------------------------------------- section headers

def header(idx: str, title: str, caption: str) -> str:
    W, H = 1000, 72
    b = [
        f'<defs><linearGradient id="hg" x1="0" x2="1"><stop offset="0" stop-color="{CYAN_MID}"/>'
        f'<stop offset="1" stop-color="{VIOLET_MID}"/></linearGradient>'
        f'<linearGradient id="hl" x1="0" x2="1"><stop offset="0" stop-color="{MUTED}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{MUTED}" stop-opacity=".08"/></linearGradient></defs>',
        f'<text class="m" x="2" y="42" font-size="13" font-weight="700" fill="{CYAN_MID}">{idx}</text>',
        f'<text class="m" x="27" y="42" font-size="13" fill="{MUTED}">/</text>',
        f'<text class="s" x="44" y="45" font-size="38" font-style="italic" fill="url(#hg)"{fit("serif-i", title, 38)}>{esc(title)}</text>',
        f'<text class="m" x="998" y="42" font-size="12" fill="{MUTED}" text-anchor="end">{esc(caption)}</text>',
        '<rect x="0" y="60" width="1000" height="1" fill="url(#hl)"/>',
        f'<rect class="run" x="0" y="59.5" width="64" height="2" rx="1" fill="url(#hg)"/>',
    ]
    css = (".run{animation:run 7s cubic-bezier(.6,0,.4,1) infinite}"
           "@keyframes run{0%{transform:translateX(-64px);opacity:0}10%{opacity:1}"
           "60%,100%{transform:translateX(1000px);opacity:0}}")
    return svg(W, H, "".join(b), css=css, fonts=("mono400", "mono700", "serif-i"), title=f"{idx} / {title}")


# --------------------------------------------------------------------------- stack

STACK = [
    ("LANGUAGES", [("python", "Python"), ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("dart", "Dart")]),
    ("ML · CV", [("tensorflow", "TensorFlow"), ("scikitlearn", "scikit-learn"), ("xgboost", "XGBoost"),
                 ("mediapipe", "MediaPipe"), ("opencv", "OpenCV"), ("pandas", "pandas"), ("numpy", "NumPy")]),
    ("BACKEND", [("fastapi", "FastAPI"), ("flask", "Flask"), ("express", "Express"), ("celery", "Celery"),
                 ("redis", "Redis")]),
    ("FRONTEND", [("react", "React"), ("nextdotjs", "Next.js"), ("vite", "Vite"), ("tailwindcss", "Tailwind"),
                  ("framer", "Framer Motion")]),
    ("MOBILE", [("flutter", "Flutter"), ("firebase", "Firebase"), ("mapbox", "Mapbox")]),
    ("DATA · INFRA", [("supabase", "Supabase"), ("mongodb", "MongoDB"), ("sqlite", "SQLite"), ("docker", "Docker"),
                      ("vercel", "Vercel"), ("githubactions", "GitHub Actions")]),
    ("VIBE STACK", [("claude", "Claude Code"), ("cursor", "Cursor"), ("antigravity", "Antigravity"),
                    ("googlegemini", "Gemini CLI"), ("codex", "Codex"), ("githubcopilot", "Copilot"),
                    ("lovable", "Lovable")]),
]


def stack() -> str:
    W = 1000
    top, rh = 26, 46
    H = top * 2 + rh * len(STACK) - 10
    b = [
        '<defs><linearGradient id="vg" x1="0" x2="1"><stop offset="0" stop-color="#22d3ee"/>'
        '<stop offset="1" stop-color="#a78bfa"/></linearGradient>'
        '<linearGradient id="band" x1="0" x2="1"><stop offset="0" stop-color="#a78bfa" stop-opacity=".14"/>'
        '<stop offset="1" stop-color="#22d3ee" stop-opacity=".03"/></linearGradient></defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>',
    ]
    n = 0
    for r, (label, items) in enumerate(STACK):
        yc = top + r * rh + 15
        vibe = label == "VIBE STACK"
        if vibe:
            b.append(f'<rect x="12" y="{yc - 21}" width="{W - 24}" height="42" rx="10" fill="url(#band)" '
                     f'stroke="url(#vg)" stroke-opacity=".35"/>')
        b.append(f'<text class="m" x="30" y="{yc + 4}" font-size="10.5" letter-spacing="1.8" '
                 f'fill="{"url(#vg)" if vibe else DIM}" font-weight="{700 if vibe else 400}">{label}</text>')
        x = 176.0
        for slug, name in items:
            w = 46 + len(name) * 12 * MONO_ADVANCE
            stroke = 'stroke="url(#vg)" stroke-opacity=".7"' if vibe else f'stroke="{LINE}"'
            b.append(f'<g class="in"{delay(0.1 + n * 0.022)}>'
                     f'<rect x="{x:.1f}" y="{yc - 14}" width="{w:.1f}" height="28" rx="8" fill="{CHIP}" {stroke}/>'
                     + icon(slug, x + 12, yc - 7, 14, "url(#vg)" if vibe else "#c9d1d9")
                     + f'<text class="m" x="{x + 34:.1f}" y="{yc + 4.2:.1f}" font-size="12" fill="{TEXT}">{esc(name)}</text></g>')
            x += w + 8
            n += 1
        assert x < W - 20, (label, x)
    return svg(W, H, "".join(b), fonts=("mono400", "mono700"), title="Tech stack")


# --------------------------------------------------------------------------- footer + buttons

def footer() -> str:
    W, H = 1000, 150
    FS, X, TX = 14, 40, 60
    CW = FS * MONO_ADVANCE
    segs = [("git", VIOLET, 700), (" commit -m ", TEXT), ('"let\'s build something real"', CYAN)]
    n = sum(len(s[0]) for s in segs)
    t0, per = 0.6, 0.035
    end = t0 + n * per
    kt = ";".join(f"{k:.4f}" for k in [0.0] + [(t0 + i * per) / end for i in range(n + 1)])
    widths = ";".join(["0"] + [f"{i * CW + 1:.1f}" for i in range(n)] + ["900"])
    b = [
        f'<defs><clipPath id="ft"><rect x="{TX - 2}" y="34" height="26" width="0">'
        f'<animate attributeName="width" dur="{end:.2f}s" fill="freeze" calcMode="discrete" keyTimes="{kt}" values="{widths}"/>'
        f'</rect></clipPath><radialGradient id="fg" cx="1" cy="1" r=".8"><stop offset="0" stop-color="#a78bfa" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient></defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#fg)"/>',
        chevron(X, 52),
        f'<text class="m" x="{TX}" y="52" font-size="{FS}" clip-path="url(#ft)">{spans(segs)}</text>',
        f'<text class="m in" x="{TX}" y="84" font-size="{FS}"{delay(end + 0.25)}>'
        f'{spans([("[main 2028] ", DIM), ("1 team changed, ", MUTED), ("1 engineer inserted(+)", GREEN, 700)])}</text>',
        f'<g class="fade"{delay(end + 0.6, 0.1)}>{chevron(X, 116)}'
        f'<rect class="blink" x="{TX}" y="{116 - 14}" width="{CW:.1f}" height="18" fill="{CYAN}" opacity=".85"/></g>',
    ]
    return svg(W, H, "".join(b), fonts=("mono400", "mono700"), title="git commit -m \"let's build something real\"")


def button(slug: str, label: str, accent: str) -> str:
    H = 48
    W = int(54 + len(label) * 13 * MONO_ADVANCE + 22)
    b = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>',
         icon(slug, 20, 15, 18, accent),
         f'<text class="m" x="52" y="29" font-size="13" font-weight="500" fill="{TEXT}">{esc(label)}</text>']
    return svg(W, H, "".join(b), fonts=("mono500",), title=label)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(),
        "h-shipped.svg": header("01", "shipped", "// four products, built with real people in mind"),
        "h-stack.svg": header("02", "stack", "// only what I've actually shipped with"),
        "h-telemetry.svg": header("03", "telemetry", "// rebuilt every night by a GitHub Action"),
        "h-connect.svg": header("04", "connect", "// fastest replies after midnight"),
        "stack.svg": stack(),
        "footer.svg": footer(),
        "btn-mail.svg": button("mail", "krishkavin7512@gmail.com", CYAN),
        "btn-linkedin.svg": button("linkedin", "LinkedIn", VIOLET),
        "btn-portfolio.svg": button("globe", "Portfolio", CYAN),
    }
    for c in CARDS:
        files[f'{c["file"]}.svg'] = card(c)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"{name:24} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
