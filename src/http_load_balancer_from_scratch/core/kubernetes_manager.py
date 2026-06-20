from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from http_load_balancer_from_scratch.schemas.target_schema import TargetSchema
from http_load_balancer_from_scratch.settings import settings

try:
    config.load_incluster_config()
except ConfigException:
    config.load_kube_config()

class KubernetesManager:
    __apps = client.AppsV1Api()
    __core = client.CoreV1Api()

    @classmethod
    def targets(cls) -> list[TargetSchema]:
        pods = cls.__core.list_namespaced_pod(
            namespace=settings.KUBERNETES_NAMESPACE,
            label_selector=f"app={settings.KUBERNETES_DEPLOYMENT_APP_NAME}"
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

    @classmethod
    def replicas(cls) -> int:
        scale = cls.__apps.read_namespaced_deployment_scale(
            name=settings.KUBERNETES_DEPLOYMENT_NAME,
            namespace=settings.KUBERNETES_NAMESPACE
        )

        return scale.spec.replicas or 0

    @classmethod
    def scale(cls, replicas: int) -> None:
        cls.__apps.patch_namespaced_deployment_scale(
            name=settings.KUBERNETES_DEPLOYMENT_NAME,
            namespace=settings.KUBERNETES_NAMESPACE,
            body={
                "spec": {
                    "replicas": replicas
                }
            }
        )

    @classmethod
    def scale_up(cls) -> None:
        cls.scale(cls.replicas() + 1)
    
    @classmethod
    def scale_down(cls) -> None:
        replicas: int = cls.replicas()
        cls.scale(max(0, replicas - 1))
