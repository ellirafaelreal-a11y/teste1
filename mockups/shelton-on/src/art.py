"""
Vector artwork for the Shelton x On training tee concepts.

Everything is generated as outlined SVG (no live fonts), so the files are
print/production ready. Units: 1 unit = 1 mm at the intended print size
unless noted otherwise.

The On mark is a faithful redraw for concept purposes. For production it
must be swapped for the official vector from On's brand portal.
"""
import math
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "assets", "fonts")
ART = os.path.join(ROOT, "art")

_font_cache = {}


def font(name, **axes):
    key = (name, tuple(sorted(axes.items())))
    if key not in _font_cache:
        f = TTFont(os.path.join(FONTS, name))
        if "fvar" in f and axes:
            f = instancer.instantiateVariableFont(f, axes)
        _font_cache[key] = f
    return _font_cache[key]


OUTFIT = "outfit-latin-wght-normal.woff2"
MONO = "jetbrains-mono-latin-700-normal.woff2"
MONO_R = "jetbrains-mono-latin-500-normal.woff2"


def glyph_path(f, ch, x, y, scale):
    """SVG path for glyph `ch`, baseline at (x, y) in y-down space."""
    gs = f.getGlyphSet()
    gname = f.getBestCmap()[ord(ch)]
    pen = SVGPathPen(gs)
    tpen = TransformPen(pen, (scale, 0, 0, -scale, x, y))
    gs[gname].draw(tpen)
    return pen.getCommands(), gs[gname].width * scale


def glyph_bounds(f, ch):
    gs = f.getGlyphSet()
    gname = f.getBestCmap()[ord(ch)]
    bp = BoundsPen(gs)
    gs[gname].draw(bp)
    return bp.bounds, gs[gname].width


def text_path(f, text, x, y, scale, tracking=0.0, kern=None):
    """Lay out a string glyph by glyph. tracking/kern in font units."""
    kern = kern or {}
    out = []
    cx = x
    prev = None
    for ch in text:
        if prev and (prev + ch) in kern:
            cx += kern[prev + ch] * scale
        if ch == " ":
            cx += glyph_bounds(f, " ")[1] * scale + tracking * scale
            prev = ch
            continue
        d, adv = glyph_path(f, ch, cx, y, scale)
        out.append(d)
        cx += adv + tracking * scale
        prev = ch
    return " ".join(out), cx - tracking * scale - x


def text_width(f, text, scale, tracking=0.0):
    w = 0
    for ch in text:
        w += glyph_bounds(f, ch)[1] * scale + tracking * scale
    return w - tracking * scale


# --------------------------------------------------------------------------
# On mark (redraw). Geometry expressed relative to the O diameter `D`.
# --------------------------------------------------------------------------

def ring_with_gap(cx, cy, r_out, r_in, gap_from_deg, gap_to_deg):
    """Annulus with an angular gap. Angles in maths convention (y up)."""
    def pt(r, deg):
        a = math.radians(deg)
        return cx + r * math.cos(a), cy - r * math.sin(a)

    # draw the arc from gap_to (counter-clockwise) all the way round to gap_from
    a0, a1 = gap_to_deg, gap_from_deg + 360
    sweep = a1 - a0
    large = 1 if sweep > 180 else 0
    p0 = pt(r_out, a0)
    p1 = pt(r_out, a1)
    q1 = pt(r_in, a1)
    q0 = pt(r_in, a0)
    return (
        f"M{p0[0]:.3f},{p0[1]:.3f} "
        f"A{r_out:.3f},{r_out:.3f} 0 {large} 0 {p1[0]:.3f},{p1[1]:.3f} "
        f"L{q1[0]:.3f},{q1[1]:.3f} "
        f"A{r_in:.3f},{r_in:.3f} 0 {large} 1 {q0[0]:.3f},{q0[1]:.3f} Z"
    )


def on_mark(x, baseline, D, f_n=None, n_scale=None):
    """
    Returns (o_path, n_path, total_width).
    x: left edge of the O. baseline: y of the baseline (y-down).
    D: outer diameter of the O.
    """
    f_n = f_n or font(OUTFIT, wght=700)
    stroke = D * 0.219
    r_out = D / 2
    r_in = r_out - stroke
    cx = x + r_out
    cy = baseline - r_out + D * 0.012  # tiny overshoot below baseline
    o = ring_with_gap(cx, cy, r_out, r_in, 32, 64)
    # n: x-height = 0.655 * D, sitting on the baseline
    if n_scale is None:
        n_scale = (D * 0.655) / 486.0
    (nb, nadv) = glyph_bounds(f_n, "n")
    gap = D * 0.085
    nx = x + D + gap - nb[0] * n_scale
    n_d, _ = glyph_path(f_n, "n", nx, baseline, n_scale)
    total = (nx + nb[2] * n_scale) - x
    return o, n_d, total


