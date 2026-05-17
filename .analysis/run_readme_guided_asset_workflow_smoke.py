#!/usr/bin/env python3
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
RUN = time.strftime('hermes_vn_readme_guided_smoke_%Y%m%d_%H%M%S')
INPUT_SUB = f'hermes_vn_runtime/{RUN}'
INPUT_DIR = IN_ROOT / INPUT_SUB
INPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT = Path('/home/jisub-lee/workspace/vn-demo/.analysis/readme_guided_asset_workflow_smoke_report.json')
CLIENT_ID = 'hermes-readme-guided-smoke-' + uuid.uuid4().hex

# README-guided runtime substitutions.
# Safety note: character_anchor_base and expression_variations README templates contain `nude`.
# For this live smoke run that otherwise uses school/VN cues, runtime payload replaces that token
# with `fully_clothed, school_uniform` while preserving the template structure/placeholders.
IDENTITY = {
    'hair_len': 'long_hair',
    'hair_style': 'straight_hair, blunt_bangs, sidelocks',
    'hair_color': 'black_hair',
    'eye_color': 'blue_eyes',
}

PROMPTS = {
    'anchor_pos': (
        'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, '
        '1girl, solo, fully_clothed, school_uniform, medium_breasts, cowboy_shot, standing, front_view, looking_at_viewer, '
        'expressionless, closed_mouth, arms_at_sides, straight_posture, {hair_len}, {hair_style}, {hair_color}, {eye_color}, grey_background'
    ).format(**IDENTITY),
    'anchor_neg': 'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), vignette, shadow, depth_of_field, rim_lighting',

    'expression_pos': (
        'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, '
        '1girl, solo, fully_clothed, school_uniform, medium_breasts, cowboy_shot, standing, front_view, looking_at_viewer, '
        'straight_posture, arms_at_sides, {hair_len}, {hair_style}, {hair_color}, {eye_color}, '
        'happy, smile, open_mouth, sparkling_eyes, light_blush, BREAK, depth_of_field, volumetric_lighting'
    ).format(**IDENTITY),
    'expression_neg': 'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, lowres, bad_anatomy, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, changed_clothes, different_clothes, different_hair, (worst_quality, bad_quality:1.2), sad, angry, crying, tears, disgusted, expressionless',

    'background_pos': 'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, anime_style, digital_illustration, scenery, no_humans, background, wide_shot, landscape, clear_foreground, unoccupied_bottom_third, school, classroom, desks, chairs, blackboard, windows, day, sunlight, bright, clear_sky, BREAK, depth_of_field, volumetric_lighting',
    'background_neg': '1girl, 1boy, human, person, character, crowd, people, silhouette, monster, animal, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, ugly, lowres, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, simple_background, (worst_quality, bad_quality:1.2)',

    'prop_pos': 'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, anime_style, digital_illustration, still_life, close-up, macro_shot, object_focus, antique_key, brass_key, flat_key, key_teeth, key_bow, scratched_surface, metallic_luster, dark_velvet_cloth_background, BREAK, strong_depth_of_field, blurry_background, studio_lighting, highly_detailed_texture',
    'prop_neg': '1girl, 1boy, human, person, character, face, hands, body, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, lowres, bad_anatomy, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, (worst_quality, bad_quality:1.2), readable_text, fake_letters, fake_writing, printed_text, paragraphs, symbols, glyphs, logo, label, ui, interface, screenshot, dialogue_box, subtitle, caption',

    'outfit_pos': (
        'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, '
        '1girl, solo, medium_breasts, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, arms_at_sides, straight_posture, '
        '{hair_len}, {hair_style}, {hair_color}, {eye_color}, fully_clothed, '
        'school_uniform, black_blazer, open_jacket, white_shirt, collared_shirt, red_necktie, beige_cardigan, plaid_skirt, pleated_skirt, black_pantyhose, black_loafers, wool_texture, '
        'highly_detailed_clothes, grey_background'
    ).format(**IDENTITY),
    'outfit_neg': 'nude, nipples, nsfw, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, different_face, different_hair, different_hairstyle, different_eye_color, changed_face, changed_hair, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), vignette, shadow, depth_of_field, rim_lighting',

    'event_pos': (
        'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, anime_style, cinematic_visual_novel_event_CG, '
        'same_character_as_reference, preserve_original_face, preserve_original_facial_features, preserve_original_hairstyle, preserve_original_hair_color, preserve_original_eye_color, '
        'preserve_original_school_uniform_design, preserve_original_outfit_colors, preserve_original_body_proportions, minimal_character_redesign, 1girl, solo, '
        'long_hair, straight_hair, blunt_bangs, sidelocks, black_hair, blue_eyes, white_shirt, red_ribbon, pleated_skirt, '
        'upper_body, waist_up, one_hand_lightly_near_chest, slight_body_turn, happy, smile, light_blush, school, classroom, windows, sunset, sunlight, '
        'small_natural_pose_change_only, coherent_perspective, character_integrated_with_background_lighting, natural_pose, depth_of_field, detailed_background'
    ),
    'event_neg': 'different_character, different_face, different_facial_features, different_hair, different_hairstyle, different_hair_color, different_eye_color, different_clothes, changed_uniform, outfit_redesign, different_body_type, changed_body_proportions, extreme_action_pose, acrobatics, large_pose_change, tiny_character, far_away_character, empty_room, crowd, multiple_girls, duplicate_person, bad_hands, extra_fingers, missing_fingers, fewer_digits, bad_anatomy, long_body, deformed, mutated, cropped_head, lowres, blurry, text, watermark, signature, simple_background, white_background, (worst_quality, bad_quality:1.2)',
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
            p = OUT_ROOT / sub / filename
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
    for marker in ['TEMPLATE_', '{헤어', '{감정', '{상극', '{배경', '{시간', '{아이템', '{재질', '{놓여', '{캐릭터', '{원본', '{카메라', '{의상']:
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

def patch_common(prompt, prefix, seed=None):
    for node in prompt.values():
        if isinstance(node, dict) and node.get('class_type') == 'SaveImage':
            node.setdefault('inputs', {})['filename_prefix'] = prefix
        if seed is not None and isinstance(node, dict) and node.get('class_type') == 'KSampler':
            node.setdefault('inputs', {})['seed'] = seed

report={'run': RUN, 'base': BASE, 'client_id': CLIENT_ID, 'input_dir': str(INPUT_DIR), 'prompts': PROMPTS, 'safety_adjustments': ['README nude token replaced with fully_clothed, school_uniform in anchor/expression live smoke runtime prompts'], 'results': [], 'errors': []}
try:
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

    p=load('character_anchor_base')
    set_path(p, '3.inputs.text', PROMPTS['anchor_pos'])
    set_path(p, '4.inputs.text', PROMPTS['anchor_neg'])
    patch_common(p, f'{RUN}/01_anchor_readme', seed=260517101)
    r=submit('character_anchor_base', p); report['results'].append(r); print('DONE character_anchor_base', r['prompt_id'], flush=True)
    anchor_out=first_existing(r['outputs'])
    if not anchor_out:
        raise RuntimeError('anchor output missing')
    anchor_input=copy_to_input(anchor_out)
    report['anchor_input_name']=anchor_input

    p=load('expression_variations')
    set_path(p, '1.inputs.image', anchor_input)
    set_path(p, '6.inputs.text', PROMPTS['expression_pos'])
    set_path(p, '7.inputs.text', PROMPTS['expression_neg'])
    patch_common(p, f'{RUN}/02_expression_readme', seed=260517102)
    r=submit('expression_variations', p); report['results'].append(r); print('DONE expression_variations', r['prompt_id'], flush=True)

    p=load('transparency_alpha')
    set_path(p, '1.inputs.image', anchor_input)
    patch_common(p, f'{RUN}/03_alpha_readme')
    r=submit('transparency_alpha', p); report['results'].append(r); print('DONE transparency_alpha', r['prompt_id'], flush=True)

    p=load('background_art')
    set_path(p, '3.inputs.text', PROMPTS['background_pos'])
    set_path(p, '4.inputs.text', PROMPTS['background_neg'])
    patch_common(p, f'{RUN}/04_background_readme', seed=260517104)
    r=submit('background_art', p); report['results'].append(r); print('DONE background_art', r['prompt_id'], flush=True)

    p=load('prop_closeup_cg')
    set_path(p, '3.inputs.text', PROMPTS['prop_pos'])
    set_path(p, '4.inputs.text', PROMPTS['prop_neg'])
    patch_common(p, f'{RUN}/05_prop_readme', seed=260517105)
    r=submit('prop_closeup_cg', p); report['results'].append(r); print('DONE prop_closeup_cg', r['prompt_id'], flush=True)

    p=load('outfit_variations')
    set_path(p, '3.inputs.image', anchor_input)
    set_path(p, '23.inputs.text', PROMPTS['outfit_pos'])
    set_path(p, '24.inputs.text', PROMPTS['outfit_neg'])
    patch_common(p, f'{RUN}/06_outfit_readme', seed=260517106)
    r=submit('outfit_variations', p); report['results'].append(r); print('DONE outfit_variations', r['prompt_id'], flush=True)

    p=load('event_cg')
    set_path(p, '3.inputs.image', anchor_input)
    set_path(p, '9.inputs.text', PROMPTS['event_pos'])
    set_path(p, '10.inputs.text', PROMPTS['event_neg'])
    patch_common(p, f'{RUN}/07_event_cg_readme', seed=260517107)
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
