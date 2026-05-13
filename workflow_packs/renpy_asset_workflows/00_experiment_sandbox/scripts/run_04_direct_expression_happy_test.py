#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, time, urllib.request
from pathlib import Path

ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY = Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT = 'http://172.28.224.1:8000'
RUN = 'hermes_vn_04_direct_expression_test_20260513'
OUTDIR = COMFY / 'output' / RUN
INDIR = COMFY / 'input' / RUN
OUTDIR.mkdir(parents=True, exist_ok=True)
INDIR.mkdir(parents=True, exist_ok=True)

CHAR_TAGS = 'short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts'
POSE_BASE = 'arms_crossed, crossed_arms, folded_arms'
POSE_REF = COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'
if not POSE_REF.exists():
    POSE_REF = COMFY/'input/hermes_vn_full_chain_01_04_03_02/pose_ref_arms_crossed.png'
SOURCE01 = COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
if not SOURCE01.exists():
    SOURCE01 = COMFY/'output/hermes_vn_chain_retest_20260513/01_no_depth_volumetric_source_00001_.png'


def http_json(path: str, payload=None, timeout=30):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT + path, data=data, headers=headers), timeout=timeout) as r:
        raw = r.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def submit(prompt: dict, timeout_s=1200):
    q = http_json('/queue', timeout=5)
    if q.get('queue_running') or q.get('queue_pending'):
        raise RuntimeError(f'queue busy: {q}')
    pid = http_json('/prompt', {'prompt': prompt}, timeout=30)['prompt_id']
    start = time.time()
    while time.time() - start < timeout_s:
        h = http_json(f'/history/{pid}', timeout=30)
        if pid in h:
            status = h[pid].get('status', {})
            if not status.get('completed'):
                raise RuntimeError(f'failed {pid}: {status}')
            return pid, h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def outputs(hist: dict):
    arr = []
    for node_id, node in hist.get('outputs', {}).items():
        for img in node.get('images', []):
            arr.append({'node': node_id, 'path': str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr


def first(hist: dict, node_id: str) -> str:
    for item in outputs(hist):
        if item['node'] == node_id:
            return item['path']
    raise RuntimeError(f'no output for node {node_id}: {outputs(hist)}')


def copy_to_input(src: Path, name: str) -> str:
    dst = INDIR / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f'{RUN}/{name}'

source_rel = copy_to_input(SOURCE01, '01_source_silver_bob.png')
pose_ref_rel = copy_to_input(POSE_REF, 'pose_ref_arms_crossed.png')
base = json.loads((ROOT/'04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json').read_text(encoding='utf-8'))

variants = [
    {
        'slug': 'happy_smile_no_openmouth',
        'pose_tags': f'{POSE_BASE}, smile, happy, gentle_smile, soft_smile',
        'negative_expr': 'frown, angry, annoyed, serious, stern, pouting, sad, crying, tears, scared, disgusted, surprised, open_mouth',
        'seed': 719252501,
    },
    {
        'slug': 'happy_openmouth',
        'pose_tags': f'{POSE_BASE}, smile, happy, open_mouth, cheerful',
        'negative_expr': 'frown, angry, annoyed, serious, stern, pouting, sad, crying, tears, scared, disgusted, surprised',
        'seed': 719252501,
    },
    {
        'slug': 'happy_smile_altseed',
        'pose_tags': f'{POSE_BASE}, smile, happy, gentle_smile, soft_smile',
        'negative_expr': 'frown, angry, annoyed, serious, stern, pouting, sad, crying, tears, scared, disgusted, surprised, open_mouth',
        'seed': 719252777,
    },
]

manifest = {
    'run': RUN,
    'endpoint': ENDPOINT,
    'source01': str(SOURCE01),
    'pose_reference': str(POSE_REF),
    'note': '04 direct expression test: arms_crossed plus happy expression in 04; removed smile/open_mouth from pose conflict negative and replaced with stern/frown negatives.',
    'variants': [],
}

for v in variants:
    p = json.loads(json.dumps(base))
    p['4']['inputs']['image'] = source_rel
    p['5']['inputs']['image'] = pose_ref_rel
    p['2']['inputs']['text'] = p['2']['inputs']['text'].replace('TEMPLATE_CHARACTER_TAGS', CHAR_TAGS).replace('TEMPLATE_POSE_TAGS', v['pose_tags'])
    p['3']['inputs']['text'] = p['3']['inputs']['text'].replace('TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES', v['negative_expr']).replace('TEMPLATE_POSE_CONFLICT_NEGATIVES', 'hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed')
    p['14']['inputs']['seed'] = v['seed']
    p['16']['inputs']['filename_prefix'] = f'{RUN}/04_direct_{v["slug"]}_seed{v["seed"]}'
    p['17']['inputs']['filename_prefix'] = f'{RUN}/04_control_{v["slug"]}_seed{v["seed"]}'
    pid, hist = submit(p)
    manifest['variants'].append({
        'slug': v['slug'],
        'seed': v['seed'],
        'prompt_id': pid,
        'source_output': first(hist, '16'),
        'control_output': first(hist, '17'),
        'positive': p['2']['inputs']['text'],
        'negative': p['3']['inputs']['text'],
    })

mp = OUTDIR/'manifest_04_direct_expression_happy_test.json'
mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(manifest, indent=2, ensure_ascii=False))
