# HTTP Load Balancer

Este repositório é o trabalho final da disciplina de **Sistemas Operacionais 2026.1**.

O projeto implementa e avalia algoritmos de escalonamento e balanceamento de carga em um ambiente distribuído com orquestração de contêineres. A proposta é correlacionar, na prática, os conceitos vistos na disciplina de Sistemas Operacionais com o problema de decisão de qual servidor deve receber cada requisição em um sistema distribuído.

Ao longo da implementação, o projeto faz uso intenso de:

- virtualização com contêineres Docker;
- orquestração com Docker Swarm e Kubernetes;
- multithreading;
- controle de concorrência com `locks`.

## Visão Geral

O sistema é composto por três partes principais:

1. `http_load_balancer`
2. `http_target_discovery`
3. `sample_app`

O fluxo geral funciona assim:

1. O `http_target_discovery` descobre quais instâncias estão saudáveis e disponíveis.
2. Ele envia a lista de alvos para o `http_load_balancer`.
3. O `http_load_balancer` recebe as requisições HTTP na porta pública e decide, de acordo com o algoritmo configurado, para qual target encaminhá-las.
4. O `sample_app` responde às requisições e serve como aplicação de teste para observação do comportamento dos algoritmos.

## Arquitetura

### `http_load_balancer`

É o proxy reverso do projeto. Ele expõe:

- porta `8080` para tráfego externo;
- porta `9090` para a API interna de gerenciamento.

Ele mantém em memória:

- a lista atual de targets;
- a estratégia de escalonamento selecionada;
- estatísticas por target, como número de conexões e tempo de resposta.

### `http_target_discovery`

É o serviço responsável por descobrir os targets ativos e sincronizar o estado com o balanceador.

Ele suporta dois provedores:

- Docker;
- Kubernetes.

E dois modos de rede:

- `internal`;
- `published`;
- `both`.

### `sample_app`

É uma aplicação Flask simples usada para carga e validação. Ela expõe:

- `GET /`
- `GET /info`
- `GET /health`

## Algoritmos Implementados

O balanceador implementa os seguintes algoritmos:

### Estáticos

- `round_robin`
- `weighted_round_robin`
- `ip_hash`
- `sticky_round_robin`

### Dinâmicos

- `least_connections`
- `least_response_time`

### Resumo de cada estratégia

- `round_robin`: distribui as requisições ciclicamente entre os targets.
- `weighted_round_robin`: distribui proporcionalmente ao peso de cada target.
- `ip_hash`: usa o IP do cliente para produzir um hash e escolher sempre o mesmo target para o mesmo cliente, quando possível.
- `sticky_round_robin`: mantém um mapeamento persistente entre cliente e target, preservando afinidade por IP.
- `least_connections`: envia a requisição para o target com menos conexões ativas.
- `least_response_time`: escolhe o target com menor tempo de resposta registrado.

## Concorrência e Sincronização

O projeto usa multithreading em pontos centrais do sistema:

- cada conexão TCP aceita pelo servidor é tratada em uma thread separada;
- a leitura e atualização de estados compartilhados é protegida com `locks`;
- o discovery roda em um agendador periódico para sincronizar os alvos sem bloquear o balanceador;
- as estatísticas dos targets são atualizadas de forma segura em memória.

Isso permite discutir, na prática, tópicos clássicos de Sistemas Operacionais como:

- concorrência;
- sincronização;
- exclusão mútua;
- uso eficiente de recursos;
- isolamento por contêineres;
- escalabilidade em ambientes distribuídos.

## Estrutura Do Repositório

- `packages/http_load_balancer`: implementação do balanceador.
- `packages/http_target_discovery`: descoberta e sincronização dos targets.
- `packages/sample_app`: aplicação de exemplo.
- `k8s/`: manifests para Kubernetes.
- `kind/`: cluster local para testes com Kind.
- `compose.yaml`: base para execução em Docker Swarm / Compose.
- `scripts/hammer_load_balancer.py`: script simples de geração de carga.
- `docs/`: documentação e material de apoio.

## Requisitos

- Python `3.14`
- `uv`
- Docker
- Docker Compose ou Docker Swarm
- Kubernetes
- `kind` e `kubectl` para o ambiente local de cluster

## Setup Local

### 1. Instalar dependências

```bash
make install
```

Ou diretamente:

```bash
uv sync --all-groups --all-packages
```

### 2. Executar o balanceador

```bash
make http-load-balancer
```

Ou:

```bash
uv run python -m http_load_balancer
```

### 3. Executar a descoberta de targets

```bash
make http-target-discovery
```

Ou:

```bash
uv run python -m http_target_discovery
```

### 4. Executar a aplicação de teste

```bash
uv run python -m sample_app
```

## Configuração

Os serviços usam variáveis de ambiente com prefixos próprios.

### `http_load_balancer`

Prefixo: `LB_`

Principais variáveis:

