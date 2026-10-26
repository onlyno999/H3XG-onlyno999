#!/usr/bin/env python3
"""Dispatcher for the CZX233 exit (API-only).
Workflow 2113599252554407938 (CZX233 【最强单采】双重显存优化1.0画质30秒直出流, supersedes 2108739345095155713 on 2026-10-26).
API node map (2026-10-26 probes + direct dispatch):
238/value prompt / 227/value duration seconds / 228 aspect_ratio + megapixels /
129/noise_seed (control_after_generate=randomize: a set seed may still be randomized) /
199/image ref1 / 188/image ref2 / 189/image ref3 / 190/image ref4 / 191/image ref5 / 192/image ref6 (6 images total, API direct).
API hangs 199/188 normally; canvas frontend switches do not affect the API.
Full slot table (6 images + 3 audio + 1 video) is in references/node_map_czx233.md.
Dialogue is native via prompt (<d> + (Sx)); no audio refs are hung.
"""
import sys, os, json, time, subprocess, urllib.request, argparse

sys.path.insert(0, "/opt/hatch/workflow-skills/custom-connector-setup/bin")
try:
    from dynamic_credentials import add_surrogate_to_request
except ImportError:
    sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
    from dynamic_credentials import add_surrogate_to_request

BASE = "https://www.runninghub.cn"
WF = "2113599252554407938"

ap = argparse.ArgumentParser()
ap.add_argument("--prompt-file", required=True)
ap.add_argument("--duration", type=float, default=10)
ap.add_argument("--seed", type=int, default=20261060)
ap.add_argument("--aspect", default="9:16 (Portrait Widescreen)")
ap.add_argument("--megapixels", type=float, default=0.94)  # B分辨率定死：736x1280 / 1280x736，见SKILL
ap.add_argument("--out", required=True)
ap.add_argument("--images", nargs="*", default=[])
ap.add_argument("--videos", nargs="*", default=[])
args = ap.parse_args()

def upload_media(path):
    boundary = "----NEWWFBOUNDARY7"
    with open(os.path.expanduser(path), "rb") as f:
        data = f.read()
    name = os.path.basename(path)
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/openapi/v2/media/upload/binary", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST")
    add_surrogate_to_request(req, "custom.runninghub", allowed_hosts=["www.runninghub.cn"])
    with urllib.request.urlopen(req, timeout=120) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    fn = (r.get("data") or {}).get("fileName")
    if not fn:
        print("UPLOAD FAILED:", json.dumps(r, ensure_ascii=False)[:300]); sys.exit(1)
    print("uploaded", name, "->", fn, flush=True)
    return fn

def post_json(path, payload, timeout=30):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    add_surrogate_to_request(req, "custom.runninghub", allowed_hosts=["www.runninghub.cn"])
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def resolve(ref):
    if ref and os.path.exists(os.path.expanduser(ref)):
        return upload_media(ref)
    return ref

prompt = open(os.path.expanduser(args.prompt_file), encoding="utf-8").read().strip()
nodes = [
    {"nodeId": "238", "fieldName": "value", "fieldValue": prompt},
    {"nodeId": "227", "fieldName": "value", "fieldValue": args.duration},
    {"nodeId": "228", "fieldName": "aspect_ratio", "fieldValue": args.aspect},
    {"nodeId": "228", "fieldName": "megapixels", "fieldValue": args.megapixels},
    {"nodeId": "129", "fieldName": "noise_seed", "fieldValue": args.seed},
]
for pair in args.images:
    nid, path = pair.split("=", 1)
    nodes.append({"nodeId": nid, "fieldName": "image", "fieldValue": resolve(path)})
# videos not API-exposable on this workflow (no Load Video node found); ignored
for pair in args.videos:
    pass

r = post_json(f"/openapi/v2/run/workflow/{WF}",
              {"nodeInfoList": nodes, "instanceType": "default", "usePersonalQueue": False})
if r.get("errorCode") not in (None, "", 0, "0"):
    print("DISPATCH FAILED:", json.dumps(r, ensure_ascii=False)[:800]); sys.exit(1)
tid = r.get("taskId")
print("taskId:", tid, "seed:", args.seed, flush=True)

for i in range(120):
    try:
        q = post_json("/openapi/v2/query", {"taskId": tid}, timeout=20)
    except Exception as e:
        print(f"[{(i+1)*15}s] net err: {e}", flush=True); time.sleep(15); continue
    st = q.get("status")
    if i % 4 == 0 or st in ("SUCCESS", "FAILED", "CANCELLED"):
        print(f"[{(i+1)*15}s] status={st}", flush=True)
    if st == "SUCCESS":
        res = q.get("results") or []
        url = (res[0].get("url") if isinstance(res[0], dict) else res[0]) if res else None
        print("result_url:", url)
        if url:
            outp = os.path.expanduser(args.out)
            d = os.path.dirname(outp)
            if d:
                os.makedirs(d, exist_ok=True)
            ok = False
            for attempt in range(6):
                if os.path.exists(outp):
                    os.remove(outp)
                rr = subprocess.run(["curl", "-sS", "--retry", "3", "--retry-all-errors",
                                     "--max-time", "300", "-o", outp, url],
                                    capture_output=True, text=True)
                if rr.returncode == 0 and os.path.exists(outp) and os.path.getsize(outp) > 100000:
                    ok = True; break
                print(f"download retry {attempt+1}/6", flush=True); time.sleep(5)
            print("saved:", outp, ok)
        break
    if st in ("FAILED", "CANCELLED"):
        print("task ended:", json.dumps(q, ensure_ascii=False)[:500]); break
    time.sleep(15)
