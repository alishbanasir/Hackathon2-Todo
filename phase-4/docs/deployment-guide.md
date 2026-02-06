# Deployment Guide - Todo AI Chatbot

This operational runbook covers deploying and managing the Todo AI Chatbot application on Kubernetes.

## Quick Reference

| Task | Command |
|------|---------|
| Deploy (Kustomize) | `kubectl apply -k k8s/base` |
| Deploy (Helm) | `helm install todo-app charts/todo-app -n todo-app --create-namespace` |
| Check status | `kubectl get all -n todo-app` |
| View logs | `kubectl logs -l app=todo-backend -n todo-app` |
| Scale | `kubectl scale deployment/backend --replicas=3 -n todo-app` |
| Uninstall | `helm uninstall todo-app -n todo-app` |

## Prerequisites Checklist

- [ ] Minikube running with ingress addon enabled
- [ ] Docker images built and loaded
- [ ] Secrets configured (DATABASE_URL, GOOGLE_API_KEY, BETTER_AUTH_SECRET)
- [ ] kubectl configured to target cluster

## Deployment Methods

### Method 1: Kustomize (Development)

```bash
# 1. Build Docker images
docker build -t todo-backend:latest ./phase-4/backend
docker build -t todo-frontend:latest ./phase-4/frontend

# 2. Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# 3. Configure secrets
export DATABASE_URL="postgresql://todo_user:password@postgres-service:5432/todo_db"
export GOOGLE_API_KEY="your-google-api-key"
export BETTER_AUTH_SECRET="your-auth-secret"
export POSTGRES_PASSWORD="your-db-password"

# 4. Apply secrets with envsubst
envsubst < phase-4/k8s/base/backend/secret.yaml | kubectl apply -f -
envsubst < phase-4/k8s/base/postgres/secret.yaml | kubectl apply -f -

# 5. Deploy with Kustomize
kubectl apply -k phase-4/k8s/base

# 6. Wait for pods
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-app --timeout=120s
```

### Method 2: Helm (Recommended)

```bash
# 1. Build and load images (same as above)

# 2. Install with Helm
helm upgrade --install todo-app ./phase-4/charts/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./phase-4/charts/todo-app/values-dev.yaml \
  --set backend.secrets.databaseUrl="postgresql://todo_user:password@todo-app-postgresql-service:5432/todo_db" \
  --set backend.secrets.googleApiKey="your-google-api-key" \
  --set backend.secrets.betterAuthSecret="your-auth-secret" \
  --set postgresql.secrets.password="password" \
  --wait

# 3. Verify deployment
helm status todo-app -n todo-app
```

## Environment-Specific Deployments

### Development

```bash
helm upgrade --install todo-app ./phase-4/charts/todo-app \
  --namespace todo-app-dev \
  --create-namespace \
  --values ./phase-4/charts/todo-app/values-dev.yaml \
  --set backend.secrets.databaseUrl="$DATABASE_URL" \
  --set backend.secrets.googleApiKey="$GOOGLE_API_KEY" \
  --set backend.secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set postgresql.secrets.password="$POSTGRES_PASSWORD"
```

### Staging

```bash
helm upgrade --install todo-app ./phase-4/charts/todo-app \
  --namespace todo-app-staging \
  --create-namespace \
  --values ./phase-4/charts/todo-app/values-staging.yaml \
  --set backend.secrets.databaseUrl="$DATABASE_URL" \
  --set backend.secrets.googleApiKey="$GOOGLE_API_KEY" \
  --set backend.secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set postgresql.secrets.password="$POSTGRES_PASSWORD"
```

## Post-Deployment Verification

### Health Checks

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxx                 1/1     Running   0          2m
# frontend-xxx                1/1     Running   0          2m
# postgres-0                  1/1     Running   0          2m

# Check services
kubectl get svc -n todo-app

# Check endpoints
kubectl get endpoints -n todo-app
```

### Application Tests

```bash
# Test backend health
kubectl exec -it deploy/backend -n todo-app -- curl localhost:8000/health

# Test frontend health
kubectl exec -it deploy/frontend -n todo-app -- curl localhost:3000/api/health

