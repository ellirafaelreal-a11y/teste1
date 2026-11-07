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
# On mark: stacked "o over n" symbol, reconstructed from reference images.
# All proportions are relative to the ring's outer diameter D and were measured
# on four independent copies of the logo (spread < 1 %).
# --------------------------------------------------------------------------

ON = {
    "ring_stroke": 0.228,   # radial thickness of the o
    "tab_width": 0.241,     # the 45 degree stem
    "tab_angle": 45.0,      # degrees, up-right
    "tab_end": 0.710,       # distance from ring centre to the tab's square end
    "gap": 0.115,           # o -> n vertical gap
    "n_width": 0.967,
    "n_height": 0.980,
    "n_stroke": 0.242,
}
ON_BODY = 1 + ON["gap"] + ON["n_height"]      # ring top -> n bottom, in D
ON_STROKE = (ON["ring_stroke"] + ON["n_stroke"]) / 2


def _circle(cx, cy, r, sweep):
    return (f"M{cx - r:.3f},{cy:.3f} A{r:.3f},{r:.3f} 0 1 {sweep} {cx + r:.3f},{cy:.3f} "
            f"A{r:.3f},{r:.3f} 0 1 {sweep} {cx - r:.3f},{cy:.3f} Z")


def _poly(pts):
    # orient polygon clockwise on screen (same winding as the outer circle)
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    if area < 0:
        pts = pts[::-1]
    return "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z"


def on_mark(x, baseline, body_h):
    """
    Stacked On symbol. `x` = left edge of the ring/n column, `baseline` = bottom
    of the n (y-down), `body_h` = ring top -> n bottom.
    Returns dict(o=path, n=path, D=..., width=column width, bbox=(l,t,r,b)).
    The tab is allowed to overhang the column to the upper right.
    """
    D = body_h / ON_BODY
    r = D / 2
    cx = x + r
    top = baseline - body_h
    cy = top + r
    r_in = r - ON["ring_stroke"] * D
    ring = _circle(cx, cy, r, 1) + " " + _circle(cx, cy, r_in, 0)
    a = math.radians(ON["tab_angle"])
    ux, uy = math.cos(a), -math.sin(a)          # along the tab (screen coords)
    vx, vy = math.sin(a), math.cos(a)           # across the tab
    hw = ON["tab_width"] * D / 2
    r0 = (r_in + r) / 2                          # starts inside the ring's stroke
    r1 = ON["tab_end"] * D
    tab = _poly([
        (cx + ux * r0 - vx * hw, cy + uy * r0 - vy * hw),
        (cx + ux * r1 - vx * hw, cy + uy * r1 - vy * hw),
        (cx + ux * r1 + vx * hw, cy + uy * r1 + vy * hw),
        (cx + ux * r0 + vx * hw, cy + uy * r0 + vy * hw),
    ])
    o = ring + " " + tab
    W = ON["n_width"] * D
    st = ON["n_stroke"] * D
    nx0 = cx - W / 2
    ntop = baseline - ON["n_height"] * D
    R = W / 2
    Ri = R - st
    n = (f"M{nx0:.3f},{baseline:.3f} V{ntop + R:.3f} "
         f"A{R:.3f},{R:.3f} 0 0 1 {nx0 + W:.3f},{ntop + R:.3f} V{baseline:.3f} "
         f"H{nx0 + W - st:.3f} V{ntop + R:.3f} "
         f"A{Ri:.3f},{Ri:.3f} 0 0 0 {nx0 + st:.3f},{ntop + R:.3f} V{baseline:.3f} Z")
    tab_top = cy + uy * r1 - vy * hw              # top-most corner
    tab_right = cx + ux * r1 + vx * hw            # right-most corner
    return {"o": o, "n": n, "D": D, "width": D, "stroke": ON_STROKE * D,
            "bbox": (x, tab_top, max(tab_right, x + D), baseline)}


_weight_cache = {}


def outfit_weight_for(stem_ratio, ref="I", ref_h=706.0):
    """Find the Outfit weight whose `ref` stem / ref_h equals stem_ratio."""
    key = (round(stem_ratio, 4), ref)
    if key in _weight_cache:
        return _weight_cache[key]
    lo, hi = 100.0, 900.0
    for _ in range(14):
        mid = (lo + hi) / 2
        b, _ = glyph_bounds(font(OUTFIT, wght=round(mid, 1)), ref)
        if (b[2] - b[0]) / ref_h < stem_ratio:
            lo = mid
        else:
            hi = mid
    w = round((lo + hi) / 2, 1)
    _weight_cache[key] = w
    return w


