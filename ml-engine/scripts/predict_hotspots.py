import pandas as pd
from xgboost import XGBRegressor
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("firebase/serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

def fetch_data():
    docs = db.collection("test_reports").get()
    data = [d.to_dict() for d in docs]
    return pd.DataFrame(data)

def train_predict(df):
    X = df[["frequency", "severity", "recency", "citizen_score"]]
    y = df["neglect_index"]
    model = XGBRegressor()
    model.fit(X, y)
    df["predicted_neglect"] = model.predict(X)
    return df

if __name__ == "__main__":
    df = fetch_data()
    result = train_predict(df)
    print(result[["image", "predicted_neglect"]])
