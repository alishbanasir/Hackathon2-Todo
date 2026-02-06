# Implementation Plan: Phase-4 Infrastructure

**Branch**: `002-phase4-infrastructure` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for Docker containerization, Minikube orchestration, Helm charts, and AI operations tooling

---

## Summary

This plan implements Phase-4 infrastructure for the Todo AI Chatbot application, enabling deployment to Kubernetes via Minikube. The implementation covers:

1. **Containerization**: Multi-stage Docker builds for FastAPI backend and Next.js frontend
2. **Orchestration**: Kubernetes manifests for local Minikube deployment
3. **Package Management**: Helm umbrella chart with subcharts for modular deployment
4. **AI Operations**: kubectl-ai integration with documented kubectl fallbacks

---

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x/Node.js 20 (frontend)
**Primary Dependencies**: FastAPI, Next.js 14, Docker, Kubernetes 1.28, Helm 3.14
**Storage**: PostgreSQL 15 (containerized or external)
**Testing**: helm lint, kubectl apply --dry-run, docker build validation
**Target Platform**: Minikube (local), Kubernetes (cloud-ready)
**Project Type**: Web application (frontend + backend + database)
**Performance Goals**: Pod startup <60s, horizontal scaling 1-5 replicas
**Constraints**: Minikube resources (4 CPU, 8GB RAM), local image loading
**Scale/Scope**: Single cluster, 3 services, development/staging environments

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase IV Constraints (from Constitution)

| Constraint | Status | Implementation |
|------------|--------|----------------|
| Local First: MUST deploy on Minikube before cloud | PASS | Minikube is primary target |
| Helm Charts: Required for all Kubernetes resources | PASS | Umbrella chart with subcharts |
| ConfigMaps/Secrets: Environment-specific configuration externalized | PASS | Separate ConfigMaps and Secrets |
| Health Checks: Liveness and readiness probes required | PASS | HTTP probes on /health endpoints |

### Security Standards (from Constitution)

| Standard | Status | Implementation |
|----------|--------|----------------|
| NEVER commit secrets | PASS | Secret templates with envsubst |
| Input validation with Pydantic/Zod | PASS | Existing from Phase-3 |
| Rate limiting, CORS configuration | PASS | Existing from Phase-3 |

### Code Quality (from Constitution)

| Standard | Status | Implementation |
|----------|--------|----------------|
| Container images follow security best practices | PASS | Non-root users, minimal base images |
| Infrastructure-as-Code (IaC) | PASS | All K8s resources in version control |
| 12-factor app principles | PASS | Externalized config, stateless containers |

**Gate Status**: PASSED - All constitution requirements met

---

## Project Structure

### Documentation (this feature)

```text
phase-4/specs/002-phase4-infrastructure/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions (completed)
├── data-model.md        # Infrastructure entities (completed)
├── quickstart.md        # Deployment guide (completed)
├── checklists/          # Validation checklists
│   └── infrastructure-requirements.md
├── contracts/           # Resource schemas
│   ├── helm-values-schema.yaml
│   └── k8s-resources.yaml
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
phase-4/
├── backend/
│   ├── Dockerfile           # Multi-stage Python build (NEW)
│   ├── .dockerignore        # Existing
│   └── src/                 # Existing application code
├── frontend/
│   ├── Dockerfile           # Multi-stage Node.js build (NEW)
│   ├── .dockerignore        # (NEW)
│   └── ...                  # Existing application code
├── k8s/
│   ├── base/                # Base Kubernetes manifests (NEW)
│   │   ├── namespace.yaml
│   │   ├── backend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── secret.yaml
│   │   ├── frontend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── configmap.yaml
│   │   └── postgres/
│   │       ├── statefulset.yaml
│   │       ├── service.yaml
│   │       ├── configmap.yaml
│   │       ├── secret.yaml
│   │       └── pvc.yaml
│   └── overlays/            # Environment-specific patches (NEW)
│       ├── dev/
│       └── staging/
├── charts/
│   └── todo-app/            # Helm umbrella chart (NEW)
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-staging.yaml
│       ├── templates/
│       │   ├── _helpers.tpl
│       │   ├── NOTES.txt
│       │   └── namespace.yaml
│       └── charts/
│           ├── backend/
│           ├── frontend/
│           └── postgresql/
├── docs/
│   ├── minikube-setup.md    # (NEW)
│   ├── kubectl-ai-guide.md  # (NEW)
│   └── deployment-guide.md  # (NEW)
├── docker-compose.yml       # Existing (updated)
└── Makefile                 # Build automation (NEW)
```

**Structure Decision**: Web application structure with added infrastructure directories (k8s/, charts/, docs/). Maintains existing backend/frontend separation while adding Kubernetes deployment layer.

---

## Architecture Overview

### Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Build Pipeline                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Backend Dockerfile              Frontend Dockerfile         │
│  ┌─────────────────┐            ┌─────────────────┐         │
│  │ Stage 1: Builder│            │ Stage 1: Deps   │         │
│  │ python:3.11-slim│            │ node:20-alpine  │         │
│  │ - Install deps  │            │ - npm ci        │         │
│  └────────┬────────┘            └────────┬────────┘         │
│           │                              │                   │
│  ┌────────▼────────┐            ┌────────▼────────┐         │
│  │ Stage 2: Runtime│            │ Stage 2: Builder│         │
│  │ python:3.11-slim│            │ node:20-alpine  │         │
│  │ - Copy venv     │            │ - next build    │         │
│  │ - Non-root user │            └────────┬────────┘         │
│  │ - Port 8000     │                     │                   │
│  └─────────────────┘            ┌────────▼────────┐         │
│                                 │ Stage 3: Runtime│         │
│                                 │ node:20-alpine  │         │
│                                 │ - Standalone    │         │
│                                 │ - Non-root user │         │
│                                 │ - Port 3000     │         │
│                                 └─────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Minikube Cluster                          │
├─────────────────────────────────────────────────────────────┤
│  Namespace: todo-app                                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                      Ingress                          │   │
│  │              (nginx ingress controller)               │   │
│  │         todo.local → frontend-service                 │   │
│  │         todo.local/api → backend-service              │   │
│  └────────────────┬─────────────────┬───────────────────┘   │
│                   │                 │                        │
│  ┌────────────────▼───┐  ┌─────────▼────────────────┐       │
│  │  frontend-service  │  │    backend-service       │       │
│  │  (NodePort:30001)  │  │    (ClusterIP:8000)      │       │
│  └────────┬───────────┘  └───────────┬──────────────┘       │
│           │                          │                       │
│  ┌────────▼───────────┐  ┌───────────▼──────────────┐       │
│  │    Deployment      │  │      Deployment          │       │
│  │    frontend        │  │      backend             │       │
│  │    (2 replicas)    │  │      (2 replicas)        │       │
│  │  ┌─────┐ ┌─────┐   │  │   ┌─────┐ ┌─────┐        │       │
│  │  │ Pod │ │ Pod │   │  │   │ Pod │ │ Pod │        │       │
│  │  └─────┘ └─────┘   │  │   └─────┘ └─────┘        │       │
│  └────────────────────┘  └───────────┬──────────────┘       │
│                                      │                       │
│                          ┌───────────▼──────────────┐       │
│                          │   postgres-service       │       │
│                          │   (ClusterIP:5432)       │       │
│                          └───────────┬──────────────┘       │
│                          ┌───────────▼──────────────┐       │
│                          │    StatefulSet           │       │
│                          │    postgres              │       │
│                          │    (1 replica)           │       │
│                          │   ┌─────┐                │       │
│                          │   │ Pod │◄───┐           │       │
│                          │   └─────┘    │           │       │
│                          └──────────────┼───────────┘       │
│                                         │                    │
│                          ┌──────────────▼───────────┐       │
│                          │    PersistentVolumeClaim │       │
│                          │    postgres-data (10Gi)  │       │
│                          └──────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Service Discovery Flow

```
┌─────────────┐     HTTP      ┌─────────────────────┐
│   Browser   │──────────────▶│   Ingress           │
│             │               │   (todo.local)      │
└─────────────┘               └──────────┬──────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    │
           ┌───────────────┐    ┌───────────────┐            │
           │   frontend-   │    │   backend-    │            │
           │   service     │    │   service     │            │
           │   :3000       │    │   :8000       │            │
           └───────┬───────┘    └───────┬───────┘            │
                   │                    │                     │
                   │    Internal DNS    │                     │
                   │    ─────────────   │                     │
                   │                    │                     │
                   ▼                    ▼                     │
           ┌───────────────┐    ┌───────────────┐            │
           │   Frontend    │────│   Backend     │            │
           │   Pods        │API │   Pods        │            │
           │               │call│               │            │
           └───────────────┘    └───────┬───────┘            │
                                        │                     │
                                        │ K8s DNS:            │
                                        │ postgres-service    │
                                        ▼                     │
                                ┌───────────────┐            │
                                │   PostgreSQL  │            │
                                │   Pod         │            │
                                └───────────────┘            │
```

### Helm Chart Hierarchy

```
charts/todo-app/                 (Umbrella Chart)
├── Chart.yaml
│   name: todo-app
│   version: 1.0.0
│   dependencies:
│     - backend
│     - frontend
│     - postgresql
│
├── values.yaml                  (Default values)
│   global:
│     namespace: todo-app
│   backend: {...}
│   frontend: {...}
│   postgresql: {...}
│
└── charts/
    ├── backend/                 (Subchart)
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   └── templates/
    │       ├── deployment.yaml
    │       ├── service.yaml
    │       ├── configmap.yaml
    │       ├── secret.yaml
    │       └── hpa.yaml
    │
    ├── frontend/                (Subchart)
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   └── templates/
    │       ├── deployment.yaml
    │       ├── service.yaml
    │       ├── configmap.yaml
    │       └── ingress.yaml
    │
    └── postgresql/              (Subchart)
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── statefulset.yaml
            ├── service.yaml
            ├── configmap.yaml
            ├── secret.yaml
            └── pvc.yaml
```

