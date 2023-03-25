import subprocess
import os
import time

#time.sleep(500)
cmd = "kubectl config use-context kind-kind"
p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8', preexec_fn=os.setsid)
cmd = "kubectl get pods -n default"
p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8', preexec_fn=os.setsid)
print(len(p.stdout.read().split('\n')[1:-1]))