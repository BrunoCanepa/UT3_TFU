from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal
import json 
from ..cache import cache_get, cache_set, cache_del

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# RPC
@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    cache_del("products:all")
    return db_product

@router.get("/", response_model=list[schemas.Product])
def list_products(db: Session = Depends(get_db)):
    cache_key = "products:all"  
    cached = cache_get(cache_key)  
    if cached:  
        return [schemas.Product(**p) for p in json.loads(cached)]  
    items = db.query(models.Product).all()  
    cache_set(cache_key, [schemas.Product.from_orm(p).dict() for p in items], ttl_seconds=60)  
    return items