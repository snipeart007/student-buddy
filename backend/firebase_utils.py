import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Optional, Dict, Any
from agent_prompts.schemas import StudentState

# Initialize Firebase
# This expects a path to a service account JSON file in the FIREBASE_SERVICE_ACCOUNT environment variable.
# If not provided, it will attempt to use default credentials (useful for some cloud environments).
def initialize_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to default or partial init for local development
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                print(f"Firebase initialization warning: {e}")

initialize_firebase()
db = firestore.client()

def get_student_state_from_firebase(user_id: str) -> Optional[StudentState]:
    """Retrieves the student state from Firestore."""
    doc_ref = db.collection("student_states").document(user_id)
    doc = doc_ref.get()
    # Check if doc is a DocumentSnapshot and exists
    if hasattr(doc, "exists") and doc.exists:
        # Use Any to bypass strict union check from ty
        data = getattr(doc, "to_dict")()
        if data:
            return StudentState(**data)
    return None

def save_student_state_to_firebase(user_id: str, state: StudentState):
    """Saves the student state to Firestore."""
    doc_ref = db.collection("student_states").document(user_id)
    doc_ref.set(state.model_dump())

def verify_firebase_token(token: str) -> Optional[str]:
    """Verifies a Firebase ID token and returns the user_id."""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception:
        return None
