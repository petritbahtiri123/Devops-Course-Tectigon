#!/usr/bin/env bash
set -euo pipefail

kubectl patch svc app-active -n final-task --type merge -p \
'{"spec":{"selector":{"app":"final-task-app","color":"green"}}}' >/dev/null

echo "Switched app-active to GREEN"
kubectl get svc app-active -n final-task -o=jsonpath='{.spec.selector.color}{"\n"}'
