import argparse
import utils.kubernetes as k8s
import utils.datatable as datatable
from config import VERSION

def version():
    print(VERSION)

def root_less_checker_emoji(is_root_less):
    if is_root_less=="N/A":
        return "❓"  
    if is_root_less == False:
        return "⚠️"
    return "✅"

def root_less_checker(args):
    """Handler for root_less_checker."""
    kubernetes = k8s.Kubernetes()
    namespaces = [args['namespace']] if args['namespace'] else ['default']
    namespaces = list(map(lambda item: item.metadata.name, kubernetes.get_namespaces().items)) if args['all_namespaces'] else namespaces
    data_output = []
    for namespace in namespaces:
        pods = kubernetes.get_pods(namespace)
        for pod in pods.items:
            for key,container in enumerate(pod.spec.containers):
                is_root_less = "N/A"
                is_started = pod.status.container_statuses[key].started
                if is_started:
                    output,err = kubernetes.exec_commands(namespace, pod.metadata.name, container_name=container.name, command="whoami")
                    is_root_less = False if (output.strip() == "root") else True
                    is_root_less = "N/A" if err else is_root_less
                data_output.append([
                    namespace,
                    pod.metadata.name,
                    container.name,
                    is_started,
                    is_root_less,
                    output if is_root_less!="N/A" else '',
                    root_less_checker_emoji(is_root_less)
                ])
    headers = ["Namespace", "Pod", "ContainerName", "isStarted", "isRooLess", "User", "Overall"]

    table = datatable.ColoredTable()
    table.display_table(data_output, headers)

def last_termination_reason_checker_emoji(last_termination_reason):
    if last_termination_reason:
        return "⚠️"
    return "✅"

def last_termination_reason_checker(args):
    """Handler for last_termination_reason_checker."""
    kubernetes = k8s.Kubernetes()
    namespaces = [args['namespace']] if args['namespace'] else ['default']
    namespaces = list(map(lambda item: item.metadata.name, kubernetes.get_namespaces().items)) if args['all_namespaces'] else namespaces

    data_output = []
    for namespace in namespaces:
        pods = kubernetes.get_pods(namespace)
        for pod in pods.items:
            for key,container in enumerate(pod.spec.containers):
                last_termination_reason = pod.status.container_statuses[key].last_state.terminated.reason if pod.status.container_statuses[key].last_state.terminated else ''
                last_termination_exit_code = pod.status.container_statuses[key].last_state.terminated.exit_code if pod.status.container_statuses[key].last_state.terminated else ''

                data_output.append([
                    namespace,
                    pod.metadata.name,
                    container.name,
                    last_termination_reason,
                    last_termination_exit_code,
                    last_termination_reason_checker_emoji(last_termination_reason)
                ])
    headers = ["Namespace", "Pod", "ContainerName", "LastTerminationReason", "LastTerminationExitCode", "Overall"]

    table = datatable.ColoredTable()
    table.display_table(data_output, headers)

def main():
    """Main"""
    parser = argparse.ArgumentParser(description='k8s-SwissKnife. The utility you ever wanted.')
    subparsers = parser.add_subparsers(dest='command', required=False, help='Sub-command help')

    parser_version = subparsers.add_parser('version', help='Version')

    # Sub-parser for the first command
    parser_one = subparsers.add_parser('root_less_checker', help='Check rootless status of pods')
    parser_one.add_argument('--namespace', '-n', dest='namespace', type=str, help='Filter by namespace (optional, default to all namespaces)')
    parser_one.add_argument('--all', '-A', dest='all_namespaces', help='All namespaces', action='store_true')

    # Sub-parser for the second command
    parser_two = subparsers.add_parser('last_termination_reason_checker', help='Check last termination reason of pods (ex. OOM reason). FS ❤️.')
    parser_two.add_argument('--namespace', '-n', dest='namespace', type=str, help='Filter by namespace (optional, default to all namespaces)')
    parser_two.add_argument('--all', '-A', dest='all_namespaces', help='All namespaces', action='store_true')

    args = vars(parser.parse_args()) 
    if args['command'] == 'root_less_checker':
        root_less_checker(args)
    elif args['command'] == 'version':
        version()
    elif args['command'] == 'last_termination_reason_checker':
        last_termination_reason_checker(args)

if __name__ == "__main__":
    main()
