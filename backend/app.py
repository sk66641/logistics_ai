import hashlib
import random

import joblib
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Logistics Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("⏳ Loading Models...")
classifier = joblib.load("backend/models/classifier.joblib")
regressor = joblib.load("backend/models/regressor.joblib")
model_columns = joblib.load("backend/models/model_columns.joblib")
print(f"✅ Models Loaded. Expecting {len(model_columns)} features.")

class ShipmentRequest(BaseModel):
    Origin: str
    Destination: str
    Carrier: str
    Date: str
    ShipmentType: str | None = None
    ServiceLevel: str | None = None
    Mode: str | None = None
    Priority: str | None = None
    PackageWeightKg: float | None = None
    SLAHours: int | None = None


def _seed_from(*parts: str) -> int:
    key = "|".join(str(p) for p in parts)
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)

def get_live_weather(city, date):
    conditions = ["Clear", "Rain", "Heavy Rain (Monsoon)", "Fog", "Storm"]
    weights = [60, 20, 10, 5, 5]
    rng = random.Random(_seed_from(city, date, "weather"))
    return rng.choices(conditions, weights=weights)[0]

def get_traffic_factor(origin, destination):
    rng = random.Random(_seed_from(origin, destination, "traffic"))
    return rng.choice(["Low", "Medium", "High", "Jam (Gridlock)"])

def get_distance(origin, destination):
    rng = random.Random(_seed_from(origin, destination, "distance"))
    return rng.randint(50, 2500)

@app.post("/predict")
def predict_delay(request: ShipmentRequest):
    try:
        weather = get_live_weather(request.Destination, request.Date)
        traffic = get_traffic_factor(request.Origin, request.Destination)
        distance = get_distance(request.Origin, request.Destination)
        
        shipment_type = request.ShipmentType or "B2B"
        service_level = request.ServiceLevel or "Standard"
        mode = request.Mode or "Road"
        priority = request.Priority or "Normal"
        package_weight = request.PackageWeightKg if request.PackageWeightKg is not None else 2.0
        sla_hours = request.SLAHours if request.SLAHours is not None else 48

        input_data = {
            "Origin": request.Origin,
            "Destination": request.Destination,
            "Distance_km": distance,
            "Carrier": request.Carrier,
            "Shipment_Type": shipment_type,
            "Service_Level": service_level,
            "Mode": mode,
            "Priority": priority,
            "Package_Weight_kg": package_weight,
            "Promised_SLA_Hours": sla_hours,
            "Weather": weather,
            "Traffic": traffic,
            "Month": int(request.Date.split("-")[1]),
            "Is_Festival_Season": 1 if int(request.Date.split("-")[1]) in [10, 11] else 0,
        }

        input_df = pd.DataFrame([input_data])
        input_encoded = pd.get_dummies(input_df)

        input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)

        risk_prob = float(classifier.predict_proba(input_encoded)[0][1])
        risk_level = "High Risk" if risk_prob > 0.6 else "Medium Risk" if risk_prob > 0.4 else "Low Risk"

        delay_hours = float(regressor.predict(input_encoded)[0])
        if risk_level == "Low Risk":
            delay_hours = 0.0

        sla_status = "On Track"
        if delay_hours > 0:
            if delay_hours >= sla_hours:
                sla_status = "High SLA Breach Risk"
            elif delay_hours >= 0.5 * sla_hours:
                sla_status = "Medium SLA Breach Risk"
            else:
                sla_status = "Low SLA Breach Risk"
        
        reason = "Normal Conditions"
        if weather in ["Heavy Rain (Monsoon)", "Storm"]:
            reason = f"Severe Weather Alert: {weather}"
        elif traffic == "Jam (Gridlock)":
            reason = "Critical Traffic Congestion Detected"
        elif risk_level == "High Risk":
            reason = "Combination of Distance & Carrier History"

        recommendation = "Proceed with Standard Dispatch"
        if risk_level == "High Risk":
            recommendation = "⚠️ Action Needed: Switch to Express Air or Change Carrier"

        return {
            "prediction": {
                "risk_score": round(risk_prob * 100, 1),
                "risk_level": risk_level,
                "estimated_delay_hours": round(delay_hours, 1),
                "promised_sla_hours": sla_hours,
                "sla_status": sla_status
            },
            "factors": {
                "weather_forecast": weather,
                "traffic_condition": traffic,
                "primary_reason": reason
            },
            "recommendation": recommendation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn backend.app:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)