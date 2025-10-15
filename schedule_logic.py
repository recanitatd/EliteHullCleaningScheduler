# schedule_logic.py
import pandas as pd

def generate_schedules(due_boats, pairs, target_pay_per_diver=200, pay_tolerance=50):
    """Generate schedules based on city grouping and pay targets."""
    schedules = {pair: [] for pair in pairs}
    
    # Extract city from address for grouping
    due_boats_copy = due_boats.copy()
    due_boats_copy['city'] = due_boats_copy['Location/Address'].str.extract(r', (.*?)(?=, FL)', expand=False)
    
    # Group boats by city
    city_groups = {name: group for name, group in due_boats_copy.groupby('city')}
    available_cities = list(city_groups.keys())
    remaining_boats = due_boats_copy[due_boats_copy['city'].isna()]  # Boats without clear city
    
    # Assign cities to teams
    num_teams = len([p for p in pairs if p[0] != "None" or p[1] != "None"])
    team_idx = 0
    
    for pair in pairs:
        diver1, diver2 = pair
        if diver1 == "None" and diver2 == "None":
            continue
        
        total_pay = 0
        schedule = []
        assigned_city = None
        
        # Try to assign a city to this team
        if available_cities and team_idx < len(available_cities):
            assigned_city = available_cities[team_idx]
            team_boats = city_groups[assigned_city].copy()
            
            for idx, boat in team_boats.iterrows():
                if total_pay < (target_pay_per_diver - pay_tolerance) * (2 if diver2 else 1):
                    pay_per_diver = boat["total_pay"] * (0.6 if not diver2 else 0.3)
                    if total_pay + pay_per_diver <= (target_pay_per_diver + pay_tolerance) * (2 if diver2 else 1):
                        schedule.append(boat)
                        total_pay += pay_per_diver
                        due_boats_copy = due_boats_copy[due_boats_copy["Boat ID/Name"] != boat["Boat ID/Name"]]
            
            # Remove assigned city from available cities
            if assigned_city in available_cities:
                available_cities.remove(assigned_city)
        
        # Add remaining boats if pay target not met
        remaining_options = due_boats_copy[due_boats_copy['city'].notna()]  # Only boats with cities
        for idx, boat in remaining_options.iterrows():
            if total_pay < (target_pay_per_diver - pay_tolerance) * (2 if diver2 else 1):
                pay_per_diver = boat["total_pay"] * (0.6 if not diver2 else 0.3)
                if total_pay + pay_per_diver <= (target_pay_per_diver + pay_tolerance) * (2 if diver2 else 1):
                    schedule.append(boat)
                    total_pay += pay_per_diver
                    due_boats_copy = due_boats_copy[due_boats_copy["Boat ID/Name"] != boat["Boat ID/Name"]]
        
        schedules[pair] = schedule
    
    missed_boats = due_boats_copy[["Boat ID/Name", "Size (ft)", "Location/Address", "Due Date", "total_pay"]]
    return schedules, missed_boats