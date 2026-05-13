#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path

COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_florence_protected_inpaint_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)

SRC=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
POSE=COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'

POS=('masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_explicit, '
     '1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, '
     'arms_crossed, crossed_arms, folded_arms, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, '
     'navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, thick_outline, grey_background')
NEG=('modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, '
     'long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, '
     'signature, watermark, username, conjoined, bad_ai-generated, smile, open_mouth, happy, frown, angry, annoyed, serious, stern, pouting, '
     'sad, crying, tears, scared, disgusted, surprised, arms_at_sides, hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, '
     'large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, white_background, bright_background, gradient_background, '
     'patterned_background, black_background, dark_background, vignette, (worst quality, bad quality:1.2)')


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

def make_mask(name, draw):
    dst=INDIR/name
    cmd=['ffmpeg','-y','-f','lavfi','-i','color=black:s=1152x1536', '-vf', draw, '-frames:v','1', str(dst)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f'{RUN}/{name}'

def build_prompt(mask_rel, denoise, seed, slug):
    return {
      '1': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/source01.png'}},
      '2': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/pose_arms_crossed.png'}},
      '3': {'class_type':'LoadImage','inputs':{'image':mask_rel}},
      '4': {'class_type':'ImageToMask','inputs':{'image':['3',0],'channel':'red'}},
      '5': {'class_type':'DownloadAndLoadFlorence2Model','inputs':{'model':'microsoft/Florence-2-large','precision':'fp16','convert_to_safetensors':False}},
      '6': {'class_type':'Florence2Run','inputs':{'image':['1',0],'florence2_model':['5',0],'text_input':'head','task':'referring_expression_segmentation','fill_mask':True,'keep_model_loaded':False,'max_new_tokens':1024,'num_beams':3,'do_sample':False,'output_mask_select':'','seed':719251777}},
      '7': {'class_type':'AILab_MaskEnhancer','inputs':{'mask':['6',1],'sensitivity':1.0,'mask_blur':4,'mask_offset':20,'smooth':1.0,'fill_holes':True,'invert_output':False}},
      '8': {'class_type':'MaskComposite','inputs':{'destination':['4',0],'source':['7',0],'x':0,'y':0,'operation':'subtract'}},
      '9': {'class_type':'GrowMask','inputs':{'mask':['8',0],'expand':8,'tapered_corners':True}},
      '10': {'class_type':'ImpactGaussianBlurMask','inputs':{'mask':['9',0],'kernel_size':16,'sigma':8.0}},
      '11': {'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'novaAnimeXL_ilV190.safetensors'}},
      '12': {'class_type':'CLIPTextEncode','inputs':{'clip':['11',1],'text':POS}},
      '13': {'class_type':'CLIPTextEncode','inputs':{'clip':['11',1],'text':NEG}},
      '14': {'class_type':'DifferentialDiffusion','inputs':{'model':['11',0],'strength':1.0}},
      '15': {'class_type':'InpaintModelConditioning','inputs':{'positive':['12',0],'negative':['13',0],'vae':['11',2],'pixels':['1',0],'mask':['10',0],'noise_mask':True}},
      '16': {'class_type':'OpenposePreprocessor','inputs':{'image':['2',0],'detect_hand':'enable','detect_body':'enable','detect_face':'disable','resolution':1024,'scale_stick_for_xinsr_cn':'enable'}},
      '17': {'class_type':'ControlNetLoader','inputs':{'control_net_name':'xinsir-controlnet-union-sdxl-1.0-promax.safetensors'}},
      '18': {'class_type':'SetUnionControlNetType','inputs':{'control_net':['17',0],'type':'openpose'}},
      '19': {'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['15',0],'negative':['15',1],'control_net':['18',0],'image':['16',0],'strength':0.75,'start_percent':0.0,'end_percent':0.85,'vae':['11',2]}},
      '20': {'class_type':'KSampler','inputs':{'model':['14',0],'positive':['19',0],'negative':['19',1],'latent_image':['15',2],'seed':seed,'steps':28,'cfg':5.0,'sampler_name':'euler_ancestral','scheduler':'karras','denoise':denoise}},
      '21': {'class_type':'VAEDecode','inputs':{'samples':['20',0],'vae':['11',2]}},
      '22': {'class_type':'ImageCompositeMasked','inputs':{'destination':['1',0],'source':['21',0],'x':0,'y':0,'resize_source':False,'mask':['10',0]}},
      '23': {'class_type':'MaskToImage','inputs':{'mask':['10',0]}},
      '24': {'class_type':'SaveImage','inputs':{'images':['23',0],'filename_prefix':f'{RUN}/mask_{slug}'}},
      '25': {'class_type':'SaveImage','inputs':{'images':['16',0],'filename_prefix':f'{RUN}/openpose_{slug}'}},
      '26': {'class_type':'SaveImage','inputs':{'images':['21',0],'filename_prefix':f'{RUN}/raw_{slug}'}},
      '27': {'class_type':'SaveImage','inputs':{'images':['22',0],'filename_prefix':f'{RUN}/composite_{slug}'}},
    }

def main():
    shutil.copy2(SRC, INDIR/'source01.png')
    shutil.copy2(POSE, INDIR/'pose_arms_crossed.png')
    masks={
      'medium': make_mask('mask_arm_pose_medium.png', "drawbox=x=210:y=500:w=730:h=520:color=white:t=fill,drawbox=x=135:y=560:w=230:h=560:color=white:t=fill,drawbox=x=790:y=560:w=230:h=560:color=white:t=fill"),
      'wide': make_mask('mask_arm_pose_wide.png', "drawbox=x=155:y=455:w=850:h=700:color=white:t=fill"),
    }
    variants=[('medium',0.55,719254055),('medium',0.70,719254070),('wide',0.60,719254160)]
    manifest={'run':RUN,'source':str(SRC),'pose':str(POSE),'purpose':'Florence-2 head-protected original-preserving arms-crossed inpaint. Manual arm/torso mask minus Florence head mask; OpenPose guides pose; final output composited back onto original outside mask.','variants':[]}
    for mask_name,denoise,seed in variants:
        slug=f'{mask_name}_d{int(denoise*100):02d}_seed{seed}'
        p=build_prompt(masks[mask_name],denoise,seed,slug)
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_04_florence_protected_inpaint_{slug}_api.json'
        wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
        pid,h=submit(p)
        manifest['variants'].append({'slug':slug,'mask':mask_name,'denoise':denoise,'seed':seed,'prompt_id':pid,'workflow_api':str(wf),'outputs':outputs(h)})
    mp=OUTDIR/'manifest_florence_protected_inpaint.json'; mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
