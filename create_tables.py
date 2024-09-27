import sqlite3
from werkzeug.security import generate_password_hash

def create_tables(database_path):
    # Connect to the database
    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()

        # Create the Users table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')

        # Create the Images table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                image BLOB NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users (id)
            )
        ''')

        # Commit the changes
        connection.commit()

# Replace 'your_database_path/Login.db' with the actual path to your SQLite database file
database_path = 'Login.db'
create_tables(database_path)
