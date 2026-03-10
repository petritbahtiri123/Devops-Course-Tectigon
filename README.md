# Final Task — Local Mini Platform (WSL Ubuntu)

## Overview

This repository contains a local end-to-end **mini platform** built and tested in **WSL Ubuntu**.  
It demonstrates a practical DevOps flow from local development to containerization, configuration generation, environment bootstrap, Kubernetes deployment, and blue/green release switching.

The project covers these main areas:

- **Docker**: containerized Flask application + PostgreSQL
- **Terraform**: generates configuration artifacts used by the platform
- **Ansible**: bootstraps the local environment and validates tooling
- **Kubernetes (kind)**: runs the application locally inside a cluster
- **Blue/Green deployment**: switch traffic between two app versions
- **Rollback**: revert traffic back to the previous version
- **Runbook + scripts**: simple operational workflow for testing and verification

---

## Goal

The goal of this project is to demonstrate this full flow locally:

**build → test → deploy → configure → observe → rollback**

This repository is intended as a practical final-task submission for trainer review.

---

## Architecture

The platform consists of:

- A **Flask web application**
- A **PostgreSQL database**
- A **Docker Compose** setup for local development
- A **Terraform module** that generates configuration artifacts
- An **Ansible playbook** that bootstraps the WSL environment
- A **kind Kubernetes cluster**
- Two app deployments in Kubernetes:
  - `app-blue`
  - `app-green`
- One active service:
  - `app-active`

Traffic is routed through `app-active` and can be switched between blue and green.

---

## Features Implemented

### Application
The Flask app exposes these endpoints:

- `GET /health` → health check
- `GET /` → returns application name and version
- `POST /messages` → stores a message in PostgreSQL
- `GET /messages` → returns stored messages

### Local Docker environment
- App container
- PostgreSQL container
- Health checks for both services
- Persistent DB volume

### Terraform
Terraform generates:

- `generated/k8s-values.json`
- `generated/inventory.ini`

It also demonstrates version-based configuration diffs.

### Ansible
Ansible bootstrap validates or prepares:

- local folder structure
- `.env` file presence
- tooling checks for:
  - `kubectl`
  - `kind`
  - `helm`

### Kubernetes
The project deploys:

- namespace
- PostgreSQL StatefulSet + Service
- Blue app Deployment + Service
- Green app Deployment + Service
- Active Service that points to blue or green

### Blue/Green switch
Traffic switching is done with:

- `scripts/switch-green.sh`
- `scripts/switch-blue.sh`

### Rollback
Rollback is performed by switching `app-active` back to the previous selector.

---

## Repository Structure

