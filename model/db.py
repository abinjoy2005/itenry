import os
import sqlite3
from datetime import datetime

_DB_FILE_NAME = 'query_logs.db'


def initialize_database() -> None:
    """Create database and table if they don't exist"""
    conn = sqlite3.connect(_DB_FILE_NAME)
    c = conn.cursor()

    # Create table
    c.execute("""CREATE TABLE IF NOT EXISTS query_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME NOT NULL,
                  origin TEXT,
                  destination TEXT NOT NULL,
                  age INTEGER NOT NULL,
                  trip_duration INTEGER NOT NULL,
                  budget INTEGER)""")
    conn.commit()
    conn.close()

def retrieve_data():
    """
    Retrieves all data fron the table.
    """

    try:
       # Connect to the SQLite database
        conn = sqlite3.connect(_DB_FILE_NAME)
        cursor = conn.cursor()

        # Retrieve all data from the specified table
        cursor.execute(f"SELECT * FROM query_logs")
        data = cursor.fetchall()

        # Close the database connection
        conn.close()
        for item in data:
            print (item)

    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None


def log_query(origin: str, destination: str,
              age: int, trip_duration: int, budget: int) -> None:
    """Log a query to the database"""

    # Check if file exists, if not initialize the db
    if not os.path.isfile(_DB_FILE_NAME):
        initialize_database()

    conn = sqlite3.connect(_DB_FILE_NAME)
    c = conn.cursor()

    # Insert log record
    c.execute(
        """INSERT INTO query_logs 
                 (timestamp, origin, destination, age, trip_duration, budget)
                 VALUES (?, ?, ?, ?, ?, ?)""",
        (datetime.now(), origin, destination, age, trip_duration, budget),
    )
    conn.commit()
    conn.close()

"""
    If this program is executed directly, just print out all the data in the tables
"""
if __name__ == "__main__":
    retrieve_data() 
