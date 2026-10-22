import json,sys,os,re,hashlib
S=sys.argv[1]; M=json.load(open(S+'/movies.final.json'))
wd=json.load(open(S+'/wd.json')); jw=json.load(open(S+'/jw.json')) if os.path.exists(S+'/jw.json') else {}
# trailer asset map: sha256 -> url from assets listing; local files hashed
amap={}
if os.path.exists(S+'/assets.txt'):
  for l in open(S+'/assets.txt'):
    m=re.search(r'(/_blob/[0-9a-f]{32})\s.*sha256 ([0-9a-f]{64})',l)
    if m: amap[m.group(2)]=m.group(1)
AM={}
for l in open(S+'/assets.map'):
  k,size,aid=l.split()
  f=S+'/trailers/%s.mp4'%k
  assert re.fullmatch(r'[0-9a-f]{32}',aid),l
  if os.path.exists(f): assert os.path.getsize(f)==int(size),('size mismatch',l)
  AM[k]=aid
# curadores: cada um pode listar seus filmes em "films"; o que não estiver em nenhuma lista fica com o "default"
CUR=json.load(open(S+'/curators.json'))
CDEF=next(c['id'] for c in CUR if c.get('default'))
CBY={}
for c in CUR:
  for f in c.get('films',[]): CBY.setdefault(f,[]).append(c['id'])
YT=dict(l.split() for l in open(S+'/trailers.yt')) if os.path.exists(S+'/trailers.yt') else {}
T={'FLATRATE':'Assinatura','FREE':'Grátis','ADS':'Grátis com anúncios','RENT':'Aluguel','BUY':'Compra'}
def pname(n):
  n=n.replace(' with Ads','').replace(' Standard','')
  n={'Amazon Prime Video':'Prime Video','Amazon Video':'Amazon','Plex Player':'Plex','Plex Channel':'Plex','Apple TV Store':'Apple TV','Netflix basic':'Netflix'}.get(n,n)
  if n.endswith(' Amazon Channel'): n=n[:-len(' Amazon Channel')]
  return n
STUDIO_SKIP={'Netflix'}  # distributor-ish noise is fine; keep list small
for m in M:
  w=wd.get(m['imdb'] or '',{})
  m['directors']=w.get('d',[]); m['studios']=[x for x in w.get('s',[])][:4]
  j=jw.get(m['id'])
  offers=[]; seen=set()
  if j:
    m['jw']=(j['content'] or {}).get('fullPath')
    for o in j['offers']:
      t=T.get(o['monetizationType']); n=pname(o['package']['clearName'])
      if not t or (n,t) in seen: continue
      seen.add((n,t)); offers.append({'n':n,'t':t,'u':o['standardWebURL']})
  m['watch']=offers
  a=AM.get(m['id'])
  if a: m['tr']='/_blob/'+a
  if m['id'] in YT: m['ytt']=YT[m['id']]
  m['cur']=CBY.get(m['id'],[CDEF])
js=lambda x: json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
t=open(S+'/site/template.html').read()
cur=[{k:v for k,v in c.items() if k!='films'} for c in CUR]
# compartilhamento: Open Graph (Facebook, WhatsApp, LinkedIn, Telegram, Slack, Discord, Pinterest, iMessage…),
# cartão do X/Twitter, schema.org e ícones. Os robôs não rodam JS nem leem o hash, então cada curador ganha
# uma página estática em site/curador/<id>.html com o próprio cartão, que redireciona para o perfil.
BASE='https://alfa-dev.github.io/cinemateca-estranha/site/'
NC=len({c for m in M for c in m['countries']})
def meta(title,desc,url,img,alt,kind='website',up=''):
  e=lambda x: x.replace('&','&amp;').replace('"','&quot;').replace('<','&lt;')
  t,d,a=e(title),e(desc),e(alt)
  return '\n'.join([
    f'<meta name="description" content="{d}">',
    f'<link rel="canonical" href="{url}">',
    '<meta name="robots" content="index,follow,max-image-preview:large">',
    '<meta name="theme-color" content="#121019">',
    '<meta name="color-scheme" content="dark light">',
    '<meta name="application-name" content="Cinemateca Estranha">',
    '<meta name="apple-mobile-web-app-title" content="Cinemateca">',
    '<meta name="apple-mobile-web-app-capable" content="yes">',
    '<meta name="mobile-web-app-capable" content="yes">',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
    f'<link rel="icon" href="{up}favicon.ico" sizes="48x48">',
    f'<link rel="icon" type="image/png" sizes="192x192" href="{up}icons/icon-192.png">',
    f'<link rel="icon" type="image/png" sizes="512x512" href="{up}icons/icon-512.png">',
    f'<link rel="apple-touch-icon" sizes="180x180" href="{up}icons/apple-touch-icon.png">',
    f'<link rel="manifest" href="{up}site.webmanifest">',
    f'<meta property="og:type" content="{kind}">',
    '<meta property="og:site_name" content="Cinemateca Estranha">',
    '<meta property="og:locale" content="pt_BR">',
    f'<meta property="og:title" content="{t}">',
    f'<meta property="og:description" content="{d}">',
    f'<meta property="og:url" content="{url}">',
    f'<meta property="og:image" content="{img}">',
    f'<meta property="og:image:secure_url" content="{img}">',
    '<meta property="og:image:type" content="image/jpeg">',
    '<meta property="og:image:width" content="1200">',
    '<meta property="og:image:height" content="630">',
    f'<meta property="og:image:alt" content="{a}">',
    '<meta name="twitter:card" content="summary_large_image">',
    f'<meta name="twitter:title" content="{t}">',
    f'<meta name="twitter:description" content="{d}">',
    f'<meta name="twitter:image" content="{img}">',
    f'<meta name="twitter:image:alt" content="{a}">',
    f'<meta itemprop="name" content="{t}">',
    f'<meta itemprop="description" content="{d}">',
    f'<meta itemprop="image" content="{img}">'])
