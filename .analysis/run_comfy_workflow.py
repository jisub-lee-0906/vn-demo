#!/usr/bin/env python3
import json, os, sys, time, uuid, shutil, urllib.request
from pathlib import Path

ENDPOINT=os.environ.get('COMFY_ENDPOINT','http://172.28.224.1:8000').rstrip('/')
CLIENT_ID='hermes-vn-'+str(uuid.uuid4())
OUT_ROOT=Path('/mnt/c/Users/Desktop/Documents/ComfyUI/output')
IN_ROOT=Path('/mnt/c/Users/Desktop/Documents/ComfyUI/input')

def api(path, data=None):
    if data is not None:
        b=json.dumps(data).encode('utf-8')
        req=urllib.request.Request(ENDPOINT+path, data=b, headers={'Content-Type':'application/json'})
    else:
        req=urllib.request.Request(ENDPOINT+path)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

def wait_idle():
    q=api('/queue')
    running=q.get('queue_running') or []
    pending=q.get('queue_pending') or []
    if running or pending:
        print('queue not empty:', len(running), 'running', len(pending), 'pending')
    return q

def submit(prompt):
    res=api('/prompt', {'prompt': prompt, 'client_id': CLIENT_ID})
    pid=res['prompt_id']
    print('prompt_id',pid)
    start=time.time()
    while time.time()-start < 1200:
        h=api('/history/'+pid)
        if pid in h:
            item=h[pid]
            outs=[]
            for node,out in item.get('outputs',{}).items():
                for im in out.get('images',[]):
                    folder=im.get('subfolder') or ''
                    fname=im['filename']
                    typ=im.get('type','output')
                    root=OUT_ROOT if typ=='output' else IN_ROOT
                    outs.append(str(root/folder/fname))
            print('\n'.join(outs))
            return pid, outs
        time.sleep(2)
    raise TimeoutError(pid)

if __name__=='__main__':
    prompt=json.load(open(sys.argv[1],encoding='utf-8'))
    wait_idle()
    pid, outs=submit(prompt)
    if len(sys.argv)>2:
        Path(sys.argv[2]).write_text(json.dumps({'prompt_id':pid,'outputs':outs},indent=2),encoding='utf-8')
