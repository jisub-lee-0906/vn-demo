#!/usr/bin/env python3
import argparse, json, pathlib, subprocess, tempfile, time, sys

ENDPOINT_DEFAULT = 'http://127.0.0.1:8001'

CHARACTER_TAGS = {
    't5': 'short_hair, dark_green_hair, green_eyes, glasses, blunt_bangs',
    'pink01': 'pink_hair, twin_braids, green_eyes, long_hair, twin_tails',
}

PRESETS = {
    'lavender_hoodie_black_skirt': {
        'outfit': 'lavender_hoodie, light_purple_hoodie, hoodie, pullover_hoodie, long_sleeves, casual_clothes, hood_down, front_pocket, loose_hoodie, ribbed_cuffs, ribbed_hem, black_pleated_skirt, pleated_skirt, black_pantyhose',
        'negative_add': 'school_uniform, cardigan, beige_cardigan, cream_cardigan, white_shirt, collared_shirt, bowtie, necktie, ribbon, blouse, blazer, jacket, old_clothes, previous_outfit, visible_old_clothing, leftover_clothing, shirt_collar, visible_collar, buttoned_shirt, buttons, waistband, exposed_midriff, belly_cutout',
        'seed': 62019146,
        'denoise': 0.92,
        'pulid_weight': 0.72,
    },
    'blue_denim_jacket': {
        'outfit': 'blue_denim_jacket, denim_jacket, open_jacket, unbuttoned_jacket, plain_white_t-shirt, white_t-shirt, blank_shirt, casual_clothes, long_sleeves, black_pleated_skirt, pleated_skirt, black_pantyhose',
        'negative_add': 'school_uniform, cardigan, beige_cardigan, cream_cardigan, sailor_collar, bowtie, necktie, ribbon, blouse, blazer, hoodie, hood, drawstring, old_clothes, previous_outfit, visible_old_clothing, leftover_clothing, shirt_collar, visible_collar, buttoned_shirt, buttons, cream_trim, beige_trim, yellow_trim, print_shirt, shirt_logo, clothes_writing, english_text, letters, brand_name',
        'seed': 62018641,
        'denoise': 0.82,
        'pulid_weight': 0.72,
    },
}

INPUTS = {
    't5': 'hermes_vn_outfit_t5/t5_green_glasses_01_seed719260141.png',
    'pink01': 'source_pink_twinbraids_seed719251102_00001_.png',
}

def cmd_curl(args, timeout=60):
    cmd = ['cmd.exe', '/c', 'curl', '-sS', '-m', str(timeout)] + args
    p = subprocess.run(cmd, capture_output=True)
    out = p.stdout.decode('utf-8', 'replace')
    err = p.stderr.decode('utf-8', 'replace')
    if p.returncode != 0:
        raise RuntimeError(f'curl failed {p.returncode}: {err}\n{out}')
    # cmd.exe from UNC may print a warning before JSON; trim to first JSON brace.
    first = min([i for i in [out.find('{'), out.find('[')] if i >= 0] or [0])
    return out[first:]

def post_prompt(endpoint, prompt):
    tmp = pathlib.Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input/hermes_tmp_06_prompt.json')
    body = {'prompt': prompt}
    tmp.write_text(json.dumps(body, ensure_ascii=False), encoding='utf-8')
    win = r'C:\Users\Desktop\Documents\ComfyUI\input\hermes_tmp_06_prompt.json'
    out = cmd_curl(['-X', 'POST', endpoint + '/prompt', '-H', 'Content-Type: application/json', '--data-binary', '@' + win], timeout=120)
    return json.loads(out)['prompt_id']

def get_json(endpoint, path):
    return json.loads(cmd_curl([endpoint + path], timeout=60))

def patch_prompt(template, slug, preset_slug, run_slug):
    p = json.loads(json.dumps(template))
    preset = PRESETS[preset_slug]
    p['3']['inputs']['image'] = INPUTS[slug]
    p['23']['inputs']['text'] = p['23']['inputs']['text'].replace('TEMPLATE_CHARACTER_IDENTITY_TAGS', CHARACTER_TAGS[slug]).replace('TEMPLATE_TARGET_FULL_OUTFIT_TAGS', preset['outfit'])
    if preset['negative_add'] not in p['24']['inputs']['text']:
        p['24']['inputs']['text'] += ', ' + preset['negative_add']
    p['27']['inputs']['seed'] = preset['seed']
    p['27']['inputs']['denoise'] = preset['denoise']
    p['22']['inputs']['weight'] = preset['pulid_weight']
    # cleanup branch seed follows main seed + 1 unless node exists differently
    if '41' in p:
        p['41']['inputs']['seed'] = preset['seed'] + 1
    for node in p.values():
        if node.get('class_type') == 'SaveImage':
            pref = node['inputs']['filename_prefix']
            pref = pref.replace('hermes_vn_outfit_variation/', f'hermes_vn_outfit_variation/{run_slug}_')
            pref = pref.replace('TEMPLATE_character_slug', slug)
            pref = pref.replace('TEMPLATE_preset_slug', preset_slug)
            pref = pref.replace('TEMPLATE_seed', str(preset['seed']))
            node['inputs']['filename_prefix'] = pref
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--template', required=True)
    ap.add_argument('--slug', required=True, choices=sorted(INPUTS))
    ap.add_argument('--preset', default='lavender_hoodie_black_skirt', choices=sorted(PRESETS))
    ap.add_argument('--run-slug', default='v4e28_gpu')
    ap.add_argument('--endpoint', default=ENDPOINT_DEFAULT)
    ap.add_argument('--timeout', type=int, default=1800)
    args = ap.parse_args()
    template = json.loads(pathlib.Path(args.template).read_text(encoding='utf-8'))
    q = get_json(args.endpoint, '/queue')
    if q.get('queue_running') or q.get('queue_pending'):
        print('QUEUE_NOT_EMPTY', json.dumps(q)[:1000])
        return 3
    prompt = patch_prompt(template, args.slug, args.preset, args.run_slug)
    pid = post_prompt(args.endpoint, prompt)
    print(f'prompt_id={pid}')
    start = time.time()
    while time.time() - start < args.timeout:
        h = get_json(args.endpoint, '/history/' + pid)
        if pid in h:
            status = h[pid].get('status', {})
            print(json.dumps(status, ensure_ascii=False))
            return 0 if status.get('completed') and status.get('status_str') == 'success' else 1
        time.sleep(5)
    print('TIMEOUT', pid)
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
