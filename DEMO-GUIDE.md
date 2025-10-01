# 🚀 HPA Demo Guide

## Quick Start Commands

### 1. Start Minikube
```bash
minikube start
```

### 2. Deploy Kubernetes Configuration
```bash
kubectl apply -k k8s/
```

### 3. Verify Deployment (Optional)
```bash
# Check pods are running
kubectl get pods -l app=api

# Check HPA is created
kubectl get hpa api-hpa

# Check service
kubectl get svc api-service
```

### 4. Run HPA Demo
```bash
./demo-hpa.sh
```

## 📊 Monitoring Links

- **K6 Load Test Dashboard**: http://localhost:5665
- **API Service**: http://localhost:8080 (via port-forward)

## 🔍 Manual Monitoring (Optional)

Open these in separate terminals to watch real-time:

```bash
# Watch HPA scaling
watch kubectl get hpa api-hpa

# Watch pods scaling
watch kubectl get pods -l app=api

# Watch resource usage
watch kubectl top pods -l app=api
```

## 📋 Demo Timeline (2 minutes)

- **0-10s**: Ramp to 60 users → HPA triggers
- **10s-1m10s**: 100 users → Scale to 4-6 pods  
- **1m10s-1m40s**: 120 users → Scale to 6-8 pods
- **1m40s-2m**: Scale down → Back to 2 pods

## 🎯 What to Watch

1. **K6 Dashboard**: Load metrics and user count
2. **Lens** (open manually): HPA and pod scaling visualization
3. **Terminal**: Real-time kubectl output

## 🛠️ Troubleshooting

```bash
# If pods not ready
kubectl describe pods -l app=api

# If HPA not working
kubectl describe hpa api-hpa

# Check metrics server
kubectl top nodes

# Restart demo
kubectl delete -k k8s/
kubectl apply -k k8s/
```

## 🧹 Cleanup

```bash
# Stop demo (Ctrl+C will auto-cleanup)
# Or manually clean up
kubectl delete -k k8s/
minikube stop
```
