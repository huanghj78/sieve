import json
import yaml
import copy
import sys
import os
import shutil
import kubernetes
import controllers

SONAR_EVENT_MARK = "[SONAR-EVENT]"
SONAR_SIDE_EFFECT_MARK = "[SONAR-SIDE-EFFECT]"
SONAR_RECORD_MARK = "[SONAR-RECORD]"

POD = "pod"
PVC = "persistentvolumeclaim"
DEPLOYMENT = "deployment"
STS = "statefulset"

ktypes = [POD, PVC, DEPLOYMENT, STS]


def generateEventMap(path):
    eventMap = {}
    for line in open(path).readlines():
        if SONAR_EVENT_MARK not in line:
            continue
        line = line[line.find(SONAR_EVENT_MARK):].strip()
        tokens = line.split("\t")
        eventID = tokens[1]
        eventType = tokens[2]
        eventObjectType = tokens[3]
        eventObject = json.loads(tokens[4])
        ntn = eventObject["metadata"]["namespace"] + "/" + \
            eventObjectType + "/" + eventObject["metadata"]["name"]
        if ntn not in eventMap:
            eventMap[ntn] = []
        eventMap[ntn].append(
            {"eventID": eventID, "eventType": eventType, "eventObjectType": eventObjectType, "eventObject": eventObject})
    return eventMap


def generateRecords(path):
    records = []
    for line in open(path).readlines():
        if SONAR_RECORD_MARK not in line:
            continue
        line = line[line.find(SONAR_RECORD_MARK):].strip()
        tokens = line.split("\t")
        effects = json.loads(tokens[1])
        eventID = tokens[2]
        eventType = tokens[3]
        eventObjectType = tokens[4]
        eventObject = json.loads(tokens[5])
        ntn = eventObject["metadata"]["namespace"] + "/" + \
            eventObjectType + "/" + eventObject["metadata"]["name"]
        records.append({"effects": effects, "ntn": ntn, "eventID": eventID,
                       "eventType": eventType, "eventObject": eventObject})
    return records


def findPreviousEvent(id, ntn, eventMap):
    assert ntn in eventMap, "invalid ntn %s, not found in eventMap" % (
        ntn)
    for i in range(len(eventMap[ntn])):
        if eventMap[ntn][i]["eventID"] == id:
            if i == 0:
                return None, eventMap[ntn][i]
            else:
                return eventMap[ntn][i-1], eventMap[ntn][i]


def compressObject(prevObject, curObject, slimPrevObject, slimCurObject):
    toDel = []
    toDelCur = []
    toDelPrev = []
    allKeys = set(curObject.keys()).union(prevObject.keys())
    for key in allKeys:
        if key not in curObject:
            continue
        elif key not in prevObject:
            continue
        elif key == "resourceVersion" or key == "time" or key == "managedFields" or key == "lastTransitionTime" or key == "generation":
            toDel.append(key)
        elif str(curObject[key]) != str(prevObject[key]):
            if isinstance(curObject[key], dict):
                if not isinstance(prevObject[key], dict):
                    continue
                res = compressObject(
                    prevObject[key], curObject[key], slimPrevObject[key], slimCurObject[key])
                if res:
                    toDel.append(key)
            elif isinstance(curObject[key], list):
                if not isinstance(prevObject[key], list):
                    continue
                for i in range(len(curObject[key])):
                    if i >= len(prevObject[key]):
                        break
                    elif str(curObject[key][i]) != str(prevObject[key][i]):
                        if isinstance(curObject[key][i], dict):
                            if not isinstance(prevObject[key][i], dict):
                                continue
                            res = compressObject(
                                prevObject[key][i], curObject[key][i], slimPrevObject[key][i], slimCurObject[key][i])
                            if res:
                                # SONAR_SKIP means we can skip the value in list when later comparing to the events in testing run
                                slimCurObject[key][i] = "SONAR-SKIP"
                                slimPrevObject[key][i] = "SONAR-SKIP"
                        elif isinstance(curObject[key][i], list):
                            assert False
                        else:
                            continue
                    else:
                        slimCurObject[key][i] = "SONAR-SKIP"
                        slimPrevObject[key][i] = "SONAR-SKIP"
            else:
                continue
        else:
            toDel.append(key)
    for key in toDel:
        del slimCurObject[key]
        del slimPrevObject[key]
    for key in slimCurObject:
        if isinstance(slimCurObject[key], dict):
            if len(slimCurObject[key]) == 0:
                toDelCur.append(key)
    for key in slimPrevObject:
        if isinstance(slimPrevObject[key], dict):
            if len(slimPrevObject[key]) == 0:
                toDelPrev.append(key)
    for key in toDelCur:
        del slimCurObject[key]
    for key in toDelPrev:
        del slimPrevObject[key]
    if len(slimCurObject) == 0 and len(slimPrevObject) == 0:
        return True
    return False


