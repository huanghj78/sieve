import optparse
import kubernetes
import sieve
import time
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
    test_context = TestContext(
        controller=controller_config.controller_name,
        controller_config_dir=options.controller_config_dir,
        test_workload="",
        mode="test",
        phase="all",
        original_test_plan="/root/sieve/sieve_learn_results/mongodb-operator/recreate/generate-oracle/learn.yaml/intermediate-state/intermediate-state-test-plan-1.yaml",
        test_plan="/root/sieve/sieve_learn_results/mongodb-operator/recreate/generate-oracle/learn.yaml/intermediate-state/intermediate-state-test-plan-1.yaml",
        result_root_dir="",
        result_dir="/root/sieve/mydir",
        oracle_dir="",
        container_registry=common_config.container_registry,
        image_tag="test",
        num_apiservers=3,
        num_workers=3,
        use_csi_driver=False,
        common_config=common_config,
        controller_config=controller_config,
    )
    sieve.setup_kind_cluster(test_context)
    kubernetes.config.load_kube_config()
    core_v1 = kubernetes.client.CoreV1Api()
    # Then we wait apiservers to be ready
    print("Waiting for apiservers to be ready...")
    apiserver_list = []
    for i in range(test_context.num_apiservers):
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
    sieve.prepare_sieve_server(test_context)
    cprint("Setting up Sieve server...", bcolors.OKGREEN)
    sieve.start_sieve_server(test_context)
    ok("Sieve server set up")