# --------------------------------------------------------------------------
# Lockups: the On symbol takes the place of the letters "on". It is used
# unaltered; the type is drawn to match it (same stroke, aligned heights).
# --------------------------------------------------------------------------

def lockup_lower(x=0, baseline=0, xh=100.0, mode="serve"):
    """
    'shelt' + On symbol.
    mode "serve": the symbol's n has the x-height and the letters take the
    n's stroke, so the o rises above the word like a ball toss.
    mode "fit": the whole symbol fits baseline -> ascender (letters thin).
    """
    f0 = font(OUTFIT, wght=700)
    if mode == "serve":
        D = xh / ON["n_height"]
        body = D * ON_BODY
        # letters: stem of 'l' == n stroke ; x-height of 'x' == xh
        target = ON["n_stroke"] * D / xh          # stem / x-height
        wght = _match_weight(lambda f: (glyph_bounds(f, "l")[0][2] - glyph_bounds(f, "l")[0][0])
                             / glyph_bounds(f, "x")[0][3], target)
    else:
        wght = 355.3
    f = font(OUTFIT, wght=wght)
    s = xh / glyph_bounds(f, "x")[0][3]
    if mode != "serve":
        asc = glyph_bounds(f, "l")[0][3] * s
        body = asc
        D = body / ON_BODY
    shelt, w = text_path(f, "shelt", x, baseline, s, tracking=10)
    mx = x + w + D * 0.16
    mk = on_mark(mx, baseline, body)
    left = x + glyph_bounds(f, "s")[0][0] * s
    l, t, r, b = mk["bbox"]
    return {"shelt": shelt, "o": mk["o"], "n": mk["n"], "wght": wght,
            "bbox": (left, t, r, b), "xh": xh, "D": D, "mark_bbox": mk["bbox"]}


def lockup_upper(x=0, baseline=0, cap=100.0, tracking=60, mode="serve"):
    """'SHELT' + On symbol (see lockup_lower for the modes)."""
    if mode == "serve":
        D = cap / ON["n_height"]
        body = D * ON_BODY
        target = ON["n_stroke"] * D / cap
        wght = _match_weight(lambda f: (glyph_bounds(f, "I")[0][2] - glyph_bounds(f, "I")[0][0])
                             / glyph_bounds(f, "H")[0][3], target)
    else:
        wght = 327.5
        body = cap
        D = cap / ON_BODY
    f = font(OUTFIT, wght=wght)
    s = cap / glyph_bounds(f, "H")[0][3]
    shelt, w = text_path(f, "SHELT", x, baseline, s, tracking=tracking)
    mx = x + w + tracking * s + D * 0.10
    mk = on_mark(mx, baseline, body)
    left = x + glyph_bounds(f, "S")[0][0] * s
    l, t, r, b = mk["bbox"]
    return {"shelt": shelt, "o": mk["o"], "n": mk["n"], "wght": wght,
            "bbox": (left, t, r, b), "cap": cap, "D": D, "mark_bbox": mk["bbox"]}


def _match_weight(measure, target):
    key = (measure.__code__.co_code, measure.__code__.co_consts, round(target, 4))
    if key in _weight_cache:
        return _weight_cache[key]
    lo, hi = 100.0, 900.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if measure(font(OUTFIT, wght=round(mid, 1))) < target:
            lo = mid
        else:
            hi = mid
    w = round((lo + hi) / 2, 1)
    _weight_cache[key] = w
    return w


# --------------------------------------------------------------------------
# Inline ("horizontal") lockups: the On symbol is un-stacked so its o and n sit
# side by side inside the word, each at the height of the surrounding letters.
# The o keeps its 45 degree tab; the n is the symbol's arch.
# --------------------------------------------------------------------------

def on_inline_o(x, baseline, h, overshoot=0.03):
    """o with tab, ring diameter = h*(1+overshoot), centred on the h band."""
    D = h * (1 + overshoot)
    r = D / 2
    cx = x + r
    cy = baseline - h / 2
    r_in = r - ON["ring_stroke"] * D
    ring = _circle(cx, cy, r, 1) + " " + _circle(cx, cy, r_in, 0)
    a = math.radians(ON["tab_angle"])
    ux, uy = math.cos(a), -math.sin(a)
    vx, vy = math.sin(a), math.cos(a)
    hw = ON["tab_width"] * D / 2
    r0 = (r_in + r) / 2
    r1 = ON["tab_end"] * D
    tab = _poly([
        (cx + ux * r0 - vx * hw, cy + uy * r0 - vy * hw),
        (cx + ux * r1 - vx * hw, cy + uy * r1 - vy * hw),
        (cx + ux * r1 + vx * hw, cy + uy * r1 + vy * hw),
        (cx + ux * r0 + vx * hw, cy + uy * r0 + vy * hw),
    ])
    top = cy + uy * r1 - vy * hw
    return ring + " " + tab, D, top


