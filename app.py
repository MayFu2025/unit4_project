import flask as fl
from flask import request, session, redirect, url_for, render_template, make_response
from library import DatabaseWorker, make_hash, check_hash_match, retrieve_following, get_all_posts, search_all_posts, check_session

app = fl.Flask(__name__)
db = DatabaseWorker('database.db')
app.secret_key = 'aslkcjfahroeuhnaczlfewhagakdjsfhaljasgakjhjoiaufecanmakweoiqwepsadfqf'

# if check_session(session) is not None:
#     user = db.search(f"SELECT id, uname, name, pfp, saved_cats, saved_posts FROM users WHERE id = {session['user_id']}", multiple=False)
#     categories = retrieve_following('categories', db, session['user_id'])
#     posts = retrieve_following('posts', db, session['user_id'])
#     users = retrieve_following('users', db, session['user_id'])


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
        user = db.search(f"SELECT id, uname, name, pfp, saved_cats, saved_posts FROM users WHERE id = {session['user_id']}", multiple=False)

        if request.method == 'GET':
            # print(get_all_posts(db=db, choice='categories', ids=retrieve_following('categories', db, session['user_id'])[0]))
            return render_template('home.html', user_id=session['user_id'], user=user, categories=retrieve_following('categories', db, session['user_id']),
                                   posts=get_all_posts(db, 'categories', retrieve_following('categories', db, session['user_id'])[0]))

        elif request.method == 'POST':  #TODO: not working but also not priority :D
            keyword = request.form.get('search')
            # print(keyword)
            results = search_all_posts(db, keyword)
            return redirect(url_for('search', user=user, categories=retrieve_following('categories', db, session['user_id']),
                                   keyword=keyword, results=results))

    else:  # If not logged in, redirect to log in
        return redirect(url_for('login'))


@app.route('/?search=<string:keyword>')  # Search for keyword in posts
def search(user, categories, keyword, results):
    return render_template('results.html', user=user, categories=categories, keyword=keyword, results=results)

@app.route('/profile/<int:user_id>')  # If session exists, show to profile screen, else redirect to login
def get_profile(user_id):
    if 'user_id' in session:
        if user_id == session['user_id']:
            user = db.search(f"SELECT id, uname, name, email, pfp, saved_cats, saved_posts FROM users WHERE id = {user_id}", multiple=False)
            categories = retrieve_following('categories', db, user_id)
            posts = get_all_posts(db, choice='posts', ids=retrieve_following('posts', db, user_id)[0])

            if len(retrieve_following('users', db, user_id)[0]) == 0:
                users = []
            else:
                query = "SELECT id, uname, pfp FROM users WHERE "
                for id in retrieve_following('users', db, user_id)[0]:
                    query += f"id = {id} OR "
                query = query[:-4]
                users = db.search(query, multiple=True)
            # print(retrieve_following('users', db, user_id)[0])
            # print(users)
            return render_template("profile.html", is_self=True, user_id=session['user_id'], categories=categories, user=user, following_u=users, saved_posts=posts, posts=get_all_posts(db, 'users', [user[0]]))

        else: # User is requesting to see another user's profile
            categories = retrieve_following('categories', db, session['user_id'])  # Find saved categories for Navbar
            # print(categories)
            return render_template('profile.html', is_self=False, user_id=session['user_id'], categories=categories, user=db.search(f"SELECT id, uname, pfp FROM users WHERE id = {user_id}", multiple=False), posts=get_all_posts(db, 'users', [user_id]))
    else:
        return redirect(url_for('login'))




    # else:
    #
    #         if user_id == session['user_id']:  # The user is requesting to see their own profile
    #             user = db.search(f"SELECT * FROM users WHERE id = {u_id}", multiple=False)
    #             print(user)
    #             # Find saved categories
    #             saved_cats = retrieve_following('categories', db, user_id)
    #             # Find saved posts
    #             saved_posts = retrieve_following('posts', db, user_id)
    #             # Find following users
    #             following_u = retrieve_following('users', db, user_id)
    #             return render_template('profile.html', user_id=user[0], details=user, saved_cats=saved_cats,saved_posts=saved_posts, following_u=following_u)
    #         else:  # The user is requesting to see another user's profile
    #             user = db.search(f"SELECT id, uname, pfp FROM users WHERE id = {user_id}", multiple=False)
    #             return render_template('profile.html', user_id=user[0], details=user)

@app.route('/profile/<int:user_id>/edit')  # If session exists, show to profile screen, else redirect to login
def edit_profile():
    return 'Profile Page'


# Categories, posts, and threads
@app.route('/categories')  # Show button that redirects to all categories in alphabetical order
def all_categories():
    all_categories = db.search(query="SELECT * from categories ORDER BY name ASC", multiple=True)
    category_count = db.search(query="SELECT COUNT(*) FROM categories", multiple=False)[0]
    return render_template('all_categories.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']), all_categories=all_categories, count=category_count)


@app.route('/categories/new')  # User can create new category
def new_category():
    return 'New Category'


@app.route('/categories/<int:cat_id>')  # Show all posts in a category
def get_category(cat_id):
    user_id = check_session(session)
    details = db.search(f"SELECT * FROM categories WHERE id={cat_id}", False)
    return render_template('category.html', user_id=user_id, categories=retrieve_following('categories', db, session['user_id']), details=details, posts=get_all_posts(db, choice="categories", ids=[cat_id]))


@app.route('/post/<int:post_id>')  # Show a post and all comments, form to add a new comment
def get_post(post_id):
    post = db.search(query=f"""SELECT posts.id, posts.date, posts.saved_count, posts.comment_count, categories.id, categories.name, users.id, users.uname
                                FROM posts INNER JOIN users ON posts.user_id = users.id INNER JOIN categories on posts.category_id = categories.id
                                WHERE posts.id = {post_id}""", multiple=False)
    comments = db.search(query=f"""SELECT comments.id, comments.date, comments.content, users.id users.uname
                                    FROM comments INNER JOIN users ON comments.user_id = users.id
                                    WHERE posts.id = {post_id}""", multiple=True)
    print(post)
    print(comments)
    return render_template('post.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']), post=post, comments=comments)


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
