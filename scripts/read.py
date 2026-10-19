import zipfile,re,sys,json
import xml.etree.ElementTree as ET
z=zipfile.ZipFile(sys.argv[1]); ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ss=[]
if 'xl/sharedStrings.xml' in z.namelist():
  for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns):
    ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%ns['m'])))
wb=ET.fromstring(z.read('xl/workbook.xml'))
print([s.get('name') for s in wb.find('m:sheets',ns)])
out={}
for n in sorted(x for x in z.namelist() if x.startswith('xl/worksheets/sheet')):
  rows=[]
  for r in ET.fromstring(z.read(n)).iter('{%s}row'%ns['m']):
    row={}
    for c in r.findall('m:c',ns):
      col=re.match(r'[A-Z]+',c.get('r')).group(); v=c.find('m:v',ns); t=c.get('t')
      if t=='inlineStr': val=''.join(x.text or '' for x in c.iter('{%s}t'%ns['m']))
      elif v is None: continue
      elif t=='s': val=ss[int(v.text)]
      else: val=v.text
      row[col]=val
    rows.append(row)
  out[n]=rows
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
for n,rows in out.items():
  print(n,len(rows))
  for r in rows[:8]: print(r)
