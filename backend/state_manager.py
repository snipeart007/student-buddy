import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .agent_prompts.schemas import StudentState

# Constants
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STATE_FILE = os.path.join(DATA_DIR, "student_state.json.enc")
KEY_FILE = os.path.join(DATA_DIR, ".key")

class StudentStateManager:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key)

    def _get_or_create_key(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            # Generate a new key
            # In a real app, this could be derived from hardware ID or user password
            # For this local app, we'll generate and save it
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b"student-buddy-default-secret"))
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            return key

    def save_state(self, state: StudentState):
        state_dict = state.model_dump()
        state_json = json.dumps(state_dict).encode("utf-8")
        encrypted_data = self.fernet.encrypt(state_json)
        with open(STATE_FILE, "wb") as f:
            f.write(encrypted_data)

    def load_state(self) -> StudentState:
        if not os.path.exists(STATE_FILE):
            return StudentState()
        
        with open(STATE_FILE, "rb") as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            state_dict = json.loads(decrypted_data.decode("utf-8"))
            return StudentState(**state_dict)
        except Exception as e:
            print(f"Error loading state: {e}")
            # If decryption fails, return default state (or handle appropriately)
            return StudentState()

    def update_from_questionnaire(self, questionnaire: dict):
        # This will be used during onboarding
        state = StudentState()
        
        # Populate academic state
        state.academic.current_education = f"{questionnaire.get('current_education_degree')} in {questionnaire.get('current_education_major')} (Year {questionnaire.get('current_education_year')})"
        state.academic.current_grades = questionnaire.get('current_grades', [])
        state.academic.subjects = questionnaire.get('subjects', [])
        state.academic.exams_preparing_for = questionnaire.get('exams_preparing_for', [])
        state.academic.academic_strengths = questionnaire.get('academic_strengths', [])
        state.academic.academic_weaknesses = questionnaire.get('academic_weaknesses', [])
        state.academic.education_goals = questionnaire.get('education_goals', "")
        
        # Populate mental health state
        state.mental_health.stress_level = questionnaire.get('stress_level', 0.0)
        state.mental_health.baseline_context = f"History of burnout: {questionnaire.get('burnout_history')}"
        
        self.save_state(state)
        return state
