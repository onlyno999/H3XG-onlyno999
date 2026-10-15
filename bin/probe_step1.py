#!/usr/bin/env python3
import os
import sys, json, urllib.request, urllib.error
for _p in ("/opt/hatch/workflow-skills/custom-connector-setup/bin",
           "/opt/hatch/skills/skill-creator/bin"):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)
from dynamic_credentials import add_surrogate_to_request
BASE="https://www.runninghub.cn"; WF="2110385615559806978"
def post(ep, nid):
    payload={"nodeInfoList":[{"nodeId":str(nid),"fieldName":"__bogus_probe_field__","fieldValue":"x"}]}
    req=urllib.request.Request(BASE+f"/openapi/v2/run/{ep}/{WF}", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json","User-Agent":"probe/1.0"}, method="POST")
    add_surrogate_to_request(req,"custom.runninghub",allowed_hosts=["www.runninghub.cn"])
    try:
        with urllib.request.urlopen(req, timeout=25) as resp: r=json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body=e.read().decode(errors="replace")
        try: r=json.loads(body)
        except: r={"_http":e.code,"_body":body[:300]}
    except Exception as e: return f"ERR {e}"
    msg=json.dumps(r,ensure_ascii=False)
    tag=""
    if r.get("taskId"): tag="!!! TASK CREATED "+str(r.get("taskId"))
    elif "node_not_found_in_workflow" in msg: tag="MISSING (node_not_found_in_workflow)"
    elif "field_not_found" in msg: tag="EXISTS (field_not_found)"
    return f"errorCode={r.get('errorCode')} {tag} | {msg[:260]}"
for ep in ("workflow","ai-app"):
    print(f"== endpoint: {ep} ==")
    for nid in (1, 99999):
        print(f"{nid}: {post(ep,nid)}", flush=True)
