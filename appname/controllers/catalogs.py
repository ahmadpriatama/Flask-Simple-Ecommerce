
from appname.models import Category, Product
from flask import Blueprint, render_template, redirect, flash, url_for, request

catalogs = Blueprint('catalogs', __name__, template_folder='templates/catalogs')

@catalogs.route('/catalogs')
def index():
    category = Category.query.get(request.args.get('cat')) if request.args.get('cat') else None
    categories = Category.query.filter_by(isRemoved=False).all()
    if category:
        products = Product.query.filter(Product.categories.any(id=category.id)).filter_by(isRemoved=False).all()
    else:
        products = Product.query.all()
    return render_template('catalogs/index.html', categories=categories, category=category, products=products)