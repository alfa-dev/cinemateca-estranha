import json,sys,collections
d=json.load(open(sys.argv[1]))
names=['Weird Movies','Weird Movies around the world','Mindfuck','Pleasing Horror','Thelema, Magia e Ocultismo']
L='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
for i,(n,rows) in enumerate(sorted(d.items())):
  h=rows[0]; inv={v.strip():k for k,v in h.items()}
  print('==',names[i],h)
  cnt=0; odd=[]
  for r in rows[1:]:
    if not r: continue
    if 'A' in r and not r['A'].replace('.0','').isdigit(): odd.append(r); continue
    if 'B' not in r: odd.append(r); continue
    cnt+=1
  print(cnt,'movies; odd rows:',len(odd))
  for o in odd[:40]: print('  ',o)
