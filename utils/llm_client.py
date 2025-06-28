import os
import requests
import openai
from huggingface_hub import InferenceClient

class LLMClient:
    def __init__(self, api_key=None, model="HuggingFaceH4/zephyr-7b-beta"):
        self.api_key = api_key or os.getenv('HF_API_KEY')
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        # Groq config
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_api_base = "https://api.groq.com/openai/v1"
        self.groq_model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def chat(self, prompt, kb_passages=None):
        """
        Try Groq Llama-4-Scout-17B-16E-Instruct first (using OpenAI v1+ interface). If it fails, fallback to HuggingFace.
        Returns a tuple (reply, rationale).
        """
        # 1. Try Groq (OpenAI v1+ interface)
        if self.groq_api_key:
            try:
                groq_client = openai.OpenAI(
                    api_key=self.groq_api_key,
                    base_url=self.groq_api_base
                )
                response = groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=512,
                )
                reply = response.choices[0].message.content.strip()
                # No rationale for Groq for now
                return reply, None
            except Exception as e:
                print(f"[Groq LLM] Error: {e}. Falling back to HuggingFace model.")
        # 2. Fallback to HuggingFace
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256, "return_full_text": False}
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 404:
            return "Model not found or is not available for Inference API. Please check your model name or use a supported public model.", None
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[-1]:
            reply = result[-1]["generated_text"].strip()
        elif isinstance(result, dict) and "generated_text" in result:
            reply = result["generated_text"].strip()
        else:
            reply = str(result)
        # Refined rationale prompt, limit to top 2 KB passages
        limited_references = (kb_passages or [])[:2]
        references = "\n".join(limited_references).strip() if limited_references else ""
        if not references or references == "N/A":
            rationale = "No relevant facts or KB snippets were found for this answer."
            return reply, rationale
        rationale_prompt = f"""
You are PolicyPulse. Given the following answer and ONLY the reference facts or KB snippets below, explain in one sentence which snippet(s) were most important in producing this answer. Do not mention anything not in the references.

Answer: {reply}
References:
{references}
"""
        payload_rationale = {
            "inputs": rationale_prompt,
            "parameters": {"max_new_tokens": 64, "return_full_text": False}
        }
        response_rationale = requests.post(self.api_url, headers=self.headers, json=payload_rationale)
        if response_rationale.status_code == 404:
            return reply, None
        response_rationale.raise_for_status()
        result_rationale = response_rationale.json()
        if isinstance(result_rationale, list) and "generated_text" in result_rationale[-1]:
            rationale = result_rationale[-1]["generated_text"].strip()
        elif isinstance(result_rationale, dict) and "generated_text" in result_rationale:
            rationale = result_rationale["generated_text"].strip()
        else:
            rationale = str(result_rationale)
        return reply, rationale

    def stream_chat_response(self, prompt: str):
        """
        Stream tokens from HuggingFace InferenceClient as a generator.
        Falls back to regular chat if streaming fails.
        """
        try:
            # Use a more compatible model for streaming
            streaming_model = "gpt2"  # More compatible than zephyr-7b-beta
            client = InferenceClient(
                model=streaming_model,
                token=self.api_key
            )
            # Streaming text generation
            stream = client.text_generation(
                prompt,
                max_new_tokens=256,
                stream=True,
                return_full_text=False
            )
            for response in stream:
                # response is a dict with 'token' or a string (depending on HF version)
                if isinstance(response, dict) and 'token' in response:
                    yield response['token']
                else:
                    yield str(response)
        except Exception as e:
            print(f"Streaming failed: {e}. Falling back to regular chat.")
            # Fallback to regular chat method
            reply, _ = self.chat(prompt)
            # Yield the reply as a single token for compatibility
            yield reply