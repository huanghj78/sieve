import optparse
import os
import kubernetes
import time
import traceback
import sieve
from sieve_common.config import (
    get_common_config,
    load_controller_config,
)
from sieve_common.common import (
    TestContext,
    TestResult,
    cprint,
    bcolors,
    ok,
    fail,
    sieve_modes,
    cmd_early_exit,
    deploy_directory,
)


def generate_kind_config(num_apiservers, num_workers):
    kind_config_dir = "kind_configs"
    os.makedirs(kind_config_dir, exist_ok=True)
    kind_config_filename = os.path.join(
        kind_config_dir,
        "kind-%sa-%sw.yaml"
        % (
            str(num_apiservers),
            str(num_workers),
        ),
    )
    kind_config_file = open(kind_config_filename, "w")
    kind_config_file.writelines(
        ["kind: Cluster\n", "apiVersion: kind.x-k8s.io/v1alpha4\n", "nodes:\n"]
    )
    for i in range(num_apiservers):
        kind_config_file.write("- role: control-plane\n")
    for i in range(num_workers):
        kind_config_file.write("- role: worker\n")
    kind_config_file.close()
    return kind_config_filename


if __name__ == "__main__":
    common_config = get_common_config()
    usage = "usage: python3 setup_cluster.py [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        "-c",
        "--controller_config_dir",
        dest="controller_config_dir",
        help="specify the CONTROLLER_CONFIG_DIR",
        metavar="CONTROLLER_CONFIG_DIR",
    )
    (options, args) = parser.parse_args()
    if options.controller_config_dir is None:
        parser.error("parameter controller required")
    controller_config = sieve.load_controller_config(
        options.controller_config_dir)
    mode = "test"
    test_plan = "/root/sieve/sieve_learn_results/mongodb-operator/recreate/generate-oracle/learn.yaml/intermediate-state/intermediate-state-test-plan-1.yaml"
    container_registry = common_config.container_registry
    image_tag = "test"
    num_apiservers = 3
    num_workers = 3
    # sieve.setup_kind_cluster(test_context)
    kind_config = generate_kind_config(
        num_apiservers, num_workers
    )
    k8s_container_registry = container_registry
    k8s_image_tag = (
        controller_config.kubernetes_version + "-" + image_tag
    )
    retry_cnt = 0
    while retry_cnt < 5:
        try:
            cmd_early_exit("kind delete cluster")
            # sleep here in case if the machine is slow and kind cluster deletion is not done before creating a new cluster
            time.sleep(5 + 10 * retry_cnt)
            retry_cnt += 1
            print("try to create kind cluster; retry count {}".format(retry_cnt))
            cmd_early_exit(
                "kind create cluster --image %s/node:%s --config %s"
                % (k8s_container_registry, k8s_image_tag, kind_config)
            )
            cmd_early_exit(
                "docker exec kind-control-plane bash -c 'mkdir -p /root/.kube/ && cp /etc/kubernetes/admin.conf /root/.kube/config'"
            )
            break
        except Exception:
            print(traceback.format_exc())
    kubernetes.config.load_kube_config()
    core_v1 = kubernetes.client.CoreV1Api()
    # Then we wait apiservers to be ready
    print("Waiting for apiservers to be ready...")
    apiserver_list = []
    for i in range(num_apiservers):
        apiserver_name = "kube-apiserver-kind-control-plane" + (
            "" if i == 0 else str(i + 1)
        )
        apiserver_list.append(apiserver_name)
    for tick in range(600):
        created = core_v1.list_namespaced_pod(
            "kube-system", watch=False, label_selector="component=kube-apiserver"
        ).items
        if len(created) == len(apiserver_list) and len(created) == len(
            [item for item in created if item.status.phase == "Running"]
        ):
            break
        time.sleep(1)
    # sieve.prepare_sieve_server(test_context)
    cmd_early_exit("cp %s sieve_server/server.yaml" % test_plan)
    org_dir = os.getcwd()
    os.chdir("sieve_server")
    cmd_early_exit("go mod tidy")
    # TODO: we should build a container image for sieve server
    cmd_early_exit("env GOOS=linux GOARCH=amd64 go build")
    os.chdir(org_dir)
    cmd_early_exit("docker cp sieve_server kind-control-plane:/sieve_server")

    cprint("Setting up Sieve server...", bcolors.OKGREEN)
    cmd_early_exit(
        "docker exec kind-control-plane bash -c 'cd /sieve_server && ./sieve-server &> sieve-server.log &'"
    )
    ok("Sieve server set up")
