#!/usr/bin/env python3
import copy
import json
import shutil
import time
import uuid
import urllib.request
import urllib.error
from pathlib import Path

BASE = 'http://172.28.224.1:8001'
ROOT = Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
OUT_ROOT = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')
IN_ROOT = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input')
RUN = time.strftime('hermes_vn_final_smoke_%Y%m%d_%H%M%S')
INPUT_SUB = f'hermes_vn_runtime/{RUN}'
INPUT_DIR = IN_ROOT / INPUT_SUB
INPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT = Path('/home/jisub-lee/workspace/vn-demo/.analysis/final_asset_workflow_smoke_report.json')
CLIENT_ID = 'hermes-final-smoke-' + uuid.uuid4().hex

PROMPTS = {
    'anchor_pos': 'masterpiece, best quality, absurdres, 1girl, solo, visual novel sprite, full body, standing, looking_at_viewer, expressionless, closed_mouth, long_hair, black_hair, blue_eyes, school_uniform, white_shirt, red_ribbon, pleated_skirt, grey_background, simple_background',
    'anchor_neg': 'lowres, worst quality, bad anatomy, bad hands, extra fingers, missing fingers, extra limbs, multiple_girls, text, logo, watermark, signature, blurry, cropped, out of frame',
    'expression_pos': 'masterpiece, best quality, same character, happy, smile, open_mouth, sparkling_eyes, blush, looking_at_viewer',
    'expression_neg': 'sad, angry, crying, scared, expressionless, closed_eyes, bad anatomy, bad hands, text, logo, watermark, signature',
    'background_pos': 'masterpiece, best quality, visual novel background, scenery, no_humans, classroom, desks, window, sunlight, depth_of_field, day, wide_shot, clean composition, 16:9',
    'background_neg': 'people, person, character, 1girl, multiple_girls, text, logo, watermark, signature, lowres, blurry, bad perspective',
    'prop_pos': 'masterpiece, best quality, still_life, object_focus, close-up, brass_key, wooden_table, depth_of_field, dramatic shadow, visual novel cut-in, 16:9',
    'prop_neg': 'person, hand, fingers, text, logo, watermark, signature, label, caption, speech_bubble, lowres, blurry',
    'outfit_pos': 'masterpiece, best quality, same character, fully_clothed, school_uniform, white_shirt, red_ribbon, navy_blazer, pleated_skirt, long_sleeves, loafers, looking_at_viewer',
    'outfit_neg': 'nude, naked, underwear, swimsuit, bad anatomy, bad hands, extra fingers, missing fingers, text, logo, watermark, signature, cropped face, deformed face',
    'event_pos': 'masterpiece, best quality, visual novel event cg, 1girl, solo, same character, preserving original face and hairstyle, preserving original outfit, sitting, hand_on_own_chest, classroom, window, sunset, warm light, gentle smile, upper_body, 16:9',
    'event_neg': 'different character, different outfit, nude, naked, bad anatomy, bad hands, extra fingers, missing fingers, text, logo, watermark, signature, blurry, lowres',
}

WORKFLOWS = {
    'character_anchor_base': ROOT/'character_anchor_base/character_anchor_base_workflow_api.json',
    'expression_variations': ROOT/'expression_variations/expression_variations_workflow_api.json',
    'transparency_alpha': ROOT/'transparency_alpha/transparency_alpha_workflow_api.json',
    'background_art': ROOT/'background_art/background_art_workflow_api.json',
    'prop_closeup_cg': ROOT/'prop_closeup_cg/prop_closeup_cg_workflow_api.json',
    'outfit_variations': ROOT/'outfit_variations/outfit_variations_workflow_api.json',
    'event_cg': ROOT/'event_cg/event_cg_workflow_api.json',
}