def on_inline_n(x, baseline, h):
    """The symbol's n (arch), height h on the baseline. Returns (path, width)."""
    Dn = h / ON["n_height"]
    W = ON["n_width"] * Dn
    st = ON["n_stroke"] * Dn
    ntop = baseline - h
    R = W / 2
    Ri = R - st
    d = (f"M{x:.3f},{baseline:.3f} V{ntop + R:.3f} "
         f"A{R:.3f},{R:.3f} 0 0 1 {x + W:.3f},{ntop + R:.3f} V{baseline:.3f} "
         f"H{x + W - st:.3f} V{ntop + R:.3f} "
         f"A{Ri:.3f},{Ri:.3f} 0 0 0 {x + st:.3f},{ntop + R:.3f} V{baseline:.3f} Z")
    return d, W


def lockup_inline(prefix, suffix, case="lower", h=100.0, tracking=None,
                  kern_in=0.0, kern_out=0.0):
    """
    prefix + o + n + suffix on one line. h = x-height (lower) or cap height (upper).
    Letter weight is matched to the symbol's n stroke.
    kern_in / kern_out: extra space (in h) before the o / after the n.
    """
    n_stroke = ON["n_stroke"] / ON["n_height"]       # stroke / h
    if case == "lower":
        wght = _match_weight(lambda f: (glyph_bounds(f, "l")[0][2] - glyph_bounds(f, "l")[0][0])
                             / glyph_bounds(f, "x")[0][3], n_stroke)
        f = font(OUTFIT, wght=wght)
        s = h / glyph_bounds(f, "x")[0][3]
        ref_o, ref_n = "o", "n"
        tracking = 6 if tracking is None else tracking
    else:
        wght = _match_weight(lambda f: (glyph_bounds(f, "I")[0][2] - glyph_bounds(f, "I")[0][0])
                             / glyph_bounds(f, "H")[0][3], n_stroke)
        f = font(OUTFIT, wght=wght)
        s = h / glyph_bounds(f, "H")[0][3]
        ref_o, ref_n = "O", "H"
        prefix, suffix = prefix.upper(), suffix.upper()
        tracking = 40 if tracking is None else tracking
    tr = tracking * s
    # side bearings borrowed from the font's own o / n so the rhythm matches
    ob, oadv = glyph_bounds(f, ref_o)
    nb, nadv = glyph_bounds(f, ref_n)
    o_lsb = ob[0] * s
    o_rsb = (oadv - ob[2]) * s
    n_lsb = nb[0] * s
    n_rsb = (nadv - nb[2]) * s
    parts = {}
    x = 0.0
    pre_d, w = text_path(f, prefix, x, 0, s, tracking=tracking) if prefix else ("", 0.0)
    parts["pre"] = pre_d
    x += w + (tr if prefix else 0) + o_lsb + kern_in * h
    o_d, D, o_top = on_inline_o(x, 0, h)
    parts["o"] = o_d
    o_x0 = x
    x += D + o_rsb + tr + n_lsb
    n_d, W = on_inline_n(x, 0, h)
    parts["n"] = n_d
    n_x1 = x + W
    x += W + n_rsb + tr + kern_out * h
    suf_d, w2 = text_path(f, suffix, x, 0, s, tracking=tracking) if suffix else ("", 0.0)
    parts["suf"] = suf_d
    left = glyph_bounds(f, prefix[0])[0][0] * s if prefix else 0.0
    if suffix:
        last = suffix[-1]
        lb, ladv = glyph_bounds(f, last)
        right = x + w2 - (ladv - lb[2]) * s
    else:
        right = x - n_rsb - tr - kern_out * h
    # vertical extent: ascenders / tab
    top = min(o_top, -max(glyph_bounds(f, c)[0][3] for c in (prefix + suffix) if c != " ") * s)
    bottom = max(-min(glyph_bounds(f, c)[0][1] for c in (prefix + suffix) if c != " ") * s,
                 (D - h) / 2)
    return {**parts, "bbox": (left, top, right, bottom), "wght": wght, "h": h,
            "on_span": (o_x0, n_x1)}


