#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_alpha_minus_head_02_gate_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
TEMPLATE=ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json'
CANDIDATES={
 'prev_g32_d90': COMFY/'output/hermes_vn_04_alpha_minus_head_inpaint_20260513/composite_d90_alphagrow32_hard_seed719254291_00001_.png',
 'g24_d90': COMFY/'output/hermes_vn_04_alpha_minus_head_sweep2_20260513/composite_g24_d90_seed719254291_00001_.png',
 'g28_d88': COMFY/'output/hermes_vn_04_alpha_minus_head_sweep2_20260513/composite_g28_d88_seed719254291_00001_.png',
}

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

def outputs(h):
    arr=[]
    for nid,node in h.get('outputs',{}).items():
        for img in node.get('images',[]):
            arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr

def alpha_preview(alpha_path: Path, slug: str):
    white=OUTDIR/f'preview_{slug}_white.png'
    dark=OUTDIR/f'preview_{slug}_dark.png'
    split=OUTDIR/f'preview_{slug}_white_dark.png'
    for color,dst in [('white',white),('#202020',dark)]:
        subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i',f'color={color}:s=1152x1536','-i',str(alpha_path),'-filter_complex','[0:v][1:v]overlay=format=auto,format=rgb24[out]','-map','[out]','-frames:v','1',str(dst)],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(white),'-i',str(dark),'-filter_complex','[0:v]scale=384:512:force_original_aspect_ratio=decrease,pad=384:512:(ow-iw)/2:(oh-ih)/2:white[v0];[1:v]scale=384:512:force_original_aspect_ratio=decrease,pad=384:512:(ow-iw)/2:(oh-ih)/2:white[v1];[v0][v1]hstack=inputs=2[out]','-map','[out]','-frames:v','1',str(split)],check=True)
    return str(split)

def contact(previews):
    inputs=[]; labels=[]
    for i,p in enumerate(previews):
        inputs += ['-i',p]
        labels.append(f'[{i}:v]setsar=1[v{i}]')
    filt=';'.join(labels)+';'+''.join(f'[v{i}]' for i in range(len(previews)))+f'vstack=inputs={len(previews)}[out]'
    dst=OUTDIR/'contact_02_light_dark_candidates.png'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)],check=True)
    return str(dst)

def main():
    tpl=json.loads(TEMPLATE.read_text())
    manifest={'run':RUN,'purpose':'02 alpha smoke gate for best alpha-minus-head 04 candidates; build light/dark composites to inspect edge/ghost/halo.','candidates':[]}
    previews=[]
    for slug,src in CANDIDATES.items():
        if not src.exists(): raise FileNotFoundError(src)
        in_name=f'{slug}.png'
        shutil.copy2(src, INDIR/in_name)
        p=json.loads(json.dumps(tpl))
        p['1']['inputs']['image']=f'{RUN}/{in_name}'
        p['3']['inputs']['filename_prefix']=f'{RUN}/alpha_{slug}_b1_ref1'
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_02_after_04_alpha_minus_head_{slug}_api.json'
        wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
        pid,h=submit(p)
        outs=outputs(h)
        alpha=Path(outs[0]['path'])
        preview=alpha_preview(alpha,slug)
        previews.append(preview)
        manifest['candidates'].append({'slug':slug,'source':str(src),'prompt_id':pid,'workflow_api':str(wf),'alpha_output':str(alpha),'preview_light_dark':preview,'outputs':outs})
    manifest['contact_sheet']=contact(previews)
    mp=OUTDIR/'manifest_02_gate.json'
    mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
