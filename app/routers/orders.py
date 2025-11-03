from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .. import models, schemas
# from ..database import SessionLocal
from ..database import get_db
from datetime import datetime
from ..limiter import limiter

router = APIRouter(prefix="/orders", tags=["Orders"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/", response_model=schemas.Order)
@limiter.limit("10/minute")
def create_order(request: Request, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    new_order = models.Order(
        customer_id=order.customer_id,
        total=order.total,
        date=datetime.utcnow()
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/", response_model=list[schemas.Order])
@limiter.limit("10/minute")
def list_orders(request: Request, db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.get("/{order_id}", response_model=schemas.Order)
@limiter.limit("10/minute")
def get_order(request: Request, order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order
