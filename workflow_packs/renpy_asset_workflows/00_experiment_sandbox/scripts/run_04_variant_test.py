#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request, shutil, sys
from pathlib import Path
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT='http://172.28.224.1:8000'
CHAR_TAGS='short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts'
POSE_TAGS='arms_crossed, crossed_arms, folded_arms'
EXPR_NEG='smile, open_mouth'
POSE_NEG='hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed'

def http_json(path,payload=None,timeout=30):
    data=None; headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
        raw=r.read().decode(); return json.loads(raw) if raw else {}

def submit(prompt,timeout_s=900):
    q=http_json('/queue',timeout=5)
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(f'queue busy {q}')
    pid=http_json('/prompt',{'prompt':prompt})['prompt_id']; start=time.time()
    while time.time()-start<timeout_s:
        h=http_json(f'/history/{pid}',timeout=30)
        if pid in h:
            st=h[pid].get('status',{})
            if not st.get('completed'): raise RuntimeError(f'failed {pid} {st}')
            return pid,h[pid]
        time.sleep(2)
    raise TimeoutError(pid)

def outs(h):
    out=[]
    for node in h.get('outputs',{}).values():
        for img in node.get('images',[]): out.append(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])
    return out

def make_prompt(style_block, slug):
    p=json.loads((ROOT/'04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json').read_text())
    p['4']['inputs']['image']='hermes_identity_silver_bob_anchor_v190.png'
    p['5']['inputs']['image']='hermes_pose_ref_silver_bob_arms_crossed.png'
    p['2']['inputs']['text']='masterpiece, best_quality, very_aesthetic, newest, rating_explicit, 1girl, solo, cowboy_shot, standing, looking_at_viewer, '+CHAR_TAGS+', '+POSE_TAGS+', '+style_block
    p['3']['inputs']['text']=p['3']['inputs']['text'].replace('TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES',EXPR_NEG).replace('TEMPLATE_POSE_CONFLICT_NEGATIVES',POSE_NEG)
    p['14']['inputs']['seed']=719252501
    p['16']['inputs']['filename_prefix']=f'hermes_vn_chain_retest_20260513/{slug}_src'
    p['17']['inputs']['filename_prefix']=f'hermes_vn_chain_retest_20260513/{slug}_control'
    return p

def run_variant(slug, style_block):
    p04=make_prompt(style_block, slug)
    pid04,h04=submit(p04); paths=outs(h04)
    src=[p for p in paths if f'{slug}_src' in str(p)][0]
    ctrl=[p for p in paths if f'{slug}_control' in str(p)][0]
    input_rel=f'hermes_vn_chain_retest_20260513/{slug}_src.png'
    ip=COMFY/'input'/input_rel; ip.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,ip)
    p02=json.loads((ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json').read_text())
    p02['1']['inputs']['image']=input_rel; p02['3']['inputs']['filename_prefix']=f'hermes_vn_chain_retest_20260513/{slug}_alpha_b1_ref1'
    pid02,h02=submit(p02); alpha=[p for p in outs(h02) if f'{slug}_alpha_b1_ref1' in str(p)][0]
    return {'slug':slug,'style_block':style_block,'04_prompt_id':pid04,'02_prompt_id':pid02,'04_source':str(src),'04_control':str(ctrl),'02_alpha':str(alpha),'04_positive':p04['2']['inputs']['text']}

variants=[
    ('candidate_no_thick_outline','clean_lineart, anime_coloring, grey_background'),
]
results=[run_variant(slug, style) for slug,style in variants]
mp=COMFY/'output/hermes_vn_chain_retest_20260513/manifest_candidate_no_thick_outline.json'
mp.write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(results,indent=2,ensure_ascii=False))
