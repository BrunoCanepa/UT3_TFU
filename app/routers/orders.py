from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal
from ..queue import get_queue
from ..tasks import create_order_task

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):

    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    q = get_queue()
    job = q.enqueue(create_order_task, order.customer_id, order.total)
    
    return {
        "message": "Orden encolada exitosamente",
        "job_id": job.id,
        "customer_id": order.customer_id,
        "total": order.total
    }

@router.get("/", response_model=list[schemas.Order])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order
