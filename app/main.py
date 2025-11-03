from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .database import get_db
import os
from . import models
from .database import engine
from .routers import products, customers, orders
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .limiter import limiter
from .routers import products, customers, orders
from .cache import get_redis

# Evitar que múltiples instancias ejecuten DDL simultáneamente (solo cuando RUN_DB_INIT=true)
if os.getenv("RUN_DB_INIT", "false").lower() == "true":
    models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini E-Commerce API")


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

@app.get("/health/live", tags=["Health Check"])
def liveness_check():
    return {"status": "alive"}

@app.get("/health/ready", tags=["Health Check"])
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail={"status": "not_ready", "database": "disconnected", "error": str(e)}
        )
@app.get("/cache")
def get_cache():
    """Show all cached data"""
    redis = get_redis()
    keys = redis.keys("*")
    cache_data = {}
    for key in keys:
        cache_data[key] = redis.get(key)
    return {"cached_items": len(cache_data), "data": cache_data}
