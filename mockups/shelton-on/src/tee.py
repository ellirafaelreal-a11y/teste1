"""
Procedural ghost-mannequin crew-neck training tee.

Generates the vector maps that compose.py turns into a shaded render:
silhouette / part masks, a fold (relief) map, seam & stitch lines.

Coordinate system: 1 unit = 1 mm (size M: chest 52 cm, body 72 cm),
viewBox 0 40 1000 1000, y down.
"""

VB = (0, 40, 1000, 1000)

# ---------------------------------------------------------------- outlines --
FRONT_TOP = "M415,180 C445,166 472,162 500,162 C528,162 555,166 585,180"
BACK_TOP = "M415,180 C445,188 472,193 500,193 C528,193 555,188 585,180"

REST = (
    " C632,186 684,200 730,225"          # right shoulder
    " C795,255 853,296 902,345"          # right sleeve top
    " C876,396 843,443 804,484"          # right cuff
    " C790,462 770,440 758,422"          # right underarm
    " C750,560 748,760 754,900"          # right side
    " C650,919 350,919 246,900"          # hem
    " C252,760 250,560 242,422"          # left side
    " C230,440 210,462 196,484"          # left underarm
    " C157,443 124,396 98,345"           # left cuff
    " C147,296 205,255 270,225"          # left sleeve top
    " C316,200 368,186 415,180 Z"        # left shoulder
)


def outline(view):
    return (FRONT_TOP if view == "front" else BACK_TOP) + REST


# sleeves: shoulder point -> sleeve top -> cuff -> underarm -> armpit -> armhole seam
SLEEVE_L = (
    "M270,225 C205,255 147,296 98,345 C124,396 157,443 196,484 "
    "C210,462 230,440 242,422 C262,372 272,290 270,225 Z"
)
SLEEVE_R = (
    "M730,225 C795,255 853,296 902,345 C876,396 843,443 804,484 "
    "C790,462 770,440 758,422 C738,372 728,290 730,225 Z"
)
ARMHOLE_L = "M270,225 C272,290 262,372 242,422"
ARMHOLE_R = "M730,225 C728,290 738,372 758,422"

# front neck
BACKCOLLAR_IN = (
    "M415,180 C445,166 472,162 500,162 C528,162 555,166 585,180 "
    "L572,187 C548,181 524,179 500,179 C476,179 452,181 428,187 Z"
)
INSIDE = (
    "M428,187 C452,181 476,179 500,179 C524,179 548,181 572,187 "
    "C563,226 534,249 500,249 C466,249 437,226 428,187 Z"
)
FRONTCOLLAR = (
    "M415,180 C425,231 460,268 500,268 C540,268 575,231 585,180 "
    "L572,187 C563,226 534,249 500,249 C466,249 437,226 428,187 Z"
)
FRONTCOLLAR_MID = "M421.5,183.5 C431,228 463,258.5 500,258.5 C537,258.5 569,228 578.5,183.5"
FRONTCOLLAR_OUTER = "M415,180 C425,231 460,268 500,268 C540,268 575,231 585,180"
BACKCOLLAR_MID = "M421.5,183.5 C448,173 474,170.5 500,170.5 C526,170.5 552,173 578.5,183.5"

# back neck
BACKCOLLAR_OUT = (
    "M415,180 C445,188 472,193 500,193 C528,193 555,188 585,180 "
    "L587,197 C557,206 529,211 500,211 C471,211 443,206 413,197 Z"
)
BACKCOLLAR_OUT_MID = "M414,188.5 C444,197 471,202 500,202 C529,202 556,197 586,188.5"
BACKCOLLAR_OUT_SEAM = "M413,197 C443,206 471,211 500,211 C529,211 557,206 587,197"


def hem_offset(dy):
    return f"M{248},{900-dy} C350,{919-dy} 650,{919-dy} {752},{900-dy}"


def cuff_offset_l(d):
    # cuff L runs (196,484)->(98,345); shift along sleeve axis towards shoulder
    ox, oy = 0.819 * d, -0.574 * d
    pts = [(196, 484), (157, 443), (124, 396), (98, 345)]
    p = [(x + ox, y + oy) for x, y in pts]
    return f"M{p[0][0]:.1f},{p[0][1]:.1f} C{p[1][0]:.1f},{p[1][1]:.1f} {p[2][0]:.1f},{p[2][1]:.1f} {p[3][0]:.1f},{p[3][1]:.1f}"


def cuff_offset_r(d):
    ox, oy = -0.819 * d, -0.574 * d
    pts = [(804, 484), (843, 443), (876, 396), (902, 345)]
    p = [(x + ox, y + oy) for x, y in pts]
    return f"M{p[0][0]:.1f},{p[0][1]:.1f} C{p[1][0]:.1f},{p[1][1]:.1f} {p[2][0]:.1f},{p[2][1]:.1f} {p[3][0]:.1f},{p[3][1]:.1f}"


