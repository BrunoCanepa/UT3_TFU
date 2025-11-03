# Mini E‑Commerce API (FastAPI)

Este proyecto es una API REST simple para un mini e‑commerce hecha con FastAPI. La usamos para practicar conceptos de arquitectura de sistemas distribuidos que vemos en la materia.

La app tiene tres componentes principales (cada uno con sus endpoints):

- **Productos** (`/products`): Gestión de catálogo de productos
- **Clientes** (`/customers`): Gestión de usuarios/clientes  
- **Órdenes** (`/orders`): Gestión de pedidos y transacciones

Cada componente expone su interfaz REST y se conecta a la base de datos usando SQLAlchemy.

## Cómo levantar el proyecto

### Prerequisitos:

Antes de empezar, asegúrate de tener instaladas las siguientes herramientas:

* **Docker Desktop**
* **Minikube** y **kubectl**
* **k6**
* **jq**

### Opciones de Ejecución:

### Kubernetes con Minikube

```bash
minikube start
eval $(minikube -p minikube docker-env)
docker build -t ut3-tfu-api:latest .
kubectl apply -k k8s

# Ver pods y readiness
kubectl get pods -l app=api -w

# URL del Service y pruebas
minikube service api-service --url
curl $(minikube service api-service --url)/health
curl $(minikube service api-service --url)/whoami
```

Nota: para acceder a FastAPI, puedes hacer port-forward del Service:

```bash
kubectl port-forward svc/api-service 8080:80  
# abrir http://localhost:8080/docs#
```

Nota: para acceder al dashboard de RQ en Kubernetes, puedes hacer port-forward del Service:
```bash
kubectl port-forward svc/rq-dashboard-svc 9181:9181
# abrir http://localhost:9181
```

### Health Endpoint Monitoring

Endpoints de salud y diagnóstico:

```bash
export BASE=${BASE:-http://localhost:8080}

# Salud básica
curl -s $BASE/health

# Liveness (si el proceso está vivo)
curl -s $BASE/health/live

# Readiness (verifica conexión a base de datos; devuelve 503 si no está lista)
curl -i $BASE/health/ready

# Identificar qué pod/instancia responde (útil para balanceo)
for i in {1..6}; do curl -s $BASE/whoami; echo; done
```

En Kubernetes, los probes están configurados en el `Deployment` para golpear `/health` como liveness y readiness.

### Rate Limiting (SlowAPI + Redis)

Cada endpoint tiene límite por IP de 10 requests/minuto. Al superar el límite se devuelve HTTP 429.

```bash
export BASE=${BASE:-http://localhost:8080}
for i in $(seq 1 12); do 
  echo -n "$i: "; curl -s -o /dev/null -w "%{http_code}\n" $BASE/products/; 
done

# Ver detalle del 429
curl -i $BASE/products/
```

### Patrón Cache-Aside (Redis)

`GET /products/` intenta leer del cache `products:all` (TTL 60s). Si no existe, consulta la DB y llena el cache. `POST /products/` invalida `products:all`.

Prueba sugerida:

```bash
export BASE=${BASE:-http://localhost:8080}

# Crear un producto y forzar invalidación de cache
curl -s -X POST $BASE/products/ -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":1200.00,"stock":5}' | jq '.'

# 1ª lectura: sin cache (from_cache=false)
curl -s $BASE/products/ | jq '.from_cache,.processing_time_ms'

# 2ª lectura inmediata: con cache (from_cache=true, menor tiempo)
curl -s $BASE/products/ | jq '.from_cache,.processing_time_ms'

# Inspeccionar datos cacheados
curl -s $BASE/cache | jq '.'
```

### Patrón Queue-Based Load Leveling (Redis Queue - RQ)

`POST /orders/` encola un trabajo en Redis (cola `default`); el `worker` lo procesa y crea la orden en la base. Monitorea con RQ Dashboard.

```bash
export BASE=${BASE:-http://localhost:8080}

# kubectl port-forward svc/rq-dashboard-svc 9181:9181
# abrir http://localhost:9181

# 1) Crear cliente
CID=$(curl -s -X POST $BASE/customers/ -H "Content-Type: application/json" \
  -d '{"name":"Ana","email":"ana@example.com"}' | jq -r '.id')

# 2) Encolar orden (respuesta incluye job_id)
curl -s -X POST $BASE/orders/ -H "Content-Type: application/json" \
  -d "{\"customer_id\":$CID,\"total\":199.99}" | jq '.'

# 3) Verificar procesamiento a los pocos segundos
sleep 3
curl -s $BASE/orders/ | jq '.'
```
