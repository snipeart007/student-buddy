# Student Buddy Backend

The backend of Student Buddy is a FastAPI application integrated with a Gradio chat interface. It acts as the local orchestrator for the AI agents, handles user sessions, manages student state, and performs local inference using `llama.cpp`.

---

## 📁 File Structure & Key Modules

- [main.py](file:///home/snipeart007/repos/student-buddy/backend/main.py): The entry point of the FastAPI application. Sets up CORS, implements login/registration routes, and mounts the Gradio interface to `/advisor_chat`.
- [orchestrator.py](file:///home/snipeart007/repos/student-buddy/backend/orchestrator.py): Implements the routing logic. Coordinates between the policy agent, specialized advisor agents, and the final fusion agent.
- [llm_handler.py](file:///home/snipeart007/repos/student-buddy/backend/llm_handler.py): Encapsulates initialization and interaction with the local LLM.
- [state_manager.py](file:///home/snipeart007/repos/student-buddy/backend/state_manager.py): Handles loading, saving, and AES encrypting the local student profile state.
- [agent_prompts/](file:///home/snipeart007/repos/student-buddy/backend/agent_prompts/):
  - [prompts.py](file:///home/snipeart007/repos/student-buddy/backend/agent_prompts/prompts.py): Defines prompt templates for each agent role.
  - [schemas.py](file:///home/snipeart007/repos/student-buddy/backend/agent_prompts/schemas.py): Pydantic validation schemas defining the structure of `StudentState`, agent outputs, and onboarding questionnaires.

---

## 🛠️ Key Technical Implementations

### 1. Local Encrypted Persistence
Student privacy is maintained by encrypting the state JSON using Fernet symmetric encryption.
- **File Locations**: Data is persisted in `../data/student_state.json.enc`.
- **Key Generation**: A unique encryption key is auto-generated upon the first run and written to `../data/.key`.

### 2. Multi-Agent Prompt Orchestration
- **Policy Pass**: Extracts current student metrics and formats a structured JSON query to evaluate risks.
- **Advisor Routing**: Under high-risk scenarios, requests are sent to both the academic and mental health prompts. For development purposes, these fallback to the local model (with `#TODO: Replace with institution API call` annotations for production deployment).
- **Fusion Pass**: Consolidates advisor responses and queries the fusion adapter.
- **Background Updates**: In non-critical risk scenarios, updating the state is offloaded to a separate background thread so it does not block the real-time chat stream.

---

## ⚠️ LoRA Adapter Limitation Note

Because `llama.cpp` and its Python bindings do not support runtime hot-reloading/applying multiple LoRA adapters dynamically on a single base model instance, `llm_handler.py` implements the following fallback in `_get_llm()`:

```python
self._llm_instances[adapter_name] = Llama(
    model_path=self.base_model_path,
    lora_path=lora_path,
    chat_handler=chat_handler,
    n_ctx=2048,
    ...
)
```

This lazy-loads a separate, independent `Llama` object for each adapter/role (`policy`, `academic`, `mental`, `fusion`). Consequently, multiple copies of the model are instantiated and cached, which requires a substantial amount of RAM/VRAM. Keep this in mind when running on low-resource environments.

---

## 🚀 Running the Backend

Ensure you have [uv](https://github.com/astral-sh/uv) installed, then run:

```bash
uv run --project backend python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
This serves the API on `http://127.0.0.1:8000`, and exposes the Gradio chat app endpoint on `http://127.0.0.1:8000/advisor_chat`.
