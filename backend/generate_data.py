import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

NUM_SAMPLES = 5000

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Kolkata", "Chennai", 
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
]

CARRIERS = [
    "Delhivery", "Blue Dart", "DTDC", "Ecom Express", 
    "Shadowfax", "Xpressbees", "India Post"
]

WEATHER_CONDITIONS = ["Clear", "Rain", "Heavy Rain (Monsoon)", "Fog", "Storm"]
TRAFFIC_LEVELS = ["Low", "Medium", "High", "Jam (Gridlock)"]

SHIPMENT_TYPES = ["B2B", "B2C"]
SERVICE_LEVELS = ["Standard", "Express", "Same Day"]
MODES = ["Road", "Air"]
PRIORITIES = ["Normal", "High"]

def generate_logistics_data():
    data = []

    for _ in range(NUM_SAMPLES):
        origin = random.choice(CITIES)
        destination = random.choice(CITIES)
        while origin == destination:
            destination = random.choice(CITIES)
        
        carrier = random.choice(CARRIERS)
        distance = random.randint(50, 2500)

        shipment_type = random.choice(SHIPMENT_TYPES)
        service_level = random.choice(SERVICE_LEVELS)
        mode = random.choice(MODES)
        priority = random.choice(PRIORITIES)
        package_weight = round(random.uniform(0.2, 40.0), 2)
        
        month = random.randint(1, 12)
        
        if month in [6, 7, 8, 9]:
            weather_weights = [30, 30, 30, 5, 5]
        elif month in [12, 1]:
            weather_weights = [50, 5, 5, 35, 5]
        else:
            weather_weights = [70, 10, 5, 5, 10]

        weather = random.choices(WEATHER_CONDITIONS, weights=weather_weights)[0]
        
        metro_cities = ["Mumbai", "Bangalore", "Delhi"]
        if origin in metro_cities or destination in metro_cities:
            traffic_weights = [10, 30, 40, 20]
        else:
            traffic_weights = [40, 40, 15, 5]

        traffic = random.choices(TRAFFIC_LEVELS, weights=traffic_weights)[0]
        
        is_festival_season = 1 if month in [10, 11] else 0

        if service_level == "Same Day":
            promised_sla_hours = random.choice([8, 12])
        elif service_level == "Express":
            promised_sla_hours = random.choice([24, 36])
        else:
            promised_sla_hours = random.choice([48, 72, 96])

        delay_probability = 0.05
        added_delay_hours = 0
        
        if weather == "Heavy Rain (Monsoon)":
            delay_probability += 0.50
            added_delay_hours += random.uniform(5.0, 24.0)
        elif weather == "Rain":
            delay_probability += 0.20
            added_delay_hours += random.uniform(1.0, 4.0)
        elif weather == "Fog" and (origin == "Delhi" or destination == "Delhi"):
            delay_probability += 0.60
            added_delay_hours += random.uniform(4.0, 12.0)
            
        if traffic == "Jam (Gridlock)":
            delay_probability += 0.40
            added_delay_hours += random.uniform(2.0, 6.0)
        
        if is_festival_season:
            delay_probability += 0.15
            added_delay_hours += random.uniform(12.0, 48.0)

        if mode == "Road" and distance > 800:
            delay_probability += 0.15
            added_delay_hours += random.uniform(4.0, 16.0)

        if package_weight > 20:
            delay_probability += 0.05
            added_delay_hours += random.uniform(1.0, 5.0)

        if priority == "High":
            delay_probability -= 0.05

        if mode == "Air":
            delay_probability -= 0.05

        is_delayed = 1 if random.random() < delay_probability else 0
        actual_delay_hours = added_delay_hours if is_delayed == 1 else 0

        data.append({
            "Origin": origin,
            "Destination": destination,
            "Distance_km": distance,
            "Carrier": carrier,
            "Shipment_Type": shipment_type,
            "Service_Level": service_level,
            "Mode": mode,
            "Priority": priority,
            "Package_Weight_kg": package_weight,
            "Promised_SLA_Hours": promised_sla_hours,
            "Weather": weather,
            "Traffic": traffic,
            "Month": month,
            "Is_Festival_Season": is_festival_season,
            "Delayed": is_delayed,
            "Delay_Hours": round(actual_delay_hours, 2)
        })

    df = pd.DataFrame(data)
    df.to_csv("backend/data/shipment_data.csv", index=False)
    print(f"Generated {NUM_SAMPLES} Indian shipment records in backend/data/shipment_data.csv")

if __name__ == "__main__":
    generate_logistics_data()