"""
Vertical lettering tees (from the user's reference): the name runs top to
bottom so the On symbol's o and n stay stacked in their natural order.
07 FONSECA and 08 SHELTON, on the lifestyle (boxy) tee.

    python3 src/vertical.py      (after compose.py has been run once)
"""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art  # noqa: E402
import board  # noqa: E402
import compose  # noqa: E402
import tee_boxy  # noqa: E402

OUT, BUILD, S = compose.OUT, compose.BUILD, compose.SCALE
HPS_Y = 178.0
O, N_ = art.ON_O, art.ON_N
CAP = 38.0        # mm, letter height on the back
PITCH = 1.8       # row pitch in letter heights
BACK_TOP = 258.0  # first row top (mm, tee coords)

VERTICAL = {
    "07": {
        "name": "FONSECA", "tokens": ["F", O, N_, "S", "E", "C", "A"], "pre": "f", "suf": "seca",
        "full_d": "João Fonseca",
        "tee": "#CDCBD1", "tee_name": "Heather Grey", "heather": 0.045,
        "ink": "#151515", "ink_name": "Black",
        "spec": 0.010, "fresnel": 0.0, "label_ink": "#8f8c94",
        "opacity": 0.985, "grain": 0.03, "bg": "#DEDCD8",
        "pantone": ("&asymp; 14-4102 TCX", "&asymp; Black 6 C"),
        "fabric": "Algodão 240 g/m², mescla",
        "tech": "Silk base d'água, toque zero",
        "concept": ("Como na sua referência: com o nome escrito de cima para baixo, o símbolo On entra "
                    "<b>inteiro e na ordem original</b>, o em cima e n embaixo, sem desmontar nada. "
                    "A coluna desce pelas costas; na frente, o nome pequeno no peito. Mescla cinza e tinta preta."),
    },
    "08": {
        "name": "SHELTON", "tokens": ["S", "H", "E", "L", "T", O, N_], "pre": "shelt", "suf": "",
        "full_d": "Ben Shelton",
        "tee": "#1B1B1D", "tee_name": "Black", "heather": 0.0,
        "ink": "#ECE6D6", "ink_name": "Ecru",
        "spec": 0.030, "fresnel": 0.015, "label_ink": "#5e5e60",
        "opacity": 0.95, "grain": 0.045, "bg": "#DEDCD8",
        "pantone": ("&asymp; 19-0303 TCX", "&asymp; 9224 C"),
        "fabric": "Algodão orgânico 240 g/m²",
        "tech": "Silk discharge (toque zero em malha escura)",
        "concept": ("O mesmo sistema no Shelton: o símbolo On fecha a coluna, como a última sílaba do nome, "
                    "e aparece exatamente como a marca o desenha. Preto e tinta ecru, só letra e símbolo."),
    },
}


def vlock(cid):
    return art.lockup_vertical(VERTICAL[cid]["tokens"], h=CAP, pitch=PITCH)


def chest_lock(cid):
    c = VERTICAL[cid]
    return art.lockup_inline(c["pre"], c["suf"], "upper")


CHEST_W, CHEST_CX, CHEST_TOP = 78.0, 610.0, 332.0


def print_svg(cid, view):
    c = VERTICAL[cid]
    x0, y0, w0, h0 = tee_boxy.VB
    g = []
    if view == "back":
        g.append(art.vertical_group(vlock(cid), 1.0, c["ink"], c["ink"], cx=500.0, top=BACK_TOP))
    else:
        lk = chest_lock(cid)
        l, t, r, b = lk["bbox"]
        k = CHEST_W / (r - l)
        g.append(f'<g transform="translate({CHEST_CX - CHEST_W/2:.3f},{CHEST_TOP:.3f})">'
                 f'{art.inline_group(lk, k, c["ink"])}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w0} {h0}">'
            f'{"".join(g)}</svg>')


