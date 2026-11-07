# Shelton × On: camisetas de treino (conceito)

Dois mockups de camiseta de treino para Ben Shelton, com o "on" de SHELTON
substituído pelo logo da On.

| | Conceito | Cor | Frente | Costas |
| --- | --- | --- | --- | --- |
| 01 | **Baseline** | Undyed White / tinta preta | `shelt` + símbolo On, 190 × 73 mm | Mapa de quadra em escala ITF com o slice canhoto no lado da vantagem |
| 02 | **Call Ended.** | Black / branco + lime | `SHELT` branco + símbolo On lime, 250 × 91 mm | "CALL ENDED.", referência à comemoração de desligar o telefone |

### Lifestyle com o On na horizontal

| | Atleta | Cor | Frente | Nuca |
| --- | --- | --- | --- | --- |
| 03 | **shelton** | Ecru / navy + On laranja | `shelt` + o + n em linha, 232 × 52 mm | Símbolo On + "BEN SHELTON / FLORIDA, USA" |
| 04 | **fonseca** | Forest / ecru + On amarelo canário | `f` + o + n + `seca`, 244 × 51 mm | Símbolo On + "JOÃO FONSECA / RIO DE JANEIRO, BR" |

Aqui o símbolo é desmontado: o "o" com a haste e o "n" ficam lado a lado no lugar do
"on", na altura das letras, e o nome se lê de uma vez. A camiseta é outra modelagem
(`tee_boxy.py`): oversized, ombro caído, algodão 240 g/m² e gola larga.

### Lettering vertical (a partir da referência)

| | Atleta | Cor | Costas | Frente |
| --- | --- | --- | --- | --- |
| 07 | **FONSECA** | Heather grey (mescla) / preto | F · o · n · S · E · C · A em coluna, 43 × 449 mm | FONSECA com On horizontal, 78 mm, peito esquerdo |
| 08 | **SHELTON** | Preto / ecru | S · H · E · L · T · o · n em coluna | SHELTON com On horizontal, 78 mm, peito esquerdo |

Com o nome escrito de cima para baixo, o símbolo On entra inteiro e na ordem original,
o "o" em cima e o "n" embaixo. O "o" e o "n" seguem o mesmo tamanho e o mesmo
espaçamento das letras da coluna.

## Arquivos

- `output/00-overview.png`: as duas frentes lado a lado (3200 × 2000)
- `output/01-baseline-board.png`, `output/02-call-ended-board.png`: pranchas com frente,
  costas, cores, medidas de aplicação e detalhe da estampa (3200 × 2000)
- `output/tee-0X-{front,back}.png`: renders isolados em PNG transparente (2400 × 2400)
- `output/05-lifestyle-overview.png`, `output/03-shelton-lifestyle-board.png`,
  `output/04-fonseca-lifestyle-board.png`: camisetas lifestyle com o On na horizontal
- `output/06-lettering-horizontal.png`: folha de lettering (minúsculas e maiúsculas, Shelton e Fonseca)
- `art/*.svg`: artes vetoriais já em curvas, em milímetros no tamanho real de impressão
  (inclui `lockup-horizontal-*.svg` e `lockup-vertical-*.svg`)
- `output/09-vertical-overview.png`, `output/07-fonseca-vertical-board.png`,
  `output/08-shelton-vertical-board.png`: lettering vertical nas costas

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
python3 src/lifestyle.py # camisetas lifestyle 03/04 + lettering horizontal -> output/
python3 src/vertical.py  # camisetas 07/08 com lettering vertical -> output/
```

Pipeline: `art.py` gera os vetores (glifos convertidos em curvas com fontTools),
`tee.py` desenha a camiseta em vetor (silhueta, recortes, dobras e costuras),
`shot.mjs` rasteriza no Chromium e `compose.py` faz o sombreamento em espaço linear:
volume por distância à borda, oclusão nas axilas, brilho no tecido preto e trama de malha.
A estampa é deslocada pelo relevo das dobras e recebe a mesma luz do tecido.

## Mockups realistas (IA)

`output/10-mockups-realistas.png` junta as três fotos geradas na Higgsfield (Nano Banana 2.1):

- `higgsfield/hf-02-campaign.png`: treino 02, em quadra
- `higgsfield/hf-03-shelton-lifestyle.png`: lifestyle 03 (shelton com On horizontal), num café
- `higgsfield/hf-07-fonseca-vertical.png`: lifestyle 07 (FONSECA vertical nas costas), no calçadão de Copacabana

As pessoas são fictícias e aparecem sem rosto. As referências enviadas estão em `higgsfield/refs/`.

### Foto de campanha (IA)

`higgsfield/hf-02-campaign.png` é uma foto de campanha do conceito 02 (1856 × 2304), gerada
na Higgsfield com o modelo Nano Banana 2.1. As referências enviadas estão em
`higgsfield/refs/`: o render da camiseta e a arte vetorial do nome.

O atleta é anônimo e aparece enquadrado sem o rosto. A IA reproduziu bem o nome e o
símbolo, mas deixou o traço do símbolo um pouco mais fino que o original. Use a foto
como imagem de clima; para aplicação exata do logo, valem as artes em `art/`.
