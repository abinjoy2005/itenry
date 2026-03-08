import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create tables based on architecture (PostgreSQL syntax)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            preferences TEXT
        );

        CREATE TABLE IF NOT EXISTS trip_experiences (
            trip_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            destination TEXT,
            trip_date TEXT,
            companion_type TEXT,
            stay_name TEXT,
            stay_price REAL,
            stay_rating REAL,
            total_expense REAL
        );

        CREATE TABLE IF NOT EXISTS places_visited (
            place_id SERIAL PRIMARY KEY,
            trip_id INTEGER REFERENCES trip_experiences(trip_id),
            place_order INTEGER,
            place_name TEXT,
            place_rating REAL,
            entry_fee REAL,
            distance_from_prev REAL,
            travel_method TEXT,
            travel_cost REAL,
            travel_rating REAL,
            experience_review TEXT
        );
    ''')
    
    conn.commit()
    c.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("PostgreSQL Database initialized successfully.")
