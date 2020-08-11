from flask import (Blueprint, flash, redirect, url_for,
                   render_template, abort, request)
from flask_login import login_required, current_user
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flaskblog.models import Post

posts = Blueprint('posts', __name__)


# new post route, also accepts POST
@posts.route("/post/new", methods=['GET', 'POST'])
# required login decorator
@login_required
def new_post():
    # create that form
    form = PostForm()
    # did they submit a valid form?
    if form.validate_on_submit():
        # create a Post
        post = Post(title=form.title.data,
                    content=form.content.data,
                    author=current_user)
        # add to db
        db.session.add(post)
        db.session.commit()
        # show message
        flash('Your post has been created!', 'success')
        # send them home after logging in
        return redirect(url_for('main.home'))
    # for GET request, just base create post template
    return render_template('create_post.html', title='New Post',
                           form=form, legend="New Post")


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated", 'succes')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend="Update Post")


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))
