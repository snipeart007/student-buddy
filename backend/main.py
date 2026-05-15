import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import gradio as gr
from .state_manager import StudentStateManager
from .llm_handler import LLMHandler
from .orchestrator import Orchestrator
from .agent_prompts.schemas import QuestionnaireResponse
# Initialize components
state_manager = StudentStateManager()
llm_handler = LLMHandler()
orchestrator = Orchestrator(llm_handler, state_manager)

app = FastAPI(title="Student Buddy API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- FastAPI Endpoints ---

@app.post("/auth/register")
async def register(data: dict = Body(...)):
    # TODO: Replace with institution API call
    return {"status": "success", "message": "User registered locally", "user_id": data.get("email")}

@app.post("/auth/login")
async def login(data: dict = Body(...)):
    # TODO: Replace with institution API call
    return {"status": "success", "message": "Logged in", "user_id": data.get("email")}

@app.post("/onboarding")
async def onboarding(data: dict = Body(...)):
    try:
        # Validate data against QuestionnaireResponse schema (simplified here)
        state_manager.update_from_questionnaire(data)
        return {"status": "success", "message": "Onboarding complete"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Gradio Interface ---

def chat_interface(message, history, user_id):
    # Gradio history is list of openai-style dictionaries (Gradio 6+)
    # user_id is passed from the additional_inputs
    for chunk in orchestrator.orchestrate(message, user_id):
        yield chunk

# Gradio Chat Interface with custom styling
with gr.Blocks() as chat_api:
    gr.ChatInterface(
        fn=chat_interface,
        additional_inputs=[gr.Textbox(label="User ID", value="default_user", visible=False)],
        title="Academic Advisor",
        description="Your personal assistant for academic goals and mental wellbeing. Upload images of your assignments or schedules for better advice!",
        examples=[
            [{"text": "I'm feeling burnt out from my exams."}, "default_user"],
            [{"text": "How can I improve my study schedule?"}, "default_user"]
        ],
        multimodal=True,
        fill_height=True,
        fill_width=True
    )


# Mount Gradio to FastAPI
# We mount this FIRST so it takes precedence over the greedy static root mount
app = gr.mount_gradio_app(
    app, 
    chat_api, 
    path="/advisor_chat",
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate")
)

# Serve frontend static files if they exist
frontend_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "frontend", "out"))
if os.path.exists(frontend_path):
    # Mount this LAST as a catch-all for the frontend
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
