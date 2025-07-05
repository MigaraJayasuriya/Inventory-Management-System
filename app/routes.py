from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, database
from typing import Optional
from fastapi import Query
from datetime import datetime

from . import models

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/items/", response_model=list[schemas.Item])
def read_items(db: Session = Depends(get_db)):
    return crud.get_items(db)

@router.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)

@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db, item_id, item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.delete_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

# Categories
@router.post("/categories/", response_model=schemas.Category)
def add_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)

@router.get("/categories/", response_model=list[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

# Suppliers
@router.post("/suppliers/", response_model=schemas.Supplier)
def add_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    return crud.create_supplier(db, supplier)

@router.get("/suppliers/", response_model=list[schemas.Supplier])
def list_suppliers(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)

@router.get("/items/filter", response_model=list[schemas.Item])
def filter_items(
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(None),
    supplier_id: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    query = db.query(models.Item)

    if category_id:
        query = query.filter(models.Item.category_id == category_id)
    if supplier_id:
        query = query.filter(models.Item.supplier_id == supplier_id)
    if location:
        query = query.filter(models.Item.location == location)
    if start_date and end_date:
        query = query.filter(models.Item.date_added.between(start_date, end_date))
    elif start_date:
        query = query.filter(models.Item.date_added >= start_date)
    elif end_date:
        query = query.filter(models.Item.date_added <= end_date)

    return query.all()

@router.get("/items/low-stock", response_model=list[schemas.Item])
def get_low_stock_items(db: Session = Depends(get_db)):
    return db.query(models.Item).filter(
        models.Item.quantity < models.Item.min_stock_level
    ).all()

@router.get("/items/search", response_model=list[schemas.Item])
def search_items(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    search_term = f"%{query}%"
    results = db.query(models.Item).filter(
        (models.Item.name.ilike(search_term)) | (models.Item.description.ilike(search_term))
    ).all()
    return results
