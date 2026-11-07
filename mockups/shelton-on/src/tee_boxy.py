"""
Procedural ghost-mannequin LIFESTYLE tee: heavyweight cotton, oversized/boxy
fit, dropped shoulders, wide rib collar. Same interface as tee.py.

1 unit = 1 mm (size M oversized: chest 60 cm, body 70 cm), viewBox 0 40 1000 1000.
"""
import os

VB = (0, 40, 1000, 1000)

FRONT_TOP = "M402,178 C438,163 468,158 500,158 C532,158 562,163 598,178"
BACK_TOP = "M402,178 C438,186 468,191 500,191 C532,191 562,186 598,178"

REST = (
    " C680,186 750,198 795,213"          # right shoulder (flat, wide)
    " C850,250 900,292 938,338"          # right sleeve top
    " C918,392 885,452 850,500"          # right cuff
    " C832,490 812,480 795,470"          # right underarm
    " C792,600 792,760 793,880"          # right side (boxy, straight)
    " C680,902 320,902 207,880"          # hem
    " C208,760 208,600 205,470"          # left side
    " C188,480 168,490 150,500"          # left underarm
    " C115,452 82,392 62,338"            # left cuff
    " C100,292 150,250 205,213"          # left sleeve top
    " C250,198 320,186 402,178 Z"        # left shoulder
)


def outline(view):
    return (FRONT_TOP if view == "front" else BACK_TOP) + REST


SLEEVE_L = ("M205,213 C150,250 100,292 62,338 C82,392 115,452 150,500 "
            "C168,490 188,480 205,470 C214,390 214,290 205,213 Z")
SLEEVE_R = ("M795,213 C850,250 900,292 938,338 C918,392 885,452 850,500 "
            "C832,490 812,480 795,470 C786,390 786,290 795,213 Z")
ARMHOLE_L = "M205,213 C214,290 214,390 205,470"
ARMHOLE_R = "M795,213 C786,290 786,390 795,470"

BACKCOLLAR_IN = (
    "M402,178 C438,163 468,158 500,158 C532,158 562,163 598,178 "
    "L583,186 C556,179 528,177 500,177 C472,177 444,179 417,186 Z"
)
INSIDE = (
    "M417,186 C444,179 472,177 500,177 C528,177 556,179 583,186 "
    "C573,226 540,245 500,245 C460,245 427,226 417,186 Z"
)
FRONTCOLLAR = (
    "M402,178 C414,234 454,270 500,270 C546,270 586,234 598,178 "
    "L583,186 C573,226 540,245 500,245 C460,245 427,226 417,186 Z"
)
FRONTCOLLAR_MID = "M409.5,182 C420.5,230 457,257.5 500,257.5 C543,257.5 579.5,230 590.5,182"
FRONTCOLLAR_OUTER = "M402,178 C414,234 454,270 500,270 C546,270 586,234 598,178"
BACKCOLLAR_MID = "M409.5,182 C441,171 470,167.5 500,167.5 C530,167.5 559,171 590.5,182"

BACKCOLLAR_OUT = (
    "M402,178 C438,186 468,191 500,191 C532,191 562,186 598,178 "
    "L600,198 C565,208 532,213 500,213 C468,213 435,208 400,198 Z"
)
BACKCOLLAR_OUT_MID = "M401,188 C436,197 468,202 500,202 C532,202 564,197 599,188"
BACKCOLLAR_OUT_SEAM = "M400,198 C435,208 468,213 500,213 C532,213 565,208 600,198"


def hem_offset(dy):
    return f"M209,{880-dy} C320,{902-dy} 680,{902-dy} 791,{880-dy}"


def _shift(pts, ox, oy):
    p = [(x + ox, y + oy) for x, y in pts]
    return (f"M{p[0][0]:.1f},{p[0][1]:.1f} C{p[1][0]:.1f},{p[1][1]:.1f} "
            f"{p[2][0]:.1f},{p[2][1]:.1f} {p[3][0]:.1f},{p[3][1]:.1f}")


def cuff_offset_l(d):
    return _shift([(150, 500), (115, 452), (82, 392), (62, 338)], 0.82 * d, -0.57 * d)


def cuff_offset_r(d):
    return _shift([(850, 500), (885, 452), (918, 392), (938, 338)], -0.82 * d, -0.57 * d)


