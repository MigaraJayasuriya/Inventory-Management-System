from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, UTC

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    items = relationship("Item", back_populates="category")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    contact = Column(String, nullable=True)

    items = relationship("Item", back_populates="supplier")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer, default=0)
    description = Column(String, nullable=True)

    min_stock_level = Column(Integer, default=0)
    
    cost_price = Column(Float)
    selling_price = Column(Float)
    branch_location = Column(String)
    date_added = Column(DateTime, default=datetime.now(UTC))

    category_id = Column(Integer, ForeignKey("categories.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    category = relationship("Category", back_populates="items")
    supplier = relationship("Supplier", back_populates="items")