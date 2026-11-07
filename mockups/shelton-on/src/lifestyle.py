"""
Lifestyle tees with the horizontal (un-stacked) On lettering:
03 SHELTON and 04 FONSECA, plus a lettering sheet and an overview.

    python3 src/lifestyle.py     (after compose.py has been run once)
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

OUT = compose.OUT
BUILD = compose.BUILD
S = compose.SCALE
HPS_Y = 178.0

LIFESTYLE = {
    "03": {
        "name": "shelton", "pre": "shelt", "suf": "", "full": "BEN SHELTON", "place": "FLORIDA, USA", "full_d": "Ben Shelton", "place_d": "Florida, USA",
        "tee": "#E7E0CE", "tee_name": "Ecru",
        "ink": "#1D2A44", "ink_name": "Navy",
        "on": "#E2672B", "on_name": "Orange",
        "width": 232.0, "top": 302.0,
        "spec": 0.008, "fresnel": 0.0, "label_ink": "#a19a88",
        "opacity": 0.985, "grain": 0.02,
        "bg": "#DEDAD0",
        "pantone": ("&asymp; 12-0304 TCX", "&asymp; 533 C", "&asymp; 7578 C"),
        "tech": "Silk base d'água, toque zero",
        "concept": ("Fora da quadra. O símbolo On desmontado na horizontal: o <b>o</b> com a haste e o "
                    "<b>n</b> entram no lugar do “on”, e o nome se lê de uma vez, <b>shelton</b>. "
                    "Ecru com navy e o On em laranja, um aceno à Flórida, onde ele cresceu."),
    },
    "04": {
        "name": "fonseca", "pre": "f", "suf": "seca", "full": "JOÃO FONSECA", "place": "RIO DE JANEIRO, BR", "full_d": "João Fonseca", "place_d": "Rio de Janeiro, BR",
        "tee": "#24423A", "tee_name": "Forest",
        "ink": "#EEE7D5", "ink_name": "Ecru",
        "on": "#F2C230", "on_name": "Canary",
        "width": 244.0, "top": 302.0,
        "spec": 0.022, "fresnel": 0.012, "label_ink": "#6f8a80",
        "opacity": 0.95, "grain": 0.045,
        "bg": "#DDDAD2",
        "pantone": ("&asymp; 19-5420 TCX", "&asymp; 9224 C", "&asymp; 123 C"),
        "tech": "Silk discharge (toque zero em malha escura)",
        "concept": ("O “on” de Fonseca também vira o símbolo On, no meio do nome. Verde floresta, "
                    "letras em ecru e o On em amarelo canário: Brasil sem precisar de bandeira. "
                    "Na nuca, o Rio de Janeiro, a cidade dele."),
    },
}


def lockup(cid):
    c = LIFESTYLE[cid]
    return art.lockup_inline(c["pre"], c["suf"], "lower")


def placed(cid):
    c = LIFESTYLE[cid]
    lk = lockup(cid)
    l, t, r, b = lk["bbox"]
    k = c["width"] / (r - l)
    ox, oy = 500 - c["width"] / 2, c["top"]
    on0, on1 = lk["on_span"]
    on_box = (ox + (on0 - l) * k, oy, ox + (on1 - l) * k, oy + (b - t) * k)
    svg = (f'<g transform="translate({ox:.3f},{oy:.3f})">'
           f'{art.inline_group(lk, k, c["ink"], c["on"])}</g>')
    return svg, (c["width"], (b - t) * k), on_box


def print_svg(cid, view):
    c = LIFESTYLE[cid]
    x0, y0, w0, h0 = tee_boxy.VB
    g = []
    if view == "front":
        g.append(placed(cid)[0])
    else:
        g.append(compose.neck_mark(c["on"], top=230.0, body=18.0))
        d1, w1, _ = art.tiny_text(c["full"], c["ink"], cap_mm=3.6, tracking=170)
        d2, w2, _ = art.tiny_text(c["place"], c["ink"], cap_mm=2.6, tracking=170, f=art.font(art.MONO_R))
        g.append(f'<path transform="translate({500 - w1/2:.3f},{266:.3f})" d="{d1}" fill="{c["ink"]}"/>')
        g.append(f'<path transform="translate({500 - w2/2:.3f},{273.5:.3f})" d="{d2}" fill="{c["ink"]}"/>')
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
    for cid, c in LIFESTYLE.items():
        compose.CONCEPTS[cid] = {"tee": c["tee"], "spec": c["spec"], "fresnel": c["fresnel"],
                                 "label_ink": c["label_ink"]}
        for view in ("front", "back"):
            sp = os.path.join(BUILD, f"print-{cid}-{view}.svg")
            with open(sp, "w") as fh:
                fh.write(print_svg(cid, view))
            jobs.append({"in": sp, "out": sp[:-4] + ".png", "w": 1000, "h": 1000, "scale": S,
                         "transparent": True})
            prints[(cid, view)] = [{"file": sp[:-4] + ".png", "opacity": c["opacity"],
                                    "grain": c["grain"], "spec": 0.006}]
        lp = os.path.join(BUILD, f"label-{cid}.svg")
        with open(lp, "w") as fh:
            fh.write(compose.neck_label_svg(cid))
        jobs.append({"in": lp, "out": lp[:-4] + ".png", "w": 1000, "h": 1000, "scale": S,
                     "transparent": True})
        prints[(cid, "front")].insert(0, {"file": lp[:-4] + ".png", "inside": True,
                                          "opacity": 0.9, "spec": 0.0})
    compose.rasterise(jobs)

    for view in ("front", "back"):
        M = {k: compose.load_gray(p, k in ("seams", "hilite")) for k, p in maps[view].items()}
        if "inside" not in M:
            M["inside"] = np.zeros((compose.N, compose.N), np.float32)
        wx, wy = compose.cloth_warp(seed=31 if view == "front" else 37, amp_px=3.8)
        M = {k: cv2.remap(v, wx, wy, cv2.INTER_LINEAR) for k, v in M.items()}
        for cid in LIFESTYLE:
            ps = []
            for p in prints[(cid, view)]:
                rgb, a = compose.load_rgba(p["file"])
                q = dict(p)
                q["rgb"] = cv2.remap(rgb, wx, wy, cv2.INTER_LINEAR)
                q["a"] = cv2.remap(a, wx, wy, cv2.INTER_LINEAR)
                ps.append(q)
            rgba = compose.composite(cid, view, M, ps)
            compose.save_rgba(os.path.join(OUT, f"tee-{cid}-{view}.png"), rgba)
            print("rendered", cid, view)


# ------------------------------------------------------------------ boards --

def lockup_svg(lk, height_px, ink, on):
    l, t, r, b = lk["bbox"]
    k = height_px / (b - t)
    w = (r - l) * k
    return (f'<svg width="{w:.1f}" height="{height_px:.1f}" viewBox="0 0 {w:.2f} {height_px:.2f}">'
            f'{art.inline_group(lk, k, ink, on)}</svg>')


def cm(v):
    return f"{v:.1f}".replace(".", ",") + " cm"


def tee_board(cid):
    c = LIFESTYLE[cid]
    _, size, on_box = placed(cid)
    det = os.path.join(BUILD, f"detail-{cid}.png")
    board.crop_detail(os.path.join(OUT, f"tee-{cid}-front.png"), det,
                      (on_box[0] + on_box[2]) / 2, (on_box[1] + on_box[3]) / 2 + 4, 96, c["tee"])
    sw = [(c["tee_name"], c["tee"], f"Malha<br>{c['pantone'][0]}"),
          (c["ink_name"], c["ink"], f"Tinta<br>{c['pantone'][1]}"),
          (c["on_name"], c["on"], f"Tinta On<br>{c['pantone'][2]}")]
    sw_html = "".join(
        f'<div><div class="chip" style="background:{h}"></div><div class="n">{n}</div>'
        f'<div class="c">{h.upper()}<br>{note}</div></div>' for n, h, note in sw)
    rows = [
        ("Frente", f"Wordmark {c['name']} &middot; {size[0]:.0f} &times; {size[1]:.0f} mm &middot; centro, "
                   f"topo {cm((c['top'] - HPS_Y) / 10)} abaixo do ombro (HPS)"),
        ("Nuca", f"Símbolo On 18 mm + {c['full_d']} / {c['place_d']}"),
        ("Malha", "Algodão orgânico 240 g/m², penteado"),
        ("Modelagem", "Oversized, ombro caído, gola em ribana 2,4 cm"),
        ("Técnica", c["tech"]),
    ]
    rows_html = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    title = lockup_svg(lockup(cid), 50, "#141414", "#141414")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{board.font_css()}
:root{{--bg:{c['bg']};--fg:#141414;--muted:#74726c;--rule:rgba(20,20,20,.14)}}{board.BASE_CSS}
.ttl{{display:flex;flex-direction:column;gap:12px}}
.view img{{left:-30px;top:-40px;width:650px;height:650px}}
.view .lab{{top:572px}}
</style></head><body><div class="grain"></div>
<header>
  <div class="titlewrap"><div class="num">{cid}</div>
    <div class="ttl">{title}<div class="subtitle mono">Camiseta lifestyle &middot; {c['tee_name']} / {c['ink_name']} / {c['on_name']}</div></div></div>
  <div class="meta mono"><b>{c['full_d']} &times; {board.on_svg('#141414')}</b><br>Lifestyle tee &middot; Concept<br>On Tennis &middot; SS27</div>
</header>
<div class="stage">
  <div class="view"><img src="file://{OUT}/tee-{cid}-front.png">
    <div class="lab mono"><span>FRENTE</span><span>{c['name']} &middot; On na horizontal</span></div></div>
  <div class="view"><img src="file://{OUT}/tee-{cid}-back.png">
    <div class="lab mono"><span>COSTAS</span><span>Nuca &middot; {c['place_d']}</span></div></div>
</div>
<aside>
  <h4>Conceito</h4><p>{c['concept']}</p>
  <h4>Cores</h4><div class="sw">{sw_html}</div>
  <h4>Aplicações &middot; tam. M</h4><table>{rows_html}</table>
  <div class="detail"><img src="file://{det}"><span>Detalhe: o <b>o</b> com a haste e o <b>n</b> do símbolo On lado a lado, no ritmo das outras letras.</span></div>
</aside>
<footer class="mono"><span>Conceito não oficial para apresentação &middot; Símbolo On reconstruído e desmontado: validar com a marca antes da produção</span>
<span>On Tennis &middot; Lifestyle &middot; {cid}</span></footer>
</body></html>"""
    p = os.path.join(BUILD, f"board-{cid}.html")
    with open(p, "w") as fh:
        fh.write(html)
    return p


