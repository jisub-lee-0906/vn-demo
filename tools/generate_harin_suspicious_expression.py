#!/usr/bin/env python3
"""Generate distinct Harin suspicious/tsundere expression candidates from selected s03 anchor."""
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
from datetime import datetime
from pathlib import Path

REPO = Path('/home/jisub-lee/workspace/vn-demo')
PACK = REPO / 'workflow_packs/renpy_asset_workflows'
SRC_TEMPLATE = PACK / 'api_workflows/03_expression_source_angry_move_d0p54_w0p48_api.json'
ALPHA_TEMPLATE = PACK / 'api_workflows/03_expression_alpha_angry_toonout_o0_b0_ref0_api.json'
ENDPOINT = 'http://172.28.224.1:8000'
CLIENT_ID = str(uuid.uuid4())
COMFY_INPUT = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input')
RUN_ID = datetime.now().strftime('harin_suspicious_expression_%Y%m%d_%H%M%S')
OUT_DIR = REPO / 'generated/comfyui' / RUN_ID
DERIVED_DIR = OUT_DIR / 'derived_workflows'
SOURCE = REPO / 'generated/comfyui/harin_tsundere_candidates_20260512_215310/s03_harin_tsundere.png'
SEM_SUSPICIOUS = REPO / 'demo/game/images/characters/harin/harin_suspicious.png'

QUALITY = 'masterpiece, best quality, very aesthetic, newest'
IDENTITY = '1girl, solo, anime style, cowboy shot, upper body character portrait, full head visible, complete hair visible, large centered character, chestnut shoulder-length bob hair with inward curled ends, blue-gray eyes, small rounded face, white blouse, navy ribbon tie, cropped ivory cardigan, navy pleated skirt, neat academy uniform, clean sharp anime lineart, flat solid medium gray background, plain uniform gray backdrop'
BASE_NEG = 'text, watermark, logo, multiple girls, duplicate character, cropped head, cut off hair, cropped arms, cropped hands, out of frame, extra arms, extra hands, bad hands, fused fingers, missing fingers, low quality, worst quality, full body, tiny character, chibi, feet visible, shoes, white background, bright background, gradient background, green background, teal background, headwear, object above head, ribbon on head, bow on head, hair ornament, hat, crown, reference sheet, character sheet, sprite sheet, expression sheet, inset, profile card, ui, interface, dialogue box, neutral face, expressionless, big smile, happy smile, sad, crying, screaming, distorted face, comic symbols, anger mark'

CANDIDATES = [
    {
        'id': 'suspicious_a',
        'seed': 1038431,
        'denoise': 0.54,
        'weight': 0.48,
        'cfg': 6.2,
        'expression': 'suspicious tsundere expression, furrowed brows, narrowed eyes, small pouting mouth, faint blush, clearly annoyed but cute, not subtle expression',
        'note': '기본 의심/삐짐: 눈썹+작은 pout+홍조',
    },
    {
        'id': 'suspicious_b',
        'seed': 1038432,
        'denoise': 0.52,
        'weight': 0.52,
        'cfg': 6.0,
        'expression': 'skeptical side-eye expression, one eyebrow slightly raised, small pout, faint blush, cute strict audit officer look, clearly suspicious face',
        'note': '보수적 identity 유지: side-eye + 한쪽 눈썹',
    },
    {
        'id': 'suspicious_c',
        'seed': 1038433,
        'denoise': 0.56,
        'weight': 0.46,
        'cfg': 6.2,
        'expression': 'strong tsundere annoyed expression, puffed cheeks, furrowed brows, sharp suspicious eyes, tiny frown, embarrassed blush, readable pout',
        'note': '강한 츤데레: 볼 부풀림/홍조, drift 주의',
    },
    {
        'id': 'suspicious_d',
        'seed': 1038434,
        'denoise': 0.54,
        'weight': 0.50,
        'cfg': 6.1,
        'expression': 'strict suspicious expression, narrowed blue-gray eyes, serious small frown, slightly blushing cheeks, cute but stern student council auditor, readable annoyed face',
        'note': '감찰 담당 느낌 강화: 엄격하지만 귀여운 표정',
    },
]


