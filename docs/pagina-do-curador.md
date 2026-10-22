# Página do curador

Cada curador tem uma página de perfil em `site/cinemateca.html#curador/<id>`. Ela mostra só o perfil, sem a lista de filmes, e tem um botão que leva ao catálogo já filtrado pela curadoria dele.

O código fica em `site/template.html`: CSS em `/* Página do curador */` e JS em `renderCurator()`. Os dados ficam em `curators.json`.

## Dados (`curators.json`)

```json
{
  "id": "gisele-britto",
  "name": "Gisele Britto",
  "role": "Curadora",
  "color": "#a77bff",
  "photo": {"base": "curadores/gisele-britto", "widths": [96, 480, 800, 1200]},
  "screen": {"film": "tt0076162", "video": "curadores/gisele-britto-tela.mp4", "poster": "curadores/gisele-britto-tela.webp",
             "videoMobile": "curadores/gisele-britto-tela-mobile.mp4", "posterMobile": "curadores/gisele-britto-tela-mobile.webp"},
  "default": true,
  "bio": ["parágrafo 1", "parágrafo 2", "…"],
  "films": ["tt…"]
}
```

| Campo | Para quê |
| --- | --- |
| `id` | rota (`#curador/<id>`) e prefixo dos arquivos em `site/curadores/` |
| `name` | título da página; a última palavra vai na cor do curador |
| `role` | "Curadora" ou "Curador"; aparece em "Curadora da Cinemateca Estranha" |
| `color` | cor do curador na página dele (Gisele: roxo). Sem ela, usa o laranja do site |
| `photo` | retrato em WebP, em várias larguras (`<base>-<largura>.webp`) |
| `screen` | trecho de filme que passa na tela atrás do retrato (opcional) |
| `bio` | um item por parágrafo; `**trecho**` vira destaque em negrito |
| `films` | ids do IMDb dos filmes do curador |
| `default` | quem fica com os filmes que não estão no `films` de ninguém (só um curador) |

Um filme pode ter vários curadores. Basta ele estar no `films` de cada um. Para um filme ser do curador `default` e também de outro, ele precisa estar listado no `films` dos dois.

Depois de editar, rode `python3 scripts/finalize.py .`.

## Layout

- **Desktop:** retrato à esquerda (até 400px) e texto à direita.
- **Celular (≤760px):** retrato em cima (até 380px) e texto embaixo.
- A seção fica sempre escura, como a hero, mesmo no tema claro.
- Coluna do texto, de cima para baixo:
  - "← Todo o catálogo";
  - "Curadora da Cinemateca Estranha", em mono e na cor do curador;
  - o nome, enorme, em Big Shoulders, com a última palavra na cor do curador (como "Cinemateca **Estranha**" na marca);
  - os números, calculados dos filmes: filmes, países, sessões, do ano mais antigo ao mais novo;
  - o botão "Ver os N filmes da curadoria";
  - a bio:
    - a capitular de letreiro tem quatro linhas de altura e vai na cor do curador, com duas cópias deslocadas em contorno, como impressão fora de registro;
    - os trechos marcados com `**…**` aparecem em negrito branco, com um grifo na cor do curador.
- Na página do curador ficam escondidos a hero, as sessões, os filtros e a grade. A aba do navegador mostra "<nome> · Cinemateca Estranha".

## Retrato

- **Formato da foto:** quadrada, com fundo **transparente** e a figura encostada na borda de baixo. É o recorte que todos os curadores devem ter.
- **Arquivos:** WebP com transparência em 96, 480, 800 e 1200px. O 96 é o avatar da linha "Curadoria" na ficha de cada filme. Os outros vão no `srcset`: o celular baixa o de 480, e o desktop, o de 800.

  ```sh
  for w in 96 480 800 1200; do
    cwebp -resize $w 0 -q 78 -alpha_q 90 -m 6 foto.png -o site/curadores/<id>-$w.webp
  done
  ```

