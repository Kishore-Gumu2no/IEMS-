import random, datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Predefined example issue types
issue_types = ["pothole", "garbage", "water_leak", "streetlight_fault"]

def generate_fake_reports(n=15):
    for i in range(n):
        report = {
            "image": f"report_{i+1}.jpg",
            "detected": [random.choice(issue_types)],
            "frequency": random.randint(1, 5),
            "severity": random.randint(1, 10),
            "recency": random.randint(1, 10),
            "citizen_score": random.randint(1, 10),
            "status": "simulated",
            "created_at": datetime.datetime.utcnow(),
        }
        db.collection("test_reports").add(report)
        print(f"Added fake report {i+1}")

if __name__ == "__main__":
    generate_fake_reports(20)
