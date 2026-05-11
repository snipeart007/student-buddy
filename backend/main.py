from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agent_prompts.schemas import (
    StudentState, AcademicState, MentalHealthState, BehavioralSignals,
    QueryRequest, QuestionnaireResponse,
    PolicyAgentInput, PolicyAgentOutput,
    MentalAgentInput,
    AcademicAgentInput,
    FusionAgentInput, FusionAgentOutput
)
from gemini_utils import main_gemini_manager, policy_gemini_manager
from firebase_utils import get_student_state_from_firebase, save_student_state_to_firebase
from agent_prompts.prompts import (
    MENTAL_HEALTH_AGENT_PROMPT,
    ACADEMIC_AGENT_PROMPT,
    POLICY_AGENT_PROMPT,
    FUSION_AGENT_PROMPT
)

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Student Buddy API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
USE_FIREBASE = os.getenv("USE_FIREBASE", "False").lower() == "true"

# Temporary in-memory stores
user_store: Dict[str, Dict[str, str]] = {} # user_id -> {username, password}
state_store: Dict[str, StudentState] = {}

class AuthRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/register")
async def register(request: AuthRequest):
    user_id = f"user_{len(user_store) + 1}"
    user_store[user_id] = {"username": request.username, "password": request.password}
    return {"message": "User registered", "user_id": user_id}

@app.post("/auth/login")
async def login(request: AuthRequest):
    for user_id, user_data in user_store.items():
        if user_data["username"] == request.username and user_data["password"] == request.password:
            return {"message": "Login successful", "user_id": user_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

def get_student_state(user_id: str) -> StudentState:
    if USE_FIREBASE:
        state = get_student_state_from_firebase(user_id)
        return state if state else StudentState()

    if user_id not in state_store:
        state_store[user_id] = StudentState()
    return state_store[user_id]

def save_student_state(user_id: str, state: StudentState):
    if USE_FIREBASE:
        save_student_state_to_firebase(user_id, state)
    else:
        state_store[user_id] = state

@app.post("/onboarding/submit")
async def submit_onboarding(user_id: str, response: QuestionnaireResponse):
    # Initialize StudentState from QuestionnaireResponse
    academic_state = AcademicState(
        current_education=f"{response.current_education.get('degree')} in {response.current_education.get('major')}, Year {response.current_education.get('year')}",
        current_grades=response.current_grades,
        subjects=response.subjects,
        exams_preparing_for=response.exams_preparing_for,
        academic_strengths=response.academic_strengths,
        academic_weaknesses=response.academic_weaknesses,
        education_goals=response.education_goals,
        baseline_context=f"Student is a {response.age} year old pursuing {response.current_education.get('degree')}. Goal: {response.education_goals}"
    )
    
    mental_state = MentalHealthState(
        stress_level=response.baseline_mental_health.get("stress_level", 0.0),
        baseline_context=f"Initial stress level: {response.baseline_mental_health.get('stress_level')}. Burnout history: {response.baseline_mental_health.get('burnout_history')}"
    )
    
    behavioral_signals = BehavioralSignals(
        baseline_context=f"Preferred study times: {response.learning_style.get('preferred_study_times')}"
    )
    
    new_state = StudentState(
        academic=academic_state,
        mental_health=mental_state,
        behavioral=behavioral_signals
    )
    
    save_student_state(user_id, new_state)
    return {"message": "Onboarding complete", "initial_state": new_state.model_dump()}

@app.get("/")
async def root():
    return {"message": "Student Buddy Backend is running"}

@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        # 1. Load state
        student_state = get_student_state(request.user_id)
        logger.info(f"Processing query for user {request.user_id}: {request.query}")
        
        # 2. Policy call
        policy_input = PolicyAgentInput(
            student_state=student_state,
            current_query=request.query
        )
        policy_output: PolicyAgentOutput = await policy_gemini_manager.generate_structured_output(
            system_prompt=POLICY_AGENT_PROMPT,
            input_data=policy_input,
            output_schema=PolicyAgentOutput
        )
        logger.info(f"Policy weights: Mental={policy_output.mental_weight}, Academic={policy_output.academic_weight}")
        
        # 3. Parallel Advisor calls (Natural Language)
        mental_input = MentalAgentInput(
            student_state=student_state,
            current_query=request.query
        )
        academic_input = AcademicAgentInput(
            student_state=student_state,
            current_query=request.query
        )
        
        # We run them in parallel
        mental_task = main_gemini_manager.generate_text(
            system_prompt=MENTAL_HEALTH_AGENT_PROMPT,
            input_data=mental_input
        )
        academic_task = main_gemini_manager.generate_text(
            system_prompt=ACADEMIC_AGENT_PROMPT,
            input_data=academic_input
        )
        
        mental_text, academic_text = await asyncio.gather(mental_task, academic_task)
        logger.info("Advisor calls (text) completed.")
        
        # 4. Fusion call
        fusion_input = FusionAgentInput(
            student_state=student_state,
            current_query=request.query,
            mental_agent_output=mental_text,
            academic_agent_output=academic_text,
            policy_weights=policy_output
        )
        fusion_output: FusionAgentOutput = await main_gemini_manager.generate_structured_output(
            system_prompt=FUSION_AGENT_PROMPT,
            input_data=fusion_input,
            output_schema=FusionAgentOutput
        )
        
        # 5. Update and Persist state
        # Fusion agent now updates the entire state
        updated_state = StudentState(
            academic=fusion_output.updated_academic_state,
            mental_health=fusion_output.updated_mental_health_state,
            behavioral=fusion_output.updated_behavioral_signals
        )
        save_student_state(request.user_id, updated_state)
        
        return {
            "response": fusion_output.response,
            "action_items": fusion_output.action_items,
            "follow_up_questions": fusion_output.follow_up_questions,
            "policy": policy_output.model_dump(),
            "updated_state": updated_state.model_dump()
        }
    except Exception as e:
        logger.error(f"Error in orchestration pipeline: {e}", exc_info=True)
        # Fallback response
        return {
            "response": "I'm sorry, I'm having a bit of trouble processing everything right now. Let's take a deep breath. Can you tell me more about how you're feeling, or should we focus on one small task at a time?",
            "action_items": ["Take a short break", "Identify one priority"],
            "follow_up_questions": ["What is the most urgent thing on your mind?"],
            "error": "Pipeline failure, falling back to safety response."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
