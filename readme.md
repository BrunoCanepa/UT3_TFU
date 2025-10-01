# Mini E‑Commerce API (FastAPI)

Este proyecto es una API REST simple para un mini e‑commerce hecha con FastAPI. La usamos para practicar conceptos de arquitectura de sistemas distribuidos que vemos en la materia.

La app tiene tres componentes principales (cada uno con sus endpoints):

- **Productos** (`/products`): Gestión de catálogo de productos
- **Clientes** (`/customers`): Gestión de usuarios/clientes  
- **Órdenes** (`/orders`): Gestión de pedidos y transacciones

Cada componente expone su interfaz REST y se conecta a la base de datos usando SQLAlchemy.

## Conceptos aplicados (UT3)

- **Componentes e interfaces**: Los routers están separados por dominio en `app/routers/products.py`, `app/routers/customers.py` y `app/routers/orders.py`. Se montan en `app/main.py` con `include_router`, cada uno con su prefijo (`/products`, `/customers`, `/orders`). Cada componente expone su propia interfaz REST independiente.

- **Escalabilidad horizontal**: 
  - En Kubernetes: configuramos `replicas: 2` en `k8s/deployment.yaml` y HPA en `k8s/hpa.yaml` que escala automáticamente de 2 a 10 pods según CPU (50%) y memoria (70%). 
  - El Service NodePort (`k8s/service.yaml`) distribuye tráfico entre pods.
  - En Docker Compose: Nginx (`nginx.conf`) actúa como load balancer hacia el servicio `api`.

- **Contenedores**: Usamos Docker (`Dockerfile`) para empaquetar la aplicación. Docker Compose orquesta múltiples servicios: `api`, `db` (Postgres) y `nginx`.

- **Servicios sin estado (stateless)**: 
  - No guardamos sesiones en memoria; todo estado va a la base de datos.
  - El endpoint `/whoami` devuelve `INSTANCE_NAME` para identificar qué instancia responde.
  - Solo una instancia inicializa la DB (`RUN_DB_INIT=true`) para evitar condiciones de carrera.

- **Consistencia ACID**: Usamos SQLAlchemy con transacciones por operación. Restricción de unicidad en `email` de `Customer` que devuelve HTTP 400 si se viola.

## Cómo levantar el proyecto

### Opción A: Docker (una sola instancia)

```bash
docker build -t ut3-tfu-api:latest .
docker run -d -p 8000:8000 ut3-tfu-api:latest
```

Abrir: `http://localhost:8000/docs`

### Opción B: Docker Compose (API + Postgres + Nginx)

```bash
docker compose up --build
```

Servicios:
- API: `api`
- Proxy: Nginx en `http://localhost:8080`
- Base de datos: Postgres

Chequeos rápidos:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/whoami
```

### Opción C: Kubernetes con Minikube

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

# Balanceo entre 2 réplicas iniciales 
for i in {1..10}; do curl -s $(minikube service api-service --url)/whoami; echo; done
```

### Opción D: Demo de Autoescalado (HPA)

Para demostrar el autoescalado horizontal con Kubernetes:

```bash
# Prerequisitos: tener Minikube corriendo y k6 instalado
minikube start
kubectl apply -k k8s

# Ejecutar demo de HPA (2 minutos)
./demo-hpa.sh
```

El script `demo-hpa.sh`:
- Configura port-forwarding automático
- Ejecuta pruebas de carga con K6
- Muestra el autoescalado en tiempo real
- Dashboard K6: `http://localhost:5665`

**Timeline del demo (2 minutos)**:
- 0-10s: 60 usuarios → HPA se activa
- 10s-1m10s: 100 usuarios → Escala a 4-6 pods  
- 1m10s-1m40s: 120 usuarios → Escala a 6-8 pods
- 1m40s-2m: Reducción → Vuelve a 2 pods

## Endpoints y pruebas (curl)

Base URL según el entorno:
- **Local o Docker**: `http://localhost:8000`
- **Docker Compose** (vía Nginx): `http://localhost:8080`
- **Kubernetes**: usar la URL que devuelve `minikube service api-service --url`

**Tip**: Define la variable `BASE` para facilitar las pruebas:
```bash
# Para Docker Compose
export BASE=http://localhost:8080

# Para local/Docker
export BASE=http://localhost:8000

# Para Kubernetes
export BASE=$(minikube service api-service --url)
```

### Salud y diagnóstico

```bash
# Verificar que la API está funcionando
curl -s $BASE/health

# Ver qué instancia/pod está respondiendo (útil para balanceo)
curl -s $BASE/whoami

# Endpoint raíz
curl -s $BASE/
```

### Productos (`/products`)

```bash
# Crear producto
curl -s -X POST $BASE/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Mouse Inalámbrico","price":29.99,"stock":50}'

# Listar todos los productos
curl -s $BASE/products/ | jq '.'
```

### Clientes (`/customers`)

```bash
# Crear clientes de ejemplo
curl -s -X POST $BASE/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana García","email":"ana@example.com"}'

# Listar todos los clientes
curl -s $BASE/customers/ | jq '.'

# Obtener cliente específico por ID
curl -s $BASE/customers/1 | jq '.'

# Probar validación de email único (debe devolver HTTP 400)
curl -i -X POST $BASE/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana Duplicada","email":"ana@example.com"}'

# Probar cliente inexistente (debe devolver HTTP 404)
curl -i $BASE/customers/999
```

### Órdenes (`/orders`)

```bash
# Crear orden (usar un customer_id válido)
curl -s -X POST $BASE/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"total":1590.98}'

# Listar todas las órdenes
curl -s $BASE/orders/ | jq '.'

# Obtener orden específica por ID
curl -s $BASE/orders/1 | jq '.'

# Probar orden con cliente inexistente (debe devolver HTTP 404)
curl -i -X POST $BASE/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":999,"total":100.00}'

# Probar orden inexistente (debe devolver HTTP 404)
curl -i $BASE/orders/999
# Respuesta: HTTP/1.1 404 Not Found {"detail":"Orden no encontrada"}
```

### Flujo completo de prueba

```bash
# Script completo para probar toda la funcionalidad
export BASE=http://localhost:8080  # Ajustar según entorno

echo "=== Verificando salud de la API ==="
curl -s $BASE/health

echo -e "\n=== Creando productos ==="
LAPTOP=$(curl -s -X POST $BASE/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":1200.00,"stock":5}' | jq -r '.id')
echo "Laptop creada con ID: $LAPTOP"

echo -e "\n=== Creando cliente ==="
CUSTOMER=$(curl -s -X POST $BASE/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Juan Pérez","email":"juan@test.com"}' | jq -r '.id')
echo "Cliente creado con ID: $CUSTOMER"

echo -e "\n=== Creando orden ==="
ORDER=$(curl -s -X POST $BASE/orders/ \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\":$CUSTOMER,\"total\":1200.00}" | jq -r '.id')
echo "Orden creada con ID: $ORDER"

echo -e "\n=== Verificando datos creados ==="
echo "Productos:"
curl -s $BASE/products/ | jq '.'
echo -e "\nClientes:"
curl -s $BASE/customers/ | jq '.'
echo -e "\nÓrdenes:"
curl -s $BASE/orders/ | jq '.'
```
