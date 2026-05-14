import json
import threading
from typing import Generator, Dict, Any, List, Union
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

    def _get_condensed_state(self, state: StudentState) -> Dict[str, Any]:
        """
        Strips zero/empty values from the state to reduce LLM context and evaluation time.
        """
        state_dict = state.model_dump()
        condensed = {}
        
        for category, fields in state_dict.items():
            if isinstance(fields, dict):
                cat_data = {k: v for k, v in fields.items() if v not in [0, 0.0, "", [], {}, None]}
                if cat_data:
                    condensed[category] = cat_data
            else:
                if fields not in [0, 0.0, "", [], {}, None]:
                    condensed[category] = fields
        return condensed

    def orchestrate(self, query: Union[str, Dict], user_id: str) -> Generator[str, None, None]:
        # 1. Load State and Condense
        state = self.state_manager.load_state()
        condensed_state = self._get_condensed_state(state)
        state_json = json.dumps(condensed_state)
        
        # 2. Policy Agent
        yield "### 🧠 Policy Orchestration\n"
        yield "Analyzing query and student state...\n"
        
        policy_query = query
        if isinstance(query, dict):
            policy_query = query.copy()
            policy_query["text"] = f"Context: {state_json}\nQuery: {query.get('text', '')}"
        else:
            policy_query = f"Context: {state_json}\nQuery: {query}"

        policy_output_dict = self.llm.generate_json(policy_query, POLICY_AGENT_PROMPT, adapter="policy")
        policy_output = PolicyAgentOutput(**policy_output_dict)
        
        yield f"**Weights Assigned:** Mental: {policy_output.mental_weight}, Academic: {policy_output.academic_weight}\n"
        yield f"**Mode:** {policy_output.mode} | **Risk Level:** {policy_output.risk_level}\n\n"
        
        risk_is_high = policy_output.risk_level in ["high", "critical"]
        
        if risk_is_high:
            yield "### ⚠️ High Risk Detected\n"
            yield "Routing to specialized Academic and Mental Health agents...\n\n"
            
            academic_query = query
            if isinstance(query, dict):
                academic_query = query.copy()
                academic_query["text"] = f"Context: {state_json}\nQuery: {query.get('text', '')}"
            else:
                academic_query = f"Context: {state_json}\nQuery: {query}"

            # TODO: Replace with institution API call for Academic response
            academic_response = ""
            yield "#### 🎓 Academic Advisor reasoning\n"
            for chunk in self.llm.stream_generate(academic_query, ACADEMIC_AGENT_PROMPT, adapter="academic"):
                academic_response += chunk
                yield chunk
            yield "\n\n"
            
            # TODO: Replace with institution API call for Mental Health response
            mental_response = ""
            yield "#### 🧘 Mental Health Advisor reasoning\n"
            for chunk in self.llm.stream_generate(academic_query, MENTAL_HEALTH_AGENT_PROMPT, adapter="mental"):
                mental_response += chunk
                yield chunk
            yield "\n\n"
            
            yield "### 🛠️ Fusion Optimization\n"
            yield "Combining advisor perspectives for a balanced response...\n\n"
            
            # For Fusion, we provide the advisor summaries
            fusion_input = (
                f"Weights: {policy_output_dict}\n"
                f"Academic: {academic_response}\n"
                f"Mental: {mental_response}\n"
                f"User Query: {query.get('text', '') if isinstance(query, dict) else query}"
            )
            
            final_response = ""
            for chunk in self.llm.stream_generate(fusion_input, FUSION_AGENT_PROMPT, adapter="fusion"):
                final_response += chunk
                yield chunk
            
            self._update_state_post_interaction(state, query, final_response, policy_output)
            
        else:
            yield "### 💬 Advisor Response\n"
            
            advisor_input = (
                f"Context: {state_json}\n"
                f"Weights: {policy_output_dict}\n"
                f"Query: {query.get('text', '') if isinstance(query, dict) else query}"
            )

            final_response = ""
            for chunk in self.llm.stream_generate(advisor_input, FUSION_AGENT_PROMPT, adapter="fusion"):
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
