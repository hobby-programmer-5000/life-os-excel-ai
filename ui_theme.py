"""
=============================================================================
🎨 ALL-IN-ONE LIFE OS : Modern Minimal UI Theme Tokens & Lucide Stock Loader
=============================================================================
Implements a calm, restrained 60-30-10 neutral surface palette (Zinc/Obsidian)
inspired by Dieter Rams ("Less, but better"), Edward Tufte (minimal non-data
ink), Weiser & Brown (Calm Technology), and Nielsen Norman cognitive-load UX.

Renders crisp, anti-aliased UI icons directly from official ISC-licensed Lucide
SVG stock assets located in assets/icons/lucide/ (see THIRD-PARTY-NOTICES.md).
=============================================================================
"""

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw


# Restraint-driven 60-30-10 Neutral Dark Token System
THEME = {
    # 60% Matte Neutral Canvas & Structural Containers
    "bg": "#09090B",           # Obsidian canvas (Zinc 950)
    "card": "#111216",         # Elevated structural surface
    "surface_alt": "#18181B",  # Hover / input / secondary ghost fill (Zinc 900)
    "border": "#27272A",       # 1px hairline border (Zinc 800)
    "border_strong": "#3F3F46",# Subtle hover/focus border (Zinc 700)

    # 30% Monochrome Typography Hierarchy
    "text": "#F4F4F5",         # Primary legible off-white (Zinc 100)
    "sub": "#A1A1AA",          # Muted labels & metadata (Zinc 400)
    "muted": "#71717A",        # Placeholder & subtle hints (Zinc 500)

    # 10% Intentional Functional Semantic States
    "cta_bg": "#F4F4F5",       # Primary neutral CTA button fill
    "cta_fg": "#09090B",       # Primary neutral CTA button ink
    "accent": "#38BDF8",       # Subtle focus underline/ring only where needed
    "green": "#10B981",        # Checked / active live state ONLY
    "green_btn": "#059669",    # Done primary state fill (restrained emerald)
    "gold": "#D4D4D8",         # Monochrome pin/secondary label (replaces noisy yellow!)
    "warn_bg": "#18140E",      # Quiet amber hairline box strictly for security tips
    "warn_border": "#423315",
    "warn_fg": "#F59E0B",
}

_SVG_TOKEN_RE = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")


def _resource_root() -> Path:
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_lucide_dir() -> Path:
    return _resource_root() / "assets" / "icons" / "lucide"


def _hex_to_rgba(color: str, alpha: int = 255) -> tuple:
    h = color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def _draw_thick_polyline(draw: ImageDraw.ImageDraw, pts: list, fill: tuple, width: int):
    if len(pts) < 2:
        return
    draw.line(pts, fill=fill, width=width, joint="curve")
    r = width / 2.0
    for x, y in pts:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def _cubic_bezier(p0, p1, p2, p3, steps=18):
    out = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
        y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
        out.append((x, y))
    return out


