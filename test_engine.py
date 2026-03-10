from engine import recommendation, mcts_selector, optimizer, planner

data = {
    "origin": "Kochi",
    "destination": "Munnar",
    "budget": 1000,
    "duration": 1,
    "style": "moderate",
    "transport": "car",
    "age": 30
}

all_attractions = recommendation.get_top_attractions(data["destination"], user_prefs=data)
print(f"All: {len(all_attractions)}")

selected = mcts_selector.select_best_attractions(all_attractions, data["budget"], duration=data["duration"])
print(f"Selected: {len(selected)}")

optimized_route = optimizer.solve_tsp_2opt(selected)
print(f"Optimized: {len(optimized_route)}")

for i in range(len(optimized_route)):
    if i > 0:
        dist = recommendation.get_avg_distance(optimized_route[i-1]['place_name'], optimized_route[i]['place_name'])
        optimized_route[i]['distance_to_prev'] = dist
    else:
        optimized_route[i]['distance_to_prev'] = 0.0

city_transport_cost = recommendation.get_avg_transport_cost(data["destination"], data["transport"])
final_plan = planner.build_itinerary(optimized_route, duration=data["duration"], transport=data["transport"], avg_travel_cost=city_transport_cost)

print(f"Final Days: {len(final_plan['days'])}")
for d in final_plan['days']:
    print(f"Day {d['day_number']}: {len(d['route'])} spots")
