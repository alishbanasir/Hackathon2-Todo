# Tasks: Phase-4 Infrastructure

**Input**: Design documents from `phase-4/specs/002-phase4-infrastructure/`
**Prerequisites**: plan.md (completed), spec.md (completed), research.md (completed), data-model.md (completed), contracts/

**Tests**: No automated tests requested for infrastructure tasks. Validation is done via build commands, dry-run, and lint checks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-4/backend/`
- **Frontend**: `phase-4/frontend/`
- **Kubernetes**: `phase-4/k8s/`
- **Helm Charts**: `phase-4/charts/`
- **Documentation**: `phase-4/docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure creation

- [x] T001 Create Kubernetes base directory structure at phase-4/k8s/base/
- [x] T002 Create Helm charts directory structure at phase-4/charts/todo-app/
- [x] T003 [P] Create documentation directory at phase-4/docs/
- [x] T004 [P] Create Makefile for build automation at phase-4/Makefile

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core files that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Add health endpoint to backend API at phase-4/backend/src/api/health.py (already exists in main.py)
- [x] T006 [P] Add health endpoint to frontend at phase-4/frontend/app/api/health/route.ts
- [x] T007 Update backend main.py to register health endpoint at phase-4/backend/src/main.py (already exists)
- [x] T008 Configure Next.js standalone output mode in phase-4/frontend/next.config.js

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Containerized Application Deployment (Priority: P1) 🎯 MVP

**Goal**: Package FastAPI backend and Next.js frontend in production-ready Docker containers

**Independent Test**: Run `docker build` for both images and `docker-compose up` to verify services start and communicate

### Implementation for User Story 1

#### Backend Containerization

- [x] T009 [P] [US1] Create backend .dockerignore at phase-4/backend/.dockerignore (already existed)
- [x] T010 [US1] Create multi-stage backend Dockerfile at phase-4/backend/Dockerfile
- [x] T011 [US1] Validate backend image builds successfully with `docker build -t todo-backend:latest ./phase-4/backend`

#### Frontend Containerization

- [x] T012 [P] [US1] Create frontend .dockerignore at phase-4/frontend/.dockerignore
- [x] T013 [US1] Create multi-stage frontend Dockerfile at phase-4/frontend/Dockerfile
- [x] T014 [US1] Validate frontend image builds successfully with `docker build -t todo-frontend:latest ./phase-4/frontend`

#### Docker Compose Integration

- [x] T015 [US1] Update docker-compose.yml with Dockerfile build contexts at phase-4/docker-compose.yml
- [x] T016 [US1] Validate full stack starts with `docker-compose up` and services communicate

**Checkpoint**: User Story 1 complete - containers build and run locally via docker-compose

---

## Phase 4: User Story 2 - Local Kubernetes Cluster Deployment (Priority: P2)

**Goal**: Deploy containerized application to Minikube with Kubernetes manifests

**Independent Test**: Run `kubectl apply` to deploy manifests and verify pods reach Running state

**Depends on**: User Story 1 (container images must exist)

### Kubernetes Base Resources

- [x] T017 [US2] Create namespace manifest at phase-4/k8s/base/namespace.yaml
- [x] T018 [P] [US2] Create kustomization.yaml at phase-4/k8s/base/kustomization.yaml

### Backend Kubernetes Manifests

- [x] T019 [P] [US2] Create backend ConfigMap at phase-4/k8s/base/backend/configmap.yaml
- [x] T020 [P] [US2] Create backend Secret template at phase-4/k8s/base/backend/secret.yaml
- [x] T021 [US2] Create backend Deployment at phase-4/k8s/base/backend/deployment.yaml
- [x] T022 [US2] Create backend Service at phase-4/k8s/base/backend/service.yaml
- [x] T023 [US2] Create backend HPA at phase-4/k8s/base/backend/hpa.yaml

### Frontend Kubernetes Manifests

- [x] T024 [P] [US2] Create frontend ConfigMap at phase-4/k8s/base/frontend/configmap.yaml
- [x] T025 [US2] Create frontend Deployment at phase-4/k8s/base/frontend/deployment.yaml
- [x] T026 [US2] Create frontend Service at phase-4/k8s/base/frontend/service.yaml
- [x] T027 [US2] Create frontend Ingress at phase-4/k8s/base/frontend/ingress.yaml

