#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, time, urllib.request
from pathlib import Path

COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_florence_mask_probe_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
SRC=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'

def http_json(path,payload=None,timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
        raw=r.read().decode(); return json.loads(raw) if raw else {}

def submit(p,timeout_s=900):
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
        for img in node.get('images',[]):
            arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr

shutil.copy2(SRC, INDIR/'source01.png')
p={
 '1': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/source01.png'}},
 '2': {'class_type':'DownloadAndLoadFlorence2Model','inputs':{'model':'microsoft/Florence-2-large','precision':'fp16','convert_to_safetensors':False}},
}
terms=['face','head','hair','arms','hands','sleeves','cardigan','upper body']
node=3
manifest={'run':RUN,'source':str(SRC),'terms':[]}
for term in terms:
    run_id=str(node); enh_id=str(node+1); img_id=str(node+2); save_id=str(node+3)
    p[run_id]={'class_type':'Florence2Run','inputs':{'image':['1',0],'florence2_model':['2',0],'text_input':term,'task':'referring_expression_segmentation','fill_mask':True,'keep_model_loaded':False,'max_new_tokens':1024,'num_beams':3,'do_sample':False,'output_mask_select':'','seed':719251777}}
    p[enh_id]={'class_type':'AILab_MaskEnhancer','inputs':{'mask':[run_id,1],'sensitivity':1.0,'mask_blur':2,'mask_offset':0,'smooth':1.0,'fill_holes':True,'invert_output':False}}
    p[img_id]={'class_type':'MaskToImage','inputs':{'mask':[enh_id,0]}}
    p[save_id]={'class_type':'SaveImage','inputs':{'images':[img_id,0],'filename_prefix':f'{RUN}/mask_{term.replace(" ","_")}'}}
    manifest['terms'].append({'term':term,'save_node':save_id})
    node+=4
wf=ROOT/'00_experiment_sandbox/workflow_api/00_04_florence_mask_probe_api.json'
wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
pid,h=submit(p)
manifest['prompt_id']=pid; manifest['workflow_api']=str(wf); manifest['outputs']=outs(h)
mp=OUTDIR/'manifest_florence_mask_probe.json'; mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest,indent=2,ensure_ascii=False))
