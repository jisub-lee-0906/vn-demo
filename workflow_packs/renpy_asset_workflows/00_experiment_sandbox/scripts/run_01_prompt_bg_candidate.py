#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request, shutil
from pathlib import Path
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT='http://172.28.224.1:8000'

def http_json(path,payload=None,timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
        raw=r.read().decode(); return json.loads(raw) if raw else {}

def submit(prompt,timeout_s=900):
    q=http_json('/queue',timeout=5)
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(f'queue busy {q}')
    pid=http_json('/prompt',{'prompt':prompt})['prompt_id']; start=time.time()
    while time.time()-start<timeout_s:
        h=http_json(f'/history/{pid}',timeout=30)
        if pid in h:
            st=h[pid].get('status',{})
            if not st.get('completed'): raise RuntimeError(f'failed {pid} {st}')
            return pid,h[pid]
        time.sleep(2)
    raise TimeoutError(pid)

def outs(h):
    out=[]
    for node in h.get('outputs',{}).values():
        for img in node.get('images',[]): out.append(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])
    return out

p=json.loads((ROOT/'01_character_anchor_and_prompt/workflow_api/01_character_anchor_apose_neutral_api.json').read_text())
p['3']['inputs']['text']=p['3']['inputs']['text'].replace(', BREAK depth_of_field, volumetric_lighting','')
p['8']['inputs']['filename_prefix']='hermes_vn_chain_retest_20260513/01_no_depth_volumetric_source'
pid01,h01=submit(p)
src=[x for x in outs(h01) if '01_no_depth_volumetric_source' in str(x)][0]
rel='hermes_vn_chain_retest_20260513/01_no_depth_volumetric_source.png'
ip=COMFY/'input'/rel; ip.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,ip)
a=json.loads((ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json').read_text())
a['1']['inputs']['image']=rel
a['3']['inputs']['filename_prefix']='hermes_vn_chain_retest_20260513/01_no_depth_volumetric_alpha_b1_ref1'
pid02,h02=submit(a)
alpha=[x for x in outs(h02) if '01_no_depth_volumetric_alpha_b1_ref1' in str(x)][0]
manifest={'01_prompt_id':pid01,'02_prompt_id':pid02,'01_source':str(src),'02_alpha':str(alpha),'positive':p['3']['inputs']['text'],'negative':p['4']['inputs']['text']}
mp=COMFY/'output/hermes_vn_chain_retest_20260513/manifest_01_no_depth_volumetric.json'
mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest,indent=2,ensure_ascii=False))
