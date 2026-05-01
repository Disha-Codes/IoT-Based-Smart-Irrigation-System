import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
import joblib
import os

# ---------------- LOAD DATA ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "../dataset/data.csv"))

# ---------------- CLEAN COLUMNS ----------------
df.columns = df.columns.str.strip().str.lower()

print("Columns found:", df.columns.tolist())

# ---------------- SAFETY CHECK ----------------
required_cols = ["soil", "temp", "humidity", "crop type", "growth stage"]
for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Missing column: {col}")

# ---------------- ENCODE CROP ----------------
df["crop type"] = df["crop type"].astype(str).str.strip().str.lower()

crop_map = {
    "chilli": 0,
    "carrot": 1
}
df["crop"] = df["crop type"].map(crop_map)

# ---------------- ENCODE STAGE ----------------
df["growth stage"] = df["growth stage"].astype(str).str.strip().str.lower()

stage_map = {
    "germination": 0,
    "vegetative": 1,
    "flowering": 2,
    "fruiting": 3
}
df["stage"] = df["growth stage"].map(stage_map)

# ---------------- DROP BAD ROWS ----------------
df = df.dropna()

# ---------------- FEATURES ----------------
X = df[["soil", "temp", "humidity", "crop", "stage"]]

y_water = df["water"]
y_duration = df["duration"]

# ---------------- SPLIT ----------------
X_train, X_test, y_water_train, y_water_test = train_test_split(
    X, y_water, test_size=0.2, random_state=42
)

X_train2, X_test2, y_duration_train, y_duration_test = train_test_split(
    X, y_duration, test_size=0.2, random_state=42
)

# ---------------- TRAIN ----------------
model_water = DecisionTreeClassifier()
model_duration = DecisionTreeRegressor()

model_water.fit(X_train, y_water_train)
model_duration.fit(X_train2, y_duration_train)

# ---------------- SAVE ----------------
joblib.dump(model_water, os.path.join(BASE_DIR, "../models/water_model.pkl"))
joblib.dump(model_duration, os.path.join(BASE_DIR, "../models/duration_model.pkl"))

print("✅ Models retrained successfully!")