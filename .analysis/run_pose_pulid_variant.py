#!/usr/bin/env python3
import json, time, urllib.request, uuid
from pathlib import Path
BASE='http://172.28.224.1:8001'
REPO=Path('/home/jisub-lee/workspace/vn-demo')
WF=REPO/'workflow_packs/renpy_asset_workflows/pose_variations/pose_variations_workflow_api.json'
OUT=Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')
RUNTIME=REPO/'.analysis/comfyui_runtime/pose_variations_crossed_arms_20260516'
RUNTIME.mkdir(parents=True, exist_ok=True)
w=json.loads(WF.read_text())
# PuLID + empty latent variant: stronger pose freedom, still uses source outfit image as identity reference.
w['13']={'class_type':'PulidModelLoader','inputs':{'pulid_file':'ip-adapter_pulid_sdxl_fp16.safetensors'},'_meta':{'title':'PuLID identity model'}}
w['14']={'class_type':'PulidEvaClipLoader','inputs':{},'_meta':{'title':'PuLID EVA CLIP'}}
w['15']={'class_type':'PulidInsightFaceLoader','inputs':{'provider':'CPU'},'_meta':{'title':'PuLID face analysis'}}
w['16']={'class_type':'ApplyPulidAdvanced','inputs':{'model':['1',0],'pulid':['13',0],'eva_clip':['14',0],'face_analysis':['15',0],'image':['2',0],'weight':0.85,'projection':'ortho_v2','fidelity':8,'noise':0.0,'start_at':0.0,'end_at':0.75},'_meta':{'title':'apply source face identity'}}
w['17']={'class_type':'EmptyLatentImage','inputs':{'width':1152,'height':1536,'batch_size':1},'_meta':{'title':'free latent for pose change'}}
w['9']['inputs']['model']=['16',0]
w['9']['inputs']['latent_image']=['17',0]
w['9']['inputs']['seed']=73051002
w['9']['inputs']['denoise']=1.0
w['7']['inputs']['strength']=1.35
w['7']['inputs']['end_percent']=0.9
w['11']['inputs']['filename_prefix']='hermes_vn_pose_variation/crossed_arms_controlnet_pulid_seed73051002'
obj=json.loads(urllib.request.urlopen(f'{BASE}/object_info',timeout=30).read().decode())
missing=sorted({v['class_type'] for v in w.values()}-set(obj))
if missing: raise SystemExit(f'missing {missing}')
rp=RUNTIME/'pose_variations_crossed_arms_pulid_payload.json'
rp.write_text(json.dumps(w,indent=2,ensure_ascii=False)+'\n')
pid=str(uuid.uuid4())
req=urllib.request.Request(f'{BASE}/prompt',data=json.dumps({'prompt':w,'client_id':pid}).encode(),headers={'Content-Type':'application/json'})
prompt_id=json.loads(urllib.request.urlopen(req,timeout=30).read().decode())['prompt_id']
for _ in range(600):
 hist=json.loads(urllib.request.urlopen(f'{BASE}/history/{prompt_id}',timeout=30).read().decode())
 if prompt_id in hist:
  saved=[]
  for node_id,out in hist[prompt_id].get('outputs',{}).items():
   for img in out.get('images',[]):
    saved.append(str(OUT/(img.get('subfolder') or '')/img['filename']))
  summary={'prompt_id':prompt_id,'status':hist[prompt_id].get('status',{}),'runtime_payload':str(rp),'saved_outputs':saved,'variant':'pulid_empty_latent_pose_control'}
  (RUNTIME/'run_summary_pulid.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
  print(json.dumps(summary,ensure_ascii=False))
  break
 time.sleep(1)
else: raise SystemExit('timeout')