- `LB_HOST` - host de bind, padrão `0.0.0.0`
- `LB_PROXY_PORT` - porta pública, padrão `8080`
- `LB_INTERNAL_PORT` - porta interna, padrão `9090`
- `LB_BUFFER_SIZE` - tamanho do buffer TCP, padrão `4096`
- `LB_BACKLOG` - backlog da fila de conexões, padrão `128`

O balanceador persiste o estado de rotacionamento em `settings/routing.yaml`.

### `http_target_discovery`

Prefixo: `DISCOVERY_`

Principais variáveis:

- `DISCOVERY_PROVIDER_STRATEGY` - `docker` ou `kubernetes`
- `DISCOVERY_NETWORK_STRATEGY` - `internal`, `published` ou `both`
- `DISCOVERY_LB_TARGETS_URL` - endpoint interno do balanceador, por exemplo `http://http-load-balancer-internal:9090/targets`
- `DISCOVERY_POLL_INTERVAL_SECONDS` - intervalo de sincronização, padrão `5`
- `DISCOVERY_REQUEST_TIMEOUT_SECONDS` - timeout das requisições HTTP, padrão `5`
- `DISCOVERY_DOCKER_TARGET_LABEL` - label usada para descobrir containers Docker, padrão `http-load-balancer.target`
- `DISCOVERY_KUBERNETES_DEPLOYMENT_NAME` - nome do deployment observado no Kubernetes
- `DISCOVERY_KUBERNETES_DEPLOYMENT_APP_NAME` - nome do app observado no Kubernetes
- `DISCOVERY_KUBERNETES_NAMESPACE` - namespace observado, padrão `default`

## Como Funciona

### Fluxo no balanceador

1. O servidor de proxy recebe a conexão na porta `8080`.
2. O request é lido manualmente via socket.
3. O algoritmo atual escolhe o target de acordo com a estratégia configurada.
4. A requisição é encaminhada ao target escolhido.
5. A resposta é repassada de volta ao cliente.
6. As estatísticas do target são atualizadas.

### Fluxo no discovery

1. O discovery consulta o provedor escolhido.
2. Ele identifica targets saudáveis e ativos.
3. Ele compara o snapshot atual com o último estado enviado.
4. Se houver mudança, sincroniza os targets via API interna do balanceador.

### Estratégia em Docker

O provider Docker busca containers com a label `http-load-balancer.target=true`, filtra apenas os que estão saudáveis e suporta descoberta por:

- IP interno do container;
- porta publicada;
- ambos, dependendo da estratégia de rede.

### Estratégia em Kubernetes

O provider Kubernetes observa:

- `Deployment`;
- `ReplicaSet`;
- `Pod`.

Ele considera apenas pods em estado `Running` e `Ready`, e descobre alvos por:

- IP do pod e porta do container;
- IP do nó e `hostPort`, quando aplicável.

## Kubernetes

O repositório contém manifests em `k8s/` para:

- `http_load_balancer`
- `http_target_discovery`
- `sample_app`

### Subir o cluster local com Kind

```bash
bash kind/setup.sh
```

Isso cria ou reaproveita o cluster definido em `kind/config.yaml`, exporta o kubeconfig e instala `metrics-server`, necessário para o `HorizontalPodAutoscaler`.

### Aplicar os manifests

```bash
kubectl apply -k k8s/
```

### Componentes principais no Kubernetes

- `http-load-balancer` exposto em `NodePort` na porta `30080`
- `http-load-balancer-internal` exposto internamente na porta `9090`
- `http-target-discovery` com permissões para consultar `Deployment`, `ReplicaSet` e `Pod`
- `sample-app` com `readinessProbe`, `livenessProbe` e `HPA`

## Docker Swarm / Compose

O arquivo `compose.yaml` descreve a base usada para orquestração com contêineres e replica a aplicação de teste com `deploy.replicas`.

Em um ambiente compatível com Swarm, a ideia é publicar as imagens e orquestrar os serviços a partir desse manifesto, preservando a lógica de descoberta e balanceamento do projeto.

## Teste De Carga

O script `scripts/hammer_load_balancer.py` faz uma carga simples contra o balanceador na URL padrão `http://127.0.0.1:30080`.

Execução:

```bash
python scripts/hammer_load_balancer.py
```

Ele dispara múltiplos workers em paralelo e contabiliza sucesso e falhas.

## Endpoints Úteis

### Balanceador

- `GET /targets`
- `PUT /targets`
- `POST /targets/reload`
- `GET /targets/stats`
- `PUT /targets/stats`

### Sample App

- `GET /`
- `GET /info`
- `GET /health`

## Observações

- O projeto foi organizado como workspace com `uv`.
- Cada pacote possui seu próprio `pyproject.toml` e seu próprio ponto de entrada.
- O código foi pensado para facilitar experimentos com escalonamento, afinidade, estatísticas de execução e comportamento sob concorrência.
