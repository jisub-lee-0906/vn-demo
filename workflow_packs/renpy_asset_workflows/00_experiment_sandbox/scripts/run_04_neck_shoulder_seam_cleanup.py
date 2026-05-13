#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_neck_shoulder_cleanup_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
SRC=COMFY/'output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/composite_g28_d88_seed719254291_00001_.png'
ALT=COMFY/'output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/composite_g28_d88_seed719254292_00001_.png'
POS=('masterpiece, best quality, amazing quality, high_resolution, rating_explicit, '
     '1girl, solo, front_view, looking_at_viewer, expressionless, closed_mouth, '
     'short_hair, bob_cut, silver_hair, blue_eyes, neck, shoulders, collarbone, shirt_collar, blue_bowtie, beige_cardigan, white_shirt, long_sleeves, arms_crossed, grey_background')
NEG=('lowres, bad_anatomy, bad_hands, extra_digits, missing_fingers, deformed, ugly, sketch, jpeg_artifacts, watermark, text, '
     'detached_head, floating_head, long_neck, broken_neck, extra_neck, dislocated_neck, head_tilt, bad_shoulders, asymmetrical_shoulders, '
     'extra_hands, extra_arms, hands_at_sides, arms_at_sides, smile, open_mouth, thick_outline, rim_lighting, dark_background, black_background, '
     '(worst quality, bad quality:1.2)')

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
        for img in node.get('images',[]): arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr

def make_mask(name, kind):
    dst=INDIR/name
    if kind=='tight':
        vf='drawbox=x=385:y=315:w=380:h=260:color=white:t=fill'
    elif kind=='shoulder':
        vf='drawbox=x=300:y=320:w=560:h=330:color=white:t=fill'
    else:
        vf='drawbox=x=335:y=285:w=500:h=390:color=white:t=fill'
    # black out upper face area to avoid changing eyes/fringe; blur edges for seam only
    vf=f'color=black:s=1152x1536,{vf},drawbox=x=0:y=0:w=1152:h=275:color=black:t=fill,gblur=sigma=7'
    subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i',vf,'-frames:v','1',str(dst)],check=True)
    return f'{RUN}/{name}'

def build(mask_rel, denoise, seed, slug):
    return {
      '1': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/source.png'}},
      '2': {'class_type':'LoadImage','inputs':{'image':mask_rel}},
      '3': {'class_type':'ImageToMask','inputs':{'image':['2',0],'channel':'red'}},
      '4': {'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'novaAnimeXL_ilV190.safetensors'}},
      '5': {'class_type':'CLIPTextEncode','inputs':{'clip':['4',1],'text':POS}},
      '6': {'class_type':'CLIPTextEncode','inputs':{'clip':['4',1],'text':NEG}},
      '7': {'class_type':'DifferentialDiffusion','inputs':{'model':['4',0],'strength':1.0}},
      '8': {'class_type':'InpaintModelConditioning','inputs':{'positive':['5',0],'negative':['6',0],'vae':['4',2],'pixels':['1',0],'mask':['3',0],'noise_mask':True}},
      '9': {'class_type':'KSampler','inputs':{'model':['7',0],'positive':['8',0],'negative':['8',1],'latent_image':['8',2],'seed':seed,'steps':24,'cfg':4.5,'sampler_name':'euler_ancestral','scheduler':'karras','denoise':denoise}},
      '10': {'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['4',2]}},
      '11': {'class_type':'ImageCompositeMasked','inputs':{'destination':['1',0],'source':['10',0],'x':0,'y':0,'resize_source':False,'mask':['3',0]}},
      '12': {'class_type':'MaskToImage','inputs':{'mask':['3',0]}},
      '13': {'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':f'{RUN}/mask_{slug}'}},
      '14': {'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':f'{RUN}/raw_{slug}'}},
      '15': {'class_type':'SaveImage','inputs':{'images':['11',0],'filename_prefix':f'{RUN}/composite_{slug}'}},
    }

def make_contact(manifest):
    files=[SRC]
    for v in manifest['variants']:
        files += [Path([o['path'] for o in v['outputs'] if o['node']=='13'][0]), Path([o['path'] for o in v['outputs'] if o['node']=='15'][0])]
    inputs=[]; labels=[]
    for i,f in enumerate(files):
        inputs += ['-i',str(f)]
        labels.append(f'[{i}:v]scale=384:512:force_original_aspect_ratio=decrease,pad=384:512:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[v{i}]')
    n=len(files)
    if n%2: labels.append(f'color=white:s=384x512:d=0.1,setsar=1[v{n}]'); n+=1
    layout='|'.join(('0' if i%2==0 else '384')+'_'+str((i//2)*512) for i in range(n))
    filt=';'.join(labels)+';'+''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout={layout}[out]'
    dst=OUTDIR/'contact_neck_shoulder_cleanup.png'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)],check=True)
    return str(dst)

def main():
    if not SRC.exists(): raise FileNotFoundError(SRC)
    shutil.copy2(SRC, INDIR/'source.png')
    variants=[('tight',0.26,719254401),('tight',0.34,719254402),('shoulder',0.30,719254403),('shoulder',0.38,719254404),('wide',0.30,719254405)]
    manifest={'run':RUN,'source':str(SRC),'purpose':'Low-denoise seam cleanup for neck/shoulder/collar area where original head and generated crossed-arms body feel subtly separated.','variants':[]}
    masks={k:make_mask(f'mask_{k}.png',k) for k in ['tight','shoulder','wide']}
    for kind,denoise,seed in variants:
        slug=f'{kind}_d{int(denoise*100):02d}_seed{seed}'
        p=build(masks[kind],denoise,seed,slug)
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_04_neck_shoulder_cleanup_{slug}_api.json'
        wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
        pid,h=submit(p)
        manifest['variants'].append({'slug':slug,'mask':kind,'denoise':denoise,'seed':seed,'prompt_id':pid,'workflow_api':str(wf),'outputs':outputs(h)})
    manifest['contact_sheet']=make_contact(manifest)
    mp=OUTDIR/'manifest_neck_shoulder_cleanup.json'; mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
