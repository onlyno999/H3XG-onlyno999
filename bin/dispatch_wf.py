#!/usr/bin/env python3
"""H3XG dispatcher — RunningHub workflow 2110385615559806978
《MiniMax H3加速优化版 全能参考(9图 / 3音频 / 3视频)》workflow form.

Usage:
  python3 dispatch_wf.py --prompt-file P.txt --duration 5 \
      --image 18=card.png --image 23=scene.png \
      --out-dir ./prod [--seed 20261014] [--aspect "9:16 (Portrait Widescreen)"]

Audio slots 38/67/68 are always filled with an equal-length silence WAV
(generated on the fly) to block the workflow's preset sample audio.
Exit result (JSON) is written to <out-dir>/results.json; the mp4 is
downloaded to <out-dir>/seg_raw.mp4.
"""
import sys, os, json, time, wave, argparse, mimetypes, urllib.request
for _p in ("/opt/hatch/workflow-skills/custom-connector-setup/bin",
           "/opt/hatch/skills/skill-creator/bin"):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)
from dynamic_credentials import add_surrogate_to_request

BASE = "https://www.runninghub.cn"
WF = "2110385615559806978"
CRED = "custom.runninghub"
UA = "h3xg-dispatch/1.0"

def post_json(path, payload, timeout=60):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": UA}, method="POST")
    add_surrogate_to_request(req, CRED, allowed_hosts=["www.runninghub.cn"])
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def check(resp, ctx):
    ec = resp.get("errorCode")
    if ec not in (None, "", 0, "0"):
        raise SystemExit(f"[{ctx}] errorCode={ec} errorMessage={resp.get('errorMessage')}")
    return resp

def upload_media(path):
    path = os.path.expanduser(path)
    with open(path, "rb") as f: data = f.read()
    boundary = "----h3xg" + os.urandom(8).hex()
    fname = os.path.basename(path)
    ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    body = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/openapi/v2/media/upload/binary", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": UA}, method="POST")
    add_surrogate_to_request(req, CRED, allowed_hosts=["www.runninghub.cn"])
    with urllib.request.urlopen(req, timeout=120) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    check(r, "upload")
    fn = (r.get("data") or {}).get("fileName")
    if not fn: raise SystemExit(f"upload no fileName: {json.dumps(r)[:300]}")
    print(f"[+] uploaded {path} -> {fn} ({len(data)//1024}KB)", flush=True)
    return fn

def make_silence(seconds, dest):
    w = wave.open(dest, "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100)
    w.writeframes(b"\x00\x00" * 44100 * int(seconds) * 2)
    w.close()
    return dest

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--duration", type=float, default=5)
    ap.add_argument("--aspect", default="9:16 (Portrait Widescreen)")
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--image", action="append", default=[], help="NODE=path, repeatable")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-poll", type=int, default=1500)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    prompt = open(a.prompt_file, encoding="utf-8").read()
    nodes = [
        {"nodeId": "25", "fieldName": "value", "fieldValue": prompt},
        {"nodeId": "28", "fieldName": "value", "fieldValue": a.duration},
        {"nodeId": "26", "fieldName": "aspect_ratio", "fieldValue": a.aspect},
        {"nodeId": "5", "fieldName": "noise_seed", "fieldValue": a.seed},
    ]
    for item in a.image:
        nid, _, path = item.partition("=")
        nodes.append({"nodeId": nid, "fieldName": "image", "fieldValue": upload_media(path)})
    silence_path = os.path.join(a.out_dir, f"silence_{a.duration:g}s.wav")
    make_silence(a.duration, silence_path)
    silence = upload_media(silence_path)
    for nid in ("38", "67", "68"):
        nodes.append({"nodeId": nid, "fieldName": "audio", "fieldValue": silence})
    r = post_json(f"/openapi/v2/run/workflow/{WF}",
                  {"nodeInfoList": nodes, "instanceType": "default", "usePersonalQueue": False})
    check(r, "dispatch")
    task_id = r.get("taskId")
    print(f"[+] task created: {task_id}", flush=True)
    with open(os.path.join(a.out_dir, "task_id.txt"), "w") as f: f.write(str(task_id))
    deadline = time.time() + a.max_poll
    while time.time() < deadline:
        time.sleep(10)
        q = post_json("/openapi/v2/query", {"taskId": task_id}, timeout=30)
        status = q.get("status")
        print(f"[.] status={status}", flush=True)
        if status in ("SUCCESS", "COMPLETED"):
            with open(os.path.join(a.out_dir, "results.json"), "w") as f:
                json.dump(q, f, ensure_ascii=False, indent=2)
            for item in (q.get("results") or []):
                url = item.get("url")
                if url and (".mp4" in url or item.get("outputType") == "mp4"):
                    dest = os.path.join(a.out_dir, "seg_raw.mp4")
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=300) as resp, open(dest, "wb") as out:
                        out.write(resp.read())
                    print(f"[+] downloaded -> {dest}", flush=True)
            return
        if status in ("FAILED", "ERROR", "CANCELLED"):
            print(json.dumps(q, ensure_ascii=False)[:800], flush=True)
            raise SystemExit("task failed")
    raise SystemExit("poll timeout")

if __name__ == "__main__":
    main()
