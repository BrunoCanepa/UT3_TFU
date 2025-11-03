from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal
import json 
import time
from ..cache import cache_get, cache_set, cache_del

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# RPC
@router.post("/")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    start_time = time.time()
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    cache_del("products:all")
    processing_time_ms = (time.time() - start_time) * 1000
    return {
        "data": schemas.Product.from_orm(db_product),
        "processing_time_ms": round(processing_time_ms, 2)
    }

@router.get("/")
def list_products(db: Session = Depends(get_db)):
    start_time = time.time()
    cache_key = "products:all"  
    cached = cache_get(cache_key)  
    if cached:
        products = [schemas.Product(**p) for p in json.loads(cached)]
        processing_time_ms = (time.time() - start_time) * 1000
        return {
            "data": products,
            "processing_time_ms": round(processing_time_ms, 2),
            "from_cache": True
        }
    items = db.query(models.Product).all()  
    cache_set(cache_key, [schemas.Product.from_orm(p).dict() for p in items], ttl_seconds=60)
    processing_time_ms = (time.time() - start_time) * 1000
    return {
        "data": [schemas.Product.from_orm(p) for p in items],
        "processing_time_ms": round(processing_time_ms, 2),
        "from_cache": False
    }