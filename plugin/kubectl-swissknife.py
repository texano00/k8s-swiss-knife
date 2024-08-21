import argparse, argcomplete
import utils.kubernetes as k8s
import utils.datatable as datatable
from config import VERSION


def version():
    print(VERSION)


def root_less_checker_emoji(is_root_less):
    if is_root_less == "N/A":
        return "❓"
    if is_root_less == False:
        return "⚠️"
    return "✅"


def root_less_checker(args):
    """Handler for root_less_checker."""
    kubernetes = k8s.Kubernetes()
    namespaces = [args["namespace"]] if args["namespace"] else ["default"]
    namespaces = (
        list(map(lambda item: item.metadata.name, kubernetes.get_namespaces().items))
        if args["all_namespaces"]
        else namespaces
    )
    data_output = []
    for namespace in namespaces:
        pods = kubernetes.get_pods(namespace)
        for pod in pods.items:
            for key, container in enumerate(pod.spec.containers):
                is_root_less = "N/A"
                is_started = pod.status.container_statuses[key].started
                if is_started:
                    output, err = kubernetes.exec_commands(
                        namespace,
                        pod.metadata.name,
                        container_name=container.name,
                        command="whoami",
                    )
                    is_root_less = False if (output.strip() == "root") else True
                    is_root_less = "N/A" if err else is_root_less
                data_output.append(
                    [
                        namespace,
                        pod.metadata.name,
                        container.name,
                        is_started,
                        is_root_less,
                        output if is_root_less != "N/A" else "",
                        root_less_checker_emoji(is_root_less),
                    ]
                )
    headers = [
        "Namespace",
        "Pod",
        "ContainerName",
        "isStarted",
        "isRooLess",
        "User",
        "Overall",
    ]

    table = datatable.ColoredTable()
    table.display_table(data_output, headers)


def healthcheck_warning(container_status, pod):
    last_termination_reason = (
        container_status.last_state.terminated.reason
        if container_status.last_state.terminated
        else ""
    )

    if last_termination_reason:
        return True, "⚠️"

    if pod.status.phase not in ["Running", "Succeeded"]:
        return True, "⚠️"

    return False, "✅"


def insert_newlines(string, every=30):
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i : i + every])
    return "\r".join(lines)


def healthcheck(args):
    """Handler for healthcheck."""
    kubernetes = k8s.Kubernetes()
    namespaces = [args["namespace"]] if args["namespace"] else ["default"]
    namespaces = (
        list(map(lambda item: item.metadata.name, kubernetes.get_namespaces().items))
        if args["all_namespaces"]
        else namespaces
    )
    show_only_warnings = args["show_only_warnings"]
    data_output = []
    for namespace in namespaces:
        pods = kubernetes.get_pods(namespace)
        for pod in pods.items:
            podHealth = "{phase} {reason} {message}".format(
                phase=pod.status.phase,
                reason=pod.status.reason if pod.status.reason else "",
                message=(
                    insert_newlines(pod.status.message) if pod.status.message else ""
                ),
            )
            for key, container in enumerate(pod.spec.containers):
                container_status = pod.status.container_statuses[key]
                last_termination_reason = (
                    container_status.last_state.terminated.reason
                    if container_status.last_state.terminated
                    else ""
                )
                last_termination_exit_code = (
                    container_status.last_state.terminated.exit_code
                    if container_status.last_state.terminated
                    else ""
                )
                last_termination_finished_at = (
                    container_status.last_state.terminated.finished_at
                    if container_status.last_state.terminated
                    else ""
                )
                last_termination = "{reason} {exit_code} {finished_at}".format(
                    reason=last_termination_reason,
                    exit_code=last_termination_exit_code,
                    finished_at=last_termination_finished_at,
                )
                warning, emoji = healthcheck_warning(container_status, pod)

                if show_only_warnings and not warning:
                    continue

                data_output.append(
                    [
                        namespace,
                        pod.metadata.name,
                        podHealth,
                        container_status.name,
                        True if container_status.state.running else False,
                        last_termination,
                        emoji,
                    ]
                )
    headers = [
        "Namespace",
        "Pod",
        "PodHealth",
        "ContainerName",
        "isRunning",
        "LastTermination",
        "Overall",
    ]

    table = datatable.ColoredTable()
    table.display_table(data_output, headers)


def get_resource(args):
    """Handler for get_resource."""
    kubernetes = k8s.Kubernetes()
    namespaces = [args["namespace"]] if args["namespace"] else ["default"]
    namespaces = (
        list(map(lambda item: item.metadata.name, kubernetes.get_namespaces().items))
        if args["all_namespaces"]
        else namespaces
    )
    data_output = []
    for namespace in namespaces:
        pods = kubernetes.get_pods(namespace)
        for pod in pods.items:
            for container in pod.spec.containers:
                limits = container.resources.limits or {}
                requests = container.resources.requests or {}
                data_output.append(
                    [
                        namespace,
                        pod.metadata.name,
                        container.name,
                        limits.get("cpu", "N/A"),
                        limits.get("memory", "N/A"),
                        requests.get("cpu", "N/A"),
                        requests.get("memory", "N/A"),
                    ]
                )
    headers = [
        "Namespace",
        "Pod",
        "ContainerName",
        "CPU Limit",
        "Memory Limit",
        "CPU Request",
        "Memory Request",
    ]

    table = datatable.ColoredTable()
    table.display_table(data_output, headers)


def main():
    """Main"""
    parser = argparse.ArgumentParser(
        description="k8s-SwissKnife. The utility you ever wanted."
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s v{VERSION}"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=False, help="Sub-command help"
    )

    # Sub-parser for the first command
    parser_one = subparsers.add_parser(
        "root_less_checker", help="Check rootless status of pods"
    )
    parser_one.add_argument(
        "--namespace",
        "-n",
        dest="namespace",
        type=str,
        help="Filter by namespace (optional, default to all namespaces)",
    )
    parser_one.add_argument(
        "--all", "-A", dest="all_namespaces", help="All namespaces", action="store_true"
    )
    parser_one.add_argument(
        "--show-only-warnings",
        "-sow",
        dest="show_only_warnings",
        help="Show only warnings",
        action="store_true",
        default=False,
    )

    # Sub-parser for the second command
    parser_two = subparsers.add_parser(
        "healthcheck",
        help="Check last termination reason of pods (ex. OOM reason). FS ❤️.",
    )
    parser_two.add_argument(
        "--namespace",
        "-n",
        dest="namespace",
        type=str,
        help="Filter by namespace (optional, default to all namespaces)",
    )
    parser_two.add_argument(
        "--all", "-A", dest="all_namespaces", help="All namespaces", action="store_true"
    )
    parser_two.add_argument(
        "--show-only-warnings",
        "-sow",
        dest="show_only_warnings",
        help="Show only warnings",
        action="store_true",
        default=False,
    )

    # Sub-parser for the third command
    parser_three = subparsers.add_parser(
        "get_resource", help="Get resource limits & requests of specific pods"
    )
    parser_three.add_argument(
        "--namespace",
        "-n",
        dest="namespace",
        type=str,
        help="Filter by namespace (optional, default to all namespaces)",
    )
    parser_three.add_argument(
        "--all", "-A", dest="all_namespaces", help="All namespaces", action="store_true"
    )

    argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())
    if args["command"] == "version":
        version()
    elif args["command"] == "root_less_checker":
        root_less_checker(args)
    elif args["command"] == "healthcheck":
        healthcheck(args)
    elif args["command"] == "get_resource":
        get_resource(args)


if __name__ == "__main__":
    main()
