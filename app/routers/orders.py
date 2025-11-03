from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from datetime import datetime
from ..limiter import limiter
from ..queue import get_queue
from ..tasks import create_order_task

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=schemas.Order)
@limiter.limit("10/minute")
def create_order(request: Request, order: schemas.OrderCreate, db: Session = Depends(get_db)):
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
