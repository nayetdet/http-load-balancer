from http_target_discovery.providers.docker_provider import DockerProvider
from http_target_discovery.providers.kubernetes_provider import KubernetesProvider

def main() -> None:
    print(DockerProvider.targets())
    print(KubernetesProvider.targets())

if __name__ == "__main__":
    main()
