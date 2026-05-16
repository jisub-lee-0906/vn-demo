#!/usr/bin/env python3
"""Dry-run or execute minimal ComfyUI smoke tests for this workflow pack.

This pack is edited from WSL, while the active ComfyUI Desktop backend on this
machine listens on Windows-local http://127.0.0.1:8000. WSL's own urllib cannot
reach that Windows localhost directly on some setups, so this script falls back
to Windows `cmd.exe /c curl` for localhost endpoints when running under WSL.
"""
from __future__ import annotations
import argparse, json, os, subprocess, tempfile, time, urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "WORKFLOW_INDEX.json"
WIN_COMFY_INPUT = Path("/mnt/c/Users/Desktop/Documents/ComfyUI/input")


def in_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return False


def is_windows_localhost(endpoint: str) -> bool:
    host = urlparse(endpoint).hostname or ""
    return host in {"127.0.0.1", "localhost"}


def wsl_to_win_path(path: Path) -> str:
    s = str(path.resolve())
    if s.startswith("/mnt/") and len(s) > 6:
        drive = s[5].upper()
        rest = s[7:].replace("/", "\\")
        return f"{drive}:\\{rest}"
    return s


def cmd_curl_json(endpoint: str, path: str, payload=None, timeout=10):
    url = endpoint.rstrip("/") + path
    args = ["cmd.exe", "/c", "curl", "-sS", "-m", str(timeout)]
    tmp_path = None
    if payload is not None:
        WIN_COMFY_INPUT.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix="workflow_smoke_", suffix=".json", dir=str(WIN_COMFY_INPUT))
        tmp_path = Path(tmp_name)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        args += ["-X", "POST", "-H", "Content-Type: application/json", "--data-binary", "@" + wsl_to_win_path(tmp_path)]
    args.append(url)
    try:
        p = subprocess.run(args, cwd="/mnt/c/Users/Desktop", capture_output=True, timeout=timeout + 5)
        out = p.stdout.decode("utf-8", "replace")
        err = p.stderr.decode("utf-8", "replace")
        if p.returncode != 0:
            raise RuntimeError(f"cmd curl failed {p.returncode}: {err}\n{out}")
        first = min([i for i in [out.find("{"), out.find("[")] if i >= 0] or [0])
        raw = out[first:]
        return json.loads(raw) if raw else {}
    finally:
        if tmp_path:
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass


def http_json(endpoint: str, path: str, payload=None, timeout=10):
    url = endpoint.rstrip("/") + path
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except Exception:
        if in_wsl() and is_windows_localhost(endpoint):
            return cmd_curl_json(endpoint, path, payload=payload, timeout=timeout)
        raise


def load_templates():
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    templates=[]
    for wf in data.get("workflows", []):
        for t in wf.get("api_templates", []):
            t=dict(t); t["workflow"]=wf["folder"]
            p=ROOT/t["path"]
            if not p.exists(): raise FileNotFoundError(t["path"])
            json.loads(p.read_text(encoding="utf-8"))
            templates.append(t)
    return templates


def select(templates, workflow=None, all_templates=False):
    if workflow:
        prefixes=tuple(x.strip() for x in workflow.split(",") if x.strip())
        templates=[t for t in templates if t["workflow"].startswith(prefixes)]
    if all_templates: return templates
    seen=set(); out=[]
    for t in templates:
        if t["workflow"] not in seen:
            out.append(t); seen.add(t["workflow"])
    return out


def busy(queue):
    return bool(queue.get("queue_running") or queue.get("queue_pending")), len(queue.get("queue_running") or []), len(queue.get("queue_pending") or [])


def run_prompt(endpoint, t, timeout_s):
    prompt=json.loads((ROOT/t["path"]).read_text(encoding="utf-8"))
    resp=http_json(endpoint,"/prompt",{"prompt":prompt},timeout=30)
    pid=resp.get("prompt_id")
    if not pid: return False, f"no prompt_id: {resp}"
    start=time.time()
    while time.time()-start < timeout_s:
        hist=http_json(endpoint,f"/history/{pid}",timeout=30)
        if pid in hist:
            status=hist[pid].get("status",{})
            return bool(status.get("completed")), f"prompt_id={pid} status={status}"
        time.sleep(2)
    return False, f"timeout prompt_id={pid}"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8000")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--all", dest="all_templates", action="store_true")
    ap.add_argument("--one-per-workflow", action="store_true")
    ap.add_argument("--workflow", help="prefix list like 01 or 03,05")
    ap.add_argument("--allow-busy", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    args=ap.parse_args()
    templates=load_templates(); selected=select(templates,args.workflow,args.all_templates)
    print(f"INDEX_OK templates={len(templates)} selected={len(selected)} execute={args.execute}")
    for t in selected: print(f"SELECT {t['workflow']} :: {t['path']}")
    try:
        http_json(args.endpoint,"/system_stats",timeout=5)
        q=http_json(args.endpoint,"/queue",timeout=5)
        is_busy,r,p=busy(q)
        transport="cmd.exe curl fallback" if in_wsl() and is_windows_localhost(args.endpoint) else "direct urllib"
        print(f"COMFYUI_OK endpoint={args.endpoint} transport={transport} running={r} pending={p}")
    except Exception as e:
        print(f"COMFYUI_UNREACHABLE endpoint={args.endpoint} error={e}")
        return 2 if args.execute else 0
    if not args.execute:
        print("DRY_RUN_ONLY: add --execute to submit prompts")
        return 0
    if is_busy and not args.allow_busy:
        print("REFUSE_BUSY_QUEUE")
        return 3
    failed=0
    for t in selected:
        ok,msg=run_prompt(args.endpoint,t,args.timeout)
        print(("PASS" if ok else "FAIL"),t["workflow"],t["path"],msg)
        if not ok:
            failed=1; break
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
