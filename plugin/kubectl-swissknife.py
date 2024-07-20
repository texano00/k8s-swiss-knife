import argparse
import utils.kubernetes as k8s
import utils.datatable as datatable

def version(args):
    f = open(".version", "r")
    print(f.read())

def root_less_checker_emoji(is_root_less):
    if(is_root_less=="N/A"):
        return "❓"
    
    if(is_root_less == False):
        return "⚠️"
    
    return "✅"

def root_less_checker(args):
    """Handler for root_less_checker."""
    kubernetes = k8s.Kubernetes()
    namespaces = [args['namespace']] if args['namespace'] else list(map(lambda item: item.metadata.name, kubernetes.get_namespaces().items))
    data_output = []
    for namespace in namespaces:
        pods = kubernetes.get_pods(namespace)
        for pod in pods.items:
            for key,container in enumerate(pod.spec.containers):
                is_root_less = "N/A"
                is_started = pod.status.container_statuses[key].started
                if(is_started):
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

def command_two(arg1):
    """Handler for command_two."""
    print(f"Executing command_two with arg1={arg1}")

def main():
    parser = argparse.ArgumentParser(description='k8s-SwissKnife. The utility you ever wanted.')
    subparsers = parser.add_subparsers(dest='command', required=False, help='Sub-command help')

    parser_version = subparsers.add_parser('version', help='Version')

    # Sub-parser for the first command
    parser_one = subparsers.add_parser('root_less_checker', help='Check rootless status of pods')
    parser_one.add_argument('--namespace', '-n', dest='namespace', type=str, help='Filter by namespace (optional, default to all namespaces)')

    # Sub-parser for the second command
    parser_two = subparsers.add_parser('command_two', help='TODO Stay tuned')
    parser_two.add_argument('arg1', type=str, help='Argument 1 for command_two')

    args = vars(parser.parse_args())
    
    
    if args['command'] == 'root_less_checker':
        root_less_checker(args)
    elif args['command'] == 'version':
        version(args)
    elif args['command'] == 'command_two':
        command_two(args.arg1)

if __name__ == "__main__":
    main()
