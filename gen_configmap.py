import optparse
import os
import kubernetes
import time
import traceback
import sieve
import yaml
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


def generate_configmap(test_plan):
    test_plan_content = open(test_plan).read()
    configmap = {}
    configmap["apiVersion"] = "v1"
    configmap["kind"] = "ConfigMap"
    configmap["metadata"] = {"name": "sieve-testing-global-config"}
    configmap["data"] = {"sieveTestPlan": test_plan_content}
    configmap_path = "%s-configmap.yaml" % test_plan[:-5]
    yaml.dump(configmap, open(configmap_path, "w"), sort_keys=False)
    return configmap_path


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
    parser.add_option(
        "-p",
        "--test_plan",
        dest="test_plan",
        help="",
        metavar="CONTROLLER_CONFIG_DIR",
    )
    (options, args) = parser.parse_args()
    if options.controller_config_dir is None:
        parser.error("parameter controller required")
    controller_config = sieve.load_controller_config(
        options.controller_config_dir)
    mode = "test"
    test_plan = options.test_plan
    container_registry = common_config.container_registry
    image_tag = "test"
    # ensure that every apiserver will see the configmap is created
    time.sleep(3)
    configmap = generate_configmap(test_plan)
    print(configmap)
    cmd_early_exit("kubectl apply -f %s" % configmap)

    # Preload operator image to kind nodes
    image = "%s/%s:%s" % (
        container_registry,
        controller_config.controller_name,
        image_tag,
    )
    kind_load_cmd = "kind load docker-image %s" % (image)
    print("Loading image %s to kind nodes..." % (image))
    if cmd_early_exit(kind_load_cmd, early_exit=False) != 0:
        print("Cannot load image %s locally, try to pull from remote" % (image))
        cmd_early_exit("docker pull %s" % (image))
        cmd_early_exit(kind_load_cmd)
