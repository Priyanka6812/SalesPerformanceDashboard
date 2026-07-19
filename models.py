from database import db
from flask_login import UserMixin
from datetime import datetime


# ==========================
# User Table
# ==========================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==========================
# Sales Table
# ==========================
class Sales(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.String(50))

    product = db.Column(db.String(100))

    category = db.Column(db.String(100))

    customer = db.Column(db.String(100))

    region = db.Column(db.String(100))

    quantity = db.Column(db.Integer)

    sales = db.Column(db.Float)

    profit = db.Column(db.Float)

    order_date = db.Column(db.String(50))