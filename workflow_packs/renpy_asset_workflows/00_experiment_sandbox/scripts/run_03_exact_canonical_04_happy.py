
from __future__ import annotations
import json, time, urllib.request, shutil
from pathlib import Path
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_expr_retest_20260513'
src=COMFY/'output/hermes_vn_chain_retest_20260513/no_thick_arms_crossed_src_00001_.png'
rel=f'{RUN}/{src.name}'
dst=COMFY/'input'/rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src,dst)
def http_json(path,payload=None,timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
        raw=r.read().decode(); return json.loads(raw) if raw else {}
def submit(p):
    q=http_json('/queue',timeout=5)
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(q)
    pid=http_json('/prompt',{'prompt':p})['prompt_id']
    st=time.time()
    while time.time()-st<900:
        h=http_json('/history/'+pid,timeout=30)
        if pid in h: return pid,h[pid]
        time.sleep(2)
    raise TimeoutError(pid)
p=json.loads((ROOT/'03_expression_variation_face_composite/workflow_api/03_expression_source_canonical_api.json').read_text())
p['1']['inputs']['image']=rel
p['15']['inputs']['filename_prefix']=RUN+'/04_arms_crossed_exact_canonical_happy_raw_inpaint'
p['17']['inputs']['filename_prefix']=RUN+'/04_arms_crossed_exact_canonical_happy_mask_preview'
p['19']['inputs']['filename_prefix']=RUN+'/04_arms_crossed_exact_canonical_happy_composited'
pid,h=submit(p)
outs=[]
for node_id,node in h.get('outputs',{}).items():
    for img in node.get('images',[]): outs.append({'node':node_id,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
print(json.dumps({'prompt_id':pid,'outputs':outs,'positive':p['6']['inputs']['text'],'negative':p['7']['inputs']['text']},indent=2,ensure_ascii=False))
