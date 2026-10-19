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
python3 scripts/finalize.py .      # monta site/cinemateca.html
```

## Trailers

Os MP4 (~700 MB, 360p) não estão no git. No Artifact a página os carrega de `/_blob/<asset id>`.
No GitHub Pages (ou abrindo o arquivo localmente) esses caminhos não existem, então o trailer é embutido do YouTube, a partir do mesmo vídeo de origem (`trailers.yt`).
