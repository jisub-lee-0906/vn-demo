#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, time, urllib.request
from pathlib import Path

ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY = Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT = 'http://172.28.224.1:8000'
RUN = 'hermes_vn_04_quality_style_sweep_20260513'
OUTDIR = COMFY / 'output' / RUN
INDIR = COMFY / 'input' / RUN
OUTDIR.mkdir(parents=True, exist_ok=True)
INDIR.mkdir(parents=True, exist_ok=True)

SOURCE01 = COMFY/'output/hermes_vn_full_chain_retest_20260513_current/01_source_silver_bob_seed719251035_00001_.png'
POSE_REF = COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'
CHAR_TAGS = 'short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts'
POSE_EXPR = 'arms_crossed, crossed_arms, folded_arms, smile, happy, open_mouth, cheerful'
NEG_EXPR = 'frown, angry, annoyed, serious, stern, pouting, sad, crying, tears, scared, disgusted, surprised'
NEG_POSE = 'hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed'
BASE_QUALITY = 'masterpiece, best_quality, very_aesthetic, newest, rating_explicit'
QUALITY_01_STYLE = 'masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest, rating_explicit'
CHAR_POSE = f'1girl, solo, cowboy_shot, standing, looking_at_viewer, {CHAR_TAGS}, {POSE_EXPR}'


def http_json(path: str, payload=None, timeout=30):
    data = None; headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8'); headers['Content-Type'] = 'application/json'
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
            st = h[pid].get('status', {})
            if not st.get('completed'):
                raise RuntimeError(f'failed {pid}: {st}')
            return pid, h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def outputs(hist: dict):
    arr=[]
    for nid,node in hist.get('outputs',{}).items():
        for img in node.get('images',[]):
            arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr


def first(hist: dict, nid: str):
    for item in outputs(hist):
        if item['node'] == nid:
            return item['path']
    raise RuntimeError(outputs(hist))


def copy_to_input(src: Path, name: str) -> str:
    dst = INDIR/name
    shutil.copy2(src, dst)
    return f'{RUN}/{name}'

source_rel = copy_to_input(SOURCE01, '01_source_silver_bob.png')
pose_rel = copy_to_input(POSE_REF, 'pose_ref_arms_crossed.png')
base = json.loads((ROOT/'04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json').read_text(encoding='utf-8'))

variants = [
    {
        'slug': 'baseline_openmouth_ip065',
        'positive': f'{BASE_QUALITY}, {CHAR_POSE}, clean_lineart, anime_coloring, grey_background',
        'ip_weight': 0.65,
        'seed': 719252501,
    },
    {
        'slug': 'q01_crisp_ip065',
        'positive': f'{QUALITY_01_STYLE}, {CHAR_POSE}, clean_lineart, crisp_lineart, clean_outline, anime_coloring, detailed_anime_coloring, grey_background',
        'ip_weight': 0.65,
        'seed': 719252501,
    },
    {
        'slug': 'q01_crisp_ip075',
        'positive': f'{QUALITY_01_STYLE}, {CHAR_POSE}, clean_lineart, crisp_lineart, clean_outline, anime_coloring, detailed_anime_coloring, grey_background',
        'ip_weight': 0.75,
        'seed': 719252501,
    },
    {
        'slug': 'q01_crisp_ip085',
        'positive': f'{QUALITY_01_STYLE}, {CHAR_POSE}, clean_lineart, crisp_lineart, clean_outline, anime_coloring, detailed_anime_coloring, grey_background',
        'ip_weight': 0.85,
        'seed': 719252501,
    },
]

manifest = {
    'run': RUN,
    'endpoint': ENDPOINT,
    'source01': str(SOURCE01),
    'pose_reference': str(POSE_REF),
    'purpose': '04 direct happy open-mouth quality/style sweep: test if 01-like quality tags and higher IPAdapter weight reduce color/detail drift without reintroducing thick_outline rim.',
    'variants': []
}

for v in variants:
    p = json.loads(json.dumps(base))
    p['4']['inputs']['image'] = source_rel
    p['5']['inputs']['image'] = pose_rel
    p['2']['inputs']['text'] = v['positive']
    p['3']['inputs']['text'] = p['3']['inputs']['text'].replace('TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES', NEG_EXPR).replace('TEMPLATE_POSE_CONFLICT_NEGATIVES', NEG_POSE)
    p['12']['inputs']['weight'] = v['ip_weight']
    p['14']['inputs']['seed'] = v['seed']
    p['16']['inputs']['filename_prefix'] = f'{RUN}/04_{v["slug"]}_seed{v["seed"]}'
    p['17']['inputs']['filename_prefix'] = f'{RUN}/control_{v["slug"]}_seed{v["seed"]}'
    pid, hist = submit(p)
    manifest['variants'].append({
        'slug': v['slug'],
        'seed': v['seed'],
        'ip_weight': v['ip_weight'],
        'prompt_id': pid,
        'source_output': first(hist, '16'),
        'control_output': first(hist, '17'),
        'positive': p['2']['inputs']['text'],
        'negative': p['3']['inputs']['text'],
    })

mp = OUTDIR/'manifest_04_quality_style_sweep.json'
mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(manifest, indent=2, ensure_ascii=False))
