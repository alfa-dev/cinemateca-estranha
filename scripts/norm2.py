import json,sys
d=json.load(open(sys.argv[1]))
names=['Weird Movies','Weird Movies pelo mundo','Mindfuck','Pleasing Horror','Thelema, Magia e Ocultismo']
L='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
out=[]
for i,(n,rows) in enumerate(sorted(d.items())):
  h=rows[0]; inv={v.strip():k for k,v in h.items()}
  cO,cP,cX,cG,cC=[inv[k] for k in ['Título original','Título em Português','Outros','Gêneros','País(es)']]
  gi,ci=L.index(cG),L.index(cC)
  section=None
  for r in rows[1:]:
    if not r: continue
    a=r.get('A','')
    if a and not a.replace('.0','').isdigit() and len(r)==1: section=a; continue
    t={'cat':names[i],'section':section,
       'year':int(float(a)) if a else None,
       'orig':r.get(cO,'').strip(),'pt':r.get(cP,'').strip(),'other':r.get(cX,'').strip(),
       'extra':[r[c].strip() for c in L[L.index(cX)+1:gi] if c in r],
       'genres':[r[c].strip() for c in L[gi:ci] if c in r and r[c].strip()],
       'countries':[r[c].strip() for c in L[ci:] if c in r and r[c].strip() and r[c].strip()!='?']}
    out.append(t)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
for k,t in enumerate(out): print(k,t['cat'][:6],t['section'],t['year'],'|',t['orig'],'|',t['pt'],'|',t['other'],'|',t['extra'],t['genres'],t['countries'])