```text
.
├── ansible
│   ├── inventory.ini
│   ├── roles
│   │   └── bootstrap
│   │       └── tasks
│   │           └── main.yml
│   └── site.yml
├── app
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── docker-compose.yml
├── generated
│   ├── inventory.ini
│   └── k8s-values.json
├── k8s
│   ├── 00-namespace.yaml
│   ├── 01-postgres-secret.yaml
│   ├── 02-postgres.yaml
│   ├── 03-app-blue.yaml
│   ├── 04-app-green.yaml
│   └── 05-active-service.yaml
├── runbook.md
├── scripts
│   ├── ci
│   ├── switch-blue.sh
│   └── switch-green.sh
└── terraform
    ├── main.tf
    ├── outputs.tf
    ├── templates
    ├── terraform.tfstate
    ├── terraform.tfstate.backup
    └── variables.tf
Prerequisites

This project was built and tested in:

Windows

WSL Ubuntu

Docker Desktop with WSL integration enabled

Required tools:

Docker

Docker Compose

Terraform

Ansible

kubectl

kind

Helm

Git

Environment Used

This project was implemented in:

WSL Ubuntu

Local Kubernetes via kind

Local images loaded into kind with kind load docker-image

Application API
GET /health

Returns service health.

Example:

curl http://localhost:5000/health

Expected response:

{"status":"ok"}
GET /

Returns app metadata and version.

Example:

curl http://localhost:5000/

Expected response:

{"app":"final-task","version":"v1"}
POST /messages

Stores a message in the database.

Example:

curl -X POST http://localhost:5000/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"hello from wsl"}'

Expected response:

{"content":"hello from wsl","id":1}
GET /messages

Lists messages stored in PostgreSQL.

Example:

curl http://localhost:5000/messages

Expected response:

[
  {
    "content":"hello from wsl",
    "created_at":"2026-03-10T19:11:18.872559",
    "id":1
  }
]
Step 1 — Local Docker Run
Create environment file

Copy:

cp .env.example .env

If .env.example is missing, create .env manually with:

APP_VERSION=v1
APP_PORT=5000

DB_HOST=postgres
DB_PORT=5432
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=apppass

POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppass
Build and start containers
docker compose build
docker compose up -d
docker compose ps
Test the local Docker app
curl http://localhost:5000/health
curl http://localhost:5000/
curl -X POST http://localhost:5000/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"hello from wsl"}'
curl http://localhost:5000/messages
Verify persistence

Restart containers:

docker compose down
docker compose up -d
curl http://localhost:5000/messages

The previously inserted message should still exist.

Step 2 — Terraform

Terraform in this project does not provision cloud infrastructure.
Instead, it generates local configuration artifacts used by the rest of the platform.

Files generated

generated/k8s-values.json

generated/inventory.ini

Initialize Terraform
cd terraform
terraform init
Plan and apply
terraform plan
terraform apply -auto-approve
Check outputs
cd ..
cat generated/k8s-values.json
echo
cat generated/inventory.ini
Expected generated files

generated/k8s-values.json example:

{"app_port":5000,"app_version":"v1","db":{"host":"postgres","name":"appdb","password":"apppass","port":5432,"user":"appuser"},"namespace":"final-task"}

generated/inventory.ini example:

[local]
localhost ansible_connection=local

[local:vars]
app_version=v1
namespace=final-task
app_port=5000
db_host=postgres
db_port=5432
db_name=appdb
db_user=appuser
db_password=apppass
Test version diff
cd terraform
terraform plan -var="app_version=v2"
terraform apply -auto-approve -var="app_version=v2"

Then confirm the generated files changed from v1 to v2.

Step 3 — Ansible Bootstrap

Ansible prepares and validates the local WSL environment.

Run playbook
ansible-playbook -i ansible/inventory.ini ansible/site.yml -K
Verify tooling
kubectl version --client
kind version
helm version --short
Idempotency check

Run the playbook again:

ansible-playbook -i ansible/inventory.ini ansible/site.yml -K

It should complete without breaking the environment.

Step 4 — Create Local Kubernetes Cluster

This project uses kind for local Kubernetes.

Create cluster
kind create cluster --name final-task
Verify cluster
kubectl get nodes
kubectl cluster-info
kubectl get pods -A

Wait until the node becomes:

Ready
Step 5 — Build and Load App Images into kind

Two versions are used for blue/green:

final-task-app:v1

final-task-app:v2

Build images
docker build --build-arg APP_VERSION=v1 -t final-task-app:v1 ./app
docker build --build-arg APP_VERSION=v2 -t final-task-app:v2 ./app
Load images into kind
kind load docker-image final-task-app:v1 --name final-task
kind load docker-image final-task-app:v2 --name final-task
Step 6 — Deploy to Kubernetes
Apply manifests
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-postgres-secret.yaml
kubectl apply -f k8s/02-postgres.yaml
kubectl apply -f k8s/03-app-blue.yaml
kubectl apply -f k8s/04-app-green.yaml
kubectl apply -f k8s/05-active-service.yaml
Verify resources
kubectl get all -n final-task
kubectl get pods -n final-task

Wait until all pods are in Running state.

Blue/Green Deployment Model
Blue

Deployment: app-blue

Version: v1

Green

Deployment: app-green

Version: v2

Active service

Service: app-active

Initially, app-active routes to blue.

Switching changes the selector of app-active between:

color: blue

color: green

Step 7 — Test Blue/Green Switching
Start port-forward for active service
kubectl port-forward -n final-task svc/app-active 8099:5000

In another terminal:

curl http://localhost:8099/

Expected initial result:

{"app":"final-task","version":"v1"}
Switch to green
./scripts/switch-green.sh
Important note about verification

When verifying through kubectl port-forward, the port-forward session may stay tied to the originally selected backend.
So after switching the active service, stop the port-forward session and start it again before re-testing.

Restart:

kubectl port-forward -n final-task svc/app-active 8099:5000

Then test again:

curl http://localhost:8099/

Expected result after switch:

{"app":"final-task","version":"v2"}
Roll back to blue
./scripts/switch-blue.sh

Restart port-forward again:

kubectl port-forward -n final-task svc/app-active 8099:5000

Test again:

curl http://localhost:8099/

Expected result after rollback:

{"app":"final-task","version":"v1"}
Direct Green Verification

To verify that green is serving version v2 directly:

Port-forward green service
kubectl port-forward -n final-task svc/app-green 8100:5000
Test green directly
curl http://localhost:8100/

Expected result:

{"app":"final-task","version":"v2"}
Rollback Procedure

Rollback is implemented by re-pointing app-active back to blue.

Roll back command
./scripts/switch-blue.sh
Confirm selector
kubectl get svc app-active -n final-task -o=jsonpath='{.spec.selector.color}{"\n"}'

Expected result:

blue
Scripts
scripts/switch-green.sh

Switches the active service selector to green.

scripts/switch-blue.sh

Switches the active service selector back to blue.

Make sure scripts are executable:

chmod +x scripts/switch-green.sh scripts/switch-blue.sh
runbook.md

A simplified operational runbook is included in:

runbook.md

It contains the basic switch and rollback flow.

Acceptance Criteria Coverage

This project addresses the requested acceptance points as follows:

Docker

App opens on localhost

DB persistence works

Health checks implemented

Terraform

terraform apply generates local files

version changes produce diffs

outputs are exposed

Ansible

playbook runs successfully

playbook can be re-run

local tooling is validated

Kubernetes

local cluster runs

blue and green deployments exist

service switching works

rollback works

probes are configured

Notes / Limitations

This project is intentionally local and demo-oriented.

Terraform is used for artifact generation, not cloud provisioning.

Kubernetes verification via kubectl port-forward requires restarting the forward after a service switch for clean testing.

The repository is designed to demonstrate the requested flow in a trainer-review setting.

Jenkins structure is prepared conceptually, but if a full Jenkinsfile is not present in the repository, then Jenkins is not fully implemented yet and should not be claimed as complete.

Troubleshooting
Docker app not starting

Check:

docker compose ps
docker compose logs app --tail=100
docker compose logs postgres --tail=100
.env missing

Create it manually or copy from .env.example:

cp .env.example .env
kind node stays NotReady

Check:

kubectl get nodes -w
kubectl get pods -A
docker ps
Kubernetes app pod failing

Check:

kubectl get pods -n final-task
kubectl describe pod -n final-task <pod-name>
kubectl logs -n final-task <pod-name>
Port-forward not showing switched version

This can happen if the current port-forward session is still attached to the old backend.

Fix:

Stop port-forward

Start port-forward again

Re-test

Suggested Full Test Flow

From a fresh environment, the trainer can validate with this order:

Docker
cp .env.example .env
docker compose build
docker compose up -d
curl http://localhost:5000/health
curl http://localhost:5000/
curl -X POST http://localhost:5000/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"hello from wsl"}'
curl http://localhost:5000/messages
Terraform
cd terraform
terraform init
terraform apply -auto-approve
cd ..
cat generated/k8s-values.json
cat generated/inventory.ini
Ansible + kind
ansible-playbook -i ansible/inventory.ini ansible/site.yml -K
kind create cluster --name final-task
kubectl get nodes
Kubernetes blue/green
docker build --build-arg APP_VERSION=v1 -t final-task-app:v1 ./app
docker build --build-arg APP_VERSION=v2 -t final-task-app:v2 ./app
kind load docker-image final-task-app:v1 --name final-task
kind load docker-image final-task-app:v2 --name final-task

kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-postgres-secret.yaml
kubectl apply -f k8s/02-postgres.yaml
kubectl apply -f k8s/03-app-blue.yaml
kubectl apply -f k8s/04-app-green.yaml
kubectl apply -f k8s/05-active-service.yaml

kubectl get pods -n final-task
Verify blue
kubectl port-forward -n final-task svc/app-active 8099:5000
curl http://localhost:8099/
Switch to green
./scripts/switch-green.sh
kubectl port-forward -n final-task svc/app-active 8099:5000
curl http://localhost:8099/
Roll back to blue
./scripts/switch-blue.sh
kubectl port-forward -n final-task svc/app-active 8099:5000
curl http://localhost:8099/
Author

Petrit Bahtiri

Implemented in WSL Ubuntu as a local DevOps mini-platform final task.
