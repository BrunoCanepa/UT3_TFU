import time
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

def process_order(order_id: int) -> None:
    # Simula trabajo pesado y desacoplado (pago, email, notificación, etc.)
    time.sleep(2)
    db: Session = SessionLocal()
    try:
        _ = db.query(models.Order).filter(models.Order.id == order_id).first()
    finally:
        db.close()