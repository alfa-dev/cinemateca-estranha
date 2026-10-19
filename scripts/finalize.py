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
d=json.dumps(M,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
t=open(S+'/site/template.html').read()
open(S+'/site/cinemateca.html','w').write(t.replace('__DATA__',d))
print(len(M),'filmes |',sum(1 for m in M if m['directors']),'c/ diretor |',sum(1 for m in M if m['watch']),'c/ streaming |',sum(1 for m in M if m.get('tr')),'c/ trailer')
