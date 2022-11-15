package main

import (
	"fmt"
	"net/rpc"

	"sieve.client"
)

func main() {
	hostPort := "kind-control-plane:12345"
	rpcClient, err := rpc.Dial("tcp", hostPort)
	if err != nil {
		fmt.Printf("error in setting up connection to %s due to %v\n", hostPort, err)
		return
	}
	request := sieve.EchoAPICallRequest{
		Msg: "Hello!",
	}
	var response sieve.Response
	err = rpcClient.Call("TestCoordinator.EchoAPICall", request, &response)
	if err != nil {
		fmt.Println("RPCCall Failed", err)
		return
	}
	fmt.Println(response.Message)
}
