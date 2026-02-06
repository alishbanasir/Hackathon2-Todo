# Minikube Setup Guide

This guide covers setting up Minikube for local Kubernetes development with the Todo AI Chatbot application.

## Prerequisites

- Docker Desktop (or compatible container runtime)
- kubectl CLI
- 8GB+ RAM available
- 20GB+ disk space

## Installation

### Windows (with Chocolatey)

```powershell
choco install minikube
choco install kubernetes-cli
```

### macOS (with Homebrew)

```bash
brew install minikube
brew install kubectl
```

### Linux

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

## Starting Minikube

### Recommended Configuration for Todo App

```bash
# Start with recommended resources
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --kubernetes-version=v1.28.0

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard
```

### Verify Installation

```bash
# Check cluster status
minikube status

# Verify kubectl connection
kubectl cluster-info

# Check nodes
kubectl get nodes
```

## Loading Docker Images

The Todo app uses local Docker images. Load them into Minikube:

```bash
# Build images locally
docker build -t todo-backend:latest ./phase-4/backend
docker build -t todo-frontend:latest ./phase-4/frontend

# Load into Minikube's Docker daemon
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Verify images are loaded
minikube image list | grep todo
```

### Alternative: Use Minikube's Docker Daemon

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Build directly in Minikube
docker build -t todo-backend:latest ./phase-4/backend
docker build -t todo-frontend:latest ./phase-4/frontend

# Revert to local Docker
eval $(minikube docker-env -u)
```

## Accessing Services

### Port Forwarding

```bash
# Forward frontend
kubectl port-forward svc/frontend-service 3000:3000 -n todo-app

# Forward backend API
kubectl port-forward svc/backend-service 8000:8000 -n todo-app
```

### Minikube Tunnel (for LoadBalancer/Ingress)

```bash
# Run in separate terminal
minikube tunnel
```

### Ingress Access

```bash
# Get Minikube IP
minikube ip

# Add to hosts file (/etc/hosts or C:\Windows\System32\drivers\etc\hosts)
# <minikube-ip> todo.local

# Access application
curl http://todo.local
```

## Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard
```

## Useful Commands

### Cluster Management

```bash
# Stop cluster (preserves state)
minikube stop

# Start stopped cluster
minikube start

# Delete cluster completely
minikube delete

# SSH into Minikube node
minikube ssh
```

### Debugging

```bash
# View Minikube logs
minikube logs

# Check addon status
minikube addons list

# Profile management (multiple clusters)
minikube profile list
minikube start -p todo-cluster
```

### Resource Management

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n todo-app

# Scale deployment
kubectl scale deployment backend --replicas=3 -n todo-app
```

## Troubleshooting

### Docker Driver Issues

```bash
# Reset Docker driver
minikube delete
docker system prune -af
minikube start --driver=docker
```

### Image Pull Errors

If pods show `ImagePullBackOff`:
1. Ensure images are loaded: `minikube image list`
2. Check imagePullPolicy is `IfNotPresent` or `Never`
3. Verify image name matches exactly

### Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress -n todo-app

# Run tunnel for ingress access
minikube tunnel
```

### Out of Resources

```bash
# Check node resources
kubectl describe node minikube

# Increase Minikube resources
minikube stop
minikube config set memory 10240
minikube config set cpus 6
minikube start
```

## Configuration Reference

### Recommended Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| CPUs | 4 | Application + system overhead |
| Memory | 8192MB | Pods + buffers |
| Disk | 20GB | Images + volumes |
| Driver | docker | Most compatible |

### Environment Variables

```bash
export KUBECONFIG=~/.kube/config
export MINIKUBE_DRIVER=docker
export MINIKUBE_CPUS=4
export MINIKUBE_MEMORY=8192
```
