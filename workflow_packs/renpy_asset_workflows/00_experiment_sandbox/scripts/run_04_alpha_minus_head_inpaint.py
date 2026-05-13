#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path

COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_04_alpha_minus_head_inpaint_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True)
OUTDIR.mkdir(parents=True, exist_ok=True)

SRC=COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
ALPHA_SRC=COMFY/'output/hermes_vn_toonout_other_character/alpha_silver_bob_v190_rftrue_blur1_nobgcolor_seed719251035_00001_.png'
POSE=COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'
PREV_BEST=COMFY/'output/hermes_vn_04_florence_protected_inpaint_20260513/composite_wide_d95_cn100_seed719254195_00001_.png'

POS=(
    'masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_explicit, '
    '1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, '
    'arms_crossed, crossed_arms, folded_arms, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, '
    'navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, grey_background'
)
NEG=(
    'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, '
    'long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, '
    'signature, watermark, username, conjoined, bad_ai-generated, smile, open_mouth, happy, frown, angry, annoyed, serious, stern, pouting, '
    'sad, crying, tears, scared, disgusted, surprised, arms_at_sides, hands_at_sides, hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, '
    'extra_hands, extra_arms, detached_hands, side_hands, duplicate_hands, large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, '
    'badge, emblem, logo, white_background, bright_background, gradient_background, patterned_background, black_background, dark_background, '
    'vignette, thick_outline, rim_lighting, (worst quality, bad quality:1.2)'
)


def http_json(path: str, payload=None, timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode('utf-8')
        headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path, data=data, headers=headers), timeout=timeout) as r:
        raw=r.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def submit(prompt, timeout_s=1200):
    q=http_json('/queue', timeout=5)
    if q.get('queue_running') or q.get('queue_pending'):
        raise RuntimeError(f'ComfyUI queue is not idle: {q}')
    pid=http_json('/prompt', {'prompt': prompt})['prompt_id']
    start=time.time()
    while time.time()-start < timeout_s:
        h=http_json(f'/history/{pid}', timeout=30)
        if pid in h:
            st=h[pid].get('status', {})
            if not st.get('completed'):
                raise RuntimeError(st)
            return pid, h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def outputs(history):
    arr=[]
    for nid,node in history.get('outputs', {}).items():
        for img in node.get('images', []):
            arr.append({'node': nid, 'path': str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr


def make_alpha_mask():
    dst=INDIR/'alpha_character_mask_from_02.png'
    # Extract RGBA alpha from the 02 transparent PNG, harden it, then write RGB grayscale.
    # This avoids editing the background when we later invert/subtract the head mask.
    vf='alphaextract,format=gray,lut=y=if(gte(val\\,16)\\,255\\,0),format=rgb24'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ALPHA_SRC),'-vf',vf,'-frames:v','1',str(dst)], check=True)
    return f'{RUN}/{dst.name}'


def build_prompt(alpha_mask_rel: str, denoise: float, seed: int, slug: str):
    # edit mask = alpha(character silhouette) - dilated(Florence face|head|hair)
    return {
      '1': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/source01.png'}},
      '2': {'class_type':'LoadImage','inputs':{'image':f'{RUN}/pose_arms_crossed.png'}},
      '3': {'class_type':'LoadImage','inputs':{'image':alpha_mask_rel}},
      '4': {'class_type':'ImageToMask','inputs':{'image':['3',0],'channel':'red'}},
      '5': {'class_type':'DownloadAndLoadFlorence2Model','inputs':{'model':'microsoft/Florence-2-large','precision':'fp16','convert_to_safetensors':False}},
      '6': {'class_type':'Florence2Run','inputs':{'image':['1',0],'florence2_model':['5',0],'text_input':'head','task':'referring_expression_segmentation','fill_mask':True,'keep_model_loaded':True,'max_new_tokens':1024,'num_beams':3,'do_sample':False,'output_mask_select':'','seed':719251777}},
      '7': {'class_type':'Florence2Run','inputs':{'image':['1',0],'florence2_model':['5',0],'text_input':'hair','task':'referring_expression_segmentation','fill_mask':True,'keep_model_loaded':True,'max_new_tokens':1024,'num_beams':3,'do_sample':False,'output_mask_select':'','seed':719251778}},
      '8': {'class_type':'Florence2Run','inputs':{'image':['1',0],'florence2_model':['5',0],'text_input':'face','task':'referring_expression_segmentation','fill_mask':True,'keep_model_loaded':False,'max_new_tokens':1024,'num_beams':3,'do_sample':False,'output_mask_select':'','seed':719251779}},
      '9': {'class_type':'MaskComposite','inputs':{'destination':['6',1],'source':['7',1],'x':0,'y':0,'operation':'or'}},
      '10': {'class_type':'MaskComposite','inputs':{'destination':['9',0],'source':['8',1],'x':0,'y':0,'operation':'or'}},
      '11': {'class_type':'AILab_MaskEnhancer','inputs':{'mask':['10',0],'sensitivity':1.0,'mask_blur':6,'mask_offset':28,'smooth':1.0,'fill_holes':True,'invert_output':False}},
      '12': {'class_type':'MaskComposite','inputs':{'destination':['4',0],'source':['11',0],'x':0,'y':0,'operation':'subtract'}},
      '13': {'class_type':'GrowMask','inputs':{'mask':['12',0],'expand':4,'tapered_corners':True}},
      '14': {'class_type':'ImpactGaussianBlurMask','inputs':{'mask':['13',0],'kernel_size':14,'sigma':7.0}},
      '15': {'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':'novaAnimeXL_ilV190.safetensors'}},
      '16': {'class_type':'CLIPTextEncode','inputs':{'clip':['15',1],'text':POS}},
      '17': {'class_type':'CLIPTextEncode','inputs':{'clip':['15',1],'text':NEG}},
      '18': {'class_type':'DifferentialDiffusion','inputs':{'model':['15',0],'strength':1.0}},
      '19': {'class_type':'InpaintModelConditioning','inputs':{'positive':['16',0],'negative':['17',0],'vae':['15',2],'pixels':['1',0],'mask':['14',0],'noise_mask':True}},
      '20': {'class_type':'OpenposePreprocessor','inputs':{'image':['2',0],'detect_hand':'enable','detect_body':'enable','detect_face':'disable','resolution':1024,'scale_stick_for_xinsr_cn':'enable'}},
      '21': {'class_type':'ControlNetLoader','inputs':{'control_net_name':'xinsir-controlnet-union-sdxl-1.0-promax.safetensors'}},
      '22': {'class_type':'SetUnionControlNetType','inputs':{'control_net':['21',0],'type':'openpose'}},
      '23': {'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['19',0],'negative':['19',1],'control_net':['22',0],'image':['20',0],'strength':1.0,'start_percent':0.0,'end_percent':0.90,'vae':['15',2]}},
      '24': {'class_type':'KSampler','inputs':{'model':['18',0],'positive':['23',0],'negative':['23',1],'latent_image':['19',2],'seed':seed,'steps':28,'cfg':5.0,'sampler_name':'euler_ancestral','scheduler':'karras','denoise':denoise}},
      '25': {'class_type':'VAEDecode','inputs':{'samples':['24',0],'vae':['15',2]}},
      '26': {'class_type':'ImageCompositeMasked','inputs':{'destination':['1',0],'source':['25',0],'x':0,'y':0,'resize_source':False,'mask':['14',0]}},
      '27': {'class_type':'MaskToImage','inputs':{'mask':['11',0]}},
      '28': {'class_type':'MaskToImage','inputs':{'mask':['14',0]}},
      '29': {'class_type':'SaveImage','inputs':{'images':['27',0],'filename_prefix':f'{RUN}/protect_headhairface_{slug}'}},
      '30': {'class_type':'SaveImage','inputs':{'images':['28',0],'filename_prefix':f'{RUN}/edit_alpha_minus_head_{slug}'}},
      '31': {'class_type':'SaveImage','inputs':{'images':['20',0],'filename_prefix':f'{RUN}/openpose_{slug}'}},
      '32': {'class_type':'SaveImage','inputs':{'images':['25',0],'filename_prefix':f'{RUN}/raw_{slug}'}},
      '33': {'class_type':'SaveImage','inputs':{'images':['26',0],'filename_prefix':f'{RUN}/composite_{slug}'}},
    }


