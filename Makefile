.PHONY: install http-load-balancer http-target-discovery

install:
	uv sync --all-groups --all-packages

http-load-balancer:
	uv run python -m http_load_balancer

http-target-discovery:
	uv run python -m http_target_discovery
