#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import regenerate_visual_assets_canonical_reset as base

RUN_ID = os.environ.get('RUN_ID') or 'canonical_reset_20260512_211728'
base.RUN_ID = RUN_ID
base.OUT = ROOT/'generated'/'comfyui'/RUN_ID
QUALITY = base.QUALITY
BG_NEG = base.BG_NEG_BASE

jobs = [
    base.Txt2ImgJob(
        'bg_report_room_refine', '06_background_generation_no_text_api.json', '06_background_generation_no_text',
        'empty anime headmaster office, no people, clean lower third, wide 16:9 interior background, formal academy office, large wooden desk at the back, warm lamps, dark wood walls, bookshelves as color blocks without titles, official academy crest shape without letters, quiet serious room, no classroom, no blackboard',
        BG_NEG + ', classroom, blackboard, chalkboard, school desks, students, readable book titles, letters on books, signs, posters',
        (812345541,812345542,812345543,812345544), 1024, 576, 26, 5.5, 'novaAnimeXL_ilV180.safetensors', 'bg_report_room_refine'
    ),
    base.Txt2ImgJob(
        'cg_special_observation_seal_refine', '08_event_cg_no_text_story_beat_api.json', '08_event_cg_no_text_story_beat',
        f'{QUALITY}, anime event CG, close-up of a blank parchment folder on a wooden desk, red wax seal and small gold academy crest medallion, official decision mood, warm lamplight, no letters, no readable writing, no people, no hands, 16:9 background art, large empty clean foreground in the bottom third for dialogue box',
        BG_NEG + ', fake glyphs, handwriting, printed lines, readable document, Korean text, English text, label, stamp letters, people, person, girl, boy, face, hand, fingers, silhouette, humanoid figure, black figure, waiter, butler, blood',
        (812347841,812347842,812347843,812347844), 1536, 864, 30, 5.5, 'novaAnimeXL_ilV180.safetensors', 'cg_special_observation_seal_refine'
    ),
]

def main():
    h=base.host(); print('host',h,'run',base.OUT)
    q=base.http_json('GET', f'{h}/queue', timeout=10)
    if q.get('queue_running') or q.get('queue_pending'):
        raise SystemExit(f'queue not empty: {q}')
    manifest_path=base.OUT/'RUN_MANIFEST.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    for job in jobs:
        files=[]; apis=[]; pids=[]
        for idx,seed in enumerate(job.seeds,1):
            wf=base.apply_txt2img(job,seed,idx)
            api_path=base.OUT/'api_workflows'/f'{job.asset_id}_s{idx:02d}_derived_from_{job.workflow_id}.json'
            api_path.write_text(json.dumps(wf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            apis.append(str(api_path.relative_to(ROOT)))
            print('submit',job.asset_id,seed)
            r=base.http_json('POST', f'{h}/prompt', {'prompt':wf,'client_id':base.uuid4().__str__()}, timeout=30)
            pid=r['prompt_id']; pids.append(pid)
            hist=base.wait_history(h,pid)
            files.extend(base.download_outputs(h,hist,base.OUT/job.asset_id))
        sheet=base.OUT/'contact_sheets'/f'{job.asset_id}_sheet.jpg'
        base.contact_sheet(files,sheet)
        manifest['jobs'].append({'asset_id':job.asset_id,'template':job.template,'workflow_id':job.workflow_id,'seeds':list(job.seeds),'prompt_ids':pids,'positive':job.positive,'negative':job.negative,'api_workflows':apis,'files':[str(p.relative_to(ROOT)) for p in files],'contact_sheet':str(sheet.relative_to(ROOT))})
        print('done',job.asset_id,len(files),sheet)
    manifest['status']='GENERATED_CANDIDATES_WITH_REFINES_PENDING_SELECTION'
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(manifest_path)
if __name__=='__main__': main()
