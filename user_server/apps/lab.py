import subprocess
import json
from utils import exec_bash


def get_lab():
    res = {}
    labs = exec_bash("kind get clusters").split('\n')
    containers = exec_bash(
        "docker ps --format {{.Names}}/{{.CreatedAt}}/{{.Status}}").split('\n')
    for lab in labs:
        res[lab] = []
    for ctn in containers:
        ctn = ctn.split('/')
        for lab in labs:
            if ctn[0].startswith(lab):
                res[lab].append([ctn])
                break
    return json.dumps(res)


def create_lab(name, worker_cnt):
    # todo: setup_cluster.py 加上 worker_cnt参数
    pass
