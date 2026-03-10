# Blue/Green Runbook

## Active version check
kubectl get svc app-active -n final-task -o yaml

## Switch to green
./scripts/switch-green.sh

## Verify
kubectl port-forward -n final-task svc/app-active 8099:5000
curl http://localhost:8099/health
curl http://localhost:8099/

## Rollback to blue
./scripts/switch-blue.sh

## Verify rollback
curl http://localhost:8099/health
curl http://localhost:8099/
