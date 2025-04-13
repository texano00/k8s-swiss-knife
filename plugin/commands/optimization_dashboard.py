import time
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from kubernetes import client
import utils.kubernetes as k8s


def calculate_optimization(requests, usage):
    """Calculate optimization percentage."""
    if requests == 0:
        return 0
    if requests == 0 and usage == 0:
        return 100  # Fully optimized if no requests
    return max(0, (usage / requests) * 100)


def get_speedometer_color(percentage):
    """Get color based on optimization percentage."""
    if percentage < 50:
        return "red"
    elif 50 <= percentage < 70:
        return "yellow"
    return "green"


def fetch_metrics(namespace, pod_name, container_name):
    """Fetch resource usage metrics for a container."""
    metrics_api = client.CustomObjectsApi()
    try:
        metrics = metrics_api.get_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods",
            name=pod_name,
        )
        for container in metrics["containers"]:
            if container["name"] == container_name:
                cpu_usage = float(container["usage"]["cpu"].rstrip("n")) / 1e9  # Convert nanocores to cores
                memory_usage = float(container["usage"]["memory"].rstrip("Ki")) / 1024  # Convert Ki to Mi
                return cpu_usage, memory_usage
    except Exception:
        pass
    return 0, 0  # Default to 0 if metrics are unavailable


def parse_cpu(cpu_value):
    """Parse CPU value and convert to cores."""
    if (cpu_value.endswith("n")):  # Nanocores
        return float(cpu_value.rstrip("n")) / 1e9
    elif (cpu_value.endswith("m")):  # Millicores
        return float(cpu_value.rstrip("m")) / 1000
    else:  # Cores
        return float(cpu_value)


def parse_memory(memory_value):
    """Parse memory value and convert to Mi."""
    if (memory_value.endswith("Ki")):  # Kibibytes
        return float(memory_value.rstrip("Ki")) / 1024
    elif (memory_value.endswith("Mi")):  # Mebibytes
        return float(memory_value.rstrip("Mi"))
    elif (memory_value.endswith("Gi")):  # Gibibytes
        return float(memory_value.rstrip("Gi")) * 1024
    else:  # Assume bytes
        return float(memory_value) / (1024 * 1024)


def optimization_dashboard(args):
    kubernetes = k8s.Kubernetes()
    console = Console()

    namespaces = [args["namespace"]] if args["namespace"] else ["default"]
    namespaces = (
        list(map(lambda item: item.metadata.name, kubernetes.get_namespaces().items))
        if args["all_namespaces"]
        else namespaces
    )

    # Store previous values to detect changes
    previous_values = {}

    def render_dashboard():
        """Render the real-time dashboard."""
        table = Table(title="Cluster Optimization Dashboard", expand=True)
        table.add_column("Scope", justify="center", style="bold")
        table.add_column("CPU Optimization (%)", justify="center")
        table.add_column("Memory Optimization (%)", justify="center")

        # Overall cluster optimization
        total_cpu_requests = total_cpu_usage = 0
        total_memory_requests = total_memory_usage = 0

        for namespace in namespaces:
            pods = kubernetes.get_pods(namespace)
            for pod in pods.items:
                # Only consider running pods
                if pod.status.phase != "Running":
                    continue

                for container in pod.spec.containers:
                    requests = container.resources.requests or {}
                    cpu_request = parse_cpu(requests.get("cpu", "0")) if "cpu" in requests else 0
                    memory_request = parse_memory(requests.get("memory", "0")) if "memory" in requests else 0

                    cpu_usage, memory_usage = fetch_metrics(
                        namespace, pod.metadata.name, container.name
                    )

                    total_cpu_requests += cpu_request
                    total_memory_requests += memory_request
                    total_cpu_usage += cpu_usage
                    total_memory_usage += memory_usage

        cluster_cpu_optimization = calculate_optimization(
            total_cpu_requests, total_cpu_usage
        )
        cluster_memory_optimization = calculate_optimization(
            total_memory_requests, total_memory_usage
        )

        # Detect changes and apply blinking effect
        def get_blinking_text(key, value, color):
            if key in previous_values and previous_values[key] != value:
                # Alternate between a blinking circle and no circle
                circle = "●" if previous_values[key] % 2 == 0 else "○"
                previous_values[key] = value
                return Text(f"{value:.2f}% {circle}", style=color)
            else:
                previous_values[key] = value
                return Text(f"{value:.2f}%", style=color)

        table.add_row(
            "Cluster",
            get_blinking_text("cluster_cpu", cluster_cpu_optimization, get_speedometer_color(cluster_cpu_optimization)),
            get_blinking_text("cluster_memory", cluster_memory_optimization, get_speedometer_color(cluster_memory_optimization)),
        )

        # Per namespace optimization
        for namespace in namespaces:
            namespace_cpu_requests = namespace_cpu_usage = 0
            namespace_memory_requests = namespace_memory_usage = 0

            pods = kubernetes.get_pods(namespace)
            for pod in pods.items:
                # Only consider running pods
                if pod.status.phase != "Running":
                    continue

                for container in pod.spec.containers:
                    requests = container.resources.requests or {}
                    cpu_request = parse_cpu(requests.get("cpu", "0")) if "cpu" in requests else 0
                    memory_request = parse_memory(requests.get("memory", "0")) if "memory" in requests else 0

                    cpu_usage, memory_usage = fetch_metrics(
                        namespace, pod.metadata.name, container.name
                    )

                    namespace_cpu_requests += cpu_request
                    namespace_memory_requests += memory_request
                    namespace_cpu_usage += cpu_usage
                    namespace_memory_usage += memory_usage

            namespace_cpu_optimization = calculate_optimization(
                namespace_cpu_requests, namespace_cpu_usage
            )
            namespace_memory_optimization = calculate_optimization(
                namespace_memory_requests, namespace_memory_usage
            )

            table.add_row(
                f"Namespace: {namespace}",
                get_blinking_text(f"{namespace}_cpu", namespace_cpu_optimization, get_speedometer_color(namespace_cpu_optimization)),
                get_blinking_text(f"{namespace}_memory", namespace_memory_optimization, get_speedometer_color(namespace_memory_optimization)),
            )

        return Panel(table, title="Real-Time Optimization Dashboard", border_style="bold blue")

    # Use Live to continuously refresh the dashboard
    with Live(console=console, refresh_per_second=1) as live:
        while True:
            live.update(render_dashboard())  # Update the Live context with new data
            time.sleep(1)  # Refresh every second