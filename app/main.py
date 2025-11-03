from fastapi import FastAPI, Request
import os
from . import orm
from .database import engine
from .routers import products, customers, orders

# Evitar que múltiples instancias ejecuten DDL simultáneamente (solo cuando RUN_DB_INIT=true)
if os.getenv("RUN_DB_INIT", "false").lower() == "true":
    orm.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini E-Commerce API")

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "Mini E-Commerce API Running "}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/whoami")
def whoami():
    instance = os.getenv("INSTANCE_NAME", os.getenv("HOSTNAME", "unknown"))
    return {"instance": instance}

#test endpoint para los datos del user a travez del gateway.
@app.get("/private")
async def private(request: Request):
    user_sub = request.headers.get("X-User-Sub")
    user_email = request.headers.get("X-User-Email")
    user_name = request.headers.get("X-User-Name")

    if not user_sub:
        raise HTTPException(status_code=401, detail="No autorizado: falta header user")

    print(f"Backend: petición recibida. user: {user_email}")
    return {
        "msg": "Acceso OK desde backend",
        "user": {"sub": user_sub, "email": user_email, "name": user_name}
    }