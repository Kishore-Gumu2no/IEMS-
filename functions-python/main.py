import functions_framework
import firebase_admin
from firebase_admin import firestore
import json

# Initialize Firebase only once in the global scope
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

@functions_framework.cloud_event
def run_prediction(cloud_event):
    """Triggered by a change to a Firestore document."""
    
    # === START: DEBUGGING PRINTS ===
    print("--- Function Triggered Successfully ---")
    
    # The data payload is encoded in the cloud_event.data attribute
    event_data = cloud_event.data
    
    # Print the raw event data to see its structure
    print("Raw CloudEvent Data:")
    print(json.dumps(event_data, indent=2))
    
    # Example of extracting the document ID
    try:
        resource_string = cloud_event["source"]
        # The resource string is long, e.g., projects/your-project/databases/(default)/documents/test_reports/someId
        doc_id = resource_string.split('/')[-1]
        print(f"Firestore Document ID: {doc_id}")
    except Exception as e:
        print(f"Error extracting document ID: {e}")
    
    print("--- End of Debug Log ---")
    # === END: DEBUGGING PRINTS ===

    # You can add your ML logic and Firestore write-back logic here later.
    
    return "OK", 200