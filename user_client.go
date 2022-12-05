package main

import (
	"fmt"
	"net/rpc"
	"os"

	"sieve.client"
)

func main() {
	var isRunImmediately bool
	if os.Args[1] == "0" {
		isRunImmediately = false
	} else {
		isRunImmediately = true
	}
	hostPort := "kind-control-plane:12345"
	rpcClient, err := rpc.Dial("tcp", hostPort)
	if err != nil {
		fmt.Printf("error in setting up connection to %s due to %v\n", hostPort, err)
		return
	}
	request := sieve.UpdateTestPlanRequest{
		IsRunImmediately: isRunImmediately,
	}
	var response sieve.Response
	err = rpcClient.Call("TestCoordinator.UpdateTestPlanAPICall", request, &response)
	if err != nil {
		fmt.Println("RPCCall Failed", err)
		return
	}
	fmt.Println(response.Message)
}
