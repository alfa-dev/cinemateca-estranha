import json,sys,re,urllib.request,urllib.parse
S=sys.argv[1]; M=json.load(open(S+'/movies.final.json'))
ids=sorted({m['imdb'] for m in M if m['imdb']})
out={}
for i in range(0,len(ids),40):
  vals=' '.join('"%s"'%x for x in ids[i:i+40])
  q='''SELECT ?imdb ?p ?l WHERE { VALUES ?imdb {%s} ?f wdt:P345 ?imdb .
   { ?f wdt:P57 ?x . BIND("d" AS ?p) } UNION { ?f wdt:P272 ?x . BIND("s" AS ?p) }
   SERVICE wikibase:label { bd:serviceParam wikibase:language "en,mul,pt". ?x rdfs:label ?l . } }'''%vals
  req=urllib.request.Request('https://query.wikidata.org/sparql?format=json&query='+urllib.parse.quote(q),headers={'User-Agent':'cinemateca-personal/1.0 (catalog script)'})
  import time
  for t in range(4):
    try: data=json.loads(urllib.request.urlopen(req,timeout=90).read()); break
    except Exception as ex: print('retry',i,ex,flush=True); time.sleep(10)
  for b in data['results']['bindings']:
    if re.fullmatch(r'Q\d+',b['l']['value']): continue
    e=out.setdefault(b['imdb']['value'],{'d':[],'s':[]}); l=b['l']['value']
    if l not in e[b['p']['value']]: e[b['p']['value']].append(l)
json.dump(out,open(S+'/wd.json','w'),ensure_ascii=False)
print(len(ids),'ids;',sum(1 for v in out.values() if v['d']),'com diretor;',sum(1 for v in out.values() if v['s']),'com produtora')
miss=[m['title'] for m in M if m['imdb'] and not out.get(m['imdb'],{}).get('d')]
print('sem diretor:',len(miss),miss[:60])
