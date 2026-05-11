import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Optional, Dict, Any
from agent_prompts.schemas import StudentState

# Initialize Firebase
# This expects a path to a service account JSON file in the FIREBASE_SERVICE_ACCOUNT environment variable.
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
                # We don't raise here, but functions using firebase will fail if not correctly initialized
                pass

_db = None

def get_db():
    global _db
    if _db is None:
        initialize_firebase()
        try:
            _db = firestore.client()
        except Exception as e:
            print(f"Error initializing Firestore client: {e}")
            return None
    return _db

def get_student_state_from_firebase(user_id: str) -> Optional[StudentState]:
    """Retrieves the student state from Firestore."""
    db = get_db()
    if db is None:
        return None
        
    doc_ref = db.collection("student_states").document(user_id)
    doc = doc_ref.get()
    if hasattr(doc, "exists") and doc.exists:
        data = getattr(doc, "to_dict")()
        if data:
            return StudentState(**data)
    return None

def save_student_state_to_firebase(user_id: str, state: StudentState):
    """Saves the student state to Firestore."""
    db = get_db()
    if db is None:
        return
        
    doc_ref = db.collection("student_states").document(user_id)
    doc_ref.set(state.model_dump())

def verify_firebase_token(token: str) -> Optional[str]:
    """Verifies a Firebase ID token and returns the user_id."""
    initialize_firebase()
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception:
        return None
