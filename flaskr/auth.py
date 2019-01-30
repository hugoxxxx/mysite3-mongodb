import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient



bp = Blueprint('auth', __name__, url_prefix='/auth')


def encrypt_passowrd(password):
    return generate_password_hash(password)


def verify_password(user_password, password):
    return check_password_hash(user_password, password)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = MongoClient().test_database
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.user.find_one({"username":username}) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            password = encrypt_passowrd(password)
            db.user.insert_one({"username":username, "password":password})
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = MongoClient().test_database
        error = None
        user = db.user.find_one({"username":username})

        if user is None:
            error = 'Incorrect username.'
        elif not verify_password(user.get("password"), password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['_id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = MongoClient().test_database.user.find_one({"_id": user_id})
