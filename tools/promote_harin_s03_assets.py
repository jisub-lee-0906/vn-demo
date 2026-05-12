#!/usr/bin/env python3
"""Promote selected Harin s03 candidate through toonout alpha and restore S01 semantic assets."""
from __future__ import annotations

import json
import shutil
import struct
import subprocess
import time
import urllib.parse
import urllib.request
import uuid
import zlib
from pathlib import Path

REPO = Path('/home/jisub-lee/workspace/vn-demo')
ENDPOINT = 'http://172.28.224.1:8000'
CLIENT_ID = str(uuid.uuid4())
COMFY_INPUT = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input')
RUN_DIR = REPO / 'generated/comfyui/harin_tsundere_candidates_20260512_215310'
SRC = RUN_DIR / 's03_harin_tsundere.png'
ALPHA_DIR = RUN_DIR / 'alpha_s03_toonout'
DERIVED = ALPHA_DIR / 's03_alpha_toonout_o0_b0_ref0_workflow.json'
SEM_HARIN_DIR = REPO / 'demo/game/images/characters/harin'
SEM_BG_DIR = REPO / 'demo/game/images/backgrounds'
SEM_CG_DIR = REPO / 'demo/game/images/cg'
PACK_ALPHA_TEMPLATE = REPO / 'workflow_packs/renpy_asset_workflows/api_workflows/02_alpha_toonout_o0_b0_ref0_api.json'

# Existing selected S01 assets from regenerated canonical reset.
BG_SRC = REPO / 'generated/comfyui/canonical_reset_20260512_211728/bg_summoning_hall/bg_summoning_hall_s03_00001_.png'
ORB_SRC = REPO / 'generated/comfyui/canonical_reset_20260512_211728/cg_measurement_orb/cg_measurement_orb_s01_00001_.png'