# heavy cotton: fewer, broader, softer folds
FOLDS_COMMON = [
    # soft drape from the collar towards the dropped armholes
    ("M420,262 C380,300 320,360 262,430", 34, -0.16, 22),
    ("M580,262 C620,300 680,360 738,430", 34, -0.16, 22),
    ("M440,282 C400,320 345,378 290,446", 40, +0.14, 24),
    ("M560,282 C600,320 655,378 710,446", 40, +0.14, 24),
    # armpit creases (short, soft)
    ("M214,476 C238,492 262,512 282,540", 12, -0.42, 8),
    ("M786,476 C762,492 738,512 718,540", 12, -0.42, 8),
    ("M218,500 C236,520 250,546 258,576", 16, +0.22, 10),
    ("M782,500 C764,520 750,546 742,576", 16, +0.22, 10),
    # big hanging folds of the boxy body
    ("M262,560 C272,660 258,770 266,876", 30, -0.30, 18),
    ("M300,560 C310,660 296,770 304,884", 36, +0.24, 20),
    ("M738,580 C728,680 742,780 734,876", 30, -0.28, 18),
    ("M700,580 C690,680 704,780 696,884", 36, +0.22, 20),
    ("M520,620 C528,720 514,820 522,896", 22, -0.12, 18),
    ("M470,640 C462,740 474,830 466,898", 26, +0.10, 18),
    # chest volume
    ("M484,300 C492,450 486,650 492,880", 170, +0.12, 60),
    # side shadows
    ("M226,520 C230,660 226,780 224,872", 36, -0.22, 20),
    ("M774,520 C770,660 774,780 776,872", 36, -0.22, 20),
    # hem waves
    ("M340,896 C342,876 345,858 348,840", 10, -0.32, 7),
    ("M362,898 C364,880 366,864 368,848", 14, +0.20, 9),
    ("M640,898 C638,878 636,860 633,842", 10, -0.32, 7),
    ("M618,899 C616,882 614,866 612,850", 14, +0.20, 9),
    # sleeves: one big soft fold + top highlight
    ("M205,330 C170,350 130,372 92,392", 20, -0.30, 12),
    ("M205,300 C168,318 128,338 84,360", 18, +0.22, 12),
    ("M205,232 C160,262 112,298 74,330", 26, +0.30, 14),
    ("M206,452 C186,466 168,478 152,490", 9, -0.32, 6),
    ("M795,330 C830,350 870,372 908,392", 20, -0.30, 12),
    ("M795,300 C832,318 872,338 916,360", 18, +0.22, 12),
    ("M795,232 C840,262 888,298 926,330", 26, +0.30, 14),
    ("M794,452 C814,466 832,478 848,490", 9, -0.32, 6),
    # shoulders
    ("M240,205 C300,192 360,184 405,181", 18, +0.28, 12),
    ("M760,205 C700,192 640,184 595,181", 18, +0.28, 12),
]

FOLDS_FRONT = FOLDS_COMMON + [(FRONTCOLLAR_OUTER, 6, -0.55, 5)]
FOLDS_BACK = FOLDS_COMMON + [
    (BACKCOLLAR_OUT_SEAM, 6, -0.32, 5),
    ("M402,181 C438,189 468,194 500,194 C532,194 562,189 598,181", 4, +0.30, 3),
    ("M360,300 C380,340 395,380 400,430", 50, +0.10, 30),
    ("M640,300 C620,340 605,380 600,430", 50, +0.10, 30),
]


def _svg(body, defs=""):
    x, y, w, h = VB
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}">'
            f"<defs>{defs}</defs>{body}</svg>")


def mask_svg(path_d):
    return _svg('<rect x="-100" y="-100" width="1200" height="1300" fill="#000"/>'
                f'<path d="{path_d}" fill="#fff"/>')


def body_mask_svg(view):
    cut = [SLEEVE_L, SLEEVE_R]
    cut += [BACKCOLLAR_IN, INSIDE, FRONTCOLLAR] if view == "front" else [BACKCOLLAR_OUT]
    cuts = "".join(f'<path d="{c}" fill="#000"/>' for c in cut)
    return _svg('<rect x="-100" y="-100" width="1200" height="1300" fill="#000"/>'
                f'<path d="{outline(view)}" fill="#fff"/>{cuts}')