def diffEvents(prevEvent, curEvent):
    prevObject = prevEvent["eventObject"]
    curObject = curEvent["eventObject"]
    slimPrevObject = copy.deepcopy(prevObject)
    slimCurObject = copy.deepcopy(curObject)
    compressObject(prevObject, curObject, slimPrevObject, slimCurObject)
    return slimPrevObject, slimCurObject


def canonicalization(event):
    for key in event:
        if isinstance(event[key], dict):
            canonicalization(event[key])
        else:
            if "time" in key.lower():
                event[key] = "SONAR-EXIST"
    return event


def traverseRecords(records, eventMap, ntn):
    triggeringPoints = []
    for record in records:
        if record["ntn"] != ntn:
            continue
        prevEvent, curEvent = findPreviousEvent(
            record["eventID"], record["ntn"], eventMap)
        tp = {"name": curEvent["eventObject"]["metadata"]["name"],
              "namespace": curEvent["eventObject"]["metadata"]["namespace"],
              "otype": curEvent["eventObjectType"],
              "effects": record["effects"]}
        if prevEvent is None:
            tp["ttype"] = "todo"
            continue  # TODO: consider single event cases
        elif prevEvent["eventType"] != curEvent["eventType"]:
            tp["ttype"] = "todo"
            continue  # TODO: consider ADDED/UPDATED cases
        else:
            slimPrevObject, slimCurObject = diffEvents(prevEvent, curEvent)
            tp["ttype"] = "event-delta"
            tp["prevEvent"] = slimPrevObject
            tp["curEvent"] = slimCurObject
            tp["prevEventType"] = prevEvent["eventType"]
            tp["curEventType"] = curEvent["eventType"]
        triggeringPoints.append(tp)
    return triggeringPoints


def timeTravelDescription(yamlMap):
    return "Pause %s after it processes a %s event E. "\
        "E should match the pattern %s and the events before E should match %s. "\
        "And restart the controller %s after %s processes a %s %s event." % (
            yamlMap["straggler"], "/".join([yamlMap["ce-namespace"],
                                           yamlMap["ce-rtype"], yamlMap["ce-name"]]),
            yamlMap["ce-diff-current"], yamlMap["ce-diff-previous"], yamlMap["operator-pod"],
            yamlMap["front-runner"], yamlMap["se-etype"], "/".join([yamlMap["se-namespace"],
                                                                    yamlMap["se-rtype"], yamlMap["se-name"]]))


def generateTimaTravelYaml(triggeringPoints, path, project, timing="after"):
    yamlMap = {}
    yamlMap["project"] = project
    yamlMap["mode"] = "time-travel"
    yamlMap["straggler"] = "kind-control-plane3"
    yamlMap["front-runner"] = "kind-control-plane"
    yamlMap["operator-pod"] = project
    yamlMap["command"] = controllers.command[project]
    yamlMap["timing"] = timing
    i = 0
    for triggeringPoint in triggeringPoints:
        if triggeringPoint["ttype"] == "event-delta":
            for effect in triggeringPoint["effects"]:
                # TODO: consider update side effects and even app-specific side effects
                if effect["etype"] == "delete" or effect["etype"] == "create":
                    i += 1
                    yamlMap["ce-name"] = triggeringPoint["name"]
                    yamlMap["ce-namespace"] = triggeringPoint["namespace"]
                    yamlMap["ce-rtype"] = triggeringPoint["otype"]
                    yamlMap["ce-diff-current"] = json.dumps(
                        canonicalization(copy.deepcopy(triggeringPoint["curEvent"])))
                    yamlMap["ce-diff-previous"] = json.dumps(
                        canonicalization(copy.deepcopy(triggeringPoint["prevEvent"])))
                    yamlMap["ce-etype-current"] = triggeringPoint["curEventType"]
                    yamlMap["ce-etype-previous"] = triggeringPoint["prevEventType"]
                    yamlMap["se-name"] = effect["name"]
                    yamlMap["se-namespace"] = effect["namespace"]
                    yamlMap["se-rtype"] = effect["rtype"]
                    yamlMap["se-etype"] = "ADDED" if effect["etype"] == "delete" else "DELETED"
                    yamlMap["description"] = timeTravelDescription(yamlMap)
                    yaml.dump(yamlMap, open(
                        os.path.join(path, "%s-%s.yaml" % (str(i), timing)), "w"), sort_keys=False)
        else:
            print("ignoring single event trigger")
            # TODO: handle the single event trigger


