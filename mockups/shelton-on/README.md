# Shelton × On: camisetas de treino (conceito)

Dois mockups de camiseta de treino para Ben Shelton, com o "on" de SHELTON
substituído pelo logo da On.

| | Conceito | Cor | Frente | Costas |
| --- | --- | --- | --- | --- |
| 01 | **Baseline** | Undyed White / tinta preta | `shelt` + On em caixa-baixa, 200 × 42 mm | Mapa de quadra em escala ITF com o slice canhoto no lado da vantagem |
| 02 | **Call Ended.** | Black / branco + lime | `SHELT` branco + On lime, 276 × 44 mm | "CALL ENDED.", referência à comemoração de desligar o telefone |

## Arquivos

- `output/00-overview.png`: as duas frentes lado a lado (3200 × 2000)
- `output/01-baseline-board.png`, `output/02-call-ended-board.png`: pranchas com frente,
  costas, cores, medidas de aplicação e detalhe da estampa (3200 × 2000)
- `output/tee-0X-{front,back}.png`: renders isolados em PNG transparente (2400 × 2400)
- `art/*.svg`: artes vetoriais já em curvas, em milímetros no tamanho real de impressão

## Como o lettering funciona

O `shelt` usa a Outfit 700, uma fonte geométrica. Ela foi escalada para que a altura-x
dela seja igual à altura do "n" do logo e a haste fique com a mesma espessura do anel
do "O" (cerca de 21% do diâmetro). Assim o logo On fecha a palavra sem quebra de peso
nem de ritmo. Na versão em caixa-alta, a altura das maiúsculas acompanha o diâmetro do "O".

> **Importante:** o símbolo On deste repositório é um **redesenho** feito para a
> apresentação (`art/on-mark-redraw.svg`). Na produção, troque pelo vetor oficial do
> brand portal da On. É um conceito não oficial: uso comercial depende de licença da
> On e do atleta.

## Como regerar

Requer Python 3 (numpy, opencv-python-headless, fonttools, brotli) e Node com Playwright/Chromium.

```bash
python3 src/compose.py   # artes SVG + renders das camisetas -> art/, output/
python3 src/board.py     # pranchas de apresentação -> output/
```

Pipeline: `art.py` gera os vetores (glifos convertidos em curvas com fontTools),
`tee.py` desenha a camiseta em vetor (silhueta, recortes, dobras e costuras),
`shot.mjs` rasteriza no Chromium e `compose.py` faz o sombreamento em espaço linear:
volume por distância à borda, oclusão nas axilas, brilho no tecido preto e trama de malha.
A estampa é deslocada pelo relevo das dobras e recebe a mesma luz do tecido.
