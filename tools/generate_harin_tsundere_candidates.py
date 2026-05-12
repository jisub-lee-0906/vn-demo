#!/usr/bin/env python3
"""Generate cute-tsundere Harin anchor candidates from canonical workflow-pack 01."""
from __future__ import annotations

import json
import time
import urllib.parse
import subprocess
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

REPO = Path('/home/jisub-lee/workspace/vn-demo')
PACK = REPO / 'workflow_packs/renpy_asset_workflows'
TEMPLATE = PACK / 'api_workflows/01_character_anchor_seed719238043_api.json'
RUN_ID = datetime.now().strftime('harin_tsundere_candidates_%Y%m%d_%H%M%S')
OUT_DIR = REPO / 'generated/comfyui' / RUN_ID
COMFY_OUTPUT = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')
ENDPOINT = 'http://172.28.224.1:8000'
CLIENT_ID = str(uuid.uuid4())

QUALITY = 'masterpiece, best quality, very aesthetic, newest'
FRAMING = '1girl, solo, anime style, cowboy shot, upper body character portrait, waist-up to upper-thigh visible, full head visible, complete hair visible, large centered character, hands inside canvas'
STYLE = 'cute tsundere girl, slight pout, faint blush, clean face, clean sharp anime lineart, flat solid medium gray background, plain uniform gray backdrop'
BASE_NEG = 'text, watermark, logo, multiple girls, duplicate character, cropped head, cut off hair, cropped arms, cropped hands, out of frame, extra arms, extra hands, bad hands, fused fingers, missing fingers, low quality, worst quality, full body, tiny character, chibi, feet visible, shoes, white background, bright background, gradient background, green background, teal background, green clothes, green cardigan, green uniform, green hair, teal hair, green highlights, green reflection, green rim light, background color bleeding into hair, translucent green edges, headwear, object above head, ribbon on head, bow on head, hair ornament, hat, crown, reference sheet, character sheet, sprite sheet, inset, profile card, ui, interface, dialogue box'

CANDIDATES = [
    {
        'id': 's01',
        'seed': 719238151,
        'design': 'short chestnut bob hair, large amber eyes, small rounded face, white blouse, navy ribbon tie, oversized light beige cardigan, navy pleated skirt, neat academy uniform, relaxed standing pose, hands below frame',
        'note': '기본형: 짧은 밤색 보브 + 큰 눈 + 오버핏 베이지 가디건',
    },
    {
        'id': 's02',
        'seed': 719238152,
        'design': 'soft auburn low twin tails, large warm brown eyes, small rounded face, white blouse, navy ribbon tie, light beige knit cardigan, navy pleated skirt, neat academy uniform, one hand near waist, other hand below frame',
        'note': '더 귀여운 방향: 낮은 양갈래 느낌, 단정한 감찰관',
    },
    {
        'id': 's03',
        'seed': 719238153,
        'design': 'chestnut shoulder-length bob hair with inward curled ends, blue-gray eyes, small rounded face, white blouse, navy ribbon tie, cropped ivory cardigan, navy pleated skirt, neat academy uniform, relaxed standing pose, hands below frame',
        'note': '청회색 눈 + 안쪽으로 말린 단발, 조금 더 히로인감',
    },
    {
        'id': 's04',
        'seed': 719238154,
        'design': 'warm brown fluffy bob hair, large honey eyes, tiny frown, white blouse, navy ribbon tie, oversized ivory knit cardigan, navy pleated skirt, neat academy uniform, one hand on hip, other hand below frame',
        'note': '츤데레 강조: 한 손 허리 + 작은 찡그림',
    },
    {
        'id': 's05',
        'seed': 719238155,
        'design': 'light chestnut medium bob hair, large violet-brown eyes, small rounded face, white blouse, navy ribbon tie, cream school cardigan, navy pleated skirt, neat academy uniform, arms relaxed below frame',
        'note': '부드러운 컬러: 밝은 체스트넛 + 보라빛 눈',
    },
    {
        'id': 's06',
        'seed': 719238156,
        'design': 'dark chestnut short bob hair, large amber eyes, sharp but cute eyes, white blouse, navy ribbon tie, light beige cardigan, navy pleated skirt, neat academy uniform, holding a small report folder at waist level',
        'note': '감찰 담당성 강조: 허리 높이 보고서 폴더, fake text 위험 확인 필요',
    },
]

