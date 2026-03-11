import database
import random
from psycopg2.extras import execute_batch

reviews_list = [
    "Absolutely loved it, highly recommend!",
    "It was okay, a bit crowded but worth seeing.",
    "Not what I expected, but still a decent experience.",
    "Fantastic place! Will definitely visit again.",
    "The views were breathtaking, 10/10.",
    "A bit overpriced for what you get.",
    "Great for families and kids, we all enjoyed it.",
    "A must-visit location if you are in town.",
    "Peaceful and serene, a perfect getaway.",
    "Incredible history and culture to absorb here.",
    "Average experience, could have been better.",
    "Truly a hidden gem!",
    "Amazing vibe, great food around.",
    "Too touristy for my taste, but still nice.",
    "One of the highlights of my trip!"
]

def update_data():
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT place_id FROM places_visited")
    rows = c.fetchall()
    print(f"Found {len(rows)} places. Updating...")
    
    update_data = [(round(random.uniform(1.0, 5.0), 1), random.choice(reviews_list), row[0]) for row in rows]
    
    execute_batch(c, """
        UPDATE places_visited 
        SET travel_rating = %s, experience_review = %s 
        WHERE place_id = %s
    """, update_data, page_size=1000)
    
    conn.commit()
    
    # Verify the update
    c.execute("SELECT travel_rating, experience_review FROM places_visited LIMIT 5")
    sample = c.fetchall()
    print("Sample updated records:")
    for row in sample:
        print(f"Rating: {row[0]}, Review: {row[1]}")
        
    c.close()
    conn.close()
    print("Successfully updated the dataset!")

if __name__ == '__main__':
    update_data()
