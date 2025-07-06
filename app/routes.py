from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, database
from typing import Optional
from fastapi import Query
from datetime import datetime
from starlette import status
from .auth_doc import get_current_user

from . import models

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the current user
user_dependency = Annotated[dict, Depends(get_current_user)]

# Exampl endpoint to check if the API is running
@router.get("/", status_code=status.HTTP_200_OK)
async def root(user: user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "Welcome to the Inventory Management API"}

@router.get("/items/filter", response_model=list[schemas.Item])
def filter_items(
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(None),
    supplier_id: Optional[int] = Query(None),
    branch_location: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    query = db.query(models.Item)

    if category_id:
        query = query.filter(models.Item.category_id == category_id)
    if supplier_id:
        query = query.filter(models.Item.supplier_id == supplier_id)
    if branch_location:
        query = query.filter(models.Item.branch_location == branch_location)
    if start_date and end_date:
        query = query.filter(models.Item.date_added.between(start_date, end_date))
    elif start_date:
        query = query.filter(models.Item.date_added >= start_date)
    elif end_date:
        query = query.filter(models.Item.date_added <= end_date)

    return query.all()

@router.get("/items/", response_model=list[schemas.Item])
def read_items(user:user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.get_items(db)

@router.post("/items/", response_model=schemas.Item)
def create_item(user:user_dependency, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    return crud.create_item(db, item)

@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(user:user_dependency, item_id: int, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(user:user_dependency, item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    db_item = crud.update_item(db, item_id, item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.delete("/items/{item_id}")
def delete_item(user:user_dependency, item_id: int, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    item = crud.delete_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

# Categories
@router.post("/categories/", response_model=schemas.Category)
def add_category(user:user_dependency, category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    return crud.create_category(db, category)

@router.get("/categories/", response_model=list[schemas.Category])
def list_categories(user:user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.get_categories(db)

@router.get("/categories/{category_id}", response_model=schemas.Category)
def get_category(user:user_dependency, category_id: int, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_category = crud.get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# Suppliers
@router.post("/suppliers/", response_model=schemas.Supplier)
def add_supplier(user:user_dependency, supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    return crud.create_supplier(db, supplier)

@router.get("/suppliers/", response_model=list[schemas.Supplier])
def list_suppliers(user:user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.get_suppliers(db)

@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def get_supplier(user:user_dependency, supplier_id: int, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_supplier = crud.get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

@router.get("/low-stock", response_model=list[schemas.Item])
def get_low_stock_items(user:user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    return db.query(models.Item).filter(
        models.Item.quantity < models.Item.min_stock_level
    ).all()

@router.get("/items-Search", response_model=list[schemas.Item])
def search_items(user:user_dependency, query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    search_term = f"%{query}%"
    results = db.query(models.Item).filter(
        (models.Item.name.ilike(search_term)) | (models.Item.description.ilike(search_term))
    ).all()
    return results
