# Kubernetes Manifests for Todo App

This directory contains Kubernetes manifests for deploying the Todo AI Chatbot application.

## Structure

```
k8s/
├── base/                    # Base manifests (Kustomize)
│   ├── namespace.yaml       # Namespace definition
│   ├── kustomization.yaml   # Kustomize configuration
│   ├── backend/             # Backend API manifests
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── frontend/            # Frontend manifests
│   │   ├── configmap.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── postgres/            # PostgreSQL manifests
│       ├── configmap.yaml
│       ├── secret.yaml
│       ├── pvc.yaml
│       ├── statefulset.yaml
│       └── service.yaml
└── overlays/                # Environment-specific overlays
    ├── dev/                 # Development environment
    └── staging/             # Staging environment
```

## Prerequisites

1. Minikube installed and running
2. kubectl configured
3. Docker images built and loaded into Minikube

## Quick Start

### 1. Start Minikube

```bash
minikube start --driver=docker --cpus=4 --memory=8192
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Build and Load Images

```bash
# Build images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Load into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### 3. Set Up Secrets

Before deploying, replace the secret placeholders:

```bash
export DATABASE_URL="postgresql://todo_user:password@postgres-service:5432/todo_db"
export GOOGLE_API_KEY="your-google-api-key"
export BETTER_AUTH_SECRET="your-auth-secret"
export POSTGRES_PASSWORD="your-db-password"

# Apply with envsubst (or use sealed-secrets in production)
envsubst < k8s/base/backend/secret.yaml | kubectl apply -f -
envsubst < k8s/base/postgres/secret.yaml | kubectl apply -f -
```

### 4. Deploy with Kustomize

**Development Environment:**
```bash
kubectl apply -k k8s/overlays/dev
```

**Staging Environment:**
```bash
kubectl apply -k k8s/overlays/staging
```

**Production (base):**
```bash
kubectl apply -k k8s/base
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# View logs
kubectl logs -l app=todo-backend -n todo-app
kubectl logs -l app=todo-frontend -n todo-app
```

### 6. Access the Application

Add the following to `/etc/hosts`:
```
$(minikube ip) todo.local
```

Then access: http://todo.local

## Validation Commands

```bash
# Dry-run validation
kubectl apply -k k8s/base --dry-run=client

# Kustomize build (view rendered manifests)
kubectl kustomize k8s/base
kubectl kustomize k8s/overlays/dev

# Validate individual manifests
kubectl apply -f k8s/base/backend/deployment.yaml --dry-run=client -o yaml
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app
```

### Database connection issues
```bash
kubectl exec -it postgres-0 -n todo-app -- psql -U todo_user -d todo_db
```

### Ingress not working
```bash
minikube tunnel  # Required for LoadBalancer/Ingress on some setups
kubectl get ingress -n todo-app
```
