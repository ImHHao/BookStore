import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum as RoleEnum
from app import db, app

import hashlib
import json
import pytz
from datetime import datetime

# Sử dụng pytz để lấy múi giờ của Việt Nam
vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
created_date = datetime.now(vietnam_tz)


# quyền của nhân viên
class RolePermission(RoleEnum):
    MANAGER = 1
    SELLER = 2


# vai trò người dùng
class UserRole(RoleEnum):
    ADMIN = 1
    STAFF = 2
    CUSTOMER = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    avatar = Column(String(250), default='https://png.pngtree.com/png-clipart/20210608/ourlarge/pngtree-dark-gray-simple-avatar-png-image_3418404.jpg')

    customer = relationship('Customer', backref='user', cascade="all, delete-orphan", uselist=False)
    staff = relationship('Staff', backref='user', cascade="all, delete-orphan", uselist=False)

    def set_password(self, password):
        """Băm mật khẩu bằng MD5 và lưu."""
        self.password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

    def check_password(self, password):
        """Kiểm tra mật khẩu so với giá trị đã băm."""
        return self.password == hashlib.md5(password.strip().encode('utf-8')).hexdigest()


    def is_customer(self):
        return self.role == 'customer'
    
class Customer(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    phone = Column(String(50), nullable=False)
    address = Column(String(100), nullable=False)

    orders = relationship('Order', backref='customer', lazy=True)
    comments = relationship('Comment', backref='customer', lazy=True)
    

class Staff(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    phone = Column(String(50))
    role_permission = Column(Enum(RolePermission), nullable=False)

    orders = relationship('Order', backref='staff', lazy=True)
    forms = relationship('Form', backref='staff', lazy=True)


    @hybrid_property
    def username(self):
        return self.user.username


class Author(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    books = relationship('Book', backref='author', lazy=True)

    def __str__(self):
        return self.name


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    books = relationship('Book', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Book(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False, unique=True)
    inventoryQuantity = Column(Integer, nullable=False)
    image = Column(String(300), nullable=True,
                    default="https://cdn-icons-png.flaticon.com/512/2716/2716054.png")
    price = Column(Integer, nullable=False)

    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    order_details = relationship("OrderDetails", backref="book", cascade="all, delete-orphan", lazy=True)
    form_details = relationship("FormDetails", backref="book", cascade="all, delete-orphan", lazy=True)
    comments = relationship("Comment", backref="book", lazy=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Order(db.Model):
    id = Column(String(50), primary_key=True)
    createdDate = Column(DateTime, default=created_date, nullable=False)
    expireDate = Column(DateTime, nullable=True)
    isPay = Column(Boolean, default=False)
    isCancel = Column(Boolean, default=False)

    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)

    order_details = relationship("OrderDetails", backref="order", cascade="all, delete-orphan", lazy=True)


class Form(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    createdDate = Column(DateTime, default=created_date, nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    form_details = relationship("FormDetails", backref="form", lazy=True)


class OrderDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)
    order_id = Column(String(50), ForeignKey(Order.id), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    unit_price = Column(Integer, nullable=False, default=0)


class FormDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)
    form_id = Column(Integer, ForeignKey(Form.id), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)


class Comment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)
    createdDate = Column(DateTime, default=created_date, nullable=False)
    class Meta:
        ordering = ['-id']


class ImportRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    min_quantity = db.Column(db.Integer, nullable=False, default=150)
    max_quantity = db.Column(db.Integer, nullable=False, default=300)
    expire_time = db.Column(db.Integer, nullable=False, default=2)


if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()

        password = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
        admin = User(name="Admin", username="admin", password=password,
                    email="admin@gmail.com", user_role=UserRole.ADMIN)
        db.session.add(admin)
        db.session.commit()
        manager = User(name='Manager', username='manager', password=password,
                    email="manager@gmail.com", user_role=UserRole.STAFF)
        m = Staff(phone='123456789', role_permission=RolePermission.MANAGER, user=manager)

        seller = User(name='Seller', username='seller', password=password,
                    email="seller@gmail.com", user_role=UserRole.STAFF)
        s = Staff(phone='123456789', role_permission=RolePermission.SELLER, user=seller)
        db.session.add_all([m, s])
        db.session.commit()

        customer = User(name="Lê Thị Ngọc Hân", username="lele",
                        password=password,
                        email="2254050012han@ou.edu.vn", user_role=UserRole.CUSTOMER,
                        avatar="https://cdn-i.doisongphapluat.com.vn/602/2020/4/24/Thong-tin-thu-vi-ve-nhung-nhan-vat-phu-trong-phim-hoat-hinh-sieu-kinh-dien-tom-va-jerry-8.jpg")
        c = Customer(phone="0123456789", address="Phú Nhuận", user=customer)
        customer2 = User(name="Hoàn Hảo", username="haohao",
                        password=password,
                        email="2254052025hao@ou.edu.vn", user_role=UserRole.CUSTOMER,
                        avatar="https://haycafe.vn/wp-content/uploads/2022/01/Hinh-nen-tho-dang-yeu-trong-phim-hoat-hinh.jpg")
        c2 = Customer(phone="0987654321", address="Gò Vấp", user=customer2)
        db.session.add_all([c, c2])
        db.session.commit()

        with open('data/authors.json', encoding='utf-8') as f:
            authors = json.load(f)
            for p in authors:
                author = Author(**p)
                db.session.add(author)

        with open('data/categories.json', encoding='utf-8') as f:
            categories = json.load(f)
            for p in categories:
                cate = Category(**p)
                db.session.add(cate)

        with open('data/books.json', encoding='utf-8') as f:
            books = json.load(f)
            for p in books:
                book = Book(**p)
                db.session.add(book)

        db.session.commit()

        r = ImportRule()
        db.session.add(r)
        db.session.commit()

        