#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request, shutil
from pathlib import Path
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_expr_retest_20260513'
src=COMFY/'output/hermes_vn_chain_retest_20260513/no_thick_arms_crossed_src_00001_.png'
rel=f'{RUN}/{src.name}'
dst=COMFY/'input'/rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src,dst)
QUALITY='masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest'
CHAR='rating_explicit, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, grey_background'
POS=f'{QUALITY}, {CHAR}, smile, open_mouth, happy, BREAK depth_of_field, volumetric_lighting'
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
        if pid in h: return pid,h[pid]
        time.sleep(2)
    raise TimeoutError(pid)
def outs(h):
    arr=[]
    for nid,node in h.get('outputs',{}).items():
        for img in node.get('images',[]): arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr
template=json.loads((ROOT/'03_expression_variation_face_composite/workflow_api/03_expression_source_canonical_api.json').read_text())
manifest=[]
for denoise in [0.50,0.55,0.65]:
    p=json.loads(json.dumps(template))
    p['1']['inputs']['image']=rel
    p['4']['inputs']['seed']=719251301
    p['6']['inputs']['text']=POS
    p['7']['inputs']['text']=NEG
    p['13']['inputs']['seed']=719251301
    p['13']['inputs']['denoise']=denoise
    prefix=f'{RUN}/04_arms_happy_denoise{str(denoise).replace(".","")}_seed719251301'
    p['15']['inputs']['filename_prefix']=prefix+'_raw_inpaint'
    p['17']['inputs']['filename_prefix']=prefix+'_mask_preview'
    p['19']['inputs']['filename_prefix']=prefix+'_composited'
    pid,h=submit(p)
    manifest.append({'denoise':denoise,'prompt_id':pid,'outputs':outs(h)})
mp=COMFY/'output'/RUN/'manifest_04_happy_denoise_sweep.json'
mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'manifest':str(mp),'items':manifest},indent=2,ensure_ascii=False))
