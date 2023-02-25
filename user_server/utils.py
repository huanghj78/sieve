import subprocess


def exec_bash(cmd):
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, encoding='utf-8')
    p.wait()
    return p.stdout.read().split('\n')[:-1]
