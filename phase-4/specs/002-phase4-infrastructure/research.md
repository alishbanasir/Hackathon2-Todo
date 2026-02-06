# Research: Phase-4 Infrastructure

**Feature**: 002-phase4-infrastructure
**Date**: 2026-01-24
**Purpose**: Technology decisions and best practices for containerization, orchestration, and AI operations

---

## 1. Docker Containerization Strategy

### Decision: Multi-stage Builds with Distroless/Slim Base Images

**Rationale**: Multi-stage builds reduce final image size by 60-80% and eliminate build dependencies from runtime. This aligns with Constitution principle of security best practices.

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Single-stage build | Simple, fast to write | Large images (500MB+), includes dev tools | Rejected |
| Multi-stage with Alpine | Small base (~5MB), good package availability | musl libc compatibility issues with some Python packages | Rejected for backend |
| Multi-stage with Debian slim | Good compatibility, smaller than full Debian | Slightly larger than Alpine (~25MB) | **Selected for backend** |
| Multi-stage with distroless | Minimal attack surface, no shell | Debugging harder, no package manager | Consider for production |

### Backend Dockerfile Architecture

```
Stage 1: Builder (python:3.11-slim)
├── Install build dependencies (gcc, libpq-dev)
├── Create virtual environment
├── Install Python dependencies
└── Copy source code

Stage 2: Runtime (python:3.11-slim)
├── Copy virtual environment from builder
├── Copy application code
├── Create non-root user (appuser)
├── Set PYTHONUNBUFFERED=1
└── Expose port 8000
```

**Key Decisions**:
- Use `python:3.11-slim` for compatibility with asyncpg and psycopg2
- Create non-root user `appuser` (UID 1000) for security
- Use multi-stage to exclude build tools from final image
- Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`

### Frontend Dockerfile Architecture

```
Stage 1: Dependencies (node:20-alpine)
├── Copy package.json and package-lock.json
└── Run npm ci (clean install)

Stage 2: Builder (node:20-alpine)
├── Copy dependencies from stage 1
├── Copy source code
└── Run next build

Stage 3: Runtime (node:20-alpine)
├── Copy standalone build output
├── Copy static assets
├── Create non-root user (nextjs)
└── Expose port 3000
```

**Key Decisions**:
- Use Next.js standalone output mode for minimal image
- Leverage npm ci for reproducible builds
- Use Alpine for Node.js (no musl issues like Python)
- Create non-root user `nextjs` (UID 1001)

---

## 2. Minikube Deployment Strategy

### Decision: Docker Driver with Image Loading via `minikube image load`

**Rationale**: The docker driver is most compatible with Windows/WSL2 environments and allows direct image loading without a registry.

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Local registry (localhost:5000) | Standard Docker push/pull | Requires TLS or insecure registry config | Considered for CI |
| minikube image load | Direct, no registry needed | Slower for large images | **Selected for local dev** |
| minikube docker-env | Build directly in Minikube | Context switching confusing | Rejected |
| Remote registry (Docker Hub) | Universal access | Requires account, push time | Out of scope |

### Minikube Configuration

```yaml
Driver: docker
Kubernetes Version: v1.28.x (latest stable)
CPU: 4 cores
Memory: 8192 MB
Disk: 40 GB
Addons:
  - ingress (NGINX Ingress Controller)
  - metrics-server (for HPA)
  - dashboard (optional, for debugging)
```

### Image Loading Workflow

```bash
# 1. Build images locally
docker build -t todo-backend:latest ./phase-4/backend
docker build -t todo-frontend:latest ./phase-4/frontend

