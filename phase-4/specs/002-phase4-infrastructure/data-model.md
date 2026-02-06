# Data Model: Phase-4 Infrastructure

**Feature**: 002-phase4-infrastructure
**Date**: 2026-01-24
**Purpose**: Define infrastructure entities, configurations, and their relationships

---

## Overview

Phase-4 infrastructure does not introduce new application-level data models. Instead, it defines **infrastructure configurations** that describe how existing application entities (from Phase-3) are deployed and managed within containers and Kubernetes.

---

## 1. Container Image Configuration

### Entity: DockerImage

Represents a built container image ready for deployment.

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | Image name | `todo-backend` |
| tag | string | Version tag | `1.0.0`, `latest` |
| registry | string (optional) | Container registry | `localhost:5000`, `docker.io` |
| size | integer | Image size in MB | `180` |
| layers | integer | Number of layers | `12` |
| created | datetime | Build timestamp | `2026-01-24T12:00:00Z` |
| platform | string | Target platform | `linux/amd64` |

### Entity: Dockerfile

Configuration for building container images.

| Attribute | Type | Description |
|-----------|------|-------------|
| path | string | Location relative to project root |
| baseImage | string | Base image reference |
| stages | array | Build stages (for multi-stage) |
| exposedPorts | array[int] | Ports exposed by container |
| user | string | Runtime user (non-root) |
| healthcheck | object | Container health check config |

**Backend Dockerfile Configuration**:
```yaml
path: phase-4/backend/Dockerfile
baseImage: python:3.11-slim
stages:
  - name: builder
    purpose: Install dependencies and build
  - name: runtime
    purpose: Minimal runtime image
exposedPorts: [8000]
user: appuser (UID 1000)
healthcheck:
  command: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Frontend Dockerfile Configuration**:
```yaml
path: phase-4/frontend/Dockerfile
baseImage: node:20-alpine
stages:
  - name: deps
    purpose: Install npm dependencies
  - name: builder
    purpose: Build Next.js application
  - name: runtime
    purpose: Serve production build