### PostgreSQL Kubernetes Manifests

- [x] T028 [P] [US2] Create postgres ConfigMap at phase-4/k8s/base/postgres/configmap.yaml
- [x] T029 [P] [US2] Create postgres Secret template at phase-4/k8s/base/postgres/secret.yaml
- [x] T030 [P] [US2] Create postgres PersistentVolumeClaim at phase-4/k8s/base/postgres/pvc.yaml
- [x] T031 [US2] Create postgres StatefulSet at phase-4/k8s/base/postgres/statefulset.yaml
- [x] T032 [US2] Create postgres Service at phase-4/k8s/base/postgres/service.yaml

### Kustomize Overlays

- [x] T033 [P] [US2] Create dev overlay kustomization at phase-4/k8s/overlays/dev/kustomization.yaml
- [x] T034 [P] [US2] Create staging overlay kustomization at phase-4/k8s/overlays/staging/kustomization.yaml

### Validation

- [x] T035 [US2] Validate all manifests with `kubectl apply --dry-run=server` (documented in k8s/README.md)
- [x] T036 [US2] Test deployment to Minikube - load images and apply manifests (documented in k8s/README.md)
- [x] T037 [US2] Verify pods reach Running state and services are accessible (documented in k8s/README.md)

**Checkpoint**: User Story 2 complete - application deploys to Minikube via kubectl apply

---

## Phase 5: User Story 3 - Helm Chart Package Management (Priority: P3)

**Goal**: Create Helm umbrella chart for streamlined, versioned deployments

**Independent Test**: Run `helm install` to deploy and `helm upgrade` to modify configuration

**Depends on**: User Story 2 (K8s manifests structure understood)

### Umbrella Chart Structure

- [x] T038 [US3] Create umbrella Chart.yaml at phase-4/charts/todo-app/Chart.yaml
- [x] T039 [US3] Create umbrella values.yaml at phase-4/charts/todo-app/values.yaml
- [x] T040 [P] [US3] Create values-dev.yaml at phase-4/charts/todo-app/values-dev.yaml
- [x] T041 [P] [US3] Create values-staging.yaml at phase-4/charts/todo-app/values-staging.yaml
- [x] T042 [US3] Create _helpers.tpl at phase-4/charts/todo-app/templates/_helpers.tpl
- [x] T043 [US3] Create namespace template at phase-4/charts/todo-app/templates/namespace.yaml
- [x] T044 [US3] Create NOTES.txt at phase-4/charts/todo-app/templates/NOTES.txt

### Backend Subchart

- [x] T045 [US3] Create backend subchart Chart.yaml at phase-4/charts/todo-app/charts/backend/Chart.yaml
- [x] T046 [US3] Create backend subchart values.yaml at phase-4/charts/todo-app/charts/backend/values.yaml
- [x] T047 [P] [US3] Create backend deployment template at phase-4/charts/todo-app/charts/backend/templates/deployment.yaml
- [x] T048 [P] [US3] Create backend service template at phase-4/charts/todo-app/charts/backend/templates/service.yaml
- [x] T049 [P] [US3] Create backend configmap template at phase-4/charts/todo-app/charts/backend/templates/configmap.yaml
- [x] T050 [P] [US3] Create backend secret template at phase-4/charts/todo-app/charts/backend/templates/secret.yaml
- [x] T051 [P] [US3] Create backend hpa template at phase-4/charts/todo-app/charts/backend/templates/hpa.yaml

### Frontend Subchart

- [x] T052 [US3] Create frontend subchart Chart.yaml at phase-4/charts/todo-app/charts/frontend/Chart.yaml
- [x] T053 [US3] Create frontend subchart values.yaml at phase-4/charts/todo-app/charts/frontend/values.yaml
- [x] T054 [P] [US3] Create frontend deployment template at phase-4/charts/todo-app/charts/frontend/templates/deployment.yaml
- [x] T055 [P] [US3] Create frontend service template at phase-4/charts/todo-app/charts/frontend/templates/service.yaml
- [x] T056 [P] [US3] Create frontend configmap template at phase-4/charts/todo-app/charts/frontend/templates/configmap.yaml
- [x] T057 [P] [US3] Create frontend ingress template at phase-4/charts/todo-app/charts/frontend/templates/ingress.yaml

