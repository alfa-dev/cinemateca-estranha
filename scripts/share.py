import json,sys,os,subprocess,random
# imagens de compartilhamento e ícones: monta cada uma em HTML e fotografa com o Chrome headless
# saída: site/share/*.jpg (1200x630), site/icons/*.png, site/favicon.ico
S=os.path.abspath(sys.argv[1])
CHROME=os.environ.get('CHROME','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
M=json.load(open(S+'/movies.final.json')); CUR=json.load(open(S+'/curators.json'))
P=json.load(open(S+'/site/posters.json'))
FONTS='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;900&family=Instrument+Sans:wght@400;600&family=JetBrains+Mono:wght@500&display=swap">'
BASE='*{box-sizing:border-box}html,body{margin:0;background:#121019;color:#eeeaf4}'
os.makedirs(S+'/site/share',exist_ok=True); os.makedirs(S+'/site/icons',exist_ok=True)
def shot(name,html,w,h,out):
  f=S+'/site/_share_%s.html'%name
  open(f,'w').write('<!doctype html><meta charset="utf-8">'+FONTS+'<style>'+BASE+'</style>'+html)
  png=f[:-5]+'.png'
  subprocess.run([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1','--virtual-time-budget=6000','--window-size=%d,%d'%(w,h),'--screenshot='+png,'file://'+f],stderr=subprocess.DEVNULL,check=True)
  os.remove(f)
  if out.endswith('.jpg'): subprocess.run(['magick',png,'-strip','-quality','84',out],check=True); os.remove(png)
  else: os.replace(png,out)
ncountries=len({c for m in M for c in m['countries']})
# site: mosaico de cartazes inclinado, escurecido, com a marca por cima
random.seed(7)
ids=[m['id'] for m in M if m['id'] in P]; random.shuffle(ids)
tiles=''.join('<img src="%s">'%P[i] for i in ids[:60])
shot('site','''<style>
.m{position:fixed;inset:-120px -160px;display:grid;grid-template-columns:repeat(12,1fr);gap:10px;rotate:-8deg;opacity:.55}
.m img{width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:4px}
.v{position:fixed;inset:0;background:radial-gradient(70% 90% at 30% 60%,#121019f2 30%,#12101999 70%,#12101955)}
.t{position:fixed;left:72px;bottom:72px}
b{display:block;font:900 150px/.82 "Big Shoulders Display";text-transform:uppercase}b span{color:#f4a640}
p{margin:26px 0 0;font:500 26px "JetBrains Mono";letter-spacing:.08em;text-transform:uppercase;color:#b4adc4}
</style><div class="m">{TILES}</div><div class="v"></div><div class="t"><b>Cinemateca<br><span>Estranha</span></b><p>{N} filmes de culto · {C} países · 5 sessões</p></div>'''.replace('{N}',str(len(M))).replace('{C}',str(ncountries)).replace('{TILES}',tiles),1200,630,S+'/site/share/cinemateca.jpg')
# curador: tela desfocada do trecho + retrato à esquerda, nome e números à direita
for c in CUR:
  listed={f for x in CUR for f in x.get('films',[])}
  l=[m for m in M if m['id'] in c.get('films',[]) or (c.get('default') and m['id'] not in listed)]
  ys=[m['year'] for m in l if m['year']]; w=c['name'].split()
  scr=('<img class="s" src="%s">'%c['screen']['poster']) if c.get('screen') else ''
  shot('cur_'+c['id'],'''<style>
.f{position:fixed;left:56px;top:56px;width:470px;height:574px;border-radius:12px 12px 0 0;overflow:hidden;background:#2b2333}
.s{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.f::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,#000a,transparent 55%%)}
.p{position:fixed;left:56px;bottom:0;width:470px;height:470px;filter:drop-shadow(0 10px 22px #0009)}
.t{position:fixed;left:590px;right:56px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center}
k{font:500 22px "JetBrains Mono";letter-spacing:.12em;text-transform:uppercase;color:%s}
h1{margin:14px 0 0;font:900 136px/.84 "Big Shoulders Display";text-transform:uppercase}h1 span{color:%s}
p{margin:26px 0 0;font:500 24px "JetBrains Mono";color:#b4adc4}p b{color:#eeeaf4;font-weight:500}
i{position:fixed;right:56px;bottom:48px;font:900 34px "Big Shoulders Display";font-style:normal;text-transform:uppercase}i span{color:#f4a640}
</style><div class="f">%s</div><img class="p" src="%s-800.webp"><div class="t"><k>%s da Cinemateca Estranha</k><h1>%s<br><span>%s</span></h1>
<p><b>%d</b> filmes · <b>%d</b> países<br>de <b>%d</b> a <b>%d</b></p></div><i>Cinemateca <span>Estranha</span></i>'''%(
    c.get('color','#f4a640'),c.get('color','#f4a640'),scr,c['photo']['base'],c['role'],' '.join(w[:-1]),w[-1],
    len(l),len({x for m in l for x in m['countries']}),min(ys),max(ys)),1200,630,S+'/site/share/%s.jpg'%c['id'])
# ícone: monograma CE (C claro, E laranja), o mesmo do cabeçalho compacto no celular
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="%d" fill="#121019"/><text x="256" y="368" text-anchor="middle" font-family="Big Shoulders Display,Impact,sans-serif" font-weight="900" font-size="330" letter-spacing="-6"><tspan fill="#eeeaf4">C</tspan><tspan fill="#f4a640">E</tspan></text></svg>'
# o Chrome headless não abre janelas tão pequenas: renderiza em 512 e reduz
for n,rx,pad in [('icon-512',96,0),('apple-touch-icon',0,0)]:
  st=' style="padding:%dpx"'%pad if pad else ''
  shot('icon_'+n,'<style>html,body{background:transparent}svg{display:block;width:100vw;height:100vh}</style>'+(svg%rx).replace('<svg ','<svg'+st+' '),512,512,S+'/site/icons/%s.png'%n)
# maskable (Android): fundo até a borda, monograma dentro da zona segura
subprocess.run(['magick',S+'/site/icons/apple-touch-icon.png','-resize','400x400','-background','#121019','-gravity','center','-extent','512x512',S+'/site/icons/icon-maskable-512.png'],check=True)
subprocess.run(['magick',S+'/site/icons/apple-touch-icon.png','-resize','180x180',S+'/site/icons/apple-touch-icon.png'],check=True)
subprocess.run(['magick',S+'/site/icons/icon-512.png','-resize','192x192',S+'/site/icons/icon-192.png'],check=True)
subprocess.run(['magick',S+'/site/icons/icon-512.png','-define','icon:auto-resize=48,32,16',S+'/site/favicon.ico'],check=True)
print('ok:', sorted(os.listdir(S+'/site/share')), sorted(os.listdir(S+'/site/icons')))
