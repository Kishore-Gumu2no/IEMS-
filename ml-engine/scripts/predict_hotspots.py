import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from firebase_admin import credentials, firestore, initialize_app

# --- Initialize Firebase ---
cred = credentials.Certificate("firebase/serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()


# --- Fetch Data from Firestore ---
def fetch_data():
    docs = db.collection("test_reports").get()
    data = [d.to_dict() for d in docs]

    if not data:
        print("⚠️ No documents found in 'test_reports' collection.")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    print(f"✅ Fetched {len(df)} records from Firestore.")
    return df


# --- Train Model and Predict ---
def train_predict(df):
    required_columns = ["frequency", "severity", "recency", "citizen_score", "neglect_index"]

    # Ensure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"❌ Missing column: '{col}' in Firestore data.")

    # Separate features and target
    X = df[["frequency", "severity", "recency", "citizen_score"]].copy()
    y = df["neglect_index"].copy()

    # Handle missing or invalid data
    X = X.replace([np.inf, -np.inf], np.nan)
    y = y.replace([np.inf, -np.inf], np.nan)

    # Fill NaN values with 0 (or mean if you prefer)
    X = X.fillna(0)
    y = y.fillna(0)

    # Debug summary
    print("📊 Training Data Summary:")
    print(X.describe())
    print("NaN in X:", X.isna().sum().sum())
    print("NaN in y:", y.isna().sum())

    # Train model
    model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X, y)

    # Predict neglect index
    df["predicted_neglect"] = model.predict(X)
    print("✅ Model trained and predictions made successfully!")
    return df


# --- Main Execution ---
if __name__ == "__main__":
    df = fetch_data()

    if df.empty:
        print("⚠️ No data available for training. Please add test_reports to Firestore.")
    else:
        result = train_predict(df)
        print(result[["image", "predicted_neglect"]] if "image" in result.columns else result.head())