# ------------------------------------------------------------------- folds --
# (path, stroke width, signed intensity, blur)
FOLDS_COMMON = [
    # armpit drag lines (diagonal, towards centre chest / waist)
    ("M246,436 C276,446 306,468 344,506 C360,522 372,540 380,556", 11, -0.62, 6),
    ("M250,474 C272,492 292,514 310,548 C318,564 322,580 324,596", 8, -0.45, 6),
    ("M254,454 C286,468 314,490 340,524 C350,538 358,552 362,566", 13, +0.40, 8),
    ("M248,500 C262,520 274,546 282,580", 7, +0.25, 7),
    ("M754,436 C724,448 694,470 656,508 C640,524 628,542 620,558", 11, -0.62, 6),
    ("M750,472 C728,490 708,512 690,546 C682,562 678,578 676,594", 8, -0.45, 6),
    ("M746,454 C714,470 686,492 660,526 C650,540 642,554 638,568", 13, +0.40, 8),
    ("M752,500 C738,520 726,546 718,580", 7, +0.25, 7),
    # long body waves (hanging fabric)
    ("M326,600 C334,680 322,760 326,840 C328,866 324,884 322,898", 14, -0.30, 12),
    ("M350,610 C358,690 346,770 350,850 C352,872 348,888 346,904", 22, +0.24, 14),
    ("M680,630 C672,710 682,790 678,860 C677,878 680,890 682,898", 14, -0.26, 12),
    ("M656,630 C648,710 658,790 654,860 C653,880 656,894 658,906", 22, +0.22, 14),
    ("M548,680 C556,760 544,840 552,912", 12, -0.13, 14),
    ("M455,700 C448,780 458,850 452,914", 14, +0.10, 14),
    # central chest volume
    ("M480,300 C490,450 485,650 492,880", 150, +0.13, 55),
    # waist side shadows
    ("M262,560 C266,680 262,800 258,890", 30, -0.20, 18),
    ("M738,560 C734,680 738,800 742,890", 30, -0.20, 18),
    # hem ripples
    ("M292,900 C293,880 296,860 300,836", 8, -0.42, 5),
    ("M306,903 C308,884 311,866 314,846", 10, +0.25, 7),
    ("M421,916 C422,896 423,880 426,860", 7, -0.32, 5),
    ("M440,915 C442,897 443,884 445,870", 10, +0.22, 7),
    ("M576,916 C575,896 573,880 570,862", 7, -0.32, 5),
    ("M708,903 C706,884 703,866 699,844", 8, -0.42, 5),
    ("M694,906 C692,888 690,872 687,854", 10, +0.24, 7),
    # sleeves: underarm creases radiating from the armpit
    ("M240,430 C212,430 172,420 136,400", 10, -0.50, 7),
    ("M240,446 C218,452 196,462 176,472", 7, -0.38, 5),
    ("M236,414 C214,404 190,388 166,366", 7, -0.25, 7),
    ("M244,422 C220,418 186,404 152,384", 9, +0.22, 8),
    ("M262,242 C220,272 170,306 122,338", 24, +0.34, 13),
    ("M760,430 C788,430 828,420 864,400", 10, -0.50, 7),
    ("M760,446 C782,452 804,462 824,472", 7, -0.38, 5),
    ("M764,414 C786,404 810,388 834,366", 7, -0.25, 7),
    ("M756,422 C780,418 814,404 848,384", 9, +0.22, 8),
    ("M738,242 C780,272 830,306 878,338", 24, +0.34, 13),
    # cuff hem roll
    ("M190,476 C160,440 130,398 108,352", 6, +0.22, 4),
    ("M810,476 C840,440 870,398 892,352", 6, +0.22, 4),
    # shoulders
    ("M300,214 C340,200 380,190 410,186", 16, +0.30, 10),
    ("M700,214 C660,200 620,190 590,186", 16, +0.30, 10),
]

FOLDS_FRONT = FOLDS_COMMON + [
    # contact shadow under the front collar rib
    (FRONTCOLLAR_OUTER, 5, -0.55, 4),
    ("M380,300 C392,340 402,380 406,420", 16, +0.10, 16),
    ("M620,300 C608,340 598,380 594,420", 16, +0.10, 16),
]

FOLDS_BACK = FOLDS_COMMON + [
    (BACKCOLLAR_OUT_SEAM, 5, -0.30, 4),
    ("M415,183 C445,191 472,196 500,196 C528,196 555,191 585,183", 4, +0.30, 3),
    # shoulder blades
    ("M360,300 C380,340 395,380 400,430", 40, +0.12, 26),
    ("M640,300 C620,340 605,380 600,430", 40, +0.12, 26),
    ("M500,230 C500,330 500,430 500,520", 10, -0.10, 12),
]


def _svg(body, defs=""):
    x, y, w, h = VB
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}">'
        f"<defs>{defs}</defs>{body}</svg>"
    )


