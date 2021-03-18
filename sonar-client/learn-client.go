package sonar

import (
	"log"
	"encoding/json"
)

func NotifyLearnBeforeIndexerWrite(operationType string, object interface{}) {
	if !checkMode(learn) {
		return
	}
	log.Printf("[sonar][NotifyLearnBeforeIndexerWrite] operationType: %s\n", operationType)
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
	request := &NotifyLearnBeforeIndexerWriteRequest{
		OperationType: operationType,
		Object: string(jsonObject),
	}
	var response Response
	err = client.Call("LearnListener.NotifyBeforeIndexerWrite", request, &response)
	if err != nil {
		printError(err, replyError)
		return
	}
	checkResponse(response, "NotifyLearnBeforeIndexerWrite")
	client.Close()
}

func NotifyLearnBeforeReconcile() {
	if !checkMode(learn) {
		return
	}
	log.Printf("[sonar][NotifyLearnBeforeReconcile]\n")
	client, err := newClient()
	if err != nil {
		printError(err, connectionError)
		return
	}
	request := &NotifyLearnBeforeReconcileRequest{
		Nothing: "nothing",
	}
	var response Response
	err = client.Call("LearnListener.NotifyBeforeReconcile", request, &response)
	if err != nil {
		printError(err, replyError)
		return
	}
	checkResponse(response, "NotifyLearnBeforeReconcile")
	client.Close()
}

func NotifyLearnAfterReconcile() {
	if !checkMode(learn) {
		return
	}
	log.Printf("[sonar][NotifyLearnAfterReconcile]\n")
	client, err := newClient()
	if err != nil {
		printError(err, connectionError)
		return
	}
	request := &NotifyLearnAfterReconcileRequest{
		Nothing: "nothing",
	}
	var response Response
	err = client.Call("LearnListener.NotifyAfterReconcile", request, &response)
	if err != nil {
		printError(err, replyError)
		return
	}
	checkResponse(response, "NotifyLearnAfterReconcile")
	client.Close()
}

func NotifyLearnSideEffects(sideEffectType string) {
	if !checkMode(learn) {
		return
	}
	log.Printf("[sonar][NotifyLearnSideEffects]\n")
	client, err := newClient()
	if err != nil {
		printError(err, connectionError)
		return
	}
	request := &NotifyLearnSideEffectsRequest{
		SideEffectType: sideEffectType,
	}
	var response Response
	err = client.Call("LearnListener.NotifySideEffects", request, &response)
	if err != nil {
		printError(err, replyError)
		return
	}
	checkResponse(response, "NotifyLearnSideEffects")
	client.Close()
}