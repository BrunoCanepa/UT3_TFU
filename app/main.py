from fastapi import FastAPI
import os
from . import models
from .database import engine
from .routers import products, customers, orders

# Evitar que múltiples instancias ejecuten DDL simultáneamente (solo cuando RUN_DB_INIT=true)
if os.getenv("RUN_DB_INIT", "false").lower() == "true":
    models.Base.metadata.create_all(bind=engine)

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
