import json,sys,urllib.request,urllib.error,os,re,unicodedata
from concurrent.futures import ThreadPoolExecutor
S=sys.argv[1]; M=json.load(open(S+'/movies.final.json'))
Q='''query($q:String!){popularTitles(country:BR,first:6,filter:{searchQuery:$q}){edges{node{objectType content(country:BR,language:"pt"){title originalReleaseYear externalIds{imdbId} fullPath}
offers(country:BR,platform:WEB){monetizationType presentationType package{clearName technicalName} standardWebURL}}}}}'''
def slug(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())
def q(s):
  req=urllib.request.Request('https://apis.justwatch.com/graphql',data=json.dumps({'query':Q,'variables':{'q':s}}).encode(),headers={'content-type':'application/json','User-Agent':'Mozilla/5.0'})
  import time
  for i in range(40):
    time.sleep(4)
    try: return json.loads(urllib.request.urlopen(req,timeout=25).read())['data']['popularTitles']['edges']
    except urllib.error.HTTPError as e:
      if e.code==429: time.sleep(120); continue
      return []
    except Exception: time.sleep(3)
  print('gave up',s,flush=True); return []
def work(m):
  for s in [m['title']]+m['aka'][:2]:
    for e in q(s):
      n=e['node']; c=n['content']
      ok=(m['imdb'] and c['externalIds'] and c['externalIds'].get('imdbId')==m['imdb']) or \
         (not m['imdb'] and slug(c['title'])==slug(s) and m['year'] and c['originalReleaseYear'] and abs(c['originalReleaseYear']-m['year'])<=1)
      if ok: return m['id'],n
  return m['id'],None
prev=json.load(open(S+'/jw.json')) if os.path.exists(S+'/jw.json') else {}
res={k:v for k,v in prev.items() if v}
for m in M:
  if m['id'] in res: continue
  k,v=work(m); res[k]=v
  json.dump(res,open(S+'/jw.json','w'),ensure_ascii=False)
json.dump(res,open(S+'/jw.json','w'),ensure_ascii=False)
found=[k for k,v in res.items() if v]; withoff=[k for k,v in res.items() if v and v['offers']]
print(len(found),'no JustWatch;',len(withoff),'com ofertas no Brasil')
from collections import Counter
print(Counter((o['package']['clearName'],o['monetizationType']) for v in res.values() if v for o in v['offers']).most_common(60))
