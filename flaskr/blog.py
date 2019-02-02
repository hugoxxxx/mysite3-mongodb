from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from pymongo import MongoClient, DESCENDING

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = MongoClient().test_database
    posts = db.blog.article.find().sort("title", DESCENDING)
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = MongoClient().test_database
            article = {"title": title, "body": body, "user_id": str(g.user['_id'])}
            db.blog.article.insert_one(article)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')
