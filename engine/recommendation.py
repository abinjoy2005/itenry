import sqlite3
import os

# Assuming database.py is in the parent directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'travel.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_top_attractions(destination, limit=20):
    """
    Aggregates community data to find top attractions for a destination.
    Returns a list of dicts with name, avg_rating, avg_fee, and popularity count.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    query = '''
        SELECT 
            p.place_name,
            AVG(p.place_rating) as avg_rating,
            AVG(p.entry_fee) as avg_fee,
            COUNT(p.place_id) as visitation_count
        FROM places_visited p
        JOIN trip_experiences t ON p.trip_id = t.trip_id
        WHERE LOWER(t.destination) = LOWER(?)
        GROUP BY p.place_name
        ORDER BY avg_rating DESC, visitation_count DESC
        LIMIT ?
    '''
    
    rows = c.execute(query, (destination, limit)).fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_travel_stats(destination):
    """
    Calculates average travel costs and ratings between places for a destination.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    query = '''
        SELECT 
            travel_method,
            AVG(travel_cost) as avg_cost,
            AVG(travel_rating) as avg_rating,
            AVG(distance_from_prev) as avg_distance,
            COUNT(*) as frequency
        FROM places_visited p
        JOIN trip_experiences t ON p.trip_id = t.trip_id
        WHERE LOWER(t.destination) = LOWER(?) AND travel_method IS NOT NULL
        GROUP BY travel_method
    '''
    
    rows = c.execute(query, (destination,)).fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

if __name__ == '__main__':
    # Test with mock data if needed
    stats = get_top_attractions('Munnar')
    print("Top Attractions in Munnar:")
    for s in stats:
        print(f"- {s['place_name']}: {s['avg_rating']} stars (Fee: ₹{s['avg_fee']})")
