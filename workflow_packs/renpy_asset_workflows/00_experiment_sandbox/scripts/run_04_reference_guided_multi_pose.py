#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path

COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_reference_guided_multi_pose_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
SRC=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
ALPHA_SRC=COMFY/'output/hermes_vn_toonout_other_character/alpha_silver_bob_v190_rftrue_blur1_nobgcolor_seed719251035_00001_.png'
BASE=ROOT/'00_experiment_sandbox/workflow_api/00_04_alpha_minus_head_sweep2_g28_d88_seed719254291_api.json'
POSE_REFS={
    'arms_crossed': COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png',
    'hand_chest': COMFY/'input/hermes_pose_ref_multi04b_silver_bob_hand_chest.png',
    'pointing': COMFY/'input/hermes_pose_ref_multi04b_silver_bob_pointing.png',
}
POSE_TAGS={
    'arms_crossed': 'arms_crossed, crossed_arms, folded_arms',
    'hand_chest': 'hand_on_chest, one_hand_on_chest, bent_arm',
    'pointing': 'pointing, pointing_at_viewer, outstretched_arm, extended_arm',
}
NEG_POSE={
    'arms_crossed': 'arms_at_sides, hands_at_sides, hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, pointing, outstretched_arm',
    'hand_chest': 'arms_crossed, crossed_arms, folded_arms, arms_at_sides, hands_at_sides, hands_on_hips, pointing, outstretched_arm',
    'pointing': 'arms_crossed, crossed_arms, folded_arms, arms_at_sides, hands_at_sides, hands_on_hips, hand_on_chest, hands_in_pockets',
}
POS_BASE=('masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_explicit, '
          '1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, '
          'short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, grey_background')
NEG_BASE=('modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, '
          'long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, '
          'signature, watermark, username, conjoined, bad_ai-generated, smile, open_mouth, happy, frown, angry, annoyed, serious, stern, pouting, '
          'sad, crying, tears, scared, disgusted, surprised, extra_hands, extra_arms, detached_hands, side_hands, duplicate_hands, '
          'large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, white_background, bright_background, gradient_background, patterned_background, black_background, dark_background, vignette, thick_outline, rim_lighting, (worst quality, bad quality:1.2)')

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

def make_alpha_mask():
    dst=INDIR/'alpha_character_mask_from_02.png'
    vf='alphaextract,format=gray,lut=y=if(gte(val\\,16)\\,255\\,0),format=rgb24'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ALPHA_SRC),'-vf',vf,'-frames:v','1',str(dst)],check=True)

def make_masked_ref(src:Path, dst:Path):
    # Keep a broad arm/torso reference region, black out head and lower legs.
    # This lets Canny carry sleeve/arm silhouette without forcing donor face/hair/background.
    # Assumes current VN sprite canvas ~1152x1536; drawbox coords are deliberately broad for pointing.
    vf='drawbox=x=0:y=0:w=iw:h=330:color=black:t=fill,drawbox=x=0:y=1180:w=iw:h=ih-1180:color=black:t=fill,drawbox=x=0:y=0:w=70:h=ih:color=black:t=fill,drawbox=x=1082:y=0:w=iw-1082:h=ih:color=black:t=fill'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-vf',vf,'-frames:v','1',str(dst)],check=True)

def prepare_inputs():
    shutil.copy2(SRC, INDIR/'source01.png')
    make_alpha_mask()
    for pose, path in POSE_REFS.items():
        shutil.copy2(path, INDIR/f'pose_ref_{pose}.png')
        make_masked_ref(path, INDIR/f'pose_ref_{pose}_arms_torso_only.png')

