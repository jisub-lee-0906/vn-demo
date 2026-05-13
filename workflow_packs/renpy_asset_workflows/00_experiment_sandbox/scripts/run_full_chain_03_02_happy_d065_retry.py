#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, time, urllib.request
from pathlib import Path
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_full_chain_retest_20260513_current'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
QUALITY='masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest'
CHAR_03='rating_explicit, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, grey_background'
NEG='modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, dynamic_pose, hands_on_hips, hands_in_pockets, hands_near_face, large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, white_background, bright_background, gradient_background, patterned_background, black_background, dark_background, vignette, changed_clothes, different_clothes, different_hair, (worst quality, bad quality:1.2), sad, angry, crying, tears, surprised, disgusted, fearful'

def http_json(path,payload=None,timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
        raw=r.read().decode(); return json.loads(raw) if raw else {}
def submit(p):
    q=http_json('/queue',timeout=5)
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(q)
    pid=http_json('/prompt',{'prompt':p})['prompt_id']
    st=time.time()
    while time.time()-st<900:
        h=http_json('/history/'+pid,timeout=30)
        if pid in h:
            status=h[pid].get('status',{})
            if not status.get('completed'): raise RuntimeError(status)
            return pid,h[pid]
        time.sleep(2)
    raise TimeoutError(pid)
def first(h,nid):
    for node_id,node in h.get('outputs',{}).items():
        for img in node.get('images',[]):
            if node_id==nid: return COMFY/'output'/(img.get('subfolder') or '')/img['filename']
    raise RuntimeError(h.get('outputs'))
# source already copied by previous full-chain script
source_rel=f'{RUN}/04_pose_silver_bob_arms_crossed_seed719252501.png'
p03=json.loads((ROOT/'03_expression_variation_face_composite/workflow_api/03_expression_source_canonical_api.json').read_text())
p03['1']['inputs']['image']=source_rel
p03['4']['inputs']['seed']=719251301
p03['6']['inputs']['text']=f'{QUALITY}, {CHAR_03}, smile, open_mouth, happy, BREAK depth_of_field, volumetric_lighting'
p03['7']['inputs']['text']=NEG
p03['13']['inputs']['seed']=719251301
p03['13']['inputs']['denoise']=0.65
p03['15']['inputs']['filename_prefix']=f'{RUN}/03_happy_d065_raw_inpaint'
p03['17']['inputs']['filename_prefix']=f'{RUN}/03_happy_d065_mask_preview'
p03['19']['inputs']['filename_prefix']=f'{RUN}/03_happy_d065_composited'
pid03,h03=submit(p03)
source03=first(h03,'19')
rel=f'{RUN}/03_happy_d065_composited.png'
shutil.copy2(source03, COMFY/'input'/rel)
p02=json.loads((ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json').read_text())
p02['1']['inputs']['image']=rel
p02['3']['inputs']['filename_prefix']=f'{RUN}/02_alpha_after_03_happy_d065_b1_ref1'
pid02,h02=submit(p02)
alpha=first(h02,'3')
res={'03_prompt_id':pid03,'03_output':str(source03),'02_prompt_id':pid02,'02_alpha':str(alpha),'denoise':0.65}
(OUTDIR/'manifest_happy_d065_retry.json').write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(res,indent=2,ensure_ascii=False))
