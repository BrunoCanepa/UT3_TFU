from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal
from ..limiter import limiter

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# RPC
@router.post("/", response_model=schemas.Product)

@limiter.limit("10/minute")

def create_product(request: Request, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=list[schemas.Product])

# --- APLICA EL LÍMITE AQUÍ ---
@limiter.limit("10/minute") # Límite: 100 peticiones por minuto por IP
# --- FIN DEL LÍMITE ---

def list_products(request: Request, db: Session = Depends(get_db)):
    return db.query(models.Product).all()