# --------------------------------------------------------------------------
# Lockups
# --------------------------------------------------------------------------

def lockup_lower(x=0, baseline=0, xh=64.0):
    """'shelt' + On mark, lowercase. xh = x-height in output units."""
    f = font(OUTFIT, wght=700)
    s = xh / 486.0
    shelt, w = text_path(f, "shelt", x, baseline, s, tracking=-6)
    D = xh / 0.655
    # optical spacing between t and O
    ox = x + w + D * 0.06
    o, n, wm = on_mark(ox, baseline, D, f, s)
    left = x + glyph_bounds(f, "s")[0][0] * s
    right = ox + wm
    top = baseline - D * 0.988
    bottom = baseline + D * 0.012
    return {"shelt": shelt, "o": o, "n": n, "bbox": (left, top, right, bottom)}


def lockup_upper(x=0, baseline=0, cap=70.0, tracking=34):
    """'SHELT' + On mark, uppercase. cap = cap height in output units."""
    f = font(OUTFIT, wght=700)
    s = cap / 706.0
    shelt, w = text_path(f, "SHELT", x, baseline, s, tracking=tracking)
    D = cap / 0.976
    ox = x + w + tracking * s + D * 0.03
    o, n, wm = on_mark(ox, baseline, D, f, (D * 0.655) / 486.0)
    left = x + glyph_bounds(f, "S")[0][0] * s
    right = ox + wm
    top = baseline - D * 0.988
    bottom = baseline + D * 0.012
    return {"shelt": shelt, "o": o, "n": n, "bbox": (left, top, right, bottom)}


def fit_lockup(builder, target_width, **kw):
    """Scale a lockup so its bbox is exactly target_width wide, origin at 0,0 top-left."""
    probe = builder(**kw)
    l, t, r, b = probe["bbox"]
    k = target_width / (r - l)
    return probe, k, (l, t, r, b)


def svg_doc(w, h, body, bg=None):
    bgrect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.3f} {h:.3f}" '
        f'width="{w:.3f}mm" height="{h:.3f}mm">{bgrect}{body}</svg>'
    )


def lockup_group(lk, k, bbox, ink, ink_on=None):
    l, t, _, _ = bbox
    ink_on = ink_on or ink
    return (
        f'<g transform="scale({k:.6f}) translate({-l:.4f},{-t:.4f})">'
        f'<path d="{lk["shelt"]}" fill="{ink}"/>'
        f'<path d="{lk["o"]}" fill="{ink_on}"/>'
        f'<path d="{lk["n"]}" fill="{ink_on}"/>'
        f"</g>"
    )


# --------------------------------------------------------------------------
# Concept 01 back: technical court drawing with a lefty slice serve
# --------------------------------------------------------------------------

