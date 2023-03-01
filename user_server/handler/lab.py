import subprocess
import json
from utils import exec_bash
from apps.lab import setup_cluster, build


def get_lab():
    res = {}
    labs = exec_bash("kind get clusters")
    containers = exec_bash(
        "docker ps --format {{.Names}}/{{.CreatedAt}}/{{.Status}}")
    for lab in labs:
        res[lab] = []
    for ctn in containers:
        ctn = ctn.split('/')
        for lab in labs:
            if ctn[0].startswith(lab):
                res[lab].append(ctn)
                break
    return json.dumps(res)


def create_lab(name, apiserver_cnt, worker_cnt):
    # todo: setup_cluster.py 加上 worker_cnt参数
    controller_config_dir = "/root/chaos_sieve/examples/mongodb-operator"
    test_plan = "/root/chaos_sieve/mytest/create-restart-controller.yaml"
    build(controller_config_dir)
    setup_cluster(name, controller_config_dir,
                  test_plan, apiserver_cnt, worker_cnt)
    return json.dumps({'msg': 'success'})
