.PHONY: install http-load-balancer

install:
	uv sync --all-groups --all-packages

http-load-balancer:
	uv run python -m http_load_balancer
