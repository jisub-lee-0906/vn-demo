#!/usr/bin/env python3
import json, shutil, time, urllib.request, uuid
from pathlib import Path

BASE='http://172.28.224.1:8001'
REPO=Path('/home/jisub-lee/workspace/vn-demo')
WF=REPO/'workflow_packs/renpy_asset_workflows/outfit_variations/outfit_variations_workflow_api.json'
OUT_DIR=Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')
INPUT_DIR=Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input')
SRC=OUT_DIR/'hermes_vn_character_anchor/source_featureless_mannequin_base_seed719251139_00001_.png'
RUNTIME_DIR=REPO/'.analysis/comfyui_runtime/outfit_variations_test4_anchor_prompt'
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
(INPUT_DIR/'hermes_runtime').mkdir(parents=True, exist_ok=True)
input_name='hermes_runtime/source_featureless_mannequin_base_seed719251139_test4.png'
input_path=INPUT_DIR/input_name
if not input_path.exists():
    shutil.copy2(SRC, input_path)

with WF.open('r', encoding='utf-8') as f:
    base_prompt=json.load(f)

# Exact identity tokens recovered from the PNG metadata of the anchor image:
# shoulder_length_hair, straight_hair, dark_brown_hair, amber_eyes
anchor_identity = 'shoulder_length_hair, straight_hair, dark_brown_hair, amber_eyes'
positive_text = (
    'masterpiece, best quality, amazing quality, 4k, very aesthetic, high resolution, ultra-detailed, absurdres, newest, '
    '1girl, solo, medium_breasts, cowboy_shot, standing, front_view, looking_at_viewer, expressionless, closed_mouth, '
    'arms_at_sides, straight_posture, '
    + anchor_identity + ', '
    'fully clothed, Japanese school uniform, sailor collar, white blouse, navy pleated skirt, red neck ribbon, '
    'long sleeves, knee socks, loafers, coordinated_outfit, highly detailed clothes, opaque clothing, cloth folds, grey_background'
)
negative_text = (
    'nude, nipples, bare chest, bare torso, see-through, transparent clothes, body paint, painted clothes, swimsuit, underwear, '
    'pink hair, twin braids, twintails, braided hair, different hairstyle, changed hairstyle, different hair color, changed hair color, '
    'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, '
    'disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra digits, fewer digits, cropped, very displeasing, sketch, '
    'jpeg artifacts, signature, watermark, username, conjoined, bad ai-generated, (worst quality, bad quality:1.2), vignette, shadow, depth of field, rim lighting'
)

def post_json(path, payload):
    data=json.dumps(payload).encode('utf-8')
    req=urllib.request.Request(BASE+path, data=data, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

def get_json(path):
    with urllib.request.urlopen(BASE+path, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

def make_prompt(label, body_expand, alpha_cap_expand, denoise, seed):
    p=json.loads(json.dumps(base_prompt))
    p['3']['inputs']['image']=input_name
    p['8']['inputs']['text_input']='head, hair, face'
    p['16']['inputs']['expand']=body_expand
    p['23']['inputs']['text']=positive_text
    p['24']['inputs']['text']=negative_text
    p['27']['inputs']['seed']=seed
    p['27']['inputs']['denoise']=denoise
    p['35']['inputs']['filename_prefix']=f'hermes_vn_outfit_variation/test4_anchorprompt_{label}_school_uniform_seed{seed}'
    # keep round2 mask correction: body edit capped by slightly expanded alpha.
    p['954']={'class_type':'GrowMask','inputs':{'mask':['4',1],'expand':alpha_cap_expand,'tapered_corners':True}}
    p['955']={'class_type':'ImpactGaussianBlurMask','inputs':{'mask':['954',0],'kernel_size':7,'sigma':3.0}}
    p['18']['inputs']['destination']=['17',0]
    p['18']['inputs']['source']=['955',0]
    p['18']['inputs']['operation']='multiply'
    p['53']['inputs']['mask1']=['18',0]
    p['53']['inputs']['mask2']=['8',1]
    # QA previews
    p['950']={'class_type':'MaskToImage','inputs':{'mask':['53',0]}}
    p['951']={'class_type':'SaveImage','inputs':{'images':['950',0],'filename_prefix':f'hermes_vn_outfit_variation/test4_anchorprompt_{label}_editmask_seed{seed}'}}
    p['952']={'class_type':'MaskToImage','inputs':{'mask':['8',1]}}
    p['953']={'class_type':'SaveImage','inputs':{'images':['952',0],'filename_prefix':f'hermes_vn_outfit_variation/test4_anchorprompt_{label}_protect_headhair_seed{seed}'}}
    p['956']={'class_type':'MaskToImage','inputs':{'mask':['955',0]}}
    p['957']={'class_type':'SaveImage','inputs':{'images':['956',0],'filename_prefix':f'hermes_vn_outfit_variation/test4_anchorprompt_{label}_expanded_alpha_cap_seed{seed}'}}
    return p

def queue_and_wait(prompt,label):
    resp=post_json('/prompt', {'prompt':prompt,'client_id':'hermes-vn-test4-anchorprompt-'+uuid.uuid4().hex})
    pid=resp['prompt_id']
    print(f'QUEUED {label} prompt_id={pid}', flush=True)
    start=time.time()
    while True:
        hist=get_json('/history/'+pid)
        if pid in hist:
            item=hist[pid]
            status=item.get('status',{})
            print(f'DONE {label} status={status}', flush=True)
            outputs=[]
            for node_id,node_out in item.get('outputs',{}).items():
                for im in node_out.get('images',[]):
                    root=OUT_DIR if (im.get('type') or 'output')=='output' else INPUT_DIR
                    outputs.append(str(root/(im.get('subfolder') or '')/im.get('filename')))
            return pid, outputs, status
        if time.time()-start>900:
            raise TimeoutError(pid)
        time.sleep(2)

runs=[
    ('E_anchorid_body08_alphacap06_den092',8,6,0.92,62019321),
    ('F_anchorid_body08_alphacap06_den100',8,6,1.0,62019322),
]
summary={'source_anchor':str(SRC),'anchor_metadata_identity':anchor_identity,'input_copy':str(input_path),'workflow_source':str(WF),'positive_text':positive_text,'negative_text':negative_text,'runs':[]}
for label,be,ace,den,seed in runs:
    prompt=make_prompt(label,be,ace,den,seed)
    runtime_json=RUNTIME_DIR/f'{label}.json'
    runtime_json.write_text(json.dumps(prompt,indent=2,ensure_ascii=False),encoding='utf-8')
    pid,outputs,status=queue_and_wait(prompt,label)
    summary['runs'].append({'label':label,'body_expand':be,'alpha_cap_expand':ace,'denoise':den,'seed':seed,'prompt_id':pid,'runtime_json':str(runtime_json),'outputs':outputs,'status':status})
summary_path=RUNTIME_DIR/'run_summary.json'
summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print('\nSUMMARY_JSON')
print(json.dumps(summary,indent=2,ensure_ascii=False))
