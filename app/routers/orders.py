from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import orm, schemas
from ..database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(orm.Customer).filter(orm.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    new_order = orm.Order(
        customer_id=order.customer_id,
        total=order.total,
        date=datetime.utcnow()
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/", response_model=list[schemas.Order])
def list_orders(db: Session = Depends(get_db)):
    return db.query(orm.Order).all()

@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(orm.Order).filter(orm.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order