def api_json(path: str, payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(ENDPOINT + path, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def wait_prompt(prompt_id: str, timeout=900):
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


def output_images(hist):
    images = []
    for node_out in hist.get('outputs', {}).values():
        images.extend(node_out.get('images', []))
    if not images:
        raise RuntimeError('workflow produced no image')
    return images


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
    stride = width * 4
    prev = bytearray(stride)
    offset = 0
    transparent = opaque = semi = 0
    amin, amax = 255, 0
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        scanline = bytearray(raw[offset:offset+stride])
        offset += stride
        for i in range(stride):
            left = scanline[i-4] if i >= 4 else 0
            up = prev[i]
            up_left = prev[i-4] if i >= 4 else 0
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
            amin = min(amin, amax if False else a)
            amax = max(amax, a)
            if a == 0:
                transparent += 1
            elif a == 255:
                opaque += 1
            else:
                semi += 1
        prev = scanline
    return {'width': width, 'height': height, 'alpha_min': amin, 'alpha_max': amax, 'transparent': transparent, 'opaque': opaque, 'semi': semi}


def make_sheet(images, sheet_path: Path, alpha=False):
    cell_paths = []
    font = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    for label, path in images:
        cell = sheet_path.parent / f'_cell_{label}.png'
        if alpha:
            vf = f"color=c=0x222222:s=420x560[bg];[0:v]scale=320:-1[fg];[bg][fg]overlay=(W-w)/2:20:format=auto,drawtext=fontfile={font}:text='{label}':x=16:y=520:fontsize=26:fontcolor=white,drawbox=x=0:y=0:w=420:h=560:color=0x909090:t=2"
            subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(path),'-filter_complex',vf,'-frames:v','1',str(cell)], check=True)
        else:
            vf = (
                "scale=320:426:force_original_aspect_ratio=decrease,"
                "pad=420:560:(ow-iw)/2:20:white,"
                f"drawtext=fontfile={font}:text='{label}':x=16:y=520:fontsize=26:fontcolor=black,"
                "drawbox=x=0:y=0:w=420:h=560:color=0x505050:t=2"
            )
            subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(path),'-vf',vf,str(cell)], check=True)
        cell_paths.append(cell)
    if len(cell_paths) == 1:
        shutil.copy2(cell_paths[0], sheet_path)
    else:
        inputs=[]
        for p in cell_paths:
            inputs += ['-i', str(p)]
        layout='0_0|420_0|0_560|420_560'
        subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error',*inputs,'-filter_complex',f'xstack=inputs={len(cell_paths)}:layout={layout}:fill=0xE6E6E6',str(sheet_path)], check=True)
    for p in cell_paths:
        p.unlink(missing_ok=True)


def run_source(c):
    wf = json.loads(SRC_TEMPLATE.read_text())
    wf['3']['inputs']['image'] = 'hermes_harin_s03_neutral_for_expression.png'
    wf['6']['inputs']['weight'] = c['weight']
    wf['7']['inputs']['text'] = f"{QUALITY}, {IDENTITY}, {c['expression']}"
    wf['8']['inputs']['text'] = BASE_NEG
    wf['10']['inputs']['seed'] = c['seed']
    wf['10']['inputs']['denoise'] = c['denoise']
    wf['10']['inputs']['cfg'] = c['cfg']
    wf['12']['inputs']['filename_prefix'] = f"hermes_vn_harin_suspicious_20260512/{RUN_ID}_{c['id']}_source"
    path = DERIVED_DIR / f"{c['id']}_source_workflow.json"
    path.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n')
    resp = api_json('/prompt', {'prompt': wf, 'client_id': CLIENT_ID}, timeout=30)
    hist = wait_prompt(resp['prompt_id'])
    local = OUT_DIR / f"{c['id']}_source.png"
    img = output_images(hist)[0]
    download_image(img, local)
    return local, path, resp['prompt_id'], img