def lettering_sheet():
    cells = []
    specs = [("shelt", "", "lower"), ("f", "seca", "lower"), ("shelt", "", "upper"), ("f", "seca", "upper")]
    for pre, suf, case in specs:
        lk = art.lockup_inline(pre, suf, case)
        lab = ("caixa-baixa" if case == "lower" else "caixa-alta")
        name = (pre + "on" + suf)
        cells.append(f"""<div class="cell light">{lockup_svg(lk, 92 if case == 'lower' else 70, '#141414', '#141414')}
<span class="mono">{name} &middot; {lab} &middot; Outfit {lk['wght']:.0f}</span></div>""")
    for pre, suf, ink, on, bg in [("shelt", "", "#1D2A44", "#E2672B", "#E7E0CE"),
                                  ("f", "seca", "#EEE7D5", "#F2C230", "#24423A")]:
        lk = art.lockup_inline(pre, suf, "lower")
        cells.append(f"""<div class="cell" style="background:{bg}">{lockup_svg(lk, 92, ink, on)}
<span class="mono" style="color:{ink};opacity:.7">{pre}on{suf} &middot; cores da camiseta</span></div>""")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{board.font_css()}
:root{{--bg:#E2E0DA;--fg:#141414;--muted:#74726c;--rule:rgba(20,20,20,.14)}}{board.BASE_CSS}
.grid{{position:absolute;left:56px;right:56px;top:170px;bottom:120px;display:grid;
  grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr 1fr;gap:18px}}
.cell{{position:relative;border-radius:4px;display:flex;align-items:center;justify-content:center;background:#ECEAE4}}
.cell span{{position:absolute;left:20px;bottom:14px;font-size:10px;color:var(--muted)}}
.note{{position:absolute;left:56px;right:56px;bottom:62px;font-size:13px;color:var(--muted);max-width:1100px}}
.big{{font-family:'Outfit';font-weight:700;font-size:30px}}
</style></head><body><div class="grain"></div>
<header><div><div class="big">Lettering &middot; On na horizontal</div>
<div class="subtitle mono">O símbolo On desmontado: o + n lado a lado, no lugar do “on”</div></div>
<div class="meta mono"><b>Shelton &middot; Fonseca</b><br>On Tennis &middot; Lifestyle<br>SS27</div></header>
<div class="grid">{''.join(cells)}</div>
<p class="note">O “o” mantém a haste a 45° e o “n” mantém o arco do símbolo; os dois ficam com a altura das
letras ao redor. O peso da Outfit é calculado para que a haste das letras tenha a mesma espessura do traço do símbolo.</p>
<footer class="mono"><span>Conceito não oficial &middot; Símbolo On reconstruído: validar com a marca antes da produção</span><span>Lettering</span></footer>
</body></html>"""
    p = os.path.join(BUILD, "board-lettering.html")
    with open(p, "w") as fh:
        fh.write(html)
    return p


def overview():
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{board.font_css()}
:root{{--bg:#E0DDD6;--fg:#141414;--muted:#74726c;--rule:rgba(20,20,20,.14)}}{board.BASE_CSS}
.ov{{position:absolute;left:0;right:0;top:120px;display:flex;justify-content:center;gap:10px}}
.ov figure{{position:relative;width:740px;height:800px}}
.ov img{{position:absolute;left:-10px;top:0;width:760px;height:760px}}
.ov figcaption{{position:absolute;left:70px;right:70px;top:745px;display:flex;justify-content:space-between;
  border-top:1px solid var(--rule);padding-top:12px;font-size:11px;color:var(--muted)}}
.ov figcaption b{{color:var(--fg)}}
.big{{font-family:'Outfit';font-weight:700;font-size:30px}}
</style></head><body><div class="grain"></div>
<header><div><div class="big">On Tennis &middot; Lifestyle</div>
<div class="subtitle mono">Shelton &middot; Fonseca &middot; On na horizontal</div></div>
<div class="meta mono"><b>{board.on_svg('#141414', '30px')}</b><br>Concept &middot; SS27</div></header>
<div class="ov">
<figure><img src="file://{OUT}/tee-03-front.png"><figcaption class="mono"><span><b>03</b> &nbsp;shelton</span><span>Ecru / Navy / Orange</span></figcaption></figure>
<figure><img src="file://{OUT}/tee-04-front.png"><figcaption class="mono"><span><b>04</b> &nbsp;fonseca</span><span>Forest / Ecru / Canary</span></figcaption></figure>
</div>
<footer class="mono"><span>Conceito não oficial para apresentação &middot; Símbolo On reconstruído: validar com a marca antes da produção</span><span>Lifestyle</span></footer>
</body></html>"""
    p = os.path.join(BUILD, "board-lifestyle-00.html")
    with open(p, "w") as fh:
        fh.write(html)
    return p


def export_art():
    for cid, c in LIFESTYLE.items():
        lk = lockup(cid)
        l, t, r, b = lk["bbox"]
        W = c["width"]
        k = W / (r - l)
        H = (b - t) * k
        with open(os.path.join(art.ART, f"lockup-horizontal-{c['name']}.svg"), "w") as fh:
            fh.write(art.svg_doc(W, H, art.inline_group(lk, k, c["ink"], c["on"])))
        lu = art.lockup_inline(c["pre"], c["suf"], "upper")
        l, t, r, b = lu["bbox"]
        k = W / (r - l)
        with open(os.path.join(art.ART, f"lockup-horizontal-{c['name']}-caps.svg"), "w") as fh:
            fh.write(art.svg_doc(W, (b - t) * k, art.inline_group(lu, k, "#141414")))


def main():
    os.makedirs(BUILD, exist_ok=True)
    export_art()
    render()
    jobs = [
        {"in": overview(), "out": os.path.join(OUT, "05-lifestyle-overview.png"), "w": 1600, "h": 1000, "scale": 2},
        {"in": lettering_sheet(), "out": os.path.join(OUT, "06-lettering-horizontal.png"), "w": 1600, "h": 1000, "scale": 2},
        {"in": tee_board("03"), "out": os.path.join(OUT, "03-shelton-lifestyle-board.png"), "w": 1600, "h": 1000, "scale": 2},
        {"in": tee_board("04"), "out": os.path.join(OUT, "04-fonseca-lifestyle-board.png"), "w": 1600, "h": 1000, "scale": 2},
    ]
    compose.rasterise(jobs)
    print("lifestyle boards ok")


if __name__ == "__main__":
    main()
