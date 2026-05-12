from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict

class BaseSchema(BaseModel):
    pass

class GradeEntry(BaseSchema):
    subject: str
    grade: str
    score: Optional[float] = None

class ExamEntry(BaseSchema):
    exam_name: str
    date: str
    priority: str # e.g. "high", "medium", "low"

class LearningStyle(BaseSchema):
    preferred_study_times: str
    strengths: List[str]
    weaknesses: List[str]

class AcademicState(BaseSchema):
    # Baseline context: Overall summary of academic standing and recent performance trends.
    baseline_context: str = "Stable academic performance with standard workload."
    current_education: str = ""
    current_grades: List[GradeEntry] = []
    subjects: List[str] = []
    exams_preparing_for: List[ExamEntry] = []
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

class MentalHealthState(BaseSchema):
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

class BehavioralSignals(BaseSchema):
    # Baseline context: Description of typical behavioral patterns and communication style.
    baseline_context: str = "Communicates clearly and seeks help when necessary."
    hopeless_wording_frequency: float = 0.0
    self_criticism_frequency: float = 0.0
    panic_indicators: float = 0.0
    urgency: float = 0.0
    avoidance_behavior: float = 0.0
    emotional_volatility: float = 0.0

class StudentState(BaseSchema):
    academic: AcademicState = AcademicState()
    mental_health: MentalHealthState = MentalHealthState()
    behavioral: BehavioralSignals = BehavioralSignals()

# Output Schemas
class PolicyAgentOutput(BaseSchema):
    mental_weight: float
    academic_weight: float
    mode: str
    risk_level: str

class FusionAgentOutput(BaseSchema):
    response: str
    action_items: List[str]
    follow_up_questions: List[str]
    updated_academic_state: AcademicState
    updated_mental_health_state: MentalHealthState
    updated_behavioral_signals: BehavioralSignals

# Input Schemas
class MentalAgentInput(BaseSchema):
    student_state: StudentState
    current_query: str

class AcademicAgentInput(BaseSchema):
    student_state: StudentState
    current_query: str

class PolicyAgentInput(BaseSchema):
    student_state: StudentState
    current_query: str

class FusionAgentInput(BaseSchema):
    student_state: StudentState
    current_query: str
    mental_agent_output: Optional[str] = None
    academic_agent_output: Optional[str] = None
    policy_weights: Optional[PolicyAgentOutput] = None

class QueryRequest(BaseSchema):
    user_id: str
    query: str

class QuestionnaireResponse(BaseSchema):
    age: int
    current_education_degree: str
    current_education_major: str
    current_education_year: int
    current_grades: List[GradeEntry]
    subjects: List[str]
    exams_preparing_for: List[ExamEntry]
    academic_strengths: List[str]
    academic_weaknesses: List[str]
    learning_style: LearningStyle
    education_goals: str
    stress_level: float
    burnout_history: str
