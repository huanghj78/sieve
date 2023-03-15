import json
import yaml
import os
import time
from utils import exec_bash, PROJECT_DIR
from apps.workflow import generate_config, update_test_plan

def get_all_workflow():
    res = []
    os.chdir(PROJECT_DIR+"/workflow")
    workflows = exec_bash("ls -l")[1:]
    for workflow in workflows:
        item = {}
        workflow = workflow.split()
        item['lab_name'] = workflow[-1].split('-')[0]
        item['name'] = '-'.join(workflow[-1].split('-')[1:])
        item['created_at'] = " ".join(workflow[5:8])
        with open(workflow[-1], 'r', encoding='utf-8') as f:
            config = yaml.load(f)
            actions = [action['actionType'] for action in config['actions']]
            item['actions'] = ",".join(actions)
        res.append(item)
    return json.dumps(res)

def get_workflow(lab_name, workflow):
    os.chdir(PROJECT_DIR+"/workflow")
    with open(f'{lab_name}-{workflow}', 'r', encoding='utf-8') as f:
        config = yaml.load(f)
    return json.dumps(config)

def create_workflow(workflow_form, plan_form):
    config = generate_config(workflow_form, plan_form)
    workflow = workflow_form['name']
    lab_name = workflow_form['labName']
    file_name = f'{PROJECT_DIR}/workflow/{lab_name}-{workflow}'
    with open(file_name, 'w', encoding='utf-8') as f:
        yaml.dump(data=config, stream=f, allow_unicode=True)
    # cnt = 0
    # for item in plan_form['items']:
    #     if item['triggerForm']['immediately']:
    #         cnt += 1
    #     else:
    #         break
    # update_test_plan(workflow_form['labName'], file_name, cnt)
    return config

def run_workflow(lab_name, workflow):
    file_name = f'{PROJECT_DIR}/workflow/{lab_name}-{workflow}'
    with open(file_name, 'r', encoding='utf-8') as f:
        config = yaml.load(data=config, stream=f, allow_unicode=True)
    cnt = 0
    for action in config['actions']:
        if action['trigger']['expression'] == '':
            cnt += 1
        else:
            break
    update_test_plan(lab_name, file_name, cnt)
    return config

def delete_workflow(lab_name, workflow):
    os.chdir(PROJECT_DIR+"/workflow")
    exec_bash(f"rm {lab_name}-{workflow}")
    return json.dumps({})