def render():
    jobs, maps, prints = [], {}, {}
    for view in ("front", "back"):
        paths = tee_boxy.write_maps(os.path.join(BUILD, "maps"), view)
        maps[view] = {}
        for k, svg in paths.items():
            png = svg[:-4] + ".png"
            jobs.append({"in": svg, "out": png, "w": 1000, "h": 1000, "scale": S,
                         "transparent": k in ("seams", "hilite")})
            maps[view][k] = png
    for cid, c in VERTICAL.items():
        compose.CONCEPTS[cid] = {k: c[k] for k in ("tee", "spec", "fresnel", "label_ink", "heather")}
        for view in ("front", "back"):
            sp = os.path.join(BUILD, f"print-{cid}-{view}.svg")
            with open(sp, "w") as fh:
                fh.write(print_svg(cid, view))
            jobs.append({"in": sp, "out": sp[:-4] + ".png", "w": 1000, "h": 1000, "scale": S, "transparent": True})
            prints[(cid, view)] = [{"file": sp[:-4] + ".png", "opacity": c["opacity"],
                                    "grain": c["grain"], "spec": 0.006}]
        lp = os.path.join(BUILD, f"label-{cid}.svg")
        with open(lp, "w") as fh:
            fh.write(compose.neck_label_svg(cid))
        jobs.append({"in": lp, "out": lp[:-4] + ".png", "w": 1000, "h": 1000, "scale": S, "transparent": True})
        prints[(cid, "front")].insert(0, {"file": lp[:-4] + ".png", "inside": True, "opacity": 0.9, "spec": 0.0})
    compose.rasterise(jobs)
    for view in ("front", "back"):
        M = {k: compose.load_gray(p, k in ("seams", "hilite")) for k, p in maps[view].items()}
        if "inside" not in M:
            M["inside"] = np.zeros((compose.N, compose.N), np.float32)
        wx, wy = compose.cloth_warp(seed=41 if view == "front" else 43, amp_px=3.8)
        M = {k: cv2.remap(v, wx, wy, cv2.INTER_LINEAR) for k, v in M.items()}
        for cid in VERTICAL:
            ps = []
            for p in prints[(cid, view)]:
                rgb, a = compose.load_rgba(p["file"])
                q = dict(p)
                q["rgb"] = cv2.remap(rgb, wx, wy, cv2.INTER_LINEAR)
                q["a"] = cv2.remap(a, wx, wy, cv2.INTER_LINEAR)
                ps.append(q)
            compose.save_rgba(os.path.join(OUT, f"tee-{cid}-{view}.png"), compose.composite(cid, view, M, ps))
            print("rendered", cid, view)


def cm(v):
    return f"{v:.1f}".replace(".", ",") + " cm"


def inline_svg(lk, height_px, ink):
    l, t, r, b = lk["bbox"]
    k = height_px / (b - t)
    w = (r - l) * k
    return (f'<svg width="{w:.1f}" height="{height_px:.1f}" viewBox="0 0 {w:.2f} {height_px:.2f}">'
            f'{art.inline_group(lk, k, ink)}</svg>')


def tee_board(cid):
    c = VERTICAL[cid]
    lk = vlock(cid)
    l, t, r, b = lk["bbox"]
    vw, vh = r - l, b - t
    io = c["tokens"].index(O)
    cy = BACK_TOP + (io + 0.5) * PITCH * CAP + CAP / 2
    det = os.path.join(BUILD, f"detail-{cid}.png")
    board.crop_detail(os.path.join(OUT, f"tee-{cid}-back.png"), det, 500, cy, 150, c["tee"])
    cl = chest_lock(cid)
    cb = cl["bbox"]
    ch = CHEST_W * (cb[3] - cb[1]) / (cb[2] - cb[0])
    sw = [(c["tee_name"], c["tee"], f"Malha<br>{c['pantone'][0]}"),
          (c["ink_name"], c["ink"], f"Tinta<br>{c['pantone'][1]}")]
    sw_html = "".join(
        f'<div><div class="chip" style="background:{h}"></div><div class="n">{n}</div>'
        f'<div class="c">{h.upper()}<br>{note}</div></div>' for n, h, note in sw)
    rows = [
        ("Costas", f"Coluna vertical {c['name']} &middot; {vw:.0f} &times; {vh:.0f} mm &middot; eixo central, "
                   f"topo {cm((BACK_TOP - HPS_Y) / 10)} abaixo do ombro"),
        ("Frente", f"{c['name']} com On na horizontal &middot; {CHEST_W:.0f} &times; {ch:.0f} mm &middot; peito esquerdo"),
        ("Malha", c["fabric"]),
        ("Modelagem", "Oversized, ombro caído, gola em ribana 2,4 cm"),
        ("Técnica", c["tech"]),
    ]
    rows_html = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{board.font_css()}