def generateDigest(path):
    digest = {}
    empty_entry = {"size": -1, "terminating": -1,
                   "create": 0, "update": 0, "delete": 0}
    for line in open(path).readlines():
        if SONAR_SIDE_EFFECT_MARK not in line:
            continue
        line = line[line.find(SONAR_SIDE_EFFECT_MARK):].strip()
        tokens = line.split("\t")
        effectType = tokens[1]
        # if effectType == "update":
        #     continue
        rType = tokens[2]
        if rType not in digest:
            digest[rType] = copy.deepcopy(empty_entry)
        digest[rType][effectType] += 1

    kubernetes.config.load_kube_config()
    core_v1 = kubernetes.client.CoreV1Api()
    apps_v1 = kubernetes.client.AppsV1Api()
    k8s_namespace = "default"
    resources = {}
    for ktype in ktypes:
        resources[ktype] = []
        if ktype not in digest:
            digest[ktype] = copy.deepcopy(empty_entry)
    for pod in core_v1.list_namespaced_pod(k8s_namespace, watch=False).items:
        resources[POD].append(pod)
    for pvc in core_v1.list_namespaced_persistent_volume_claim(k8s_namespace, watch=False).items:
        resources[PVC].append(pvc)
    for dp in apps_v1.list_namespaced_deployment(k8s_namespace, watch=False).items:
        resources[DEPLOYMENT].append(dp)
    for sts in apps_v1.list_namespaced_stateful_set(k8s_namespace, watch=False).items:
        resources[STS].append(sts)
    for ktype in ktypes:
        digest[ktype]["size"] = len(resources[ktype])
        terminating = 0
        for item in resources[ktype]:
            if item.metadata.deletion_timestamp != None:
                terminating += 1
        digest[ktype]["terminating"] = terminating
    return digest


def analyzeTrace(project, dir, double_sides=False):
    log_path = os.path.join(dir, "sonar-server.log")
    json_dir = os.path.join(dir, "generated-json")
    conf_dir = os.path.join(dir, "generated-config")
    if os.path.exists(json_dir):
        shutil.rmtree(json_dir)
    if os.path.exists(conf_dir):
        shutil.rmtree(conf_dir)
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(conf_dir, exist_ok=True)
    eventMap = generateEventMap(log_path)
    records = generateRecords(log_path)
    digest = generateDigest(log_path)
    json.dump(eventMap, open(os.path.join(
        json_dir, "event-map.json"), "w"), indent=4)
    json.dump(records, open(os.path.join(
        json_dir, "records.json"), "w"), indent=4)
    json.dump(digest, open(os.path.join(
        dir, "digest.json"), "w"), indent=4)
    triggeringPoints = []
    for ntn in eventMap:
        triggeringPoints = triggeringPoints + \
            traverseRecords(records, eventMap, ntn)
    json.dump(triggeringPoints, open(os.path.join(
        json_dir, "triggering-points.json"), "w"), indent=4)
    generateTimaTravelYaml(triggeringPoints, conf_dir, project)
    if double_sides:
        generateTimaTravelYaml(triggeringPoints, conf_dir, project, "before")


if __name__ == "__main__":
    project = sys.argv[1]
    test = sys.argv[2]
    dir = os.path.join("log", project, test, "learn")
    analyzeTrace(project, dir)