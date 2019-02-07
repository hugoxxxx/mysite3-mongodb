from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from pymongo import MongoClient, DESCENDING
from datetime import  datetime
from bson.objectid import ObjectId


bp = Blueprint('blog', __name__)
db = MongoClient().test_database

@bp.route('/')
def index():
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
            article = {"title": title, "body": body, "user_id": str(g.user['_id']), "created": datetime.utcnow()}
            db.blog.article.insert_one(article)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = db.blog.article.find_one({"_id": ObjectId(id)})

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['user_id'] != str(g.user['_id']):
        abort(403)

    return post


@bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    id = str(id)
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db.blog.article.update_one({"_id": ObjectId(id)},
                                       {'$set': {"title": title, "body": body}})
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    id = str(id)
    get_post(id)
    db.blog.article.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('blog.index'))
