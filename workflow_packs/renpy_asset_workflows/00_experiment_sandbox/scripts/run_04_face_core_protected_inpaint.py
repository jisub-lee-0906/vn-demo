#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path

COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_face_core_protected_inpaint_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
SRC=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
ALPHA_SRC=COMFY/'output/hermes_vn_toonout_other_character/alpha_silver_bob_v190_rftrue_blur1_nobgcolor_seed719251035_00001_.png'
POSE=COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'
CURRENT_BEST=COMFY/'output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/composite_g28_d88_seed719254291_00001_.png'
BASE=ROOT/'00_experiment_sandbox/workflow_api/00_04_alpha_minus_head_sweep2_g28_d88_seed719254291_api.json'


def http_json(path,payload=None,timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
        raw=r.read().decode(); return json.loads(raw) if raw else {}


def submit(p,timeout_s=1200):
    q=http_json('/queue',timeout=5)
    if q.get('queue_running') or q.get('queue_pending'):
        raise RuntimeError(q)
    pid=http_json('/prompt',{'prompt':p})['prompt_id']; start=time.time()
    while time.time()-start<timeout_s:
        h=http_json(f'/history/{pid}',timeout=30)
        if pid in h:
            st=h[pid].get('status',{})
            if not st.get('completed'):
                raise RuntimeError(st)
            return pid,h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def outputs(h):
    arr=[]
    for nid,node in h.get('outputs',{}).items():
        for img in node.get('images',[]):
            arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr


def make_inputs():
    shutil.copy2(SRC,INDIR/'source01.png')
    shutil.copy2(POSE,INDIR/'pose_arms_crossed.png')
    dst=INDIR/'alpha_character_mask_from_02.png'
    vf='alphaextract,format=gray,lut=y=if(gte(val\\,16)\\,255\\,0),format=rgb24'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ALPHA_SRC),'-vf',vf,'-frames:v','1',str(dst)],check=True)


def configure(base, *, slug, protect_terms, protect_offset, protect_blur, protect_smooth, alpha_grow, edit_grow, denoise, seed):
    p=json.loads(json.dumps(base))
    p['1']['inputs']['image']=f'{RUN}/source01.png'
    p['2']['inputs']['image']=f'{RUN}/pose_arms_crossed.png'
    p['3']['inputs']['image']=f'{RUN}/alpha_character_mask_from_02.png'

    # Middle route: protect only face core (or deliberately tiny face+bangs), while neck/shoulders/collar/body regenerate together.
    # Base graph ORs Florence nodes 6,7,8 into a protection mask; feed only the requested protection terms.
    for nid,term in zip(['6','7','8'], protect_terms):
        p[nid]['inputs']['text_input']=term
        p[nid]['inputs']['keep_model_loaded']=(nid!='8')
    p['11']['inputs']['mask_offset']=protect_offset
    p['11']['inputs']['mask_blur']=protect_blur
    p['11']['inputs']['smooth']=protect_smooth
    p['34']['inputs']['expand']=alpha_grow
    p['13']['inputs']['expand']=edit_grow
    p['24']['inputs']['seed']=seed
    p['24']['inputs']['denoise']=denoise
    for nid,prefix in [('29','protect_facecore'),('30','edit_alpha_minus_facecore'),('31','openpose'),('32','raw'),('33','composite')]:
        p[nid]['inputs']['filename_prefix']=f'{RUN}/{prefix}_{slug}'
    return p


def make_contact(manifest):
    files=[SRC,CURRENT_BEST]
    labels_text=['01 source','prev best head-protect']
    for v in manifest['variants']:
        files += [Path([o['path'] for o in v['outputs'] if o['node']=='29'][0]), Path([o['path'] for o in v['outputs'] if o['node']=='30'][0]), Path([o['path'] for o in v['outputs'] if o['node']=='33'][0])]
        labels_text += [v['slug']+' protect', v['slug']+' edit', v['slug']+' comp']
    inputs=[]; filters=[]
    for i,f in enumerate(files):
        inputs+=['-i',str(f)]
        # image-only contact sheet; filenames/manifest carry labels to avoid font dependency.
        filters.append(f'[{i}:v]scale=384:512:force_original_aspect_ratio=decrease,pad=384:512:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[v{i}]')
    n=len(files)
    cols=3
    while n % cols:
        filters.append(f'color=white:s=384x512:d=0.1,setsar=1[v{n}]')
        n += 1
    layout='|'.join(f'{(i%cols)*384}_{(i//cols)*512}' for i in range(n))
    filt=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout={layout}[out]'
    dst=OUTDIR/'contact_face_core_protected_inpaint.png'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)],check=True)
    (OUTDIR/'contact_face_core_labels.txt').write_text('\n'.join(f'{i}: {lab} -> {path}' for i,(lab,path) in enumerate(zip(labels_text,files))),encoding='utf-8')
    return str(dst)


def main():
    make_inputs()
    base=json.loads(BASE.read_text(encoding='utf-8'))
    variants=[
        # face-core only: lower offsets should keep eyes/mouth while freeing jaw/neck/shoulder seam.
        {'slug':'face_o08_g28_d88_s291','protect_terms':['face','face','face'],'protect_offset':8,'protect_blur':4,'protect_smooth':1.0,'alpha_grow':28,'edit_grow':6,'denoise':0.88,'seed':719254291},
        {'slug':'face_o14_g28_d88_s291','protect_terms':['face','face','face'],'protect_offset':14,'protect_blur':5,'protect_smooth':1.0,'alpha_grow':28,'edit_grow':6,'denoise':0.88,'seed':719254291},
        {'slug':'face_o20_g28_d88_s291','protect_terms':['face','face','face'],'protect_offset':20,'protect_blur':6,'protect_smooth':1.0,'alpha_grow':28,'edit_grow':6,'denoise':0.88,'seed':719254291},
        # slightly wider variant: face plus bangs/front hair, still not full head/hair protection.
        {'slug':'face_bangs_o12_g28_d88_s291','protect_terms':['face','bangs','front hair'],'protect_offset':12,'protect_blur':5,'protect_smooth':1.0,'alpha_grow':28,'edit_grow':6,'denoise':0.88,'seed':719254291},
        # lower denoise sanity check: see whether face identity improves without losing arms-crossed readability.
        {'slug':'face_o14_g28_d82_s291','protect_terms':['face','face','face'],'protect_offset':14,'protect_blur':5,'protect_smooth':1.0,'alpha_grow':28,'edit_grow':6,'denoise':0.82,'seed':719254291},
    ]
    manifest={'run':RUN,'purpose':'Middle-route 04 test: protect only face core or face+front-hair while allowing neck/shoulders/collar/body to regenerate together, aiming to reduce seam without full-character face drift.','source':str(SRC),'alpha_source':str(ALPHA_SRC),'pose':str(POSE),'previous_best':str(CURRENT_BEST),'variants':[]}
    for v in variants:
        p=configure(base,**v)
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f"00_04_face_core_protected_{v['slug']}_api.json"
        wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
        pid,h=submit(p)
        rec=dict(v); rec.update({'prompt_id':pid,'workflow_api':str(wf),'outputs':outputs(h)})
        manifest['variants'].append(rec)
    manifest['contact_sheet']=make_contact(manifest)
    mp=OUTDIR/'manifest_face_core_protected_inpaint.json'
    mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
