"""
Build pipeline: vector maps -> Chromium raster -> numpy shading/compositing.

    python3 src/compose.py

Writes build/ (intermediate) and output/ (final renders).
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art  # noqa: E402
import tee  # noqa: E402

ROOT = art.ROOT
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "output")
SCALE = 2.4            # px per mm
N = int(1000 * SCALE)  # render size

# ------------------------------------------------------------------ colours --
INK_BLACK = "#141414"
INK_WHITE = "#F3F3EF"
LIME = "#D4F53C"

CONCEPTS = {
    "01": {
        "name": "BASELINE",
        "tee": "#EEECE6",   # undyed white
        "spec": 0.020,
        "fresnel": 0.0,
        "label_ink": "#9a9890",
    },
    "02": {
        "name": "CALL ENDED",
        "tee": "#161719",   # black
        "spec": 0.075,
        "fresnel": 0.045,
        "label_ink": "#5d5f62",
    },
}


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def srgb2lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin2srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


# ---------------------------------------------------------------- print art --

def print_svg(concept, view):
    """Artwork placed in tee coordinates (mm)."""
    x0, y0, w0, h0 = tee.VB
    g = []
    if concept == "01" and view == "front":
        lk = art.lockup_lower()
        l, t, r, b = lk["bbox"]
        W = 200.0
        k = W / (r - l)
        g.append(f'<g transform="translate({500 - W/2:.3f},322)">{art.lockup_group(lk, k, lk["bbox"], INK_BLACK)}</g>')
        g.append(sleeve_hit("LEFTY", INK_BLACK))
    elif concept == "01" and view == "back":
        g.append(neck_mark(INK_BLACK))
        body, W, L = art.court_graphic(INK_BLACK, width=100.0)
        top = 262
        g.append(f'<g transform="translate({500 - W/2:.3f},{top})">{body}</g>')
        d, w, _ = art.tiny_text("SERVE MAP / B. SHELTON", INK_BLACK, cap_mm=3.4, tracking=110)
        g.append(f'<path transform="translate({500 - w/2:.3f},{top + L + 24:.3f})" d="{d}" fill="{INK_BLACK}"/>')
    elif concept == "02" and view == "front":
        lu = art.lockup_upper()
        l, t, r, b = lu["bbox"]
        W = 276.0
        k = W / (r - l)
        g.append(f'<g transform="translate({500 - W/2:.3f},326)">{art.lockup_group(lu, k, lu["bbox"], INK_WHITE, LIME)}</g>')
        g.append(sleeve_hit("LEFTY", LIME))
    elif concept == "02" and view == "back":
        g.append(neck_mark(LIME))
        body, bb = art.call_ended_graphic(INK_WHITE, LIME, width=262.0)
        l, t, r, b = bb
        g.append(f'<g transform="translate({500 - (r-l)/2:.3f},{252 - t:.3f})">{body}</g>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w0} {h0}">'
        f'{"".join(g)}</svg>'
    )


def neck_mark(ink):
    o, n, wm = art.on_mark(0, 0, 13.0)
    W = 20.0
    k = W / wm
    return (
        f'<g transform="translate({500 - W/2:.3f},{230:.3f}) scale({k:.4f})">'
        f'<path d="{o}" fill="{ink}"/><path d="{n}" fill="{ink}"/></g>'
    )


def sleeve_hit(txt, ink):
    """Small text running down the wearer's left sleeve (image right on the front)."""
    d, w, cap = art.tiny_text(txt, ink, cap_mm=5.2, tracking=160)
    # sleeve axis: shoulder point (730,225) -> cuff centre (853,414); angle ~ 35 deg (sleeve top direction)
    cx, cy = 818, 338
    return (
        f'<g transform="translate({cx},{cy}) rotate(35) translate({-w/2:.3f},{cap/2:.3f})">'
        f'<path d="{d}" fill="{ink}"/></g>'
    )


