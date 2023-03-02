import json
import os
from utils import exec_bash, PROJECT_DIR


def get_target():
    os.chdir(PROJECT_DIR)
    targets = exec_bash("ls examples")
    return json.dumps(targets)

def create_target():
    pass