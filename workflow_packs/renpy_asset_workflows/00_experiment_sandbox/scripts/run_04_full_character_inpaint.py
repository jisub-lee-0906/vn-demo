#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_full_character_inpaint_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
SRC=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
ALPHA_SRC=COMFY/'output/hermes_vn_toonout_other_character/alpha_silver_bob_v190_rftrue_blur1_nobgcolor_seed719251035_00001_.png'
POSE=COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'
CURRENT_BEST=COMFY/'output/hermes_vn_04_alpha_minus_head_seedhunt_20260513/composite_g28_d88_seed719254291_00001_.png'
POS=('masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_explicit, '
     '1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, '
     'arms_crossed, crossed_arms, folded_arms, short_hair, bob_cut, silver_hair, blue_eyes, small_face, neat_bangs, '
     'beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, grey_background')
NEG=('modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, '
     'long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, '
     'signature, watermark, username, conjoined, bad_ai-generated, smile, open_mouth, happy, frown, angry, annoyed, serious, stern, pouting, '
     'sad, crying, tears, scared, disgusted, surprised, arms_at_sides, hands_at_sides, hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, '
     'extra_hands, extra_arms, detached_hands, side_hands, duplicate_hands, long_neck, detached_head, floating_head, bad_neck, bad_shoulders, '
     'large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, white_background, bright_background, gradient_background, '
     'patterned_background, black_background, dark_background, vignette, thick_outline, rim_lighting, (worst quality, bad quality:1.2)')

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
        for img in node.get('images',[]): arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr

def make_mask(name,grow=0, head_cut=0):
    dst=INDIR/name
    filters=['alphaextract','format=gray','lut=y=if(gte(val\\,16)\\,255\\,0)']
    if grow:
        # max filter approximates dilation; repeat for grow amount in chunks.
        reps=max(1,grow//4)
        filters += ['erosion=coordinates=255']*reps  # for white on black in ffmpeg, erosion expands white in this setup? verified by prior generated masks via Comfy GrowMask later mainly.
    filters += ['format=rgb24']
    vf=','.join(filters)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ALPHA_SRC),'-vf',vf,'-frames:v','1',str(dst)],check=True)
    return f'{RUN}/{name}'

def build(mask_rel, denoise, seed, slug, grow_node):
    return {
      '1': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/source01.png'}},
      '2': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/pose_arms_crossed.png'}},
      '3': {'class_type':'LoadImage','inputs':{'image':mask_rel}},
      '4': {'class_type':'ImageToMask','inputs':{'image':['3',0],'channel':'red'}},
      '5': {'class_type':'GrowMask','inputs':{'mask':['4',0],'expand':grow_node,'tapered_corners':True}},
      '6': {'class_type':'ImpactGaussianBlurMask','inputs':{'mask':['5',0],'kernel_size':8,'sigma':4.0}},
      '7': {'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'novaAnimeXL_ilV190.safetensors'}},
      '8': {'class_type':'CLIPTextEncode','inputs':{'clip':['7',1],'text':POS}},
      '9': {'class_type':'CLIPTextEncode','inputs':{'clip':['7',1],'text':NEG}},
      '10': {'class_type':'DifferentialDiffusion','inputs':{'model':['7',0],'strength':1.0}},
      '11': {'class_type':'InpaintModelConditioning','inputs':{'positive':['8',0],'negative':['9',0],'vae':['7',2],'pixels':['1',0],'mask':['6',0],'noise_mask':True}},
      '12': {'class_type':'OpenposePreprocessor','inputs':{'image':['2',0],'detect_hand':'enable','detect_body':'enable','detect_face':'disable','resolution':1024,'scale_stick_for_xinsr_cn':'enable'}},
      '13': {'class_type':'ControlNetLoader','inputs':{'control_net_name':'xinsir-controlnet-union-sdxl-1.0-promax.safetensors'}},
      '14': {'class_type':'SetUnionControlNetType','inputs':{'control_net':['13',0],'type':'openpose'}},
      '15': {'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['11',0],'negative':['11',1],'control_net':['14',0],'image':['12',0],'strength':1.0,'start_percent':0.0,'end_percent':0.90,'vae':['7',2]}},
      '16': {'class_type':'KSampler','inputs':{'model':['10',0],'positive':['15',0],'negative':['15',1],'latent_image':['11',2],'seed':seed,'steps':28,'cfg':5.0,'sampler_name':'euler_ancestral','scheduler':'karras','denoise':denoise}},
      '17': {'class_type':'VAEDecode','inputs':{'samples':['16',0],'vae':['7',2]}},
      '18': {'class_type':'ImageCompositeMasked','inputs':{'destination':['1',0],'source':['17',0],'x':0,'y':0,'resize_source':False,'mask':['6',0]}},
      '19': {'class_type':'MaskToImage','inputs':{'mask':['6',0]}},
      '20': {'class_type':'SaveImage','inputs':{'images':['19',0],'filename_prefix':f'{RUN}/mask_{slug}'}},
      '21': {'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':f'{RUN}/openpose_{slug}'}},
      '22': {'class_type':'SaveImage','inputs':{'images':['17',0],'filename_prefix':f'{RUN}/raw_{slug}'}},
      '23': {'class_type':'SaveImage','inputs':{'images':['18',0],'filename_prefix':f'{RUN}/composite_{slug}'}},
    }

def make_contact(manifest):
    files=[SRC,CURRENT_BEST]
    for v in manifest['variants']:
        files += [Path([o['path'] for o in v['outputs'] if o['node']=='20'][0]), Path([o['path'] for o in v['outputs'] if o['node']=='23'][0])]
    inputs=[]; labels=[]
    for i,f in enumerate(files):
        inputs += ['-i',str(f)]
        labels.append(f'[{i}:v]scale=384:512:force_original_aspect_ratio=decrease,pad=384:512:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[v{i}]')
    n=len(files)
    if n%2: labels.append(f'color=white:s=384x512:d=0.1,setsar=1[v{n}]'); n+=1
    layout='|'.join(('0' if i%2==0 else '384')+'_'+str((i//2)*512) for i in range(n))
    filt=';'.join(labels)+';'+''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout={layout}[out]'
    dst=OUTDIR/'contact_full_character_inpaint.png'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)],check=True)
    return str(dst)

def main():
    shutil.copy2(SRC,INDIR/'source01.png'); shutil.copy2(POSE,INDIR/'pose_arms_crossed.png')
    mask=make_mask('alpha_character_mask.png')
    variants=[
        ('full_g16_d70',16,0.70,719254501),
        ('full_g16_d78',16,0.78,719254502),
        ('full_g24_d70',24,0.70,719254503),
        ('full_g24_d82',24,0.82,719254504),
        ('full_g28_d88',28,0.88,719254505),
    ]
    manifest={'run':RUN,'purpose':'Test user hypothesis: inpaint head and body together inside full/grown character alpha, without subtracting Florence head/hair/face, to reduce head-body separation while checking face preservation.','variants':[]}
    for slug,grow,denoise,seed in variants:
        p=build(mask,denoise,seed,slug,grow)
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_04_full_character_inpaint_{slug}_api.json'
        wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
        pid,h=submit(p)
        manifest['variants'].append({'slug':slug,'grow':grow,'denoise':denoise,'seed':seed,'prompt_id':pid,'workflow_api':str(wf),'outputs':outputs(h)})
    manifest['contact_sheet']=make_contact(manifest)
    mp=OUTDIR/'manifest_full_character_inpaint.json'; mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
