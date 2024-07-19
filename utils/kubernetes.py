"""Kubernetes module"""
import datetime
import logging
from kubernetes.client.rest import ApiException
from kubernetes import client, config
from kubernetes.stream import stream

class Kubernetes:
    """Kubernetes class"""

    def __init__(self):
        auth_strategy_mapper = {"incluster": config.load_incluster_config, "kubeconfig": config.load_kube_config}
        auth_strategy_mapper['kubeconfig']()
        self.v1_apps = client.AppsV1Api()
        self.v1_core = client.CoreV1Api()

    def get_namespaces(self):
        """get_namespaces"""
        namespace = self.v1_core.list_namespace()
        return namespace

    def get_deployments(self, namespace):
        """get_deployments"""
        deployments = self.v1_apps.list_namespaced_deployment(namespace=namespace)
        return deployments

    def restart_deployment(self, namespace, deployment):
        """restart_deployment"""
        logging.info("Restarting %s in ns %s", deployment, namespace)
        now = datetime.datetime.utcnow()
        now = str(now.isoformat("T") + "Z")
        body = {"spec": {"template": {"metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": now}}}}}
        try:
            self.v1_apps.patch_namespaced_deployment(deployment, namespace, body, pretty="true")
        except ApiException as exception:
            logging.error("Exception when calling AppsV1Api->read_namespaced_deployment_status: %s\n", exception)
        self.v1_apps = client.AppsV1Api()
        self.v1_core = client.CoreV1Api()

    def get_pods(self, namespace):
        """get_pods"""
        pods = self.v1_core.list_namespaced_pod(namespace=namespace)
        return pods
    

    def exec_commands(self, namespace, name, command):
        # Calling exec and waiting for response
        exec_command = [
            '/bin/sh',
            '-c',
            command]
        # When calling a pod with multiple containers running the target container
        # has to be specified with a keyword argument container=<name>.
        err = False
        resp = ""
        try:
            resp = stream(self.v1_core.connect_get_namespaced_pod_exec,
                        name,
                        namespace,
                        command=exec_command,
                        stderr=True, stdin=False,
                        stdout=True, tty=False)
        except Exception as e:
            print("ok")
            err = True

        print(resp)


        return resp, err


        # # Calling exec interactively
        # exec_command = ['/bin/sh']
        # resp = stream(api_instance.connect_get_namespaced_pod_exec,
        #             name,
        #             namespace,
        #             command=exec_command,
        #             stderr=True, stdin=True,
        #             stdout=True, tty=False,
        #             _preload_content=False)
        # commands = [
        #     "echo This message goes to stdout",
        #     "echo \"This message goes to stderr\" >&2",
        # ]

        # while resp.is_open():
        #     resp.update(timeout=1)
        #     if resp.peek_stdout():
        #         print(f"STDOUT: {resp.read_stdout()}")
        #     if resp.peek_stderr():
        #         print(f"STDERR: {resp.read_stderr()}")
        #     if commands:
        #         c = commands.pop(0)
        #         print(f"Running command... {c}\n")
        #         resp.write_stdin(c + "\n")
        #     else:
        #         break

        # resp.write_stdin("date\n")
        # sdate = resp.readline_stdout(timeout=3)
        # print(f"Server date command returns: {sdate}")
        # resp.write_stdin("whoami\n")
        # user = resp.readline_stdout(timeout=3)
        # print(f"Server user is: {user}")
        # resp.close()