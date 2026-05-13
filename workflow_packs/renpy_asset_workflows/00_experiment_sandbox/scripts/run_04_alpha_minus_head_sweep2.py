#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path

COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_alpha_minus_head_sweep2_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
SRC=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
ALPHA_SRC=COMFY/'output/hermes_vn_toonout_other_character/alpha_silver_bob_v190_rftrue_blur1_nobgcolor_seed719251035_00001_.png'
POSE=COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'
BASE=ROOT/'00_experiment_sandbox/workflow_api/00_04_alpha_minus_head_inpaint_d90_alphagrow32_hard_seed719254291_api.json'
PREV=COMFY/'output/hermes_vn_04_alpha_minus_head_inpaint_20260513/composite_d90_alphagrow32_hard_seed719254291_00001_.png'
ORIG=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'

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

def outputs(h):
    arr=[]
    for nid,node in h.get('outputs',{}).items():
        for img in node.get('images',[]):
            arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr

def copy_inputs():
    shutil.copy2(SRC, INDIR/'source01.png')
    shutil.copy2(POSE, INDIR/'pose_arms_crossed.png')
    dst=INDIR/'alpha_character_mask_from_02.png'
    vf='alphaextract,format=gray,lut=y=if(gte(val\\,16)\\,255\\,0),format=rgb24'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ALPHA_SRC),'-vf',vf,'-frames:v','1',str(dst)],check=True)

def retarget_inputs(p):
    p['1']['inputs']['image']=f'{RUN}/source01.png'
    p['2']['inputs']['image']=f'{RUN}/pose_arms_crossed.png'
    p['3']['inputs']['image']=f'{RUN}/alpha_character_mask_from_02.png'

def make_contact(manifest):
    files=[ORIG, PREV]
    for v in manifest['variants']:
        files.append(Path([o['path'] for o in v['outputs'] if o['node']=='30'][0]))
        files.append(Path([o['path'] for o in v['outputs'] if o['node']=='33'][0]))
    # 2 columns, enough rows
    inputs=[]; labels=[]
    for i,f in enumerate(files):
        inputs += ['-i',str(f)]
        labels.append(f'[{i}:v]scale=384:512:force_original_aspect_ratio=decrease,pad=384:512:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[v{i}]')
    n=len(files)
    if n%2:
        labels.append(f'color=white:s=384x512:d=0.1,setsar=1[v{n}]'); n+=1
    layout='|'.join(('0' if i%2==0 else '384')+'_'+str((i//2)*512) for i in range(n))
    filt=';'.join(labels)+';'+''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout={layout}[out]'
    dst=OUTDIR/'contact_alpha_minus_head_sweep2.png'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)],check=True)
    return str(dst)

def main():
    copy_inputs()
    variants=[
        {'grow':16,'denoise':0.90,'seed':719254291,'slug':'g16_d90_seed719254291'},
        {'grow':24,'denoise':0.90,'seed':719254291,'slug':'g24_d90_seed719254291'},
        {'grow':28,'denoise':0.90,'seed':719254291,'slug':'g28_d90_seed719254291'},
        {'grow':24,'denoise':0.86,'seed':719254291,'slug':'g24_d86_seed719254291'},
        {'grow':32,'denoise':0.86,'seed':719254291,'slug':'g32_d86_seed719254291'},
        {'grow':28,'denoise':0.88,'seed':719254291,'slug':'g28_d88_seed719254291'},
    ]
    manifest={'run':RUN,'source':str(SRC),'alpha_source':str(ALPHA_SRC),'baseline_previous_best':str(PREV),'purpose':'Second refinement sweep for alpha-grown character silhouette minus Florence head/hair/face protection. Same seed where possible; tune alpha grow and denoise for less old-side-hand ghosting with less outfit drift.','variants':[]}
    base=json.loads(BASE.read_text())
    for v in variants:
        p=json.loads(json.dumps(base))
        retarget_inputs(p)
        slug=v['slug']
        p['34']['inputs']['expand']=v['grow']
        p['24']['inputs']['denoise']=v['denoise']
        p['24']['inputs']['seed']=v['seed']
        # keep hard-ish final mask, but slightly less expansion after subtract to preserve torso details
        p['13']['inputs']['expand']=6
        p['14']['inputs']['kernel_size']=8
        p['14']['inputs']['sigma']=4.0
        for nid,prefix in [('29','protect_headhairface'),('30','edit_alpha_minus_head'),('31','openpose'),('32','raw'),('33','composite')]:
            p[nid]['inputs']['filename_prefix']=f'{RUN}/{prefix}_{slug}'
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_04_alpha_minus_head_sweep2_{slug}_api.json'
        wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
        pid,h=submit(p)
        item=dict(v); item.update({'prompt_id':pid,'workflow_api':str(wf),'outputs':outputs(h)})
        manifest['variants'].append(item)
    manifest['contact_sheet']=make_contact(manifest)
    mp=OUTDIR/'manifest_alpha_minus_head_sweep2.json'
    mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