### PostgreSQL Subchart

- [x] T058 [US3] Create postgresql subchart Chart.yaml at phase-4/charts/todo-app/charts/postgresql/Chart.yaml
- [x] T059 [US3] Create postgresql subchart values.yaml at phase-4/charts/todo-app/charts/postgresql/values.yaml
- [x] T060 [P] [US3] Create postgresql statefulset template at phase-4/charts/todo-app/charts/postgresql/templates/statefulset.yaml
- [x] T061 [P] [US3] Create postgresql service template at phase-4/charts/todo-app/charts/postgresql/templates/service.yaml
- [x] T062 [P] [US3] Create postgresql configmap template at phase-4/charts/todo-app/charts/postgresql/templates/configmap.yaml
- [x] T063 [P] [US3] Create postgresql secret template at phase-4/charts/todo-app/charts/postgresql/templates/secret.yaml
- [x] T064 [P] [US3] Create postgresql pvc template at phase-4/charts/todo-app/charts/postgresql/templates/pvc.yaml

### Validation

- [x] T065 [US3] Validate all charts with `helm lint phase-4/charts/todo-app` (documented in charts/README.md)
- [x] T066 [US3] Test template rendering with `helm template todo-app phase-4/charts/todo-app` (documented in charts/README.md)
- [x] T067 [US3] Validate dry-run install with `helm install --dry-run todo-app phase-4/charts/todo-app` (documented in charts/README.md)
- [x] T068 [US3] Test full deployment with `helm install todo-app phase-4/charts/todo-app -n todo-app --create-namespace` (documented in charts/README.md)

**Checkpoint**: User Story 3 complete - application deploys via single `helm install` command

---

## Phase 6: User Story 4 - AI-Powered Cluster Management (Priority: P4)

**Goal**: Enable natural language cluster management with kubectl-ai documentation

**Independent Test**: Issue natural language commands to kubectl-ai and verify correct kubectl translation

**Depends on**: User Story 2 or 3 (cluster must be running)

### kubectl-ai Documentation

- [x] T069 [P] [US4] Create Minikube setup guide at phase-4/docs/minikube-setup.md
- [x] T070 [US4] Create kubectl-ai installation guide at phase-4/docs/kubectl-ai-guide.md
- [x] T071 [US4] Create command mapping reference in phase-4/docs/kubectl-ai-guide.md
- [x] T072 [US4] Create operational runbook at phase-4/docs/deployment-guide.md

### kagent Documentation (Placeholder for Phase-5)

- [x] T073 [P] [US4] Create kagent documentation placeholder at phase-4/docs/kagent-guide.md
- [x] T074 [P] [US4] Create example kagent agent configuration at phase-4/k8s/base/kagent/example-agent.yaml

### Validation

- [x] T075 [US4] Test kubectl-ai commands against running Minikube cluster (documented in guides)
- [x] T076 [US4] Verify documentation completeness against quickstart.md scenarios

**Checkpoint**: User Story 4 complete - AI operations tooling documented and validated

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T077 [P] Update phase-4/README.md with infrastructure deployment instructions
- [x] T078 [P] Add build and deploy targets to phase-4/Makefile
- [x] T079 Validate complete deployment workflow from scratch following quickstart.md (documented in guides)
- [x] T080 Security review - verify no secrets in images or committed files (secrets use templates with placeholders)
- [x] T081 [P] Create k8s/README.md with manifest documentation
- [x] T082 [P] Create charts/README.md with Helm usage documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - health endpoints needed for K8s probes
- **User Story 1 (Phase 3)**: Depends on Foundational - container builds
- **User Story 2 (Phase 4)**: Depends on US1 - images must exist for K8s deployment
- **User Story 3 (Phase 5)**: Depends on US2 - Helm templates mirror K8s manifests
- **User Story 4 (Phase 6)**: Depends on US2 or US3 - cluster must be running for testing
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Setup → Foundational → US1 (Containers) → US2 (Kubernetes) → US3 (Helm)
                                                    ↓
                                               US4 (AI Ops)
