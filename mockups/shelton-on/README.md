# Shelton × On: camisetas de treino (conceito)

Dois mockups de camiseta de treino para Ben Shelton, com o "on" de SHELTON
substituído pelo logo da On.

| | Conceito | Cor | Frente | Costas |
| --- | --- | --- | --- | --- |
| 01 | **Baseline** | Undyed White / tinta preta | `shelt` + símbolo On, 190 × 73 mm | Mapa de quadra em escala ITF com o slice canhoto no lado da vantagem |
| 02 | **Call Ended.** | Black / branco + lime | `SHELT` branco + símbolo On lime, 250 × 91 mm | "CALL ENDED.", referência à comemoração de desligar o telefone |

## Arquivos

- `output/00-overview.png`: as duas frentes lado a lado (3200 × 2000)
- `output/01-baseline-board.png`, `output/02-call-ended-board.png`: pranchas com frente,
  costas, cores, medidas de aplicação e detalhe da estampa (3200 × 2000)
- `output/tee-0X-{front,back}.png`: renders isolados em PNG transparente (2400 × 2400)
- `art/*.svg`: artes vetoriais já em curvas, em milímetros no tamanho real de impressão

## Como o lettering funciona

O símbolo On (o "o" com a haste a 45° empilhado sobre o "n") entra no lugar das letras
"on" **sem nenhuma alteração**. As proporções foram medidas em quatro cópias do logo
oficial, com variação abaixo de 1%:

- **anel:** traço de 0,228 D, sendo D o diâmetro externo
- **haste:** a 45°, largura de 0,241 D, terminando a 0,71 D do centro
- **"n":** 0,967 × 0,98 D, com traço de 0,242 D
- **vão entre o "o" e o "n":** 0,115 D

A tipografia é que se adapta ao símbolo:
- O "n" do logo fica na altura-x (ou na altura das maiúsculas) e serve de última letra da palavra.
- O peso da Outfit é calculado para que a haste das letras tenha a mesma espessura do
  traço do "n": wght 541 em `shelt` e 782 em `SHELT`.
- O "o" sobe acima da linha, como a bola no lançamento do saque.

> **Importante:** o símbolo deste repositório é uma **reconstrução** feita a partir de
> imagens de referência (`art/on-mark-redraw.svg`). Na produção, troque pelo vetor
> oficial do brand portal da On. É um conceito não oficial: uso comercial depende de
> licença da On e do atleta.

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

## Foto de campanha (IA)

`higgsfield/hf-02-campaign.png` é uma foto de campanha do conceito 02 (1856 × 2304), gerada
na Higgsfield com o modelo Nano Banana 2.1. As referências enviadas estão em
`higgsfield/refs/`: o render da camiseta e a arte vetorial do nome.

O atleta é anônimo e aparece enquadrado sem o rosto. A IA reproduziu bem o nome e o
símbolo, mas deixou o traço do símbolo um pouco mais fino que o original. Use a foto
como imagem de clima; para aplicação exata do logo, valem as artes em `art/`.
