from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from http_target_discovery.providers.base_provider import BaseProvider
from http_target_discovery.schemas.target_schema import TargetSchema
from http_target_discovery.settings import settings

try:
    config.load_incluster_config()
except ConfigException:
    config.load_kube_config()

class KubernetesProvider(BaseProvider):
    _core = client.CoreV1Api()

    @classmethod
    def targets(cls) -> list[TargetSchema]:
        pods = cls._core.list_namespaced_pod(
            namespace=settings.kubernetes_namespace,
            label_selector=f"app={settings.kubernetes_deployment_app_name}"
        )

        targets: list[TargetSchema] = []
        for pod in pods.items:
            if pod.status.phase != "Running":
                continue

            ip: str = pod.status.pod_ip
            if not ip:
                continue

            port: int = pod.spec.containers[0].ports[0].container_port
            targets.append(TargetSchema(ip=ip, port=port))

        if not targets:
            raise RuntimeError("No available targets")
        return targets
