import optparse
import os
from sieve_common.common import (
    TestContext,
    TestResult,
    cprint,
    bcolors,
    ok,
    fail,
    sieve_modes,
    cmd_early_exit,
    deploy_directory,
)

def update_test_plan(lab_name, test_plan, cnt):
    cmd_early_exit(
        f"docker cp {test_plan} {lab_name}-control-plane:/chaos_server/server.yaml")
    cmd_early_exit(
        f"docker exec {lab_name}-control-plane bash -c '/chaos_server/user_client {lab_name} {cnt}'")


def generate_config(workflowForm, planForm):
    config = {}
    config['workload'] = workflowForm['workload']
    config['actions'] = []
    for item in planForm['items']:
        action = {}
        action['actionType'] = item['actionType']
        if action['actionType'] == 'pauseAPIServer' or action['actionType'] == 'resumeAPIServer':
            action['apiServerName'] = item['actionArgs'][0]
            action['pauseScope'] = item['actionArgs'][1]
        elif action['actionType'] == 'pauseController' or action['actionType'] == 'resumeController':
            action['pauseAt'] = item['actionArgs'][0]
            action['pauseScope'] = item['actionArgs'][1]
            action['avoidOngoingRead'] = True
        elif action['actionType'] == 'reconnectController':
            #todo
            return
        elif action['actionType'] == 'delayAPIServer':
            action['apiServerName'] = item['actionArgs'][0]
            action['delayTime'] = item['actionArgs'][1]
            action['pauseAt'] = item['actionArgs'][2]
            action['pauseScope'] = item['actionArgs'][3]
            action['avoidOngoingRead'] = True
        action['trigger'] = {'definitions': []}
        trigger = {}
        trigger['definitions'] = []
        triggerForm = item['triggerForm']
        for triggerItem in triggerForm['items']:
            definition = {}
            definition['triggerName'] = triggerItem['name']
            definition['condition'] = {}
            definition['condition']['conditionType'] = triggerItem['conditionType']
            definition['condition']['resourceKey'] = triggerItem['resourceKey']
            definition['condition']['occurrence'] = 1
            definition['observationPoint'] = {}
            definition['observationPoint']['when'] = triggerItem['observedWhen']
            definition['observationPoint']['by'] = triggerItem['observedBy']
            trigger['definitions'].append(definition)
        if triggerForm['immediately']:
            trigger['expression'] = ''
        else:
            trigger['expression'] = triggerForm['expression']
        action['trigger'] = trigger
        config['actions'].append(action)
    return config



