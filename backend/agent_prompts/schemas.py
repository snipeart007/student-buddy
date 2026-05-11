from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class AcademicState(BaseModel):
    # Baseline context: Overall summary of academic standing and recent performance trends.
    baseline_context: str = "Stable academic performance with standard workload."
    current_education: str = ""
    current_grades: Dict[str, Any] = {}
    subjects: List[str] = []
    exams_preparing_for: List[Dict[str, Any]] = []
    academic_strengths: List[str] = []
    academic_weaknesses: List[str] = []
    education_goals: str = ""
    gpa_trend: float = 0.0
    assignment_backlog: int = 0
    attendance: float = 0.0
    exam_proximity: float = 0.0
    study_consistency: float = 0.0
    procrastination: float = 0.0
    subject_confidence: float = 0.0
    academic_momentum: float = 0.0

class MentalHealthState(BaseModel):
    # Baseline context: General emotional baseline and recent psychological observations.
    baseline_context: str = "Generally stable mood with typical student stress levels."
    stress_level: float = 0.0
    burnout_level: float = 0.0
    anxiety: float = 0.0
    loneliness: float = 0.0
    emotional_exhaustion: float = 0.0
    resilience: float = 0.0
    emotional_stability: float = 0.0
    motivation: float = 0.0

class BehavioralSignals(BaseModel):
    # Baseline context: Description of typical behavioral patterns and communication style.
    baseline_context: str = "Communicates clearly and seeks help when necessary."
    hopeless_wording_frequency: float = 0.0
    self_criticism_frequency: float = 0.0
    panic_indicators: float = 0.0
    urgency: float = 0.0
    avoidance_behavior: float = 0.0
    emotional_volatility: float = 0.0

class StudentState(BaseModel):
    academic: AcademicState = AcademicState()
    mental_health: MentalHealthState = MentalHealthState()
    behavioral: BehavioralSignals = BehavioralSignals()

# Output Schemas
class PolicyAgentOutput(BaseModel):
    mental_weight: float
    academic_weight: float
    mode: str
    risk_level: str

class FusionAgentOutput(BaseModel):
    response: str
    action_items: List[str]
    follow_up_questions: List[str]
    updated_academic_state: AcademicState
    updated_mental_health_state: MentalHealthState
    updated_behavioral_signals: BehavioralSignals

# Input Schemas
class MentalAgentInput(BaseModel):
    student_state: StudentState
    current_query: str

class AcademicAgentInput(BaseModel):
    student_state: StudentState
    current_query: str

class PolicyAgentInput(BaseModel):
    student_state: StudentState
    current_query: str

class FusionAgentInput(BaseModel):
    student_state: StudentState
    current_query: str
    mental_agent_output: Optional[str] = None
    academic_agent_output: Optional[str] = None
    policy_weights: Optional[PolicyAgentOutput] = None

class QueryRequest(BaseModel):
    user_id: str
    query: str

class QuestionnaireResponse(BaseModel):
    age: int
    current_education: Dict[str, Any] # e.g. {"degree": "B.Sc", "major": "CS", "year": 3}
    past_education: List[Dict[str, Any]]
    current_grades: Dict[str, Any]
    subjects: List[str]
    exams_preparing_for: List[Dict[str, Any]]
    academic_strengths: List[str]
    academic_weaknesses: List[str]
    learning_style: Dict[str, Any] # e.g. {"preferred_study_times": "evening", "strengths": [], "weaknesses": []}
    education_goals: str
    baseline_mental_health: Dict[str, Any] # e.g. {"stress_level": 0.3, "burnout_history": "none", "support_systems": []}
