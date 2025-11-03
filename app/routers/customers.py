from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal
import random

router = APIRouter(prefix="/customers", tags=["Customers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    new_customer = models.Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/")
def list_customers(db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    if random.random() < 0.1:
        customers_data = [
            {"id": f"El id es: {c.id}", "name": f"El nombre es: {c.name.upper()}", "email": f"El email es: {c.email}"}
            for c in customers
        ]
        print("Customersdata(canary)")
        print(customers_data)
        return {
            "version": "v2",
            "note": "Canary release - Nueva presentación de clientes",
            "customers_quantity": len(customers_data),
            "customers": customers_data
    }
    else:
        print("noncanary customers")
        print(customers)
        return customers

@router.get("/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer
