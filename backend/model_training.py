import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error

print("⏳ Loading Data...")
data = pd.read_csv("backend/data/shipment_data.csv")

print("⚙️ Preprocessing Features...")

X = data.drop(columns=["Delayed", "Delay_Hours"])
y_class = data["Delayed"]
y_reg = data["Delay_Hours"]

X_encoded = pd.get_dummies(X)

model_columns = list(X_encoded.columns)
joblib.dump(model_columns, "backend/models/model_columns.joblib")
print(f"✅ Saved feature columns structure ({len(model_columns)} features)")

print("\n🤖 Training Risk Classifier (XGBoost)...")

X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_class, test_size=0.2, random_state=42
)

classifier = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=5,
    use_label_encoder=False,
    eval_metric="logloss"
)
classifier.fit(X_train, y_train)

# Evaluate
y_pred = classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Classifier Accuracy: {accuracy * 100:.2f}%")

# Save Classifier
joblib.dump(classifier, "backend/models/classifier.joblib")

# 4. TRAIN REGRESSOR (LightGBM)
# This model answers: "How late will it be?"
# CRITICAL: We only train this on data that WAS actually delayed.
# Predicting delay time for on-time shipments confuses the model.
print("\n📉 Training Duration Regressor (LightGBM)...")

# Filter only delayed shipments for training the time predictor
delayed_indices = y_class == 1
X_delayed = X_encoded[delayed_indices]
y_delayed = y_reg[delayed_indices]

X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_delayed, y_delayed, test_size=0.2, random_state=42)

# Initialize and Train
regressor = lgb.LGBMRegressor(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=5
)
regressor.fit(X_train_reg, y_train_reg)

# Evaluate
y_pred_reg = regressor.predict(X_test_reg)
mae = mean_absolute_error(y_test_reg, y_pred_reg)
print(f"✅ Regressor Mean Error: {mae:.2f} hours")

# Save Regressor
joblib.dump(regressor, "backend/models/regressor.joblib")

print("\n🎉 Success! All models saved in 'backend/models/'")