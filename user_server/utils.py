import subprocess

PROJECT_DIR = "/root/chaos_sieve"

def exec_bash(cmd, wait=True):
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, encoding='utf-8')
    if not wait:
        return
    p.wait()
    return p.stdout.read().split('\n')[:-1]
