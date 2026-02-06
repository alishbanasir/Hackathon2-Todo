# Phase-4 Infrastructure Makefile
# Build automation for Docker, Kubernetes, and Helm deployments

.PHONY: help build build-backend build-frontend push load-minikube \
        deploy deploy-k8s deploy-helm undeploy clean lint test \
        minikube-start minikube-stop logs

# Default target
help:
	@echo "Phase-4 Infrastructure Build Automation"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make build           - Build all Docker images"
	@echo "  make build-backend   - Build backend image only"
	@echo "  make build-frontend  - Build frontend image only"
	@echo "  make load-minikube   - Load images into Minikube"
	@echo ""
	@echo "Kubernetes Commands:"
	@echo "  make deploy-k8s      - Deploy using kubectl/kustomize"
	@echo "  make deploy-helm     - Deploy using Helm"
	@echo "  make undeploy        - Remove deployment"
	@echo ""
	@echo "Minikube Commands:"
	@echo "  make minikube-start  - Start Minikube cluster"
	@echo "  make minikube-stop   - Stop Minikube cluster"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make lint            - Lint Helm charts"
	@echo "  make logs            - View application logs"
	@echo "  make clean           - Clean up resources"

# Variables
BACKEND_IMAGE := todo-backend
FRONTEND_IMAGE := todo-frontend
IMAGE_TAG := latest
NAMESPACE := todo-app
HELM_RELEASE := todo-app

# Docker Build Commands
build: build-backend build-frontend
	@echo "All images built successfully"

build-backend:
	@echo "Building backend image..."
	docker build -t $(BACKEND_IMAGE):$(IMAGE_TAG) ./backend
	@echo "Backend image built: $(BACKEND_IMAGE):$(IMAGE_TAG)"

build-frontend:
	@echo "Building frontend image..."
	docker build -t $(FRONTEND_IMAGE):$(IMAGE_TAG) ./frontend
	@echo "Frontend image built: $(FRONTEND_IMAGE):$(IMAGE_TAG)"

# Minikube Commands
minikube-start:
	@echo "Starting Minikube..."
	minikube start --cpus=4 --memory=8192 --driver=docker
	minikube addons enable ingress
	minikube addons enable metrics-server
	@echo "Minikube started with ingress and metrics-server"

minikube-stop:
	@echo "Stopping Minikube..."
	minikube stop

load-minikube: build
	@echo "Loading images into Minikube..."
	minikube image load $(BACKEND_IMAGE):$(IMAGE_TAG)
	minikube image load $(FRONTEND_IMAGE):$(IMAGE_TAG)
	@echo "Images loaded into Minikube"

# Kubernetes Deployment (kubectl/kustomize)
deploy-k8s:
	@echo "Deploying with kubectl..."
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -k k8s/overlays/dev -n $(NAMESPACE)
	@echo "Deployment complete. Waiting for pods..."
	kubectl wait --for=condition=ready pod -l app=todo-backend -n $(NAMESPACE) --timeout=120s
	kubectl wait --for=condition=ready pod -l app=todo-frontend -n $(NAMESPACE) --timeout=120s
	@echo "All pods are ready"

# Helm Deployment
deploy-helm:
	@echo "Deploying with Helm..."
	helm upgrade --install $(HELM_RELEASE) ./charts/todo-app \
		--namespace $(NAMESPACE) \
		--create-namespace \
		--values ./charts/todo-app/values-dev.yaml \
		--wait
	@echo "Helm deployment complete"

deploy: load-minikube deploy-helm
	@echo "Full deployment complete"

# Undeploy
undeploy:
	@echo "Removing deployment..."
	-helm uninstall $(HELM_RELEASE) -n $(NAMESPACE)
	-kubectl delete namespace $(NAMESPACE)
	@echo "Deployment removed"

# Validation
lint:
	@echo "Linting Helm charts..."
	helm lint ./charts/todo-app
	@echo "Helm lint passed"

test:
	@echo "Running validation tests..."
	kubectl apply --dry-run=server -k k8s/overlays/dev
	helm template $(HELM_RELEASE) ./charts/todo-app --values ./charts/todo-app/values-dev.yaml > /dev/null
	@echo "All validation tests passed"

# Logs
logs:
	@echo "Fetching logs..."
	kubectl logs -f -l app=todo-backend -n $(NAMESPACE) --all-containers=true &
	kubectl logs -f -l app=todo-frontend -n $(NAMESPACE) --all-containers=true

logs-backend:
	kubectl logs -f -l app=todo-backend -n $(NAMESPACE) --all-containers=true

logs-frontend:
	kubectl logs -f -l app=todo-frontend -n $(NAMESPACE) --all-containers=true

# Clean up
clean:
	@echo "Cleaning up..."
	-docker rmi $(BACKEND_IMAGE):$(IMAGE_TAG)
	-docker rmi $(FRONTEND_IMAGE):$(IMAGE_TAG)
	-minikube image rm $(BACKEND_IMAGE):$(IMAGE_TAG)
	-minikube image rm $(FRONTEND_IMAGE):$(IMAGE_TAG)
	@echo "Cleanup complete"

# Docker Compose (local development)
up:
	docker-compose up -d
	@echo "Services started. Frontend: http://localhost:3000, Backend: http://localhost:8000"

down:
	docker-compose down

# Status
status:
	@echo "=== Minikube Status ==="
	-minikube status
	@echo ""
	@echo "=== Pods ==="
	-kubectl get pods -n $(NAMESPACE)
	@echo ""
	@echo "=== Services ==="
	-kubectl get svc -n $(NAMESPACE)
	@echo ""
	@echo "=== Helm Releases ==="
	-helm list -n $(NAMESPACE)
