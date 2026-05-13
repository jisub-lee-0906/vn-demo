#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, time, urllib.request
from pathlib import Path

ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY = Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT = 'http://172.28.224.1:8000'
RUN = 'hermes_vn_full_chain_retest_20260513_current'
OUTDIR = COMFY/'output'/RUN
INDIR = COMFY/'input'/RUN
OUTDIR.mkdir(parents=True, exist_ok=True)
INDIR.mkdir(parents=True, exist_ok=True)

CHAR_TAGS = 'short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts'
POSE_TAGS = 'arms_crossed, crossed_arms'
POSE_REF = COMFY/'input/hermes_pose_ref_multi04b_silver_bob_arms_crossed.png'
if not POSE_REF.exists():
    POSE_REF = COMFY/'input/hermes_vn_full_chain_01_04_03_02/pose_ref_arms_crossed.png'

QUALITY = 'masterpiece, best quality, amazing quality, 4k, very aesthetic, high_resolution, ultra-detailed, absurdres, newest'
CHAR_03 = 'rating_explicit, 1girl, solo, cowboy_shot, standing, front_view, looking_at_viewer, short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts, grey_background'
COMMON_NEG_03 = 'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, dynamic_pose, hands_on_hips, hands_in_pockets, hands_near_face, large_breasts, huge_breasts, cleavage, nsfw, nude, nipples, badge, emblem, logo, white_background, bright_background, gradient_background, patterned_background, black_background, dark_background, vignette, changed_clothes, different_clothes, different_hair, (worst quality, bad quality:1.2)'


def http_json(path: str, payload=None, timeout=30):
    data = None; headers = {}
    if payload is not None:
        data = json.dumps(payload).encode(); headers['Content-Type'] = 'application/json'
    with urllib.request.urlopen(urllib.request.Request(ENDPOINT + path, data=data, headers=headers), timeout=timeout) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw else {}


def submit(prompt: dict, timeout_s=1200):
    q = http_json('/queue', timeout=5)
    if q.get('queue_running') or q.get('queue_pending'):
        raise RuntimeError(f'queue busy: {q}')
    pid = http_json('/prompt', {'prompt': prompt})['prompt_id']
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


def outs(hist: dict):
    arr = []
    for node_id, node in hist.get('outputs', {}).items():
        for img in node.get('images', []):
            arr.append({'node': node_id, 'path': str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
    return arr


def first_output(hist: dict, node_id: str|None=None, contains: str|None=None) -> Path:
    candidates = outs(hist)
    for item in candidates:
        if node_id is not None and item['node'] != node_id:
            continue
        if contains is not None and contains not in item['path']:
            continue
        return Path(item['path'])
    raise RuntimeError(f'no matching output node={node_id} contains={contains}: {candidates}')


def copy_to_input(src: Path, name: str) -> str:
    dst = INDIR/name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f'{RUN}/{name}'

manifest = {'run': RUN, 'endpoint': ENDPOINT, 'steps': {}}

# 01 current canonical
p01 = json.loads((ROOT/'01_character_anchor_and_prompt/workflow_api/01_character_anchor_apose_neutral_api.json').read_text(encoding='utf-8'))
p01['8']['inputs']['filename_prefix'] = f'{RUN}/01_source_silver_bob_seed719251035'
pid01, h01 = submit(p01)
source01 = first_output(h01, node_id='8')
manifest['steps']['01'] = {'prompt_id': pid01, 'output': str(source01), 'positive': p01['3']['inputs']['text'], 'negative': p01['4']['inputs']['text']}
source01_rel = copy_to_input(source01, '01_source_silver_bob_seed719251035.png')
pose_ref_rel = copy_to_input(POSE_REF, 'pose_ref_arms_crossed.png')

# 04 current canonical with no-thick character tags
p04 = json.loads((ROOT/'04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json').read_text(encoding='utf-8'))
p04['4']['inputs']['image'] = source01_rel
p04['5']['inputs']['image'] = pose_ref_rel
p04['2']['inputs']['text'] = p04['2']['inputs']['text'].replace('TEMPLATE_CHARACTER_TAGS', CHAR_TAGS).replace('TEMPLATE_POSE_TAGS', POSE_TAGS)
p04['3']['inputs']['text'] = p04['3']['inputs']['text'].replace('TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES', 'smile, open_mouth, happy, surprised, crying, tears').replace('TEMPLATE_POSE_CONFLICT_NEGATIVES', 'hands_on_hips, hands_in_pockets, hands_near_face')
p04['14']['inputs']['seed'] = 719252501
p04['16']['inputs']['filename_prefix'] = f'{RUN}/04_pose_silver_bob_arms_crossed_seed719252501'
p04['17']['inputs']['filename_prefix'] = f'{RUN}/04_control_silver_bob_arms_crossed_seed719252501'
pid04, h04 = submit(p04)
source04 = first_output(h04, node_id='16')
control04 = first_output(h04, node_id='17')
manifest['steps']['04'] = {'prompt_id': pid04, 'source_output': str(source04), 'control_output': str(control04), 'positive': p04['2']['inputs']['text'], 'negative': p04['3']['inputs']['text']}
source04_rel = copy_to_input(source04, '04_pose_silver_bob_arms_crossed_seed719252501.png')

# 03 current face-composite route, post-04 happy candidate denoise 0.55
p03 = json.loads((ROOT/'03_expression_variation_face_composite/workflow_api/03_expression_source_canonical_api.json').read_text(encoding='utf-8'))
p03['1']['inputs']['image'] = source04_rel
p03['4']['inputs']['seed'] = 719251301
p03['6']['inputs']['text'] = f'{QUALITY}, {CHAR_03}, smile, open_mouth, happy, BREAK depth_of_field, volumetric_lighting'
p03['7']['inputs']['text'] = f'{COMMON_NEG_03}, sad, angry, crying, tears, surprised, disgusted, fearful'
p03['13']['inputs']['seed'] = 719251301
p03['13']['inputs']['denoise'] = 0.55
p03['15']['inputs']['filename_prefix'] = f'{RUN}/03_happy_d055_raw_inpaint'
p03['17']['inputs']['filename_prefix'] = f'{RUN}/03_happy_d055_mask_preview'
p03['19']['inputs']['filename_prefix'] = f'{RUN}/03_happy_d055_composited'
pid03, h03 = submit(p03)
source03 = first_output(h03, node_id='19')
mask03 = first_output(h03, node_id='17')
raw03 = first_output(h03, node_id='15')
manifest['steps']['03'] = {'prompt_id': pid03, 'composited_output': str(source03), 'mask_output': str(mask03), 'raw_output': str(raw03), 'denoise': 0.55, 'positive': p03['6']['inputs']['text'], 'negative': p03['7']['inputs']['text']}
source03_rel = copy_to_input(source03, '03_happy_d055_composited.png')

# 02 alpha current canonical
p02 = json.loads((ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json').read_text(encoding='utf-8'))
p02['1']['inputs']['image'] = source03_rel
p02['3']['inputs']['filename_prefix'] = f'{RUN}/02_alpha_after_03_happy_d055_b1_ref1'
pid02, h02 = submit(p02)
alpha02 = first_output(h02, node_id='3')
manifest['steps']['02'] = {'prompt_id': pid02, 'alpha_output': str(alpha02)}

mp = OUTDIR/'manifest_full_chain_current.json'
mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(manifest, indent=2, ensure_ascii=False))
