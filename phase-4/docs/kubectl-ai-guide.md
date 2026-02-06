# kubectl-ai Guide

kubectl-ai enables natural language interaction with Kubernetes clusters, translating human-readable commands into kubectl operations.

## Installation

### Prerequisites

- kubectl installed and configured
- OpenAI API key or compatible LLM endpoint
- Access to a Kubernetes cluster

### Install kubectl-ai

```bash
# Using go install
go install github.com/sozercan/kubectl-ai@latest

# Or download binary
curl -LO https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai_$(uname -s)_$(uname -m)
chmod +x kubectl-ai_*
sudo mv kubectl-ai_* /usr/local/bin/kubectl-ai
```

### Configure API Key

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Or use config file
mkdir -p ~/.config/kubectl-ai
echo "api_key: your-api-key" > ~/.config/kubectl-ai/config.yaml
```

## Basic Usage

### Natural Language Commands

```bash
# Get all pods
kubectl-ai "show me all pods in the todo-app namespace"

# Check pod status
kubectl-ai "what pods are not running in todo-app"

# Scale deployment
kubectl-ai "scale the backend deployment to 3 replicas in todo-app"

# View logs
kubectl-ai "show me the last 50 lines of logs from the backend pod"
```

### Command Mapping Reference

| Natural Language | kubectl Equivalent |
|------------------|-------------------|
| "show all pods" | `kubectl get pods -A` |
| "pods in todo-app namespace" | `kubectl get pods -n todo-app` |
| "describe the backend pod" | `kubectl describe pod -l app=todo-backend -n todo-app` |
| "backend logs" | `kubectl logs -l app=todo-backend -n todo-app` |
| "restart backend" | `kubectl rollout restart deployment/backend -n todo-app` |
| "scale backend to 5" | `kubectl scale deployment/backend --replicas=5 -n todo-app` |
| "what's wrong with pods" | `kubectl get events --sort-by=.lastTimestamp -n todo-app` |
| "delete crashed pods" | `kubectl delete pods --field-selector=status.phase=Failed -n todo-app` |

## Todo App Operations

### Deployment Operations

```bash
# Deploy the application
kubectl-ai "apply all manifests from k8s/base"

# Check deployment status
kubectl-ai "show deployment status in todo-app namespace"

# Watch pods come up
kubectl-ai "watch pods in todo-app namespace"
```

### Debugging

```bash
# Find failing pods
kubectl-ai "which pods are in CrashLoopBackOff in todo-app"

# Get pod events
kubectl-ai "show events for backend pods"

# Check resource usage
kubectl-ai "show cpu and memory usage for todo-app pods"

# Exec into container
kubectl-ai "exec into the backend pod and run bash"
```

### Scaling Operations

```bash
# Scale up
kubectl-ai "increase backend replicas to handle more traffic"

# Scale down
kubectl-ai "reduce frontend to 1 replica for maintenance"

# Autoscaling status
kubectl-ai "show HPA status for todo-app"
```

### Service & Networking

```bash
# Check services
kubectl-ai "list all services in todo-app"

# Check endpoints
kubectl-ai "show endpoints for backend service"

# Check ingress
kubectl-ai "describe the ingress in todo-app"

# Port forward
kubectl-ai "forward local port 8000 to backend service"
```

### Database Operations

```bash
# Check PostgreSQL
kubectl-ai "is the postgres pod healthy"

# View postgres logs
kubectl-ai "show postgres logs from the last hour"

# Check PVC
kubectl-ai "what's the status of postgres storage"

# Exec psql
kubectl-ai "connect to postgres and list databases"
```

## Advanced Usage

### Dry-Run Mode

```bash
# Preview without executing
kubectl-ai --dry-run "delete all pods in todo-app"
```

### Context Specification

```bash
# Specify cluster context
kubectl-ai --context=minikube "show all pods"
```

### Output Formatting

```bash
# JSON output
kubectl-ai "get backend deployment as json"

# YAML output
kubectl-ai "export backend deployment as yaml"

# Wide output
kubectl-ai "show pods with more details"
```

## Common Scenarios

### Application Not Starting

```bash
kubectl-ai "why isn't the backend starting in todo-app"
kubectl-ai "show me events for failed pods"
kubectl-ai "check if secrets are configured correctly"
```

### Performance Issues

```bash
kubectl-ai "which pods are using the most cpu in todo-app"
kubectl-ai "are any pods hitting memory limits"
kubectl-ai "show HPA scaling events"
```

### Rolling Update

```bash
kubectl-ai "update backend image to v2.0"
kubectl-ai "watch the rollout progress"
kubectl-ai "rollback if the deployment fails"
```

### Cleanup

```bash
kubectl-ai "delete completed jobs in todo-app"
kubectl-ai "remove pods stuck in terminating state"
kubectl-ai "clean up unused config maps"
```

## Safety Features

kubectl-ai includes safety features:

1. **Confirmation prompts** for destructive operations
2. **Dry-run mode** for previewing commands
3. **Namespace scoping** to prevent cluster-wide accidents
4. **Resource protection** for critical components

### Unsafe Commands

The following operations require explicit confirmation:
- `delete` operations on deployments/statefulsets
- `scale` to 0 replicas
- Namespace deletion
- ConfigMap/Secret deletion

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test connection
kubectl-ai "hello"
```

### Command Not Recognized

```bash
# Use more specific language
# Instead of: "fix pods"
# Use: "restart pods that are in error state in todo-app namespace"
```

### Slow Responses

```bash
# Use simpler queries
# Break complex operations into steps
# Check network connectivity to OpenAI API
```

## Best Practices

1. **Be specific** about namespaces and resource names
2. **Use dry-run** for destructive operations first
3. **Review translated commands** before execution
4. **Keep queries simple** for faster responses
5. **Use kubectl directly** for complex or scripted operations
