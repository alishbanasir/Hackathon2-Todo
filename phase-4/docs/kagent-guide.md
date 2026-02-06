# kagent Guide

kagent is a Kubernetes-native agent framework for autonomous cluster operations. This guide documents its use with the Todo AI Chatbot application.

> **Note**: kagent is an emerging technology. This documentation serves as a placeholder for future integration. Verify current capabilities and APIs before implementation.

## Overview

kagent enables:
- Autonomous monitoring and remediation
- Natural language cluster operations
- Event-driven workflows
- Self-healing applications

## Concepts

### Agent

An autonomous entity that monitors resources and takes actions based on defined policies.

```yaml
apiVersion: kagent.io/v1alpha1
kind: Agent
metadata:
  name: todo-monitor
spec:
  description: "Monitor Todo app health and auto-remediate issues"
  triggers:
    - type: event
      filter: "type=Warning,reason=Unhealthy"
  actions:
    - type: kubernetes
      command: "restart-pod"
```

### Trigger Types

| Type | Description | Use Case |
|------|-------------|----------|
| event | Kubernetes events | Pod failures, scaling events |
| schedule | Cron-based | Periodic health checks |
| metric | Threshold-based | CPU/memory alerts |
| webhook | External trigger | CI/CD integration |

### Action Types

| Type | Description | Example |
|------|-------------|---------|
| kubernetes | kubectl operations | Scale, restart, patch |
| notification | Alerts | Slack, email, PagerDuty |
| custom | User-defined | Scripts, webhooks |

## Installation

### Prerequisites

- Kubernetes 1.21+
- Helm 3.0+
- kubectl-ai (optional, for natural language)

### Install kagent

```bash
# Add Helm repository (placeholder)
helm repo add kagent https://kagent.io/charts
helm repo update

# Install kagent operator
helm install kagent kagent/kagent-operator \
  --namespace kagent-system \
  --create-namespace
```

## Todo App Integration

### Auto-Restart Agent

Automatically restart unhealthy pods:

```yaml
# phase-4/k8s/base/kagent/restart-agent.yaml
apiVersion: kagent.io/v1alpha1
kind: Agent
metadata:
  name: todo-restart-agent
  namespace: todo-app
spec:
  description: "Restart unhealthy Todo app pods"
  selector:
    matchLabels:
      app.kubernetes.io/part-of: todo-app
  triggers:
    - type: event
      filter:
        type: Warning
        reason: Unhealthy
        count: 3  # After 3 failures
  actions:
    - type: kubernetes
      operation: rollout-restart
      target: deployment
  cooldown: 5m
```

### Scaling Agent

Scale based on custom metrics:

```yaml
# phase-4/k8s/base/kagent/scaling-agent.yaml
apiVersion: kagent.io/v1alpha1
kind: Agent
metadata:
  name: todo-scaling-agent
  namespace: todo-app
spec:
  description: "Scale backend based on queue depth"
  triggers:
    - type: metric
      source: prometheus
      query: "todo_queue_depth > 100"
  actions:
    - type: kubernetes
      operation: scale
      target: deployment/backend
      params:
        replicas: "+2"  # Add 2 replicas
  maxReplicas: 10
  cooldown: 2m
```

### Database Backup Agent

Scheduled database backups:

```yaml
# phase-4/k8s/base/kagent/backup-agent.yaml
apiVersion: kagent.io/v1alpha1
kind: Agent
metadata:
  name: todo-backup-agent
  namespace: todo-app
spec:
  description: "Nightly database backup"
  triggers:
    - type: schedule
      cron: "0 2 * * *"  # 2 AM daily
  actions:
    - type: custom
      script: |
        kubectl exec postgres-0 -n todo-app -- \
          pg_dump -U todo_user todo_db | \
          gzip > /backups/todo_$(date +%Y%m%d).sql.gz
```

### Notification Agent

Alert on critical events:

```yaml
# phase-4/k8s/base/kagent/alert-agent.yaml
apiVersion: kagent.io/v1alpha1
kind: Agent
metadata:
  name: todo-alert-agent
  namespace: todo-app
spec:
  description: "Alert on critical failures"
  triggers:
    - type: event
      filter:
        type: Warning
        reason: CrashLoopBackOff
  actions:
    - type: notification
      channel: slack
      webhook: "${SLACK_WEBHOOK_URL}"
      message: |
        :warning: Pod crash detected in Todo App
        Namespace: {{ .event.namespace }}
        Pod: {{ .event.involvedObject.name }}
        Message: {{ .event.message }}
```

## Natural Language Operations

kagent can integrate with kubectl-ai for natural language commands:

```bash
# Via kagent CLI
kagent ask "scale the backend if response time exceeds 500ms"

# Creates an Agent resource automatically
kagent generate --from-prompt "restart pods on OOM kill"
```

## Best Practices

### 1. Use Cooldowns

Prevent action storms with cooldown periods:

```yaml
spec:
  cooldown: 5m  # Wait 5 minutes between actions
```

### 2. Set Limits

Cap automated scaling:

```yaml
spec:
  maxReplicas: 10
  minReplicas: 2
```

### 3. Selective Targeting

Use label selectors carefully:

```yaml
spec:
  selector:
    matchLabels:
      environment: production
      tier: api
```

### 4. Audit Trail

Enable logging for compliance:

```yaml
spec:
  audit:
    enabled: true
    retention: 30d
```

### 5. Dry-Run Mode

Test agents before enabling:

```yaml
spec:
  mode: dry-run  # Log actions without executing
```

## Monitoring kagent

```bash
# Check agent status
kubectl get agents -n todo-app

# View agent logs
kubectl logs -l app=kagent -n kagent-system

# Agent execution history
kubectl get agentexecutions -n todo-app
```

## Troubleshooting

### Agent Not Triggering

```bash
# Check events match filter
kubectl get events -n todo-app

# Verify agent status
kubectl describe agent <name> -n todo-app
```

### Action Failed

```bash
# Check execution logs
kubectl get agentexecution -n todo-app
kubectl logs <execution-pod> -n todo-app
```

### Permission Denied

Ensure kagent has necessary RBAC:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: kagent-role
  namespace: todo-app
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "patch", "update"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "delete"]
```

## Resources

- [kagent Documentation](https://kagent.io/docs) (placeholder)
- [kubectl-ai Integration](./kubectl-ai-guide.md)
- [Kubernetes Event-Driven Autoscaling (KEDA)](https://keda.sh)

## Future Roadmap

- Integration with OpenAI for intelligent decision-making
- Predictive scaling based on traffic patterns
- Cross-cluster agent coordination
- GitOps-native agent definitions
