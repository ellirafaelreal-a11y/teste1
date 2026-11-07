"""
Presentation boards (HTML -> PNG via Chromium).

    python3 src/board.py      (run after compose.py)
"""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art  # noqa: E402
import compose  # noqa: E402

ROOT = art.ROOT
OUT = compose.OUT
BUILD = compose.BUILD
FONTS = art.FONTS
S = compose.SCALE


def crop_detail(src, dst, cx_mm, cy_mm, size_mm, bg):
    im = cv2.imread(src, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    x0 = int((cx_mm - size_mm / 2 - compose.tee.VB[0]) * S)
    y0 = int((cy_mm - size_mm / 2 - compose.tee.VB[1]) * S)
    n = int(size_mm * S)
    c = im[y0:y0 + n, x0:x0 + n]
    a = c[..., 3:4]
    bgc = compose.hex2rgb(bg)[::-1]
    rgb = c[..., :3] * a + bgc * (1 - a)
    cv2.imwrite(dst, (np.clip(rgb, 0, 1) * 255).astype(np.uint8))


def dims():
    """Real print dimensions (mm) computed from the artwork itself."""
    lk = art.lockup_lower()
    l, t, r, b = lk["bbox"]
    d01 = (200.0, 200.0 * (b - t) / (r - l))
    lu = art.lockup_upper()
    l, t, r, b = lu["bbox"]
    d02 = (276.0, 276.0 * (b - t) / (r - l))
    _, W, L = art.court_graphic("#000", width=100.0)
    _, bb = art.call_ended_graphic("#fff", "#0f0", width=262.0)
    ce = (bb[2] - bb[0], bb[3] - bb[1])
    _, wl, _ = art.tiny_text("LEFTY", "#000", cap_mm=5.2, tracking=160)
    return {"01f": d01, "02f": d02, "court": (W, L), "call": ce, "lefty": wl}


def on_svg(color, h=None, cls="onmark"):
    o, n, wm = art.on_mark(0, 100, 100)
    style = f' style="height:{h}"' if h else ""
    return (f'<svg class="{cls}" viewBox="0 -1 {wm:.2f} 103" {style}>'
            f'<path d="{o}" fill="{color}"/><path d="{n}" fill="{color}"/></svg>')


def font_css():
    def ff(name, file, weight="100 900"):
        return (f"@font-face{{font-family:'{name}';src:url('file://{FONTS}/{file}') format('woff2');"
                f"font-weight:{weight};font-display:block}}")
    return "".join([
        ff("Inter Tight", "inter-tight-latin-wght-normal.woff2"),
        ff("Outfit", "outfit-latin-wght-normal.woff2"),
        ff("JB", "jetbrains-mono-latin-400-normal.woff2", "400"),
        ff("JB", "jetbrains-mono-latin-500-normal.woff2", "500"),
        ff("JB", "jetbrains-mono-latin-700-normal.woff2", "700"),
    ])


BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1600px;height:1000px;overflow:hidden}
body{background:var(--bg);color:var(--fg);font-family:'Inter Tight',sans-serif;
  -webkit-font-smoothing:antialiased;position:relative}
.grain{position:absolute;inset:0;pointer-events:none;opacity:.35;mix-blend-mode:multiply;
  background-image:radial-gradient(ellipse at 50% 38%, rgba(255,255,255,.55), rgba(0,0,0,0) 62%),
  radial-gradient(ellipse at 50% 120%, rgba(0,0,0,.10), rgba(0,0,0,0) 60%)}
.mono{font-family:'JB',monospace;letter-spacing:.06em;text-transform:uppercase}
header{position:absolute;left:56px;right:56px;top:44px;display:flex;justify-content:space-between;align-items:flex-start}
.num{font-family:'Outfit';font-weight:200;font-size:112px;line-height:.8;letter-spacing:-.04em}
.titlewrap{display:flex;gap:26px;align-items:flex-end}
.title{font-family:'Outfit';font-weight:700;font-size:40px;letter-spacing:.02em;line-height:1}
.subtitle{font-size:12px;margin-top:10px;color:var(--muted)}
.meta{text-align:right;font-size:11px;line-height:1.75;color:var(--muted)}
.meta b{color:var(--fg);font-weight:700}
.onmark{height:15px;width:auto;vertical-align:-2px}
.stage{position:absolute;left:20px;top:160px;width:1180px;height:760px;display:flex;justify-content:center;gap:0}
.view{position:relative;width:590px;height:760px}
.view img{position:absolute;left:-55px;top:-34px;width:700px;height:700px}
.view .lab{position:absolute;left:40px;right:40px;top:610px;border-top:1px solid var(--rule);padding-top:12px;
  display:flex;justify-content:space-between;font-size:11px}