def get(path, timeout=30):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def post_prompt(prompt):
    payload = json.dumps({'prompt': prompt, 'client_id': CLIENT_ID}).encode('utf-8')
    req = urllib.request.Request(BASE + '/prompt', data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        raise RuntimeError(f'HTTP {e.code}: {body}')

def wait_history(prompt_id, timeout=900):
    start = time.time()
    while time.time() - start < timeout:
        h = get('/history/' + prompt_id, timeout=30)
        if prompt_id in h:
            return h[prompt_id]
        time.sleep(2)
    raise TimeoutError(prompt_id)

def output_paths(history):
    paths=[]
    for node_id, data in history.get('outputs', {}).items():
        for im in data.get('images', []):
            filename=im.get('filename')
            sub=im.get('subfolder') or ''
            typ=im.get('type') or 'output'
            base = OUT_ROOT if typ == 'output' else OUT_ROOT
            p = base / sub / filename
            paths.append({'node': node_id, 'filename': filename, 'subfolder': sub, 'type': typ, 'wsl_path': str(p), 'exists': p.exists(), 'size': p.stat().st_size if p.exists() else None})
    return paths

def set_path(prompt, path, value):
    node, _, rest = path.partition('.')
    cur = prompt[node]
    parts = rest.split('.')
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value

def load(name):
    return json.loads(WORKFLOWS[name].read_text())

def unresolved(prompt):
    text=json.dumps(prompt, ensure_ascii=False)
    bad=[]
    for marker in ['TEMPLATE_', '{헤어', '{감정', '{상극', '{배경', '{시간', '{아이템', '{캐릭터', '{의상']:
        if marker in text:
            bad.append(marker)
    return bad

def submit(name, prompt):
    bad = unresolved(prompt)
    if bad:
        raise RuntimeError(f'unresolved placeholders in {name}: {bad}')
    res = post_prompt(prompt)
    pid = res['prompt_id']
    hist = wait_history(pid)
    paths = output_paths(hist)
    return {'workflow': name, 'prompt_id': pid, 'outputs': paths, 'status': hist.get('status', {})}

def first_existing(outputs):
    for o in outputs:
        if o['exists'] and o['filename'] and o['filename'].lower().endswith('.png'):
            return Path(o['wsl_path'])
    return None

def copy_to_input(src):
    dst = INPUT_DIR / src.name
    shutil.copy2(src, dst)
    return f'{INPUT_SUB}/{dst.name}'

def patch_common(prompt, prefix, seed=None, steps=None):
    # Apply seed and save prefix broadly where node ids match current pack.
    for node in prompt.values():
        if isinstance(node, dict) and node.get('class_type') == 'SaveImage':
            node.setdefault('inputs', {})['filename_prefix'] = prefix
        if seed is not None and isinstance(node, dict) and node.get('class_type') == 'KSampler':
            node.setdefault('inputs', {})['seed'] = seed
            if steps is not None:
                node['inputs']['steps'] = steps

report={'run': RUN, 'base': BASE, 'client_id': CLIENT_ID, 'input_dir': str(INPUT_DIR), 'results': [], 'errors': []}
try:
    # backend and object availability
    report['system_stats'] = get('/system_stats')
    report['queue_before'] = get('/queue')
    obj = get('/object_info')
    report['object_info_count'] = len(obj)
    classes=set()
    for path in WORKFLOWS.values():
        graph=json.loads(path.read_text())
        for n in graph.values():
            if isinstance(n, dict) and 'class_type' in n:
                classes.add(n['class_type'])
    missing_classes=sorted(c for c in classes if c not in obj)
    report['missing_class_types'] = missing_classes
    if missing_classes:
        raise RuntimeError('missing class types: ' + ', '.join(missing_classes))

    # 1 anchor
    p=load('character_anchor_base')
    set_path(p, '3.inputs.text', PROMPTS['anchor_pos'])
    set_path(p, '4.inputs.text', PROMPTS['anchor_neg'])
    patch_common(p, f'{RUN}/01_anchor', seed=260517001)
    r=submit('character_anchor_base', p); report['results'].append(r); print('DONE character_anchor_base', r['prompt_id'], flush=True)
    anchor_out=first_existing(r['outputs'])
    if not anchor_out:
        raise RuntimeError('anchor output missing')
    anchor_input=copy_to_input(anchor_out)
    report['anchor_input_name']=anchor_input

    # 2 expression
    p=load('expression_variations')
    set_path(p, '1.inputs.image', anchor_input)
    set_path(p, '6.inputs.text', PROMPTS['expression_pos'])
    set_path(p, '7.inputs.text', PROMPTS['expression_neg'])
    patch_common(p, f'{RUN}/02_expression', seed=260517002)
    r=submit('expression_variations', p); report['results'].append(r); print('DONE expression_variations', r['prompt_id'], flush=True)

    # 3 alpha on anchor
    p=load('transparency_alpha')
    set_path(p, '1.inputs.image', anchor_input)
    patch_common(p, f'{RUN}/03_alpha_anchor')
    r=submit('transparency_alpha', p); report['results'].append(r); print('DONE transparency_alpha', r['prompt_id'], flush=True)

    # 4 background
    p=load('background_art')
    set_path(p, '3.inputs.text', PROMPTS['background_pos'])
    set_path(p, '4.inputs.text', PROMPTS['background_neg'])
    patch_common(p, f'{RUN}/04_background', seed=260517004)
    r=submit('background_art', p); report['results'].append(r); print('DONE background_art', r['prompt_id'], flush=True)

    # 5 prop
    p=load('prop_closeup_cg')
    set_path(p, '3.inputs.text', PROMPTS['prop_pos'])
    set_path(p, '4.inputs.text', PROMPTS['prop_neg'])
    patch_common(p, f'{RUN}/05_prop', seed=260517005)
    r=submit('prop_closeup_cg', p); report['results'].append(r); print('DONE prop_closeup_cg', r['prompt_id'], flush=True)

    # 6 outfit
    p=load('outfit_variations')
    set_path(p, '3.inputs.image', anchor_input)
    set_path(p, '23.inputs.text', PROMPTS['outfit_pos'])
    set_path(p, '24.inputs.text', PROMPTS['outfit_neg'])
    patch_common(p, f'{RUN}/06_outfit', seed=260517006)
    r=submit('outfit_variations', p); report['results'].append(r); print('DONE outfit_variations', r['prompt_id'], flush=True)

    # 7 event cg
    p=load('event_cg')
    set_path(p, '3.inputs.image', anchor_input)
    set_path(p, '9.inputs.text', PROMPTS['event_pos'])
    set_path(p, '10.inputs.text', PROMPTS['event_neg'])
    patch_common(p, f'{RUN}/07_event_cg', seed=260517007)
    r=submit('event_cg', p); report['results'].append(r); print('DONE event_cg', r['prompt_id'], flush=True)

except Exception as e:
    report['errors'].append({'error': repr(e)})
    print('ERROR', repr(e), flush=True)
finally:
    try:
        report['queue_after'] = get('/queue')
    except Exception as e:
        report['queue_after_error'] = repr(e)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print('REPORT', REPORT, flush=True)
    if report['errors']:
        raise SystemExit(1)
