#!/usr/bin/env python3
import json, shutil, time, urllib.request, uuid
from pathlib import Path

BASE = 'http://172.28.224.1:8001'
REPO = Path('/home/jisub-lee/workspace/vn-demo')
PACK = REPO / 'workflow_packs/renpy_asset_workflows'
POSE_DIR = PACK / 'pose_variations'
WF_PATH = POSE_DIR / 'pose_variations_workflow_api.json'
INPUT_DIR = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input')
OUT_DIR = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')
RUNTIME_DIR = REPO / '.analysis/comfyui_runtime/pose_variations_crossed_arms_20260516'
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_OUTFIT = Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_outfit_variation/test4_anchorprompt_E_anchorid_body08_alphacap06_den092_school_uniform_seed62019321_00001_.png')
SOURCE_INPUT_REL = 'hermes_vn_pose/source_school_uniform_test4E.png'
POSE_INPUT_REL = 'hermes_vn_pose/pose_crossed_arms_openpose_1152x1536.png'

# Copy outfit source into ComfyUI input, preserving generated outputs outside repo pack.
(INPUT_DIR / 'hermes_vn_pose').mkdir(parents=True, exist_ok=True)
shutil.copy2(SOURCE_OUTFIT, INPUT_DIR / SOURCE_INPUT_REL)

# Create a simple OpenPose-style crossed-arms guide. This is intentionally outside the README/canonical docs.
def make_pose(path: Path, w=1152, h=1536):
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (w, h), (0, 0, 0))
    d = ImageDraw.Draw(img)
    # approximate upper-body COCO keypoints in source character framing
    pts = {
        'nose': (576, 290),
        'neck': (576, 430),
        'r_shoulder': (455, 500),
        'r_elbow': (625, 670),
        'r_wrist': (760, 625),
        'l_shoulder': (700, 500),
        'l_elbow': (525, 680),
        'l_wrist': (390, 625),
        'r_hip': (500, 870),
        'l_hip': (655, 870),
        'r_eye': (535, 270),
        'l_eye': (615, 270),
        'r_ear': (490, 285),
        'l_ear': (665, 285),
    }
    # OpenPose-ish limb colors (not exact-critical for controlnet)
    limbs = [
        ('neck','r_shoulder',(255,0,0)), ('neck','l_shoulder',(255,85,0)),
        ('r_shoulder','r_elbow',(255,170,0)), ('r_elbow','r_wrist',(255,255,0)),
        ('l_shoulder','l_elbow',(170,255,0)), ('l_elbow','l_wrist',(85,255,0)),
        ('neck','r_hip',(0,255,85)), ('neck','l_hip',(0,255,170)),
        ('r_hip','l_hip',(0,255,255)), ('nose','neck',(0,170,255)),
        ('nose','r_eye',(0,85,255)), ('r_eye','r_ear',(0,0,255)),
        ('nose','l_eye',(85,0,255)), ('l_eye','l_ear',(170,0,255)),
    ]
    for a,b,c in limbs:
        d.line([pts[a], pts[b]], fill=c, width=18)
    for name, p in pts.items():
        d.ellipse((p[0]-13,p[1]-13,p[0]+13,p[1]+13), fill=(255,255,255))
    # faint torso guide only, not a filled mask
    d.line([(455,500),(700,500),(655,870),(500,870),(455,500)], fill=(80,80,80), width=5)
    img.save(path)

try:
    from PIL import Image  # noqa
except Exception:
    raise SystemExit('Pillow is required; run this script via: uv run --with pillow python .analysis/create_pose_workflow_and_test.py')
make_pose(INPUT_DIR / POSE_INPUT_REL)

positive = (
    'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, '
    '1girl, solo, medium_breasts, cowboy_shot, front_view, looking_at_viewer, expressionless, closed_mouth, '
    'long brown hair, straight hair, blunt bangs, brown hair, amber eyes, fully_clothed, '
    'school_uniform, serafuku, white_shirt, long_sleeves, sailor_collar, red_ribbon, pleated_skirt, beige_skirt, '
    'crossed_arms, arms_crossed, highly_detailed, grey_background'
)
negative = (
    'nude, nipples, nsfw, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, '
    'glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, '
    'extra_digits, fewer_digits, different_face, different_hair, different_hairstyle, different_eye_color, changed_face, '
    'changed_hair, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, '
    'bad_ai-generated, (worst_quality, bad_quality:1.2), vignette, shadow, depth_of_field, rim_lighting, '
    'arms_at_sides, hands_on_hips, reaching_out'
)

