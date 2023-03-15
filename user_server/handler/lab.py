import json
import os
from utils import exec_bash, PROJECT_DIR
from apps.lab import setup_cluster, build


def get_lab():
    res = []
    labs = exec_bash("kind get clusters")
    containers = exec_bash(
        "docker ps --format {{.Names}},{{.CreatedAt}},{{.Status}},{{.Image}}")
    for lab in labs:
        nodes = []
        for ctn in containers:
            ctn = ctn.split(',')
            if ctn[-1] != "ghcr.io/sieve-project/action/node:v1.18.9-test":
                continue
            if ctn[0].startswith(lab):
                nodes.append(
                    {"name": ctn[0], "created_at": ctn[1], "status": ctn[2]})
        res.append({"name": lab, "nodes": nodes})
    print(res)
    return json.dumps(res)


def create_lab(name, apiserver_cnt, worker_cnt, target, workflow):
    os.chdir(PROJECT_DIR)
    # build(controller_config_dir)
    setup_cluster(name, os.path.join("/root/chaos_sieve/examples", target),
                  os.path.join("/root/chaos_sieve/test_plan", workflow + ".yaml"), apiserver_cnt, worker_cnt)
    return json.dumps({'msg': 'success'})

def get_apiserver(name):
    nodes = exec_bash(
        "docker ps --format {{.Names}} | grep %s" % name)
    res = []
    for node in nodes:
        print(node)
        if node.startswith(f"{name}-control-plane"):
            res.append(node)
    return json.dumps(res)