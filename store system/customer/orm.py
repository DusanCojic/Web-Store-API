from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class OrderStatus(Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"


class Category(db.Model):
    __tablename__ = 'Category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False, unique=True)

    products = db.relationship('Product', secondary='ProductCategory', back_populates='categories')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Product(db.Model):
    __tablename__ = 'Product'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    categories = db.relationship('Category', secondary='ProductCategory', back_populates='products')
    orders = db.relationship('OrderProduct', back_populates='product', cascade="all, delete-orphan", lazy='select')

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class ProductCategory(db.Model):
    __tablename__ = 'ProductCategory'

    product_id = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='CASCADE'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id', ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return f"<ProductCategory(product_id={self.product_id}, category_id={self.category_id})>"


class Order(db.Model):
    __tablename__ = 'Order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.CREATED)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    address = db.Column(db.String(256), nullable=False)

    products = db.relationship('OrderProduct', back_populates='order', cascade="all, delete-orphan", lazy='select')

    def __repr__(self):
        return f"<Order(id={self.id}, email='{self.email}', status='{self.status.name}')>"


class OrderProduct(db.Model):
    __tablename__ = 'OrderProduct'

    order_id = db.Column(db.Integer, db.ForeignKey('Order.id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='CASCADE'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', back_populates='products')
    product = db.relationship('Product', back_populates='orders')

    def __repr__(self):
        return f"<OrderProduct(order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"
