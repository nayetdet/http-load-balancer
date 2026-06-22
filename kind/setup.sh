#!/usr/bin/env bash
set -euo pipefail

scripts_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cluster_name="${KIND_CLUSTER_NAME:-kind}"
config="${KIND_CONFIG:-${scripts_path}/config.yaml}"
control_plane="${cluster_name}-control-plane"

wait_ready() {
  local label="$1"
  local prefix=""
  shift

  [[ -n "${label}" ]] && prefix=" ${label}"

  for attempt in 1 2 3 4 5 6; do
    if "$@" --request-timeout=5s get --raw=/readyz >/dev/null 2>&1; then
      return 0
    fi

    echo "[kind] waiting for Kubernetes API${prefix} (${attempt}/6)"
    sleep 5
  done
  return 1
}

if kind get clusters | grep -qx "${cluster_name}"; then
  echo "[kind] cluster ${cluster_name} already exists, skipping creation"
else
  echo "[kind] creating cluster ${cluster_name} from ${config}"
  kind create cluster --name "${cluster_name}" --config "${config}"
fi

kind export kubeconfig --name "${cluster_name}"
if wait_ready "" kubectl; then
  kubectl_cmd=(kubectl)
elif wait_ready "inside ${control_plane}" docker exec -i "${control_plane}" kubectl --kubeconfig=/etc/kubernetes/admin.conf; then
  echo "[kind] host cannot reach the Kubernetes API, using kubectl inside ${control_plane}"
  kubectl_cmd=(docker exec -i "${control_plane}" kubectl --kubeconfig=/etc/kubernetes/admin.conf)
else
  echo "[kind] Kubernetes API is not reachable"
  exit 1
fi

manifest="$(curl -fsSL https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml)"
image="$(printf '%s\n' "${manifest}" | awk '/image:/ { print $2; exit }')"
echo "[kind] pulling ${image} on the host"
docker pull "${image}" >/dev/null
while IFS= read -r node; do
  [ -n "${node}" ] || continue
  echo "[kind] loading ${image} into ${node}"
  docker save "${image}" | docker exec -i "${node}" ctr --namespace=k8s.io images import --digests -
done < <(kind get nodes --name "${cluster_name}")

printf '%s\n' "${manifest}" | "${kubectl_cmd[@]}" apply --validate=false -f -
"${kubectl_cmd[@]}" -n kube-system patch deployment metrics-server --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"},
  {"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname"}
]' || true

"${kubectl_cmd[@]}" -n kube-system rollout status deployment/metrics-server --timeout=180s
"${kubectl_cmd[@]}" get apiservice v1beta1.metrics.k8s.io -o wide
"${kubectl_cmd[@]}" top nodes
