import os
from datetime import datetime

import flask as fl
from flask import request, session, redirect, url_for, render_template, make_response, send_from_directory
from library import DatabaseWorker, make_hash, check_hash_match, retrieve_following, get_all_posts, search_all_posts, check_session

app = fl.Flask(__name__)
db = DatabaseWorker('database.db')
app.secret_key = 'aslkcjfahroeuhnaczlfewhagakdjsfhaljasgakjhjoiaufecanmakweoiqwepsadfqf'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'static/images')
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

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


# User specific pages
@app.route('/')  # If session exists, redirect to home screen
def home():
    # Check if the user is logged in, if so, retrieve name, profile picture, saved categories, and saved posts
    if 'user_id' in session: #TODO: switch to new method using check_session
        user = db.search(f"SELECT id, uname, name, pfp, saved_cats, saved_posts FROM users WHERE id = {session['user_id']}", multiple=False)

        if request.method == 'GET':
            # print(get_all_posts(db=db, choice='categories', ids=retrieve_following('categories', db, session['user_id'])[0]))
            return render_template('home.html', user_id=session['user_id'], user=user, categories=retrieve_following('categories', db, session['user_id']),
                                   posts=get_all_posts(db, 'categories', retrieve_following('categories', db, session['user_id'])[0]))

    else:  # If not logged in, redirect to log in
        return redirect(url_for('login'))



@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])  # If session exists, show to profile screen, else redirect to login
def get_profile(user_id):
    if check_session(session) is None:
        return redirect(url_for('login'))
    else:
        if user_id == session['user_id']:
            if request.method == 'POST':
                pfp = request.files['pfp']
                if pfp:
                    filename = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")) + pfp.filename
                    pfp.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    db.run_query(f"UPDATE users SET pfp = '{filename}' WHERE id = {user_id}")
                return redirect(url_for('get_profile', user_id=user_id))
            else:
                user = db.search(f"SELECT id, uname, email, pfp, saved_cats, saved_posts FROM users WHERE id = {user_id}", multiple=False)
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
                return render_template("profile.html", is_self=True, user_id=session['user_id'], categories=categories, user=user, following_u=users, saved_posts=posts, posts=get_all_posts(db, 'users', [user[0]]))

        else: # User is requesting to see another user's profile
            categories = retrieve_following('categories', db, session['user_id'])  # Find saved categories for Navbar
            return render_template('profile.html', is_self=False, user_id=session['user_id'], categories=categories, user=db.search(f"SELECT id, uname, pfp FROM users WHERE id = {user_id}", multiple=False), posts=get_all_posts(db, 'users', [user_id]))


# Categories, posts, and threads
@app.route('/categories')  # Show button that redirects to all categories in alphabetical order
def all_categories():
    all_categories = db.search(query="SELECT * from categories ORDER BY name ASC", multiple=True)
    category_count = db.search(query="SELECT COUNT(*) FROM categories", multiple=False)[0]
    return render_template('all_categories.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']), all_categories=all_categories, count=category_count)


@app.route('/categories/new', methods=['GET', 'POST'])  # User can create new category
def new_category():
    if check_session(session) is None:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')

            file = request.files['image']
            print(file)
            if file:
                filename = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")) + file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = None
            db.run_query(f"INSERT INTO categories (name, description, img) VALUES ('{name}', '{description}', '{filename}')")
            return redirect(url_for('all_categories'))
        else:
            return render_template('new_category.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']))


@app.route('/categories/<int:cat_id>')  # Show all posts in a category
def get_category(cat_id):
    user_id = check_session(session)
    details = db.search(f"SELECT * FROM categories WHERE id={cat_id}", False)
    return render_template('category.html', user_id=user_id, categories=retrieve_following('categories', db, session['user_id']), details=details, posts=get_all_posts(db, choice="categories", ids=[cat_id]))


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])  # Show a post and all comments, form to add a new comment
def get_post(post_id):
    if check_session(session) is None:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            user_id = check_session(session)
            new_comment = request.form.get('new_comment')
            db.run_query(f"INSERT INTO comments (content, user_id, post_id) VALUES ('{new_comment}', {user_id}, {post_id})")
            return redirect(url_for('get_post', post_id=post_id))

        else:
            post = db.search(query=f"""SELECT posts.id, posts.date, posts.saved_count, posts.comment_count, posts.title, posts.content, posts.attachment, categories.id, categories.name, users.id, users.uname
                                        FROM posts INNER JOIN users ON posts.user_id = users.id INNER JOIN categories on posts.category_id = categories.id
                                        WHERE posts.id = {post_id}""", multiple=False)
            comments = db.search(query=f"""SELECT comments.id, comments.date, comments.content, users.id, users.uname
                                            FROM comments INNER JOIN users ON comments.user_id = users.id INNER JOIN posts ON comments.post_id = posts.id
                                            WHERE posts.id = {post_id}""", multiple=True)
            return render_template('post.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']), post=post, comments=comments, editing_comment=None)

@app.route('/categories/<int:cat_id>/post/new', methods=['GET', 'POST'])  # User can create new post in category
def new_post(cat_id):
    if check_session(session) is None:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            user_id = check_session(session)
            title = request.form.get('title')
            content = request.form.get('content')

            file = request.files['attachment']
            print(file)
            if file:
                filename = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")) + file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = None
            db.run_query(f"INSERT INTO posts (title, content, attachment, user_id, category_id) VALUES ('{title}', '{content}', '{filename}',{user_id}, {cat_id})")
            return redirect(url_for('get_category', cat_id=cat_id))
        else:
            cat_name = db.search(f"SELECT name FROM categories WHERE id = {cat_id}", multiple=False)[0]
            uname = db.search(f"SELECT uname FROM users WHERE id = {session['user_id']}", multiple=False)[0]
            return render_template('new_post.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']), cat_id=cat_id, cat_name=cat_name, uname=uname)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])  # Edit a post, if owner of post