workflow = {
  '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'novaAnimeXL_ilV190.safetensors'}},
  '2': {'class_type': 'LoadImage', 'inputs': {'image': SOURCE_INPUT_REL}, '_meta': {'title': 'source outfit character image'}},
  '3': {'class_type': 'LoadImage', 'inputs': {'image': POSE_INPUT_REL}, '_meta': {'title': 'pose control image / OpenPose-style guide'}},
  '4': {'class_type': 'ControlNetLoader', 'inputs': {'control_net_name': 'noobaiXLControlnet_openposeModel.safetensors'}, '_meta': {'title': 'SDXL OpenPose ControlNet'}},
  '5': {'class_type': 'CLIPTextEncode', 'inputs': {'text': positive, 'clip': ['1', 1]}},
  '6': {'class_type': 'CLIPTextEncode', 'inputs': {'text': negative, 'clip': ['1', 1]}},
  '7': {'class_type': 'ControlNetApplyAdvanced', 'inputs': {'positive': ['5', 0], 'negative': ['6', 0], 'control_net': ['4', 0], 'image': ['3', 0], 'strength': 1.15, 'start_percent': 0.0, 'end_percent': 0.82}, '_meta': {'title': 'apply pose control'}},
  '8': {'class_type': 'VAEEncode', 'inputs': {'pixels': ['2', 0], 'vae': ['1', 2]}},
  '9': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'seed': 73051001, 'steps': 30, 'cfg': 4.8, 'sampler_name': 'euler_ancestral', 'scheduler': 'normal', 'positive': ['7', 0], 'negative': ['7', 1], 'latent_image': ['8', 0], 'denoise': 0.78}},
  '10': {'class_type': 'VAEDecode', 'inputs': {'samples': ['9', 0], 'vae': ['1', 2]}},
  '11': {'class_type': 'SaveImage', 'inputs': {'images': ['10', 0], 'filename_prefix': 'hermes_vn_pose_variation/crossed_arms_controlnet_seed73051001'}, '_meta': {'title': 'save pose variation'}},
  '12': {'class_type': 'SaveImage', 'inputs': {'images': ['3', 0], 'filename_prefix': 'hermes_vn_pose_variation/poseguide_crossed_arms_openpose'}, '_meta': {'title': 'save pose guide copy'}}
}
POSE_DIR.mkdir(parents=True, exist_ok=True)
WF_PATH.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

# Validate classes against live ComfyUI before submit.
obj = json.loads(urllib.request.urlopen(f'{BASE}/object_info', timeout=30).read().decode())
missing = sorted({v['class_type'] for v in workflow.values()} - set(obj))
if missing:
    raise SystemExit(f'missing classes: {missing}')

runtime_path = RUNTIME_DIR / 'pose_variations_crossed_arms_payload.json'
runtime_path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

pid = str(uuid.uuid4())
req = urllib.request.Request(
    f'{BASE}/prompt',
    data=json.dumps({'prompt': workflow, 'client_id': pid}).encode(),
    headers={'Content-Type': 'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
prompt_id = resp['prompt_id']

# Wait for completion.
for _ in range(360):
    hist = json.loads(urllib.request.urlopen(f'{BASE}/history/{prompt_id}', timeout=30).read().decode())
    if prompt_id in hist:
        status = hist[prompt_id].get('status', {})
        outputs = hist[prompt_id].get('outputs', {})
        saved = []
        for node_id, out in outputs.items():
            for img in out.get('images', []):
                sub = img.get('subfolder') or ''
                saved.append(str(OUT_DIR / sub / img['filename']))
        summary = {
            'prompt_id': prompt_id,
            'status': status,
            'source_input': str(INPUT_DIR / SOURCE_INPUT_REL),
            'pose_input': str(INPUT_DIR / POSE_INPUT_REL),
            'canonical_workflow': str(WF_PATH),
            'runtime_payload': str(runtime_path),
            'saved_outputs': saved,
            'parameters': {
                'pose': 'crossed_arms',
                'controlnet': 'noobaiXLControlnet_openposeModel.safetensors',
                'control_strength': 1.15,
                'control_end_percent': 0.82,
                'denoise': 0.78,
                'seed': 73051001
            }
        }
        (RUNTIME_DIR / 'run_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps(summary, ensure_ascii=False))
        break
    time.sleep(1)
else:
    raise SystemExit('timeout waiting for ComfyUI history')
