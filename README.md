# Logistics AI – Delivery Delay Risk Predictor

This project is a small end-to-end demo of a delivery delay prediction system.

* **Backend:** FastAPI with XGBoost and LightGBM models to estimate delay risk and delay hours.
* **UI:** A single HTML page using Chart.js.
* **Data:** Synthetic shipment data for India with weather, traffic, SLA, and shipment details.

---

## 1. Setup

Clone and enter the repo:

```bash
git clone https://github.com/sk66641/logistics_ai.git
cd logistics_ai
```

(Optional) create a virtual environment:

```bash
python -m venv myenv
source myenv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 2. Run the API

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

Default URL: `http://127.0.0.1:8000`

* Endpoint: `POST /predict`
* Required fields: `Origin`, `Destination`, `Carrier`, `Date`
* Optional fields: `ShipmentType`, `ServiceLevel`, `Mode`, `Priority`, `PackageWeightKg`, `SLAHours`

---

## 3. Open the ui

```bash
python -m http.server 5500
```

Open `http://127.0.0.1:5500/index.html`.

Features:

* Shipment input form
* Delay risk %, delay hours, SLA risk
* Weather and traffic indicators
* Simple charts
* Carrier comparison (what-if simulation)