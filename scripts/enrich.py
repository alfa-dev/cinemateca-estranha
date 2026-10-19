import json,sys,re,urllib.request,urllib.parse,unicodedata,time
from concurrent.futures import ThreadPoolExecutor
S=sys.argv[1]
rows=json.load(open(S+'/norm.json'))
OV={117:('A Clockwork Orange',1971),118:('Fight Club',1999),119:('Oldboy',2003),120:('Se7en',1995),
122:('Blue Velvet',1986),123:('Mulholland Drive',2001),124:('Lost Highway',1997),128:("Pan's Labyrinth",2006),
130:('The Holy Mountain',1973),249:('The Holy Mountain',1973),167:('American Psycho',2000),168:('Annihilation',2018),169:('Antichrist',2009),
170:('Black Swan',2010),171:('Borgman',2013),172:('Eraserhead',1977),174:('Get Out',2017),175:('Hereditary',2018),
176:("Jacob's Ladder",1990),177:('Martyrs',2008),178:('Midsommar',2019),179:('Mother!',2017),181:('Split',2016),
182:('The Gift',2015),183:('The Lighthouse',2019),184:('The Mist',2007),185:('The Orphanage',2007),186:('The Shining',1980),
187:('The Wailing',2016),188:('The Witch',2015),213:('The Witch',2015),189:('Un Chien Andalou',1929),190:('The Thing',1982),191:('Suspiria',2018),
203:('Faust',1926),204:('Gothic',1986),210:('The Ninth Gate',1999),212:('Haxan',1922),157:('1984',1984),
144:('The Matrix',1999),147:('Stalker',1979),131:('Paprika',2006),107:('Irreversible',2002),105:('The Handmaiden',2016),
111:('Dogtooth',2009),15:('Uncle Boonmee Who Can Recall His Past Lives',2010),7:('The Lure',2015),3:('House',1977),208:('House',1977),
16:('Consuming Spirits',2012),56:('Institute Benjamenta',1995),76:('Welcome to Nowhere',2012),146:('Interstellar',2014),
226:('The Cabinet of Dr. Caligari',1920),227:('The Blood of a Poet',1932),30:('Enthiran',2010),12:('The Mysterious Castle in the Carpathians',1981),
92:('Revolutionary Girl Utena: The Adolescence of Utena',1999),165:('Timecrimes',2007),219:('Succubus',1968),110:('Birdman',2014),
95:('Las',2009),109:('Waking Life',2001),137:('Black Mirror: Bandersnatch',2018),234:('Strange Angel',2018),129:('The Fall',2006)}
SKIP={206,207}
def clean(t):
  t=re.sub(r'\s*\((YT|vimeo|SITE|https?://[^)]*)\)','',t).strip()
  return t
def fetch(url,binary=False):
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'en-US'})
  for _ in range(3):
    try:
      with urllib.request.urlopen(req,timeout=20) as r: d=r.read(); return d if binary else d.decode('utf8','replace')
    except Exception as e: time.sleep(1)
  return None
def slug(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def imdb(q,year):
  s=slug(q)[:20] or 'x'
  j=fetch('https://v2.sg.media-imdb.com/suggestion/%s/%s.json'%(s[0],urllib.parse.quote(q)))
  if not j: return None
  try: d=json.loads(j).get('d',[])
  except: return None
  d=[x for x in d if x.get('id','').startswith('tt')]
  if year: 
    m=[x for x in d if x.get('y') and abs(x['y']-year)<=1]
    if m:
      exact=[x for x in m if slug(x['l'])==slug(q)]
      return (exact or m)[0]
    return None
  exact=[x for x in d if slug(x['l'])==slug(q)]
  return exact[0] if exact else None
def yt(q):
  h=fetch('https://www.youtube.com/results?search_query='+urllib.parse.quote(q))
  m=re.search(r'"videoId":"([\w-]{11})"',h or '')
  return m.group(1) if m else None
def work(k):
  r=rows[k]
  if k in SKIP: return k,None,None
  cands=[]
  if k in OV: cands.append(OV[k])
  for f in ['orig','other','pt']:
    for t in clean(r[f]).split(' / '):
      if t and not t.endswith('.0'): cands.append((t,r['year']))
  hit=None
  for t,y in cands:
    hit=imdb(t,y)
    if hit: break
  name=hit['l'] if hit else (cands[0][0] if cands else r['pt'])
  y=(hit or {}).get('y') or r['year']
  v=yt('%s %s trailer'%(name,y or ''))
  return k,hit,v
with ThreadPoolExecutor(8) as ex: res=list(ex.map(work,range(len(rows))))
out={k:{'imdb':h,'yt':v} for k,h,v in res}
json.dump(out,open(S+'/enrich.json','w'),ensure_ascii=False)
miss=[k for k,h,v in res if not h]
print('no imdb:',len(miss)); 
for k in miss: print(k,rows[k]['orig'] or rows[k]['pt'] or rows[k]['other'],rows[k]['year'])
print('no poster:',[k for k,h,v in res if h and not h.get('i')])
print('no yt:',[k for k,h,v in res if not v])
