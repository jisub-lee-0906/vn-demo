#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, time, urllib.request
from pathlib import Path
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_direct_expression_test_20260513'
INDIR=COMFY/'input'/RUN
INDIR.mkdir(parents=True, exist_ok=True)

def http_json(path,payload=None,timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
        raw=r.read().decode(); return json.loads(raw) if raw else {}

def submit(p,timeout_s=1200):
    q=http_json('/queue',timeout=5)
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(q)
    pid=http_json('/prompt',{'prompt':p})['prompt_id']; start=time.time()
    while time.time()-start<timeout_s:
        h=http_json(f'/history/{pid}',timeout=30)
        if pid in h:
            st=h[pid].get('status',{})
            if not st.get('completed'): raise RuntimeError(st)
            return pid,h[pid]
        time.sleep(2)
    raise TimeoutError(pid)

def outs(h):
    arr=[]
    for nid,node in h.get('outputs',{}).items():
        for img in node.get('images',[]): arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr

def first(h,nid):
    for x in outs(h):
        if x['node']==nid: return x['path']
    raise RuntimeError(outs(h))

inputs=[
('happy_smile_no_openmouth','/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/04_direct_happy_smile_no_openmouth_seed719252501_00001_.png'),
('happy_openmouth','/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_04_direct_expression_test_20260513/04_direct_happy_openmouth_seed719252501_00001_.png'),
]
manifest={'run':RUN,'alpha_variants':[]}
for slug,src in inputs:
    dst=INDIR/f'04_direct_{slug}.png'; shutil.copy2(src,dst)
    p=json.loads((ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json').read_text(encoding='utf-8'))
    p['1']['inputs']['image']=f'{RUN}/{dst.name}'
    p['3']['inputs']['filename_prefix']=f'{RUN}/02_alpha_after_04_direct_{slug}_b1_ref1'
    pid,h=submit(p)
    manifest['alpha_variants'].append({'slug':slug,'prompt_id':pid,'source':src,'alpha_output':first(h,'3')})
mp=COMFY/'output'/RUN/'manifest_02_after_04_direct_expression.json'
mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest,indent=2,ensure_ascii=False))