def inline_group(lk, k, ink, ink_on=None):
    l, t, _, _ = lk["bbox"]
    ink_on = ink_on or ink
    out = [f'<g transform="scale({k:.6f}) translate({-l:.4f},{-t:.4f})">']
    for key, col in (("pre", ink), ("o", ink_on), ("n", ink_on), ("suf", ink)):
        if lk.get(key):
            out.append(f'<path d="{lk[key]}" fill="{col}"/>')
    out.append("</g>")
    return "".join(out)


# --------------------------------------------------------------------------
# Vertical lockups: letters stacked top to bottom, so the On symbol's o and n
# keep their natural stacked order. Each glyph is centred on the vertical axis
# and the o / n take the same size and pitch as the letters.
# --------------------------------------------------------------------------

ON_O, ON_N = "\u24DE", "\u24DD"   # placeholder tokens for the symbol parts


def lockup_vertical(tokens, h=100.0, pitch=1.8):
    """tokens: e.g. ["F", ON_O, ON_N, "S", "E", "C", "A"]. h = cap height.
    Returns dict(letters=path, on=path, bbox, wght, centers)."""
    n_stroke = ON["n_stroke"] / ON["n_height"]
    wght = _match_weight(lambda f: (glyph_bounds(f, "I")[0][2] - glyph_bounds(f, "I")[0][0])
                         / glyph_bounds(f, "H")[0][3], n_stroke)
    f = font(OUTFIT, wght=wght)
    s = h / glyph_bounds(f, "H")[0][3]
    letters, on = [], []
    xs = []
    for i, tk in enumerate(tokens):
        base = i * pitch * h + h          # baseline of this row (first row top at y=0)
        if tk == ON_O:
            D = h * 1.03
            d, D, _ = on_inline_o(-D / 2, base, h)
            on.append(d)
            xs.append((-D / 2, D / 2 + 0.087 * D))
        elif tk == ON_N:
            W = ON["n_width"] * h / ON["n_height"]
            d, W = on_inline_n(-W / 2, base, h)
            on.append(d)
            xs.append((-W / 2, W / 2))
        else:
            b, _ = glyph_bounds(f, tk)
            cx = (b[0] + b[2]) / 2 * s
            d, _ = glyph_path(f, tk, -cx, base, s)
            letters.append(d)
            xs.append((b[0] * s - cx, b[2] * s - cx))
    left = min(a for a, _ in xs)
    right = max(b for _, b in xs)
    # the o's tab pokes above its row; include it in the bbox
    top = 0.0
    if tokens and tokens[0] == ON_O:
        top = -0.09 * h
    bottom = (len(tokens) - 1) * pitch * h + h * 1.02
    return {"letters": " ".join(letters), "on": " ".join(on), "bbox": (left, top, right, bottom),
            "wght": wght, "h": h, "pitch": pitch}


def vertical_group(lk, k, ink, ink_on=None, cx=0.0, top=0.0):
    """Place a vertical lockup with its axis at x=cx and its first row top at y=top."""
    ink_on = ink_on or ink
    return (f'<g transform="translate({cx:.3f},{top:.3f}) scale({k:.6f})">'
            f'<path d="{lk["letters"]}" fill="{ink}"/><path d="{lk["on"]}" fill="{ink_on}"/></g>')


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
        W = 190.0
        k = W / (r - l)
        H = (b - t) * k
        out[name] = svg_doc(W, H, lockup_group(lk, k, lk["bbox"], ink, inkon), bg)

    lu = lockup_upper()
    l, t, r, b = lu["bbox"]
    for name, ink, inkon in [
        ("lockup-uppercase-white-lime", "#F4F4F2", "#D4F53C"),
        ("lockup-uppercase-black", "#111111", "#111111"),
    ]:
        W = 250.0
        k = W / (r - l)
        H = (b - t) * k
        out[name] = svg_doc(W, H, lockup_group(lu, k, lu["bbox"], ink, inkon))

    # On mark alone
    mk = on_mark(0, 0, 100)
    l, t, r, b = mk["bbox"]
    out["on-mark-redraw"] = svg_doc(r - l, b - t, f'<g transform="translate({-l:.3f},{-t:.3f})"><path d="{mk["o"]}" fill="#111"/><path d="{mk["n"]}" fill="#111"/></g>')

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
