import os
import json
import base64
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from typing import Generator, List, Dict, Any, Union

class LLMHandler:
    def __init__(self, 
                 base_model_path: str = "./models/gemma-4-2b-base.gguf",
                 clip_path: str = "./models/gemma-4-2b-mmproj.gguf"):
        self.base_model_path = base_model_path
        self.clip_path = clip_path
        
        # Paths for LoRA adapters (to be provided later)
        self.adapter_paths = {
            "policy": "./models/adapters/policy.gguf",
            "academic": "./models/adapters/academic.gguf",
            "mental": "./models/adapters/mental.gguf",
            "fusion": "./models/adapters/fusion.gguf"
        }
        
        # Cache for loaded model instances
        self._llm_instances = {}
        
        # Warm up the base model (without adapters)
        self._get_llm(None)

    def _get_llm(self, adapter_name: str = None) -> Llama:
        """
        Returns a Llama instance for the specified adapter. 
        Lazily loads and caches the instances.
        """
        if adapter_name not in self._llm_instances:
            if not os.path.exists(self.base_model_path):
                print(f"Warning: Base model not found at {self.base_model_path}.")
                return None
            
            lora_path = self.adapter_paths.get(adapter_name) if adapter_name else None
            if lora_path and not os.path.exists(lora_path):
                print(f"Warning: Adapter {adapter_name} not found at {lora_path}. Using base model.")
                lora_path = None

            print(f"Initializing model for role: {adapter_name or 'base'}...")
            
            chat_handler = None
            if os.path.exists(self.clip_path):
                chat_handler = Llava15ChatHandler(clip_model_path=self.clip_path)

            self._llm_instances[adapter_name] = Llama(
                model_path=self.base_model_path,
                lora_path=lora_path,
                chat_handler=chat_handler,
                n_ctx=2048,
                n_threads=max(1, os.cpu_count() - 1),
                verbose=False
            )
            
        return self._llm_instances[adapter_name]

    def _format_bare_prompt(self, prompt: str, system_prompt: str) -> str:
        return f"{system_prompt}\n\nUser: {prompt}\nAssistant: "

    def generate_json(self, prompt: Union[str, Dict], system_prompt: str, adapter: str = "policy") -> Dict[str, Any]:
        llm = self._get_llm(adapter)
        if not llm:
            return self._mock_json_response(prompt)
        
        user_msg = prompt if isinstance(prompt, str) else prompt.get("text", "")
        raw_prompt = self._format_bare_prompt(user_msg, system_prompt)
        
        try:
            response = llm(
                raw_prompt,
                max_tokens=500,
                temperature=0.1,
                stop=["User:", "Assistant:"]
            )
            
            text = response["choices"][0]["text"].strip()
            if "{" in text:
                text = text[text.find("{"):text.rfind("}")+1]
            return json.loads(text)
        except Exception as e:
            print(f"Error in generate_json ({adapter}): {e}")
            return self._mock_json_response(prompt)

    def stream_generate(self, prompt: Union[str, Dict], system_prompt: str, adapter: str = None) -> Generator[str, None, None]:
        llm = self._get_llm(adapter)
        if not llm:
            mock_text = f"Mock response. Model not found.\nQuery: {prompt}"
            for word in mock_text.split():
                yield word + " "
            return

        user_msg = prompt if isinstance(prompt, str) else prompt.get("text", "")
        raw_prompt = self._format_bare_prompt(user_msg, system_prompt)
        
        try:
            stream = llm(
                raw_prompt,
                max_tokens=1024,
                temperature=0.7,
                repeat_penalty=1.1,
                stream=True,
                stop=["User:", "Assistant:"]
            )
            
            for chunk in stream:
                token = chunk["choices"][0]["text"]
                yield token
        except Exception as e:
            yield f"Error in stream_generate ({adapter}): {e}"

    def _mock_json_response(self, prompt: Any) -> Dict[str, Any]:
        return {
            "mental_weight": 0.5,
            "academic_weight": 0.5,
            "mode": "balanced_support",
            "risk_level": "low"
        }