def folds_svg(view):
    folds = FOLDS_FRONT if view == "front" else FOLDS_BACK
    defs = [f'<clipPath id="sil"><path d="{outline(view)}"/></clipPath>']
    body = []
    for i, (d, w, k, blur) in enumerate(folds):
        defs.append(f'<filter id="b{i}" filterUnits="userSpaceOnUse" x="-100" y="-100" '
                    f'width="1200" height="1300"><feGaussianBlur stdDeviation="{blur}"/></filter>')
        col = "#fff" if k > 0 else "#000"
        body.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
                    f'stroke-linecap="round" opacity="{abs(k):.3f}" filter="url(#b{i})"/>')
    return _svg('<rect x="-100" y="-100" width="1200" height="1300" fill="#808080"/>'
                f'<g clip-path="url(#sil)">{"".join(body)}</g>', "".join(defs))


def seams_svg(view):
    s = []

    def p(d, w, op, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        s.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{w}" '
                 f'opacity="{op}" stroke-linecap="round"{da}/>')

    for d in (ARMHOLE_L, ARMHOLE_R):
        p(d, 1.8, 0.55)
    # wide single-needle hem (heavy cotton)
    p(hem_offset(26), 1.3, 0.22)
    p(hem_offset(22), 1.0, 0.55, "3 1.8")
    for fn in (cuff_offset_l, cuff_offset_r):
        p(fn(24), 1.2, 0.22)
        p(fn(20), 1.0, 0.55, "2.8 1.7")
    p("M400,184 C330,190 260,200 207,219", 1.2, 0.30)
    p("M600,184 C670,190 740,200 793,219", 1.2, 0.30)
    if view == "front":
        p(FRONTCOLLAR_MID, 23, 0.18, "1.0 1.4")
        p(BACKCOLLAR_MID, 17, 0.15, "1.0 1.4")
        p("M398,181 C410,240 452,277 500,277 C548,277 590,240 602,181", 1.0, 0.55, "2.6 1.6")
        p(FRONTCOLLAR_OUTER, 1.5, 0.45)
    else:
        p(BACKCOLLAR_OUT_MID, 20, 0.10, "1.0 1.4")
        p(BACKCOLLAR_OUT_SEAM, 1.5, 0.45)
        p("M398,205 C434,215 468,220 500,220 C532,220 566,215 602,205", 1.0, 0.55, "2.6 1.6")
    return _svg(f'<g clip-path="url(#sil)">{"".join(s)}</g>',
                f'<clipPath id="sil"><path d="{outline(view)}"/></clipPath>')


def highlights_svg(view):
    s = []

    def p(d, w, op):
        s.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w}" opacity="{op}"/>')

    p("M208,214 C217,290 217,390 208,470", 2.4, 0.30)
    p("M792,214 C783,290 783,390 792,470", 2.4, 0.30)
    p(hem_offset(28), 2.2, 0.22)
    if view == "front":
        p("M399,178 C411,236 452,273 500,273 C548,273 589,236 601,178", 1.8, 0.22)
    return _svg(f'<g clip-path="url(#sil)">{"".join(s)}</g>',
                f'<clipPath id="sil"><path d="{outline(view)}"/></clipPath>')


def write_maps(outdir, view):
    os.makedirs(outdir, exist_ok=True)
    files = {
        "sil": mask_svg(outline(view)),
        "body": body_mask_svg(view),
        "sleeveL": mask_svg(SLEEVE_L),
        "sleeveR": mask_svg(SLEEVE_R),
        "folds": folds_svg(view),
        "seams": seams_svg(view),
        "hilite": highlights_svg(view),
    }
    if view == "front":
        files["inside"] = mask_svg(INSIDE)
        files["collar"] = mask_svg(FRONTCOLLAR)
        files["backcollar"] = mask_svg(BACKCOLLAR_IN)
    else:
        files["collar"] = mask_svg(BACKCOLLAR_OUT)
    paths = {}
    for k, v in files.items():
        fp = os.path.join(outdir, f"boxy-{view}-{k}.svg")
        with open(fp, "w") as fh:
            fh.write(v)
        paths[k] = fp
    return paths