def edit_post(post_id):
    if check_session(session) is None:
        redirect(url_for('login'))
    elif check_session(session) != db.search(f"SELECT user_id FROM posts WHERE id = {post_id}", multiple=False)[0]:
        return 'You do not have permission to edit this post'  # TODO: we need a proper popup or page for this
    else:
        if request.method=='POST':
            title = request.form.get('title')
            content = request.form.get('content')
            attachment = request.files['attachment']
            if not attachment:
                db.run_query(f"UPDATE posts SET title = '{title}', content = '{content}' WHERE id = {post_id}")
            else:
                filename = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")) + attachment.filename
                attachment.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.run_query(f"UPDATE posts SET title = '{title}', content = '{content}', attachment = '{filename}' WHERE id = {post_id}")
            return redirect(url_for('get_post', post_id=post_id))
        else:
            cat_id = db.search(f"SELECT category_id FROM posts WHERE id = {post_id}", multiple=False)[0]
            cat_name = db.search(f"SELECT name FROM categories WHERE id = {cat_id}", multiple=False)[0]
            uname = db.search(f"SELECT uname FROM users WHERE id = {session['user_id']}", multiple=False)[0]

            title = db.search(f"SELECT title FROM posts WHERE id = {post_id}", multiple=False)[0]
            content = db.search(f"SELECT content FROM posts WHERE id = {post_id}", multiple=False)[0]
            attachment = db.search(f"SELECT attachment FROM posts WHERE id = {post_id}", multiple=False)[0]
            return render_template('edit_post.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']), cat_id=cat_id, cat_name=cat_name, uname=uname, editing_post=[title, content, attachment])

@app.route('/post/<int:post_id>/delete')  # Delete a post, if owner of post
def delete_post(post_id):
    if check_session(session) is None:
        redirect(url_for('login'))
    elif check_session(session) != db.search(f"SELECT user_id FROM posts WHERE id = {post_id}", multiple=False)[0]:
        return 'You do not have permission to delete this post'  # TODO: we need a proper popup or page for this
    else:
        cat_id = db.search(f"SELECT category_id FROM posts WHERE id = {post_id}", multiple=False)[0]
        db.run_query(f"DELETE FROM comments WHERE post_id = {post_id}")
        db.run_query(f"DELETE FROM posts WHERE post_id={post_id}")
        return redirect(url_for('get_category', cat_id=cat_id))


@app.route(
    '/post/<int:post_id>/comment/<int:comment_id>/edit', methods=['GET', 'POST'])  # Edit or Delete a comment of post, if owner of comment
def edit_comment(post_id, comment_id):
    if check_session(session) is None:
        redirect(url_for('login'))
    elif check_session(session) != db.search(f"SELECT user_id FROM comments WHERE id = {comment_id}", multiple=False)[0]:
        return 'You do not have permission to edit this comment' #TODO: we need a proper popup or page for this
    else:
        if request.method == 'POST':
            new_comment = request.form.get('new_comment')
            db.run_query(f"UPDATE comments SET content = '{new_comment}' WHERE id = {comment_id}")
            db.run_query(f"UPDATE posts SET comment_count = comment_count + 1 WHERE id = {post_id}")
            return redirect(url_for("get_post", post_id=post_id))
        else:
            post = db.search(query=f"""SELECT posts.id, posts.date, posts.saved_count, posts.comment_count, posts.title, posts.content, posts.attachment, categories.id, categories.name, users.id, users.uname
                                                    FROM posts INNER JOIN users ON posts.user_id = users.id INNER JOIN categories on posts.category_id = categories.id
                                                    WHERE posts.id = {post_id}""", multiple=False)
            comments = db.search(query=f"""SELECT comments.id, comments.date, comments.content, users.id, users.uname
                                                        FROM comments INNER JOIN users ON comments.user_id = users.id INNER JOIN posts ON comments.post_id = posts.id
                                                        WHERE posts.id = {post_id}""", multiple=True)
            comment_content = db.search(f"SELECT content FROM comments WHERE id = {comment_id}", multiple=False)[0]
            return render_template('post.html', user_id=check_session(session), categories=retrieve_following('categories', db, session['user_id']), post=post, comments=comments, editing_comment=comment_content)


@app.route(
    '/post/<int:post_id>/comment/<int:comment_id>/delete')
def delete_comment(post_id, comment_id):
    if check_session(session) is None:
        redirect(url_for('login'))
    elif check_session(session) != db.search(f"SELECT user_id FROM comments WHERE id = {comment_id}", multiple=False)[0]:
        return 'You do not have permission to delete this comment'  # TODO: we need a proper popup or page for this
    else:
        db.run_query(f"DELETE FROM comments WHERE id = {comment_id}")
        db.run_query(f"UPDATE posts SET comment_count = comment_count - 1 WHERE id = {post_id}")
        return redirect(url_for('get_post', post_id=post_id))


@app.route('/uploads/<filename>')
def get_img(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/<filename>')
def get_default_img(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

if __name__ == '__main__':
    app.run()
