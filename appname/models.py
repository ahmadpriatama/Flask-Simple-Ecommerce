from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Model():
    isRemoved = db.Column(db.Boolean, default=False)

    def update(self):
        db.session.commit()

    def put(self):
        db.session.add(self)
        db.session.commit()

    def trash(self):
        self.isRemoved = True
        db.session.commit()


class User(db.Model, UserMixin, Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=100))
    password = db.Column(db.String(length=100))

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username


tags = db.Table('category_product',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
    db.Column('created_at', db.DateTime()),
    db.Column('update_at', db.DateTime()),
)


class Category(db.Model, Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=100))
    parent_id = db.Column(db.String(length=6))
    created_at = db.Column(db.DateTime())
    update_at = db.Column(db.DateTime())

    def parent(self):
        if self.parent_id:
            return Category.query.get(self.parent_id)
        else:
            return None

    def parent_title(self):
        parent = self.parent()
        if parent:
            return parent.title
        else:
            return ''

    def products(self):
        return Category.query.filter_by();


class Product(db.Model, Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100))
    photo = db.Column(db.String(length=200))
    model = db.Column(db.String(length=100))
    created_at = db.Column(db.DateTime())
    update_at = db.Column(db.DateTime())
    categories = db.relationship('Category', secondary=tags, backref=db.backref('product'))

    def getUrl(self):
        return '/uploads/' + self.photo if self.photo else ''

