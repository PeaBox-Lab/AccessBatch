import json, sqlite3, time, uuid, zipfile, html
from pathlib import Path
from urllib.parse import urljoin, urlparse
from fastapi import FastAPI, BackgroundTasks, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
BASE=Path(__file__).resolve().parents[1]; DB=BASE/'data/accessbatch.db'; OUT=BASE/'output'
app=FastAPI(title='AccessBatch'); templates=Jinja2Templates(directory=str(BASE/'app/templates'))
AXE_JS='https://cdn.jsdelivr.net/npm/axe-core@4.10.3/axe.min.js'
def init():
 c=sqlite3.connect(DB);c.execute('CREATE TABLE IF NOT EXISTS scans(id TEXT PRIMARY KEY,target TEXT,status TEXT,created REAL,finished REAL,pages INTEGER,issues INTEGER,error TEXT)');c.commit();c.close()
init()
def dbexec(q,a=(),fetch=False):
 c=sqlite3.connect(DB);cur=c.execute(q,a);r=cur.fetchall() if fetch else None;c.commit();c.close();return r
async def crawl(seed,max_pages):
 host=urlparse(seed).netloc;todo=[seed];seen=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True);page=await browser.new_page()
  while todo and len(seen)<max_pages:
   u=todo.pop(0)
   if u in seen:continue
   try:
    await page.goto(u,wait_until='domcontentloaded',timeout=30000);seen.append(u);content=await page.content();s=BeautifulSoup(content,'html.parser')
    for a in s.find_all('a',href=True):
     x=urljoin(u,a['href']).split('#')[0]
     if urlparse(x).scheme in ('http','https') and urlparse(x).netloc==host and x not in seen and x not in todo:todo.append(x)
   except:pass
  await browser.close()
 return seen
async def run_scan(scan_id,target,max_pages):
 folder=OUT/scan_id;folder.mkdir(parents=True,exist_ok=True);all_issues=[]
 try:
  pages=await crawl(target,max_pages)
  async with async_playwright() as p:
   browser=await p.chromium.launch(headless=True);ctx=await browser.new_context(viewport={'width':1440,'height':1000})
   for idx,u in enumerate(pages,1):
    page=await ctx.new_page()
    try:
     await page.goto(u,wait_until='networkidle',timeout=45000);shot=f'page-{idx:03d}.png';await page.screenshot(path=str(folder/shot),full_page=True)
     try:await page.add_script_tag(url=AXE_JS)
     except:raise RuntimeError('Could not load axe-core. Ensure the scan host has internet access to the configured axe script.')
     result=await page.evaluate('''async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})''')
     for v in result.get('violations',[]):
      for node in v.get('nodes',[]):all_issues.append({'page':u,'rule':v['id'],'impact':v.get('impact'),'help':v.get('help'),'helpUrl':v.get('helpUrl'),'wcag':v.get('tags',[]),'target':' > '.join(node.get('target',[])),'html':node.get('html',''),'failure':node.get('failureSummary',''),'screenshot':shot})
    except Exception as e:all_issues.append({'page':u,'rule':'scan-error','impact':'incomplete','help':'Page could not be scanned','failure':str(e),'target':'','html':'','wcag':[],'screenshot':''})
    finally:await page.close()
   await browser.close()
  (folder/'issues.json').write_text(json.dumps(all_issues,indent=2),encoding='utf-8');make_report(folder,target,pages,all_issues);make_zip(folder,scan_id)
  dbexec('UPDATE scans SET status=?,finished=?,pages=?,issues=? WHERE id=?',('completed',time.time(),len(pages),len([x for x in all_issues if x['rule']!='scan-error']),scan_id))
 except Exception as e:dbexec('UPDATE scans SET status=?,finished=?,error=? WHERE id=?',('failed',time.time(),str(e),scan_id))
def make_report(folder,target,pages,issues):
 rows=''.join(f"<tr><td>{html.escape(i['impact'] or '')}</td><td>{html.escape(i['rule'])}</td><td>{html.escape(i['page'])}</td><td><code>{html.escape(i['target'])}</code></td><td>{html.escape(i['failure'])}</td></tr>" for i in issues)
 doc=f'''<!doctype html><meta charset="utf-8"><title>AccessBatch report</title><style>body{{font:14px system-ui;margin:32px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;vertical-align:top}}th{{background:#111827;color:white}}code{{white-space:pre-wrap}}</style><h1>AccessBatch accessibility scan</h1><p><b>Target:</b> {html.escape(target)}</p><p><b>Pages scanned:</b> {len(pages)} &nbsp; <b>Issues:</b> {len(issues)}</p><p>Automated findings require human review and do not establish WCAG conformance.</p><table><tr><th>Impact</th><th>Rule</th><th>Page</th><th>Target</th><th>Developer guidance</th></tr>{rows}</table>''';(folder/'report.html').write_text(doc,encoding='utf-8')
def make_zip(folder,sid):
 with zipfile.ZipFile(folder/f'accessbatch-{sid}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in folder.iterdir():
   if p.suffix in ('.png','.json','.html'):z.write(p,p.name)
@app.get('/',response_class=HTMLResponse)
def home(request:Request):
 scans=dbexec('SELECT id,target,status,created,pages,issues FROM scans ORDER BY created DESC LIMIT 30',fetch=True);return templates.TemplateResponse('index.html',{'request':request,'scans':scans})
@app.post('/scan')
def scan(background_tasks:BackgroundTasks,target:str=Form(...),max_pages:int=Form(10)):
 if not target.startswith(('http://','https://')):raise HTTPException(400,'Target must start with http:// or https://')
 sid=uuid.uuid4().hex[:12];max_pages=max(1,min(max_pages,100));dbexec('INSERT INTO scans VALUES(?,?,?,?,?,?,?,?)',(sid,target,'queued',time.time(),None,0,0,None));background_tasks.add_task(run_scan,sid,target,max_pages);return {'scan_id':sid,'status_url':f'/api/scans/{sid}'}
@app.get('/api/scans/{sid}')
def status(sid:str):
 r=dbexec('SELECT id,target,status,created,finished,pages,issues,error FROM scans WHERE id=?',(sid,),True)
 if not r:raise HTTPException(404);x=r[0];return dict(zip(['id','target','status','created','finished','pages','issues','error'],x))
@app.get('/report/{sid}',response_class=HTMLResponse)
def report(sid:str):
 p=OUT/sid/'report.html'
 if not p.exists():raise HTTPException(404,'Report not ready');return HTMLResponse(p.read_text(encoding='utf-8'))
@app.get('/bundle/{sid}')
def bundle(sid:str):
 p=OUT/sid/f'accessbatch-{sid}.zip'
 if not p.exists():raise HTTPException(404,'Bundle not ready');return FileResponse(p,filename=p.name)
