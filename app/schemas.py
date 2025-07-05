from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Category
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    model_config = {"from_attributes": True}

# Supplier
class SupplierBase(BaseModel):
    name: str
    contact: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
    model_config = {"from_attributes": True}

# Item
class ItemBase(BaseModel):
    name: str
    quantity: int
    description: Optional[str] = None
    min_stock_level: int = 0
    cost_price: float
    selling_price: float
    location: str
    category_id: Optional[int]
    supplier_id: Optional[int]

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    date_added: datetime

    model_config = {"from_attributes": True}