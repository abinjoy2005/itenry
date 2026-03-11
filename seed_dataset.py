import database
import json
import random
from datetime import datetime, timedelta
from psycopg2.extras import execute_values

def seed_data(count=10000):
    conn = database.get_db_connection()
    c = conn.cursor()

    print(f"Starting seed of {count} entries...")

    # 1. Ensure a seed user exists
    c.execute("INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING RETURNING user_id", 
              ('Seed User', 'seed@example.com', 'hashed_password'))
    res = c.fetchone()
    user_id = res[0] if res else None
    if not user_id:
        c.execute("SELECT user_id FROM users WHERE email = %s", ('seed@example.com',))
        user_id = c.fetchone()[0]

    # 2. Sample Data Collections
    destinations = {
        "Munnar": [("Eravikulam National Park", 4.8, 200), ("Tea Museum", 4.5, 150), ("Mattupetty Dam", 4.3, 50), ("Echo Point", 4.2, 20), ("Pothamedu Viewpoint", 4.6, 0)],
        "Alleppey": [("Houseboat", 4.9, 8000), ("Alappuzha Beach", 4.4, 0), ("Marari Beach", 4.7, 0), ("Vembanad Lake", 4.5, 500), ("Pathiramanal Island", 4.3, 200)],
        "Kochi": [("Fort Kochi", 4.7, 0), ("Mattancherry Palace", 4.5, 10), ("Jewish Synagogue", 4.6, 5), ("Marine Drive", 4.2, 0), ("Lulu Mall", 4.8, 0)],
        "Wayanad": [("Banasura Sagar Dam", 4.6, 100), ("Edakkal Caves", 4.7, 50), ("Pookode Lake", 4.4, 30), ("Soochipara Falls", 4.5, 50), ("Chembra Peak", 4.8, 750)],
        "Thekkady": [("Periyar National Park", 4.8, 500), ("Elephant Junction", 4.6, 1500), ("Spice Walk", 4.5, 100), ("Kalari Center", 4.7, 250), ("Mangala Devi Temple", 4.4, 0)],
        "Varkala": [("Papanasam Beach", 4.7, 0), ("Varkala Cliff", 4.8, 0), ("Janardhana Swami Temple", 4.5, 0), ("Anjengo Fort", 4.3, 0), ("Kappil Lake", 4.4, 0)],
        "Kovalam": [("Lighthouse Beach", 4.6, 0), ("Hawah Beach", 4.4, 0), ("Samudra Beach", 4.5, 0), ("Vizhinjam Marine Aquarium", 4.2, 50), ("Halcyon Castle", 4.3, 0)]
    }

    origins = ["Cochin", "Bangalore", "Chennai", "Mumbai", "Delhi", "Pune", "Hyderabad", "Kolkata"]
    interests_list = ["Museums", "Outdoor Adventures", "Shopping", "Children's Entertainment", "Off the beat activities", "Night Life", "Spirituality"]
    cuisines_list = ["Ethnic", "American", "Italian", "Mexican", "Chinese", "Indian", "Vegan"]
    companions = ["solo", "friends", "family", "couple"]
    transports = ["bus", "car", "train", "walking"]
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

    batch_size = 500
    
    for b in range(0, count, batch_size):
        current_batch_count = min(batch_size, count - b)
        places_to_insert = []
        
        try:
            for i in range(current_batch_count):
                dest_name = random.choice(list(destinations.keys()))
                origin = random.choice(origins)
                age = random.randint(18, 70)
                companion = random.choice(companions)
                has_kids = (companion == "family") or (random.random() < 0.2)
                interests = ",".join(random.sample(interests_list, random.randint(1, 3)))
                cuisines = ",".join(random.sample(cuisines_list, random.randint(1, 3)))
                trip_date = (datetime.now() - timedelta(days=random.randint(1, 1000))).strftime("%Y-%m-%d")
                stay_price = random.randint(800, 10000)
                stay_rating = round(random.uniform(3.0, 5.0), 1)
                
                # Insert Trip
                c.execute("""
                    INSERT INTO trip_experiences 
                    (user_id, origin, destination, trip_date, age, companion_type, has_children, interests, cuisine_preferences, stay_name, stay_price, stay_rating, total_expense)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING trip_id
                """, (user_id, origin, dest_name, trip_date, age, companion, has_kids, interests, cuisines, 
                    f"{dest_name} {random.choice(['Residency', 'Hotel', 'Villas', 'Spa', 'Inn'])}", 
                    stay_price, stay_rating, 0))
                
                trip_id = c.fetchone()[0]
                
                selected_places = random.sample(destinations[dest_name], random.randint(2, 4))
                total_exp = stay_price
                for p_idx, (p_name, p_rate, p_fee) in enumerate(selected_places):
                    t_cost = random.randint(20, 1000)
                    total_exp += (p_fee + t_cost)
                    places_to_insert.append((
                        trip_id, p_idx+1, p_name, p_rate, float(p_fee), float(random.randint(1, 50)), 
                        random.choice(transports), float(t_cost), round(random.uniform(1.0, 5.0), 1), random.choice(reviews_list)
                    ))
                
                # Update total_expense for the trip
                c.execute("UPDATE trip_experiences SET total_expense = %s WHERE trip_id = %s", (total_exp, trip_id))

            # Batch insert places for this batch of trips
            if places_to_insert:
                execute_values(c, """
                    INSERT INTO places_visited 
                    (trip_id, place_order, place_name, place_rating, entry_fee, distance_from_prev, travel_method, travel_cost, travel_rating, experience_review)
                    VALUES %s
                """, places_to_insert)

            conn.commit()
            print(f"Committed batch up to {b + current_batch_count} trips...")
            
        except Exception as e:
            conn.rollback()
            print(f"Error in batch starting at {b}: {e}")
            # Optional: break or continue. Let's break to be safe and investigate.
            raise e

    c.close()
    conn.close()
    print(f"Successfully seeded {count} entries into the database.")

if __name__ == '__main__':
    seed_data(10000)
