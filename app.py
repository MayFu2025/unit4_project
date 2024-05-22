import flask as fl
from flask import request, session, redirect, url_for, render_template
from library import DatabaseWorker, make_hash, check_hash_match

app = fl.Flask(__name__)
db = DatabaseWorker('database.db')


# For Login and Register
@app.route('/login', methods=['GET', 'POST'])  # Login screen
def login():
    # If user already logged in, redirect to home screen
    if 'user_id' in session:
        return redirect(url_for('home'))
    # Recieve username and password
    if request.method == 'POST':
        uname = request.form.get('uname')
        pword = request.form.get('pword')
        # Check database for user, then compare hash
        results = db.search(f"SELECT * FROM users WHERE uname = '{uname}'", multiple=False)
        if len(results) != 1:
            return 'User not Found'  # User not found, redirect to somewhere
        else:
            if check_hash_match(pword, results[3]):
                session['user_id'] = results[0]
                return redirect(url_for('home'))
            else:
                return 'Incorrect Password'  # Incorrect password redirect to somewhere

    return render_template('login.html')


@app.route('/logout')  # No screen just delete session and redirect to login
def logout():
    return 'Login Page'


@app.route('/register', methods=['GET', 'POST'])  # Register screen
def register():
    # If user already logged in, redirect to home screen
    if 'user_id' in session:
        return redirect(url_for('home'))
    # Receive new user details
    if request.method == 'POST':
        uname = request.form.get('uname')
        email = request.form.get('email')
        pword = request.form.get('pword')
        check_pword = request.form.get('check_pword')

        # Check database for existing users
        results = db.search(f"SELECT * FROM users WHERE uname = '{uname}' or email = '{email}'", multiple=False)
        if results is not None:
            if len(results) != 0:
                print('Username already taken, or email already in use')
                return 'Username already taken, or email already in use'  # Redirect to somewhere
            else:  # Check that passwords match
                if pword != check_pword:
                    print('Passwords do not match')
                    return 'Passwords do not match'
                else:
                    # Hash password and insert into database
                    hashed_pword = make_hash(pword)
                    db.run_query(f"INSERT INTO users (uname, email, pword) VALUES ('{uname}', '{email}', '{hashed_pword}')")
                    print('New user created')
                    return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/recover')  # Recover account screen
def recover():
    return 'Register Page'


# User specific pages
@app.route('/')  # If session exists, redirect to home screen
def home():
    return 'Home Screen'


@app.route('/profile')  # If session exists, show to profile screen, else redirect to login
def profile():
    return 'Profile Page'


@app.route('/profile/edit')  # If session exists, show to profile screen, else redirect to login
def edit_profile():
    return 'Profile Page'


# Categories, posts, and threads
@app.route('/categories')  # Show button that redirects to all categories in alphabetical order
def all_categories():
    return 'All Categories'


@app.route('/categories/new')  # User can create new category
def new_category():
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


@app.route(
    '/categories/<int:cat_id>/post/<int:post_id>/comment/<int:comment_id>')  # Edit a comment of post, if owner of comment
def edit_comment(cat_id, post_id, comment_id):
    return 'Post Page'


if __name__ == '__main__':
    app.run()
