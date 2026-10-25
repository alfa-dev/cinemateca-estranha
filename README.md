# Cinemateca Estranha

Catálogo de 248 filmes estranhos, cult e de horror, gerado a partir de uma planilha pessoal (`data/Movies.xlsx`).
Tem capas, trailers que tocam dentro da página, categorias, filtros (gênero, diretor, produtora, país, década, onde ver, formato), busca e "onde assistir no Brasil".

- GitHub Pages: https://alfa-dev.github.io/cinemateca-estranha/
- Artifact no Claude: https://claude.ai/artifact/6ziCfiwDLVMxvY9QeWfSai

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `data/Movies.xlsx` | planilha original |
| `scripts/` | pipeline em Python (só biblioteca padrão, exceto `trailers.py`) |
| `*.json` | dados intermediários de cada etapa |
| `trailers.yt` | `<id do filme> <id do vídeo no YouTube>` — de onde cada trailer foi baixado |
| `assets.map` | `<id do filme> <bytes> <asset id>` — trailers enviados como assets do Artifact |
| `site/template.html` | código-fonte da página (`__DATA__` recebe os dados) |
| `site/cinemateca.html` | página final |
| `site/posters.json` | capas em base64, carregadas pela página |
| `sessions.json` | sessões: nome, descrição e cor (a da página vem de `--c-<id>` no template) |
| `curators.json` | curadores: nome, foto, bio e (opcional) a lista `films` de ids de filmes |
| `site/curadores/` | retratos dos curadores em WebP com transparência, em várias larguras (`<id>-<largura>.webp`); quadrados, figura recortada encostada na borda de baixo |

## Pipeline

Todos os scripts recebem a raiz do repositório como primeiro argumento.

```sh
python3 scripts/read.py data/Movies.xlsx movies.json   # lê o xlsx (zip + XML)
python3 scripts/norm2.py movies.json norm.json          # normaliza linhas
python3 scripts/enrich.py .        # IMDb (id, ano, capa) + YouTube → enrich.json
python3 scripts/build.py .         # junta duplicatas, baixa capas → movies.final.json, site/posters.json
python3 scripts/wd.py .            # Wikidata: diretor e produtora → wd.json
python3 scripts/jw.py .            # JustWatch Brasil: onde assistir → jw.json (lento, respeita rate limit)
python3 scripts/trailers.py .      # yt-dlp + ffmpeg → trailers/<id>.mp4 (precisa de requirements.txt e ffmpeg)
python3 scripts/share.py .         # imagens de compartilhamento (site/share/) e ícones (precisa do Chrome e do ImageMagick)
python3 scripts/finalize.py .      # monta site/cinemateca.html, as páginas de compartilhamento dos curadores e as tags
```

## Compartilhamento

`finalize.py` põe no `<head>` as tags Open Graph (Facebook, WhatsApp, LinkedIn, Telegram, Slack, Discord, Pinterest, iMessage), o cartão do X/Twitter, schema.org, ícones e o manifest, no `site/cinemateca.html` e no `index.html` da raiz. Os robôs não rodam JS nem leem o `#`, então cada curador e cada sessão têm uma página estática (`site/curador/<id>.html`, `site/sessao/<id>.html`) com o próprio cartão em `site/share/`, que redireciona para a página: é esse o link para compartilhar.

## Sessões

Cada sessão tem uma página em `#<id>` (ex.: `#mindfuck`). No lugar da hero entra um cabeçalho com o nome, a descrição, os números, os diretores e os países mais frequentes (clicáveis, viram filtro) e um leque de cartazes. Abaixo vêm os filtros e a grade, só com os filmes da sessão. Para compartilhar, use `site/sessao/<id>.html`, que tem o cartão próprio (`site/share/sessao-<id>.jpg`) e redireciona para a página.

## Curadores

Cada curador tem uma página em `#curador/<id>`, com retrato, números e bio, e um botão que leva ao catálogo filtrado pela curadoria dele. Para adicionar um, inclua uma entrada em `curators.json` com `color` (a cor do curador na página dele), `screen` (um trecho curto de um filme da curadoria, MP4 mudo de ~6 s em 640×384, com um quadro em WebP de pôster) e `films` (ids do IMDb, como em `movies.final.json`), gere a foto em `site/curadores/` (`cwebp -resize <largura> 0 -q 78 -alpha_q 90 foto.png -o site/curadores/<id>-<largura>.webp` para 96, 480, 800 e 1200) e rode `finalize.py`. Um filme pode ter vários curadores: basta estar no `films` de cada um. Filmes que não estão em nenhuma lista ficam com o curador marcado `"default": true` (hoje, Gisele Britto, com todos os 248); para um filme ser dela e de outro curador, liste-o também no `films` dela.

Detalhes da página de perfil (layout, retrato, tela com o trecho de filme e como montá-lo) em [`docs/pagina-do-curador.md`](docs/pagina-do-curador.md).

## Locadora

`site/locadora.html` (gerada por `finalize.py` a partir de `site/locadora-template.html`) mostra as fitas numa estante 3D (three.js), uma prateleira por sessão, com uma bancada, um VCR e uma TV de tubo. Clique numa fita, ponha no VCR e o trailer toca na TV, com efeito CRT inspirado no [pen do Mobius1](https://codepen.io/Mobius1/pen/ZNgwbr). `#<id do filme>` abre com a fita já no VCR.

Os modelos vêm do Sketchfab (lista e créditos em `site/modelos/creditos.json`). Baixe o `.glb` de texturas 1k em `modelos-baixados/` (fora do git) com os nomes `vcr.glb`, `tv.glb`, `fita.glb`, `estante.glb` e `bancada.glb`, e otimize cada um para `site/modelos/`:

```sh
npx @gltf-transform/cli optimize modelos-baixados/tv.glb site/modelos/tv.glb --compress meshopt --texture-compress webp
```

Escala, rotação, a boca do VCR, o retângulo da tela da TV e as alturas das prateleiras ficam em `site/modelos/cena.json`. Enquanto um modelo não existe, a página usa uma peça provisória desenhada no código.

## Trailers

Os MP4 (~700 MB, 360p) não estão no git. No Artifact a página os carrega de `/_blob/<asset id>`.
No GitHub Pages (ou abrindo o arquivo localmente) esses caminhos não existem, então o trailer é embutido do YouTube, a partir do mesmo vídeo de origem (`trailers.yt`).
