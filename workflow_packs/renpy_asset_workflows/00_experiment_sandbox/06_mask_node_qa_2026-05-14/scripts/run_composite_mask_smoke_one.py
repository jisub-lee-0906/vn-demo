#!/usr/bin/env python3
import argparse, json, pathlib, subprocess, time, urllib.request

def post(endpoint, prompt):
    req=urllib.request.Request(endpoint.rstrip()+'/prompt', data=json.dumps({'prompt':prompt}).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)['prompt_id']

def history(endpoint, pid):
    with urllib.request.urlopen(endpoint.rstrip()+'/history/'+pid, timeout=30) as r: return json.load(r)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--endpoint')
    ap.add_argument('--template', required=True)
    ap.add_argument('--slug', required=True)
    ap.add_argument('--image', required=True)
    ap.add_argument('--timeout', type=int, default=900)
    args=ap.parse_args()
    if not args.endpoint:
        ip=subprocess.check_output("ip route | awk '/default/ {print $3; exit}'", shell=True, text=True).strip()
        args.endpoint=f'http://{ip}:8000'
    prompt=json.loads(pathlib.Path(args.template).read_text())
    prompt['3']['inputs']['image']=args.image
    for node in prompt.values():
        if node.get('class_type')=='SaveImage':
            pref=node['inputs']['filename_prefix']
            pref=pref.replace('TEMPLATE_character_slug', args.slug).replace('TEMPLATE_preset_slug','bypasssource').replace('TEMPLATE_seed','62019146')
            node['inputs']['filename_prefix']=pref
    pid=post(args.endpoint, prompt)
    print(f'prompt_id={pid}')
    start=time.time()
    while time.time()-start<args.timeout:
        h=history(args.endpoint, pid)
        if pid in h:
            print(json.dumps(h[pid].get('status',{}), ensure_ascii=False))
            return 0 if h[pid].get('status',{}).get('completed') else 1
        time.sleep(3)
    print('TIMEOUT')
    return 2
if __name__=='__main__': raise SystemExit(main())
