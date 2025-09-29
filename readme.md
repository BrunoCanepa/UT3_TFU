README.md — Mini E-Commerce API (FastAPI Demo)
# Descripción

Esta es una API REST de Mini E-Commerce desarrollada con Python + FastAPI, que demuestra los distintos conceptos de arquitectura de sistemas distribuidos y escalables.

La aplicación incluye tres módulos principales:

- Productos
- Clientes
- Órdenes de compra

Cada módulo es un componente independiente que expone su propia interfaz a través de endpoints REST.

# Conceptos demostrados

## Componentes e interfaces	

La API está dividida en componentes (products, customers, orders), cada uno con sus propios endpoints (interfaces REST). Se comunican a través de la capa de base de datos.

## Escalabilidad horizontal / vertical

- Horizontal: la app puede ejecutarse en múltiples contenedores y balancearse (por ejemplo, usando Nginx o Kubernetes).

- Vertical: se pueden asignar más recursos al contenedor Docker (CPU, RAM) sin cambiar el código.

## Contenedores	

Se usa un Dockerfile para empaquetar la aplicación, permitiendo portabilidad, despliegue rápido y aislamiento del entorno.

## ACID o BASE	

La base de datos SQLite cumple las propiedades ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad). Cada operación de escritura se realiza dentro de una transacción controlada por SQLAlchemy.

### Servicios sin estado (Stateless)	

La API no almacena sesiones de usuario ni variables en memoria. Toda la información persistente se guarda en la base de datos. Cualquier instancia puede atender cualquier request sin depender de un estado previo.


# Ejecución con Docker

1. Construir imagen

docker build -t fastapi-ecommerce .

2. Ejecutar contenedor
docker run -d -p 8000:8000 fastapi-ecommerce

3. Verificar:
http://localhost:8000/docs

# Ejemplos con curl

1️. Crear un producto

curl -X POST http://localhost:8000/products/ \
-H "Content-Type: application/json" \
-d '{"name":"Laptop","price":1500,"stock":10}'


2️. Crear un cliente

curl -X POST http://localhost:8000/customers/ \
-H "Content-Type: application/json" \
-d '{"name":"Bruno","email":"bruno@test.com"}'


3️. Crear una orden

curl -X POST http://localhost:8000/orders/ \
-H "Content-Type: application/json" \
-d '{"customer_id":1,"total":1500}'


4️. Listar órdenes

curl http://localhost:8000/orders/