def neck_label_svg(concept):
    """Printed care label inside the back neck (front view only)."""
    ink = CONCEPTS[concept]["label_ink"]
    x0, y0, w0, h0 = tee.VB
    o, n, wm = art.on_mark(0, 0, 9.0)
    k = 14.0 / wm
    d, w, _ = art.tiny_text("M", ink, cap_mm=4.0, tracking=0)
    d2, w2, _ = art.tiny_text("ON TENNIS", ink, cap_mm=1.8, tracking=120)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w0} {h0}">'
        f'<g transform="translate({500 - 7:.3f},{197:.3f}) scale({k:.4f})"><path d="{o}" fill="{ink}"/><path d="{n}" fill="{ink}"/></g>'
        f'<path transform="translate({500 - w/2:.3f},{211:.3f})" d="{d}" fill="{ink}"/>'
        f'<path transform="translate({500 - w2/2:.3f},{217:.3f})" d="{d2}" fill="{ink}"/>'
        f"</svg>"
    )


# ------------------------------------------------------------------ raster --

def rasterise(jobs):
    jp = os.path.join(BUILD, "jobs.json")
    with open(jp, "w") as fh:
        json.dump(jobs, fh)
    subprocess.run(["node", os.path.join(ROOT, "src", "shot.mjs"), jp], check=True,
                   stdout=subprocess.DEVNULL)


def load_gray(p, use_alpha=False):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if use_alpha:
        return im[..., 3].astype(np.float32) / 255.0  # alpha
    if im.ndim == 3 and im.shape[2] == 4:
        im = im[..., :3]
    if im.ndim == 3:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    return im.astype(np.float32) / 255.0


