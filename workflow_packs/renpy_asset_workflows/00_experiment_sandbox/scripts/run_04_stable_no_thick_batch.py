#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request, shutil
from pathlib import Path
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ENDPOINT='http://172.28.224.1:8000'
CHAR_TAGS='short_hair, bob_cut, silver_hair, blue_eyes, beige_cardigan, white_shirt, blue_bowtie, navy_skirt, pleated_skirt, black_pantyhose, long_sleeves, small_breasts'
BASE_STYLE='clean_lineart, anime_coloring, grey_background'
POSES=[
 ('arms_crossed','hermes_pose_ref_silver_bob_arms_crossed.png','arms_crossed, crossed_arms, folded_arms','hands_on_hips, hands_in_pockets, hands_near_face, hand_on_chest, arms_relaxed',719252511),
 ('hand_chest','hermes_pose_ref_multi04b_silver_bob_hand_chest.png','hand_on_chest, hand_to_own_chest, hands_near_chest','arms_crossed, crossed_arms, folded_arms, hands_on_hips, hands_in_pockets, hands_near_face',719252513),
]

def http_json(path,payload=None,timeout=30):
 data=None; headers={}
 if payload is not None:
  data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
 with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
  raw=r.read().decode(); return json.loads(raw) if raw else {}

def submit(prompt,timeout_s=900):
 q=http_json('/queue',timeout=5)
 if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(f'queue busy {q}')
 pid=http_json('/prompt',{'prompt':prompt})['prompt_id']; start=time.time()
 while time.time()-start<timeout_s:
  h=http_json(f'/history/{pid}',timeout=30)
  if pid in h:
   st=h[pid].get('status',{})
   if not st.get('completed'): raise RuntimeError(f'failed {pid} {st}')
   return pid,h[pid]
  time.sleep(2)
 raise TimeoutError(pid)

def outs(h):
 out=[]
 for node in h.get('outputs',{}).values():
  for img in node.get('images',[]): out.append(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])
 return out

def run(slug, pose_ref, pose_tags, pose_neg, seed):
 p=json.loads((ROOT/'04_pose_variation_reference_and_regeneration/workflow_api/04_pose_refregen_openpose_ipadapter_masked_canonical_api.json').read_text())
 p['4']['inputs']['image']='hermes_identity_silver_bob_anchor_v190.png'; p['5']['inputs']['image']=pose_ref
 p['2']['inputs']['text']='masterpiece, best_quality, very_aesthetic, newest, rating_explicit, 1girl, solo, cowboy_shot, standing, looking_at_viewer, '+CHAR_TAGS+', '+pose_tags+', '+BASE_STYLE
 p['3']['inputs']['text']=p['3']['inputs']['text'].replace('TEMPLATE_EXPRESSION_CONFLICT_NEGATIVES','smile, open_mouth').replace('TEMPLATE_POSE_CONFLICT_NEGATIVES',pose_neg)
 p['14']['inputs']['seed']=seed
 prefix=f'hermes_vn_chain_retest_20260513/no_thick_{slug}'
 p['16']['inputs']['filename_prefix']=prefix+'_src'; p['17']['inputs']['filename_prefix']=prefix+'_control'
 pid04,h04=submit(p); op=outs(h04); src=[x for x in op if prefix+'_src' in str(x)][0]; ctrl=[x for x in op if prefix+'_control' in str(x)][0]
 rel=f'hermes_vn_chain_retest_20260513/no_thick_{slug}_src.png'; ip=COMFY/'input'/rel; ip.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,ip)
 a=json.loads((ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json').read_text())
 a['1']['inputs']['image']=rel; a['3']['inputs']['filename_prefix']=prefix+'_alpha_b1_ref1'
 pid02,h02=submit(a); alpha=[x for x in outs(h02) if prefix+'_alpha_b1_ref1' in str(x)][0]
 return {'slug':slug,'seed':seed,'04_prompt_id':pid04,'02_prompt_id':pid02,'04_source':str(src),'04_control':str(ctrl),'02_alpha':str(alpha),'04_positive':p['2']['inputs']['text']}
res=[run(*x) for x in POSES]
mp=COMFY/'output/hermes_vn_chain_retest_20260513/manifest_no_thick_stable_batch.json'
mp.write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(res,indent=2,ensure_ascii=False))
