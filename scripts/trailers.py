import json,sys,os,re,subprocess,unicodedata
from concurrent.futures import ThreadPoolExecutor
import yt_dlp
S=sys.argv[1]; M=json.load(open(S+'/movies.final.json'))
WD=json.load(open(S+'/wd.json'))
ONLY=set(open(S+'/bad.txt').read().split()) if len(sys.argv)>2 else None
if ONLY: M=[m for m in M if m['id'] in ONLY]
log=open(S+'/trailers.log','a')
def slug(s): return re.sub(r'[^a-z0-9 ]','',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())
def pick(m):
  d=(WD.get(m['imdb'] or '',{}).get('d') or [''])[0]
  q='%s %s %s trailer'%(m['title'],m['year'] or '',d)
  with yt_dlp.YoutubeDL({'quiet':True,'extract_flat':True,'skip_download':True,'no_warnings':True}) as y:
    r=y.extract_info('ytsearch8:'+q,download=False)
  es=[e for e in r.get('entries',[]) if e.get('duration') and 20<e['duration']<420]
  names=[m['title']]+m['aka']
  words=[w for n in names for w in slug(n).split() if len(w)>3 and w not in ('the','and','with','from','trailer')]
  def score(e):
    t=slug(e.get('title'))
    return (('trailer' in t) + ('teaser' in t)*.5 + sum(w in t for w in words)/max(1,len(words)) + (e.get('id')==m.get('yt'))*.3)
  if ONLY: es=[e for e in es if any(w in slug(e.get('title')) for w in words) and (not m['year'] or str(m['year']) in (e.get('title') or '') or len([w for w in words if w in slug(e.get('title'))])>=2 or d.split()[-1:] and slug(d.split()[-1]) in slug(e.get('title')))]
  es.sort(key=score,reverse=True)
  return es[:5]
def work(m):
  out=S+'/trailers/%s.mp4'%m['id']
  if os.path.exists(out): return m['id'],'have'
  try:
    cands=pick(m)
    if not cands: log.write('NONE %s %s\n'%(m['id'],m['title'])); log.flush(); return m['id'],None
    raw=S+'/raw/%s.%%(ext)s'%m['id']
    for e in cands:
      try:
        with yt_dlp.YoutubeDL({'quiet':True,'no_warnings':True,'format':'bv*[height<=480]+ba/b[height<=480]/b','outtmpl':raw,'merge_output_format':'mp4'}) as y:
          y.download(['https://www.youtube.com/watch?v='+e['id']])
        break
      except Exception as ex: last=ex
    else: raise last
    src=[f for f in os.listdir(S+'/raw') if f.startswith(m['id']+'.')][0]
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',S+'/raw/'+src,'-t','200','-vf','scale=-2:360','-c:v','libx264','-preset','veryfast','-crf','30','-c:a','aac','-b:a','80k','-ac','2','-movflags','+faststart',out],check=True)
    os.remove(S+'/raw/'+src)
    log.write('OK %s %s | %s | %s | %dKB\n'%(m['id'],m['title'],e['id'],e.get('title'),os.path.getsize(out)//1024)); log.flush()
    return m['id'],e['id']
  except Exception as ex:
    log.write('ERR %s %s %s\n'%(m['id'],m['title'],str(ex)[:200])); log.flush(); return m['id'],None
with ThreadPoolExecutor(4) as ex: res=list(ex.map(work,M))
print('done',sum(1 for k,v in res if v))
