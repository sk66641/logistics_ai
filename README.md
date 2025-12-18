## Logistics AI – Delivery Delay & SLA Risk Simulator

This project is a small end‑to‑end logistics intelligence demo:

- **Backend**: FastAPI + XGBoost + LightGBM models for delivery delay risk and delay hours.
- **Frontend**: Single‑page dashboard (plain HTML/CSS/JS + Chart.js).
- **Data**: Synthetic Indian shipment dataset with weather, traffic, SLA and shipment attributes.

### 1. Environment setup

1. Create and activate a virtualenv (optional but recommended):

```bash
git clone https://github.com/sk66641/logistics_ai.git
cd logistics_ai
```

```bash
python -m venv myenv
source myenv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Generate synthetic data

This creates `backend/data/shipment_data.csv` with enriched shipment + environment features.

```bash
python backend/generate_data.py
```

### 3. Train models

This trains:

- an **XGBoost classifier** to predict delay risk (0/1),
- a **LightGBM regressor** to predict delay hours for delayed shipments,
- and saves the one‑hot encoded feature columns.

```bash
python backend/model_training.py
```

Artifacts are stored in `backend/models/`:

- `classifier.joblib`
- `regressor.joblib`
- `model_columns.joblib`

### 4. Run the API

Start the FastAPI backend (served with Uvicorn):

```bash
uvicorn backend.app:app --reload
```

By default it listens on `http://127.0.0.1:8000`.

- Main prediction endpoint: `POST /predict`
- Request body (JSON) includes:
  - `Origin`, `Destination`, `Carrier`, `Date`
  - optional: `ShipmentType`, `ServiceLevel`, `Mode`, `Priority`, `PackageWeightKg`, `SLAHours`

### 5. Open the frontend

The frontend is a static page in `frontend/`:

```bash
cd frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500/index.html` in your browser.

The page provides:

- A **shipment form** with route, carrier, shipment type, service level, mode, priority, weight, SLA and date.
- **Prediction dashboard** showing:
  - Delay risk (%), estimated delay hours.
  - Promised SLA (hours) and **SLA breach risk**.
  - Context chips for weather and traffic.
  - A bar chart showing relative impact of weather, traffic and carrier.
- **What‑if simulator** to compare carriers for the same lane/date via multiple `/predict` calls.

### 6. Data Strategy & Feature Engineering (Prototype vs. Future)

This repo currently uses **synthetic data** for experimentation, but is designed to be swapped to real feeds later.

#### Data Sources (Planned for production)

- **Historical Logs:** Past shipment data (Origin, Destination, Carrier, Status) used for training.
- **Live Environmental Data:** Real-time fetching of Weather (precipitation, visibility) and Traffic patterns via external APIs (e.g. maps + weather providers).

#### Key Features Used

- **Static Features (already in prototype):** Route distance, carrier, shipment type (B2B/B2C), service level, mode, package weight, SLA hours.
- **Dynamic Features (currently simulated, later real):**
  - **Weather:** Rain intensity, heavy-rain vs. clear/fog/storm.
  - **Traffic:** Congestion level bucket (Low/Medium/High/Jam) and its impact on delay.
- **Derived Features (already in prototype):**
  - **Seasonality:** Festival month indicator (e.g. Oct–Nov rush).
  - **Temporal:** Month extracted from date; can be extended to weekday/weekend, hour-of-day.

---

### 7. Model Logic

#### Two‑stage architecture

The system follows a **two‑stage prediction pattern**:

1. **Stage 1 – Risk classification (XGBoost)**
   - **Question:** “Will this shipment be delayed?”
   - **Output:** Binary class (On time vs. Delayed) + probability.
2. **Stage 2 – Delay duration (LightGBM)**
   - **Question:** “If delayed, by how many hours?”
   - **Output:** Continuous value in hours, trained only on actually delayed shipments.

The prototype reports:

- **Risk score** (percentage), **risk level** (Low / Medium / High),
- **Estimated delay hours**,
- **SLA breach risk** (On track / Low / Medium / High) based on delay vs. SLA.

#### Explainability (Current vs. planned)

- Current UI shows a **simple factor bar chart** (weather, traffic, carrier) as an intuitive explanation.
- In a production version, we can plug in **SHAP (Shapley values)** on top of XGBoost/LightGBM to quantify how much each feature contributed to a specific prediction.

---

### 8. Implementation Challenges & Planned Solutions

These are **design notes for the real‑data version** of the system:

1. **Handling API latency**
   - **Problem:** Fetching weather/traffic data for every request can add 2–3 seconds.
   - **Planned solution:** Use async `FastAPI` endpoints with `httpx` and short‑term caching for repeated lanes/time windows.

2. **Data imbalance**
   - **Problem:** In real shipment logs, most shipments are “On time”, making delays the minority class.
   - **Planned solution:** Use techniques like **SMOTE** / class‑weighted loss during training, and carefully monitor precision/recall.

3. **Real‑world consistency**
   - **Problem:** Weather and traffic update quickly; naive re‑querying can cause noisy predictions and high API costs.
   - **Planned solution:** Cache responses for a small TTL (e.g. 10 minutes) per (lane, time‑bucket) and log the versions of external data used.

---

### 9. Future Scope & Roadmap

Some ideas for growing this prototype into a fuller logistics intelligence platform:

- **Real APIs:** Plug in production weather and traffic APIs instead of synthetic generators.
- **GPS Integration:** In‑transit tracking for trucks, not just pre‑dispatch ETA at booking time.
- **User Accounts & Roles:** Separate dashboards for **Admin**, **Planner**, and **Driver** views.
- **Alerting:** Webhooks / email / WhatsApp alerts for high‑risk or SLA‑breach‑risk shipments.
- **What‑if Playbooks:** Save scenario presets (e.g. “Festival Rush”, “Monsoon South India”) for planners to re‑use.
- **Deeper Explainability:** Full SHAP‑based explanations and feature importance drill‑downs per lane/carrier.

---

### 10. Project structure

- `backend/`
  - `generate_data.py` – synthetic data generation.
  - `model_training.py` – training and saving models.
  - `app.py` – FastAPI app and `/predict` endpoint.
- `frontend/`
  - `index.html` – UI.
  - `script.js` – API calls and dashboard logic.
- `requirements.txt` – Python dependencies.

