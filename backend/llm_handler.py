import os
import json
import base64
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from typing import Generator, List, Dict, Any, Union

class LLMHandler:
    def __init__(self, 
                 model_path: str = "./models/student-buddy-gemma-policy-model-gguf/gemma-4-e2b-it.Q4_K_M.gguf",
                 clip_path: str = "./models/student-buddy-gemma-policy-model-gguf/gemma-4-e2b-it.F16-mmproj.gguf"):
        self.model_path = model_path
        self.clip_path = clip_path
        
        if not os.path.exists(model_path):
            print(f"Warning: Model not found at {model_path}. LLM calls will fail.")
            self.llm = None
        else:
            # Use Llava15ChatHandler for multi-modal support if clip_path exists
            chat_handler = None
            if os.path.exists(clip_path):
                print(f"Loading vision projector from {clip_path}")
                chat_handler = Llava15ChatHandler(clip_model_path=clip_path)
            else:
                print(f"Warning: Vision projector not found at {clip_path}. Multi-modal will be disabled.")

            self.llm = Llama(
                model_path=model_path,
                chat_handler=chat_handler,
                n_ctx=4096,
                n_threads=os.cpu_count(),
                logits_all=True # Often needed for multimodal
            )

    def _prepare_messages(self, prompt: Union[str, Dict], system_prompt: str) -> List[Dict]:
        messages = [{"role": "system", "content": system_prompt}]
        
        if isinstance(prompt, str):
            messages.append({"role": "user", "content": prompt})
        elif isinstance(prompt, dict):
            # Handle Gradio multimodal input: {"text": "...", "files": [...]}
            content = []
            if "text" in prompt and prompt["text"]:
                content.append({"type": "text", "text": prompt["text"]})
            
            if "files" in prompt:
                for file_path in prompt["files"]:
                    if os.path.exists(file_path):
                        # Convert image to data URI
                        with open(file_path, "rb") as f:
                            base64_image = base64.b64encode(f.read()).decode("utf-8")
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        })
            
            messages.append({"role": "user", "content": content})
        
        return messages

    def generate_json(self, prompt: Union[str, Dict], system_prompt: str) -> Dict[str, Any]:
        if not self.llm:
            return self._mock_json_response(prompt)
        
        messages = self._prepare_messages(prompt, system_prompt)
        
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=500,
                response_format={"type": "json_object"} if "json" in system_prompt.lower() else None
            )
            
            text = response["choices"][0]["message"]["content"].strip()
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Error in generate_json: {e}")
            return self._mock_json_response(prompt)

    def stream_generate(self, prompt: Union[str, Dict], system_prompt: str) -> Generator[str, None, None]:
        if not self.llm:
            mock_text = f"Mock response. Model not found.\nQuery: {prompt}"
            for word in mock_text.split():
                yield word + " "
            return

        messages = self._prepare_messages(prompt, system_prompt)
        
        try:
            stream = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=2048,
                stream=True
            )
            
            for chunk in stream:
                if "content" in chunk["choices"][0]["delta"]:
                    yield chunk["choices"][0]["delta"]["content"]
        except Exception as e:
            yield f"Error in stream_generate: {e}"

    def _mock_json_response(self, prompt: Any) -> Dict[str, Any]:
        return {
            "mental_weight": 0.5,
            "academic_weight": 0.5,
            "mode": "balanced_support",
            "risk_level": "low"
        }
