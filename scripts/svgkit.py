"""Shared palette, fonts, icons and CSS for the profile SVGs.

Every SVG embeds its fonts and icon paths, so it renders identically on
GitHub (which loads README images with no network access).
"""
from __future__ import annotations

import base64
import io
import os
import re
from functools import lru_cache
from html import escape, unescape
from pathlib import Path

# abspath, not resolve(): resolving can expand links into paths past Windows' MAX_PATH
ROOT = Path(os.path.abspath(__file__)).parent.parent
FONTS = ROOT / "vendor" / "fonts"
ICONS = ROOT / "vendor" / "icons"

BG, PANEL, CHIP, LINE = "#0a0d13", "#0e131b", "#111720", "#1e2633"
TEXT, MUTED, DIM = "#e6edf3", "#8b949e", "#545d6a"
CYAN, VIOLET, GREEN, PINK = "#22d3ee", "#a78bfa", "#3fb950", "#f472b6"
# mid-tones that stay readable on both GitHub light and dark backgrounds
CYAN_MID, VIOLET_MID = "#0891b2", "#8b5cf6"

MONO = "'JBM',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SERIF = "'IS','Iowan Old Style',Georgia,serif"
MONO_ADVANCE = 0.6  # JetBrains Mono advance width, in em

_FONT_FILES = {
    "mono400": ("JBM", 400, "normal", "jetbrains-mono-latin-400-normal.woff2"),
    "mono500": ("JBM", 500, "normal", "jetbrains-mono-latin-500-normal.woff2"),
    "mono700": ("JBM", 700, "normal", "jetbrains-mono-latin-700-normal.woff2"),
    "mono800": ("JBM", 800, "normal", "jetbrains-mono-latin-800-normal.woff2"),
    "serif": ("IS", 400, "normal", "instrument-serif-latin-400-normal.woff2"),
    "serif-i": ("IS", 400, "italic", "instrument-serif-latin-400-italic.woff2"),
}

# Icons simple-icons does not ship, drawn on the same 24x24 grid.
_CUSTOM_ICONS = {
    "lovable": "M12 21s-7.5-4.6-9.6-9.2C.9 8.5 3 4.5 6.8 4.5c2.1 0 3.6 1.1 5.2 3 1.6-1.9 3.1-3 5.2-3 3.8 0 5.9 4 4.4 7.3C19.5 16.4 12 21 12 21z",
    "antigravity": "M12 2.5 21 12h-5.4v9.5H8.4V12H3z",
    "codex": "M3 4h18a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zm2.3 4.2L4 9.5 6.6 12 4 14.5l1.3 1.3L9.2 12zM11 15h6v1.8h-6z",
    "xgboost": "M10 2h4v4h-4zM4 14h4v4H4zm12 0h4v4h-4zM11.2 6h1.6v3H18v5h-1.6v-3.4H7.6V14H6V9h5.2z",
    "mail": "M2 5.5A1.5 1.5 0 0 1 3.5 4h17A1.5 1.5 0 0 1 22 5.5v13a1.5 1.5 0 0 1-1.5 1.5h-17A1.5 1.5 0 0 1 2 18.5zm2.2.5 7.8 6.2L19.8 6zM4 8.2V18h16V8.2l-8 6.3z",
    "linkedin": "M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zm6.5 0h3.8v1.6h.06c.53-1 1.83-2 3.77-2 4.03 0 4.77 2.65 4.77 6.1V21h-4v-5.1c0-1.22-.02-2.8-1.7-2.8-1.71 0-1.97 1.33-1.97 2.7V21h-4z",
    "globe": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-2.9a15.6 15.6 0 0 0-1.4-3.6A8 8 0 0 1 18.9 8zM12 4.1c.8 1.1 1.5 2.4 1.9 3.9h-3.8c.4-1.4 1.1-2.8 1.9-3.9zM4.3 14a8.2 8.2 0 0 1 0-4h3.4a16.5 16.5 0 0 0 0 4zm.8 2h2.9c.3 1.3.8 2.5 1.4 3.6A8 8 0 0 1 5.1 16zM8 8H5.1a8 8 0 0 1 4.3-3.6C8.8 5.5 8.4 6.7 8 8zm4 11.9c-.8-1.1-1.5-2.4-1.9-3.9h3.8c-.4 1.4-1.1 2.8-1.9 3.9zM14.3 14H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4zm.3 5.6c.6-1.1 1.1-2.3 1.4-3.6h2.9a8 8 0 0 1-4.3 3.6zm1.7-5.6a16.5 16.5 0 0 0 0-4h3.4a8.2 8.2 0 0 1 0 4z",
}

