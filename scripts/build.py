import json,sys,re,urllib.request,base64,os,subprocess
from concurrent.futures import ThreadPoolExecutor
S=sys.argv[1]
rows=json.load(open(S+'/norm.json')); en=json.load(open(S+'/enrich.json'))
en['110']['imdb']={'id':'tt2562232','l':'Birdman or (The Unexpected Virtue of Ignorance)','y':2014,'i':{'imageUrl':'https://m.media-amazon.com/images/M/MV5BODAzNDMxMzAxOV5BMl5BanBnXkFtZTgwMDMxMjA4MjE@._V1_.jpg'}}
en['216']['imdb']=None; en['237']['imdb']=None
v=json.loads(urllib.request.urlopen(urllib.request.Request('https://v2.sg.media-imdb.com/suggestion/v/Vera.json',headers={'User-Agent':'Mozilla/5.0'})).read())['d']
en['94']['imdb']=next(x for x in v if x['id']=='tt0274193') if any(x['id']=='tt0274193' for x in v) else {'id':'tt0274193','l':'Vera','y':2003}
GF={'mistário':'Mistério','mistério':'Mistério','terrro':'Terror','avetura':'Aventura','ficção científica':'Ficção científica','música':'Música'}
CF={'Candá':'Canadá','Irlanda do Norte':None,'Irlanda':None,'Bali':'Indonésia'}
SEC={'Thriller':'Thriller','Drama':'Drama','Action/Crime':'Policial','Mistery':'Mistério','Fantasy':'Fantasia','Anime':'Animação','Comedy':'Comédia','Science Fiction':'Ficção científica','Horror':'Terror'}
PLAT={'netflix':'Netflix','amazon':'Prime Video','HBO':'HBO'}
CATS={'Weird Movies':'weird','Weird Movies pelo mundo':'mundo','Mindfuck':'mindfuck','Pleasing Horror':'horror','Thelema, Magia e Ocultismo':'thelema'}
def clean(t): return re.sub(r'\s*\((YT|vimeo|SITE|https?://[^)]*)\)','',t).strip()
movies={}; order=[]
for k,r in enumerate(rows):
  e=en[str(k)]; h=e['imdb']
  key=h['id'] if h else 'r%d'%k
  orig=clean(r['orig']); pt=clean(r['pt']); other=clean(r['other'])
  if k==16: pt=''
  if orig.endswith('.0'): orig=orig[:-2]; pt=''
  title=orig or (h['l'] if h else '') or other or pt
  if not r['orig'] and h: title=h['l']
  genres=[]
  for g in r['genres']:
    g=GF.get(g.lower(),g[0].upper()+g[1:].lower() if g else g)
    if g=='Série': continue
    if g not in genres: genres.append(g)
  if not genres and r['section']: genres=[SEC[r['section']]]
  countries=[]
  for c in r['countries']:
    c=CF.get(c,c)
    if c and c not in countries: countries.append(c)
  if k==16: countries=['Estados Unidos']
  links=[]
  m=re.search(r'\((https?://[^)]*)\)',r['orig'])
  if m: links.append(('Site oficial',m.group(1)))
  flags=[]
  if '(YT)' in r['orig'] or '(YT)' in r['other']: flags.append('Completo no YouTube')
  if '(vimeo)' in r['orig']: flags.append('No Vimeo')
  plats=[PLAT[x] for x in r['extra'] if x in PLAT]
  year=r['year'] or (h or {}).get('y')
  aka=[x for x in [pt,other,(h or {}).get('l')] if x and x.lower()!=title.lower()]
  aka=list(dict.fromkeys(a for t in aka for a in t.split(' / ')))
  if key in movies:
    m0=movies[key]
    if CATS[r['cat']] not in m0['cats']: m0['cats'].append(CATS[r['cat']])
    for f,vals in [('genres',genres),('countries',countries),('platforms',plats),('flags',flags),('aka',aka)]:
      for x in vals:
        if x not in m0[f] and x!=m0['title']: m0[f].append(x)
    continue
  movies[key]={'id':key,'title':title,'aka':aka,'year':year,'cats':[CATS[r['cat']]],'genres':genres,'countries':countries,
    'platforms':plats,'flags':flags,'links':links,'imdb':h['id'] if h else None,'yt':e['yt'],
    'kind':{'short':'Curta','tvSeries':'Série','tvMiniSeries':'Minissérie','tvMovie':'Telefilme','video':'Vídeo'}.get((h or {}).get('qid')),
    'cast':(h or {}).get('s'),'_img':((h or {}).get('i') or {}).get('imageUrl')}
  order.append(key)
def dl(key):
  m=movies[key]; u=m['_img']
  if not u: return key,None
  p=S+'/posters/%s.jpg'%key
  if not os.path.exists(p):
    u2=re.sub(r'\._V1_.*\.jpg$','._V1_QL70_UX260_.jpg',u)
    try:
      d=urllib.request.urlopen(urllib.request.Request(u2,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
      open(p,'wb').write(d)
    except Exception as ex: print('fail',key,ex); return key,None
  return key,'data:image/jpeg;base64,'+base64.b64encode(open(p,'rb').read()).decode()
with ThreadPoolExecutor(8) as ex: posters=dict(x for x in ex.map(dl,order) if x[1])
out=[]
for key in order:
  m=movies[key]; m.pop('_img'); m['poster']=key in posters; out.append(m)
os.makedirs(S+'/site',exist_ok=True)
json.dump(posters,open(S+'/site/posters.json','w'),separators=(',',':'))
json.dump(out,open(S+'/movies.final.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(out),'filmes,',len(posters),'capas,',os.path.getsize(S+'/site/posters.json')//1024,'KB')
