# ---------------- IMPORTS ----------------
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score
)
import joblib

# ---------------- LOAD DATA ----------------
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "../dataset/data.csv"))

# ---------------- CLEAN ----------------
df.columns = df.columns.str.strip().str.lower()

# ---------------- REMOVE DUPLICATES ----------------
df = df.drop_duplicates()

# ---------------- ENCODE ----------------
df["crop type"] = df["crop type"].str.strip().str.lower()
df["growth stage"] = df["growth stage"].str.strip().str.lower()

crop_map = {"chilli": 0, "carrot": 1}
stage_map = {"germination": 0, "vegetative": 1, "flowering": 2, "fruiting": 3}

df["crop"] = df["crop type"].map(crop_map)
df["stage"] = df["growth stage"].map(stage_map)

df = df.dropna()

# ---------------- FEATURES ----------------
X = df[["soil", "temp", "humidity", "crop", "stage"]]
y_water = df["water"]
y_duration = df["duration"]

# ---------------- SPLIT (MORE REALISTIC) ----------------
X_train, X_test, y_water_train, y_water_test, y_duration_train, y_duration_test = train_test_split(
    X, y_water, y_duration, test_size=0.3, random_state=42
)

# ---------------- MODELS (CONTROL OVERFITTING) ----------------
model_water = DecisionTreeClassifier(
    max_depth=4,
    min_samples_split=10,
    random_state=42
)

model_duration = DecisionTreeRegressor(
    max_depth=4,
    min_samples_split=10,
    random_state=42
)

# ---------------- TRAIN ----------------
model_water.fit(X_train, y_water_train)
model_duration.fit(X_train, y_duration_train)

print("✅ Models trained!")
# ---------------- EVALUATION ----------------

print("\n===== WATER MODEL =====")
y_pred_water = model_water.predict(X_test)

print("Accuracy:", accuracy_score(y_water_test, y_pred_water))
print("Precision:", precision_score(y_water_test, y_pred_water, zero_division=0))
print("Recall:", recall_score(y_water_test, y_pred_water, zero_division=0))
print("F1:", f1_score(y_water_test, y_pred_water, zero_division=0))

y_prob = model_water.predict_proba(X_test)[:,1]
print("ROC:", roc_auc_score(y_water_test, y_prob))

print("\nConfusion Matrix:\n", confusion_matrix(y_water_test, y_pred_water))

print("\n===== DURATION MODEL =====")
y_pred_duration = model_duration.predict(X_test)

print("MAE:", mean_absolute_error(y_duration_test, y_pred_duration))
print("MSE:", mean_squared_error(y_duration_test, y_pred_duration))
print("R2:", r2_score(y_duration_test, y_pred_duration))

# ---------------- SAVE ----------------
joblib.dump(model_water, os.path.join(BASE_DIR, "../models/water_model.pkl"))
joblib.dump(model_duration, os.path.join(BASE_DIR, "../models/duration_model.pkl"))


print("💾 Models saved!")

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

# Get probabilities
y_prob = model_water.predict_proba(X_test)[:, 1]

# Compute ROC
fpr, tpr, thresholds = roc_curve(y_water_test, y_prob)
roc_auc = roc_auc_score(y_water_test, y_prob)

# Plot
plt.figure()
plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.2f})")
plt.plot([0, 1], [0, 1], linestyle="--")  # random line

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Water Prediction Model")
plt.legend()

plt.show()