.view .lab span:first-child{font-weight:700;color:var(--fg)}
.view .lab span{color:var(--muted)}
aside{position:absolute;right:56px;top:178px;width:322px}
aside h4{font-size:10.5px;font-family:'JB';font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);margin:0 0 10px;padding-bottom:8px;border-bottom:1px solid var(--rule)}
aside p{font-size:14px;line-height:1.5;margin-bottom:22px;text-wrap:pretty}
.sw{display:flex;gap:12px;margin-bottom:22px}
.sw div{flex:1}
.chip{height:54px;border-radius:3px;border:1px solid var(--rule);margin-bottom:7px}
.sw .n{font-size:11.5px;font-weight:600;line-height:1.25}
.sw .c{font-family:'JB';font-size:9.5px;color:var(--muted);line-height:1.5;margin-top:2px}
table{width:100%;border-collapse:collapse;font-size:11.5px;margin-bottom:22px}
td{padding:6px 0;border-bottom:1px solid var(--rule);vertical-align:top}
td:first-child{color:var(--muted);width:92px;font-family:'JB';font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding-top:7px}
.detail{display:flex;gap:16px;align-items:center}
.detail img{width:132px;height:132px;border-radius:50%;object-fit:cover;border:1px solid var(--rule)}
.detail span{font-size:11.5px;line-height:1.5;color:var(--muted)}
footer{position:absolute;left:56px;right:56px;bottom:30px;display:flex;justify-content:space-between;
  font-size:9.5px;color:var(--muted)}
"""


def concept_board(cid, d):
    c = compose.CONCEPTS[cid]
    if cid == "01":
        title = "BASELINE"
        sub = "Camiseta de treino &middot; Undyed White"
        concept = ("Minimalismo suíço para o treino do dia a dia. O <b>shelt</b> foi desenhado no mesmo peso "
                   "e na mesma geometria do logo On, então o “on” de Shelton vira a própria marca, sem ruído. "
                   "Nas costas, o mapa do saque canhoto: slice aberto no lado da vantagem.")
        swatches = [
            ("Undyed White", c["tee"], "Malha<br>&asymp; 11-0602 TCX"),
            ("Black", compose.INK_BLACK, "Tinta<br>&asymp; Black 6 C"),
        ]
        rows = [
            ("Frente", f"Wordmark shelt&#8203;On &middot; {d['01f'][0]:.0f} &times; {d['01f'][1]:.0f} mm &middot; centro, 5,4 cm abaixo da gola"),
            ("Costas", f"Mapa de quadra (escala ITF) &middot; {d['court'][0]:.0f} &times; {d['court'][1]:.0f} mm &middot; 5 cm abaixo da gola"),
            ("Manga E.", f"LEFTY &middot; {d['lefty']:.0f} mm, no sentido do braço"),
            ("Nuca", "Logo On &middot; 20 mm"),
            ("Técnica", "Silk base d'água, toque zero"),
            ("Malha", "Poliéster reciclado 130 g/m², malha técnica respirável"),
        ]
        lab_front = ("FRENTE", "shelt + On &middot; peito")
        lab_back = ("COSTAS", "Serve map &middot; slice canhoto")
        detail_cap = "Detalhe da estampa: tinta preta fosca acompanhando a trama e as dobras da malha."
        bg, fg, muted, rule = "#E0DED8", "#141414", "#74726c", "rgba(20,20,20,.14)"
        detail = ("01", "front", 562, 343, 84)
    else:
        title = "CALL ENDED."
        sub = "Camiseta de treino &middot; Black / Lime"
        concept = ("Feita para aparecer. <b>SHELT</b> em caixa-alta branca e o On em lime, o único ponto de cor da peça. "
                   "Nas costas, a referência à comemoração mais famosa dele: desligar o telefone "
                   "depois de fechar o jogo.")
        swatches = [
            ("Black", c["tee"], "Malha<br>&asymp; 19-0303 TCX"),
            ("White", compose.INK_WHITE, "Tinta<br>branco opaco"),
            ("Lime", compose.LIME, "Tinta<br>&asymp; 380 C"),
        ]
        rows = [
            ("Frente", f"Wordmark SHELT&#8203;On &middot; {d['02f'][0]:.0f} &times; {d['02f'][1]:.0f} mm &middot; centro, 5,8 cm abaixo da gola"),
            ("Costas", f"CALL ENDED. &middot; {d['call'][0]:.0f} &times; {d['call'][1]:.0f} mm &middot; 4 cm abaixo da gola"),
            ("Manga E.", f"LEFTY lime &middot; {d['lefty']:.0f} mm, no sentido do braço"),
            ("Nuca", "Logo On lime &middot; 20 mm"),
            ("Técnica", "Silk plastisol soft-hand; On lime em transfer de silicone"),
            ("Malha", "Poliéster reciclado 130 g/m², malha técnica respirável"),
        ]
        lab_front = ("FRENTE", "SHELT + On lime &middot; peito")
        lab_back = ("COSTAS", "Hang-up &middot; call ended")
        detail_cap = "Detalhe: branco soft-hand e o On em lime, com a trama aparecendo de leve."
        bg, fg, muted, rule = "#E6E4DF", "#141414", "#75736d", "rgba(20,20,20,.14)"
        detail = ("02", "front", 597, 349, 96)

    det_png = os.path.join(BUILD, f"detail-{cid}.png")
    crop_detail(os.path.join(OUT, f"tee-{detail[0]}-{detail[1]}.png"), det_png,
                detail[2], detail[3], detail[4], c["tee"])

    sw_html = "".join(
        f'<div><div class="chip" style="background:{h}"></div><div class="n">{n}</div>'
        f'<div class="c">{h.upper()}<br>{note}</div></div>'
        for n, h, note in swatches
    )
    rows_html = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}
:root{{--bg:{bg};--fg:{fg};--muted:{muted};--rule:{rule}}}{BASE_CSS}</style></head><body>
<div class="grain"></div>
<header>
  <div class="titlewrap"><div class="num">{cid}</div>
    <div><div class="title">{title}</div><div class="subtitle mono">{sub}</div></div></div>
  <div class="meta mono"><b>Ben Shelton &times; {on_svg(fg)}</b><br>Training tee &middot; Concept<br>Tennis &middot; SS27</div>
</header>
<div class="stage">
  <div class="view"><img src="file://{OUT}/tee-{cid}-front.png">
    <div class="lab mono"><span>{lab_front[0]}</span><span>{lab_front[1]}</span></div></div>
  <div class="view"><img src="file://{OUT}/tee-{cid}-back.png">
    <div class="lab mono"><span>{lab_back[0]}</span><span>{lab_back[1]}</span></div></div>
</div>
<aside>
  <h4>Conceito</h4><p>{concept}</p>
  <h4>Cores</h4><div class="sw">{sw_html}</div>
  <h4>Aplicações &middot; tam. M</h4><table>{rows_html}</table>
  <div class="detail"><img src="file://{det_png}"><span>{detail_cap}</span></div>
</aside>
<footer class="mono"><span>Conceito não oficial para apresentação &middot; Logo On redesenhado: usar o vetor oficial da marca na produção</span>
<span>Shelton &times; On &middot; {cid}/02</span></footer>
</body></html>"""
    p = os.path.join(BUILD, f"board-{cid}.html")
    with open(p, "w") as fh:
        fh.write(html)
    return p


