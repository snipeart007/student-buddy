import os
import json
from typing import Type, TypeVar, Any, Optional
from pydantic import BaseModel, ValidationError
from google import genai
import outlines
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

# Ensure API Key is set
gemini_key = os.getenv("GEMINI_API_KEY")
if not os.getenv("GOOGLE_API_KEY") and gemini_key:
    os.environ["GOOGLE_API_KEY"] = gemini_key

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY must be set in environment")

client = genai.Client(api_key=api_key)

T = TypeVar('T', bound=BaseModel)
I = TypeVar('I', bound=BaseModel)

class GeminiManager:
    def __init__(self, model_name: str):
        # Use the from_gemini helper which takes a genai.Client
        self.model = outlines.from_gemini(client, model_name)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception)),
        reraise=True
    )
    async def generate_structured_output(
        self, 
        system_prompt: str, 
        input_data: I, 
        output_schema: Type[T]
    ) -> T:
        """
        Takes a system prompt, an input Pydantic model, and an output schema.
        Serializes input to JSON, and uses Outlines to get a structured response.
        Includes automated retries for transient failures.
        """
        # Serialize input data to JSON string
        input_json = input_data.model_dump_json(indent=2)

        # Combine system prompt with the input data
        full_prompt = f"{system_prompt}\n\n### INPUT DATA (JSON):\n{input_json}\n\n### RESPONSE:"

        try:
            # Use model.generate with output_type to get structured output
            response_json = self.model.generate(full_prompt, output_type=output_schema)

            # Parse the JSON string into the Pydantic model
            return output_schema.model_validate_json(response_json)
        except ValidationError as e:
            print(f"Schema validation error for {output_schema.__name__}: {e}")
            raise # Let tenacity retry
        except Exception as e:
            print(f"Error during generation for {output_schema.__name__}: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception)),
        reraise=True
    )
    async def generate_text(
        self, 
        system_prompt: str, 
        input_data: Any
    ) -> str:
        """
        Takes a system prompt and an input object.
        Serializes input to JSON, and returns a plain text response.
        """
        if isinstance(input_data, BaseModel):
            input_json = input_data.model_dump_json(indent=2)
        else:
            input_json = str(input_data)

        # Combine system prompt with the input data
        full_prompt = f"{system_prompt}\n\n### INPUT DATA (JSON):\n{input_json}\n\n### RESPONSE:"

        try:
            # Use model.generate without output_type to get plain text
            return self.model.generate(full_prompt)
        except Exception as e:
            print(f"Error during text generation: {e}")
            raise

# Main model for conversational agents (Gemma 4 31B)
main_gemini_manager = GeminiManager(model_name="gemma-4-31b")

# Policy model (Gemma 3 2B)
policy_gemini_manager = GeminiManager(model_name="gemma-3-2b")
