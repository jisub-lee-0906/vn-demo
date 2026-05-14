#!/usr/bin/env python3
import argparse, json, os, pathlib, shlex, subprocess, sys, time, urllib.request

REPO = pathlib.Path(__file__).resolve().parents[5]
TEMPLATE = pathlib.Path(__file__).resolve().parents[1] / 'workflow_api' / '06_outfit_mask_node_qa_api.json'
COMFY_OUT = pathlib.Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')

STAGES = [
    '00_source', '01_char_alpha', '02_florence_hand', '03_florence_both_hands',
    '04_florence_fingers', '05_union_hand_both', '06_union_plus_fingers',
    '07_grow2', '08_blur_existing_hand', '09_handfallback_final_enhanced',
    '10_handfallback_roi', '11_handfallback_added', '12_handfallback_debug',
    '13_refined_existing_skinfiltered', '14_skin_candidate', '15_wrist_bridge',
    '16_pretrim_before_cuff_trim',
]


def default_endpoint():
    try:
        ip = subprocess.check_output("ip route | awk '/default/ {print $3; exit}'", shell=True, text=True).strip()
        return f'http://{ip}:8000'
    except Exception:
        return 'http://127.0.0.1:8000'


def post_prompt(endpoint, prompt):
    req = urllib.request.Request(endpoint.rstrip('/') + '/prompt', data=json.dumps({'prompt': prompt}).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)['prompt_id']


def wait_history(endpoint, pid, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(endpoint.rstrip() + '/history/' + pid, timeout=30) as r:
            h = json.load(r)
        if pid in h:
            return h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def newest(pattern):
    hits = sorted(pathlib.Path('/').glob(pattern) if pattern.startswith('/') else pathlib.Path('.').glob(pattern), key=lambda p: p.stat().st_mtime)
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[-1]


def ffmpeg(cmd):
    subprocess.run(cmd, shell=True, check=True)


def make_sheet(run_dir, slug):
    parts = []
    for idx, stage in enumerate(STAGES):
        matches = sorted(run_dir.glob(f'{stage}_{slug}_*.png'), key=lambda p: p.stat().st_mtime)
        if not matches:
            print(f'WARN missing {stage} for {slug}', file=sys.stderr)
            continue
        src = matches[-1]
        out = pathlib.Path('/tmp') / f'vn06_maskqa_{run_dir.name}_{slug}_{idx:02d}.png'
        # lower-body crop; for masks/debug/source alike
        vf = f"crop=620:760:266:690,scale=248:304:flags=neighbor,drawbox=x=0:y=0:w=248:h=24:color=white@0.85:t=fill,drawtext=text={shlex.quote(stage)}:x=4:y=5:fontsize=13:fontcolor=black"
        ffmpeg(f"ffmpeg -y -v error -i {shlex.quote(str(src))} -vf {shlex.quote(vf)} {shlex.quote(str(out))}")
        parts.append(out)
    if not parts:
        return None
    blank = pathlib.Path('/tmp') / f'vn06_maskqa_{run_dir.name}_{slug}_blank.png'
    ffmpeg(f"ffmpeg -y -v error -f lavfi -i color=c=white:s=248x304 -frames:v 1 {shlex.quote(str(blank))}")
    while len(parts) < 18:
        parts.append(blank)
    inputs = ' '.join('-i ' + shlex.quote(str(p)) for p in parts[:18])
    layout = '|'.join(f'{(i%6)*248}_{(i//6)*304}' for i in range(18))
    sheet = run_dir / f'contact_{slug}_mask_node_qa.png'
    ffmpeg(f"ffmpeg -y -v error {inputs} -filter_complex {shlex.quote('xstack=inputs=18:layout=' + layout)} {shlex.quote(str(sheet))}")
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--endpoint', default=default_endpoint())
    ap.add_argument('--run-slug', default=time.strftime('v4e24_maskqa_%Y%m%d_%H%M%S'))
    ap.add_argument('--template', default=str(TEMPLATE), help='workflow API JSON template path')
    ap.add_argument('--character', action='append', required=True, help='slug=input/path/inside/ComfyUI/input.png')
    args = ap.parse_args()
    template = json.loads(pathlib.Path(args.template).read_text())
    run_dir = COMFY_OUT / 'hermes_vn_06_mask_node_qa' / args.run_slug
    results = []
    for item in args.character:
        if '=' not in item:
            raise SystemExit('--character must be slug=input.png')
        slug, image = item.split('=', 1)
        prompt = json.loads(json.dumps(template))
        prompt['3']['inputs']['image'] = image
        for node in prompt.values():
            if node.get('class_type') == 'SaveImage':
                node['inputs']['filename_prefix'] = node['inputs']['filename_prefix'].replace('TEMPLATE_run_slug', args.run_slug).replace('TEMPLATE_character_slug', slug)
        pid = post_prompt(args.endpoint, prompt)
        print(f'{slug}: prompt_id={pid}')
        hist = wait_history(args.endpoint, pid)
        print(f'{slug}: status={hist.get("status")}')
        sheet = make_sheet(run_dir, slug)
        results.append((slug, pid, sheet))
    print('\nRESULTS')
    for slug, pid, sheet in results:
        print(f'{slug}\tprompt_id={pid}\tsheet={sheet}')

if __name__ == '__main__':
    main()