- **Moldura:** a área do retrato é um pouco mais alta que larga (1:1,13). A figura fica embaixo, com sombra projetada.
- **Entrada:** ao abrir a página, a figura sobe e aparece (1,2s). Não há interação com o mouse.

## Tela atrás do retrato

- **Fundo, não conteúdo:** a tela é uma camada de fundo (`.cur-bg`) na mesma célula do grid que o retrato. Ela não tem conteúdo em fluxo, então não muda a altura de nada: quem define a altura da seção é o texto.
- **Desktop:** o fundo vai de cima a baixo da coluna do retrato. O retrato fica centralizado na vertical ao lado do texto, como sempre esteve.
- **Celular (≤760px):** o fundo vai de borda a borda atrás do retrato, que fica centralizado no topo.
- **Vídeo:** passa um trecho curto de um filme da curadoria (Gisele: *Hausu*, 1977). É mudo, em loop e começa sozinho.
- **Dois cortes, um para cada formato de tela:** o vídeo é recortado no formato certo, em vez de ser esticado. `video`/`poster` são o corte alto do desktop; `videoMobile`/`posterMobile`, o corte 4:5 do celular. A página escolhe pela largura ao abrir o perfil.
- **Opacidade:** o vídeo fica a 50% sobre a base escura da página, então o filme some no escuro sem ganhar cor.
- **Camadas por cima do vídeo:**
  - uma base escurecida embaixo, para o corpo da figura não se perder num quadro claro;
  - granulação de película (ruído SVG em `overlay`).
- **Parallax:** o vídeo é mais alto que a tela e desce mais devagar que a página ao rolar. A variável `--sy` recebe o topo da seção a cada scroll, e o deslocamento é de 0,3× o scroll, limitado à sobra do vídeo.
- **Movimento reduzido:** sem autoplay, sem parallax e sem a animação de entrada. Fica o quadro de pôster parado.

### Como o trecho é feito

O preto e branco e o desfoque são aplicados **no próprio arquivo**, não com CSS. Assim, o vídeo fica leve e abre rápido.

1. Baixe o trailer de origem (o id do YouTube está em `trailers.yt`) com `yt-dlp`.
2. Escolha de 6 a 8 planos curtos, de 0,7 a 1,4s cada. Evite cartelas de texto, logos do título e quadros que vazam de outros planos. Para conferir cortes rápidos, gere quadros com `ffmpeg -ss <tempo>` a cada 0,5s.
3. Monte com `ffmpeg`:
   - desktop: recorte 1:3 do centro do quadro 4:3 (`crop=240:720:520:0`), em 240×720;
   - celular: recorte 4:5 (`crop=576:720:352:0`), em 432×540;
   - os dois a 24fps;
   - `gblur=sigma=6`, `hue=s=0` e `eq=contrast=1.15`;
   - sem áudio, H.264 com CRF 30 e `+faststart`.
   - Resultado: cerca de 6s e de 100 a 130 KB cada.
4. Tire um quadro de pôster em WebP (cerca de 2 KB) com `ffmpeg -ss 0.3 … -frames:v 1` e `cwebp -q 70`.
5. Salve como `site/curadores/<id>-tela.mp4`/`.webp` e `<id>-tela-mobile.mp4`/`.webp` e preencha `screen` no `curators.json`.

## Navegação

- **Entradas na página:** a linha "Curadoria" na ficha de cada filme (com avatar e nome) e o link direto `#curador/<id>`.
- **Botão "Ver os N filmes da curadoria":** volta ao catálogo com o filtro **Curadoria** marcado. O filtro também fica na barra, junto de Gênero, Diretor, etc.
- **Voltar do navegador:** do catálogo filtrado, retorna ao perfil.
- **Sair da página:** a marca "Cinemateca Estranha" e "← Todo o catálogo" voltam ao catálogo. Digitar na busca também leva ao catálogo.
- **Filtros:** quem entra no perfil não perde os filtros do catálogo. Eles continuam no hash e no `localStorage`.
