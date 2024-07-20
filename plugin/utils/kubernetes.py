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

    def get_pods(self, namespace, field_selector=''):
        """get_pods"""
        pods = self.v1_core.list_namespaced_pod(namespace=namespace, field_selector=field_selector)
        return pods
    

    def exec_commands(self, namespace, pod_name, container_name, command):
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
                        pod_name,
                        namespace,
                        container=container_name,
                        command=exec_command,
                        stderr=True, stdin=False,
                        stdout=True, tty=False)
            if('not found' in resp or '' == resp):
                raise Exception
        except Exception as e:
            err = True

        return resp, err