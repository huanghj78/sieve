package main

import (
	"io/ioutil"
	"log"
)

func getConfig() map[interface{}]interface{} {

	data, err := ioutil.ReadFile("server.yaml")
	checkError(err)
	m := make(map[interface{}]interface{})

	err = yaml.Unmarshal([]byte(data), &m)
	checkError(err)
	log.Printf("config:\n%v\n", m)

	return m
}
