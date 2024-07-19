import argparse
import utils.kubernetes as k8s
import utils.datatable as datatable

def command_one(arg1, arg2):
    """Handler for command_one."""
    print(f"Executing command_one with arg1={arg1} and arg2={arg2}")
    kubernetes = k8s.Kubernetes()
    namespaces = kubernetes.get_namespaces()
    data_output = []
    for namespace in namespaces.items:
        pods = kubernetes.get_pods(namespace.metadata.name)
        for pod in pods.items:
            output,err = kubernetes.exec_commands(namespace.metadata.name, pod.metadata.name, "whoami")
            is_root_less = False if (output.strip() == "root") else True
            is_root_less = "N/A" if err else is_root_less
            data_output.append([
                namespace.metadata.name,
                pod.metadata.name,
                is_root_less
            ])
    headers = ["Namespace", "Pod", "isRooLess"]

    table = datatable.ColoredTable()
    table.display_table(data_output, headers)

def command_two(arg1):
    """Handler for command_two."""
    print(f"Executing command_two with arg1={arg1}")

def main():
    parser = argparse.ArgumentParser(description='Generic CLI Utility')
    subparsers = parser.add_subparsers(dest='command', required=True, help='Sub-command help')

    # Sub-parser for the first command
    parser_one = subparsers.add_parser('command_one', help='Execute command one')
    parser_one.add_argument('arg1', type=str, help='Argument 1 for command_one')
    parser_one.add_argument('arg2', type=int, help='Argument 2 for command_one')

    # Sub-parser for the second command
    parser_two = subparsers.add_parser('command_two', help='Execute command two')
    parser_two.add_argument('arg1', type=str, help='Argument 1 for command_two')

    args = parser.parse_args()

    if args.command == 'command_one':
        command_one(args.arg1, args.arg2)
    elif args.command == 'command_two':
        command_two(args.arg1)

if __name__ == "__main__":
    main()