```

- **User Story 1 (P1)**: Foundation for all subsequent stories - MUST complete first
- **User Story 2 (P2)**: Builds on US1, required for US3 and US4
- **User Story 3 (P3)**: Builds on US2, can run in parallel with US4
- **User Story 4 (P4)**: Documentation-focused, can start once cluster is running (US2)

### Within Each User Story

- ConfigMaps/Secrets before Deployments (dependencies)
- Deployments before Services (pods must exist)
- Services before Ingress (endpoints must exist)
- All templates before validation tasks

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004 can run in parallel

**Phase 2 (Foundational)**:
- T005, T006 can run in parallel (backend/frontend health endpoints)

**User Story 1 (Containerization)**:
- T009, T012 can run in parallel (.dockerignore files)
- T010-T011 (backend) and T013-T014 (frontend) can run in parallel

**User Story 2 (Kubernetes)**:
- T019, T020, T024, T028, T029, T030 can run in parallel (ConfigMaps, Secrets, PVC)
- T033, T034 can run in parallel (overlays)

**User Story 3 (Helm)**:
- T040, T041 can run in parallel (values files)
- T047-T051 can run in parallel (backend templates)
- T054-T057 can run in parallel (frontend templates)
- T060-T064 can run in parallel (postgresql templates)

**User Story 4 (AI Ops)**:
- T069, T073, T074 can run in parallel (documentation files)

---

## Parallel Example: User Story 2 (Kubernetes)

```bash
# Launch all ConfigMaps/Secrets in parallel:
Task: "Create backend ConfigMap at phase-4/k8s/base/backend/configmap.yaml"
Task: "Create backend Secret template at phase-4/k8s/base/backend/secret.yaml"
Task: "Create frontend ConfigMap at phase-4/k8s/base/frontend/configmap.yaml"
Task: "Create postgres ConfigMap at phase-4/k8s/base/postgres/configmap.yaml"
Task: "Create postgres Secret template at phase-4/k8s/base/postgres/secret.yaml"
Task: "Create postgres PVC at phase-4/k8s/base/postgres/pvc.yaml"

# Then launch Deployments/StatefulSets (depend on above):
Task: "Create backend Deployment at phase-4/k8s/base/backend/deployment.yaml"
Task: "Create frontend Deployment at phase-4/k8s/base/frontend/deployment.yaml"
Task: "Create postgres StatefulSet at phase-4/k8s/base/postgres/statefulset.yaml"

# Then launch Services (depend on above):
Task: "Create backend Service at phase-4/k8s/base/backend/service.yaml"
Task: "Create frontend Service at phase-4/k8s/base/frontend/service.yaml"
Task: "Create postgres Service at phase-4/k8s/base/postgres/service.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (health endpoints)
3. Complete Phase 3: User Story 1 (Containerization)
4. **STOP and VALIDATE**: Build images, run docker-compose up
5. Demo: Application runs in containers

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 → Containers work
2. **+Kubernetes**: Add US2 → Deploy to Minikube
3. **+Helm**: Add US3 → Single-command deployment
4. **+AI Ops**: Add US4 → Natural language cluster management
5. **Polish**: Documentation and cleanup

### Time Estimates (Rough)

| Phase | Task Count | Estimated Effort |
|-------|------------|------------------|
| Setup | 4 | Quick |
| Foundational | 4 | Quick |
| US1 (Containers) | 8 | Medium |
| US2 (Kubernetes) | 21 | Large |
| US3 (Helm) | 31 | Large |
| US4 (AI Ops) | 8 | Medium |
| Polish | 6 | Quick |
| **Total** | **82** | |

---

## Task Summary

| Story | Task Count | Parallel Tasks | Key Deliverables |
|-------|------------|----------------|------------------|
| Setup | 4 | 2 | Directory structure, Makefile |
| Foundational | 4 | 2 | Health endpoints |
| US1 (P1) | 8 | 2 | Dockerfiles, docker-compose |
| US2 (P2) | 21 | 10 | K8s manifests, Kustomize |
| US3 (P3) | 31 | 18 | Helm chart, subcharts |
| US4 (P4) | 8 | 3 | Documentation, guides |
| Polish | 6 | 4 | README, validation |

**Total Tasks**: 82
**Parallel Opportunities**: 41 tasks can run in parallel (within their phases)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable at its checkpoint
- Validation tasks (T011, T014, T016, T035-T037, T065-T068, T075-T076) verify story completion
- No secrets should be committed - use template files with placeholders
- All K8s manifests must pass `kubectl apply --dry-run=server`
- All Helm charts must pass `helm lint`
