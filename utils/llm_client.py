import os
import requests

class LLMClient:
    def __init__(self, api_key=None, model="HuggingFaceH4/zephyr-7b-beta"):
        self.api_key = api_key or os.getenv('HF_API_KEY')
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def chat(self, prompt):
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256, "return_full_text": False}
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 404:
            return "Model not found or is not available for Inference API. Please check your model name or use a supported public model."
        response.raise_for_status()
        result = response.json()
        # The output format may vary by model; this works for most chat models
        if isinstance(result, list) and "generated_text" in result[-1]:
            return result[-1]["generated_text"].strip()
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"].strip()
        else:
            return str(result)