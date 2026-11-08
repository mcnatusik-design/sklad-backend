from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="category")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    supplies = relationship("Supply", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float, nullable=False)
    current_stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=5)

    category = relationship("Category", back_populates="products")
    supply_items = relationship("SupplyItem", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")

class Supply(Base):
    __tablename__ = "supplies"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    date = Column(DateTime, default=datetime.datetime.utcnow)

    supplier = relationship("Supplier", back_populates="supplies")
    items = relationship("SupplyItem", back_populates="supply")

class SupplyItem(Base):
    __tablename__ = "supply_items"
    id = Column(Integer, primary_key=True, index=True)
    supply_id = Column(Integer, ForeignKey("supplies.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    purchase_price = Column(Float)

    supply = relationship("Supply", back_populates="items")
    product = relationship("Product", back_populates="supply_items")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(Float, default=0.0)

    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    selling_price = Column(Float)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="worker") # По умолчанию - кладовщик