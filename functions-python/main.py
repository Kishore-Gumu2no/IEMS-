# main.py

import firebase_admin
from firebase_admin import firestore
from firebase_functions import firestore_fn

# The ML import is commented out for the test.
# from predict_hotspots import predict

# Initialize the Firebase Admin SDK.
firebase_admin.initialize_app()

@firestore_fn.on_document_created("test_reports/{reportId}")
def run_prediction(event: firestore_fn.Event[firestore_fn.Change]) -> None:
    """
    Triggered when a new report is created in the 'test_reports' collection.
    This function runs the prediction and writes the result back to the document.
    """
    
    # Get the ID of the document that was created.
    report_id = event.params["reportId"]
    print(f"Function triggered for report ID: {report_id}")

    # Get the data from the new document.
    report_data = event.data.to_dict()

    if report_data is None:
        print(f"No data in document {report_id}. Exiting.")
        return

    print("Running neglect prediction model...")
    
    # The actual model call is commented out. We use a placeholder string instead.
    # prediction_result = predict(report_data)
    prediction_result = "testing"
    
    print(f"Prediction result: {prediction_result}")
    
    # Get a reference to the document and write the prediction back into it.
    doc_ref = firestore.client().collection("test_reports").document(report_id)
    doc_ref.update({
        "predicted_neglect": prediction_result
    })
    
    print(f"Successfully wrote prediction back to Firestore document {report_id}.")