import copy
import kubernetes
import common
import yaml


def generate_digest(path):
    side_effect = generate_side_effect(path)
    status = generate_status()
    return side_effect, status


def generate_side_effect(path):
    side_effect_map = {}
    side_effect_empty_entry = {"Create": 0, "Update": 0,
                               "Delete": 0, "Patch": 0, "DeleteAllOf": 0}
    for line in open(path).readlines():
        if common.SONAR_SIDE_EFFECT_MARK not in line:
            continue
        side_effect = common.parse_side_effect(line)
        if common.ERROR_MSG_FILTER_FLAG:
            if side_effect.error == "NotFound":
                continue
        rtype = side_effect.rtype
        namespace = side_effect.namespace
        name = side_effect.name
        etype = side_effect.etype
        if rtype not in side_effect_map:
            side_effect_map[rtype] = {}
        if namespace not in side_effect_map[rtype]:
            side_effect_map[rtype][namespace] = {}
        if name not in side_effect_map[rtype][namespace]:
            side_effect_map[rtype][namespace][name] = copy.deepcopy(
                side_effect_empty_entry)
        side_effect_map[rtype][namespace][name][etype] += 1
    return side_effect_map


def generate_status():
    status = {}
    status_empty_entry = {"size": 0, "terminating": 0}
    kubernetes.config.load_kube_config()
    core_v1 = kubernetes.client.CoreV1Api()
    apps_v1 = kubernetes.client.AppsV1Api()
    k8s_namespace = "default"
    resources = {}
    for ktype in common.KTYPES:
        resources[ktype] = []
        if ktype not in status:
            status[ktype] = copy.deepcopy(status_empty_entry)
    for pod in core_v1.list_namespaced_pod(k8s_namespace, watch=False).items:
        resources[common.POD].append(pod)
    for pvc in core_v1.list_namespaced_persistent_volume_claim(k8s_namespace, watch=False).items:
        resources[common.PVC].append(pvc)
    for dp in apps_v1.list_namespaced_deployment(k8s_namespace, watch=False).items:
        resources[common.DEPLOYMENT].append(dp)
    for sts in apps_v1.list_namespaced_stateful_set(k8s_namespace, watch=False).items:
        resources[common.STS].append(sts)
    for ktype in common.KTYPES:
        status[ktype]["size"] = len(resources[ktype])
        terminating = 0
        for item in resources[ktype]:
            if item.metadata.deletion_timestamp != None:
                terminating += 1
        status[ktype]["terminating"] = terminating
    return status


def check_status(learning_status, testing_status):
    alarm = 0
    all_keys = set(learning_status.keys()).union(
        testing_status.keys())
    bug_report = ""
    for rtype in all_keys:
        if rtype not in learning_status:
            bug_report += "[ERROR] %s not in learning status digest\n" % (
                rtype)
            alarm += 1
            continue
        elif rtype not in testing_status:
            bug_report += "[ERROR] %s not in testing status digest\n" % (
                rtype)
            alarm += 1
            continue
        else:
            for attr in learning_status[rtype]:
                if learning_status[rtype][attr] != testing_status[rtype][attr]:
                    alarm += 1
                    bug_report += "[ERROR] %s %s inconsistency: learning: %s, testing: %s\n" % (
                        rtype, attr, str(learning_status[rtype][attr]), str(testing_status[rtype][attr]))
    return alarm, "[BUG REPORT] status\n" + bug_report


def check_side_effect(learning_side_effect, testing_side_effect, interest_objects, selective=True):
    alarm = 0
    bug_report = ""
    for interest in interest_objects:
        rtype = interest["rtype"]
        namespace = interest["namespace"]
        name = interest["name"]
        exist = True
        if rtype not in learning_side_effect or namespace not in learning_side_effect[rtype] or name not in learning_side_effect[rtype][namespace]:
            bug_report += "[ERROR] %s/%s/%s not in learning side effect digest\n" % (
                rtype, namespace, name)
            alarm += 1
            exist = False
        if rtype not in testing_side_effect or namespace not in testing_side_effect[rtype] or name not in testing_side_effect[rtype][namespace]:
            bug_report += "[ERROR] %s/%s/%s not in testing side effect digest\n" % (
                rtype, namespace, name)
            alarm += 1
            exist = False
        if exist:
            learning_entry = learning_side_effect[rtype][namespace][name]
            testing_entry = testing_side_effect[rtype][namespace][name]
            for attr in learning_entry:
                if selective:
                    if attr == "Update" or attr == "Patch":
                        continue
                if learning_entry[attr] != testing_entry[attr]:
                    alarm += 1
                    bug_report += "[ERROR] %s/%s/%s %s inconsistency: learning: %s, testing: %s\n" % (
                        rtype, namespace, name, attr, str(learning_entry[attr]), str(testing_entry[attr]))
    return alarm, "[BUG REPORT] side effect\n" + bug_report


def compare_digest(learning_side_effect, learning_status, testing_side_effect, testing_status, config):
    testing_config = yaml.safe_load(open(config))
    interest_objects = []
    if testing_config["mode"] == "time-travel":
        interest_objects.append(
            {"rtype": testing_config["se-rtype"], "namespace": testing_config["se-namespace"], "name": testing_config["se-name"]})
    alarm_status, bug_report_status = check_status(
        learning_status, testing_status)
    alarm_side_effect, bug_report_side_effect = check_side_effect(
        learning_side_effect, testing_side_effect, interest_objects)
    alarm = alarm_side_effect + alarm_status
    bug_report = bug_report_side_effect + bug_report_status
    if alarm != 0:
        bug_report += "[BUGGY] # alarms: %d\n" % (alarm)
    print(bug_report)
    return bug_report