BASE_CSS = """
.m{font-family:%(mono)s}.s{font-family:%(serif)s}
.in{animation:in .5s cubic-bezier(.2,.7,.2,1) both}
@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.fade{animation:fade .6s ease both}
@keyframes fade{from{opacity:0}to{opacity:1}}
.draw{stroke-dasharray:1;animation:draw 1s cubic-bezier(.4,0,.2,1) both}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
.blink{animation:blink 1.05s steps(1) infinite}
@keyframes blink{50%%{opacity:0}}
.flash{opacity:0;animation:flash .1s linear none}
@keyframes flash{from,to{opacity:1}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}
@keyframes pulse{0%%{transform:scale(1);opacity:.75}100%%{transform:scale(3.4);opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
""" % {"mono": MONO, "serif": SERIF}


def _subset(data: bytes, text: str) -> bytes:
    """Cut a woff2 down to the glyphs in text. Optional: needs fonttools + brotli."""
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        return data
    font = TTFont(io.BytesIO(data))
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    out = io.BytesIO()
    font.save(out)
    return out.getvalue()


@lru_cache(maxsize=None)
def _advances(key: str):
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return None
    font = TTFont(FONTS / _FONT_FILES[key][3])
    cmap, hmtx = font.getBestCmap(), font["hmtx"].metrics
    return {cp: hmtx[name][0] for cp, name in cmap.items()}, font["head"].unitsPerEm


def fit(key: str, text: str, size: float) -> str:
    """textLength pinned to the embedded font's width, so a fallback font
    (if a viewer blocks the embedded one) can't overflow the layout."""
    metrics = _advances(key)
    if metrics is None:
        return ""
    adv, upem = metrics
    width = sum(adv.get(ord(ch), upem // 2) for ch in text) * size / upem
    return f' textLength="{width:.1f}" lengthAdjust="spacingAndGlyphs"'


def font_css(*keys: str, text: str | None = None) -> str:
    out = []
    for key in keys:
        family, weight, style, file = _FONT_FILES[key]
        raw = (FONTS / file).read_bytes()
        data = base64.b64encode(_subset(raw, text) if text else raw).decode()
        out.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
        )
    return "".join(out)


@lru_cache(maxsize=None)
def icon_path(slug: str) -> str | None:
    if slug in _CUSTOM_ICONS:
        return _CUSTOM_ICONS[slug]
    file = ICONS / f"{slug}.svg"
    if not file.exists():
        return None
    match = re.search(r'<path d="([^"]+)"', file.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def icon(slug: str, x: float, y: float, size: float, fill: str, extra: str = "") -> str:
    d = icon_path(slug)
    if d is None:
        return ""
    rule = ' fill-rule="evenodd"' if slug == "codex" else ""
    return (
        f'<path transform="translate({x:.2f} {y:.2f}) scale({size / 24:.4f})" '
        f'd="{d}" fill="{fill}"{rule}{extra}/>'
    )


def esc(s: str) -> str:
    return escape(s, quote=False)


def mono_width(text: str, size: float) -> float:
    return len(text) * size * MONO_ADVANCE


def spans(segs) -> str:
    """segs: iterable of (text, fill) or (text, fill, weight)."""
    out = []
    for seg in segs:
        text, fill, weight = (seg + (None,))[:3]
        w = f' font-weight="{weight}"' if weight else ""
        out.append(f'<tspan fill="{fill}"{w}>{esc(text)}</tspan>')
    return "".join(out)


def delay(t: float, dur: float | None = None) -> str:
    style = f"animation-delay:{t:.2f}s"
    if dur is not None:
        style += f";animation-duration:{dur:.2f}s"
    return f' style="{style}"'


def wrap(text: str, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        lines.append(cur)
    return lines


def svg(width: int, height: int, body: str, css: str = "", fonts: tuple[str, ...] = (), title: str = "") -> str:
    head = f"<title>{esc(title)}</title>" if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" role="img">{head}'
        f"<style>{font_css(*fonts, text=unescape(re.sub(r'<[^>]*>', '', body)))}{BASE_CSS}{css}</style>{body}</svg>"
    )