# Test database connection
kubectl exec -it postgres-0 -n todo-app -- pg_isready -U todo_user -d todo_db
```

### Access Application

```bash
# Port forward for testing
kubectl port-forward svc/frontend-service 3000:3000 -n todo-app &
kubectl port-forward svc/backend-service 8000:8000 -n todo-app &

# Open http://localhost:3000

# Or use ingress (requires minikube tunnel)
minikube tunnel &
# Add to /etc/hosts: <minikube-ip> todo.local
# Open http://todo.local
```

## Scaling Operations

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment/backend --replicas=3 -n todo-app

# Verify scaling
kubectl get pods -l app=todo-backend -n todo-app
```

### Autoscaling

```bash
# Check HPA status
kubectl get hpa -n todo-app

# View HPA details
kubectl describe hpa backend-hpa -n todo-app
```

## Monitoring

### View Logs

```bash
# Backend logs
kubectl logs -l app=todo-backend -n todo-app --tail=100 -f

# Frontend logs
kubectl logs -l app=todo-frontend -n todo-app --tail=100 -f

# PostgreSQL logs
kubectl logs -l app=todo-postgres -n todo-app --tail=100
```

### Resource Usage

```bash
# Node resources (requires metrics-server)
kubectl top nodes

# Pod resources
kubectl top pods -n todo-app

# Container resources
kubectl top pods -n todo-app --containers
```

### Events

```bash
# Recent events
kubectl get events -n todo-app --sort-by=.lastTimestamp

# Warning events only
kubectl get events -n todo-app --field-selector type=Warning
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Common issues:
# - ImagePullBackOff: Image not loaded into Minikube
# - CrashLoopBackOff: Application error, check logs
# - Pending: Resource constraints, check node capacity
```

### Database Connection Issues

```bash
# Verify postgres is running
kubectl get pods -l app=todo-postgres -n todo-app

# Check postgres service
kubectl get svc postgres-service -n todo-app

# Test connection from backend
kubectl exec -it deploy/backend -n todo-app -- \
  python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Network Issues

```bash
# Check service endpoints
kubectl get endpoints -n todo-app

# Test inter-pod communication
kubectl exec -it deploy/frontend -n todo-app -- \
  curl http://backend-service:8000/health
```

### Secret Issues

```bash
# Verify secrets exist
kubectl get secrets -n todo-app

# Check secret data (base64 encoded)
kubectl get secret backend-secrets -n todo-app -o yaml
```

## Updates and Rollbacks

### Rolling Update

```bash
# Update image tag
kubectl set image deployment/backend backend=todo-backend:v2.0 -n todo-app

# Watch rollout
kubectl rollout status deployment/backend -n todo-app
```

### Rollback

```bash
# View history
kubectl rollout history deployment/backend -n todo-app

# Rollback to previous
kubectl rollout undo deployment/backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app
```

### Helm Updates

```bash
# Upgrade with new values
helm upgrade todo-app ./phase-4/charts/todo-app \
  --namespace todo-app \
  --values ./phase-4/charts/todo-app/values.yaml \
  --reuse-values \
  --set backend.image.tag=v2.0

# Rollback
helm rollback todo-app 1 -n todo-app
```

## Cleanup

### Remove Application

```bash
# Helm uninstall
helm uninstall todo-app -n todo-app

# Delete namespace (removes everything)
kubectl delete namespace todo-app

# Or delete specific resources
kubectl delete -k phase-4/k8s/base
```

### Remove PVC Data

```bash
# Delete PVC (data will be lost!)
kubectl delete pvc postgres-pvc -n todo-app
```

## Maintenance Tasks

### Backup Database

```bash
# Create backup
kubectl exec -it postgres-0 -n todo-app -- \
  pg_dump -U todo_user todo_db > backup.sql
```

### Restore Database

```bash
# Restore from backup
kubectl exec -i postgres-0 -n todo-app -- \
  psql -U todo_user todo_db < backup.sql
```

### Rotate Secrets

```bash
# Update secret
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="new-url" \
  --from-literal=GOOGLE_API_KEY="new-key" \
  --from-literal=BETTER_AUTH_SECRET="new-secret" \
  -n todo-app \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secrets
kubectl rollout restart deployment/backend -n todo-app
```