def load_rgba(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0
    rgb = im[..., [2, 1, 0]]
    a = im[..., 3]
    return rgb, a


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def dist(mask):
    m = (mask > 0.5).astype(np.uint8)
    return cv2.distanceTransform(m, cv2.DIST_L2, 5).astype(np.float32)


def cloth_warp(seed, amp_px=3.2):
    """Low-frequency displacement so edges/seams are not machine-perfect."""
    rng = np.random.default_rng(seed)
    f = []
    for _ in range(2):
        n = cv2.GaussianBlur(rng.standard_normal((N // 16, N // 16)).astype(np.float32), (0, 0), 2.2)
        n = cv2.resize(n, (N, N), interpolation=cv2.INTER_CUBIC)
        f.append(n / (np.abs(n).max() + 1e-6) * amp_px)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    return xx + f[0], yy + f[1]


def fabric_texture(seed):
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((N, N)).astype(np.float32)
    knit = cv2.GaussianBlur(n, (0, 0), sigmaX=0.6, sigmaY=1.5)
    knit /= knit.std() + 1e-6
    blot = cv2.GaussianBlur(rng.standard_normal((N // 8, N // 8)).astype(np.float32), (0, 0), 3)
    blot = cv2.resize(blot, (N, N), interpolation=cv2.INTER_CUBIC)
    blot /= blot.std() + 1e-6
    # faint horizontal course lines of a jersey knit
    yy = np.arange(N, dtype=np.float32)[:, None]
    course = np.sin(yy * 2 * np.pi / 2.1) * 0.25
    return knit * 0.7 + blot * 0.12 + course


# --------------------------------------------------------------- shading ----

LUMPY = 0.010


def shade(view, M):
    """Return diffuse D, spec S, rim r (0 at edge -> 1 inside) for a view."""
    H = W = N
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    xm = xx / SCALE + tee.VB[0]
    ym = yy / SCALE + tee.VB[1]

    D = np.zeros((H, W), np.float32)
    rim_all = np.zeros((H, W), np.float32)

    # per part rim falloff (cylindrical volume)
    parts = [("body", 95), ("sleeveL", 40), ("sleeveR", 40), ("collar", 6)]
    if view == "front":
        parts += [("backcollar", 5)]
    for name, R in parts:
        m = M[name]
        d = dist(m) / SCALE
        s = smoothstep(0, R, d)
        prof = 0.58 + 0.42 * (1 - (1 - s) ** 2.2)
        if name == "collar":
            prof = (0.84 + 0.14 * s) if view == "front" else (0.93 + 0.07 * s)
        if name == "backcollar":
            prof = 0.58 + 0.14 * s
        D += m * prof
        rim_all += m * s

    # cylinder across the torso + key light from upper left
    cyl = 1 - 0.10 * ((xm - 492) / 260) ** 2
    light = 1 + 0.06 * (500 - xm) / 260 + 0.05 * (540 - ym) / 380
    D *= cyl * light

    # ambient occlusion: sleeves shading the torso near the armpits,
    # body shading the sleeve undersides, collar rib casting onto the chest
    sleeves = np.clip(M["sleeveL"] + M["sleeveR"], 0, 1)
    near_pit = smoothstep(300, 430, ym) * (1 - smoothstep(520, 640, ym))
    ao_body = cv2.GaussianBlur(sleeves, (0, 0), 9 * SCALE) * near_pit
    ao_sleeve = cv2.GaussianBlur(M["body"], (0, 0), 7 * SCALE) * smoothstep(330, 470, ym)
    D *= 1 - 0.55 * ao_body * M["body"]
    D *= 1 - 0.35 * ao_sleeve * sleeves
    # soft uneven cloth surface
    rng = np.random.default_rng(3 if view == "front" else 5)
    lumpy = cv2.GaussianBlur(rng.standard_normal((N // 6, N // 6)).astype(np.float32), (0, 0), 4)
    lumpy = cv2.resize(lumpy, (N, N), interpolation=cv2.INTER_CUBIC)
    lumpy /= lumpy.std() + 1e-6
    D *= 1 + LUMPY * lumpy

    if view == "front":
        mi = M["inside"]
        di = dist(mi) / SCALE
        # inside back of the shirt: dim, brighter towards the top, shadowed by the front collar
        t = np.clip((ym - 179) / 70.0, 0, 1)
        inside = (0.46 - 0.22 * t) * (0.75 + 0.25 * smoothstep(0, 8, di))
        D = D * (1 - mi) + inside * mi

    F = M["folds"] - 0.5
    D = D + F * 0.80 * (M["sil"])
    D *= 1 - 0.55 * M["seams"]
    D += 0.10 * M["hilite"]

    # spec: fold crests + broad chest highlight + shoulders
    crest = np.clip(F, 0, None) * 2.0
    broad = np.exp(-(((xm - 410) / 170) ** 2 + ((ym - 390) / 210) ** 2))
    S = crest * 0.9 + broad * 0.45 + 0.6 * M["hilite"]
    S *= M["sil"]
    return np.clip(D, 0, 1.3), S, rim_all


def composite(concept, view, M, prints):
    cfg = CONCEPTS[concept]
    D, S, rim = shade(view, M)
    sil = M["sil"]
    tex = fabric_texture(seed=7 if view == "front" else 11)

    alb = srgb2lin(hex2rgb(cfg["tee"]))
    col = alb[None, None, :] * D[..., None] + (cfg["spec"] * S)[..., None]
    col += (cfg["fresnel"] * (1 - rim) * sil)[..., None]
    col *= (1 + 0.018 * tex)[..., None]

    # ---- prints: displaced by the fold relief, lit by the same light ----
    relief = cv2.GaussianBlur(M["folds"], (0, 0), 5)
    gx = cv2.Sobel(relief, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(relief, cv2.CV_32F, 0, 1, ksize=5)
    k = 5.0 / (np.abs(np.stack([gx, gy])).max() + 1e-6)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    mapx = xx - gx * k
    mapy = yy - gy * k

    printable = np.clip(M["body"] + M["sleeveL"] + M["sleeveR"], 0, 1)
    for p in prints:
        rgb, a = p["rgb"], p["a"]
        rgb = cv2.remap(rgb, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        a = cv2.remap(a, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        clipm = M["inside"] if p.get("inside") else printable
        a = a * clipm
        ink = srgb2lin(np.clip(rgb, 0, 1))
        # soft-hand ink: fabric grain shows through a little
        a = a * np.clip(p.get("opacity", 0.97) + p.get("grain", 0.03) * tex, 0, 1)
        ink_lit = ink * D[..., None] + (p.get("spec", 0.03) * S)[..., None]
        ink_lit *= (1 + 0.03 * tex)[..., None]
        col = col * (1 - a[..., None]) + ink_lit * a[..., None]

    out = lin2srgb(col)
    # grain in display space
    out = out + (tex * 0.004)[..., None]
    out = np.clip(out, 0, 1)

    # drop shadow + contact shadow
    def shifted_blur(m, dy, sigma):
        M2 = np.float32([[1, 0, 0], [0, 1, dy]])
        sh = cv2.warpAffine(m, M2, (N, N))
        return cv2.GaussianBlur(sh, (0, 0), sigma)

    sh = 0.30 * shifted_blur(sil, 30, 34) + 0.18 * shifted_blur(sil, 8, 9)
    sh = np.clip(sh, 0, 0.42)
    a_out = sil + sh * (1 - sil)
    rgb_out = (out * sil[..., None]) / np.maximum(a_out, 1e-6)[..., None]
    rgba = np.dstack([rgb_out, a_out])
    return rgba


def save_rgba(path, rgba):
    im = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(path, im[..., [2, 1, 0, 3]])


def flatten(rgba, bg_hex):
    bg = hex2rgb(bg_hex)
    a = rgba[..., 3:4]
    return rgba[..., :3] * a + bg[None, None, :] * (1 - a)


def main():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    art.export_all()

    jobs = []
    maps = {}
    for view in ("front", "back"):
        paths = tee.write_maps(os.path.join(BUILD, "maps"), view)
        maps[view] = {}
        for k, svg in paths.items():
            png = svg[:-4] + ".png"
            transparent = k in ("seams", "hilite")
            jobs.append({"in": svg, "out": png, "w": 1000, "h": 1000, "scale": SCALE,
                         "transparent": transparent})
            maps[view][k] = png

    prints = {}
    for c in CONCEPTS:
        for view in ("front", "back"):
            sp = os.path.join(BUILD, f"print-{c}-{view}.svg")
            with open(sp, "w") as fh:
                fh.write(print_svg(c, view))
            pp = sp[:-4] + ".png"
            jobs.append({"in": sp, "out": pp, "w": 1000, "h": 1000, "scale": SCALE, "transparent": True})
            prints[(c, view)] = [{"file": pp, "opacity": 0.99 if c == "01" else 0.955,
                                  "grain": 0.008 if c == "01" else 0.03,
                                  "spec": 0.012 if c == "01" else 0.03}]
        lp = os.path.join(BUILD, f"label-{c}.svg")
        with open(lp, "w") as fh:
            fh.write(neck_label_svg(c))
        jobs.append({"in": lp, "out": lp[:-4] + ".png", "w": 1000, "h": 1000, "scale": SCALE, "transparent": True})
        prints[(c, "front")].insert(0, {"file": lp[:-4] + ".png", "inside": True, "opacity": 0.9, "spec": 0.0})

    rasterise(jobs)

    for view in ("front", "back"):
        M = {k: load_gray(p, k in ("seams", "hilite")) for k, p in maps[view].items()}
        if "inside" not in M:
            M["inside"] = np.zeros((N, N), np.float32)
        wx, wy = cloth_warp(seed=21 if view == "front" else 23)
        M = {k: cv2.remap(v, wx, wy, cv2.INTER_LINEAR) for k, v in M.items()}
        for c in CONCEPTS:
            ps = []
            for p in prints[(c, view)]:
                rgb, a = load_rgba(p["file"])
                wp = dict(p)
                wp["rgb"] = cv2.remap(rgb, wx, wy, cv2.INTER_LINEAR)
                wp["a"] = cv2.remap(a, wx, wy, cv2.INTER_LINEAR)
                ps.append(wp)
            rgba = composite(c, view, M, ps)
            save_rgba(os.path.join(OUT, f"tee-{c}-{view}.png"), rgba)
            print("rendered", c, view)


if __name__ == "__main__":
    main()
