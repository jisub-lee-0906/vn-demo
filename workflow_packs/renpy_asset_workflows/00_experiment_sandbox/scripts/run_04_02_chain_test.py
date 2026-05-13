#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request, shutil
from pathlib import Path

ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY = Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT = 'http://172.28.224.1:8000'

CHAR_TAGS = 'short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts'
POSE_TAGS = 'arms_crossed, crossed_arms, folded_arms'
EXPR_NEG = 'smile, open_mouth'
POSE_NEG = 'hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed'

def http_json(path, payload=None, timeout=30):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(ENDPOINT.rstrip('/') + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode('utf-8')
        return json.loads(raw) if raw else {}

def queue_clear():
    q=http_json('/queue', timeout=5)
    return not (q.get('queue_running') or q.get('queue_pending')), q

def submit_and_wait(prompt, timeout_s=900):
    clear,q = queue_clear()
    if not clear:
        raise RuntimeError(f'ComfyUI queue busy: {q}')
    resp=http_json('/prompt', {'prompt': prompt}, timeout=30)
    pid=resp.get('prompt_id')
    if not pid:
        raise RuntimeError(f'no prompt_id: {resp}')
    start=time.time()
    while time.time()-start < timeout_s:
        hist=http_json(f'/history/{pid}', timeout=30)
        if pid in hist:
            status=hist[pid].get('status',{})
            if not status.get('completed'):
                raise RuntimeError(f'prompt {pid} failed: {status}')
            return pid, hist[pid]
        time.sleep(2)
    raise TimeoutError(pid)

def output_paths(history):
    paths=[]
    for node in history.get('outputs',{}).values():
        for img in node.get('images',[]):
            sub=img.get('subfolder') or ''
            paths.append(COMFY/'output'/sub/img['filename'])
    return paths

p04=json.loads((ROOT/'04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json').read_text())
p04['4']['inputs']['image']='hermes_identity_silver_bob_anchor_v190.png'
p04['5']['inputs']['image']='hermes_pose_ref_silver_bob_arms_crossed.png'
p04['2']['inputs']['text']=p04['2']['inputs']['text'].replace('TEMPLATE_CHARACTER_TAGS',CHAR_TAGS).replace('TEMPLATE_POSE_TAGS',POSE_TAGS)
p04['3']['inputs']['text']=p04['3']['inputs']['text'].replace('TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES',EXPR_NEG).replace('TEMPLATE_POSE_CONFLICT_NEGATIVES',POSE_NEG)
p04['14']['inputs']['seed']=719252501
p04['16']['inputs']['filename_prefix']='hermes_vn_chain_retest_20260513/current04_silver_arms_crossed_src'
p04['17']['inputs']['filename_prefix']='hermes_vn_chain_retest_20260513/current04_silver_arms_crossed_control'

pid04,h04=submit_and_wait(p04)
outs04=output_paths(h04)
src04=[p for p in outs04 if 'current04_silver_arms_crossed_src' in str(p)][0]
ctrl04=[p for p in outs04 if 'current04_silver_arms_crossed_control' in str(p)][0]
input_rel='hermes_vn_chain_retest_20260513/current04_silver_arms_crossed_src.png'
input_path=COMFY/'input'/input_rel
input_path.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src04,input_path)

p02=json.loads((ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json').read_text())
p02['1']['inputs']['image']=input_rel
p02['3']['inputs']['filename_prefix']='hermes_vn_chain_retest_20260513/current04_silver_arms_crossed_alpha_b1_ref1'
pid02,h02=submit_and_wait(p02)
outs02=output_paths(h02)
alpha02=[p for p in outs02 if 'current04_silver_arms_crossed_alpha_b1_ref1' in str(p)][0]
manifest={
    'endpoint': ENDPOINT,
    '04_prompt_id': pid04,
    '02_prompt_id': pid02,
    '04_source': str(src04),
    '04_control': str(ctrl04),
    '02_alpha': str(alpha02),
    '04_positive': p04['2']['inputs']['text'],
    '04_negative': p04['3']['inputs']['text'],
    'seed': 719252501,
}
manifest_path=COMFY/'output/hermes_vn_chain_retest_20260513/manifest_current04_to_02.json'
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest,indent=2,ensure_ascii=False))
