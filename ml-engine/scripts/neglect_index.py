import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# Initialize Firebase
cred = credentials.Certificate("firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def calculate_neglect_index(report):
    frequency = report.get("frequency", 1)
    severity = report.get("severity", 1)
    recency = report.get("recency", 1)
    citizen_score = report.get("citizen_score", 1)
    return (frequency * severity * recency) + citizen_score

def update_neglect_index():
    reports = db.collection("test_reports").get()
    for doc in reports:
        data = doc.to_dict()
        ni = calculate_neglect_index(data)
        db.collection("test_reports").document(doc.id).update({
            "neglect_index": ni,
            "last_updated": datetime.datetime.utcnow()
        })
        print(f"Updated {doc.id} → NI = {ni}")

if __name__ == "__main__":
    update_neglect_index()