# 2. Load into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# 3. Verify
minikube image ls | grep todo
```

---

## 3. Kubernetes Manifest Architecture

### Decision: Separate Manifests per Resource Type with Kustomize Overlays

**Rationale**: Separate files enable independent updates and clear Git diffs. Kustomize provides native Kubernetes configuration management without Helm complexity for base manifests.

### Directory Structure

```
phase-4/k8s/
├── base/
│   ├── namespace.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── secret.yaml (template)
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── postgres/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml (template)
│   │   └── pvc.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── staging/
│   │   └── kustomization.yaml
│   └── prod/
│       └── kustomization.yaml
└── README.md
```

### Service Discovery Strategy

**Decision**: Use Kubernetes DNS for internal service discovery

```
Backend accessible at: backend-service.todo-app.svc.cluster.local:8000
Frontend accesses API via: http://backend-service:8000/api
```

**Frontend API Proxy Configuration**:
- Build-time: `NEXT_PUBLIC_API_URL` set to internal service URL
- Runtime in container: Next.js rewrites proxy `/api/*` to backend service
- Ingress exposes single entry point for external access

---

## 4. Helm Chart Architecture

### Decision: Umbrella Chart with Subcharts for Backend, Frontend, PostgreSQL

**Rationale**: Umbrella chart provides single `helm install` deployment while subcharts enable independent versioning and reuse.

### Chart Structure

```
phase-4/charts/
└── todo-app/
    ├── Chart.yaml              # Umbrella chart metadata
    ├── values.yaml             # Default values
    ├── values-dev.yaml         # Development overrides
    ├── values-staging.yaml     # Staging overrides
    ├── values-prod.yaml        # Production overrides
    ├── templates/
    │   ├── _helpers.tpl        # Template helpers
    │   ├── NOTES.txt           # Post-install instructions
    │   └── namespace.yaml      # Namespace creation
    └── charts/
        ├── backend/
        │   ├── Chart.yaml
        │   ├── values.yaml
        │   └── templates/
        │       ├── deployment.yaml
        │       ├── service.yaml
        │       ├── configmap.yaml
        │       ├── secret.yaml
        │       └── hpa.yaml
        ├── frontend/
        │   ├── Chart.yaml
        │   ├── values.yaml
        │   └── templates/
        │       ├── deployment.yaml
        │       ├── service.yaml
        │       ├── configmap.yaml
        │       └── ingress.yaml
        └── postgresql/
            ├── Chart.yaml
            ├── values.yaml
            └── templates/
                ├── statefulset.yaml
                ├── service.yaml
                ├── configmap.yaml
                ├── secret.yaml
                └── pvc.yaml
```

### Key Values Configuration

```yaml
# values.yaml (defaults)
global:
  namespace: todo-app
  imagePullPolicy: IfNotPresent

backend:
  replicaCount: 2
  image:
    repository: todo-backend
    tag: latest
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  probes:
    liveness:
      path: /health
      initialDelaySeconds: 30
    readiness:
      path: /health
      initialDelaySeconds: 10

frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
  resources:
    requests:
      cpu: 50m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

postgresql:
  enabled: true
  persistence:
    enabled: true
    size: 10Gi
```

---

## 5. AI Operations Tools

### kubectl-ai Integration

**Decision**: Use kubectl-ai for natural language cluster operations with documented fallback to standard kubectl

**Rationale**: kubectl-ai reduces barrier to entry for Kubernetes operations but may have limited availability. All operations must have documented kubectl equivalents.

**Installation**:
```bash
# Install via krew (kubectl plugin manager)
kubectl krew install ai

# Configure with API key
export OPENAI_API_KEY=<your-key>
kubectl ai configure
```

**Common Operations Mapping**:
| Natural Language | kubectl Equivalent |
|-----------------|-------------------|
| "show me all running pods" | `kubectl get pods -n todo-app` |
| "scale backend to 3 replicas" | `kubectl scale deployment backend -n todo-app --replicas=3` |
| "show backend logs" | `kubectl logs -f deployment/backend -n todo-app` |
| "describe the backend service" | `kubectl describe svc backend-service -n todo-app` |
| "what's wrong with my deployment" | `kubectl describe deployment backend -n todo-app` |

### kagent Integration

**Decision**: Defer kagent implementation to Phase-5 (microservices)

**Rationale**: kagent is designed for managing AI agents within Kubernetes, which is more relevant for the microservices phase where we'll have multiple AI-powered services. For Phase-4, focus on kubectl-ai for cluster operations.

**Phase-4 Scope**:
- Document kagent installation requirements
- Create placeholder configuration files
- Prepare integration points for Phase-5

**Phase-5 Integration Plan**:
- Deploy kagent operator to cluster
- Configure agent CRDs (Custom Resource Definitions)
- Implement AI agent health monitoring
- Set up agent lifecycle management

---

## 6. Health Checks and Probes

### Decision: HTTP Probes with Dedicated Health Endpoints

**Backend Health Check**:
```python
# /health endpoint
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "timestamp": "2026-01-24T12:00:00Z"
}
```

**Kubernetes Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

**Frontend Health Check**:
- Next.js provides `/api/health` endpoint
- Readiness: Check if Next.js server responds
- Liveness: Basic HTTP 200 check

---

## 7. Resource Management

### Decision: Conservative Defaults with HPA for Backend

**Rationale**: Start with conservative resource requests to ensure scheduling on Minikube, with HPA for automatic scaling under load.

**Backend Resources**:
```yaml
resources:
  requests:
    cpu: 100m      # 0.1 CPU core
    memory: 256Mi  # 256 MB RAM
  limits:
    cpu: 500m      # 0.5 CPU core
    memory: 512Mi  # 512 MB RAM
```

**HPA Configuration**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 1
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 8. Security Considerations

### Non-negotiable Security Practices

1. **No secrets in images**: Use Kubernetes Secrets with external references
2. **Non-root users**: All containers run as non-root (UID 1000+)
3. **Read-only filesystem**: Where possible, mount filesystem as read-only
4. **Network policies**: Restrict pod-to-pod communication (Phase-5)
5. **Resource limits**: Prevent resource exhaustion attacks

### Secret Management

```yaml
# secrets.yaml (template - values replaced at deploy time)
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  DATABASE_URL: "${DATABASE_URL}"
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
  BETTER_AUTH_SECRET: "${BETTER_AUTH_SECRET}"
```

**Deployment Command**:
```bash
# Substitute secrets from environment
envsubst < k8s/base/backend/secret.yaml | kubectl apply -f -
```

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Base Images | python:3.11-slim, node:20-alpine | Compatibility + size balance |
| Build Strategy | Multi-stage | Security + size reduction |
| Image Loading | minikube image load | Simple local dev workflow |
| K8s Manifests | Kustomize + Helm | Base flexibility + deploy simplicity |
| Helm Structure | Umbrella + subcharts | Single install + modular |
| Service Discovery | Kubernetes DNS | Native, no external deps |
| AI Operations | kubectl-ai primary, kubectl fallback | Enhanced DX with safety net |
| Health Checks | HTTP probes on /health | Standard K8s pattern |
| Scaling | HPA on CPU | Automatic load handling |
| Secrets | K8s Secrets with envsubst | Simple, no external deps |