def _svg_arc_to_points(p0, rx, ry, x_rot_deg, large_arc, sweep, p1, steps=24):
    """Convert SVG elliptical arc command to sampled polyline points."""
    x0, y0 = p0
    x1, y1 = p1
    if (x0 == x1 and y0 == y1) or rx == 0 or ry == 0:
        return [p0, p1]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(x_rot_deg % 360.0)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x0 - x1) / 2.0, (y0 - y1) / 2.0
    x1p = cos_p * dx2 + sin_p * dy2
    y1p = -sin_p * dx2 + cos_p * dy2

    lam = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if lam > 1.0:
        s = math.sqrt(lam)
        rx *= s
        ry *= s

    num = max(0.0, (rx * ry) ** 2 - (rx * y1p) ** 2 - (ry * x1p) ** 2)
    den = (rx * y1p) ** 2 + (ry * x1p) ** 2
    factor = math.sqrt(num / den) if den > 1e-9 else 0.0
    if large_arc == sweep:
        factor = -factor
    cxp = factor * (rx * y1p) / ry
    cyp = factor * -(ry * x1p) / rx
    cx = cos_p * cxp - sin_p * cyp + (x0 + x1) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (y0 + y1) / 2.0

    def angle(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        mag = math.hypot(ux, uy) * math.hypot(vx, vy)
        c = max(-1.0, min(1.0, dot / mag)) if mag > 1e-9 else 1.0
        ang = math.acos(c)
        return -ang if (ux * vy - uy * vx) < 0 else ang

    vx0, vy0 = (x1p - cxp) / rx, (y1p - cyp) / ry
    vx1, vy1 = (-x1p - cxp) / rx, (-y1p - cyp) / ry
    theta1 = angle(1.0, 0.0, vx0, vy0)
    dtheta = angle(vx0, vy0, vx1, vy1)
    if not sweep and dtheta > 0:
        dtheta -= 2 * math.pi
    elif sweep and dtheta < 0:
        dtheta += 2 * math.pi

    pts = []
    for i in range(steps + 1):
        th = theta1 + dtheta * (i / steps)
        xp = rx * math.cos(th)
        yp = ry * math.sin(th)
        pts.append((cos_p * xp - sin_p * yp + cx, sin_p * xp + cos_p * yp + cy))
    return pts


def _parse_svg_path_polylines(d: str) -> list:
    tokens = _SVG_TOKEN_RE.findall(d or "")
    polylines = []
    cur_poly = []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    last_ctrl = None
    i = 0
    cmd = ""

    def next_f():
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    def is_num():
        return i < len(tokens) and not tokens[i].isalpha()

    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
        elif cmd in ("M", "m"):
            cmd = "L" if cmd == "M" else "l"

        c_up = cmd.upper()
        rel = cmd.islower()

        if c_up == "M":
            if cur_poly:
                polylines.append(cur_poly)
            x, y = next_f(), next_f()
            if rel:
                x += cur[0]
                y += cur[1]
            cur = (x, y)
            start = cur
            cur_poly = [cur]
            last_ctrl = None
            while is_num():
                x, y = next_f(), next_f()
                if rel:
                    x += cur[0]
                    y += cur[1]
                cur = (x, y)
                cur_poly.append(cur)
        elif c_up == "L":
            while is_num():
                x, y = next_f(), next_f()
                if rel:
                    x += cur[0]
                    y += cur[1]
                cur = (x, y)
                cur_poly.append(cur)
            last_ctrl = None
        elif c_up == "H":
            while is_num():
                x = next_f() + (cur[0] if rel else 0.0)
                cur = (x, cur[1])
                cur_poly.append(cur)
            last_ctrl = None
        elif c_up == "V":
            while is_num():
                y = next_f() + (cur[1] if rel else 0.0)
                cur = (cur[0], y)
                cur_poly.append(cur)
            last_ctrl = None
        elif c_up == "C":
            while is_num():
                x1, y1, x2, y2, x, y = [next_f() for _ in range(6)]
                if rel:
                    x1 += cur[0]; y1 += cur[1]
                    x2 += cur[0]; y2 += cur[1]
                    x += cur[0]; y += cur[1]
                pts = _cubic_bezier(cur, (x1, y1), (x2, y2), (x, y))
                cur_poly.extend(pts[1:])
                last_ctrl = (x2, y2)
                cur = (x, y)
        elif c_up == "S":
            while is_num():
                if last_ctrl is not None:
                    x1 = 2 * cur[0] - last_ctrl[0]
                    y1 = 2 * cur[1] - last_ctrl[1]
                else:
                    x1, y1 = cur
                x2, y2, x, y = [next_f() for _ in range(4)]
                if rel:
                    x2 += cur[0]; y2 += cur[1]
                    x += cur[0]; y += cur[1]
                pts = _cubic_bezier(cur, (x1, y1), (x2, y2), (x, y))
                cur_poly.extend(pts[1:])
                last_ctrl = (x2, y2)
                cur = (x, y)
        elif c_up == "A":
            def next_flag():
                nonlocal i
                tok = tokens[i]
                flag_val = int(tok[0])
                if len(tok) > 1:
                    tokens[i] = tok[1:]
                else:
                    i += 1
                return flag_val

            while is_num():
                rx, ry, rot = next_f(), next_f(), next_f()
                la, sw = next_flag(), next_flag()
                x, y = next_f(), next_f()
                if rel:
                    x += cur[0]; y += cur[1]
                pts = _svg_arc_to_points(cur, rx, ry, rot, la, sw, (x, y))
                cur_poly.extend(pts[1:])
                cur = (x, y)
            last_ctrl = None
        elif c_up == "Z":
            if cur_poly:
                cur_poly.append(start)
                polylines.append(cur_poly)
                cur_poly = []
            cur = start
            last_ctrl = None
        else:
            break

    if cur_poly:
        polylines.append(cur_poly)
    return polylines


def render_lucide_icon(name: str, size: int = 16, color: str = "#F4F4F5", stroke_width: float = 2.0) -> Image.Image:
    """Render an ISC-licensed Lucide SVG from assets/icons/lucide/ into an anti-aliased RGBA Image."""
    svg_path = get_lucide_dir() / f"{name}.svg"
    if not svg_path.is_file():
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    scale = 8.0
    canvas_px = int(round(24 * scale))
    img = Image.new("RGBA", (canvas_px, canvas_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    rgba = _hex_to_rgba(color, 255)
    sw = max(2, int(round(stroke_width * scale)))

    root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
    for el in root:
        tag = el.tag.split("}")[-1]
        a = el.attrib
        if tag == "path":
            for poly in _parse_svg_path_polylines(a.get("d", "")):
                scaled = [(px * scale, py * scale) for px, py in poly]
                _draw_thick_polyline(draw, scaled, rgba, sw)
        elif tag == "line":
            pts = [
                (float(a["x1"]) * scale, float(a["y1"]) * scale),
                (float(a["x2"]) * scale, float(a["y2"]) * scale),
            ]
            _draw_thick_polyline(draw, pts, rgba, sw)
        elif tag == "circle":
            cx, cy, r = float(a["cx"]) * scale, float(a["cy"]) * scale, float(a["r"]) * scale
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=rgba, width=sw)
        elif tag == "rect":
            x, y = float(a.get("x", 0)) * scale, float(a.get("y", 0)) * scale
            w, h = float(a["width"]) * scale, float(a["height"]) * scale
            rx = float(a.get("rx", 0)) * scale
            if rx > 0:
                draw.rounded_rectangle((x, y, x + w, y + h), radius=rx, outline=rgba, width=sw)
            else:
                draw.rectangle((x, y, x + w, y + h), outline=rgba, width=sw)

    return img.resize((size, size), Image.Resampling.LANCZOS)


def get_tk_lucide_icon(widget_owner, name: str, size: int = 15, color: str = "#A1A1AA", bg: str = None, stroke_width: float = 2.0):
    """Return a cached tk.PhotoImage for the requested Lucide icon (safe in Tk & headless cleanup)."""
    import tkinter as tk
    from PIL import ImageTk

    cache = getattr(widget_owner, "_lucide_cache", None)
    if cache is None:
        cache = {}
        widget_owner._lucide_cache = cache

    key = (name, size, color, bg, stroke_width)
    if key in cache:
        return cache[key]

    fg_img = render_lucide_icon(name, size=size, color=color, stroke_width=stroke_width)
    if bg:
        base = Image.new("RGBA", (size, size), _hex_to_rgba(bg, 255))
        base.alpha_composite(fg_img)
        fg_img = base

    photo = ImageTk.PhotoImage(fg_img, master=widget_owner.root if hasattr(widget_owner, "root") else widget_owner)
    cache[key] = photo
    return photo
