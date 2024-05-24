import flask as fl
from flask import request, session, redirect, url_for, render_template, make_response
from library import DatabaseWorker, make_hash, check_hash_match

app = fl.Flask(__name__)
db = DatabaseWorker('database.db')
app.secret_key = 'aslkcjfahroeuhnaczlfewhagakdjsfhaljasgakjhjoiaufecanmakweoiqwepsadfqf'


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
        print(uname, pword)
        # Check database for user, then compare hash
        results = db.search(f"SELECT * FROM users WHERE uname = '{uname}'", multiple=False)
        print(results)
        if results is None:
            print('User not found')
            return 'User not Found'  # User not found, redirect to somewhere
        else:
            if check_hash_match(pword, results[3]):
                session['user_id'] = results[0]
                print('Log-in Successful')
                return redirect(url_for('home'))
            else:
                print('Incorrect Password')
                return 'Incorrect Password'  # Incorrect password redirect to somewhere
    return render_template('login.html')


@app.route('/logout')  # No screen just delete session and redirect to login
def logout():
    session.pop('user_id', None)
    # response = make_response(redirect(url_for('login_page')))
    return redirect(url_for('login'))


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
        results = db.search(f"SELECT * FROM users WHERE uname = '{uname}' or email = '{email}'", multiple=True)
        print(results)
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
                db.run_query(
                    f"INSERT INTO users (uname, email, password) VALUES ('{uname}', '{email}', '{hashed_pword}')")
                print('New user created')
                return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/recover')  # Recover account screen
def recover():
    return 'Register Page'


# User specific pages
@app.route('/')  # If session exists, redirect to home screen
def home():
    # Check if the user is logged in, if so, retrieve name, profile picture, saved categories, and saved posts
    if 'user_id' in session:
        user_id = session['user_id']
        user = db.search(f"SELECT uname, name, pfp, saved_cats, saved_posts FROM users WHERE id = {user_id}", multiple=False)
        # Find name
        if user[1] is None:
            name = user[0]
        else:
            name = user[1]
        # Find following categories to show on sidebar
        if user[3] is None:
            following = []
        else:
            following = map(int, user[3].split(','))
    else:  # If not logged in, redirect to log in
        return redirect(url_for('login'))
    return render_template('home.html', name=name, following=following)


@app.route('/profile')  # If session exists, show to profile screen, else redirect to login
def profile():
    # Check if the user is logged in, if so, retrieve name, email, profile picture, saved categories, and saved posts
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            user = db.search(f"SELECT uname, email, name, pfp, saved_cats, saved_posts FROM users WHERE id = {user_id}", multiple=False)
            # Find name
            if user[2] is None: name = 'No name set'
            else: name = user[2]
            # Find email
            email = user[1]
            # Find profile picture
            pfp = user[3]
            # Find saved categories
            if user[4] is None: saved_cats = []
            else: saved_cats = map(int, user[4].split(','))
            # Find saved posts
            if user[5] is None:
                saved_posts = []
            else:
                saved_posts = map(int, user[5].split(','))
    return render_template('profile.html', username=user[0], email=email, name=name, pfp=pfp, saved_cats=saved_cats, saved_posts=saved_posts)


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
def get_category(cat_id):
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
