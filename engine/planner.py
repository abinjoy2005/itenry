import math
from datetime import datetime, timedelta

def build_itinerary(route: list, duration: int = 1, transport: str = "car", avg_travel_cost: float = 100.0, start_time: str = "09:00", stay_per_place: int = 120) -> dict:
    """
    Transforms an optimized route into a timed itinerary with estimated costs, 
    distributing attractions across multiple days and including travel methods and costs.
    """
    if not route:
        return {"days": [], "total_cost": 0.0}

    # Determine places per day (at least 1, max depends on route length)
    places_per_day = max(1, math.ceil(len(route) / duration))
    
    itinerary_days = []
    total_cost = 0.0
    
    for day_num in range(1, duration + 1):
        day_route = []
        current_time = datetime.strptime(start_time, "%H:%M")
        # Calculate slice for this day
        start_idx = (day_num - 1) * places_per_day
        end_idx = min(day_num * places_per_day, len(route))
        day_route_list = route[start_idx:end_idx]
        
        current_time = datetime.strptime(start_time, "%H:%M")
        
        # Add travel cost between days (except morning of Day 1)
        if day_num > 1 and day_route_list:
            pass # We will handle total_cost below based on segment cost

        if not day_route_list and day_num > 1:
            break

        for i, place in enumerate(day_route_list):
            dist = place.get('distance_to_prev', 0.0)
            
            # Determine dynamic transport and cost
            segment_transport = None
            segment_cost = 0.0
            
            is_first_of_trip = (day_num == 1 and i == 0)
            
            if not is_first_of_trip:
                if dist <= 1.5 and dist > 0:
                    segment_transport = "walking"
                    segment_cost = 0.0
                else:
                    segment_transport = transport
                    if transport == "car":
                        segment_cost = round((dist if dist > 0 else 5.0) * 15.0)
                    elif transport == "bus":
                        segment_cost = 30.0
                    elif transport == "bike":
                        segment_cost = round((dist if dist > 0 else 5.0) * 5.0)
                    else:
                        segment_cost = avg_travel_cost
            
            # 1. Travel Time Simulation (between places in a day)
            if not is_first_of_trip:
                current_time += timedelta(minutes=30)
                total_cost += segment_cost
                
            # 2. Place Visit Entry
            visit_entry = {
                "time": current_time.strftime("%H:%M"),
                "place": place.get('place_name', 'Unknown'),
                "cost": float(place.get('avg_fee', 0.0)),
                "rating": round(float(place.get('avg_rating', 0.0)), 1),
                "reviews": place.get('reviews', []),
                "transport": segment_transport,
                "travel_cost": segment_cost,
                "distance": dist
            }
            day_route.append(visit_entry)
            total_cost += float(place.get('avg_fee', 0.0))
            
            # 3. Visit Duration
            current_time += timedelta(minutes=stay_per_place)
            
        itinerary_days.append({
            "day_number": day_num,
            "route": day_route
        })
        
    return {
        "days": itinerary_days,
        "total_cost": round(total_cost, 2)
    }

if __name__ == '__main__':
    # Test stub
    mock_route = [
        {'place_name': 'Tea Museum', 'avg_fee': 200, 'avg_rating': 4.5},
        {'place_name': 'Mattupetty Dam', 'avg_fee': 50, 'avg_rating': 4.2}
    ]
    plan = build_itinerary(mock_route)
    print("Generated Plan:")
    for item in plan['days'][0]['route']:
        print(f"{item['time']} - {item['place']} (₹{item['cost']})")
    print(f"Total Cost: ₹{plan['total_cost']}")
