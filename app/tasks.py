import time
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
from datetime import datetime

def create_order_task(customer_id: int, total: float) -> int:
    """Crea una orden en la base de datos (ejecutado por el worker)"""
    db: Session = SessionLocal()
    try:
        new_order = models.Order(
            customer_id=customer_id,
            total=total,
            date=datetime.utcnow()
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order.id
    finally:
        db.close()

def process_order(order_id: int) -> None:
    # Simula trabajo pesado y desacoplado (pago, email, notificación, etc.)
    time.sleep(2)
    db: Session = SessionLocal()
    try:
        _ = db.query(models.Order).filter(models.Order.id == order_id).first()
    finally:
        db.close()