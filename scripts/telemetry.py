#!/usr/bin/env python3
"""Builds the live telemetry card from the GitHub GraphQL API.

    GITHUB_TOKEN=... python scripts/telemetry.py dist/telemetry.svg [login]

Runs nightly in .github/workflows/profile.yml; stdlib only.
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.request
from datetime import date, datetime, timezone

from svgkit import BG, CYAN, DIM, GREEN, LINE, MUTED, PINK, TEXT, VIOLET, delay, esc, svg

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositoriesContributedTo(first: 1, includeUserRepositories: false,
        contributionTypes: [COMMIT, PULL_REQUEST, PULL_REQUEST_REVIEW, REPOSITORY]) { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}
"""

# notebooks and markup inflate byte counts without saying much about what I build;
# "PureBasic" is linguist misreading TensorFlow SavedModel .pb graphs
SKIP_LANGUAGES = {"Jupyter Notebook", "HTML", "CSS", "SCSS", "Makefile", "Dockerfile", "Batchfile",
                  "PowerShell", "Shell", "Procfile", "Mako", "PureBasic"}
WEEKDAYS = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"]
LANG_COLORS = [CYAN, VIOLET, PINK, "#fbbf24", "#34d399", "#60a5fa"]


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "kavin-telemetry"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def card(user: dict, login: str) -> str:
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [(date.fromisoformat(d["date"]), d["contributionCount"])
            for w in cal["weeks"] for d in w["contributionDays"]]
    total = cal["totalContributions"]
    # count active days per weekday, not contributions, so one huge day can't skew it
    per_weekday = [0] * 7
    for d, n in days:
        per_weekday[d.weekday()] += bool(n)
    fav = WEEKDAYS[max(range(7), key=per_weekday.__getitem__)]
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]][-52:]

    sizes: dict[str, int] = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name not in SKIP_LANGUAGES:
                sizes[name] = sizes.get(name, 0) + edge["size"]
    langs = sorted(sizes.items(), key=lambda kv: -kv[1])
    lang_total = sum(sizes.values()) or 1
    top = langs[:5]
    other = lang_total - sum(s for _, s in top)
    if other > 0:
        top.append(("Other", other))

    W, H = 1000, 300
    b = [
        '<defs><linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22d3ee" stop-opacity=".28"/>'
        '<stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>'
        '<linearGradient id="tg" x1="0" x2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>'
        '<radialGradient id="gl" cx="0" cy="0" r=".7"><stop offset="0" stop-color="#22d3ee" stop-opacity=".12"/>'
        '<stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>'
        '<filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="2.6" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<clipPath id="bar"><rect x="362" y="236" width="604" height="10" rx="5"/></clipPath></defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#gl)"/>',
        # left: headline numbers
        f'<text class="m" x="32" y="46" font-size="10.5" letter-spacing="1.8" fill="{DIM}">CONTRIBUTIONS · LAST YEAR</text>',
        f'<text class="s in" x="29" y="122" font-size="80" fill="{TEXT}"{delay(0.1)}>{total:,}</text>',
        f'<path d="M330 30V270" stroke="{LINE}"/>',
    ]
    shipped = sum(1 for r in user["repositories"]["nodes"] if r["name"].lower() != login.lower())
    stats = [
        ("repos shipped", str(shipped), CYAN),
        ("team repos", str(user["repositoriesContributedTo"]["totalCount"]), VIOLET),
        ("ships most on", fav, GREEN),
    ]
    for i, (k, v, c) in enumerate(stats):
        y = 178 + i * 30
        b.append(f'<g class="in"{delay(0.25 + i * 0.08)}>'
                 f'<text class="m" x="32" y="{y}" font-size="11.5" fill="{DIM}">{k}</text>'
                 f'<text class="m" x="300" y="{y}" font-size="13" font-weight="700" fill="{c}" text-anchor="end">{esc(v)}</text></g>')

    # right: weekly activity
    # sqrt scale keeps quiet weeks visible next to a spike
    x0, x1, yT, yB = 362, 966, 80, 196
    peak = math.sqrt(max(weeks) or 1)
    pts = [(x0 + (x1 - x0) * i / (len(weeks) - 1), yB - (yB - yT) * math.sqrt(n) / peak) for i, n in enumerate(weeks)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    updated = datetime.now(timezone.utc).strftime("%d %b %Y")
    b += [
        f'<text class="m" x="{x0}" y="46" font-size="10.5" letter-spacing="1.8" fill="{DIM}">CONTRIBUTIONS / WEEK</text>',
        f'<text class="m" x="{x1}" y="46" font-size="10.5" fill="{DIM}" text-anchor="end">updated {updated}</text>',
        f'<path d="M{x0} {yB}H{x1}" stroke="{LINE}"/>',
        f'<path class="fade" d="{line} L{x1} {yB} L{x0} {yB}Z" fill="url(#ar)"{delay(1.0, 0.8)}/>',
        f'<path class="draw" d="{line}" pathLength="1" stroke="{CYAN}" stroke-width="2" stroke-linejoin="round" '
        f'filter="url(#glow)"{delay(0.2, 1.6)}/>',
    ]
    pi = max(range(len(weeks)), key=weeks.__getitem__)
    px, py = pts[pi]
    anchor = "end" if px > x1 - 80 else "middle"
    b.append(f'<g class="in"{delay(1.6)}><circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{VIOLET}" filter="url(#glow)"/>'
             f'<text class="m" x="{px:.1f}" y="{py - 10:.1f}" font-size="11" font-weight="700" fill="{VIOLET}" '
             f'text-anchor="{anchor}">peak {weeks[pi]}/wk</text></g>')

    # right: languages
    b.append(f'<text class="m" x="{x0}" y="226" font-size="10.5" letter-spacing="1.8" fill="{DIM}">TOP LANGUAGES · BY BYTES</text>')
    b.append('<g clip-path="url(#bar)">')
    x = float(x0)
    for i, (name, size) in enumerate(top):
        w = (x1 - x0) * size / lang_total
        color = DIM if name == "Other" else LANG_COLORS[i % len(LANG_COLORS)]
        b.append(f'<rect class="fade" x="{x:.1f}" y="236" width="{w + 0.5:.1f}" height="10" fill="{color}"{delay(0.4 + i * 0.1)}/>')
        x += w
    b.append("</g>")
    lx = float(x0)
    for i, (name, size) in enumerate(top):
        color = DIM if name == "Other" else LANG_COLORS[i % len(LANG_COLORS)]
        pct = f"{100 * size / lang_total:.0f}%"
        b.append(f'<circle cx="{lx + 4:.1f}" cy="268" r="4" fill="{color}"/>'
                 f'<text class="m" x="{lx + 14:.1f}" y="272" font-size="11.5">'
                 f'<tspan fill="{TEXT}">{esc(name)}</tspan><tspan fill="{DIM}"> {pct}</tspan></text>')
        lx += 14 + (len(name) + len(pct) + 1) * 11.5 * 0.6 + 18

    return svg(W, H, "".join(b), fonts=("mono400", "mono700", "serif"),
               title=f"{total:,} contributions in the last year · {shipped} repos shipped")


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "dist/telemetry.svg"
    login = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("GITHUB_REPOSITORY_OWNER", "krishkavin7512")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("set GITHUB_TOKEN")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(card(fetch(login, token), login))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
