from appname.models import Product, Category
from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_table import Table, Col
from flask_wtf import Form
from wtforms import validators
from wtforms.fields import TextField, FileField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from appname import db
import werkzeug

products = Blueprint('products', __name__, template_folder='templates/products')


class ProductForm(Form):
    name = TextField('Name', validators=[validators.Required()])
    model = TextField('Model')
    categories = QuerySelectMultipleField('Categories', query_factory=lambda: Category.query.filter_by(isRemoved=0),
                                     get_pk=lambda x: x.id, get_label=lambda x: x.title)
    photo = FileField('Photo')


@products.route("/products/index")
def index():

    class ActionCol(Col):
        def __init__(self):
            super(ActionCol, self).__init__("action")

        def td_contents(self, item, attr_list):
            return '<a href="{update}">Update</a> | ' \
                   '<form method="post" action="{trash}" style="display:inline-block">' \
                        '<input class="btn btn-danger btn-xs" type="submit" value="delete"/>' \
                   '</form>'.format(
                    update=url_for('products.update', id=item.id),
                    trash=url_for('products.trash', id=item.id)
            )

    class TagCol(Col):
        def __init__(self):
            super(TagCol, self).__init__("Categories")

        def td_contents(self, item, attr_list):
            ret = ''
            for i in item.categories:
                ret += '<span class="label label-primary">' \
                    '<i class="fa fa-btn fa-tags"></i>' \
                    '{label}</span> '.format(label=i.title)
            return ret


    class ItemTable(Table):
        name = Col('Name')
        model = Col('Model')
        tag = TagCol()
        action = ActionCol()

    products = Product.query.filter_by(isRemoved=0).all()
    table = ItemTable(products, classes=['table'])
    return render_template('products/index.html', table=table)


@products.route("/products/create", methods=["GET", "POST"])
def create():
    form = ProductForm()
    model = Product()
    if form.validate_on_submit():
        form.populate_obj(model)
        if form.photo.data:
            filename = werkzeug.secure_filename(form.photo.data.filename)
            form.photo.data.save('uploads/' + filename)
            model.photo = filename
        else:
            model.photo = None
        model.put()
        flash('Success', 'success')
        return redirect('products/index')
    return render_template('products/create.html', form=form)


@products.route("/products/update/<id>", methods=['GET', 'POST'])
def update(id):
    form = ProductForm()
    model = Product.query.get(id)
    form.name.data = model.name
    form.model.data = model.model
    form.categories.data = model.categories
    # for i in model.categories:
    #     print i
    if form.validate_on_submit():
        model.name = request.form['name']
        model.model = request.form['model']
        if form.photo.data:
            filename = werkzeug.secure_filename(form.photo.data.filename)
            form.photo.data.save('uploads/' + filename)
            model.photo = filename
        model.put()
        if request.form['categories']:
            for val in reversed(model.categories):
                model.categories.remove(val)
            for i in request.form.getlist('categories'):
                model.categories.append(Category.query.get(i))
            db.session.commit()
        flash('Success', 'success')
        return redirect('products/index')
    return render_template('products/update.html', form=form, model=model)


@products.route("/products/trash/<id>", methods=['POST'])
def trash(id):
    model = Product.query.get(id)
    model.trash()
    flash('Success', 'success')
    return redirect('products/index')