---

## Implementation Phases

### Phase 1: Containerization (P1)

**Goal**: Create production-ready Docker images for backend and frontend

**Tasks**:
1. Create backend Dockerfile with multi-stage build
2. Create frontend Dockerfile with Next.js standalone output
3. Create .dockerignore files for both services
4. Update docker-compose.yml with build context
5. Test local builds and container startup

**Validation**:
- `docker build` completes without errors
- Container images are under size targets (backend <500MB, frontend <200MB)
- `docker-compose up` starts all services
- Health checks pass for both containers

### Phase 2: Kubernetes Manifests (P2)

**Goal**: Create base Kubernetes manifests for Minikube deployment

**Tasks**:
1. Create namespace and base directory structure
2. Create backend manifests (Deployment, Service, ConfigMap, Secret)
3. Create frontend manifests (Deployment, Service, ConfigMap)
4. Create PostgreSQL manifests (StatefulSet, Service, PVC)
5. Implement health probes and resource limits
6. Test with `kubectl apply --dry-run`

**Validation**:
- All manifests pass `kubectl apply --dry-run=server`
- Pods reach Running state in Minikube
- Services are accessible via kubectl port-forward
- Health endpoints respond correctly

### Phase 3: Helm Charts (P3)

**Goal**: Create Helm umbrella chart for streamlined deployment

**Tasks**:
1. Create chart structure with Chart.yaml and values.yaml
2. Create backend subchart with templated manifests
3. Create frontend subchart with ingress support
4. Create PostgreSQL subchart with persistence
5. Create environment-specific values files
6. Implement NOTES.txt with post-install instructions

**Validation**:
- `helm lint` passes for all charts
- `helm template` generates valid Kubernetes YAML
- `helm install --dry-run` succeeds
- Full deployment via `helm install` works

### Phase 4: AI Operations (P4)

**Goal**: Enable natural language cluster management with kubectl-ai

**Tasks**:
1. Document kubectl-ai installation and configuration
2. Create command mapping documentation
3. Document kagent integration (placeholder for Phase-5)
4. Create operational runbook with common commands
5. Test kubectl-ai with Minikube cluster

**Validation**:
- kubectl-ai correctly interprets 80% of test queries
- All operations have documented kubectl equivalents
- Runbook covers common operational scenarios

---

## Deployment Workflow

### Local Development Workflow

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Build images
docker build -t todo-backend:latest ./phase-4/backend
docker build -t todo-frontend:latest ./phase-4/frontend

# 3. Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# 4. Deploy with Helm
helm install todo-app ./phase-4/charts/todo-app \
  --namespace todo-app --create-namespace \
  --values ./phase-4/charts/todo-app/values-dev.yaml

# 5. Access application
minikube tunnel  # In separate terminal
# Open http://localhost:3000
```

### Update Workflow

```bash
# 1. Rebuild changed image
docker build -t todo-backend:latest ./phase-4/backend

# 2. Reload into Minikube
minikube image load todo-backend:latest

# 3. Upgrade Helm release
helm upgrade todo-app ./phase-4/charts/todo-app \
  --namespace todo-app \
  --values ./phase-4/charts/todo-app/values-dev.yaml

# 4. Verify rollout
kubectl rollout status deployment/backend -n todo-app
```

---

## Complexity Tracking

> No constitution violations requiring justification. Implementation follows all Phase IV constraints.

| Decision | Justification | Simpler Alternative Considered |
|----------|---------------|--------------------------------|
| Umbrella chart with subcharts | Enables independent versioning and reuse | Single chart - rejected for maintainability |
| Multi-stage Docker builds | Security and size requirements from constitution | Single-stage - rejected for security |
| Kustomize base + Helm | Base manifests for debugging, Helm for deployment | Helm only - rejected for transparency |

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Image size exceeds targets | Medium | Low | Multi-stage builds, Alpine base images |
| Minikube resource exhaustion | Medium | Medium | Conservative resource requests, HPA limits |
| kubectl-ai unavailability | Low | Low | All commands have kubectl equivalents |
| Secret management complexity | Low | High | Template-based approach with envsubst |

---

## Next Steps

After this plan is approved:

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement Phase 1 (Containerization) first as foundation
3. Validate containers work with docker-compose before K8s migration
4. Implement remaining phases in priority order

---

## References

- [Research Document](./research.md) - Technology decisions
- [Data Model](./data-model.md) - Infrastructure entities
- [Quick Start](./quickstart.md) - Deployment guide
- [Helm Values Schema](./contracts/helm-values-schema.yaml) - Values configuration
- [K8s Resource Contracts](./contracts/k8s-resources.yaml) - Manifest specifications
- [Feature Specification](./spec.md) - Requirements