def make_contact(manifest):
    # Build an unlabeled contact sheet with ffmpeg because this WSL Python lacks Pillow.
    # Order: source, previous best, then for each variant mask+composite.
    files=[SRC]
    if PREV_BEST.exists():
        files.append(PREV_BEST)
    for v in manifest['variants']:
        comp=[o for o in v['outputs'] if o['node']=='33'][0]['path']
        mask=[o for o in v['outputs'] if o['node']=='30'][0]['path']
        files.extend([Path(mask), Path(comp)])
    dst=OUTDIR/'contact_alpha_minus_head_inpaint.png'
    inputs=[]
    labels=[]
    for idx,p in enumerate(files):
        inputs += ['-i', str(p)]
        labels.append(f'[{idx}:v]scale=384:512:force_original_aspect_ratio=decrease,pad=384:512:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[v{idx}]')
    n=len(files)
    # xstack 2 columns; add a white filler if odd.
    if n % 2:
        labels.append(f'color=white:s=384x512:d=0.1,setsar=1[v{n}]')
        n += 1
    layout=[]
    for i in range(n):
        x='0' if i%2==0 else '384'
        y=str((i//2)*512)
        layout.append(f'{x}_{y}')
    filt=';'.join(labels)+';'+''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout='+'|'.join(layout)+'[out]'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)], check=True)
    return str(dst)


def main():
    for p in [SRC, ALPHA_SRC, POSE]:
        if not p.exists():
            raise FileNotFoundError(p)
    shutil.copy2(SRC, INDIR/'source01.png')
    shutil.copy2(POSE, INDIR/'pose_arms_crossed.png')
    alpha_mask_rel=make_alpha_mask()
    variants=[(0.80,719254280),(0.90,719254290),(0.95,719254295)]
    manifest={
        'run':RUN,
        'source_rgb':str(SRC),
        'source_alpha_for_character_mask':str(ALPHA_SRC),
        'pose':str(POSE),
        'purpose':'Test user idea: use transparent character alpha as silhouette, subtract dilated Florence head/hair/face protection mask, then inpaint the remaining body area for arms_crossed and composite back onto original.',
        'mask_formula':'edit_mask = alpha(character from 02 transparent PNG) - dilated(Florence head OR hair OR face); background excluded by alpha mask.',
        'variants':[]
    }
    for denoise,seed in variants:
        slug=f'd{int(denoise*100):02d}_seed{seed}'
        p=build_prompt(alpha_mask_rel, denoise, seed, slug)
        wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_04_alpha_minus_head_inpaint_{slug}_api.json'
        wf.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding='utf-8')
        pid,h=submit(p)
        manifest['variants'].append({'slug':slug,'denoise':denoise,'seed':seed,'prompt_id':pid,'workflow_api':str(wf),'outputs':outputs(h)})
    manifest['contact_sheet']=make_contact(manifest)
    mp=OUTDIR/'manifest_alpha_minus_head_inpaint.json'
    mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(manifest, indent=2, ensure_ascii=False))

if __name__=='__main__':
    main()
