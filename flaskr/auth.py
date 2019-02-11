import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email

bp = Blueprint('auth', __name__, url_prefix='/auth')


class RegisterForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired(message=u'用户名不能为空'), Length(1, 64)])
    password = PasswordField(u'密码', validators=[DataRequired(message=u'密码不能为空')])
    submit = SubmitField(u'提交')


class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired(message=u'用户名不能为空'), Length(1, 64)])
    password = PasswordField(u'密码', validators=[DataRequired(message=u'密码不能为空')])
    submit = SubmitField(u'登录')


def encrypt_password(password):
    return generate_password_hash(password)


def verify_password(user_password, password):
    return check_password_hash(user_password, password)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = MongoClient().test_database
        error = None

        if db.user.find_one({"username": username}) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            password = encrypt_password(password)
            db.user.insert_one({"username": username, "password": password})
            return redirect(url_for('auth.login'))

        flash(error, category='error')

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        if form.validate_on_submit():
            db = MongoClient().test_database
            error = None
            user = db.user.find_one({"username": username})

            if user is None:
                error = 'Incorrect username.'
            elif not verify_password(user.get("password"), password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = str(user['_id'])
                return redirect(url_for('index'))

            flash(error)

    return render_template('auth/login.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = MongoClient().test_database.user.find_one({"_id": ObjectId(user_id)})


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