def api_json(path: str, payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(ENDPOINT + path, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def wait_prompt(prompt_id: str, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        hist = api_json('/history/' + prompt_id, timeout=20)
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(2)
    raise TimeoutError(prompt_id)


def download_image(meta, dst: Path):
    q = urllib.parse.urlencode({'filename': meta['filename'], 'subfolder': meta.get('subfolder', ''), 'type': meta.get('type', 'output')})
    with urllib.request.urlopen(ENDPOINT + '/view?' + q, timeout=60) as r:
        dst.write_bytes(r.read())


def png_alpha_counts(path: Path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise AssertionError(f'{path} is not PNG')
    pos = 8
    idat = []
    width = height = bit_depth = color_type = None
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+length]
        pos += 12 + length
        if chunk_type == b'IHDR':
            width, height, bit_depth, color_type, *_ = struct.unpack('>IIBBBBB', chunk)
        elif chunk_type == b'IDAT':
            idat.append(chunk)
        elif chunk_type == b'IEND':
            break
    if color_type != 6 or bit_depth != 8:
        raise AssertionError(f'{path} must be 8-bit RGBA; color_type={color_type} bit_depth={bit_depth}')
    raw = zlib.decompress(b''.join(idat))
    bpp = 4
    stride = width * bpp
    prev = bytearray(stride)
    offset = 0
    transparent = opaque = semi = 0
    amin, amax = 255, 0
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        scanline = bytearray(raw[offset:offset+stride])
        offset += stride
        for i in range(stride):
            left = scanline[i-bpp] if i >= bpp else 0
            up = prev[i]
            up_left = prev[i-bpp] if i >= bpp else 0
            if filter_type == 1:
                scanline[i] = (scanline[i] + left) & 255
            elif filter_type == 2:
                scanline[i] = (scanline[i] + up) & 255
            elif filter_type == 3:
                scanline[i] = (scanline[i] + ((left + up) // 2)) & 255
            elif filter_type == 4:
                pred = left + up - up_left
                pa, pb, pc = abs(pred-left), abs(pred-up), abs(pred-up_left)
                predictor = left if pa <= pb and pa <= pc else (up if pb <= pc else up_left)
                scanline[i] = (scanline[i] + predictor) & 255
            elif filter_type != 0:
                raise AssertionError(f'unsupported PNG filter {filter_type}')
        for x in range(width):
            a = scanline[x*4+3]
            amin = min(amin, a)
            amax = max(amax, a)
            if a == 0:
                transparent += 1
            elif a == 255:
                opaque += 1
            else:
                semi += 1
        prev = scanline
    return {'width': width, 'height': height, 'alpha_min': amin, 'alpha_max': amax, 'transparent': transparent, 'opaque': opaque, 'semi': semi}


def make_checker(path: Path, size='1280x1280'):
    # Single-frame checkerboard. The lavfi expression uses escaped commas for ffmpeg.
    expr = f'nullsrc=s={size},format=rgba,geq=r=if(mod(floor(X/32)+floor(Y/32)\\,2)\\,210\\,120):g=if(mod(floor(X/32)+floor(Y/32)\\,2)\\,210\\,120):b=if(mod(floor(X/32)+floor(Y/32)\\,2)\\,210\\,120):a=255'
    subprocess.run([
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi',
        '-i', expr, '-frames:v', '1', '-update', '1', str(path)
    ], check=True)


def composite(bg_expr: str, alpha_png: Path, out: Path):
    subprocess.run([
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'lavfi', '-i', bg_expr,
        '-i', str(alpha_png),
        '-filter_complex', '[1:v]scale=520:-1[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2:format=auto',
        '-frames:v', '1', str(out)
    ], check=True)


def make_qa(alpha_png: Path):
    composite('color=c=0x111111:s=1280x1280', alpha_png, ALPHA_DIR / 's03_alpha_full_dark.png')
    composite('color=c=0x777777:s=1280x1280', alpha_png, ALPHA_DIR / 's03_alpha_full_gray.png')
    checker = ALPHA_DIR / '_checker.png'
    make_checker(checker)
    subprocess.run([
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', str(checker), '-i', str(alpha_png),
        '-filter_complex', '[1:v]scale=520:-1[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2:format=auto',
        '-frames:v', '1', str(ALPHA_DIR / 's03_alpha_full_checker.png')
    ], check=True)
    checker.unlink(missing_ok=True)


def main():
    if not SRC.exists():
        raise SystemExit(f'missing selected source {SRC}')
    if not BG_SRC.exists() or not ORB_SRC.exists():
        raise SystemExit('missing regenerated S01 bg/orb selected source')
    ALPHA_DIR.mkdir(parents=True, exist_ok=True)
    queue = api_json('/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise SystemExit(f'ComfyUI queue not empty: {queue}')
    input_name = 'hermes_vn_harin_tsundere_s03_source.png'
    COMFY_INPUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, COMFY_INPUT / input_name)
    wf = json.loads(PACK_ALPHA_TEMPLATE.read_text())
    wf['1']['inputs']['image'] = input_name
    wf['3']['inputs']['filename_prefix'] = 'hermes_vn_harin_tsundere_20260512/alpha_s03_toonout_o0_b0_ref0'
    DERIVED.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n')
    resp = api_json('/prompt', {'prompt': wf, 'client_id': CLIENT_ID}, timeout=30)
    prompt_id = resp['prompt_id']
    hist = wait_prompt(prompt_id)
    images = []
    for node_out in hist.get('outputs', {}).values():
        images.extend(node_out.get('images', []))
    if not images:
        raise RuntimeError('alpha workflow produced no image')
    alpha_local = ALPHA_DIR / 's03_harin_tsundere_alpha.png'
    download_image(images[0], alpha_local)
    stats = png_alpha_counts(alpha_local)
    if stats['alpha_min'] != 0 or stats['alpha_max'] != 255 or stats['transparent'] == 0 or stats['opaque'] == 0:
        raise AssertionError(f'bad alpha stats: {stats}')
    make_qa(alpha_local)
    SEM_HARIN_DIR.mkdir(parents=True, exist_ok=True)
    SEM_BG_DIR.mkdir(parents=True, exist_ok=True)
    SEM_CG_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(alpha_local, SEM_HARIN_DIR / 'harin_neutral.png')
    shutil.copy2(alpha_local, SEM_HARIN_DIR / 'harin_suspicious.png')
    shutil.copy2(BG_SRC, SEM_BG_DIR / 'bg_summoning_hall.png')
    shutil.copy2(ORB_SRC, SEM_CG_DIR / 'cg_measurement_orb.png')
    manifest = {
        'status': 'promoted_prototype_pending_renpy_screenshot_qa',
        'selected_candidate': 's03_harin_tsundere',
        'source': str(SRC.relative_to(REPO)),
        'alpha_workflow': str(DERIVED.relative_to(REPO)),
        'alpha_output': str(alpha_local.relative_to(REPO)),
        'alpha_stats': stats,
        'qa_sheets': [
            str((ALPHA_DIR / 's03_alpha_full_dark.png').relative_to(REPO)),
            str((ALPHA_DIR / 's03_alpha_full_gray.png').relative_to(REPO)),
            str((ALPHA_DIR / 's03_alpha_full_checker.png').relative_to(REPO)),
        ],
        'semantic_paths': [
            'demo/game/images/characters/harin/harin_neutral.png',
            'demo/game/images/characters/harin/harin_suspicious.png',
            'demo/game/images/backgrounds/bg_summoning_hall.png',
            'demo/game/images/cg/cg_measurement_orb.png',
        ],
        'comfy_output': images[0],
        'prompt_id': prompt_id,
        'note': 'suspicious currently reuses selected s03 neutral anchor until expression workflow is run.',
    }
    (ALPHA_DIR / 'PROMOTION_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
