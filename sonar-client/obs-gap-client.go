package sonar

import (
	"encoding/json"
	"log"
	"reflect"
)

func NotifyObsGapBeforeIndexerWrite(operationType string, object interface{}) {
	if !checkStage(test) || !checkMode(obsGap) {
		return
	}
	// if !triggerReconcile(object) {
	// 	return -1
	// }
	log.Printf("[sonar][NotifyObsGapBeforeIndexerWrite] operationType: %s\n", operationType)
	client, err := newClient()
	if err != nil {
		printError(err, connectionError)
		return
	}
	jsonObject, err := json.Marshal(object)
	if err != nil {
		printError(err, jsonError)
		return
	}

	// if name == config["ce-name"].(string) && namespace == config["ce-namespace"].(string) && resourceType == config["ce-rtype"].(string) {
	// }
	request := &NotifyObsGapBeforeIndexerWriteRequest{
		OperationType: operationType,
		Object:        string(jsonObject),
		ResourceType:  regularizeType(reflect.TypeOf(object).String()),
	}
	var response Response
	err = client.Call("ObsGapListener.NotifyObsGapBeforeIndexerWrite", request, &response)
	if err != nil {
		printError(err, replyError)
		return
	}
	checkResponse(response, "NotifyObsGapBeforeIndexerWrite")
	client.Close()
}

func NotifyObsGapAfterIndexerWrite(operationType string, object interface{}) {
	if !checkStage(test) || !checkMode(obsGap) {
		return
	}
	log.Printf("[sonar][NotifyObsGapAfterIndexerWrite] operationType: %s\n", operationType)
	client, err := newClient()
	if err != nil {
		printError(err, connectionError)
		return
	}
	jsonObject, err := json.Marshal(object)
	if err != nil {
		printError(err, jsonError)
		return
	}

	request := &NotifyObsGapAfterIndexerWriteRequest{
		OperationType: operationType,
		Object:        string(jsonObject),
		ResourceType:  regularizeType(reflect.TypeOf(object).String()),
	}
	var response Response
	err = client.Call("ObsGapListener.NotifyObsGapAfterIndexerWrite", request, &response)
	if err != nil {
		printError(err, replyError)
		return
	}
	checkResponse(response, "NotifyObsGapAfterIndexerWrite")
	client.Close()
}

func NotifyObsGapBeforeReconcile(controllerName string) {
	if !checkStage(test) || !checkMode(obsGap) {
		return
	}
	log.Printf("[sonar][NotifyObsGapBeforeReconcile]\n")
	client, err := newClient()
	if err != nil {
		printError(err, connectionError)
		return
	}
	request := &NotifyObsGapBeforeReconcileRequest{
		ControllerName: controllerName,
	}
	var response Response
	err = client.Call("ObsGapListener.NotifyObsGapBeforeReconcile", request, &response)
	if err != nil {
		printError(err, replyError)
		return
	}
	checkResponse(response, "NotifyObsGapBeforeReconcile")
	client.Close()
}