def configure(base, pose, canny_strength, denoise, seed):
    p=json.loads(json.dumps(base))
    p['1']['inputs']['image']=f'{RUN}/source01.png'
    p['2']['inputs']['image']=f'{RUN}/pose_ref_{pose}.png'
    p['3']['inputs']['image']=f'{RUN}/alpha_character_mask_from_02.png'
    p['16']['inputs']['text']=POS_BASE + ', ' + POSE_TAGS[pose]
    p['17']['inputs']['text']=NEG_BASE + ', ' + NEG_POSE[pose]
    p['24']['inputs']['seed']=seed
    p['24']['inputs']['denoise']=denoise
    p['23']['inputs']['strength']=1.0
    p['23']['inputs']['end_percent']=0.90
    # Reference-image structural branch: masked Canny from the pose reference, stacked after OpenPose.
    p['35']={'class_type':'LoadImage','inputs':{'image':f'{RUN}/pose_ref_{pose}_arms_torso_only.png'}}
    p['36']={'class_type':'CannyEdgePreprocessor','inputs':{'image':['35',0],'low_threshold':80,'high_threshold':180,'resolution':1024}}
    p['37']={'class_type':'ControlNetLoader','inputs':{'control_net_name':'xinsir-controlnet-union-sdxl-1.0-promax.safetensors'}}
    p['38']={'class_type':'SetUnionControlNetType','inputs':{'control_net':['37',0],'type':'canny/lineart/anime_lineart/mlsd'}}
    p['39']={'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['23',0],'negative':['23',1],'control_net':['38',0],'image':['36',0],'strength':canny_strength,'start_percent':0.0,'end_percent':0.55,'vae':['15',2]}}
    p['40']={'class_type':'SaveImage','inputs':{'images':['36',0],'filename_prefix':f'{RUN}/canny_masked_{pose}_cs{int(canny_strength*100)}'}}
    p['24']['inputs']['positive']=['39',0]
    p['24']['inputs']['negative']=['39',1]
    slug=f'{pose}_op100_canny{int(canny_strength*100)}_d{int(denoise*100)}_seed{seed}'
    for nid,prefix in [('29','protect_headhairface'),('30','edit_alpha_minus_head'),('31','openpose'),('32','raw'),('33','composite')]:
        p[nid]['inputs']['filename_prefix']=f'{RUN}/{prefix}_{slug}'
    return p, slug

def make_contact(manifest):
    files=[SRC]
    labels=['01_source']
    for item in manifest['variants']:
        outs=item['outputs']
        def node_path(n): return Path([o['path'] for o in outs if o['node']==n][0])
        files += [Path(item['pose_reference']), Path(item['masked_reference']), node_path('40'), node_path('33')]
        labels += [item['pose']+'_ref', item['pose']+'_masked_ref', item['pose']+'_canny', item['pose']+'_composite']
    inputs=[]; filters=[]
    for i,f in enumerate(files):
        inputs += ['-i',str(f)]
        filters.append(f'[{i}:v]scale=288:384:force_original_aspect_ratio=decrease,pad=288:384:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[v{i}]')
    cols=4; n=len(files)
    while n%cols:
        filters.append(f'color=white:s=288x384:d=0.1,setsar=1[v{n}]'); n+=1
    layout='|'.join(f'{(i%cols)*288}_{(i//cols)*384}' for i in range(n))
    filt=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout={layout}[out]'
    dst=OUTDIR/'contact_reference_guided_multi_pose.png'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)],check=True)
    (OUTDIR/'contact_reference_guided_labels.txt').write_text('\n'.join(f'{i}: {lab} -> {path}' for i,(lab,path) in enumerate(zip(labels,files))),encoding='utf-8')
    return str(dst)

def main():
    prepare_inputs()
    base=json.loads(BASE.read_text(encoding='utf-8'))
    # Smoke across multiple poses first, one conservative Canny strength. Do not overfit arms-crossed.
    variants=[
        ('arms_crossed',0.35,0.88,719255101),
        ('hand_chest',0.35,0.86,719255102),
        ('pointing',0.30,0.86,719255103),
    ]
    manifest={'run':RUN,'purpose':'Image-reference guided 04 smoke across multiple poses: OpenPose from reference plus masked Canny arms/torso reference, while preserving 01 head/hair/face via alpha-minus-head mask.','source':str(SRC),'alpha_source':str(ALPHA_SRC),'variants':[]}
    for pose,canny_strength,denoise,seed in variants:
        p,slug=configure(base,pose,canny_strength,denoise,seed)
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_04_reference_guided_multi_pose_{slug}_api.json'
        wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
        pid,h=submit(p)
        manifest['variants'].append({'pose':pose,'slug':slug,'canny_strength':canny_strength,'denoise':denoise,'seed':seed,'prompt_id':pid,'workflow_api':str(wf),'pose_reference':str(POSE_REFS[pose]),'masked_reference':str(INDIR/f'pose_ref_{pose}_arms_torso_only.png'),'outputs':outputs(h)})
    manifest['contact_sheet']=make_contact(manifest)
    mp=OUTDIR/'manifest_reference_guided_multi_pose.json'
    mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