:root{{--bg:{c['bg']};--fg:#141414;--muted:#74726c;--rule:rgba(20,20,20,.14)}}{board.BASE_CSS}
.ttl{{display:flex;flex-direction:column;gap:14px}}
.view img{{left:-30px;top:-40px;width:650px;height:650px}}
.view .lab{{top:572px}}
</style></head><body><div class="grain"></div>
<header>
  <div class="titlewrap"><div class="num">{cid}</div>
    <div class="ttl">{inline_svg(cl, 40, '#141414')}<div class="subtitle mono">Camiseta lifestyle &middot; lettering vertical &middot; {c['tee_name']} / {c['ink_name']}</div></div></div>
  <div class="meta mono"><b>{c['full_d']} &times; {board.on_svg('#141414')}</b><br>Lifestyle tee &middot; Concept<br>On Tennis &middot; SS27</div>
</header>
<div class="stage">
  <div class="view"><img src="file://{OUT}/tee-{cid}-back.png">
    <div class="lab mono"><span>COSTAS</span><span>{c['name']} na vertical</span></div></div>
  <div class="view"><img src="file://{OUT}/tee-{cid}-front.png">
    <div class="lab mono"><span>FRENTE</span><span>Peito esquerdo</span></div></div>
</div>
<aside>
  <h4>Conceito</h4><p>{c['concept']}</p>
  <h4>Cores</h4><div class="sw">{sw_html}</div>
  <h4>Aplicações &middot; tam. M</h4><table>{rows_html}</table>
  <div class="detail"><img src="file://{det}"><span>Detalhe: o símbolo On inteiro, o sobre n, no mesmo ritmo das letras da coluna.</span></div>
</aside>
<footer class="mono"><span>Conceito não oficial para apresentação &middot; Símbolo On reconstruído: validar com a marca antes da produção</span>
<span>On Tennis &middot; Lifestyle &middot; {cid}</span></footer>
</body></html>"""
    p = os.path.join(BUILD, f"board-{cid}.html")
    with open(p, "w") as fh:
        fh.write(html)
    return p


def overview():
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{board.font_css()}
:root{{--bg:#DEDCD8;--fg:#141414;--muted:#74726c;--rule:rgba(20,20,20,.14)}}{board.BASE_CSS}
.ov{{position:absolute;left:0;right:0;top:120px;display:flex;justify-content:center;gap:10px}}
.ov figure{{position:relative;width:740px;height:800px}}
.ov img{{position:absolute;left:-10px;top:0;width:760px;height:760px}}
.ov figcaption{{position:absolute;left:70px;right:70px;top:745px;display:flex;justify-content:space-between;
  border-top:1px solid var(--rule);padding-top:12px;font-size:11px;color:var(--muted)}}
.ov figcaption b{{color:var(--fg)}}
.big{{font-family:'Outfit';font-weight:700;font-size:30px}}
</style></head><body><div class="grain"></div>
<header><div><div class="big">Lettering vertical</div>
<div class="subtitle mono">O símbolo On inteiro, na ordem original &middot; costas</div></div>
<div class="meta mono"><b>{board.on_svg('#141414', '30px')}</b><br>On Tennis &middot; Lifestyle &middot; SS27</div></header>
<div class="ov">
<figure><img src="file://{OUT}/tee-07-back.png"><figcaption class="mono"><span><b>07</b> &nbsp;Fonseca</span><span>Heather Grey / Black</span></figcaption></figure>
<figure><img src="file://{OUT}/tee-08-back.png"><figcaption class="mono"><span><b>08</b> &nbsp;Shelton</span><span>Black / Ecru</span></figcaption></figure>
</div>
<footer class="mono"><span>Conceito não oficial para apresentação &middot; Símbolo On reconstruído: validar com a marca antes da produção</span><span>Vertical</span></footer>
</body></html>"""
    p = os.path.join(BUILD, "board-vertical-00.html")
    with open(p, "w") as fh:
        fh.write(html)
    return p


def export_art():
    for cid, c in VERTICAL.items():
        lk = vlock(cid)
        l, t, r, b = lk["bbox"]
        pad = 2.0
        W, H = r - l + 2 * pad, b - t + 2 * pad
        body = art.vertical_group(lk, 1.0, "#141414", "#141414", cx=-l + pad, top=-t + pad)
        with open(os.path.join(art.ART, f"lockup-vertical-{c['name'].lower()}.svg"), "w") as fh:
            fh.write(art.svg_doc(W, H, body))


def main():
    os.makedirs(BUILD, exist_ok=True)
    export_art()
    render()
    compose.rasterise([
        {"in": overview(), "out": os.path.join(OUT, "09-vertical-overview.png"), "w": 1600, "h": 1000, "scale": 2},
        {"in": tee_board("07"), "out": os.path.join(OUT, "07-fonseca-vertical-board.png"), "w": 1600, "h": 1000, "scale": 2},
        {"in": tee_board("08"), "out": os.path.join(OUT, "08-shelton-vertical-board.png"), "w": 1600, "h": 1000, "scale": 2},
    ])
    print("vertical boards ok")


if __name__ == "__main__":
    main()
