#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, time, urllib.request
from pathlib import Path
COMFY=Path('/mnt/c/Users/Desktop/Documents/ComfyUI')
ROOT=Path('/home/jisub-lee/workspace/vn-demo/workflow_packs/renpy_asset_workflows')
ENDPOINT='http://172.28.224.1:8000'
RUN='hermes_vn_02_after_reference_guided_multi_pose_20260513'
INDIR=COMFY/'input'/RUN
OUTDIR=COMFY/'output'/RUN
INDIR.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
BASE=ROOT/'02_toonout_transparency_alpha/workflow_api/02_alpha_toonout_b1_ref1_api.json'
SOURCES={
 'arms_crossed': COMFY/'output/hermes_vn_04_reference_guided_multi_pose_20260513/composite_arms_crossed_op100_canny35_d88_seed719255101_00001_.png',
 'hand_chest': COMFY/'output/hermes_vn_04_reference_guided_multi_pose_20260513/composite_hand_chest_op100_canny35_d86_seed719255102_00001_.png',
 'pointing': COMFY/'output/hermes_vn_04_reference_guided_multi_pose_20260513/composite_pointing_op100_canny30_d86_seed719255103_00001_.png',
}

def http_json(path,payload=None,timeout=30):
 data=None; headers={}
 if payload is not None:
  data=json.dumps(payload).encode(); headers['Content-Type']='application/json'
 with urllib.request.urlopen(urllib.request.Request(ENDPOINT+path,data=data,headers=headers),timeout=timeout) as r:
  raw=r.read().decode(); return json.loads(raw) if raw else {}

def submit(p,timeout_s=900):
 q=http_json('/queue',timeout=5)
 if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(q)
 pid=http_json('/prompt',{'prompt':p})['prompt_id']; start=time.time()
 while time.time()-start<timeout_s:
  h=http_json(f'/history/{pid}',timeout=30)
  if pid in h:
   st=h[pid].get('status',{})
   if not st.get('completed'): raise RuntimeError(st)
   return pid,h[pid]
  time.sleep(2)
 raise TimeoutError(pid)

def outputs(h):
 arr=[]
 for nid,node in h.get('outputs',{}).items():
  for img in node.get('images',[]): arr.append({'node':nid,'path':str(COMFY/'output'/(img.get('subfolder') or '')/img['filename'])})
 return arr

def make_composite(alpha_path:Path, color:str, dst:Path):
 # color e.g. white or black; overlay alpha image onto solid background.
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(alpha_path),'-f','lavfi','-i',f'color={color}:s=1152x1536','-filter_complex','[1:v][0:v]overlay=0:0:format=auto[out]','-map','[out]','-frames:v','1',str(dst)],check=True)

def contact(files, dst):
 inputs=[]; filters=[]
 for i,f in enumerate(files):
  inputs+=['-i',str(f)]
  filters.append(f'[{i}:v]scale=288:384:force_original_aspect_ratio=decrease,pad=288:384:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[v{i}]')
 cols=3; n=len(files)
 while n%cols:
  filters.append(f'color=white:s=288x384:d=0.1,setsar=1[v{n}]'); n+=1
 layout='|'.join(f'{(i%cols)*288}_{(i//cols)*384}' for i in range(n))
 filt=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout={layout}[out]'
 subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',filt,'-map','[out]','-frames:v','1',str(dst)],check=True)

def main():
 base=json.loads(BASE.read_text(encoding='utf-8'))
 manifest={'run':RUN,'purpose':'02 alpha smoke for reference-guided 04 multi-pose outputs. Includes white/black composite previews.','variants':[]}
 preview_files=[]
 for pose,src in SOURCES.items():
  local=INDIR/f'{pose}_source.png'; shutil.copy2(src,local)
  p=json.loads(json.dumps(base))
  p['1']['inputs']['image']=f'{RUN}/{pose}_source.png'
  p['3']['inputs']['filename_prefix']=f'{RUN}/alpha_{pose}'
  wf=ROOT/'00_experiment_sandbox/workflow_api'/f'00_02_after_reference_guided_{pose}_api.json'
  wf.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
  pid,h=submit(p); outs=outputs(h); alpha=Path([o['path'] for o in outs if o['node']=='3'][0])
  white=OUTDIR/f'preview_{pose}_white.png'; black=OUTDIR/f'preview_{pose}_black.png'
  make_composite(alpha,'white',white); make_composite(alpha,'black',black)
  preview_files += [src, white, black]
  manifest['variants'].append({'pose':pose,'source':str(src),'prompt_id':pid,'workflow_api':str(wf),'alpha':str(alpha),'white_preview':str(white),'black_preview':str(black),'outputs':outs})
 contact_path=OUTDIR/'contact_02_after_reference_guided_multi_pose.png'
 contact(preview_files, contact_path)
 manifest['contact_sheet']=str(contact_path)
 mp=OUTDIR/'manifest_02_after_reference_guided_multi_pose.json'
 mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