def api_json(path: str, payload=None, timeout=20):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(ENDPOINT + path, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def wait_prompt(prompt_id: str, timeout=900):
    start = time.time()
    while time.time() - start < timeout:
        h = api_json('/history/' + prompt_id, timeout=20)
        if prompt_id in h:
            return h[prompt_id]
        time.sleep(2)
    raise TimeoutError(prompt_id)

def download_image(meta, dst: Path):
    q = urllib.parse.urlencode({'filename': meta['filename'], 'subfolder': meta.get('subfolder',''), 'type': meta.get('type','output')})
    with urllib.request.urlopen(ENDPOINT + '/view?' + q, timeout=60) as r:
        dst.write_bytes(r.read())

def make_sheet(images, sheet_path: Path):
    """Dependency-light contact sheet via ffmpeg."""
    cell_paths=[]
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    for label,path in images:
        cell=sheet_path.parent/f'_cell_{label}.png'
        vf=(
            "scale=320:426:force_original_aspect_ratio=decrease,"
            "pad=340:470:(ow-iw)/2:10:white,"
            f"drawtext=fontfile={font}:text='{label}':x=12:y=438:fontsize=28:fontcolor=black,"
            "drawbox=x=0:y=0:w=340:h=470:color=0x505050:t=2"
        )
        subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(path),'-vf',vf,str(cell)], check=True)
        cell_paths.append(cell)
    # 3 columns x 2 rows for six candidates.
    inputs=[]
    for p in cell_paths:
        inputs += ['-i', str(p)]
    layout='0_0|340_0|680_0|0_470|340_470|680_470'
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error',*inputs,'-filter_complex',f'xstack=inputs={len(cell_paths)}:layout={layout}:fill=0xE6E6E6',str(sheet_path)], check=True)
    for p in cell_paths:
        p.unlink(missing_ok=True)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    queue=api_json('/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise SystemExit('ComfyUI queue is not empty; aborting shared-server-safe generation')
    template=json.loads(TEMPLATE.read_text())
    derived_dir=OUT_DIR/'derived_workflows'
    derived_dir.mkdir(exist_ok=True)
    outputs=[]
    manifest={
        'run_id': RUN_ID,
        'status': 'candidate_generation_only_not_promoted',
        'endpoint': ENDPOINT,
        'base_template': str(TEMPLATE.relative_to(REPO)),
        'policy': 'Derived from workflow-pack 01; edited only prompt, seed, and output prefix. User selection required before alpha/RenPy promotion.',
        'global_prompt_rules': {
            'quality': QUALITY,
            'framing': FRAMING,
            'style': STYLE,
            'negative': BASE_NEG,
        },
        'candidates': [],
    }
    for c in CANDIDATES:
        wf=json.loads(json.dumps(template))
        positive=f"{QUALITY}, {FRAMING}, {c['design']}, {STYLE}"
        wf['3']['inputs']['text']=positive
        wf['4']['inputs']['text']=BASE_NEG
        wf['6']['inputs']['seed']=c['seed']
        prefix=f"hermes_vn_harin_tsundere_20260512/{c['id']}_harin_tsundere"
        wf['8']['inputs']['filename_prefix']=prefix
        derived=(derived_dir/f"{c['id']}_workflow.json")
        derived.write_text(json.dumps(wf, ensure_ascii=False, indent=2))
        resp=api_json('/prompt', {'prompt': wf, 'client_id': CLIENT_ID}, timeout=30)
        pid=resp['prompt_id']
        hist=wait_prompt(pid)
        imgs=[]
        for node_out in hist.get('outputs',{}).values():
            for im in node_out.get('images',[]):
                imgs.append(im)
        if not imgs:
            raise RuntimeError(f'no image output for {c["id"]}')
        local=OUT_DIR/f"{c['id']}_harin_tsundere.png"
        download_image(imgs[0], local)
        outputs.append((c['id'], local))
        manifest['candidates'].append({
            'id': c['id'], 'seed': c['seed'], 'note': c['note'], 'positive_prompt': positive, 'negative_prompt': BASE_NEG, 'derived_workflow': str(derived.relative_to(REPO)), 'local_path': str(local.relative_to(REPO)), 'comfy_output': imgs[0]
        })
    sheet=OUT_DIR/'harin_tsundere_contact_sheet.png'
    make_sheet(outputs, sheet)
    manifest['contact_sheet']=str(sheet.relative_to(REPO))
    (OUT_DIR/'RUN_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n")
    qa=OUT_DIR/'QA_NOTES.md'
    qa.write_text('# Harin cute-tsundere candidate QA\n\n상태: candidate only / not promoted\n\n사용자 요청: 기존 하린이 매력이 부족하므로 귀여운 츤데레 방향으로 디자인과 대사를 재정의하고 후보를 여러 장 생성.\n\nContact sheet:\n`'+str(sheet)+'`\n\n후보:\n' + ''.join([f"- {m['id']}: {m['note']} — `{OUT_DIR / (m['id'] + '_harin_tsundere.png')}`\n" for m in manifest['candidates']]) + '\n다음 게이트: 사용자가 후보를 고르면 workflow 02 toonout alpha → alpha 통계/dark/checker QA → RenPy semantic path promotion.\n')
    print(json.dumps({'run_dir': str(OUT_DIR), 'contact_sheet': str(sheet), 'manifest': str(OUT_DIR/'RUN_MANIFEST.json'), 'count': len(outputs)}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
