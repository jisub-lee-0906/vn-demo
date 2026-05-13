#!/usr/bin/env python3
import argparse, copy, json, sys, time, urllib.request, urllib.error
from pathlib import Path

ENDPOINT_DEFAULT = "http://172.28.224.1:8000"
ROOT = Path('/home/jisub-lee/workspace/vn-demo')
TEMPLATE = ROOT / 'workflow_packs/renpy_asset_workflows/04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json'

CHARACTER_TAGS = "short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts"
ANCHOR = "hermes_identity_silver_bob_anchor_v190.png"
POSES = {
    "arms_crossed": {
        "ref": "hermes_pose_ref_multi04b_silver_bob_arms_crossed.png",
        "pos": "arms_crossed, crossed_arms, folded_arms",
        "neg": "hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed",
    },
    "hand_chest": {
        "ref": "hermes_pose_ref_multi04b_silver_bob_hand_chest.png",
        "pos": "hand_on_chest, hand_to_own_chest, hands_near_chest",
        "neg": "arms_crossed, crossed_arms, folded_arms, hands_on_hips, hands_in_pockets, hands_near_face",
    },
    "pointing": {
        "ref": "hermes_pose_ref_multi04b_silver_bob_pointing.png",
        "pos": "pointing, pointing_at_viewer, outstretched_arm, index_finger_raised",
        "neg": "arms_crossed, crossed_arms, folded_arms, hands_on_hips, hands_in_pockets, hands_near_face",
    },
    "one_hand_hip": {
        "ref": "hermes_pose_ref_merge04_one_hand_hip.png",
        "pos": "hand_on_hip, one_hand_on_hip, other_arm_at_side",
        "neg": "arms_crossed, crossed_arms, folded_arms, hand_on_chest, hands_near_chest",
    },
}
EXPRESSIONS = {
    "neutral": {"pos": "neutral_expression, closed_mouth", "neg": "smile, open_mouth, sad, angry, disgusted, scared, fearful, surprised, crying, tears"},
    "happy": {"pos": "happy, smile, open_mouth", "neg": "frown, sad, angry, annoyed, disgusted, scared, fearful, serious, stern, pouting, crying, tears"},
    "sad": {"pos": "sad, frown, downturned_mouth, worried", "neg": "smile, happy, laughing, angry, disgusted, surprised"},
    "angry": {"pos": "angry, scowl, furrowed_brow, frown", "neg": "smile, happy, sad, crying, scared, fearful, surprised"},
    "surprised": {"pos": "surprised, wide_eyes, open_mouth", "neg": "smile, happy, angry, sad, disgusted, serious, stern"},
    "fearful": {"pos": "scared, fearful, wide_eyes, open_mouth, worried", "neg": "smile, happy, angry, disgusted, serious, stern"},
    "disgusted": {"pos": "disgusted, nauseated, frown, half-closed_eyes", "neg": "smile, happy, surprised, scared, fearful, open_mouth"},
}

def http_json(method, url, data=None, timeout=30):
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, method=method, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def get_json(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def wait_history(endpoint, prompt_id, poll=2, timeout=900):
    start = time.time()
    while time.time() - start < timeout:
        hist = get_json(f"{endpoint}/history/{prompt_id}", timeout=30)
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(poll)
    raise TimeoutError(prompt_id)

def outputs_from_history(h):
    outs=[]
    for node_id, node in h.get('outputs', {}).items():
        for im in node.get('images', []):
            sub = im.get('subfolder','')
            name = im.get('filename')
            typ = im.get('type','output')
            if typ == 'output' and name:
                outs.append({'node': node_id, 'subfolder': sub, 'filename': name, 'path': str(Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output') / sub / name)})
    return outs

def build_prompt(template, pose_slug, expr_slug, seed, prefix_root):
    wf = copy.deepcopy(template)
    pose = POSES[pose_slug]
    expr = EXPRESSIONS[expr_slug]
    wf['4']['inputs']['image'] = ANCHOR
    wf['5']['inputs']['image'] = pose['ref']
    pose_expr = pose['pos'] + ', ' + expr['pos']
    wf['2']['inputs']['text'] = wf['2']['inputs']['text'].replace('TEMPLATE_CHARACTER_TAGS', CHARACTER_TAGS).replace('TEMPLATE_POSE_TAGS', pose_expr)
    neg_expr = expr['neg']
    neg_pose = pose['neg']
    # If the target expression needs smile/open_mouth, do not accidentally ban it via pose conflicts.
    if 'smile' in expr['pos']:
        neg_pose = ', '.join([x.strip() for x in neg_pose.split(',') if x.strip() != 'smile'])
    if 'open_mouth' in expr['pos']:
        neg_pose = ', '.join([x.strip() for x in neg_pose.split(',') if x.strip() != 'open_mouth'])
    wf['3']['inputs']['text'] = wf['3']['inputs']['text'].replace('TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES', neg_expr).replace('TEMPLATE_POSE_CONFLICT_NEGATIVES', neg_pose)
    wf['14']['inputs']['seed'] = seed
    stem = f"{pose_slug}_{expr_slug}_seed{seed}"
    wf['16']['inputs']['filename_prefix'] = f"{prefix_root}/src_{stem}"
    wf['17']['inputs']['filename_prefix'] = f"{prefix_root}/control_{stem}"
    return wf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--endpoint', default=ENDPOINT_DEFAULT)
    ap.add_argument('--prefix-root', default='hermes_vn_04_pose_expression_matrix_20260513')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()
    endpoint = args.endpoint.rstrip('/')
    queue = get_json(endpoint + '/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise SystemExit(f"ComfyUI queue not empty: {queue}")
    template = json.loads(TEMPLATE.read_text())
    manifest = {'endpoint': endpoint, 'template': str(TEMPLATE), 'anchor': ANCHOR, 'character_tags': CHARACTER_TAGS, 'prefix_root': args.prefix_root, 'runs': []}
    seed_base = 719256000
    combos = [(p,e) for p in POSES for e in EXPRESSIONS]
    if args.limit:
        combos = combos[:args.limit]
    total = len(combos)
    for i, (pose_slug, expr_slug) in enumerate(combos, 1):
        seed = seed_base + i
        wf = build_prompt(template, pose_slug, expr_slug, seed, args.prefix_root)
        print(f"[{i}/{total}] submit {pose_slug}/{expr_slug} seed={seed}", flush=True)
        resp = http_json('POST', endpoint + '/prompt', {'prompt': wf, 'client_id': 'hermes-vn-04-matrix'})
        prompt_id = resp['prompt_id']
        hist = wait_history(endpoint, prompt_id)
        outs = outputs_from_history(hist)
        status = hist.get('status', {})
        print(f"[{i}/{total}] done {pose_slug}/{expr_slug} prompt_id={prompt_id} outputs={len(outs)} status={status.get('status_str')}", flush=True)
        manifest['runs'].append({'pose':pose_slug,'expression':expr_slug,'seed':seed,'prompt_id':prompt_id,'status':status,'outputs':outs})
        out_manifest = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output') / args.prefix_root / 'manifest_04_pose_expression_matrix.json'
        out_manifest.parent.mkdir(parents=True, exist_ok=True)
        out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps({'manifest': str(out_manifest), 'count': len(manifest['runs'])}, ensure_ascii=False))

if __name__ == '__main__':
    main()