def run_alpha(selected_id: str, selected_source: Path):
    input_name = f'hermes_harin_{selected_id}_selected_source.png'
    shutil.copy2(selected_source, COMFY_INPUT / input_name)
    wf = json.loads(ALPHA_TEMPLATE.read_text())
    wf['1']['inputs']['image'] = input_name
    wf['3']['inputs']['filename_prefix'] = f"hermes_vn_harin_suspicious_20260512/{RUN_ID}_{selected_id}_alpha_toonout_o0_b0_ref0"
    path = DERIVED_DIR / f"{selected_id}_alpha_workflow.json"
    path.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n')
    resp = api_json('/prompt', {'prompt': wf, 'client_id': CLIENT_ID}, timeout=30)
    hist = wait_prompt(resp['prompt_id'])
    alpha = OUT_DIR / f"{selected_id}_alpha.png"
    img = output_images(hist)[0]
    download_image(img, alpha)
    stats = png_alpha_counts(alpha)
    if stats['alpha_min'] != 0 or stats['alpha_max'] != 255 or stats['transparent'] == 0 or stats['opaque'] == 0 or stats['semi'] == 0:
        raise AssertionError(f'bad alpha stats: {stats}')
    return alpha, path, stats, resp['prompt_id'], img


def main():
    if not SOURCE.exists():
        raise SystemExit(f'missing source {SOURCE}')
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED_DIR.mkdir(exist_ok=True)
    COMFY_INPUT.mkdir(parents=True, exist_ok=True)
    queue = api_json('/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise SystemExit(f'ComfyUI queue not empty: {queue}')
    shutil.copy2(SOURCE, COMFY_INPUT / 'hermes_harin_s03_neutral_for_expression.png')
    manifest = {
        'run_id': RUN_ID,
        'status': 'candidate_generation_and_selected_alpha_promoted',
        'endpoint': ENDPOINT,
        'source_anchor': str(SOURCE.relative_to(REPO)),
        'base_source_template': str(SRC_TEMPLATE.relative_to(REPO)),
        'base_alpha_template': str(ALPHA_TEMPLATE.relative_to(REPO)),
        'policy': 'Derived from workflow-pack 03 expression source and alpha templates; edited only input image, prompt expression phrase, seed, denoise/IPAdapter weight, and output prefix.',
        'candidates': [],
    }
    sources = []
    for c in CANDIDATES:
        local, wf_path, pid, comfy_meta = run_source(c)
        sources.append((c['id'], local))
        manifest['candidates'].append({
            **c,
            'local_path': str(local.relative_to(REPO)),
            'derived_workflow': str(wf_path.relative_to(REPO)),
            'prompt_id': pid,
            'comfy_output': comfy_meta,
        })
    source_sheet = OUT_DIR / 'harin_suspicious_source_contact_sheet.png'
    make_sheet(sources, source_sheet, alpha=False)
    # Autonomous selection: choose conservative suspicious_b unless the stronger variants are manually selected later.
    selected_id = 'suspicious_b'
    selected_source = dict(sources)[selected_id]
    alpha, alpha_wf, stats, alpha_pid, alpha_meta = run_alpha(selected_id, selected_source)
    shutil.copy2(alpha, SEM_SUSPICIOUS)
    alpha_sheet = OUT_DIR / 'harin_suspicious_alpha_dark_sheet.png'
    make_sheet([(selected_id, alpha)], alpha_sheet, alpha=True)
    manifest['contact_sheet'] = str(source_sheet.relative_to(REPO))
    manifest['selected_candidate'] = selected_id
    manifest['selection_reason'] = 'Conservative suspicious side-eye/pout setting chosen for first route prototype to maximize identity/crop consistency while making suspicious visibly distinct from neutral.'
    manifest['alpha'] = {
        'local_path': str(alpha.relative_to(REPO)),
        'derived_workflow': str(alpha_wf.relative_to(REPO)),
        'stats': stats,
        'prompt_id': alpha_pid,
        'comfy_output': alpha_meta,
        'semantic_path': str(SEM_SUSPICIOUS.relative_to(REPO)),
        'dark_sheet': str(alpha_sheet.relative_to(REPO)),
    }
    (OUT_DIR / 'RUN_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
