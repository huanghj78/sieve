import json
import os
from utils import exec_bash, PROJECT_DIR


def get_workflow():
    os.chdir(PROJECT_DIR)
    targets = exec_bash("ls mytest")
    res = [target.split('.')[0] for target in targets]
    return json.dumps(res)

def create_workflow():
    pass