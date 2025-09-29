from fastapi import FastAPI
from . import models
from .database import engine
from .routers import products, customers, orders

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini E-Commerce API")

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "Mini E-Commerce API Running 🚀"}