def court_graphic(ink, width=96.0):
    """Full tennis court, top view, to scale (ITF dims), drawn `width` mm wide
    (doubles width). Returns (svg_body, w, h)."""
    m = width / 10.97  # mm per metre
    L = 23.77 * m
    W = 10.97 * m
    sw = 8.23 * m
    alley = (W - sw) / 2
    svc = 6.40 * m
    lw = 1.3  # line weight mm
    half = L / 2
    lines = []

    def rect(x, y, w, h):
        lines.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="none" stroke="{ink}" stroke-width="{lw}"/>')

    def line(x1, y1, x2, y2, extra=""):
        lines.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{ink}" stroke-width="{lw}" {extra}/>')

    rect(0, 0, W, L)  # doubles outline
    line(alley, 0, alley, L)
    line(W - alley, 0, W - alley, L)
    # service lines
    line(alley, half - svc, W - alley, half - svc)
    line(alley, half + svc, W - alley, half + svc)
    # centre service line
    line(W / 2, half - svc, W / 2, half + svc)
    # centre marks
    line(W / 2, 0, W / 2, 0.4 * m * 2)
    line(W / 2, L, W / 2, L - 0.4 * m * 2)
    # net (thicker, dashed to suggest mesh)
    lines.append(f'<line x1="{-0.914*m:.3f}" y1="{half:.3f}" x2="{W+0.914*m:.3f}" y2="{half:.3f}" stroke="{ink}" stroke-width="{lw*1.9}"/>')
    # net posts
    for px in (-0.914 * m, W + 0.914 * m):
        lines.append(f'<circle cx="{px:.3f}" cy="{half:.3f}" r="{lw*1.3:.3f}" fill="{ink}"/>')

    # Lefty serving from the AD court (server's left), bottom end of drawing.
    sx, sy = W / 2 - 0.9 * m, L + 0.25 * m
    # Target: wide in the opponent's AD service box (top-right box from viewer)
    tx, ty = W - alley - 0.35 * m, half - svc + 0.55 * m
    # Ball leaves wide after the bounce (slice kicks away)
    ex, ey = W + 1.8 * m, half - svc - 2.6 * m
    # trajectory as dotted curve (slight slice curl)
    c1x, c1y = sx + 1.6 * m, sy - 6.0 * m
    c2x, c2y = tx + 0.3 * m, ty + 6.5 * m
    lines.append(
        f'<path d="M{sx:.3f},{sy:.3f} C{c1x:.3f},{c1y:.3f} {c2x:.3f},{c2y:.3f} {tx:.3f},{ty:.3f}" '
        f'fill="none" stroke="{ink}" stroke-width="{lw*0.95}" stroke-dasharray="0.01 2.4" stroke-linecap="round"/>'
    )
    lines.append(
        f'<path d="M{tx:.3f},{ty:.3f} Q{tx+1.2*m:.3f},{ty-1.0*m:.3f} {ex:.3f},{ey:.3f}" '
        f'fill="none" stroke="{ink}" stroke-width="{lw*0.95}" stroke-dasharray="0.01 2.4" stroke-linecap="round"/>'
    )
    # bounce mark (ball)
    lines.append(f'<circle cx="{tx:.3f}" cy="{ty:.3f}" r="{lw*2.3:.3f}" fill="{ink}"/>')
    lines.append(f'<circle cx="{tx:.3f}" cy="{ty:.3f}" r="{lw*4.6:.3f}" fill="none" stroke="{ink}" stroke-width="{lw*0.6}"/>')
    # server marker (small cross)
    k = 1.8
    line(sx - k, sy - k, sx + k, sy + k)
    line(sx - k, sy + k, sx + k, sy - k)

    # annotations (outlined mono)
    fm = font(MONO)
    fr = font(MONO_R)
    ts = 3.0 / 730  # ~3 mm cap height for labels
    def label(txt, x, y, f=fr, size=ts, anchor="start"):
        d, w = text_path(f, txt, 0, 0, size)
        if anchor == "end":
            x -= w
        elif anchor == "middle":
            x -= w / 2
        lines.append(f'<path transform="translate({x:.3f},{y:.3f})" d="{d}" fill="{ink}"/>')

    lx = W + 1.35 * m
    ly = ty + 1.4 * m
    line(tx + lw * 4.6, ty + lw * 2.0, lx - 1.2, ly - 3.6, 'stroke-width="0.6"')
    label("LEFTY SLICE", lx, ly, fm, 3.3 / 730)
    label("AD COURT / WIDE", lx, ly + 5.4, fr, 2.7 / 730)
    label("23.77 M", -3.6, L / 2 + 18, fr, 2.6 / 730, "end")
    label("10.97 M", W / 2, L + 9.5, fr, 2.6 / 730, "middle")
    body = "".join(lines)
    return body, W, L


# --------------------------------------------------------------------------
# Concept 02 back: CALL ENDED.
# --------------------------------------------------------------------------

def handset_icon(cx, cy, size, fill):
    """Classic telephone receiver lying flat - the universal 'hang up' glyph."""
    s = size / 100.0
    d = (
        "M4,57 C4,47 8,40 16,35 C32,25 68,25 84,35 C92,40 96,47 96,57 "
        "L95,62 C94.5,66 91,68 87,67 L71,63.5 C67.5,62.7 65.5,59.5 66,56 "
        "L67,50 C56,46 44,46 33,50 L34,56 C34.5,59.5 32.5,62.7 29,63.5 "
        "L13,67 C9,68 5.5,66 5,62 Z"
    )
    return (
        f'<g transform="translate({cx - 50*s:.3f},{cy - 47*s:.3f}) scale({s:.4f})">'
        f'<path d="{d}" fill="{fill}"/></g>'
    )


def call_ended_graphic(ink, accent, width=270.0):
    f8 = font(OUTFIT, wght=800)
    fm = font(MONO)
    fr = font(MONO_R)
    parts = []
    # headline
    cap = 46.0
    s = cap / 709.0
    tr = 18
    w_head = text_width(f8, "CALL ENDED.", s, tr)
    k = width / w_head
    s *= k
    cap *= k
    head, _ = text_path(f8, "CALL ENDED.", 0, 0, s, tracking=tr)
    # icon above, centered
    icon_d = cap * 1.25
    icon_cy = -cap - 20 - icon_d / 2
    parts.append(f'<circle cx="{width/2:.3f}" cy="{icon_cy:.3f}" r="{icon_d/2:.3f}" fill="{accent}"/>')
    parts.append(handset_icon(width / 2, icon_cy + icon_d * 0.03, icon_d * 0.70, "#18191B"))
    left_b = glyph_bounds(f8, "C")[0][0] * s
    parts.append(f'<path transform="translate({-left_b:.3f},0)" d="{head}" fill="{ink}"/>')
    # sub line: duration + name
    ss = 3.6 / 730
    sub = "BEN SHELTON  —  LEFTY  —  ON TENNIS"
    sub = sub.replace("—", "-")
    d_sub, w_sub = text_path(fm, sub, 0, 0, ss, tracking=120)
    parts.append(f'<path transform="translate({(width - w_sub)/2:.3f},{18:.3f})" d="{d_sub}" fill="{ink}"/>')
    # thin rule pair framing the sub line
    y_rule = 18 - 3.6 / 2 * 0.8
    gap = 6
    parts.append(f'<rect x="0" y="{y_rule-0.5:.3f}" width="{(width - w_sub)/2 - gap:.3f}" height="0.9" fill="{accent}"/>')
    parts.append(f'<rect x="{(width + w_sub)/2 + gap:.3f}" y="{y_rule-0.5:.3f}" width="{(width - w_sub)/2 - gap:.3f}" height="0.9" fill="{accent}"/>')
    top = icon_cy - icon_d / 2
    bottom = 22
    return "".join(parts), (0, top, width, bottom)


def tiny_text(txt, ink, cap_mm=3.0, f=None, tracking=80):
    f = f or font(MONO)
    s = cap_mm / 730
    d, w = text_path(f, txt, 0, 0, s, tracking=tracking)
    return d, w, cap_mm


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------

def export_all():
    os.makedirs(ART, exist_ok=True)
    out = {}

    # Lockup lowercase, 200 mm wide, black + white versions
    lk = lockup_lower()
    l, t, r, b = lk["bbox"]
    for name, ink, inkon, bg in [
        ("lockup-lowercase-black", "#111111", "#111111", None),
        ("lockup-lowercase-white", "#F4F4F2", "#F4F4F2", None),
    ]:
        W = 200.0
        k = W / (r - l)
        H = (b - t) * k
        out[name] = svg_doc(W, H, lockup_group(lk, k, lk["bbox"], ink, inkon), bg)

    lu = lockup_upper()
    l, t, r, b = lu["bbox"]
    for name, ink, inkon in [
        ("lockup-uppercase-white-lime", "#F4F4F2", "#D4F53C"),
        ("lockup-uppercase-black", "#111111", "#111111"),
    ]:
        W = 260.0
        k = W / (r - l)
        H = (b - t) * k
        out[name] = svg_doc(W, H, lockup_group(lu, k, lu["bbox"], ink, inkon))

    # On mark alone
    o, n, wm = on_mark(0, 100, 100)
    out["on-mark-redraw"] = svg_doc(wm, 101.2, f'<path d="{o}" fill="#111"/><path d="{n}" fill="#111"/>')

    body, W, L = court_graphic("#111111")
    pad = 12
    out["back-court-black"] = svg_doc(W + 2 * pad + 20, L + 2 * pad + 6,
                                      f'<g transform="translate({pad+12},{pad})">{body}</g>')

    body, bb = call_ended_graphic("#F4F4F2", "#D4F53C")
    l, t, r, b = bb
    out["back-call-ended"] = svg_doc(r - l, b - t, f'<g transform="translate({-l},{-t})">{body}</g>')

    for name, svg in out.items():
        with open(os.path.join(ART, name + ".svg"), "w") as fh:
            fh.write(svg)
    return out


if __name__ == "__main__":
    o = export_all()
    print("\n".join(sorted(o)))
