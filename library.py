import sqlite3
from passlib.hash import sha256_crypt


class dblib:  # For working with SQLlite database
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
def make_hash(text: str) -> str:
    return sha256_crypt.using(rounds=30000)(text)

def check_hash_match(text: str, hashed: str) -> bool:
    return sha256_crypt.using(rounds=30000).verify(text, hashed)
