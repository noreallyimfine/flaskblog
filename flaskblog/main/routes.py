from flask import Blueprint, request, render_template
from flaskblog.models import Post

main = Blueprint('main', __name__)

# home route, also root
@main.route("/")
@main.route("/home")
# function called home
def home():
    page = request.args.get('page', 1, type=int)
    # query db for all posts
    posts = Post.query.order_by(Post.date_posted.desc())\
                        .paginate(page=page, per_page=5)
    # render template for home.html, passing posts variable to display on home page
    return render_template("home.html", posts=posts)


# about route
@main.route("/about")
def about():
    return render_template("about.html")

