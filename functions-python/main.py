import os
from flask import Flask, request
import firebase_admin
from firebase_admin import firestore
# from predict_hotspots import predict # Your real ML function can be imported here later

# Initialize Firebase only once
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

app = Flask(__name__)

@app.route("/", methods=["POST"])
def run_prediction():
    """Receives event data from Eventarc trigger, runs the ML model, and writes back."""
    
    print("--- Event Received by Cloud Run ---")
    
    # Eventarc sends the event payload in the request body
    event_data = request.get_json()
    print(event_data)

    try:
        # For Firestore events, the document ID is in the 'ce-subject' header
        resource_string = request.headers.get("ce-subject")
        if not resource_string:
            print("ERROR: ce-subject header not found. Cannot determine document ID.")
            return "Error: Missing event metadata.", 500
            
        report_id = resource_string.split('/')[-1]
        print(f"Processing document ID: {report_id}")

        # --- YOUR ML LOGIC GOES HERE ---
        # prediction_result = predict(event_data) # Pass necessary data to your model
        prediction_result = "Prediction successful" # Placeholder
        # -----------------------------

        # Write the prediction back to the same Firestore document
        doc_ref = firestore.client().collection("test_reports").document(report_id)
        doc_ref.update({"predicted_neglect": prediction_result})
        
        print(f"Successfully wrote prediction for document: {report_id}")
        return "OK", 200

    except Exception as e:
        print(f"ERROR processing event: {e}")
        return f"Error processing event: {e}", 500

if __name__ == "__main__":
    # This command starts the web server and is used by Cloud Run
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))