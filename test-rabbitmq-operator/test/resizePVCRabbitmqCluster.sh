#!/bin/bash

set -ex

kubectl apply -f rmqc-1.yaml
sleep 50s
kubectl apply -f rmqc-1-15Gi.yaml
sleep 50s