def mask_svg(path_d, clip=None):
    clip_attr = ""
    defs = ""
    if clip:
        defs = f'<clipPath id="c"><path d="{clip}"/></clipPath>'
        clip_attr = ' clip-path="url(#c)"'
    return _svg(
        f'<rect x="-100" y="-100" width="1200" height="1300" fill="#000"/>'
        f'<path d="{path_d}" fill="#fff"{clip_attr}/>',
        defs,
    )


def body_mask_svg(view):
    """Body panel = silhouette minus sleeves (and minus collar/inside on front)."""
    cut = [SLEEVE_L, SLEEVE_R]
    if view == "front":
        cut += [BACKCOLLAR_IN, INSIDE, FRONTCOLLAR]
    else:
        cut += [BACKCOLLAR_OUT]
    cuts = "".join(f'<path d="{c}" fill="#000"/>' for c in cut)
    return _svg(
        f'<rect x="-100" y="-100" width="1200" height="1300" fill="#000"/>'
        f'<path d="{outline(view)}" fill="#fff"/>{cuts}'
    )


def folds_svg(view):
    folds = FOLDS_FRONT if view == "front" else FOLDS_BACK
    defs = [f'<clipPath id="sil"><path d="{outline(view)}"/></clipPath>']
    body = []
    for i, (d, w, k, blur) in enumerate(folds):
        defs.append(
            f'<filter id="b{i}" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1200" height="1300">'
            f'<feGaussianBlur stdDeviation="{blur}"/></filter>'
        )
        col = "#fff" if k > 0 else "#000"
        body.append(
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
            f'stroke-linecap="round" opacity="{abs(k):.3f}" filter="url(#b{i})"/>'
        )
    return _svg(
        '<rect x="-100" y="-100" width="1200" height="1300" fill="#808080"/>'
        f'<g clip-path="url(#sil)">{"".join(body)}</g>',
        "".join(defs),
    )


def seams_svg(view):
    """Dark stitch / seam lines, alpha encodes darkness (black on transparent)."""
    s = []

    def p(d, w, op, dash=None, col="#000"):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        s.append(
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
            f'opacity="{op}" stroke-linecap="round"{da}/>'
        )

    # armhole seams
    for d in (ARMHOLE_L, ARMHOLE_R):
        p(d, 1.6, 0.55)
    # hem: edge fold line + double needle stitch
    p(hem_offset(21), 1.2, 0.22)
    p(hem_offset(14), 0.9, 0.55, "2.6 1.6")
    p(hem_offset(18.5), 0.9, 0.55, "2.6 1.6")
    # cuffs
    for fn in (cuff_offset_l, cuff_offset_r):
        p(fn(17), 1.1, 0.22)
        p(fn(10), 0.9, 0.55, "2.4 1.5")
        p(fn(14), 0.9, 0.55, "2.4 1.5")
    # shoulder seams (top edge)
    p("M412,186 C366,192 316,206 272,231", 1.1, 0.30)
    p("M588,186 C634,192 684,206 728,231", 1.1, 0.30)
    if view == "front":
        # collar rib texture (perpendicular stripes via dashed thick stroke)
        p(FRONTCOLLAR_MID, 17, 0.16, "0.9 1.3")
        p(BACKCOLLAR_MID, 13, 0.14, "0.9 1.3")
        # cover stitch below collar
        p("M412,183 C421,236 458,274 500,274 C542,274 579,236 588,183", 0.9, 0.55, "2.4 1.5")
        p(FRONTCOLLAR_OUTER, 1.4, 0.45)
    else:
        p(BACKCOLLAR_OUT_MID, 17, 0.09, "0.9 1.3")
        p(BACKCOLLAR_OUT_SEAM, 1.4, 0.45)
        p("M412,203 C442,212 471,217 500,217 C529,217 558,212 588,203", 0.9, 0.55, "2.4 1.5")
    return _svg(f'<g clip-path="url(#sil)">{"".join(s)}</g>',
                f'<clipPath id="sil"><path d="{outline(view)}"/></clipPath>')


def highlights_svg(view):
    """Thin light lines next to seams (fabric ridge catching light)."""
    s = []

    def p(d, w, op):
        s.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w}" opacity="{op}"/>')

    p("M273,226 C275,290 265,372 245,422", 2.2, 0.35)
    p("M727,226 C725,290 735,372 755,422", 2.2, 0.35)
    p(hem_offset(23), 2.0, 0.25)
    if view == "front":
        p("M412,180 C422,233 458,271 500,271 C542,271 578,233 588,180", 1.6, 0.25)
    return _svg(f'<g clip-path="url(#sil)">{"".join(s)}</g>',
                f'<clipPath id="sil"><path d="{outline(view)}"/></clipPath>')


def write_maps(outdir, view):
    import os
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
        fp = os.path.join(outdir, f"{view}-{k}.svg")
        with open(fp, "w") as fh:
            fh.write(v)
        paths[k] = fp
    return paths
