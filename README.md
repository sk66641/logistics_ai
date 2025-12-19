## Logistics AI – Delivery Delay Risk Predictor

This project is a small end-to-end demo:

- Backend: FastAPI with XGBoost and LightGBM models that estimate delay risk and delay hours.
- Frontend: One HTML page with Chart.js.
- Data: Synthetic shipment data for India with weather, traffic, SLA, and shipment details.

### 1. Setup

1) Clone and enter the repo:

```bash
git clone https://github.com/sk66641/logistics_ai.git
cd logistics_ai
```

2) (Optional) create a virtual env:

```bash
python -m venv myenv
source myenv/bin/activate
```

3) Install Python packages:

```bash
pip install -r requirements.txt
```

### 2. Make sample data

Creates `backend/data/shipment_data.csv` with fake shipments plus weather and traffic columns.

```bash
python backend/generate_data.py
```

### 3. Train the models

Trains an XGBoost classifier for delay risk and a LightGBM regressor for delay hours. It also saves the one-hot column list.

```bash
python backend/model_training.py
```

Saved to `backend/models/`:

- `classifier.joblib`
- `regressor.joblib`
- `model_columns.joblib`

### 4. Run the API

Start the FastAPI server (via Uvicorn):

```bash
uvicorn backend.app:app --reload
```

Default URL: `http://127.0.0.1:8000`

- Main endpoint: `POST /predict`
- JSON body:
  - `Origin`, `Destination`, `Carrier`, `Date`
  - optional: `ShipmentType`, `ServiceLevel`, `Mode`, `Priority`, `PackageWeightKg`, `SLAHours`

### 5. Open the frontend

The UI lives in `frontend/`:

```bash
cd frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500/index.html`.

Page features:

- A simple shipment form (route, carrier, shipment type, service level, mode, priority, weight, SLA, date).
- A results area with delay risk %, delay hours, promised SLA, and SLA risk.
- Weather and traffic notes plus a small bar chart for quick factors.
- A what-if simulator to compare carriers for the same trip and date.

### 6. Data approach (today vs. later)

Today the data is fake and generated locally. You can swap in real feeds later.

Planned sources:

- Past shipment logs (origin, destination, carrier, status).
- Live weather and traffic from external APIs.

Key features used:

- Route distance, carrier, shipment type (B2B/B2C), service level, mode, priority, package weight, SLA hours.
- Simulated weather (rain, heavy rain, fog, storm) and traffic (low to jam).
- Season flag for festival months and month from the date (could add weekday or hour later).

### 7. How the models work

Two steps:

1) Risk classifier (XGBoost): predicts if a shipment will be delayed and gives a probability.
2) Delay regressor (LightGBM): for delayed shipments, predicts how many hours late.

The response includes risk score (percent), risk level (Low / Medium / High), estimated delay hours, and SLA risk (On track / Low / Medium / High).

### 8. Notes for a real build

- API latency: Getting weather/traffic for every call can be slow. Use async FastAPI endpoints, httpx, and short caching for repeat routes and time windows.
- Class balance: Most shipments are on time. Use class weights or SMOTE and watch precision/recall.
- Data freshness: Weather and traffic change fast. Cache results for a few minutes per route and time window, and log which version you used.

### 9. Possible next steps

- Replace synthetic data with real weather and traffic APIs.
- Add GPS or live truck tracking, not just ETA at booking.
- Add user roles (Admin / Planner / Driver).
- Send alerts (webhooks, email, WhatsApp) for high risk or likely SLA breaks.
- Save common what-if setups (for example “Festival Rush”).
- Add deeper explainability (e.g., SHAP) and feature importance per route or carrier.

### 10. Project structure

- `backend/`
  - `generate_data.py` – makes synthetic data.
  - `model_training.py` – trains and saves models.
  - `app.py` – FastAPI app and `/predict` endpoint.
- `frontend/`
  - `index.html` – UI.
  - `script.js` – API calls and dashboard logic.
- `requirements.txt` – Python dependencies.
