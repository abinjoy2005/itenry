import database
import csv

def export_to_csv(filename='travel_dataset.csv'):
    conn = database.get_db_connection()
    c = conn.cursor()

    print(f"Exporting dataset to {filename}...")

    # Join trip_experiences and places_visited for a complete view
    query = """
        SELECT 
            t.trip_id, t.origin, t.destination, t.trip_date, t.age, t.companion_type, t.has_children, 
            t.interests, t.cuisine_preferences, t.stay_name, t.stay_price, t.stay_rating, t.total_expense,
            p.place_name, p.place_rating, p.entry_fee, p.distance_from_prev, p.travel_method, 
            p.travel_cost, p.travel_rating, p.experience_review
        FROM trip_experiences t
        LEFT JOIN places_visited p ON t.trip_id = p.trip_id
        ORDER BY t.trip_id, p.place_order
    """
    
    c.execute(query)
    rows = c.fetchall()
    colnames = [desc[0] for desc in c.description]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(colnames)
        writer.writerows(rows)

    c.close()
    conn.close()
    print(f"Successfully exported {len(rows)} records to {filename}.")

if __name__ == '__main__':
    export_to_csv()
