import sqlite3
from passlib.hash import sha256_crypt
from flask import redirect, url_for


class DatabaseWorker:  # For working with SQLlite database
    def __init__(self, name: str):
        self.name_db = name

        # Step 1: Create a connection
        self.connection = sqlite3.connect(self.name_db, check_same_thread=False)
        # Step 2: Set cursor/where it inputs into table
        self.cursor = self.connection.cursor()
        # message
        print("Connection Successful")

    def run_query(self, query: str):
        self.cursor.execute(query)  # Run query
        self.connection.commit()  # Save changes

    def search(self, query: str, multiple: bool = False):
        results = self.cursor.execute(query)
        self.run_query(query)
        if multiple:
            return results.fetchall()  # Fetchall returns multiple rows
        else:
            return results.fetchone()  # [0] Fetchone returns single value

    def search_debug(self, query: str, multiple: bool = False):
        results = self.run_query(query=query)

        if multiple:
            return results.fetchall()  # Fetchall returns multiple rows
        else:
            return results.fetchone()  # [0] Fetchone returns single value

    def close(self):
        self.connection.close()


# Functions for hashing/verification
hasher = sha256_crypt.using(rounds=30000)


def make_hash(text: str) -> str:
    return hasher.hash(text)


def check_hash_match(text: str, hashed: str) -> bool:
    return hasher.verify(text, hashed)


def retrieve_following(choice: str, db: object, user_id:int):
    """Retrieves saved categories, posts, or users that the user is following.
    Returns a list of lists with ids and names"""
    choices = {'categories': ['saved_cats', 'name'],
               'posts': ['saved_posts','title'],
               'users': ['following_u','uname']}
    if choice in choices:
        result = db.search(f"SELECT {choices[choice][0]} FROM users WHERE id = {user_id}", multiple=False)[0]
        if result is None:
            ids = []
            names = []
        else:
            ids = list(map(int, result.split(',')))
            names = []
            for id in ids:
                print(db.search(f"SELECT {choices[choice][1]} FROM {choice} WHERE id = {choice +'.id'}", multiple=False)[0])
                names.append(db.search(f"SELECT {choices[choice][1]} FROM {choice} WHERE id = {choice +'.id'}", multiple=False)[0])
    else:
        return "Invalid Choice"
    return [ids, names]


def get_all_posts(db: object, choice:str, ids: list[int]):
    """Returns all posts that belong to the requested categories given as a list of category ids, latest posts first"""
    choices = {'categories': 'category_id',
               'posts': 'posts.id',
               'users': 'user_id'}
    query = "SELECT posts.id, posts.date, posts.saved_count, posts.comment_count, posts.title, categories.id, categories.name, users.id, users.uname FROM posts INNER JOIN categories ON posts.category_id = categories.id INNER JOIN users ON posts.user_id = users.id WHERE "
    for id in ids:
        query += f"{choices[choice]} = " + str(id) + " OR "
    query = query[:-3] + "ORDER BY date DESC" # Remove the last space and OR then sorts by date
    print(query)
    print(db.search(query, multiple=True))
    return db.search(query, multiple=True)


def search_all_posts(db:object, keyword:str):
    """Returns all posts that match the query in either the title, content, or author, most saved posts first"""
    query = f"""SELECT posts.id, posts.date, posts.saved_count, posts.comment_count, posts.title, categories.id, categories.name, users.id, users.uname
                FROM posts INNER JOIN categories ON posts.category_id = categories.id INNER JOIN users ON posts.user_id = users.id
                WHERE posts.title LIKE '%{keyword}%' OR posts.content LIKE '%{keyword}%' OR users.uname LIKE '%{keyword}%'
                SORT BY posts.saved_count DESC"""
    return db.search(query, multiple=True)

def check_session(session)-> int:
    """Checks if the user is logged in, returns user_id"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    else:
        return session['user_id']