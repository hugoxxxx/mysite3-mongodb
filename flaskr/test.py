from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session,
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from pymongo import MongoClient, DESCENDING
from datetime import datetime
from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, SelectField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired, Length, Email

bp = Blueprint('test', __name__, url_prefix='/test')
db = MongoClient().test_database


# 自定义WTForm复选框组
class MultiCheckboxFIeld(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class MultiCheckbox(FlaskForm):
    label = MultiCheckboxFIeld(u'lable')
    submit = SubmitField(u'提交')


@bp.route('/lable', methods=('GET', 'POST'))
def lable():
    mycol = list(db.table.find(projection={'_id': False}))
    lable = mycol[0].keys()
    form = MultiCheckbox(obj=lable)
    form.label.choices = [(choiceValue, choiceValue) for choiceValue in lable]
    if request.method == 'POST':
        if form.validate_on_submit():
            lable_choice = request.form.getlist('label')
            session.clear()
            session['lable_choice'] = lable_choice
            return redirect(url_for('test.lablec'))

    return render_template('test/lable.html', lable=lable, form=form)


@bp.route('lablec')
def lablec():
    lablec = session.get('lable_choice')
    mycol = list(db.table.find(projection=lablec))
    lable = list(mycol[0].keys())
    content = mycol
    m = len(lable)
    n = len(content)
    contentlist = []
    for i in range(0, n):
        contentlist.append(list(content[i].values()))
    return render_template('test/lablec.html', lablec=lablec, mycol=mycol, lable=lable, n=n, m=m, contentlist=contentlist)


@bp.route('/table')
def table():
    mycol = list(db.table.find(projection={'_id': False}))
    lable = list(mycol[0].keys())
    content = mycol
    n = len(content)
    return render_template('test/table.html', lable=lable, content=content, n=n)
