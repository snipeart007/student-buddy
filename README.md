# Student Buddy: AI-Powered Academic & Well-being Advisor

Student Buddy is a local, privacy-first desktop assistant designed to help students balance academic workloads with mental health. By utilizing a local Large Language Model via `llama.cpp` and secure local state management, the application guarantees user privacy while offering tailored educational and well-being advice.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Next.js + MUI Frontend] <-->|HTTP / API Requests| B[FastAPI Backend]
    B <-->|Exposes Chat API| C[Gradio chat_api]
    
    subgraph Multi-Agent Orchestrator
        D[Policy Agent] -->|1. Route & Weight Query| E{Risk Level Check}
        E -->|Low/Medium Risk| F[Base Model / Fusion Adapter]
        E -->|High/Critical Risk| G[Academic Advisor Agent]
        E -->|High/Critical Risk| H[Mental Health Advisor Agent]
        G & H -->|2. Merge perspectives| I[Fusion Agent]
    end

    B <-->|Load / Query| Multi-Agent Orchestrator
    B <-->|AES Encrypted Load/Save| J[(Encrypted JSON State)]
```

### 1. Multi-Agent Routing & Orchestration
When a message is received from the frontend:
1. **Policy Agent**: Analyzes the query and current `StudentState`. It assigns weights to mental and academic components (`mental_weight` and `academic_weight`), sets a mode (e.g., `emotional_recovery`), and evaluates the `risk_level`.
2. **Routing Decision**:
   - **Low/Medium Risk**: The query and state are sent directly to the local model using the **Fusion** adapter to stream a unified response.
   - **High/Critical Risk**: The query is routed to two separate agents: **Academic Advisor Agent** and **Mental Health Advisor Agent** (represented by specialized adapters/prompts). Their responses are combined via the **Fusion Agent** to generate the final output.
3. **Background State Update**: After sending the response, a background task analyzes the interaction and updates the persisted `StudentState`.

### 2. Security & Local Persistence
- All student data is stored locally on the user's computer inside the `data/` directory.
- The state is serialized to JSON and encrypted using AES-128 in CBC mode with HMAC-SHA256 (via the Python `cryptography` Fernet library) to maintain data privacy.

---

## ⚠️ Known Implementation Limitations

> [!WARNING]
> ### 1. Incomplete Frontend Chat Interface
> The current chat UI inside the frontend ([Chat.tsx](file:///home/snipeart007/repos/student-buddy/frontend/src/components/Chat.tsx)) is incomplete. Instead of rendering messages natively via Material UI (MUI) components using the `@gradio/client` API client, the frontend currently displays the raw Gradio interface using an `<iframe>` targeting `/advisor_chat`. 
> 
> *Planned fix*: Re-implement the Chat component using native React components, querying a headless Gradio API via the `@gradio/client` package, displaying distinct streaming blocks for both "Thinking Process/Routing" and "Final Response".

> [!WARNING]
> ### 2. Runtime LoRA Hot-Reloading Limitations
> The underlying engine `llama.cpp` (and the `llama-cpp-python` bindings) does not support dynamic runtime hot-reloading or applying multiple LoRA adapters on-the-fly to a single loaded base model instance. 
> 
> As a workaround, the backend ([llm_handler.py](file:///home/snipeart007/repos/student-buddy/backend/llm_handler.py)) instantiates separate, independent `Llama` instances for each role (`policy`, `academic`, `mental`, `fusion`). This duplicates the base model weights in memory for each adapter, which is highly inefficient and can lead to Out-Of-Memory (OOM) errors on systems with limited memory/VRAM.

---

## 📁 Repository Directory Structure

- [run.py](file:///home/snipeart007/repos/student-buddy/run.py) - Main entrypoint to launch both the backend server and frontend client.
- [backend/](file:///home/snipeart007/repos/student-buddy/backend) - FastAPI + Gradio server handling state encryption, local inference, and orchestrating agents.
- [frontend/](file:///home/snipeart007/repos/student-buddy/frontend) - Next.js + Material UI application providing the onboarding questionnaire and chat interfaces.
- [initial_prompt.md](file:///home/snipeart007/repos/student-buddy/initial_prompt.md) & [main_prompt.md](file:///home/snipeart007/repos/student-buddy/main_prompt.md) - Original project specifications and system requirements.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (recommended for Python package management)

### Running the Project
The project comes with a helper startup script [run.py](file:///home/snipeart007/repos/student-buddy/run.py) at the root level. To start:

1. Install dependencies for the backend and frontend.
2. Build/Export the frontend assets:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
3. Run the main runner script from the root workspace directory:
   ```bash
   python run.py
   ```
This command starts the Uvicorn-served backend and automatically opens `http://127.0.0.1:8000` in your default web browser.
