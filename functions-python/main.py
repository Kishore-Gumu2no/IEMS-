import os
from flask import Flask, request
import firebase_admin
from firebase_admin import firestore
from predict_hotspots import predict # Assuming your ML function is here

# Initialize Firebase only once
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

app = Flask(__name__)

@app.route("/", methods=["POST"])
def run_prediction():
    """Receives event data from Eventarc trigger and runs the ML model."""

    event_data = request.get_json()
    print("--- Event Received ---")
    print(event_data)

    try:
        # Extract the new document data from the Firestore event payload
        doc_data = event_data["value"]["fields"]
        report_id = event_data["document"].split('/')[-1]

        print(f"Processing document ID: {report_id}")

        # --- YOUR ML LOGIC GOES HERE ---
        # prediction_result = predict(doc_data)
        prediction_result = "ML model output would go here" # Placeholder
        # -----------------------------

        # Write the prediction back to Firestore
        doc_ref = firestore.client().collection("test_reports").document(report_id)
        doc_ref.update({"predicted_neglect": prediction_result})

        print(f"Successfully wrote prediction for document: {report_id}")
        return "OK", 200

    except Exception as e:
        print(f"ERROR processing event: {e}")
        return f"Error: {e}", 500

if __name__ == "__main__":
    # This is what Cloud Run uses to start the server
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))