SITE_DESC=f'{len(M)} filmes estranhos, cult e de horror de {NC} países, com trailers, filtros e onde assistir no Brasil. Curadoria de '+' e '.join(c['name'] for c in CUR)+'.'
site_meta=meta('Cinemateca Estranha',SITE_DESC,BASE+'cinemateca.html',BASE+'share/cinemateca.jpg','Cartazes de filmes de culto atrás do nome Cinemateca Estranha')
site_meta+='\n<script type="application/ld+json">'+js({'@context':'https://schema.org','@type':'WebSite','name':'Cinemateca Estranha','url':BASE+'cinemateca.html','description':SITE_DESC,'inLanguage':'pt-BR','image':BASE+'share/cinemateca.jpg'})+'</script>'
SES=json.load(open(S+'/sessions.json'))
open(S+'/site/cinemateca.html','w').write(t.replace('__META__',site_meta).replace('__SESSIONS__',js(SES)).replace('__CURATORS__',js(cur)).replace('__DATA__',js(M)))
json.dump({'name':'Cinemateca Estranha','short_name':'Cinemateca','description':SITE_DESC,'lang':'pt-BR','start_url':'cinemateca.html','scope':'./','display':'standalone','background_color':'#121019','theme_color':'#121019',
  'icons':[{'src':'icons/icon-192.png','sizes':'192x192','type':'image/png'},{'src':'icons/icon-512.png','sizes':'512x512','type':'image/png'},{'src':'icons/icon-maskable-512.png','sizes':'512x512','type':'image/png','purpose':'maskable'}]},
  open(S+'/site/site.webmanifest','w'),ensure_ascii=False,indent=2)
# a raiz do repositório (o endereço mais compartilhado) só redireciona; leva o mesmo cartão do site
open(S+'/index.html','w').write('<!doctype html>\n<html lang="pt-BR">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Cinemateca Estranha</title>\n'
  +site_meta.replace('href="favicon.ico"','href="site/favicon.ico"').replace('href="icons/','href="site/icons/').replace('href="site.webmanifest"','href="site/site.webmanifest"')
  +'\n<meta http-equiv="refresh" content="0; url=site/cinemateca.html">\n<a href="site/cinemateca.html">Cinemateca Estranha</a>\n')
# cada sessão também ganha uma página estática com o próprio cartão, que redireciona para #<sessão>
os.makedirs(S+'/site/sessao',exist_ok=True)
for c in SES:
  l=[m for m in M if c['id'] in m['cats']]
  desc=f"Sessão da Cinemateca Estranha: {len(l)} filmes de {len({x for m in l for x in m['countries']})} países. {c['desc']}"
  url=BASE+'sessao/'+c['id']+'.html'; dest='../cinemateca.html#'+c['id']
  mt=meta(f"{c['name']} · Cinemateca Estranha",desc,url,BASE+'share/sessao-'+c['id']+'.jpg',f"Cartazes da sessão {c['name']}",'website','../')
  mt+='\n<script type="application/ld+json">'+js({'@context':'https://schema.org','@type':'CollectionPage','name':c['name'],'description':c['desc'],'url':url,'isPartOf':{'@type':'WebSite','name':'Cinemateca Estranha','url':BASE+'cinemateca.html'},'numberOfItems':len(l)})+'</script>'
  open(S+'/site/sessao/%s.html'%c['id'],'w').write(f'''<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{c['name']} · Cinemateca Estranha</title>
{mt}
<meta http-equiv="refresh" content="0; url={dest}">
<script>location.replace("{dest}")</script>
<a href="{dest}">{c['name']} · Cinemateca Estranha</a>
''')
os.makedirs(S+'/site/curador',exist_ok=True)
for c in CUR:
  l=[m for m in M if c['id'] in m['cur']]; bio=[x.replace('**','') for x in c['bio']]; first=re.split(r'(?<=[.!?])\s',bio[0])[0]
  desc=f"{c['role']} da Cinemateca Estranha: {len(l)} filmes de {len({x for m in l for x in m['countries']})} países. {first}"
  url=BASE+'curador/'+c['id']+'.html'; dest='../cinemateca.html#curador/'+c['id']
  mt=meta(f"{c['name']} · {c['role']} da Cinemateca Estranha",desc,url,BASE+'share/'+c['id']+'.jpg',f"Retrato de {c['name']}",'profile','../')
  mt+='\n<script type="application/ld+json">'+js({'@context':'https://schema.org','@type':'ProfilePage','url':url,'mainEntity':{'@type':'Person','name':c['name'],'jobTitle':c['role'],'description':' '.join(bio),'image':BASE+c['photo']['base']+'-800.webp'}})+'</script>'
  open(S+'/site/curador/%s.html'%c['id'],'w').write(f'''<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{c['name']} · Cinemateca Estranha</title>
{mt}
<meta http-equiv="refresh" content="0; url={dest}">
<script>location.replace("{dest}")</script>
<a href="{dest}">{c['name']} · Cinemateca Estranha</a>
''')
print(len(M),'filmes |',sum(1 for m in M if m['directors']),'c/ diretor |',sum(1 for m in M if m['watch']),'c/ streaming |',sum(1 for m in M if m.get('tr')),'c/ trailer |',' | '.join('%s: %d'%(c['name'],sum(1 for m in M if c['id'] in m['cur'])) for c in CUR))
