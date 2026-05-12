import json
import threading
from typing import Generator, Dict, Any, List
from .llm_handler import LLMHandler
from .state_manager import StudentStateManager
from .agent_prompts.schemas import StudentState, PolicyAgentOutput, FusionAgentOutput
from .agent_prompts.prompts import (
    POLICY_AGENT_PROMPT,
    ACADEMIC_AGENT_PROMPT,
    MENTAL_HEALTH_AGENT_PROMPT,
    FUSION_AGENT_PROMPT
)

class Orchestrator:
    def __init__(self, llm_handler: LLMHandler, state_manager: StudentStateManager):
        self.llm = llm_handler
        self.state_manager = state_manager

    def orchestrate(self, query: Union[str, Dict], user_id: str) -> Generator[str, None, None]:
        # 1. Load State
        state = self.state_manager.load_state()
        
        # 2. Policy Agent
        yield "### 🧠 Policy Orchestration\n"
        yield "Analyzing query and student state...\n"
        
        # We pass state as context in the system prompt or prepended to the user query
        # Since we want to support vision, we'll keep the query structure if it's a dict
        
        policy_query = query
        if isinstance(query, dict):
            # Prepend state context to the text part of the multimodal query
            policy_query = query.copy()
            policy_query["text"] = f"Student State: {state.model_dump_json()}\nCurrent Query: {query.get('text', '')}"
        else:
            policy_query = f"Student State: {state.model_dump_json()}\nCurrent Query: {query}"

        policy_output_dict = self.llm.generate_json(policy_query, POLICY_AGENT_PROMPT)
        policy_output = PolicyAgentOutput(**policy_output_dict)
        
        yield f"**Weights Assigned:** Mental: {policy_output.mental_weight}, Academic: {policy_output.academic_weight}\n"
        yield f"**Mode:** {policy_output.mode} | **Risk Level:** {policy_output.risk_level}\n\n"
        
        risk_is_high = policy_output.risk_level in ["high", "critical"]
        
        if risk_is_high:
            yield "### ⚠️ High Risk Detected\n"
            yield "Routing to specialized Academic and Mental Health agents (Institution API Fallback)...\n\n"
            
            # TODO: Replace with institution API call for Academic response
            academic_response = ""
            yield "#### 🎓 Academic Advisor Reasoning\n"
            
            academic_query = query
            if isinstance(query, dict):
                academic_query = query.copy()
                academic_query["text"] = f"Student State: {state.model_dump_json()}\nCurrent Query: {query.get('text', '')}"
            else:
                academic_query = f"Student State: {state.model_dump_json()}\nCurrent Query: {query}"

            for chunk in self.llm.stream_generate(academic_query, ACADEMIC_AGENT_PROMPT):
                academic_response += chunk
                yield chunk
            yield "\n\n"
            
            # TODO: Replace with institution API call for Mental Health response
            mental_response = ""
            yield "#### 🧘 Mental Health Advisor Reasoning\n"
            for chunk in self.llm.stream_generate(academic_query, MENTAL_HEALTH_AGENT_PROMPT):
                mental_response += chunk
                yield chunk
            yield "\n\n"
            
            yield "### 🛠️ Fusion Optimization\n"
            yield "Combining advisor perspectives for a balanced response...\n\n"
            
            # Fusion usually doesn't need the image again if advisors summarized it, 
            # but we'll pass it anyway for context.
            fusion_query = query
            text_context = (
                f"Student State: {state.model_dump_json()}\n"
                f"Policy Weights: {policy_output_dict}\n"
                f"Academic Output: {academic_response}\n"
                f"Mental Health Output: {mental_response}\n"
            )
            
            if isinstance(query, dict):
                fusion_query = query.copy()
                fusion_query["text"] = f"{text_context}Original Query: {query.get('text', '')}"
            else:
                fusion_query = f"{text_context}Original Query: {query}"

            final_response = ""
            for chunk in self.llm.stream_generate(fusion_query, FUSION_AGENT_PROMPT):
                final_response += chunk
                yield chunk
            
            self._update_state_post_interaction(state, query, final_response, policy_output)
            
        else:
            yield "### 💬 Advisor Response\n"
            
            advisor_query = query
            text_context = (
                f"Student State: {state.model_dump_json()}\n"
                f"Policy Weights: {policy_output_dict}\n"
            )
            
            if isinstance(query, dict):
                advisor_query = query.copy()
                advisor_query["text"] = f"{text_context}Query: {query.get('text', '')}"
            else:
                advisor_query = f"{text_context}Query: {query}"

            final_response = ""
            for chunk in self.llm.stream_generate(advisor_query, FUSION_AGENT_PROMPT):
                final_response += chunk
                yield chunk
            
            threading.Thread(target=self._update_state_post_interaction, args=(state, query, final_response, policy_output)).start()

    def _update_state_post_interaction(self, state: StudentState, query: str, response: str, policy: PolicyAgentOutput):
        """
        Updates the student state based on the conversation.
        """
        # In a real implementation, we'd use the LLM to analyze the interaction 
        # and specifically update the fields in StudentState.
        # For now, we'll use a simplified update logic or another LLM call.
        
        update_prompt = (
            f"Current State: {state.model_dump_json()}\n"
            f"User Query: {query}\n"
            f"Advisor Response: {response}\n"
            "Analyze the interaction and provide the UPDATED StudentState in JSON format."
        )
        
        system_prompt = "You are a state management agent. Output ONLY valid JSON of the updated StudentState."
        
        try:
            updated_state_dict = self.llm.generate_json(update_prompt, system_prompt)
            updated_state = StudentState(**updated_state_dict)
            self.state_manager.save_state(updated_state)
            
            # TODO: Replace with institution API call to sync state
            print("Student state updated and saved locally.")
        except Exception as e:
            print(f"Failed to update state: {e}")