def overview_board():
    fg = "#141414"
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}
:root{{--bg:#E2E0DA;--fg:{fg};--muted:#77756f;--rule:rgba(20,20,20,.14)}}{BASE_CSS}
.ov{{position:absolute;left:0;right:0;top:120px;display:flex;justify-content:center;gap:10px}}
.ov figure{{position:relative;width:740px;height:800px}}
.ov img{{position:absolute;left:-10px;top:0;width:760px;height:760px}}
.ov figcaption{{position:absolute;left:70px;right:70px;top:745px;display:flex;justify-content:space-between;
  border-top:1px solid var(--rule);padding-top:12px;font-size:11px;color:var(--muted)}}
.ov figcaption b{{color:var(--fg)}}
.big{{font-family:'Outfit';font-weight:700;font-size:30px;letter-spacing:.01em}}
</style></head><body><div class="grain"></div>
<header><div><div class="big">Shelton &times; {on_svg(fg, '24px')}</div>
<div class="subtitle mono">Camisetas de treino &middot; 2 conceitos</div></div>
<div class="meta mono"><b>Ben Shelton</b><br>On Tennis &middot; Concept<br>SS27</div></header>
<div class="ov">
<figure><img src="file://{OUT}/tee-01-front.png"><figcaption class="mono"><span><b>01</b> &nbsp;Baseline</span><span>Undyed White / Black</span></figcaption></figure>
<figure><img src="file://{OUT}/tee-02-front.png"><figcaption class="mono"><span><b>02</b> &nbsp;Call Ended.</span><span>Black / White / Lime</span></figcaption></figure>
</div>
<footer class="mono"><span>Conceito não oficial para apresentação &middot; Logo On redesenhado: usar o vetor oficial da marca na produção</span><span>00</span></footer>
</body></html>"""
    p = os.path.join(BUILD, "board-00.html")
    with open(p, "w") as fh:
        fh.write(html)
    return p


def main():
    d = dims()
    jobs = []
    for name, p in [("00-overview", overview_board()),
                    ("01-baseline-board", concept_board("01", d)),
                    ("02-call-ended-board", concept_board("02", d))]:
        jobs.append({"in": p, "out": os.path.join(OUT, name + ".png"), "w": 1600, "h": 1000, "scale": 2})
    compose.rasterise(jobs)
    print("boards ok", d)


if __name__ == "__main__":
    main()
