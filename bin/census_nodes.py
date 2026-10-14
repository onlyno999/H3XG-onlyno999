#!/usr/bin/env python3
import sys, json, urllib.request, urllib.error
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request
from concurrent.futures import ThreadPoolExecutor, as_completed
BASE="https://www.runninghub.cn"; WF="2110385615559806978"; EP="workflow"
LO,HI=int(sys.argv[1]),int(sys.argv[2])
def post(nid):
    payload={"nodeInfoList":[{"nodeId":str(nid),"fieldName":"__bogus_probe_field__","fieldValue":"x"}]}
    req=urllib.request.Request(BASE+f"/openapi/v2/run/{EP}/{WF}", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json","User-Agent":"probe/1.0"}, method="POST")
    add_surrogate_to_request(req,"custom.runninghub",allowed_hosts=["www.runninghub.cn"])
    try:
        with urllib.request.urlopen(req, timeout=25) as resp: r=json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body=e.read().decode(errors="replace")
        try: r=json.loads(body)
        except: r={"_http":e.code,"_body":body[:200]}
    except Exception as e: return nid, f"ERR {e}"
    msg=json.dumps(r,ensure_ascii=False); ec=r.get("errorCode")
    if r.get("taskId"): return nid, f"!!! TASK CREATED {r.get('taskId')}"
    if "node_not_found_in_workflow" in msg: return nid, "MISSING"
    if "field_not_found" in msg: return nid, "EXISTS"
    return nid, f"errorCode={ec} {msg[:180]}"
results={}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs={ex.submit(post,i):i for i in range(LO,HI+1)}
    for f in as_completed(futs):
        nid,status=f.result(); results[nid]=status
        if status!="MISSING": print(f"{nid}: {status}", flush=True)
exists=sorted([k for k,v in results.items() if v=="EXISTS"])
print("EXISTS_LIST:", ",".join(map(str,exists))); print("COUNT_EXISTS:", len(exists))
with open(f"census_results_{LO}_{HI}.json","w") as out: json.dump(results,out,ensure_ascii=False,indent=2)
