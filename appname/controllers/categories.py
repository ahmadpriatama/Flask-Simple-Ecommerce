from appname.models import Category
from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask.ext.wtf import Form
from flask_table import Table, Col
from wtforms import validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import StringField

categories = Blueprint('categories', __name__, template_folder='templates/categories')


class CategoryForm(Form):
        title = StringField('Title', validators=[validators.DataRequired()])
        parent_id = QuerySelectField('Parent', query_factory=lambda: Category.query.filter_by(isRemoved=0),
                                     get_pk=lambda x: x.id, get_label=lambda x: x.title, allow_blank=True)


@categories.route("/categories/index")
def index():

    class ActionCol(Col):
        def __init__(self):
            super(ActionCol, self).__init__("action")

        def td_contents(self, item, attr_list):
            return '<a href="{update}">Update</a> | ' \
                   '<form method="post" action="{trash}" style="display:inline-block">' \
                        '<input class="btn btn-danger btn-xs" type="submit" value="delete"/>' \
                   '</form>'.format(
                    update=url_for('categories.update', id=item.id),
                    trash=url_for('categories.trash', id=item.id)
            )

    class ParentCol(Col):
        def td_contents(self, item, attr_list):
            return item.parent_title()

    class ItemTable(Table):
        title = Col('Title')
        parent_id = ParentCol('Parent')
        button = ActionCol()

    categories = Category.query.filter_by(isRemoved=0).all()
    table = ItemTable(categories, classes=['table'])
    return render_template('categories/index.html', table=table)


@categories.route("/categories/create", methods=["GET", "POST"])
def create():
    form = CategoryForm(request.form)
    model = Category()
    if form.validate_on_submit():
        form.populate_obj(model)
        model.parent_id = form.parent_id.data.id if form.parent_id.data else None
        model.put()
        flash('Success', 'success')
        return redirect('categories/index')
    return render_template('categories/create.html', form=form)


@categories.route("/categories/update/<id>", methods=['GET', 'POST'])
def update(id):
    model = Category.query.get(id)
    form = CategoryForm()
    form.title.data = model.title if model.title else None
    form.parent_id.data = model.parent() if model.parent() else None
    if form.validate_on_submit():
        model.title = request.form['title']
        model.parent_id = request.form['parent_id'] if request.form['parent_id'] else None
        model.put()
        flash('Success', 'success')
        return redirect('categories/index')
    return render_template('categories/create.html', form=form)


@categories.route("/categories/trash/<id>", methods=['POST'])
def trash(id):
    model = Category.query.get(id)
    model.trash()
    flash('Success', 'success')
    return redirect('categories/index')

