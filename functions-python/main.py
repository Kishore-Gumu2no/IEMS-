# main.py (Final Corrected Version)

# NO firebase_admin import here is needed for initialization
from firebase_admin import firestore
from firebase_functions import firestore_fn

# This imports the real prediction function
from predict_hotspots import predict

# DO NOT CALL firebase_admin.initialize_app() HERE. The environment does it for you.

@firestore_fn.on_document_created("test_reports/{reportId}")
def run_prediction(event: firestore_fn.Event[firestore_fn.Change]) -> None:
    """
    Triggered when a new report is created in the 'test_reports' collection.
    This function runs the prediction and writes the result back to the document.
    """
    
    report_id = event.params["reportId"]
    print(f"Function triggered for report ID: {report_id}")

    report_data = event.data.to_dict()

    if report_data is None:
        print(f"No data in document {report_id}. Exiting.")
        return

    print("Running neglect prediction model...")
    
    # This calls the actual ML model
    prediction_result = predict(report_data)
    
    print(f"Prediction result: {prediction_result}")
    
    # Get a reference to the document and write the real prediction back into it.
    # The client is automatically available in this environment.
    doc_ref = firestore.client().collection("test_reports").document(report_id)
    doc_ref.update({
        "predicted_neglect": prediction_result
    })
    
    print(f"Successfully wrote prediction back to Firestore document {report_id}.")