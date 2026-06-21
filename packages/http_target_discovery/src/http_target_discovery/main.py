from http_target_discovery.settings import settings
from http_target_discovery.providers.base_provider import BaseProvider

def main() -> None:
    provider: type[BaseProvider] = settings.provider_strategy.provider
    print(provider.targets())

if __name__ == "__main__":
    main()
