# Todo App Helm Chart

An umbrella Helm chart for deploying the Todo AI Chatbot application to Kubernetes.

## Prerequisites

- Kubernetes 1.21+
- Helm 3.8+
- Minikube (for local development)

## Components

This umbrella chart includes the following subcharts:

| Component | Description | Default Port |
|-----------|-------------|--------------|
| backend | FastAPI API server | 8000 |
| frontend | Next.js web application | 3000 |
| postgresql | PostgreSQL database | 5432 |

## Installation

### Quick Start (Development)

```bash
# Add dependencies
helm dependency update ./charts/todo-app

# Install with development values
helm upgrade --install todo-app ./charts/todo-app \
  --namespace todo-app-dev \
  --create-namespace \
  --values ./charts/todo-app/values-dev.yaml \
  --set backend.secrets.databaseUrl="postgresql://todo_user:password@todo-app-postgresql-service:5432/todo_db" \
  --set backend.secrets.googleApiKey="your-api-key" \
  --set backend.secrets.betterAuthSecret="your-secret" \
  --set postgresql.secrets.password="password"
```

### Staging Deployment

```bash
helm upgrade --install todo-app ./charts/todo-app \
  --namespace todo-app-staging \
  --create-namespace \
  --values ./charts/todo-app/values-staging.yaml \
  --set backend.secrets.databaseUrl="$DATABASE_URL" \
  --set backend.secrets.googleApiKey="$GOOGLE_API_KEY" \
  --set backend.secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set postgresql.secrets.password="$POSTGRES_PASSWORD"
```

## Configuration

### Global Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.imagePullPolicy` | Image pull policy | `IfNotPresent` |
| `global.namespace` | Target namespace | `todo-app` |
| `global.environment` | Environment name | `development` |

### Backend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Number of replicas | `2` |
| `backend.image.repository` | Image repository | `todo-backend` |
| `backend.image.tag` | Image tag | `latest` |
| `backend.resources.requests.cpu` | CPU request | `100m` |
| `backend.resources.requests.memory` | Memory request | `256Mi` |
| `backend.autoscaling.enabled` | Enable HPA | `true` |
| `backend.secrets.databaseUrl` | Database connection URL | `""` |
| `backend.secrets.googleApiKey` | Google AI API key | `""` |

### Frontend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Number of replicas | `2` |
| `frontend.image.repository` | Image repository | `todo-frontend` |
| `frontend.image.tag` | Image tag | `latest` |
| `frontend.resources.requests.cpu` | CPU request | `100m` |
| `frontend.resources.requests.memory` | Memory request | `128Mi` |

### PostgreSQL Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable PostgreSQL deployment | `true` |
| `postgresql.image.tag` | PostgreSQL version | `15-alpine` |
| `postgresql.persistence.enabled` | Enable persistent storage | `true` |
| `postgresql.persistence.size` | Storage size | `5Gi` |
| `postgresql.secrets.password` | Database password | `""` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `nginx` |
| `ingress.hosts[0].host` | Hostname | `todo.local` |

## Uninstallation

```bash
helm uninstall todo-app --namespace todo-app
```

## Troubleshooting

### View deployed resources

```bash
helm list -n todo-app
kubectl get all -n todo-app
```

### Check release status

```bash
helm status todo-app -n todo-app
```

### View rendered templates

```bash
helm template todo-app ./charts/todo-app --values ./charts/todo-app/values-dev.yaml
```

### Debug installation

```bash
helm upgrade --install todo-app ./charts/todo-app \
  --namespace todo-app --dry-run --debug
```