exposedPorts: [3000]
user: nextjs (UID 1001)
healthcheck:
  command: ["CMD", "wget", "--spider", "http://localhost:3000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 2. Kubernetes Resource Configurations

### Entity: Deployment

Kubernetes Deployment specification for running application pods.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Deployment name |
| namespace | string | Kubernetes namespace |
| replicas | integer | Number of pod replicas |
| selector | object | Pod selector labels |
| template | PodTemplate | Pod specification |
| strategy | object | Rolling update strategy |

**Backend Deployment**:
```yaml
name: backend
namespace: todo-app
replicas: 2
selector:
  app: todo-backend
  tier: api
template:
  containers:
    - name: backend
      image: todo-backend:latest
      ports: [8000]
      resources:
        requests: {cpu: 100m, memory: 256Mi}
        limits: {cpu: 500m, memory: 512Mi}
      probes:
        liveness: {path: /health, port: 8000}
        readiness: {path: /health, port: 8000}
strategy:
  type: RollingUpdate
  maxSurge: 1
  maxUnavailable: 0
```

### Entity: Service

Kubernetes Service for network access to pods.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Service name |
| namespace | string | Kubernetes namespace |
| type | enum | ClusterIP, NodePort, LoadBalancer |
| selector | object | Pod selector labels |
| ports | array | Port mappings |

**Service Definitions**:
```yaml
# Backend Service
name: backend-service
type: ClusterIP
selector: {app: todo-backend}
ports:
  - name: http
    port: 8000
    targetPort: 8000

# Frontend Service
name: frontend-service
type: NodePort
selector: {app: todo-frontend}
ports:
  - name: http
    port: 3000
    targetPort: 3000
    nodePort: 30001
```

### Entity: ConfigMap

Non-sensitive configuration data.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | ConfigMap name |
| namespace | string | Kubernetes namespace |
| data | map[string]string | Key-value configuration |

**Backend ConfigMap**:
```yaml
name: backend-config
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
  APP_ENV: "development"
  CORS_ORIGINS: "http://localhost:3000,http://frontend-service:3000"
```

**Frontend ConfigMap**:
```yaml
name: frontend-config
data:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
  NODE_ENV: "production"
```

### Entity: Secret

Sensitive configuration data (templates only - values injected at deploy time).

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Secret name |
| namespace | string | Kubernetes namespace |
| type | string | kubernetes.io/Opaque |
| data | map[string]string | Base64-encoded values |

**Backend Secrets (template)**:
```yaml
name: backend-secrets
data:
  DATABASE_URL: <injected>
  OPENAI_API_KEY: <injected>
  BETTER_AUTH_SECRET: <injected>
```

---

## 3. Helm Chart Values Schema

### Entity: HelmValues

Top-level Helm values configuration.

```yaml
# values.yaml schema
global:
  namespace: string          # Kubernetes namespace
  imagePullPolicy: string    # IfNotPresent, Always, Never

backend:
  enabled: boolean           # Enable/disable backend
  replicaCount: integer      # Number of replicas
  image:
    repository: string       # Image name
    tag: string             # Image tag
  resources:
    requests:
      cpu: string           # CPU request (e.g., "100m")
      memory: string        # Memory request (e.g., "256Mi")
    limits:
      cpu: string           # CPU limit
      memory: string        # Memory limit
  probes:
    liveness:
      path: string          # Health check path
      initialDelaySeconds: integer
    readiness:
      path: string
      initialDelaySeconds: integer
  autoscaling:
    enabled: boolean
    minReplicas: integer
    maxReplicas: integer
    targetCPU: integer      # Target CPU utilization %

frontend:
  enabled: boolean
  replicaCount: integer
  image:
    repository: string
    tag: string
  resources:
    requests: {cpu: string, memory: string}
    limits: {cpu: string, memory: string}
  ingress:
    enabled: boolean
    host: string            # Ingress hostname

postgresql:
  enabled: boolean          # Use in-cluster Postgres
  persistence:
    enabled: boolean
    size: string           # PVC size (e.g., "10Gi")
  auth:
    username: string
    database: string
```

---

## 4. Entity Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                        Helm Chart (todo-app)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Backend    │  │   Frontend   │  │  PostgreSQL  │           │
│  │   Subchart   │  │   Subchart   │  │   Subchart   │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Deployment    │ │   Deployment    │ │  StatefulSet    │
│   (backend)     │ │   (frontend)    │ │  (postgres)     │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • ConfigMap     │ │ • ConfigMap     │ │ • ConfigMap     │
│ • Secret        │ │ • Service       │ │ • Secret        │
│ • Service       │ │ • Ingress       │ │ • Service       │
│ • HPA           │ └─────────────────┘ │ • PVC           │
└────────┬────────┘          │          └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
              Service Discovery via K8s DNS
              ┌──────────────┴──────────────┐
              │  backend-service:8000       │
              │  frontend-service:3000      │
              │  postgres-service:5432      │
              └─────────────────────────────┘
```

---

## 5. State Transitions

### Container Build Lifecycle

```
Source Code → Build → Image → Load → Deploy → Running
     │          │       │        │        │        │
     └── Dockerfile  Docker   Minikube  kubectl   Pods
                    build    image     apply    Ready
                              load
```

### Deployment States

| State | Description | Transition Trigger |
|-------|-------------|-------------------|
| Pending | Pod scheduled, containers starting | Pod creation |
| Running | All containers running | All probes pass |
| Updating | Rolling update in progress | helm upgrade |
| Scaled | Replicas changed | HPA or manual scale |
| Degraded | Some pods unhealthy | Probe failures |
| Failed | Deployment failed | Image pull error, crash loop |

### Helm Release Lifecycle

```
Not Installed → Installed → Upgraded → Rolled Back
      │             │           │            │
   helm install  helm status  helm upgrade  helm rollback
```

---

## 6. Validation Rules

### Container Image Validation

- Image tag MUST follow semantic versioning or be `latest`
- Image MUST pass security scan with no critical vulnerabilities
- Image size SHOULD be under 500MB for backend, 200MB for frontend
- Image MUST include health check command

### Kubernetes Resource Validation

- All resources MUST specify resource requests and limits
- All Deployments MUST include liveness and readiness probes
- All Services MUST have descriptive names (not `service-1`)
- All Secrets MUST use stringData (not base64 in templates)
- Namespace MUST match global.namespace value

### Helm Chart Validation

- Chart.yaml MUST include version, appVersion, description
- All values MUST have documented defaults
- Templates MUST pass `helm lint`
- NOTES.txt MUST include access instructions
