#!/bin/bash

# HPA Fast Demo Script
# Simple K6 load test to demonstrate HPA scaling

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}⚡ HPA Fast Demo${NC}"

# Quick checks
if ! command -v k6 &> /dev/null; then
    echo -e "${YELLOW}❌ k6 not installed. Run: brew install k6${NC}"
    exit 1
fi

if ! kubectl get hpa api-hpa &> /dev/null; then
    echo -e "${YELLOW}❌ HPA not found. Run: kubectl apply -k k8s/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ready!${NC}"

# Show current status
echo -e "\n${YELLOW}📊 Current Status:${NC}"
kubectl get hpa api-hpa
kubectl get pods -l app=api

# Setup port forwarding to service (more stable than pod)
echo -e "\n${BLUE}🔗 Setting up port forwarding...${NC}"
# Kill any existing port-forward on 8080
pkill -f "kubectl.*port-forward.*8080" 2>/dev/null || true

# Port-forward to service instead of pod (survives pod restarts)
kubectl port-forward svc/api-service 8080:80 > /dev/null 2>&1 &
PORT_FORWARD_PID=$!
echo -e "${GREEN}✅ Port-forward active: http://localhost:8080${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping port-forward...${NC}"
    kill $PORT_FORWARD_PID 2>/dev/null || true
    # Also kill any remaining port-forward processes
    pkill -f "kubectl.*port-forward.*8080" 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Wait for port-forward to be ready
sleep 2

echo -e "\n${BLUE}🚀 Starting Fast Demo...${NC}"
echo -e "${YELLOW}📊 K6 Web Dashboard: http://localhost:5665${NC}"
echo -e "${YELLOW}🔍 Open Lens manually to watch HPA scaling${NC}"
echo -e "\n${GREEN}⚡ Running K6 load test (2 minutes)...${NC}"

k6 run --out web-dashboard k6-load-test.js

echo -e "\n${GREEN}✅ Demo Complete!${NC}"
kubectl get hpa api-hpa
kubectl get pods -l app=api

# The trap will handle cleanup automatically
exit 0
