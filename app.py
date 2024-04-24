from flask import Flask

app = Flask(__name__)

# For Login and Register
@app.route('/login') # Login screen
def login():
    return 'Login Page'

@app.route('/logout') # No screen just delete session and redirect to login
def login():
    return 'Login Page'

@app.route('/register') # Register screen
def register():
    return 'Register Page'

@app.route('/recover') # Recover account screen
def register():
    return 'Register Page'


# User specific pages
@app.route('/')  # If session exists, redirect to home screen
def home():
    return 'Home Screen'

@app.route('/profile')  #If session exists, show to profile screen, else redirect to login
def profile():
    return 'Profile Page'

@app.route('/profile/edit')  #If session exists, show to profile screen, else redirect to login
def profile():
    return 'Profile Page'


# Categories, posts, and threads
@app.route('/categories')  # Show button that redirects to all categories in alphabetical order
def all_categories():
    return 'All Categories'

@app.route('/categories/new')  # User can create new category
def new_categories():
    return 'New Category'

@app.route('/categories/<int:cat_id>')  # Show all posts in a category
def category(cat_id):
    return 'Category Page'

@app.route('/categories/<int:cat_id>/post/<int:post_id>')  # Show a post and all comments, form to add a new comment
def get_post(cat_id, post_id):
    return 'Post Page'

@app.route('/categories/<int:cat_id>/post/new')  # User can create new post in category
def new_post(cat_id):
    return 'New Post Page'

@app.route('/categories/<int:cat_id>/post/<int:post_id>/edit')  # Edit a post, if owner of post
def edit_post(cat_id, post_id):
    return 'Edit Post Page'

@app.route('/categories/<int:cat_id>/post/<int:post_id>/comment/<int:comment_id>')  # Edit a comment of post, if owner of comment
def edit_post(cat_id, post_id, comment_id):
    return 'Post Page'


if __name__ == '__main__':
    app.run()
