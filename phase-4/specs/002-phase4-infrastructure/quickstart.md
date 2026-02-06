# Quick Start: Phase-4 Infrastructure

**Feature**: 002-phase4-infrastructure
**Date**: 2026-01-24
**Time to Deploy**: ~15 minutes (first time) / ~5 minutes (subsequent)

---

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Docker | 24.x+ | [docker.com/get-docker](https://docker.com/get-docker) |
| Minikube | 1.32+ | `winget install minikube` or `brew install minikube` |
| kubectl | 1.28+ | Installed with Minikube |
| Helm | 3.14+ | `winget install Helm.Helm` or `brew install helm` |

### Verify Installation

```bash
# Check all tools
docker --version      # Docker version 24.x.x
minikube version      # minikube version: v1.32.x
kubectl version       # Client Version: v1.28.x
helm version          # version.BuildInfo{Version:"v3.14.x"}
```

---

## Quick Deploy (5 Steps)

### Step 1: Start Minikube

```bash
# Start with recommended resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster is running
kubectl cluster-info
```

### Step 2: Build Container Images

```bash
# Navigate to phase-4 directory
cd phase-4

# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Verify images
docker images | grep todo
```

### Step 3: Load Images into Minikube

```bash
# Load images into Minikube's Docker daemon
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Verify images are available
minikube image ls | grep todo
```

### Step 4: Create Secrets

```bash
# Create secrets file from template
# IMPORTANT: Replace placeholder values with real credentials

export DATABASE_URL="postgresql+asyncpg://postgres:postgres@postgres-service:5432/todo_app"
export OPENAI_API_KEY="your-openai-api-key"
export BETTER_AUTH_SECRET="your-auth-secret"

# Apply secrets
envsubst < k8s/base/backend/secret.yaml | kubectl apply -f -
envsubst < k8s/base/postgres/secret.yaml | kubectl apply -f -
```

### Step 5: Deploy with Helm

```bash
# Install the todo-app chart
helm install todo-app ./charts/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./charts/todo-app/values-dev.yaml

# Watch deployment progress
kubectl get pods -n todo-app -w

# Wait for all pods to be Ready (CTRL+C to exit watch)
```

---

## Access the Application

### Option A: Minikube Tunnel (Recommended)

```bash
# Start tunnel in a new terminal
minikube tunnel

# Access the app at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Option B: NodePort Access

```bash
# Get Minikube IP
minikube ip

# Access the app at:
# Frontend: http://<minikube-ip>:30001
# Backend: http://<minikube-ip>:30000
```

### Option C: Port Forward (Development)

```bash
# Forward frontend
kubectl port-forward -n todo-app svc/frontend-service 3000:3000 &

# Forward backend
kubectl port-forward -n todo-app svc/backend-service 8000:8000 &

# Access at localhost:3000 and localhost:8000
```

---

## Verify Deployment

```bash
# Check all resources
kubectl get all -n todo-app

# Expected output:
# NAME                           READY   STATUS    RESTARTS   AGE
# pod/backend-xxx                1/1     Running   0          2m
# pod/frontend-xxx               1/1     Running   0          2m
# pod/postgres-0                 1/1     Running   0          2m
#
# NAME                       TYPE        CLUSTER-IP       PORT(S)
# service/backend-service    ClusterIP   10.96.x.x        8000/TCP
# service/frontend-service   NodePort    10.96.x.x        3000:30001/TCP
# service/postgres-service   ClusterIP   10.96.x.x        5432/TCP

# Check health endpoints
kubectl exec -n todo-app deploy/backend -- curl -s localhost:8000/health
```

---

## Common Operations

### View Logs

```bash
# Backend logs
kubectl logs -n todo-app -l app=todo-backend -f

# Frontend logs
kubectl logs -n todo-app -l app=todo-frontend -f

# All logs
kubectl logs -n todo-app --all-containers=true -f
```

### Scale Deployment

```bash
# Scale backend to 3 replicas
kubectl scale deployment backend -n todo-app --replicas=3

# Or use kubectl-ai (if installed)
kubectl ai "scale backend to 3 replicas"

# Verify scaling
kubectl get pods -n todo-app -l app=todo-backend
```

### Update Configuration

```bash
# Modify values and upgrade
helm upgrade todo-app ./charts/todo-app \
  --namespace todo-app \
  --values ./charts/todo-app/values-dev.yaml \
  --set backend.replicaCount=3
```

### Rollback

```bash
# View release history
helm history todo-app -n todo-app

# Rollback to previous revision
helm rollback todo-app 1 -n todo-app

# Verify rollback
kubectl rollout status deployment/backend -n todo-app
```

---

## Cleanup

### Uninstall Application

```bash
# Remove Helm release
helm uninstall todo-app -n todo-app

# Delete namespace (removes all resources)
kubectl delete namespace todo-app
```

### Stop Minikube

```bash
# Stop cluster (preserves data)
minikube stop

# Delete cluster (removes everything)
minikube delete
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod -n todo-app <pod-name>

# Common issues:
# - ImagePullBackOff: Image not loaded into Minikube
# - CrashLoopBackOff: Check container logs
# - Pending: Check resource constraints
```

### Image Not Found

```bash
# Reload image into Minikube
minikube image load todo-backend:latest

# Verify image is present
minikube image ls | grep todo
```

### Database Connection Failed

```bash
# Check PostgreSQL pod
kubectl logs -n todo-app postgres-0

# Verify secret exists
kubectl get secret -n todo-app backend-secrets -o yaml

# Test database connectivity from backend pod
kubectl exec -n todo-app deploy/backend -- \
  python -c "from sqlalchemy import create_engine; e=create_engine('$DATABASE_URL'); e.connect()"
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n todo-app

# Verify ingress controller is running
kubectl get pods -n ingress-nginx

# Add host entry if using custom hostname
# Windows: Edit C:\Windows\System32\drivers\etc\hosts
# Add: <minikube-ip> todo.local
```

---

## Next Steps

After successful deployment:

1. **Verify all features work**: Test the Todo AI Chatbot functionality
2. **Monitor resources**: `kubectl top pods -n todo-app`
3. **Set up kubectl-ai**: For natural language cluster management
4. **Review Helm values**: Customize for your environment

See the full [Implementation Plan](./plan.md) for detailed architecture documentation.
