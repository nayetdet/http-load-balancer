#!/bin/sh
set -eu
ulimit -n 4096
exec python -m http_load_balancer
